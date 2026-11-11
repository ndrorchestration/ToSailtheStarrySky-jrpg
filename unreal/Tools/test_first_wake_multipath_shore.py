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

    def test_ue_python_enemy_enum_drops_cpp_e_prefix(self):
        from types import SimpleNamespace
        choices = SimpleNamespace(HARMONIC_SHEAR="shear", AETHER_LEAK_WISP="wisp",
                                  DOCK_SKITTER="skitter")
        ue = SimpleNamespace(TSTSSSliceEnemyKind=choices)
        values = stage.resolve_native_enemy_kinds(ue)
        self.assertEqual({"HarmonicShear":"shear", "AetherLeakWisp":"wisp",
                          "DockSkitter":"skitter"}, values)
        # The earlier real UE 5.8.4 stage failed here because it requested
        # the C++ E-prefixed name, which is not the Python export.
        with self.assertRaisesRegex(RuntimeError, "not exposed to Python"):
            stage.resolve_native_enemy_kinds(SimpleNamespace(
                ETSTSSSliceEnemyKind=choices))
        with self.assertRaisesRegex(RuntimeError, "missing DOCK_SKITTER"):
            stage.resolve_native_enemy_kinds(SimpleNamespace(
                TSTSSSliceEnemyKind=SimpleNamespace(
                    HARMONIC_SHEAR="shear", AETHER_LEAK_WISP="wisp")))
        with self.assertRaisesRegex(RuntimeError, "duplicated"):
            stage.resolve_native_enemy_kinds(SimpleNamespace(
                TSTSSSliceEnemyKind=SimpleNamespace(
                    HARMONIC_SHEAR="shear", AETHER_LEAK_WISP="wisp",
                    DOCK_SKITTER="shear")))

    def test_native_review_boolean_setter_is_explicit_and_fail_closed(self):
        class FakeActor:
            def __init__(self, supported):
                self.supported = supported
                self.data = {name: False for name in supported}
            def get_editor_property(self, name):
                if name not in self.data:
                    raise AttributeError(name)
                return self.data[name]
            def set_editor_property(self, name, value):
                if name not in self.data:
                    raise AttributeError(name)
                self.data[name] = value
        actor = FakeActor({"b_loop_review"})
        self.assertEqual("b_loop_review",
                         stage.set_required_review_bool(actor, "loop_review", True))
        self.assertTrue(actor.data["b_loop_review"])
        actor = FakeActor({"reduced_motion"})
        self.assertEqual("reduced_motion",
                         stage.set_required_review_bool(actor, "reduced_motion", True))
        with self.assertRaisesRegex(RuntimeError, "boolean missing"):
            stage.set_required_review_bool(FakeActor(set()), "loop_review", True)
        class BrokenActor(FakeActor):
            def set_editor_property(self, name, value):
                pass
        with self.assertRaisesRegex(RuntimeError, "did not stick"):
            stage.set_required_review_bool(BrokenActor({"b_loop_review"}), "loop_review", True)

    def test_source_locked_material_helper_requires_absolute_file(self):
        source = Path(stage.__file__).read_text(encoding="utf-8")
        self.assertIn('spec_from_file_location("tstss_review_material_source", helper)', source)
        self.assertIn('module.make_material()', source)
        self.assertIn('spec.loader.exec_module(module)', source)
        self.assertNotIn('from build_ender_resonator_preview import make_material', source)
        self.assertTrue((stage.PROJECT / "Tools/build_ender_resonator_preview.py").is_file())

    def test_two_process_map_duplication_avoids_ue_world_leak(self):
        source = Path(stage.__file__).read_text(encoding="utf-8")
        runner = Path(host.__file__).read_text(encoding="utf-8")
        self.assertIn('def build_native_shore(phase: str)', source)
        self.assertIn('if phase == "prepare":', source)
        self.assertIn('if not u.EditorLoadingAndSavingUtils.save_map(source_world, DEST_MAP):', source)
        self.assertIn('source_world = u.EditorLoadingAndSavingUtils.load_map(SOURCE_PACKAGE)', source)
        self.assertNotIn('u.EditorAssetLibrary.duplicate_asset(SOURCE_PACKAGE, DEST_MAP)', source)
        self.assertIn('PREPARE_RECEIPT.open("x"', source)
        self.assertIn("REVIEW_ASSETS_AND_BASE_MAP_PREPARED_NOT_PIE", source)
        self.assertIn('if phase == "compose" and (not PREPARE_RECEIPT.is_file()', source)
        self.assertIn('if phase == "compose" and not u.EditorAssetLibrary.does_directory_exist', source)
        self.assertLess(source.index("return receipt\n    # Phase two"),
                        source.index("world = u.EditorLoadingAndSavingUtils.load_map(DEST_MAP)"))
        self.assertIn('for phase in ("prepare", "compose"):', runner)
        self.assertIn('env["TSTSS_MP_PHASE"] = phase', runner)
        self.assertIn("PREPARE_LOG", runner)
        self.assertIn("PREPARE_STDOUT", runner)
        self.assertIn('if not stage.PREPARE_RECEIPT.is_file():', runner)
        self.assertIn("if current_editor_processes() or current_ubt_build_running():", runner)
        self.assertIn("separate composition process produced no native stage receipt", runner)
        self.assertIn("with HOST_RECEIPT.open(\"x\"", runner)

    def test_camera_python_rotator_fields_fail_closed(self):
        # Unreal Python's Rotator constructor is roll,pitch,yaw; the original
        # C++-ordered positional arguments created pitch +45, yaw 0, roll -18.
        stage_source = Path(stage.__file__).read_text(encoding="utf-8")
        self.assertIn("u.Rotator(roll=0.0, pitch=-18.0, yaw=45.0)", stage_source)
        self.assertNotIn("u.Rotator(-18, 45, 0)", stage_source)
        self.assertIn("HOLD: staged camera native pitch/yaw/roll mismatch", stage_source)
        self.assertIn("actual = camera.get_actor_rotation()", stage_source)
        self.assertIn("abs(actual.pitch + 18.0) > 0.01", stage_source)
        self.assertIn("abs(actual.yaw - 45.0) > 0.01", stage_source)
        self.assertIn("abs(actual.roll) > 0.01", stage_source)

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
        # Simulate the target Windows worktree on Linux CI without weakening
        # any gate in the actual staging implementation.
        with mock.patch.object(stage, "ROOT", Path("C:/" + stage.WORKTREE)), \
             mock.patch.object(stage.sys, "platform", "win32"), \
             mock.patch.dict(os.environ, {"TSTSS_MP_EXPECTED_HEAD": "invalid",
                                           "TSTSS_MP_STAGE_EXPLICIT": "1"}):
            with self.assertRaisesRegex(RuntimeError, "exact-head"):
                stage.check_native_custody()

    def test_no_implicit_host_staging_or_dirty_worktree(self):
        sha = "d" * 40

        def clean_git(*arguments):
            return {("branch", "--show-current"): stage.BRANCH,
                    ("rev-parse", "HEAD"): sha,
                    ("status", "--porcelain", "-uall"): ""}[arguments]

        with mock.patch.object(stage, "ROOT", Path("C:/" + stage.WORKTREE)), \
             mock.patch.object(stage.sys, "platform", "win32"), \
             mock.patch.object(stage, "git", side_effect=clean_git):
            with mock.patch.dict(os.environ, {"TSTSS_MP_EXPECTED_HEAD": sha,
                                               "TSTSS_MP_STAGE_EXPLICIT": ""}):
                with self.assertRaisesRegex(RuntimeError, "explicit host permission"):
                    stage.check_native_custody()

            def dirty_git(*arguments):
                if arguments == ("status", "--porcelain", "-uall"):
                    return " M unreal/Config/DefaultInput.ini"
                return clean_git(*arguments)

            with mock.patch.object(stage, "git", side_effect=dirty_git), mock.patch.dict(
                os.environ, {"TSTSS_MP_EXPECTED_HEAD": sha,
                             "TSTSS_MP_STAGE_EXPLICIT": "1"}
            ):
                with self.assertRaisesRegex(RuntimeError, "entirely clean source"):
                    stage.check_native_custody()

    def test_native_compose_allows_only_generated_review_artifacts(self):
        allowed = (
            "?? unreal/Content/TSTSS/Magic/M_ResonatorGlow.uasset\n"
            "?? unreal/Content/TSTSS/Review/MultipathV1/ObjectImports/Prop/Prop.uasset\n"
            "?? unreal/Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
        )
        with mock.patch.object(stage, "git", return_value=allowed):
            stage.assert_source_custody_for_phase("compose")
            with self.assertRaisesRegex(RuntimeError, "entirely clean source"):
                stage.assert_source_custody_for_phase("prepare")
        for drift in (
            allowed + "\n M unreal/Config/DefaultInput.ini",
            allowed + "\n?? unreal/Content/TSTSS/Review/VerticalSlice/Another.umap",
            "?? unreal/Content/TSTSS/Magic/OtherMaterial.uasset",
        ):
            with mock.patch.object(stage, "git", return_value=drift):
                with self.assertRaisesRegex(RuntimeError, "unexpected tracked/untracked"):
                    stage.assert_source_custody_for_phase("compose")

    def test_host_rejects_unsafe_sha_and_does_not_start_ue(self):
        with mock.patch.object(host.sys, "platform", "win32"), \
             mock.patch.object(host.subprocess, "Popen") as popen:
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

    def test_visual_stage_ubt_check_holds_busy_or_unreadable_process_state(self):
        from types import SimpleNamespace
        with mock.patch.object(host.subprocess, "run") as run:
            run.return_value = SimpleNamespace(returncode=0, stdout="IDLE\n")
            self.assertFalse(host.current_ubt_build_running())
            self.assertEqual("powershell", run.call_args.args[0][0])
            self.assertIn("UnrealBuildTool", run.call_args.args[0][-1])
            run.return_value = SimpleNamespace(returncode=0, stdout="BUSY\n")
            self.assertTrue(host.current_ubt_build_running())
            run.return_value = SimpleNamespace(returncode=1, stdout="IDLE\n")
            with self.assertRaisesRegex(RuntimeError, "unable to reliably inspect"):
                host.current_ubt_build_running()
            run.return_value = SimpleNamespace(returncode=0, stdout="UNKNOWN\n")
            with self.assertRaisesRegex(RuntimeError, "unable to reliably inspect"):
                host.current_ubt_build_running()

    def test_secondary_receipt_requires_exact_total_and_all_successful_rows(self):
        import hashlib
        import re
        import tempfile
        expected = "a" * 40
        required_source = (stage.PROJECT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
        required = re.findall(r"^\s*'(TSTSS\.[^']+)'", required_source, re.M)
        self.assertEqual(35, len(required))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Tools").mkdir()
            (root / "Tools/Verify-Unreal.ps1").write_text(required_source, encoding="utf-8")
            folder = root / "Saved/MigrationEvidence/fixture"
            (folder / "AutomationReport").mkdir(parents=True)
            (folder / "head.txt").write_text(expected + "\n", encoding="utf-8")
            (folder / "build.log").write_text("synthetic, NOT a real native build", encoding="utf-8")
            (folder / "automation.log").write_text("synthetic, NOT real UE", encoding="utf-8")
            report_file = folder / "AutomationReport/index.json"
            receipt_file = folder / "verified-native.json"
            data = {
                "succeeded": 35, "failed": 0, "notRun": 0,
                "tests": [{"fullTestPath": name, "state": "Success"} for name in required],
            }
            receipt = {
                "status": "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE",
                "source_sha": expected, "unreal_version": "5.8.4",
                "required_native_tests": 35, "report_sha256": "",
                "pie_player_input": "NOT_TESTED", "visual_approval": "NOT_TESTED",
            }

            def write_synthetic_result(value):
                report_file.write_text(json.dumps(value), encoding="utf-8")
                receipt["report_sha256"] = hashlib.sha256(report_file.read_bytes()).hexdigest()
                receipt_file.write_text(json.dumps(receipt), encoding="utf-8")

            with mock.patch.object(host, "PROJECT", root):
                write_synthetic_result(data)
                self.assertEqual(str(receipt_file), host.verified_native_receipt(expected)["receipt"])
                # Even with a matching report hash, inflated successes cannot
                # be used to admit the disposable UE map author.
                mutated = json.loads(json.dumps(data))
                mutated["succeeded"] = 36
                write_synthetic_result(mutated)
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt(expected)

                mutated = json.loads(json.dumps(data))
                mutated["tests"].append({"fullTestPath": "Extra.Invented", "state": "Failure"})
                mutated["succeeded"] = 36
                write_synthetic_result(mutated)
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt(expected)

                mutated = json.loads(json.dumps(data))
                mutated["tests"].append({"fullTestPath": "", "state": "Success"})
                mutated["succeeded"] = 36
                write_synthetic_result(mutated)
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt(expected)

                mutated = json.loads(json.dumps(data))
                mutated["tests"][0]["state"] = "Failed"
                write_synthetic_result(mutated)
                with self.assertRaisesRegex(RuntimeError, "no accepted exact-head"):
                    host.verified_native_receipt(expected)

    def test_source_holds_all_review_runtime_boundaries(self):

        source = Path(stage.__file__).read_text(encoding="utf-8")
        runner = Path(host.__file__).read_text(encoding="utf-8")
        for term in ("get_dirty_map_packages", "get_dirty_content_packages",
                     "does_directory_exist(DEST_ROOT)", "save_map(source_world, DEST_MAP)",
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
