"""Checks deterministic review-only stage plan without manufacturing scene proof."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import author_aureate_v4_review_scene_plan as stage


class PlanTests(unittest.TestCase):
    def test_one_ship_persistent_four_wing_identities(self):
        p=stage.plan()
        ids=p["shared_vessel"]["wing_identity_ids"]
        self.assertEqual(len(ids),4)
        self.assertEqual(len(set(ids)),4)
        self.assertEqual(set(p["forms"]),set(stage.FORMS))
        for form in p["forms"].values():
            self.assertEqual(form["wing_ids"],ids)
        self.assertEqual(p["shared_vessel"]["hull_root"],"ONE_PERSISTENT_HULL_FOR_ALL_FOUR")
        self.assertIn("BRIDGE_AND_LIVING_QUARTERS",p["shared_vessel"]["central_pivot"])

    def test_seaborne_foil_count_and_submersible_wing_visibility(self):
        p=stage.plan()["forms"]
        sea=p["Seabourne"]
        self.assertEqual(len(sea["foil_ids"]),2)
        self.assertEqual(sea["accessories"][0]["mounts"],sea["foil_ids"])
        self.assertEqual(p["Submersible"]["wing_look"],"TUCKED_BUT_IDENTIFIABLE")

    def test_starbourne_private_development_open_player_lock_unchanged(self):
        star=stage.plan()["forms"]["Starbourne"]
        self.assertEqual(star["development"],"AUTHORIZED_PRIVATE_RESEARCH")
        self.assertEqual(star["player_story_gate"],"LOCKED")
        self.assertEqual(len(set(star["radial_directions"])),4)
        self.assertEqual(star["accessories"][0]["mounts"],stage.plan()["shared_vessel"]["wing_identity_ids"])
        self.assertFalse(stage.plan()["mutations"]["starbourne_player_enabled"])

    def test_four_identical_camera_roles_no_synthetic_png_evidence(self):
        p=stage.plan()
        self.assertEqual(len(set(p["capture_contract"]["identical_roles_each_form"])),4)
        self.assertEqual(p["capture_contract"]["actual_pngs"],"NOT_ESTABLISHED_FOR_V4")
        self.assertEqual(p["capture_contract"]["camera_positions"],"TO_BE_AUTHORED_AND_RECORDED")
        self.assertFalse(p["mutations"]["scene_saved"])

    def test_gate_order_prevents_render_before_one_actor(self):
        order=stage.plan()["dependency_order"]
        self.assertLess(order.index("native_mesh_import"),order.index("full_editor_single_actor"))
        self.assertLess(order.index("full_editor_single_actor"),order.index("single_form_scene_assembly"))
        self.assertLess(order.index("single_form_scene_assembly"),order.index("gpu_camera_matched_render"))
        self.assertEqual(stage.plan()["gates"]["assembled_scene"],"NOT_VERIFIED")
        self.assertEqual(stage.plan()["gates"]["environment_sky"],"BLACK_SKY_HOLD_705")

    def test_deterministic_bytes_build_verify_reject_tamper(self):
        self.assertEqual(stage.serialized(),stage.serialized())
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"plan.json"
            stage.main(["--out",str(p)])
            expected=stage.serialized()
            self.assertEqual(p.read_bytes(),expected)
            self.assertEqual(hashlib.sha256(expected).hexdigest(),hashlib.sha256(p.read_bytes()).hexdigest())
            stage.main(["--out",str(p),"--check"])
            p.write_bytes(b'{"false":"approval"}')
            with self.assertRaises(SystemExit):
                stage.main(["--out",str(p),"--check"])
            with self.assertRaises(SystemExit):
                stage.main(["--out",str(p)])

    def test_no_unreal_gameplay_calls(self):
        s=(ROOT/"Tools"/"author_aureate_v4_review_scene_plan.py").read_text()
        for forbidden in ("import unreal", "request_form(", "save_current_level(",
                          "spawn_actor_from_class(", "EditorActorSubsystem", "merge_pull_request"):
            self.assertNotIn(forbidden,s)


if __name__=="__main__":
    unittest.main()
