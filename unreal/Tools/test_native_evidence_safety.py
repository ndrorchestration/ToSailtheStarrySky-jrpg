"""Source-only negative controls for non-destructive native verification handoff.

These assertions do not execute PowerShell, UnrealBuildTool or Unreal Editor.
They guard against regressions that erase prior native automation evidence or
make an unpinned working tree appear to be an accepted integration review.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "Tools/Verify-Unreal.ps1"
MANUAL = ROOT / "Docs/FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md"
INTEGRATION = ROOT / "Docs/INTEGRATION_GATE_2026-11-02.md"


def check_script(script: str) -> None:
    mandatory = (
        "[Parameter(Mandatory=$true)][string]$EngineRoot",
        "[string]$ExpectedHead = ''",
        "ExpectedHead must be a full 40-character Git commit SHA",
        "actual=$GitHead expected=$ExpectedHead",
        "Working tree has uncommitted changes",
        "[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')",
        "[guid]::NewGuid().ToString('N').Substring(0, 8)",
        "$Evidence = Join-Path $EvidenceRoot $RunId",
        "New-Item -Path $EvidenceRoot -ItemType Directory -Force",
        "if (Test-Path $Evidence) { throw",
        "New-Item -Path $Evidence -ItemType Directory -ErrorAction Stop",
        "$GitHead | Set-Content (Join-Path $Evidence 'head.txt')",
        "Join-Path $Evidence 'build.log'",
        "Join-Path $Evidence 'automation.log'",
        "if (Test-Path $ReportDirectory) { throw",
        "New-Item -Path $ReportDirectory -ItemType Directory -ErrorAction Stop",
        "AutomationReport/index.json",
        "if ($Matches.Count -ne 1)",
        "if ($Matches[0].state -ne 'Success')",
        "Repository HEAD changed during verification",
        "Working tree changed during verification",
        "Evidence retained at $Evidence",
    )
    if re.search(r'\bRemove-Item\b|\bClear-Content\b|\bMove-Item\b', script):
        raise ValueError("Native verifier contains a destructive evidence action")
    for token in mandatory:
        if token not in script:
            raise ValueError("Unsafe or unverifiable native review script: " + token)
    if script.count("TSTSS.FirstWake.ReviewObjectivesAreReadOnly") != 1:
        raise ValueError("First Wake objective native test declaration lost or duplicated")
    # Ensure SHA and clean tree are checked before any fresh evidence is written.
    if not (script.index("ExpectedHead -ne") < script.index("status --porcelain") <
            script.index("New-Item -Path $EvidenceRoot")):
        raise ValueError("Source custody check does not precede evidence creation")
    # No prior per-run directory may be reused, and the report is nested under it.
    if not (script.index("$Evidence = Join-Path $EvidenceRoot $RunId") <
            script.index("$ReportDirectory = Join-Path $Evidence 'AutomationReport'")):
        raise ValueError("Per-run automation report is not isolated")


class NativeEvidenceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.code = VERIFIER.read_text(encoding="utf-8")

    def reject(self, code, reason):
        with self.assertRaisesRegex(ValueError, reason):
            check_script(code)

    def test_exact_source_contract(self):
        check_script(self.code)

    def test_do_not_allow_recursive_report_deletion(self):
        altered = self.code.replace(
            "if (Test-Path $ReportDirectory) { throw 'Review automation evidence collision; refusing overwrite' }",
            "if (Test-Path $ReportDirectory) { Remove-Item $ReportDirectory -Recurse -Force }",
        )
        self.reject(altered, "destructive evidence")

    def test_expected_sha_gate_is_required(self):
        altered = self.code.replace("[string]$ExpectedHead = ''", "")
        self.reject(altered, "ExpectedHead")

    def test_unsafe_static_evidence_reuse_is_rejected(self):
        altered = self.code.replace("$Evidence = Join-Path $EvidenceRoot $RunId",
                                    "$Evidence = $EvidenceRoot")
        self.reject(altered, "Unsafe or unverifiable")

    def test_disabled_clean_tree_check_is_rejected(self):
        altered = self.code.replace("Working tree has uncommitted changes",
                                    "Working tree ignored")
        self.reject(altered, "Working tree")

    def test_duplicate_native_name_is_rejected(self):
        altered = self.code.replace(
            "'TSTSS.FirstWake.ReviewObjectivesAreReadOnly',",
            "'TSTSS.FirstWake.ReviewObjectivesAreReadOnly',\n    'TSTSS.FirstWake.ReviewObjectivesAreReadOnly',",
        )
        self.reject(altered, "lost or duplicated")

    def test_manual_pie_remains_not_executed(self):
        doc = MANUAL.read_text(encoding="utf-8")
        self.assertIn("CASE_RESULTS=P01:NOT_TESTED,...,P13:NOT_TESTED", doc)
        self.assertIn("MAIN_MERGE=NOT_AUTHORIZED", doc)
        self.assertIn("first_wake_quick", doc)
        self.assertIn("tstss_prelude_pie_quick", doc)

    def test_combined_review_does_not_claim_engine_execution(self):
        doc = INTEGRATION.read_text(encoding="utf-8")
        self.assertRegex(doc, r"25 distinct successful named\s+native automation results")
        self.assertIn("P01–P13", doc)
        self.assertIn("NOT MERGED", doc)
        self.assertIn("NOT PLAYABLE-CERTIFIED", doc)


if __name__ == "__main__":
    unittest.main()
