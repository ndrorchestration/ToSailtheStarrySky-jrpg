"""Engine-free factual guardrails for real Ender V2 sealed goggles native proof.

GitHub-hosted checks validate receipt consistency and noncanonical boundaries.
The genuine 3D GLB and GPU PNGs remain on authorized workstation NEONTIC;
hosted tests do not independently render or inspect their pixels.
"""
import copy
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent/"Evidence"
V2="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
ORIGINAL="e46af39346a953c36c010e6f103ff700b8d13ed32a41cf44c0af3b69f0c296d0"
META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
BEFORE="9e032f7350f3013e646619ab8d86280bce0b7c08ef191729d749562e015b2990"
LOWER="dc9116e68a5404ebb4b377b78f443a902a5a4521734ad5533e94793e104fc709"

def read(filename):
    return json.loads((ROOT/filename).read_text(encoding="utf8"))

def check(ok,reason):
    if not ok: raise ValueError(reason)

def verify(build,imp,spatial,first,second):
    check(build["status"]=="STATIC_3D_SEALED_GOGGLES_V2_SOURCE_VALIDATED_NONCANONICAL","source build")
    check(build["glb_sha256"]==V2 and build["glb_bytes"]==1412976,"source identity")
    check(build["material_count"]==11 and build["material_primitives"]==11,"source materials")
    check(build["triangle_count"]==57288 and build["vertices"]==29792,"source mesh")
    check(all(abs(a-b)<0.02 for a,b in zip(build["extents_cm"],[19.2,19.171,8.02])),"source scale")
    check(build["rigged"] is False and build["approved_as_canonical"] is False,"source canon")

    check(imp["status"]=="NATIVE_V2_SEALED_GOGGLES_STATICMESH_IMPORT_PASS_FIT_PENDING","native import")
    check(imp["source_glb_sha256"]==V2 and imp["original_package_glb_sha256"]==ORIGINAL,"build provenance")
    check(imp["original_binary_parity_claim"] is False,"false binary identity")
    check(imp["material_slots"]==11,"Unreal material slots")
    check(all(abs(a-b)<0.02 for a,b in zip(imp["unreal_mesh_bounds_xyz_cm"],[19.2,8.02,19.171])),"import axes")
    check(imp["meta_sha256_after"]==META and imp["map_sha256_after"]==MAP,"native import modified Ender/map")
    check(imp["glb_sha256_after"]==V2,"native import source changed")
    for k in ("fitted_to_metahuman","visual_material_approval","head_collision_pass",
              "rig_verified","gameplay_modified","canon_promoted","V1_replaced"):
        check(imp[k] is False,"false native import approval "+k)

    check(spatial["status"]=="NATIVE_V2_UPRIGHT_AXES_AND_THREE_AABB_TRIALS_PASS_VISUAL_FIT_PENDING","spatial")
    check(spatial["candidate_rotation_pitch_yaw_roll"]==[90,180,0],"wrong native rotation")
    check(spatial["meta_sha256_after"]==META and spatial["map_sha256_after"]==MAP,"spatial source drift")
    check(spatial["goggles_source_sha256_after"]==V2,"spatial V2 GLB drift")
    check(len(spatial["trials"])==3,"expected 3 temporary trials")
    checks=[
        ("eye_height_hypothesis",[0,11.4,164.5],22),
        ("above_brow_hypothesis",[0,9.5,171.5],1),
        ("lower_forehead_hypothesis",[0,9.5,168.5],6)
    ]
    for item,(name,position,count) in zip(spatial["trials"],checks):
        check(item["label"]==name and item["relative_position_cm"]==position,"trial identity")
        check(item["indexed_face_points_inside_outer_aabb"]==count,"point counts changed")
        check(item["outer_AABB_is_NOT_wearable_fit"] is True,"false wearable fit")
        check(all(abs(a-b)<0.02 for a,b in zip(item["native_outer_aabb_cm"],[19.2,19.171,8.02])),"world bounds")
    for k in ("actual_goggle_vs_skin_triangle_collision_verified","head_fitted","artist_approved",
              "rig_attached","level_saved","source_assets_modified","canon_promoted"):
        check(spatial[k] is False,"false spatial approval "+k)

    for capture,position,expected_sha in ((first,[0,9.5,171.5],BEFORE),
                                            (second,[0,9.5,168.5],LOWER)):
        check(capture["status"]=="NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED","native GPU")
        check(capture["source_goggles_sha256"]==V2 and capture["goggles_sha256_after"]==V2,"GPU GLB drift")
        check(capture["source_meta_sha256"]==META and capture["meta_sha256_after"]==META,"GPU MetaHuman drift")
        check(capture["source_map_sha256"]==MAP and capture["map_sha256_after"]==MAP,"GPU map drift")
        check(capture["goggles_position_relative_to_v5_cm"]==position,"capture position drift")
        check(capture["goggles_rotation_pitch_yaw_roll_deg"]==[90,180,0],"capture rotation drift")
        check(len(capture["captures"])==1,"expected single real image receipt")
        check(capture["captures"][0]["sha256_png_core"]==expected_sha,"PNG core evidence changed")
        check(capture["captures"][0]["image_size"]==[480,320] and capture["captures"][0]["crc_pass"],"PNG integrity")
        for k in ("canonical","face_likeness_approved","goggles_fit_approved","materials_artist_approved",
                  "rigging_verified","source_assets_saved","review_map_saved","production_game_modified"):
            check(capture[k] is False,"render treated as art approval "+k)
    check(BEFORE!=LOWER,"independent viewpoint experiment must not be identical")
    return "SOURCE_AND_NATIVE_IMPORT_AND_TWO_GPU_RECEIPTS_CONSISTENT_NONCANONICAL"

class NativeV2GogglesEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.args=[read(x) for x in (
            "neontic_v2_geometry_rebuild.json","native_import_v2.json",
            "native_spatial_v2.json","native_v2_above_brow_front_capture.json",
            "native_v2_lower_forehead_capture.json")]

    def test_receipts_provenance(self):
        self.assertEqual(verify(*self.args),
            "SOURCE_AND_NATIVE_IMPORT_AND_TWO_GPU_RECEIPTS_CONSISTENT_NONCANONICAL")

    def test_false_fit_and_canon_refused(self):
        for index,key in ((1,"fitted_to_metahuman"),(2,"head_fitted"),(3,"goggles_fit_approved"),
                          (4,"materials_artist_approved"),(4,"canonical")):
            args=copy.deepcopy(self.args)
            args[index][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify(*args)

    def test_source_drift_refused(self):
        args=copy.deepcopy(self.args)
        args[3]["meta_sha256_after"]="not-verified"
        with self.assertRaises(ValueError):
            verify(*args)

if __name__=="__main__":
    unittest.main()
