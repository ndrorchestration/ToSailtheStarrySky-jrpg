"""Engine-free guardrails for exact native V5 Ender review capture scripts.

These tests check source policies, not Unreal execution or artistic likeness.
"""
import ast
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
CAMERAS={
    "capture_profile_plus_x.py":{
        "folder":"ender_v5_green_faceclose01",
        "filename":"face_front_close.png",
        "position":"origin.x+105,origin.y+0,origin.z+174",
        "view":"FRONTAL_PLUS_X_MODEL_AXIS_UNVERIFIED_AS_ANATOMICAL_FRONT",
    },
    "capture_front_plus_y.py":{
        "folder":"ender_v5_green_truefront02",
        "filename":"face_truefront_plus_y.png",
        "position":"origin.x+0,origin.y+120,origin.z+169",
        "view":"FRONTAL_PLUS_Y_MODEL_AXIS_PROVISIONAL",
    },
    "capture_threequarter_plus_x_plus_y.py":{
        "folder":"ender_v5_green_threequarter03",
        "filename":"face_threequarter_front.png",
        "position":"origin.x+55,origin.y+105,origin.z+169",
        "view":"THREEQUARTER_PLUS_X_PLUS_Y_REVIEW",
    },
}
FORBIDDEN=("save_loaded_asset(","save_current_level(","request_auto_rigging(",
           "build_meta_human(","request_texture_sources(","remove_face_rig(",
           "EditorAssetLibrary.delete_asset(")

class BoundedNativeReviewContract(unittest.TestCase):
    def test_distinct_receipts_and_exact_camera_positions(self):
        self.assertEqual(len({c["folder"] for c in CAMERAS.values()}),3)
        self.assertEqual(len({c["filename"] for c in CAMERAS.values()}),3)
        for name,c in CAMERAS.items():
            with self.subTest(view=name):
                src=(HERE/name).read_text(encoding="utf-8")
                ast.parse(src, filename=name)
                self.assertIn('OUT=ROOT/"Saved/CharacterLookdev/V5NativeScreens/'+c["folder"]+'"',src)
                self.assertIn(c["filename"],src)
                self.assertIn(c["position"],src)
                self.assertIn(c["view"],src)
                self.assertIn('ROOT.as_posix().lower()=="c:/mh4/castallsandbox"',src)
                self.assertIn('guard(not OUT.exists(),"refuse overwrite")',src)
                self.assertIn('digest(ASSET)==ASSET_SHA',src)
                self.assertIn('digest(MAP)==MAP_SHA',src)
                self.assertIn('record["asset_sha256_after"]=digest(ASSET)',src)
                self.assertIn('record["map_sha256_after"]=digest(MAP)',src)
                self.assertIn('"visual_likeness_approved":False',src)
                self.assertIn('"production_canon_promoted":False',src)
                for x in FORBIDDEN:
                    self.assertNotIn(x,src)

    def test_contact_sheet_checks_native_png_receipts(self):
        src=(HERE/"build_native_three_angle_contact_sheet.py").read_text(encoding="utf-8")
        ast.parse(src)
        for c in CAMERAS.values():
            self.assertIn(c["folder"],src)
            self.assertIn(c["filename"],src)
        self.assertIn('if data["captures"][0]["sha256"]!=sha:',src)
        self.assertIn('cropped_or_invented_face":False',src)
        self.assertIn('"canonical":False',src)
        self.assertIn("if OUT.exists() or MANIFEST.exists():",src)

if __name__=="__main__":
    unittest.main()
