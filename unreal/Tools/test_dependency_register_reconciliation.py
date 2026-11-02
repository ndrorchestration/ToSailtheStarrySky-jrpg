"""Review-only controls for the consolidated Unreal dependency/evidence register.

No network, engine startup, installs, vulnerability scans, or auto-merges.
These checks bind claims to this branch's *declared* manifests only.
"""
from pathlib import Path
import json
import unittest

from check_dependency_contract import validate

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "unreal/Docs/DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md"
BASELINE = ROOT / "unreal/Tools/dependency_baseline.json"
PROJECT = ROOT / "unreal/ToSailTheStarrySky.uproject"
WORKFLOW = ROOT / ".github/workflows/unreal-source-preflight.yml"

PR_REFS = ("#657", "#699", "#704", "#705", "#707", "#708", "#709")


def check_review_register(text: str, baseline: dict, project: dict) -> None:
    """Fail closed if this branch overstates acceptance or hides plugin divergence."""
    required = (
        "Review-candidate register: this file, in a draft branch only.",
        "no explicit `Plugins` array",
        "enabled_project_plugins=[\"PythonScriptPlugin\"]",
        "Do not auto-merge the three PRs.",
        "A green check in one lineage does not establish its content on another.",
        "black-sky",
        "continuous",
        "release",
        "Starbourne/Orbiter",
        "security audit",
        "SOURCE / GAME BUILD / EDITOR BUILD / NAMED TEST JSON / CLEAN TREE",
    )
    for token in (*required, *PR_REFS):
        if token not in text:
            raise ValueError("Reconciliation claim or review gate missing: " + token)
    if text.count("## Consolidation decision and merge boundaries") != 1:
        raise ValueError("Consolidation decision must have one top-level section")
    if text.count("## Dependency baseline: what the repository really declares") != 1:
        raise ValueError("Preserve the source dependency register, not a duplicate")
    plugins = sorted(
        p["Name"] for p in project.get("Plugins", []) if p.get("Enabled") is True
    )
    expected = sorted(baseline["unreal"]["enabled_project_plugins"])
    if plugins != expected:
        raise ValueError("Source manifest and branch-scoped baseline differ")
    if plugins != ["PythonScriptPlugin"]:
        raise ValueError("This register's explicit plugin-variant statements need review")
    if project.get("EngineAssociation") != baseline["engine"]["association"]:
        raise ValueError("Unreal engine family drift")
    if baseline["policy"].get("auto_upgrade") is not False:
        raise ValueError("Unexpected dependency upgrade authorization")
    if baseline["policy"].get("merge_or_release_authorized") is not False:
        raise ValueError("Unexpected merge/release authorization")


class ReconciliationRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = REGISTER.read_text(encoding="utf-8")
        cls.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        cls.project = json.loads(PROJECT.read_text(encoding="utf-8"))

    def test_source_inventory_and_review_register_agree(self):
        actual = validate(ROOT)
        self.assertEqual(actual["enabled_project_plugins"], ["PythonScriptPlugin"])
        self.assertFalse(actual["runtime_build_executed"])
        self.assertFalse(actual["dependency_security_scan_executed"])
        self.assertFalse(actual["production_upgrade_authorized"])
        check_review_register(self.doc, self.baseline, self.project)

    def test_ci_checks_register_only_as_source_evidence(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("- 'unreal/Docs/DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md'", workflow)
        self.assertIn("test_dependency_register_reconciliation.py", workflow)
        self.assertIn("test_dependency_contract.py", workflow)

    def test_missing_draft_reference_is_rejected(self):
        changed = self.doc.replace("#709", "unlinked alternate review")
        with self.assertRaisesRegex(ValueError, "missing"):
            check_review_register(changed, self.baseline, self.project)

    def test_missing_cross_branch_no_merge_hold_is_rejected(self):
        changed = self.doc.replace(
            "Do not auto-merge the three PRs.", "Merge the three PRs automatically."
        )
        with self.assertRaisesRegex(ValueError, "missing"):
            check_review_register(changed, self.baseline, self.project)

    def test_wrong_unreal_project_plugin_set_is_rejected(self):
        project = dict(self.project)
        project.pop("Plugins", None)
        with self.assertRaisesRegex(ValueError, "baseline differ"):
            check_review_register(self.doc, self.baseline, project)

    def test_baseline_plugin_change_is_rejected(self):
        baseline = json.loads(json.dumps(self.baseline))
        baseline["unreal"]["enabled_project_plugins"] = []
        with self.assertRaisesRegex(ValueError, "baseline differ"):
            check_review_register(self.doc, baseline, self.project)

    def test_unreviewed_upgrade_authorization_is_rejected(self):
        baseline = json.loads(json.dumps(self.baseline))
        baseline["policy"]["auto_upgrade"] = True
        with self.assertRaisesRegex(ValueError, "upgrade authorization"):
            check_review_register(self.doc, baseline, self.project)

    def test_unreviewed_merge_authorization_is_rejected(self):
        baseline = json.loads(json.dumps(self.baseline))
        baseline["policy"]["merge_or_release_authorized"] = True
        with self.assertRaisesRegex(ValueError, "merge/release authorization"):
            check_review_register(self.doc, baseline, self.project)


if __name__ == "__main__":
    unittest.main()
