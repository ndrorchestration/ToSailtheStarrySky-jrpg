"""Source-only regression protection for an isolated walkable optical bridge.
These checks DO NOT show native collision, WASD traversal, C response, or art.
"""
from pathlib import Path
import json
import unittest
import verify_optical_bridge_reach_geometry as geo

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=(ROOT/"unreal/Tools/stage_vs02_optical_bridge_reach.py").read_text(encoding="utf-8")
AUTHORING=geo.AUTHORING.read_text(encoding="utf-8")
GAME=(ROOT/"unreal/Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")

class ReviewBridgeReachGeometryTests(unittest.TestCase):
    def test_origin_still_contains_actual_authored_player_start(self):
        report=geo.diagnose()
        self.assertTrue(report["player_start_inside_solid_bridge"])
        self.assertEqual(report["original_bridge_aabb_cm"],
                         ((-1130.,-430.),(-450.,450.),(-5.,135.)))
        self.assertEqual(report["player_start_xyz_cm"],(-1080.,0.,120.))
        self.assertGreater(report["spawn_distance_to_lift_cm"],450.)
        self.assertEqual(report["status"],
                         "SOURCE_GEOMETRY_INTERSECTION_CONFIRMED_PROPOSED_FIX_NOT_NATIVE_TESTED")

    def test_review_only_slab_is_below_spawn_and_walkable_step(self):
        result=geo.diagnose()["proposal"]
        self.assertEqual(result["scope"],"NONSHIPPING_M_ENGINEPRESENTATIONREVIEW_ONLY")
        self.assertEqual(result["new_bridge_xyz_cm"],(-780.,0.,7.5))
        self.assertEqual(result["new_bridge_scale"],(7.,9.,0.15))
        self.assertEqual(result["new_bridge_aabb_cm"],
                         ((-1130.,-430.),(-450.,450.),(0.,15.)))
        self.assertEqual(result["raised_walkable_lip_cm"],15.)
        self.assertFalse(result["player_start_intersects_proposed_bridge"])
        for claim in ("canonical_vs02_modified","authoring_script_modified",
                      "native_unreal_asset_saved","real_wasd_c_reachability_established",
                      "creator_approved"):
            self.assertFalse(result[claim],claim)

    def test_changed_or_nonblocking_authoring_does_not_pass(self):
        old='prop("BridgeDeck", "Cube", (-780, 0, 65), (7, 9, 1.4), "stone", True)'
        self.assertEqual(AUTHORING.count(old),1)
        variants=[
            old.replace("True","False"),
            old.replace("(7, 9, 1.4)","(7, 9, 0.15)"),
            old.replace('"BridgeDeck"','"BridgeLab"'),
        ]
        for bad in variants:
            with self.subTest(bad=bad):
                with self.assertRaises(RuntimeError):
                    geo.validate_original_geometry(AUTHORING.replace(old,bad))

    def test_original_scene_and_c_key_guard_unchanged(self):
        self.assertEqual(geo.sha(geo.SOURCE),geo.EXPECTED_SOURCE)
        self.assertEqual(geo.sha(geo.COPY),geo.EXPECTED_REVIEW)
        self.assertIn("FVector::Dist(GetActorLocation(), Instrument->GetActorLocation()) > 450.f",GAME)
        self.assertIn("World->WorldType != EWorldType::PIE",GAME)

    def test_stager_is_exact_source_and_opt_in_only(self):
        for required in (
            "TSTSS_BRIDGE_REACH_STAGE_EXPLICIT",
            "TSTSS_BRIDGE_REACH_EXPECT_HEAD",
            "TSTSS_840_OpticalReach_20261115",
            "review/ue58-optical-bridge-reach-probe-20261115",
            "git(\"status\",\"--porcelain=v1\",\"--untracked-files=all\")",
            "WorldType" if False else "is_in_play_in_editor()",
            "get_dirty_map_packages()",
            "get_dirty_content_packages()",
            "sha(SOURCE)==EXPECTED_SOURCE",
            "sha(COPY)==EXPECTED_REVIEW",
            "explicit_review_opt_in",
            "CollisionEnabled.QUERY_AND_PHYSICS",
        ):
            self.assertIn(required,SCRIPT,required)
        self.assertNotIn("git push",SCRIPT)
        self.assertNotIn("TeleportTo",SCRIPT)
        self.assertNotIn("Starbourne",SCRIPT)
        self.assertNotIn("QuickSave",SCRIPT)

    def test_stager_mutates_only_named_bridge_and_review_copy(self):
        self.assertEqual(SCRIPT.count("bridge.set_actor_location("),1)
        self.assertEqual(SCRIPT.count("bridge.set_actor_scale3d("),1)
        self.assertEqual(SCRIPT.count("save_map(world,MAP)"),1)
        self.assertIn("shutil.copy2(COPY,BACKUP)",SCRIPT)
        self.assertIn("MAP=\"/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview\"",SCRIPT)
        self.assertNotIn("spawn_actor_from_class(",SCRIPT)
        self.assertNotIn("player.set_actor_location(",SCRIPT)
        self.assertIn('"real_pie_wasd_c_confirmed":False',SCRIPT)

if __name__=="__main__":
    unittest.main()
