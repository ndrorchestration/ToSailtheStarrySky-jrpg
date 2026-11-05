"""Source/negative controls for noncanonical launch-water-recovery review staging.

No Unreal Editor, map writes, ship physics, PIE or player SaveGames are touched.
"""
from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import os
import shutil
import subprocess
import tempfile

import build_first_wake_splashdown_greybox as greybox


class GreyboxAuthoringContract(TestCase):
    def test_three_additive_recovery_stops_do_not_replace_prelude(self):
        plan = greybox.validate_plan()
        self.assertEqual(plan["parent_stop_count"], 7)
        self.assertEqual([s["beat"] for s in plan["new_stops"]],
                         ["Launched", "EmptyReserveInspected", "ReturnedToBerth"])
        self.assertTrue(all(s["x_cm"] < 2550 for s in plan["new_stops"]))
        self.assertEqual(plan["immutable_parent_map"],
                         "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2")
        self.assertNotEqual(plan["new_map"], plan["immutable_parent_map"])

    def test_only_noncanonical_protocol_claimed(self):
        plan = greybox.validate_plan()
        self.assertEqual(plan["status"], "SOURCE_AUTHORED_GREYBOX_PLAN_NOT_EDITOR_OR_PIE")
        for key in ("ship_geometry_approved", "playable_or_cinematic_approved",
                    "real_physics_verified", "native_build_or_pie_tested",
                    "early_lyra_recruited", "starbourne_unlocked",
                    "protected_map_changed"):
            self.assertFalse(plan[key], key)
        self.assertEqual(plan["water_tag"], "TSTSSWaterVolume")
        self.assertTrue(plan["proto_buoyancy_explicitly_opted_in"])

    def test_water_physics_lab_is_off_dock_and_initially_dry(self):
        plan = greybox.validate_plan()
        self.assertGreater(plan["hull_initial_bottom_cm"], plan["water_surface_top_cm"])
        self.assertGreater(plan["water_center_cm"][0], 3000)
        self.assertGreater(plan["water_center_cm"][1], 2000)

    def test_illegal_water_location_fails_before_editor(self):
        old = greybox.WATER_LOCATION
        try:
            greybox.WATER_LOCATION = (0.0, 0.0, 0.0)
            with self.assertRaisesRegex(RuntimeError, "above a bounded water surface|obstruct"):
                greybox.validate_plan()
        finally:
            greybox.WATER_LOCATION = old

    def test_illegal_recovery_order_fails_before_editor(self):
        old = greybox.EXTRA_STOPS
        try:
            greybox.EXTRA_STOPS = (old[1], old[0], old[2])
            with self.assertRaisesRegex(RuntimeError, "ordered"):
                greybox.validate_plan()
        finally:
            greybox.EXTRA_STOPS = old

    def test_wrong_disposable_root_denied(self):
        with tempfile.TemporaryDirectory() as temporary:
            wrong = Path(temporary) / "user-project" / "unreal"
            wrong.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "explicitly named disposable"):
                greybox.require_sandbox(wrong)

    def test_missing_expected_sha_denied_before_git_or_map_io(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / greybox.SANDBOX / "unreal"
            project.mkdir(parents=True)
            with patch.dict(os.environ, {"TSTSS_GREYBOX_EXPECTED_HEAD": "bad"}):
                with self.assertRaisesRegex(RuntimeError, "40-character"):
                    greybox.require_sandbox(project)

    def make_disposable_project(self, temporary: str) -> Path:
        project = Path(temporary) / greybox.SANDBOX / "unreal"
        (project / greybox.ORIGINAL_MAP).parent.mkdir(parents=True)
        source_map = Path(__file__).resolve().parents[1] / greybox.ORIGINAL_MAP
        shutil.copyfile(source_map, project / greybox.ORIGINAL_MAP)
        for name in ("DefaultInput.ini", "DefaultEngine.ini"):
            dest = project / "Config" / name
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(";isolated fixture", encoding="utf-8")
        return project

    def test_valid_source_custody_then_map_savegame_and_dirty_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_disposable_project(directory)
            sha = "a" * 40

            def fake_git(args, **kw):
                if "rev-parse" in args:
                    return subprocess.CompletedProcess(args, 0, sha + "\n", "")
                if "status" in args:
                    return subprocess.CompletedProcess(args, 0, "", "")
                raise RuntimeError("unexpected Git command")

            with patch.dict(os.environ, {"TSTSS_GREYBOX_EXPECTED_HEAD": sha}), (
                    patch.object(greybox.subprocess, "run", side_effect=fake_git)):
                actual, returned_sha = greybox.require_sandbox(project)
                self.assertEqual(actual, project.resolve())
                self.assertEqual(returned_sha, sha)

                target = project / greybox.ASSET_PATH
                target.write_bytes(b"existing new-map file")
                with self.assertRaisesRegex(RuntimeError, "map already exists"):
                    greybox.require_sandbox(project)
                target.unlink()

                save_dir = project / "Saved/SaveGames"
                save_dir.mkdir(parents=True)
                (save_dir / "private_player.sav").write_bytes(b"DO NOT MODIFY")
                with self.assertRaisesRegex(RuntimeError, "has SaveGame files"):
                    greybox.require_sandbox(project)
                self.assertEqual((save_dir / "private_player.sav").read_bytes(),
                                 b"DO NOT MODIFY")

    def test_dirty_git_head_rejected_before_map_authoring(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_disposable_project(directory)
            sha = "a" * 40

            def fake_git(args, **kw):
                if "rev-parse" in args:
                    return subprocess.CompletedProcess(args, 0, sha + "\n", "")
                if "status" in args:
                    return subprocess.CompletedProcess(
                        args, 0, " M unreal/Config/DefaultEngine.ini\n", "")
                raise RuntimeError("unexpected Git command")
            with patch.dict(os.environ, {"TSTSS_GREYBOX_EXPECTED_HEAD": sha}), (
                    patch.object(greybox.subprocess, "run", side_effect=fake_git)):
                with self.assertRaisesRegex(RuntimeError, "must be clean"):
                    greybox.require_sandbox(project)

    def test_build_branch_with_editor_api_doubles_preserves_v2_and_adds_water_lab(self):
        """Executes the actual authoring function, never Unreal or a real map."""
        import json
        import sys
        from types import SimpleNamespace

        class FakeMesh:
            def __init__(self):
                self.mesh = None
                self.profile = None
                self.collision = None
                self.overlap = False
                self.simulated = False
                self.mobility = None

            def set_static_mesh(self, mesh): self.mesh = mesh
            def set_collision_profile_name(self, profile): self.profile = profile
            def set_collision_enabled(self, value): self.collision = value
            def set_editor_property(self, name, value):
                if name != "generate_overlap_events":
                    raise AssertionError("Unexpected reflected mesh property")
                self.overlap = value
            def get_editor_property(self, name):
                if name != "generate_overlap_events":
                    raise AssertionError("Unexpected reflected mesh readback")
                return self.overlap
            def set_simulate_physics(self, enabled): self.simulated = enabled
            def set_mobility(self, value): self.mobility = value

        class FakeText:
            def set_text(self, txt): self.text = txt
            def set_editor_property(self, key, value): setattr(self, key, value)

        class FakeActor:
            def __init__(self, kind):
                self.kind = kind
                self.mesh = FakeMesh()
                self.text = FakeText()
                self.properties = {}
            def set_actor_label(self, value): self.label = value
            def get_component_by_class(self, kind):
                return self.text if kind == "TextRenderComponent" else self.mesh
            def set_actor_scale3d(self, scale): self.scale = scale
            def set_editor_property(self, name, value): self.properties[name] = value

        class FakeEditor:
            def __init__(self): self.actors = []
            def spawn_actor_from_class(self, cls, position, rotation):
                actor = FakeActor(cls)
                actor.position = position
                self.actors.append(actor)
                return actor

        with tempfile.TemporaryDirectory() as directory:
            project = self.make_disposable_project(directory)
            original = (project / greybox.ORIGINAL_MAP).read_bytes()
            sha = "a" * 40
            editor = FakeEditor()
            stages = []
            logs = []
            def fake_git(args, **kw):
                if "rev-parse" in args:
                    return subprocess.CompletedProcess(args, 0, sha + "\n", "")
                if "status" in args:
                    return subprocess.CompletedProcess(args, 0, "", "")
                raise RuntimeError("unexpected Git call")
            def save_new_map(world, dest):
                stages.append(dest)
                (project / greybox.ASSET_PATH).write_bytes(b"FAKE_EDITOR_ONLY")
                return True
            engine = SimpleNamespace(
                Paths=SimpleNamespace(project_dir=lambda: str(project)),
                EditorAssetLibrary=SimpleNamespace(does_asset_exist=lambda x: False),
                EditorLoadingAndSavingUtils=SimpleNamespace(
                    get_dirty_map_packages=lambda: [],
                    load_map=lambda x: object(),
                    save_map=save_new_map),
                EditorActorSubsystem=type("EditorActorSubsystem", (), {}),
                get_editor_subsystem=lambda _: editor,
                load_class=lambda _outer, p: p,
                load_asset=lambda p: "FakeCube",
                StaticMeshActor="StaticMeshActor",
                TextRenderActor="TextRenderActor",
                StaticMeshComponent="StaticMeshComponent",
                TextRenderComponent="TextRenderComponent",
                TSTSSFirstWakeBeat=SimpleNamespace(
                    LAUNCHED=4,
                    EMPTY_RESERVE_INSPECTED=7,
                    RETURNED_TO_BERTH=8),
                CollisionEnabled=SimpleNamespace(
                    QUERY_AND_PHYSICS="QueryAndPhysics", QUERY_ONLY="QueryOnly"),
                ComponentMobility=SimpleNamespace(MOVABLE="Movable"),
                Name=lambda name: name,
                Vector=lambda *xyz: xyz,
                Rotator=lambda **kwargs: kwargs,
                log=lambda line: logs.append(line),
            )
            with patch.dict(os.environ, {"TSTSS_GREYBOX_EXPECTED_HEAD": sha}), (
                    patch.dict(sys.modules, {"unreal": engine})), (
                    patch.object(greybox.subprocess, "run", side_effect=fake_git)):
                result = greybox.build_in_unreal()
            self.assertEqual(result["status"], "NEW_GREYBOX_MAP_SAVED_NOT_PIE")
            self.assertEqual(stages, [greybox.MAP])
            self.assertEqual((project / greybox.ORIGINAL_MAP).read_bytes(), original)
            self.assertEqual(len(editor.actors), 8)  # 3 markers+signs, water, hull
            hull = next(a for a in editor.actors if "HullPhysicsProxy" in a.label)
            water = next(a for a in editor.actors if "WaterVolume" in a.label)
            self.assertFalse(hull.mesh.simulated)  # no prelaunch free fall
            self.assertEqual(hull.mesh.mobility, "Movable")
            self.assertTrue(hull.mesh.overlap)
            self.assertTrue(hull.properties["arm_prototype_physics_on_launch"])
            self.assertTrue(hull.properties["enable_prototype_buoyancy"])
            self.assertEqual(water.properties["tags"], ["TSTSSWaterVolume"])
            self.assertEqual(water.mesh.profile, "OverlapAllDynamic")
            self.assertEqual(water.mesh.collision, "QueryOnly")
            self.assertFalse(any("SAVEGAME" in name.upper() for name in stages))
            report = json.loads(
                (project / "Saved/SplashdownGreyboxV1/staging_receipt.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(report["tested_git_head"], sha)
            self.assertTrue(any("NOT_PLAYTESTED" in log for log in logs))

    def test_no_game_saves_removal_or_existing_map_save_in_script(self):
        source = Path(greybox.__file__).read_text(encoding="utf-8")
        self.assertIn("with report.open(\"x\"", source)
        self.assertIn("EditorLoadingAndSavingUtils.load_map(v2.REVIEW_MAP)", source)
        self.assertIn("EditorLoadingAndSavingUtils.save_map(world, MAP)", source)
        self.assertIn('water.set_editor_property("tags", [unreal.Name("TSTSSWaterVolume")])',
                      source)
        self.assertIn('water_mesh.set_editor_property("generate_overlap_events", True)', source)
        self.assertIn('hull_mesh.set_editor_property("generate_overlap_events", True)', source)
        self.assertIn('water_mesh.get_editor_property("generate_overlap_events")', source)
        self.assertIn('hull_mesh.get_editor_property("generate_overlap_events")', source)
        self.assertNotIn(".set_generate_overlap_events(", source)
        self.assertIn('hull.set_editor_property("enable_prototype_buoyancy", True)',
                      source)
        self.assertIn('hull.set_editor_property("arm_prototype_physics_on_launch", True)',
                      source)
        self.assertIn("hull_mesh.set_simulate_physics(False)", source)
        self.assertIn("hashlib.sha256(parent_map.read_bytes()).hexdigest()", source)
        for forbidden in ("save_map(world, v2.REVIEW_MAP)",
                          "delete_game_in_slot", "save_game_to_slot",
                          "EditorAssetLibrary.delete_asset", "Stop-Process",
                          "destroy_actor(", "open('w')"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    import unittest
    unittest.main()
