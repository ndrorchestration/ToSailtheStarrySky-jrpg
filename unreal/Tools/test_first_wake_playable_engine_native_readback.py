"""Unit-level custody/negative fixtures for persisted UE engine map readback.

These tests are engine-free and do not substitute for a real Unreal session.
"""
from pathlib import Path
from unittest import TestCase

import readback_first_wake_playable_engine_atmosphere as readback
import stage_first_wake_playable_engine_atmosphere as stage


class NativeVS02EngineReadbackContractTests(TestCase):
    def test_readback_inventory_fixtures(self):
        receipt = readback.self_test()
        self.assertEqual(
            receipt["status"],
            "PLAYABLE_ENGINE_NATIVE_READBACK_OFFLINE_FIXTURES_PASS")
        self.assertEqual(receipt["positive_cases"], 1)
        self.assertEqual(receipt["negative_cases"], 7)
        self.assertFalse(receipt["native_editor_opened"])
        self.assertEqual(receipt["pie"], "NOT_RUN")

    def test_gameplay_readback_exact_scene_and_no_pie_claim(self):
        source = Path(readback.__file__).read_text(encoding="utf-8")
        self.assertEqual(readback.EXPECTED_TOTAL, 27)
        self.assertIn("stage.git(\"status\", \"--porcelain\", \"-uall\")", source)
        self.assertIn('status == [" M " + map_path]', source)
        self.assertIn('stage.digest(stage.MAP_FILE) == map_hash', source)
        self.assertIn('u.EditorLoadingAndSavingUtils.load_map(stage.MAP_ASSET)', source)
        self.assertIn('"NATIVE_VS02_MAP_REOPEN_ATMOSPHERE_PASS_NOT_PIE"', source)
        self.assertIn('"player_camera_input_test": "NOT_RUN"', source)
        self.assertIn('"visual_approval": "NOT_ESTABLISHED"', source)
        self.assertNotIn("save_map(", source)
        self.assertNotIn("save_loaded_asset(", source)
        self.assertNotIn("SpawnActor(", source)
        self.assertNotIn("spawn_actor(", source)
        self.assertNotIn("SetViewTarget(", source)
        self.assertEqual(stage.SCENE, "VS02_AureateInteriors")

    def test_readback_native_call_is_blocked_without_windows(self):
        # Reading the current platform is sufficient; never launch Unreal
        # or change files to satisfy a test.
        import sys
        if sys.platform != "win32":
            with self.assertRaisesRegex(RuntimeError, "requires Windows editor"):
                readback.native_readback()

    def test_fixture_rejects_duplicate_gauge(self):
        good = [(readback.DIRECTOR, "TSTSSAtmosphereDirector"),
                (readback.LIGHTS[0], "PointLight"),
                (readback.LIGHTS[1], "PointLight"),
                (readback.GAUGE, "StaticMeshActor"),
                (readback.ENGINE, "StaticMeshActor")]
        good.extend(
            ("TSTSS_Extra_%02d" % i, "StaticMeshActor")
            for i in range(readback.EXPECTED_TOTAL-len(good))
        )
        duplicate = good[:]
        duplicate[5] = (readback.GAUGE, "StaticMeshActor")
        with self.assertRaisesRegex(RuntimeError, "duplicate persisted actor label"):
            readback.inventory_contract(duplicate)


if __name__ == "__main__":
    import unittest
    unittest.main()
