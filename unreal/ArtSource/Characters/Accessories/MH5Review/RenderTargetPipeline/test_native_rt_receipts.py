"""Engine-free evidence checks for UE 5.8 Ender goggles render target workaround.

Checks honest receipt semantics and provenance only. Actual native image bytes
stay on the owner's private workstation, so hosted CI does not independently
validate the binary, artistic fidelity, or the native editor run.
"""
import copy,json,unittest
from pathlib import Path

DIR=Path(__file__).resolve().parent/"Evidence"
META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GOGGLES="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
SOURCE_PNG="212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808"

def load(name):
    return json.loads((DIR/name).read_text(encoding="utf-8"))

def validate_record(cube,validated_cube,native,verified):
    if cube["status"]!="DIAGNOSTIC_FAILED":
        raise ValueError("Original cube validator failure must be preserved")
    if cube.get("render_target_export_success") is True:
        raise ValueError("Unvalidated original cube falsely marked success")
    if validated_cube["status"]!="PNG_CORE_VALID_AND_TRAILING_BYTES_REMOVED":
        raise ValueError("Cube second opinion missing")
    if validated_cube["original_sha256"]!=verified_cube_raw_hash:
        raise ValueError("Cube original binary SHA drift")
    if validated_cube["trailing_bytes_removed"]!=14364 or not validated_cube["pillow_verify"]:
        raise ValueError("Cube PNG postcheck failed")

    if native["status"]!="NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED":
        raise ValueError("Native V5 capture no longer a technical proof")
    if len(native["captures"])!=1:
        raise ValueError("Native capture count drift")
    if native["source_meta_sha256"]!=META or native["meta_sha256_after"]!=META:
        raise ValueError("Character source changed")
    if native["source_map_sha256"]!=MAP or native["map_sha256_after"]!=MAP:
        raise ValueError("Original scene map changed")
    if native["source_goggles_sha256"]!=GOGGLES or native["goggles_sha256_after"]!=GOGGLES:
        raise ValueError("Goggle source changed")
    capture=native["captures"][0]
    if capture["sha256_png_core"]!=SOURCE_PNG or capture["image_size"]!=[480,320]:
        raise ValueError("Expected native PNG core receipt missing")
    if not capture["crc_pass"] or capture["trailing_bytes_after_iend"]!=1555:
        raise ValueError("Native PNG CRC or trailing anomaly evidence changed")
    if verified["status"]!="NATIVE_V5_GOGGLES_PNG_CORE_VERIFIED_SAFE_COPY":
        raise ValueError("No verified postprocessed PNG")
    if verified["original_raw_sha256"]!=capture["sha256_raw"]:
        raise ValueError("Original file SHA mismatch between receipts")
    if verified["validated_png_sha256"]!=SOURCE_PNG:
        raise ValueError("Validated PNG image core SHA mismatch")
    if verified["trailing_bytes_removed"]!=1555 or not verified["pillow_verified"]:
        raise ValueError("Unverified image integrity")
    if verified["pixel_data_modified_in_png"]:
        raise ValueError("Claim that core PNG pixels changed")
    if not verified["review_webp_lossy_recompression"]:
        raise ValueError("Lossy WebP copy must be disclosed")
    if verified["review_webp_sha256"]!="412b5b2ca48d167c3c79ca25eee04a69044785533b1aef108a2268381e6561e0":
        raise ValueError("Review WebP SHA drift")
    for key in ("real_head_collision_verified","goggles_fit_approved",
                "materials_artist_approved","face_likeness_approved",
                "rigging_verified","canonical","production_game_modified",
                "source_assets_saved","review_map_saved"):
        if native[key] is not False:
            raise ValueError("Unapproved 3D art promotion: "+key)
    for key in ("wearable_head_fit_verified","material_fidelity_verified",
                "artist_accepted","canonical","production_game_asset"):
        if verified[key] is not False:
            raise ValueError("Review copy falsely approved: "+key)
    return "TECHNICAL_RENDER_PROOF_WITH_VISUAL_APPROVAL_HELD"

verified_cube_raw_hash="02c72dc7feaa55c627f3519e699704245ec1938a3c5920b0403baed784cb615e"

class RenderTargetEvidenceQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=[
            load("cube_capture_initial_validator_failed.json"),
            load("cube_png_second_opinion.json"),
            load("v5_goggles_native_rt_capture.json"),
            load("v5_goggles_png_integrity.json"),
        ]

    def test_exact_native_receipt_semantics(self):
        self.assertEqual(validate_record(*self.data),
                         "TECHNICAL_RENDER_PROOF_WITH_VISUAL_APPROVAL_HELD")

    def test_no_false_likeness_or_fit_approval(self):
        for key in ("goggles_fit_approved","canonical",
                    "materials_artist_approved","face_likeness_approved"):
            x=copy.deepcopy(self.data)
            x[2][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_record(*x)

    def test_png_sha_drift_rejected(self):
        x=copy.deepcopy(self.data)
        x[3]["validated_png_sha256"]="fabricated"
        with self.assertRaises(ValueError):validate_record(*x)

    def test_original_false_diagnostic_pass_rejected(self):
        x=copy.deepcopy(self.data)
        x[0]["status"]="SUCCESS"
        with self.assertRaises(ValueError):validate_record(*x)

    def test_minus2_ev_native_capture_did_not_change_pixels(self):
        baseline=load("v5_goggles_native_rt_capture.json")
        adjusted=load("v5_goggles_minus2_capture.json")
        comparison=load("v5_goggles_minus2_identical_pixels.json")
        self.assertEqual(adjusted["status"],
            "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED")
        self.assertEqual(adjusted["exposure_bias_ev"],-2.0)
        self.assertEqual(adjusted["source_meta_sha256"],baseline["source_meta_sha256"])
        self.assertEqual(adjusted["source_map_sha256"],baseline["source_map_sha256"])
        self.assertEqual(adjusted["source_goggles_sha256"],baseline["source_goggles_sha256"])
        self.assertEqual(adjusted["captures"][0]["sha256_png_core"],
            baseline["captures"][0]["sha256_png_core"])
        self.assertEqual(comparison["status"],
            "EXPOSURE_MINUS2_RENDER_IDENTICAL_PIXELS_TO_BASELINE")
        self.assertTrue(comparison["same_png_core_bytes"])
        self.assertTrue(comparison["same_rgb_pixels"])
        self.assertEqual(comparison["baseline_core_sha256"],
            comparison["minus2_core_sha256"])
        self.assertFalse(comparison["visual_quality_approved"])
        self.assertFalse(comparison["any_sculpt_or_material_asset_changed"])
        self.assertFalse(comparison["goggles_fit_verified"])
        self.assertFalse(comparison["canonical"])

if __name__=="__main__":
    unittest.main()
