"""Sanity checks for reversible shell alias packs."""

from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ALIAS_DIR = ROOT / "playbooks" / "files" / "shell-aliases"
PLAYBOOKS = ROOT / "playbooks"

PACKS = (
    "kubectl",
    "helm",
    "docker",
    "git",
    "system",
    "python",
    "virt",
    "helpers",
    "sysupdate",
)

REQUIRED_SNIPPETS = {
    "kubectl": ("alias kgpa=", "ksh()", "kdrain()"),
    "helm": ("alias hla=", "hrback()"),
    "docker": ("dprune()", "dprune --yes"),
    "git": ("alias gs=", "gca()", "gundo()"),
    "system": ("alias ll=", "aptin()", "alias install="),
    "python": ("alias py=", "venv()", "activate()"),
    "virt": ("vm-on()", "vm-off()", "disown"),
    "helpers": ("duh()", "whoport()", "bak()", "extract()"),
    "sysupdate": ("sysupdate()", "apt upgrade -y", "snap refresh"),
}


class ShellAliasPackTests(unittest.TestCase):
    def test_all_pack_files_exist(self):
        for pack in PACKS:
            path = ALIAS_DIR / f"{pack}.sh"
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_pack_files_parse_with_bash_n(self):
        for pack in PACKS:
            path = ALIAS_DIR / f"{pack}.sh"
            result = subprocess.run(
                ["bash", "-n", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_required_snippets(self):
        for pack, snippets in REQUIRED_SNIPPETS.items():
            text = (ALIAS_DIR / f"{pack}.sh").read_text(encoding="utf-8")
            for snippet in snippets:
                if pack == "system" and snippet == "alias install=":
                    self.assertNotIn(snippet, text)
                    continue
                self.assertIn(snippet, text, f"{pack} missing {snippet}")

    def test_dangerous_docker_prune_is_not_a_bare_alias(self):
        text = (ALIAS_DIR / "docker.sh").read_text(encoding="utf-8")
        self.assertNotIn("alias dprune=", text)

    def test_playbooks_and_docs_exist(self):
        mapping = {
            "43_install_kubectl_aliases": "kubectl",
            "44_install_helm_aliases": "helm",
            "45_install_docker_aliases": "docker",
            "46_install_git_aliases": "git",
            "47_install_system_aliases": "system",
            "48_install_python_aliases": "python",
            "49_install_virt_aliases": "virt",
            "50_install_helper_functions": "helpers",
            "51_install_sysupdate_function": "sysupdate",
        }
        for playbook_stem, pack in mapping.items():
            playbook = PLAYBOOKS / f"{playbook_stem}.yml"
            doc = ROOT / "docs" / f"{playbook_stem}.md"
            self.assertTrue(playbook.is_file(), playbook)
            self.assertTrue(doc.is_file(), doc)
            body = playbook.read_text(encoding="utf-8")
            self.assertIn(f"shell_aliases_pack: {pack}", body)
            self.assertIn("shell_aliases_state: present", body)
            self.assertIn(f"files/shell-aliases/{pack}.sh", body)

    def test_remove_playbook_exists(self):
        self.assertTrue((PLAYBOOKS / "53_remove_shell_aliases.yml").is_file())
        self.assertTrue((ROOT / "docs" / "53_remove_shell_aliases.md").is_file())
        self.assertTrue((ROOT / "docs" / "tr" / "53_remove_shell_aliases.md").is_file())


if __name__ == "__main__":
    unittest.main()
