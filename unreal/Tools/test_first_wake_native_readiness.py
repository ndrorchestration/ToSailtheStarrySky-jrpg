"""Source-only negative fixtures for the PR769 machine-readiness gate.

No Git mutation, subprocess, process launch or actual SaveGame access.
"""
import unittest
from pathlib import Path
from check_first_wake_native_readiness import (
    APPROVED_ROOT, EXPECTED_MAP_SHA, evaluate
)

SHA = "39856193942580826c26ac73828e8cd7f001b34e"


def good_inputs() -> dict:
    return {
        "root_name": APPROVED_ROOT, "git_root_matches": True,
        "git_head": SHA, "git_clean": True,
        "map_sha": EXPECTED_MAP_SHA, "engine_version": [5, 8, 4],
        "engine_exes": True,
        "native_names": [f"TSTSS.TestCase{i:02d}" for i in range(38)],
        "save_files": [], "native_receipts": ["synthetic-candidate"],
        "map_receipts": ["synthetic-candidate"],
        "active": [], "free_ram_gib": 7.1, "free_disk_gib": 16.0,
        "errors": [],
    }


class FirstWakeNativeReadinessNegativeFixtures(unittest.TestCase):
    def result(self, phase="build", **mutations):
        params = good_inputs()
        params.update(mutations)
        return evaluate(params, SHA, phase)

    def test_clean_build_gate_passes_without_claiming_native(self):
        report = self.result()
        self.assertEqual(report["status"], "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")
        self.assertFalse(report["native_build_or_tests_executed"])
        self.assertFalse(report["player_save_changed"])
        self.assertFalse(report["receipt_files_written"])

    def test_pie_requires_evidence_candidates_without_validating_them(self):
        report = self.result(phase="pie")
        self.assertEqual(report["status"], "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")
        self.assertEqual(report["native_receipt_candidates"], 1)
        self.assertEqual(report["map_receipt_candidates"], 1)
        self.assertFalse(report["native_build_or_tests_executed"])

    def test_unapproved_directory_refused(self):
        self.assertEqual(self.result(root_name="C_Unsafe")["status"], "HOLD")

    def test_explicit_map_repair_root_allowed_only_when_all_other_gates_pass(self):
        from check_first_wake_native_readiness import MAP_REPAIR_ROOT
        self.assertEqual(self.result(root_name=MAP_REPAIR_ROOT)["status"],
                         "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")
        self.assertEqual(self.result(root_name=MAP_REPAIR_ROOT + "_copy")["status"], "HOLD")
        self.assertEqual(self.result(root_name=MAP_REPAIR_ROOT, git_clean=False)["status"], "HOLD")

    def test_marker_save_join_root_stays_exact_and_clean(self):
        from check_first_wake_native_readiness import MARKER_SAVE_JOIN_ROOT
        self.assertEqual(self.result(root_name=MARKER_SAVE_JOIN_ROOT)["status"],
                         "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")
        self.assertEqual(self.result(root_name=MARKER_SAVE_JOIN_ROOT + "_copy")["status"], "HOLD")
        self.assertEqual(self.result(root_name=MARKER_SAVE_JOIN_ROOT, git_clean=False)["status"], "HOLD")

    def test_wrong_sha_refused(self):
        self.assertEqual(self.result(git_head="0" * 40)["status"], "HOLD")

    def test_dirty_worktree_refused(self):
        self.assertEqual(self.result(git_clean=False)["status"], "HOLD")

    def test_map_changed_refused(self):
        self.assertEqual(self.result(map_sha="0" * 64)["status"], "HOLD")

    def test_wrong_engine_refused(self):
        self.assertEqual(self.result(engine_version=[5, 8, 3])["status"], "HOLD")

    def test_invalid_native_test_count_refused(self):
        self.assertEqual(self.result(native_names=["TSTSS.OnlyOne"])["status"], "HOLD")

    def test_duplicate_names_refused(self):
        names = good_inputs()["native_names"]
        names[-1] = names[0]
        self.assertEqual(self.result(native_names=names)["status"], "HOLD")

    def test_existing_review_save_refused(self):
        report = self.result(save_files=["tstss_prelude_pie_quick.sav"])
        self.assertEqual(report["status"], "HOLD")
        self.assertEqual(report["existing_review_save_count"], 1)

    def test_editor_active_refused(self):
        self.assertEqual(self.result(active=["UnrealEditor"])["status"], "HOLD")

    def test_missing_machine_telemetry_refused(self):
        self.assertEqual(self.result(active=None, free_ram_gib=None)["status"], "HOLD")

    def test_build_has_five_gib_gate(self):
        self.assertEqual(self.result(free_ram_gib=4.9)["status"], "HOLD")
        self.assertEqual(self.result(free_ram_gib=5.1)["status"],
                         "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")

    def test_pie_has_six_point_five_gib_gate(self):
        self.assertEqual(self.result(phase="pie", free_ram_gib=6.4)["status"], "HOLD")
        self.assertEqual(self.result(phase="pie", free_ram_gib=6.6)["status"],
                         "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")

    def test_disk_lower_than_fourteen_gib_refused(self):
        self.assertEqual(self.result(free_disk_gib=13.9)["status"], "HOLD")

    def test_no_native_receipts_refuses_pie_but_not_build(self):
        self.assertEqual(self.result(phase="pie", native_receipts=[])["status"], "HOLD")
        self.assertEqual(self.result(native_receipts=[])["status"],
                         "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE")

    def test_no_map_receipt_refuses_pie(self):
        self.assertEqual(self.result(phase="pie", map_receipts=[])["status"], "HOLD")

    def test_probe_source_has_no_destructive_file_or_editor_operations(self):
        code = (Path(__file__).resolve().parent /
                "check_first_wake_native_readiness.py").read_text(encoding="utf-8")
        for forbidden in ("shutil.rmtree(", ".unlink(", "os.remove(", "Stop-Process",
                          "taskkill", "Start-Process", "delete_game_in_slot("):
            self.assertNotIn(forbidden, code)
        self.assertIn('return 0 if report["status"].startswith(', code)


if __name__ == "__main__":
    unittest.main()
