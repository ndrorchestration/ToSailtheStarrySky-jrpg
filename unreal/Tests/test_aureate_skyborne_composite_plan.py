"""Source-bound geometry and authority checks for four-wing Skyborne review."""
from pathlib import Path
import json
import sys
import unittest

TOOLS=Path(__file__).resolve().parents[1]/"Tools"
sys.path.insert(0,str(TOOLS))
import aureate_skyborne_composite_plan as plan

class SkyborneReviewPlanTests(unittest.TestCase):
    def test_matches_current_cpp_pose_signature(self):
        plan.validate_cpp_contract()

    def test_four_real_wings_and_four_nonwing_supports(self):
        p=plan.build_plan()
        self.assertEqual(len(p["wings"]),4)
        self.assertEqual(len(p["supports"]),4)
        self.assertNotEqual(p["wing_mesh"],p["support_mesh"])
        self.assertTrue(p["wing_mesh"].startswith("/Game/TSTSS/Review/ShipArt/"))
        self.assertTrue(p["support_mesh"].startswith("/Game/TSTSS/Review/ShipArt/"))
        self.assertEqual(len(p["cameras"]),4)

    def test_symmetric_port_starboard_root_positions(self):
        wings=plan.build_plan()["wings"]
        for a,b in ((wings[0],wings[1]),(wings[2],wings[3])):
            self.assertEqual(a["location_cm"][0],b["location_cm"][0])
            self.assertEqual(a["location_cm"][1],-b["location_cm"][1])
            self.assertEqual(a["location_cm"][2],b["location_cm"][2])
            self.assertEqual(a["pitch_yaw_roll_deg"][1],-b["pitch_yaw_roll_deg"][1])
            self.assertEqual(a["pitch_yaw_roll_deg"][2],-b["pitch_yaw_roll_deg"][2])

    def test_fore_aft_and_support_reach(self):
        p=plan.build_plan()
        wings=p["wings"]
        self.assertEqual([w["location_cm"][0] for w in wings],[155,155,-180,-180])
        self.assertTrue(all(w["location_cm"][2]==188 for w in wings))
        for support,wing in zip(p["supports"],wings):
            self.assertEqual(support["end_cm"],wing["location_cm"])
            self.assertEqual(support["location_cm"][0],wing["location_cm"][0])
            self.assertTrue(40<support["length_cm"]<70)
            self.assertAlmostEqual(support["scale"][0],support["length_cm"]/100)

    def test_no_orbiter_or_gameplay_promotion(self):
        p=plan.build_plan()
        self.assertFalse(p["orbiter_authorized"])
        self.assertFalse(p["art_approved"])
        self.assertFalse(p["gameplay_modified"])
        self.assertFalse(p["rig_animated"])
        self.assertFalse(p["native_build_accepted"])
        self.assertEqual(p["status"],"SOURCE_GEOMETRY_PLAN_ONLY_NOT_NATIVE_BINDING")

    def test_serializable_deterministic_no_arbitrary_engine_calls(self):
        p=plan.build_plan()
        self.assertEqual(json.dumps(p,sort_keys=True),
                         json.dumps(plan.build_plan(),sort_keys=True))
        src=(TOOLS/"aureate_skyborne_composite_plan.py").read_text()
        for forbidden in ("import unreal","spawn_actor_from_class(","save_map(","RequestForm("):
            self.assertNotIn(forbidden,src)

    def test_review_only_forward_camera_targets(self):
        p=plan.build_plan()
        for cam in p["cameras"]:
            self.assertTrue(cam["name"][0:2] in {"01","02","03","04"})
            self.assertLess(abs(cam["target_cm"][0]),100)
            self.assertGreater(cam["target_cm"][2],120)
            self.assertLess(cam["target_cm"][2],240)

    def test_approved_reference_exact_digest(self):
        self.assertEqual(plan.REFERENCE_SHA256,
                         "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13")

if __name__=="__main__":unittest.main()
