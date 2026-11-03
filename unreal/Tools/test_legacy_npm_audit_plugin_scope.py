"""Source-only safeguards for dated legacy npm audit and UE Python plugin review.

Checks receipt linkage and branch manifests, NOT live vulnerabilities, plugin
load behavior, packaged Unreal startup, license approval or remediation.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "unreal/Docs/LEGACY_NPM_SECURITY_AND_UE_PYTHON_PLUGIN_SCOPE_2026-11-02.md"
REGISTER = ROOT / "unreal/Docs/DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md"
BASELINE = ROOT / "unreal/Tools/dependency_baseline.json"
PROJECT = ROOT / "unreal/ToSailTheStarrySky.uproject"
LOCK = ROOT / "package-lock.json"
PACKAGE = ROOT / "package.json"
WORKFLOW = ROOT / ".github/workflows/unreal-source-preflight.yml"

LOCK_SHA_WINDOWS = "cbd32a793748f2aa7f6e538057ca4e38113ec229ce98a0854b312e386dd005f6"
LOCK_SHA_LF = "f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce"
PARENT_HEAD = "4e4a40aed34c0ff6789ce4a69ca757f75139fee2"
RISK_COUNTS = ("32", "3 critical", "15 high", "14 moderate")


def check_document_claims(text: str) -> bool:
    must_retain = (
        "READ-ONLY EVIDENCE / REMEDIATION HOLD",
        PARENT_HEAD,
        LOCK_SHA_WINDOWS,
        LOCK_SHA_LF,
        "nwjs@0.0.15",
        "nw-builder@4.2.1",
        "Do not run `npm audit fix` automatically.",
        "not",  # A negative-control suite checks the stronger hold phrase below.
        "no exploitable shipping path",
        "Runtime",
        "UncookedOnly",
        "PythonScriptPluginPreload",
        "EnabledByDefault: false",
        "no dependency",
        "NOT INSPECTED",
        "without editing",
    )
    for item in must_retain:
        if item not in text:
            raise ValueError("Missing dated audit evidence/hold: " + item)
    for group in RISK_COUNTS:
        if group not in text:
            raise ValueError("Dated audit package-count claim changed: " + group)
    if "No package/lockfile was installed, upgraded, downgraded or modified;" not in text:
        raise ValueError("No-install/no-update evidence boundary changed")
    if "no remediation tested" not in text:
        raise ValueError("Audit must not claim completed remediation")
    return True


class LegacyNpmSecurityScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = AUDIT.read_text(encoding="utf-8")
        cls.register = REGISTER.read_text(encoding="utf-8")
        cls.project = json.loads(PROJECT.read_text(encoding="utf-8"))
        cls.base = json.loads(BASELINE.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_document_is_a_dated_read_only_observation(self):
        self.assertTrue(check_document_claims(self.text))
        self.assertEqual(self.text.count("# Legacy npm security triage"), 1)

    def test_source_lock_is_exact_audited_version_not_changed(self):
        raw = LOCK.read_bytes()
        # Git on Windows may materialize CRLF while Linux Actions checks out LF.
        # Validate the canonical LF content AND the appropriate platform
        # working-tree byte receipt; never weaken the audited dependency graph.
        normalized = raw.replace(b"\\r\\n", b"\\n")
        self.assertEqual(hashlib.sha256(normalized).hexdigest(), LOCK_SHA_LF)
        raw_expected = LOCK_SHA_WINDOWS if b"\\r\\n" in raw else LOCK_SHA_LF
        self.assertEqual(hashlib.sha256(raw).hexdigest(), raw_expected)
        self.assertEqual(self.package["devDependencies"], self.lock["packages"][""]["devDependencies"])
        self.assertTrue(self.package["private"])
        self.assertEqual(self.lock["lockfileVersion"], 3)

    def test_real_declared_direct_legacy_dependencies_are_separate_from_unreal(self):
        self.assertEqual(set(self.package["devDependencies"]), {"nw", "nwjs", "nw-builder", "playwright"})
        self.assertEqual(self.base["unreal"]["runtime_module_dependencies"],
                         ["Core", "CoreUObject", "Engine", "InputCore"])
        self.assertEqual(self.base["unreal"]["third_party_runtime_packages_added"], [])

    def test_plugin_baseline_cannot_be_mislabeled_universal(self):
        enabled = sorted(p["Name"] for p in self.project.get("Plugins", []) if p.get("Enabled"))
        self.assertEqual(enabled, ["PythonScriptPlugin"])
        self.assertEqual(self.base["unreal"]["enabled_project_plugins"], enabled)
        self.assertIn("no explicit Plugins array", self.register.replace("`", ""))
        self.assertIn("Runtime", self.text)
        self.assertIn("UncookedOnly", self.text)
        self.assertFalse(self.base["policy"]["merge_or_release_authorized"])

    def test_source_ci_checks_dated_audit_document_changes(self):
        w = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("- 'unreal/Docs/LEGACY_NPM_SECURITY_AND_UE_PYTHON_PLUGIN_SCOPE_2026-11-02.md'", w)
        self.assertIn("test_legacy_npm_audit_plugin_scope.py", w)

    def test_mutant_removing_no_auto_fix_hold_is_rejected(self):
        broken = self.text.replace("Do not run `npm audit fix` automatically.", "Apply npm fixes automatically.")
        with self.assertRaisesRegex(ValueError, "Missing"):
            check_document_claims(broken)

    def test_mutant_obscuring_runtime_module_is_rejected(self):
        broken = self.text.replace("PythonScriptPluginPreload", "EditorPythonOnly")
        with self.assertRaisesRegex(ValueError, "Missing"):
            check_document_claims(broken)

    def test_mutant_claiming_remediation_was_done_is_rejected(self):
        broken = self.text.replace("no remediation tested", "remediation tested and accepted")
        with self.assertRaisesRegex(ValueError, "completed remediation"):
            check_document_claims(broken)


if __name__ == "__main__":
    unittest.main()
