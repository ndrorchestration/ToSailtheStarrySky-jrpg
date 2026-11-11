"""Engine-free bounded tests for the First Wake multi-path shore compositor.

No tests execute Editor Python, import Unreal, launch a child or change saves.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_first_wake_multipath_shore as stage
import run_first_wake_multipath_native as host


class FirstWakeMultiPathShoreSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = stage.evidence_plan()

    def test_plan_is_original_hash_bound_and_review_only(self):
        p = self.plan
        self.assertEqual("tstss.shore.multipath.review.v1", p["schema"])
        self.assertEqual("UE 5.8.4", p["engine"])
        self.assertEqual("316299925275785494d1ec7b082f20007fa0f889f50ce59ea1c7e977ef942726",
                         p["source_sha256"])
        self.assertEqual(stage.SOURCE_PACKAGE, p["source_package"])
        self.assertNotEqual(p["source_package"], p["new_map"])
        self.assertTrue(p["new_map"].startswith("/Game/TSTSS/Review/"))
        self.assertFalse(any(p[key] for key in
            ("real_combat_executed", "runtime_transition_implemented",
             "spell_mastery_granted", "equipment_granted", "lyra_recruited",
             "live_quest_modified", "PIE_verified", "visual_approved",
             "native_staged")))
        self.assertTrue(p["review_only"])

    def test_all_three_visual_groups_and_26_new_actors(self):
        self.assertEqual((22, 8), (self.plan["original_object_imports"],
                                   self.plan["showcase_object_actors"]))
        self.assertEqual((14, 3), (self.plan["catalogued_gear"],
                                   self.plan["showcase_gear_actors"]))
        self.assertEqual(9, self.plan["preview_vfx_actors"])
        self.assertEqual(3, self.plan["enemy_silhouette_actors"])
        self.assertEqual(26, self.plan["total_new_review_actors"])
        self.assertEqual({"HarmonicShear", "AetherLeakWisp", "DockSkitter"},
                         set(stage.ENEMY_KINDS))
        self.assertEqual(9, len(set(
            row["VfxCueId"] for row in json.loads(stage.MAGIC.read_text(encoding="utf-8"))
        )))

    def test_all_three_review_equipment_assets_are_native_static_mesh_files(self):
        data = json.loads(
            (stage.EQUIPMENT / "party_equipment_manifest.review.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in data["entries"]}
        for ident in stage.GEAR_SHOWCASE:
            with self.subTest(ident=ident):
                package = stage.gear_package(by_id[ident])
                self.assertTrue(package.startswith("/Game/TSTSS/Review/PartyEquipment/"))
                file = stage.PROJECT / ("Content/" + package.removeprefix("/Game/") + ".uasset")
                self.assertTrue(file.is_file(), str(file))
                self.assertFalse(by_id[ident]["runtime_equippable"])

    def test_changed_source_map_digest_fails_closed(self):
        original_digest = stage.digest

        def tamper(path):
            if Path(path) == stage.MAP_FILE:
                return "0" * 64
            return original_digest(Path(path))

        with mock.patch.object(stage, "digest", side_effect=tamper):
            with self.assertRaisesRegex(RuntimeError, "map hash/readback drift"):
                stage.evidence_plan()

    def test_missing_exact_head_fails_before_editor_import(self):
        with mock.patch.dict(os.environ, {"TSTSS_MP_EXPECTED_HEAD": "invalid",
                                           "TSTSS_MP_STAGE_EXPLICIT": "1"}):
            with self.assertRaisesRegex(RuntimeError, "exact-head"):
                stage.check_native_custody()

    def test_no_implicit_host_staging_or_dirty_worktree(self):
        sha = "d" * 40

        def clean_git(*arguments):
            return {("branch", "--show-current"): stage.BRANCH,
                    ("rev-parse", "HEAD"): sha,
                    ("status", "--porcelain"): ""}[arguments]

        with mock.patch.object(stage.sys, "platform", "win32"), mock.patch.object(
            stage, "git", side_effect=clean_git
        ):
            with mock.patch.dict(os.environ, {"TSTSS_MP_EXPECTED_HEAD": sha,
                                               "TSTSS_MP_STAGE_EXPLICIT": ""}):
                with self.assertRaisesRegex(RuntimeError, "explicit host permission"):
                    stage.check_native_custody()

            def dirty_git(*arguments):
                if arguments == ("status", "--porcelain"):
                    return " M unreal/Config/DefaultInput.ini"
                return clean_git(*arguments)

            with mock.patch.object(stage, "git", side_effect=dirty_git), mock.patch.dict(
                os.environ, {"TSTSS_MP_EXPECTED_HEAD": sha,
                             "TSTSS_MP_STAGE_EXPLICIT": "1"}
            ):
                with self.assertRaisesRegex(RuntimeError, "dirty or changed"):
                    stage.check_native_custody()

    def test_host_rejects_unsafe_sha_and_does_not_start_ue(self):
        with mock.patch.object(host.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(RuntimeError, "exact 40-hex"):
                host.prerequisites("bad-sha")
            popen.assert_not_called()

    def test_native_visual_launcher_rejects_missing_exact_head_receipt(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Tools").mkdir()
            (root / "Tools/Verify-Unreal.ps1").write_text(
                (stage.PROJECT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8"),
                encoding="utf-8")
            with mock.patch.object(host, "PROJECT", root):
                with self.assertRaisesRegex(RuntimeError, "no native UHT"):
                    host.verified_native_receipt("f" * 40)

    def test_native_receipt_refuses_stale_head_and_forged_hash(self):
        import hashlib
        import re
        import tempfile
        required = re.findall(
            r"^\s*'(TSTSS\.[^']+)'",
            (stage.PROJECT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8"),
            re.M)
        self.assertEqual(35, len(required))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Tools").mkdir()
            (root / "Tools/Verify-Unreal.ps1").write_text(
                (stage.PROJECT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8"),
                encoding="utf-8")
            evidence = root / "Saved/MigrationEvidence/synthetic-rejection"
            (evidence / "AutomationReport").mkdir(parents=True)
            stale_head = "e" * 40
            (evidence / "head.txt").write_text(stale_head + "\n")
            (evidence / "build.log").write_text("synthetic - not a native build")
            (evidence / "automation.log").write_text("synthetic - not real UE")
            report = evidence / "AutomationReport/index.json"
            report.write_text(json.dumps({
                "succeeded": 35, "failed": 0, "notRun": 0,
                "tests": [{"fullTestPath": name, "state": "Success"} for name in required],
            }), encoding="utf-8")
            receipt = evidence / "verified-native.json"
            metadata = {
                "status": "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE",
                "source_sha": stale_head, "unreal_version": "5.8.4",
                "required_native_tests": 35,
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "pie_player_input": "NOT_TESTED", "visual_approval": "NOT_TESTED",
            }
            receipt.write_text(json.dumps(metadata), encoding="utf-8")
            with mock.patch.object(host, "PROJECT", root):
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt("f" * 40)
                metadata["report_sha256"] = "0" * 64
                receipt.write_text(json.dumps(metadata), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt(stale_head)

    def test_source_holds_all_review_runtime_boundaries(self):
        source = Path(stage.__file__).read_text(encoding="utf-8")
        runner = Path(host.__file__).read_text(encoding="utf-8")
        for term in ("get_dirty_map_packages", "get_dirty_content_packages",
                     "does_directory_exist(DEST_ROOT)", "duplicate_asset(SOURCE_PACKAGE, DEST_MAP)",
                     "get_all_level_actors", "save_map(world, DEST_MAP)",
                     "get_editor_property", "set_actor_enable_collision(False)",
                     "configs_unchanged"):
            # Source compositor checks configs via a different key than host receipt.
            if term == "configs_unchanged":
                self.assertIn(term, runner)
            else:
                self.assertIn(term, source)
        self.assertIn('create_asset', Path(stage.PROJECT / "Tools/build_ender_resonator_preview.py").read_text())
        self.assertIn('"TSTSS_MP_STAGE_EXPLICIT"', source)
        self.assertIn("current_editor_processes()", runner)
        self.assertIn("MAX_BUILD_SECONDS", runner)
        self.assertIn("child.terminate()", runner)
        self.assertIn("BELOW_NORMAL_PRIORITY_CLASS", runner)
        self.assertNotIn("TryUseDataTable(", source)
        self.assertNotIn("SaveGameToSlot(", source)
        self.assertNotIn("open_level", source.lower())

    def test_review_map_will_not_overwrite_originals_or_import_a_mission(self):
        self.assertTrue(stage.DEST_MAP.startswith(stage.DEST_ROOT))
        self.assertFalse(stage.SOURCE_PACKAGE.startswith(stage.DEST_ROOT))
        self.assertTrue(stage.OBJ_DEST.startswith(stage.DEST_ROOT))
        self.assertIn("NoAuthorizedCast_", Path(stage.__file__).read_text())
        self.assertIn("EnemyVisual_NoEncounter_", Path(stage.__file__).read_text())
        self.assertIn("StaticGear_NotEquipped_", Path(stage.__file__).read_text())
        self.assertIn("Lyra.WaterFocus", stage.GEAR_SHOWCASE)
        self.assertEqual(35, json.loads(stage.INTEGRATION.read_text())["required_native_names"])


if __name__ == "__main__":
    unittest.main()
