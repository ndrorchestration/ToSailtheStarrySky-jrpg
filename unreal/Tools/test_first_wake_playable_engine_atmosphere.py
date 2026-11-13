"""Source-locked authored VS02 weather/light and resource-admission tests.

No Unreal Editor import, map writes, live GPU use or project mutation.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

import check_first_wake_playable_engine_host as host
import stage_first_wake_playable_engine_atmosphere as stage


class PlayableEngineAtmosphereAuthoringTests(unittest.TestCase):

    def test_host_admits_repaired_checkout_but_rejects_unrelated_worktree(self):
        good = {"platform": "win32", "worktree": "TSTSS_EngineFocusFix_20261112",
                "head_matches": True, "source_changes": [], "engine_correct": True,
                "map_sha_matches": True, "compiled_dll_exists": True,
                "receipt_exists": False, "unreal_processes": [],
                "free_ram_gib": 7.0, "free_disk_gib": 16.0}
        self.assertNotIn("WRONG_WORKTREE", host.classify(good))
        self.assertIn("WRONG_WORKTREE", host.classify({**good, "worktree": "Production"}))

    def test_source_authoring_reuses_existing_recipe(self):
        p = stage.plan(strict_source=False)
        self.assertEqual(p["weather"], "Clear")
        self.assertEqual(p["initial_clock_hours"], 17.1)
        self.assertEqual(p["authored_lighting_recipe"], "engineering")
        self.assertEqual(len(p["remove_exactly"]), 4)
        self.assertEqual(len(p["proposed_practicals"]), 2)
        self.assertEqual(p["source_map"],
                         "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors")
        self.assertFalse(p["cinematic_approved"])
        self.assertFalse(p["native_pie_verified"])

    def test_self_test_does_not_claim_native_completion(self):
        s = stage.self_test()
        self.assertEqual(s["status"], "GAMEPLAY_ENGINE_AUTHORING_RECIPE_CHECK_PASS")
        self.assertEqual(s["native_scene_written"], "NOT_CHECKED")

    def test_weather_uses_native_unreal_python_enum_name(self):
        clear = object()
        mist = object()
        native = SimpleNamespace(TSTSSWeather=SimpleNamespace(CLEAR=clear, COASTAL_MIST=mist))
        self.assertIs(stage.surface.weather_enum_value(native, "Clear"), clear)
        self.assertIs(stage.surface.weather_enum_value(native, "CoastalMist"), mist)
        with self.assertRaisesRegex(RuntimeError, "unsupported native weather"):
            stage.surface.weather_enum_value(native, "Unknown")

    def test_missing_weather_enum_does_not_touch_scene(self):
        actors = Mock()
        with self.assertRaisesRegex(RuntimeError, "weather UENUM not reflected"):
            stage.surface.stage_scene_atmosphere(SimpleNamespace(), actors,
                                                 stage.SCENE, object(), object())
        actors.assert_not_called()
        actors.get_all_level_actors.assert_not_called()
        actors.destroy_actor.assert_not_called()
        actors.spawn_actor_from_class.assert_not_called()

    def test_drifting_authored_weather_fails_closed(self):
        data = dict(stage.surface.SCENE_LOOKS)
        data[stage.SCENE] = ("Storm", 17.1, "engineering")
        with patch.object(stage.surface, "SCENE_LOOKS", data):
            with self.assertRaisesRegex(RuntimeError, "recipe drifted"):
                stage.plan(strict_source=False)

    def test_drifting_sky_removal_list_fails_closed(self):
        sky = tuple(stage.surface.OLD_SKY_LABELS)[:-1]
        with patch.object(stage.surface, "OLD_SKY_LABELS", sky):
            with self.assertRaisesRegex(RuntimeError, "sky-removal"):
                stage.plan(strict_source=False)

    def test_drifting_practical_lights_fails_closed(self):
        data = dict(stage.surface.PRACTICAL_LAMPS)
        data[stage.SCENE] = ()
        with patch.object(stage.surface, "PRACTICAL_LAMPS", data):
            with self.assertRaisesRegex(RuntimeError, "practical-light"):
                stage.plan(strict_source=False)

    def test_missing_real_instrument_anchor_fails_closed(self):
        with TemporaryDirectory() as tmp:
            fake = Path(tmp) / "VS02_AureateInteriors.umap"
            fake.write_bytes(b"TSTSS_VS_REVIEW_MainHarmonicLevitationEngine_Proxy")
            with patch.object(stage, "MAP_FILE", fake):
                with self.assertRaisesRegex(RuntimeError, "real engine focus anchor"):
                    stage.plan(strict_source=False)

    def test_source_only_cannot_invoke_native_authoring(self):
        with patch.dict(stage.os.environ, {
            "TSTSS_GAMEPLAY_ENGINE_STAGE_EXPLICIT": "",
            "TSTSS_GAMEPLAY_ENGINE_EXPECTED_HEAD": "",
        }):
            with self.assertRaises(RuntimeError):
                stage.native_stage()

    def test_stage_writes_only_authored_vs02_and_not_other_maps(self):
        src = Path(stage.__file__).read_text(encoding="utf-8")
        self.assertIn("surface.stage_scene_atmosphere(", src)
        self.assertIn("u.EditorLoadingAndSavingUtils.save_map(world, MAP_ASSET)", src)
        self.assertIn('SCENE = "VS02_AureateInteriors"', src)
        self.assertNotIn("OpenLevel(", src)
        self.assertNotIn("SaveGame", src)
        self.assertIn('"world_authority_count": 1', src)
        self.assertIn("EXPECTED_ORIGINAL_ACTORS - 4 + 3", src)

    def test_host_offline_admission_negative_fixtures(self):
        a = host.self_test()
        self.assertEqual(a["status"], "PLAYABLE_ENGINE_HOST_OFFLINE_FIXTURES_PASS")
        self.assertEqual(a["cases"], 10)
        self.assertFalse(a["editor_launched"])
        self.assertFalse(a["map_written"])

    def test_host_blocks_non_exact_head_without_io(self):
        a = host.inspect("this-is-not-a-sha")
        self.assertEqual(a["status"], "HOLD")
        self.assertEqual(a["reasons"], ["INVALID_EXPECTED_HEAD"])
        self.assertFalse(a["map_written"])

    def test_host_blocks_compiler_absence(self):
        good = {
            "platform": "win32", "worktree": stage.WORKTREE,
            "head_matches": True, "source_changes": [],
            "engine_correct": True, "map_sha_matches": True,
            "compiled_dll_exists": True, "receipt_exists": False,
            "unreal_processes": [], "free_ram_gib": 7.0,
            "free_disk_gib": 16.0,
        }
        self.assertEqual(host.classify(good), [])
        self.assertIn("NATIVE_EDITOR_MODULE_UNBUILT",
                      host.classify({**good, "compiled_dll_exists": False}))

    def test_native_code_refuses_duplicate_atmosphere(self):
        src = Path(stage.surface.__file__).read_text(encoding="utf-8")
        self.assertIn("if a.get_class().get_name() in SKY_ACTOR_CLASSES", src)
        self.assertIn("actor_sys.destroy_actor(candidates[name])", src)
        self.assertIn('actor.set_editor_property("autoplay_review_cycle", False)', src)
        self.assertIn('actor.set_editor_property("initial_weather"', src)


if __name__ == "__main__":
    unittest.main()
