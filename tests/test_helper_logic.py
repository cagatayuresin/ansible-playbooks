"""Unit tests for pure helper logic used by operational playbooks."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / "playbooks" / "files"


def load_module(name: str):
    path = FILES / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


backup = load_module("etcd_backup_verify")
upgrade = load_module("k8s_upgrade_readiness_check")
workloads = load_module("k8s_workload_resilience_check")
endpoints = load_module("k8s_service_endpoints_check")
pod_security = load_module("k8s_pod_security_posture_check")
rbac = load_module("k8s_rbac_risks_check")
pod_diagnostics = load_module("k8s_unschedulable_pods_diagnose")
control_plane = load_module("control_plane_security_check")
support_bundle = load_module("support_bundle_collect")


class BackupLogicTests(unittest.TestCase):
    def test_newest_snapshot_and_zip_extraction(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            old = root / "etcd_snapshot_old.db"
            old.write_bytes(b"old")
            archive = root / "etcd_snapshot_new.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("nested/snapshot.db", b"new database")
            old_mtime = 1_700_000_000
            os.utime(old, (old_mtime, old_mtime))
            os.utime(archive, (old_mtime + 60, old_mtime + 60))

            self.assertEqual(backup.newest_snapshot(root), archive)
            workspace = root / "workspace"
            workspace.mkdir()
            extracted, note = backup.extract_if_needed(archive, workspace)
            self.assertEqual(extracted.read_bytes(), b"new database")
            self.assertIn("ZIP", note)

    def test_human_size(self):
        self.assertEqual(backup.human_size(1024), "1.0 KiB")


class UpgradeReadinessLogicTests(unittest.TestCase):
    def test_version_parser(self):
        self.assertEqual(upgrade.version_tuple("v1.34.3"), (1, 34, 3))
        self.assertIsNone(upgrade.version_tuple("1.34"))
        self.assertEqual(upgrade.release_tuple("1.22"), (1, 22, 0))

    def test_deprecated_api_metric_parser(self):
        metrics = (
            'apiserver_requested_deprecated_apis{group="extensions",'
            'removed_release="1.22",resource="ingresses",subresource="",'
            'version="v1beta1"} 1\n'
        )
        parsed = upgrade.parse_deprecated_metrics(metrics)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["removed_release"], "1.22")

    def test_main_blocks_api_removed_in_target_release(self):
        with tempfile.TemporaryDirectory() as temp_name:
            backup_file = Path(temp_name) / "etcd_snapshot_test.db"
            backup_file.write_bytes(b"snapshot")
            responses = [
                {"serverVersion": {"gitVersion": "v1.21.9"}},
                {
                    "items": [
                        {
                            "metadata": {"name": "node1"},
                            "status": {
                                "conditions": [
                                    {
                                        "type": "Ready",
                                        "status": "True",
                                        "reason": "KubeletReady",
                                    }
                                ],
                                "nodeInfo": {"kubeletVersion": "v1.21.9"},
                            },
                        }
                    ]
                },
                {"items": []},
                {"items": []},
                {"items": []},
            ]
            metrics = (
                'apiserver_requested_deprecated_apis{group="extensions",'
                'removed_release="1.22",resource="ingresses",subresource="",'
                'version="v1beta1"} 1\n'
            )
            with (
                mock.patch.object(upgrade, "kubectl_json", side_effect=[(data, None) for data in responses]),
                mock.patch.object(upgrade, "newest_backup", return_value=backup_file),
                mock.patch.object(upgrade.shutil, "which", return_value="/usr/bin/kubectl"),
                mock.patch.object(
                    upgrade,
                    "run",
                    return_value=subprocess.CompletedProcess(
                        ["kubectl"], 0, stdout=metrics, stderr=""
                    ),
                ),
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        "check",
                        "--target-version",
                        "1.22.0",
                        "--backup-dir",
                        temp_name,
                    ],
                ),
                redirect_stdout(io.StringIO()) as output,
            ):
                result = upgrade.main()
            self.assertEqual(result, 2)
            self.assertIn("Deprecated API", output.getvalue())


class WorkloadLogicTests(unittest.TestCase):
    def test_selector_matching(self):
        selector = {
            "matchLabels": {"app": "api"},
            "matchExpressions": [
                {"key": "tier", "operator": "In", "values": ["backend"]}
            ],
        }
        self.assertTrue(
            workloads.selector_matches(
                selector, {"app": "api", "tier": "backend"}
            )
        )
        self.assertFalse(
            workloads.selector_matches(
                selector, {"app": "api", "tier": "frontend"}
            )
        )

    def test_mutable_image_tag(self):
        self.assertTrue(workloads.image_has_mutable_tag("example/api:latest"))
        self.assertTrue(workloads.image_has_mutable_tag("example/api"))
        self.assertFalse(workloads.image_has_mutable_tag("example/api:v1.2.3"))
        self.assertFalse(
            workloads.image_has_mutable_tag("example/api@sha256:deadbeef")
        )

    def test_workload_report_main(self):
        workload_data = {
            "items": [
                {
                    "kind": "Deployment",
                    "metadata": {"namespace": "default", "name": "api"},
                    "spec": {
                        "replicas": 1,
                        "template": {
                            "metadata": {"labels": {"app": "api"}},
                            "spec": {
                                "containers": [
                                    {"name": "api", "image": "example/api:latest"}
                                ]
                            },
                        },
                    },
                }
            ]
        }
        with (
            mock.patch.object(
                workloads,
                "kubectl_json",
                side_effect=[workload_data, {"items": []}],
            ),
            mock.patch.object(sys, "argv", ["check"]),
            redirect_stdout(io.StringIO()) as output,
        ):
            result = workloads.main()
        self.assertEqual(result, 0)
        self.assertIn("readinessProbe", output.getvalue())


class EndpointLogicTests(unittest.TestCase):
    def test_endpoint_readiness(self):
        self.assertTrue(endpoints.endpoint_is_ready({"conditions": {}}))
        self.assertTrue(
            endpoints.endpoint_is_ready(
                {"conditions": {"ready": True, "serving": True}}
            )
        )
        self.assertFalse(
            endpoints.endpoint_is_ready(
                {
                    "conditions": {
                        "ready": True,
                        "serving": True,
                        "terminating": True,
                    }
                }
            )
        )
        self.assertFalse(
            endpoints.endpoint_is_ready({"conditions": {"ready": False}})
        )

    def test_service_without_slice_is_critical(self):
        services = {
            "items": [
                {
                    "metadata": {"namespace": "default", "name": "api"},
                    "spec": {"selector": {"app": "api"}, "type": "ClusterIP"},
                }
            ]
        }
        with (
            mock.patch.object(
                endpoints,
                "kubectl_json",
                side_effect=[services, {"items": []}],
            ),
            mock.patch.object(sys, "argv", ["check"]),
            redirect_stdout(io.StringIO()) as output,
        ):
            result = endpoints.main()
        self.assertEqual(result, 0)
        self.assertIn("[CRITICAL] default/api: EndpointSlice yok", output.getvalue())

    def test_slice_with_null_endpoints_is_reported_without_crashing(self):
        services = {
            "items": [
                {
                    "metadata": {"namespace": "default", "name": "api"},
                    "spec": {"selector": {"app": "api"}, "type": "ClusterIP"},
                }
            ]
        }
        slices = {
            "items": [
                {
                    "metadata": {
                        "namespace": "default",
                        "labels": {"kubernetes.io/service-name": "api"},
                    },
                    "endpoints": None,
                }
            ]
        }
        with (
            mock.patch.object(
                endpoints,
                "kubectl_json",
                side_effect=[services, slices],
            ),
            mock.patch.object(sys, "argv", ["check"]),
            redirect_stdout(io.StringIO()) as output,
        ):
            result = endpoints.main()
        self.assertEqual(result, 0)
        self.assertIn(
            "[CRITICAL] default/api: 0 endpoint var fakat hazır backend yok",
            output.getvalue(),
        )


class ClusterSecurityReportTests(unittest.TestCase):
    def test_privileged_pod_is_critical(self):
        namespaces = {"items": [{"metadata": {"name": "default", "labels": {}}}]}
        pods = {
            "items": [
                {
                    "metadata": {"namespace": "default", "name": "api"},
                    "spec": {
                        "containers": [
                            {
                                "name": "api",
                                "securityContext": {"privileged": True},
                            }
                        ]
                    },
                }
            ]
        }
        with (
            mock.patch.object(
                pod_security,
                "kubectl_json",
                side_effect=[namespaces, pods],
            ),
            mock.patch.object(sys, "argv", ["check"]),
            redirect_stdout(io.StringIO()) as output,
        ):
            result = pod_security.main()
        self.assertEqual(result, 0)
        self.assertIn("privileged=true", output.getvalue())

    def test_cluster_admin_binding_is_critical(self):
        cluster_bindings = {
            "items": [
                {
                    "metadata": {"name": "admins"},
                    "roleRef": {"name": "cluster-admin"},
                    "subjects": [{"kind": "Group", "name": "ops"}],
                }
            ]
        }
        with (
            mock.patch.object(
                rbac,
                "kubectl_json",
                side_effect=[
                    {"items": []},
                    {"items": []},
                    cluster_bindings,
                    {"items": []},
                    {"items": []},
                ],
            ),
            mock.patch.object(sys, "argv", ["check"]),
            redirect_stdout(io.StringIO()) as output,
        ):
            result = rbac.main()
        self.assertEqual(result, 0)
        self.assertIn("cluster-admin", output.getvalue())


class PodDiagnosticLogicTests(unittest.TestCase):
    def test_pending_and_image_pull_reasons(self):
        pod = {
            "status": {
                "phase": "Pending",
                "conditions": [
                    {
                        "type": "PodScheduled",
                        "status": "False",
                        "reason": "Unschedulable",
                        "message": "Insufficient cpu",
                    }
                ],
                "containerStatuses": [
                    {
                        "name": "api",
                        "state": {
                            "waiting": {
                                "reason": "ImagePullBackOff",
                                "message": "not found",
                            }
                        },
                    }
                ],
            }
        }
        reasons = pod_diagnostics.pod_problems(pod)
        self.assertTrue(any("Pending" in reason for reason in reasons))
        self.assertTrue(any("Insufficient cpu" in reason for reason in reasons))
        self.assertTrue(any("ImagePullBackOff" in reason for reason in reasons))


class SecurityAndRedactionLogicTests(unittest.TestCase):
    def test_control_plane_flag_parser(self):
        flags = control_plane.extract_flags(
            "- --anonymous-auth=false\n"
            "- --authorization-mode=Node,RBAC\n"
            "- --audit-log-path=/var/log/kubernetes/audit.log\n"
        )
        self.assertEqual(flags["anonymous-auth"], "false")
        self.assertEqual(flags["authorization-mode"], "Node,RBAC")

    def test_encryption_provider_order(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "encryption.yaml"
            path.write_text(
                "providers:\n"
                "  - aescbc:\n"
                "      keys: []\n"
                "  - identity: {}\n"
            )
            ok, summary = control_plane.encryption_provider_summary(path)
            self.assertTrue(ok)
            self.assertIn("aescbc", summary)

    def test_support_bundle_redaction(self):
        text = (
            "server=10.20.30.40 ipv6=2001:db8::1 user=admin@example.com "
            "password=SuperSecret token=abc123"
        )
        result = support_bundle.redact(text)
        self.assertNotIn("10.20.30.40", result)
        self.assertNotIn("2001:db8::1", result)
        self.assertNotIn("admin@example.com", result)
        self.assertNotIn("SuperSecret", result)
        self.assertNotIn("abc123", result)


if __name__ == "__main__":
    unittest.main()
