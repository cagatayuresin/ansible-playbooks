# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Kubernetes etcd backup, large file check, and external endpoint connectivity playbooks (29-31).
- etcd restore verification, Kubernetes upgrade readiness, workload resilience, Service/EndpointSlice, Pod Security, RBAC, control-plane security, pod diagnostics, node drift, patch/reboot, and support bundle playbooks (32-42).
- CI checks for the example inventory, helper script syntax, playbook/document mapping, and Kubernetes upgrade version policy.
- Explicit etcd snapshot retention configuration.

### Changed
- Secured etcd backup directory and snapshot permissions and corrected its state-changing label.
- Pinned the default Metrics Server manifest to v0.8.1.
- Enforced Kubernetes target version format and supported upgrade range before package changes.
- Pinned CI tool versions and corrected CI to use the tracked example inventory.
- Updated installation steps and playbook counts.
- Migrated GitHub Pages from Minimal to a pinned Just the Docs theme with
  wider content, ordered navigation, search, and code-copy controls.

### Fixed
- Handled nullable EndpointSlice fields without crashing and stopped masking helper execution errors in playbook 35.
- Made the etcd snapshot selection unit test deterministic across filesystems
  with coarse timestamp resolution.
- Escaped Docker's Go-template example so Jekyll does not parse it as Liquid.

## [1.0.0] - 2026-07-30

### Added
- Initial release of Ansible Playbooks for Kubernetes and Server management.
- 28 different playbooks for health checks, reporting, and maintenance.
- Extensive documentation in the `docs/` folder.
- GitHub Actions CI workflow for linting.
- GitHub Pages support configuration.
