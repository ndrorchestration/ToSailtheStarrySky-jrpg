"""Engine-free negative controls for Ender V2 material and rear-strap screenshot receipts.

These hosted tests protect provenance and claims. They do not render Unreal,
recalculate the private screenshot's pixels, validate physical head contact,
or substitute for cinematic author review.
"""
import copy
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GLB="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
FRONT="6ef2842848c21207cd17859341b015169e91d8929ea5c9f96a10f3f9aa5efbb2"
SIDE="3876c933e281831417613a3ced8d24beb1527c593b28170efc4cd06d74fc7c60"

def read(name):
    return json.loads((HERE/name).read_text(encoding="utf-8"))

def validate(front,side,metrics,montage):
    for r,sha in ((front,FRONT),(side,SIDE)):
        if not r["status"].endswith("_PNG_CORE_PASS_VISUAL_UNREVIEWED"):
            raise ValueError("Missing native screenshot PASS")
        if r["source_meta_sha256"]!=META or r["meta_sha256_after"]!=META:
            raise ValueError("MetaHuman asset drift")
        if r["source_map_sha256"]!=MAP or r["map_sha256_after"]!=MAP:
            raise ValueError("Review map drift")
        if r["source_goggles_sha256"]!=GLB or r["goggles_sha256_after"]!=GLB:
            raise ValueError("Goggles source drift")
        if len(r["captures"])!=1:
            raise ValueError("Capture count drift")
        c=r["captures"][0]
        if not c["crc_pass"] or c["image_size"]!=[480,320] or c["sha256_png_core"]!=sha:
            raise ValueError("Native PNG receipt mismatch")
        if r["goggles_rotation_pitch_yaw_roll_deg"]!=[90,180,0]:
            raise ValueError("Unexpected rotation")
        if r["goggles_position_relative_to_v5_cm"]!=[0,9.5,168.5]:
            raise ValueError("Position drift")
        for key in ("goggles_fit_approved","materials_artist_approved",
                    "face_likeness_approved","real_head_collision_verified",
                    "rigging_verified","canonical","source_assets_saved",
                    "review_map_saved","production_game_modified"):
            if r[key] is not False:
                raise ValueError("False source edit or visual-art approval: "+key)
    if side["review_camera"]!="rear-side +X,-Y, fov 44, looking at upper head":
        raise ValueError("Side camera label changed")
    if side["temporary_light_powers"]!=[11.0,6.5,5.2]:
        raise ValueError("Side lighting changed")
    if metrics["status"]!="NATIVE_REAL_PNG_FIXED_ROI_COMPARISON_REVIEW_ONLY":
        raise ValueError("Missing exposure comparison")
    if not 7.7<metrics["goggles_near_white_drop_percentage_points"]<7.9:
        raise ValueError("Goggles ROI result changed")
    if not 72.2<metrics["face_near_white_drop_percentage_points"]<72.4:
        raise ValueError("Face ROI result changed")
    for key in ("human_artist_material_approval","goggles_fit_verified",
                "metahuman_material_quality_approved"):
        if metrics[key] is not False:raise ValueError("ROI falsely approved art")
    if montage["status"]!="NATIVE_3_IMAGE_MONTAGE_VERIFIED_NONCANONICAL":
        raise ValueError("Invalid montage provenance")
    if montage["sha256"]!="5819d9e1bf267ed5849d96088c845bae1f1f465282cd17357a28128581947d7c":
        raise ValueError("Montage hash mismatch")
    if len(montage["sources"])!=3 or montage["materials_approved"] or montage["fit_verified"]:
        raise ValueError("Montage promoted or incomplete")
    if montage["game_assets_modified"] or montage["original_pixel_data_modified"]:
        raise ValueError("Montage is not a source-preserving view")
    return True

class NativeV2ReviewEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=[read(s) for s in (
            "native_v2_low_lights_front_receipt.json",
            "native_v2_rearside_low_lights_receipt.json",
            "native_v2_exposure_roi_metrics.json",
            "native_v2_review_montage_manifest.json")]

    def test_evidence_valid(self):
        self.assertTrue(validate(*self.inputs))

    def test_false_fit_claim_rejected(self):
        for key in ("goggles_fit_approved","materials_artist_approved",
                    "real_head_collision_verified","canonical"):
            x=copy.deepcopy(self.inputs)
            x[1][key]=True
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(*x)

    def test_image_hash_change_rejected(self):
        x=copy.deepcopy(self.inputs)
        x[0]["captures"][0]["sha256_png_core"]="different"
        with self.assertRaises(ValueError):validate(*x)

    def test_change_in_roi_evidence_rejected(self):
        x=copy.deepcopy(self.inputs)
        x[2]["face_near_white_drop_percentage_points"]=0
        with self.assertRaises(ValueError):validate(*x)

if __name__=="__main__":
    unittest.main()
