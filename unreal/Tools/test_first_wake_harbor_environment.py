"""Engine-free safety and spatial contracts for First Wake harbor lookdev V1.

These tests never import Unreal, open maps, or claim screenshots/PIE success.
"""
import math
import unittest
from dataclasses import replace
from unittest.mock import patch

import build_first_wake_harbor_environment as harbor


class FirstWakeHarborEnvironmentTests(unittest.TestCase):
    def test_explicit_review_only_status(self):
        plan = harbor.validate_plan()
        self.assertEqual(plan["status"], "SOURCE_HARBOR_ENVIRONMENT_PLAN_VALID_NOT_STAGED")
        for key in ("pie_verified", "native_render_verified", "artist_approved",
                    "production_modified", "starbourne_unlocked",
                    "ocean_physics_enabled", "new_actor_collision_enabled"):
            self.assertFalse(plan[key], key)

    def test_map_is_a_new_separate_review_asset_world(self):
        self.assertNotEqual(harbor.BASE_MAP, harbor.DEST_MAP)
        self.assertIn("AssetAssembly", harbor.BASE_MAP)
        self.assertIn("Environment", harbor.DEST_MAP)
        self.assertEqual(len(harbor.BASE_SHA256), 64)
        self.assertTrue(harbor.DEST_REL.endswith(".umap"))

    def test_preserves_original_seven_story_stops(self):
        self.assertEqual(harbor.MILESTONES,
            ("FlyerDiscovery", "IoniaHiring", "AureateBoarding",
             "LiftStation", "PressureStation", "ReserveStation", "EngineeringApproval"))

    def test_original_palette_and_four_harbor_focus_areas(self):
        plan = harbor.validate_plan()
        self.assertGreaterEqual(plan["native_review_assets_requested"], 40)
        self.assertIn("sea_teal", plan["material_roles"])
        self.assertIn("coastal_rock", plan["material_roles"])
        self.assertIn("HarborCustomsHouse", plan["props"])
        self.assertIn("HarmonicEngineeringShop", plan["props"])
        self.assertIn("OuterStonePier", plan["props"])
        self.assertIn("WaterBeyondHarbor", plan["props"])

    def test_geometry_respects_review_route_clear_zone(self):
        self.assertTrue(harbor.validate_plan()["props"])
        for p in harbor.PROPS:
            self.assertGreaterEqual(abs(p.xyz[1]) - p.scale[1] * 50, 400, p.name)

    def test_intruding_building_rejected(self):
        props = list(harbor.PROPS)
        props[0] = replace(props[0], xyz=(-600, 100, -65))
        with patch.object(harbor, "PROPS", tuple(props)):
            with self.assertRaisesRegex(ValueError, "corridor"):
                harbor.validate_plan()

    def test_duplicate_scenery_rejected(self):
        with patch.object(harbor, "PROPS", harbor.PROPS + (harbor.PROPS[0],)):
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                harbor.validate_plan()

    def test_nonfinite_coordinates_rejected(self):
        props = list(harbor.PROPS)
        props[0] = replace(props[0], xyz=(math.inf, 950, -65))
        with patch.object(harbor, "PROPS", tuple(props)):
            with self.assertRaisesRegex(ValueError, "Nonfinite"):
                harbor.validate_plan()

    def test_negative_scale_rejected(self):
        props = list(harbor.PROPS)
        props[0] = replace(props[0], scale=(-1, 1, 1))
        with patch.object(harbor, "PROPS", tuple(props)):
            with self.assertRaisesRegex(ValueError, "Nonpositive"):
                harbor.validate_plan()

    def test_duplicate_material_roles_are_not_implicit(self):
        with patch.dict(harbor.PALETTE, {"unwanted_production_material": ((.5,.5,.5), .6)}):
            with self.assertRaisesRegex(ValueError, "palette roles"):
                harbor.validate_plan()

    def test_palette_channels_must_be_bounded(self):
        with patch.dict(harbor.PALETTE, {"sea_teal": ((1.1, .17, .24), .29)}):
            with self.assertRaisesRegex(ValueError, "channel"):
                harbor.validate_plan()

    def test_native_stage_requires_known_parent_binary(self):
        from pathlib import Path
        source = Path(harbor.__file__).read_text(encoding="utf-8")
        self.assertIn("sha256(src) != BASE_SHA256", source)
        self.assertIn("levels.new_level_from_template(DEST_MAP, BASE_MAP)", source)
        self.assertIn("if dst.exists() or receipt.exists()", source)
        self.assertIn("if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()", source)
        self.assertIn("NoCollision", source)
        self.assertIn("TSTSS_HARBOR_NATIVE_STAGE_SAVED_NOT_PIE", source)

    def test_material_graph_and_compile_fail_closed(self):
        from pathlib import Path
        src = Path(harbor.__file__).read_text(encoding="utf-8")
        self.assertIn("if not unreal.MaterialEditingLibrary.connect_material_property(", src)
        self.assertIn("compiler_errors = list(unreal.MaterialEditingLibrary.recompile_material(material))", src)
        self.assertIn("if compiler_errors:", src)
        self.assertIn("HOLD: material compile failed", src)

    def test_physical_water_and_runtime_permissions_not_changed(self):
        source = __import__("pathlib").Path(harbor.__file__).read_text(encoding="utf-8")
        self.assertNotIn("SaveGameToSlot", source)
        self.assertNotIn("enable_prototype_buoyancy", source)
        self.assertNotIn("merge_pull_request", source)
        self.assertNotIn("TSTSSFirstWakeBeat.LAUNCHED", source)


if __name__ == "__main__":
    unittest.main()
