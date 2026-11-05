"""Engine-free contracts for independent First Wake Harbor V1 native readback."""
import inspect
import unittest

import build_first_wake_harbor_environment as plan
import verify_first_wake_harbor_native as readback


class IndependentReadbackContracts(unittest.TestCase):
    def test_no_unreal_required_for_source_only_import(self):
        self.assertTrue(callable(readback.verify_saved_harbor_world))
        self.assertEqual(len(plan.PROPS), 47)
        self.assertEqual(len(plan.PALETTE), 8)

    def test_separate_world_and_exact_inherited_story_contract(self):
        src = inspect.getsource(readback.verify_saved_harbor_world)
        self.assertIn("world.load_level(harbor.DEST_MAP)", src)
        self.assertIn("stage.get(\"previous_actor_count\") != 34", src)
        self.assertIn('len(actors) != 84', src)
        self.assertIn('unreal.PlayerStart', src)
        self.assertIn("TSTSS_PRELUDE_REVIEW_", src)
        self.assertIn("TSTSSMilestoneActor", src)

    def test_requires_native_stage_receipt_matching_map_digest(self):
        src = inspect.getsource(readback.verify_saved_harbor_world)
        self.assertIn("NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK", src)
        self.assertIn('stage.get("map_sha256") != harbor.sha256(dest)', src)
        self.assertIn("result_file.exists()", src)
        self.assertIn("harbor.sha256(parent) != harbor.BASE_SHA256", src)

    def test_47_native_scenery_collisions_stay_disabled(self):
        src = inspect.getsource(readback.verify_saved_harbor_world)
        self.assertIn("unreal.StaticMeshActor", src)
        self.assertIn("unreal.CollisionEnabled.NO_COLLISION", src)
        self.assertIn("actor.get_actor_enable_collision()", src)
        self.assertIn("len(harbor.PROPS)", src)

    def test_materials_and_sky_must_exist(self):
        src = inspect.getsource(readback.verify_saved_harbor_world)
        self.assertIn('component.get_material(0)', src)
        self.assertIn("unreal.SkyAtmosphere", src)
        self.assertIn("unreal.ExponentialHeightFog", src)
        self.assertIn("unreal.CameraActor", src)
        self.assertIn('"atmosphere_sun_light"', src)
        self.assertIn("len(harbor.PALETTE)", src)

    def test_no_runtime_art_or_starbourne_claims(self):
        src = inspect.getsource(readback.verify_saved_harbor_world)
        for gate in ('"real_player_input_verified": False',
                     '"native_gpu_capture_verified": False',
                     '"ocean_physics_verified": False',
                     '"creator_art_approved": False',
                     '"starbourne_unlocked": False'):
            self.assertIn(gate, src)
        self.assertNotIn("save_current_level", src)
        self.assertNotIn("save_map(", src)
        self.assertNotIn("save_game", src.lower())


if __name__ == "__main__":
    unittest.main()
