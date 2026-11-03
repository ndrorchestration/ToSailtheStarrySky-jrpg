"""Engine-free integrity gates for native Unreal goggles-to-MetaHuman trials.

These test saved receipts. They DO NOT verify face fit, visual appearance,
mesh intersection, scalp/strap contact, rendering, rig or game integration.
"""
import copy
import json
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent/"Evidence"
SHA_META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
SHA_GOGGLES="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
EXPECTED=[18.21768,15.35,6.1]

def load(name):
    return json.loads((BASE/name).read_text(encoding="utf-8"))

def require(b,reason):
    if not b:raise ValueError(reason)

def verify_claims(imp,axis,failed,stage):
    require(imp["status"]=="MH5_NATIVE_GOGGLES_IMPORT_PASS_POSITIONING_PENDING",
            "import success mislabeled")
    require(imp["source_glb_sha256"]==SHA_GOGGLES,"input GLB drift")
    require(imp["source_original_metahuman_sha256"]==SHA_META,"MH5 origin drift")
    require(imp["source_map_sha256"]==SHA_MAP,"map origin drift")
    require(imp["meta_sha256_after"]==SHA_META and imp["map_sha256_after"]==SHA_MAP,
            "source MetaHuman or map mutated during import")
    require(imp["material_slot_count"]==9 and
            all(abs(a-b)<.1 for a,b in zip(imp["bounds_xyz_cm"],[18.21768,6.1,15.35])),
            "imported mesh topology, material count or axis drift")
    require(imp["art_review_only"] and not imp["fitted_to_face"] and
            not imp["visual_acceptance"] and not imp["canonical"],"unapproved import promoted")

    require(axis["status"]=="NATIVE_AXIS_SEARCH_PASS_PREFERRED_AVAILABLE",
            "native axis search not PASS")
    require(axis["meta_sha256_after"]==SHA_META and axis["map_sha256_after"]==SHA_MAP,
            "axis inspection wrote source")
    require(axis["preferred_orientation_count"]>=1,"no native forward-facing orientation")
    preference=[c for c in axis["preferred_orientations"]
                if c["pitch_yaw_roll_deg"]==[90,180,0]]
    require(len(preference)==1,"preferred corrected native rotation missing")
    p=preference[0]
    require(all(abs(a-b)<.2 for a,b in zip(p["world_aabb_dimensions_cm"],EXPECTED)),
            "preferred native width/depth/height mismatch")
    require(p["local_x_mapped_to_world"][0]<-.99 and
            p["local_y_mapped_to_world"][2]>.99 and
            p["local_z_mapped_to_world"][1]>.99,"face-forward axis mapping drift")
    require(axis["face_fit_proven"] is False and
            axis["artist_approved"] is False and
            axis["native_screenshot_available"] is False,
            "native coordinate search falsely promoted art")

    require(failed["status"]=="SPATIAL_REVIEW_FAILED","first failed attempt overwritten")
    require(failed["candidate_rotation_pitch_yaw_roll_deg"]==[0.,180.,90.],
            "negative-control rotation changed")
    require(len(failed["candidates"])==2,"negative-control evidence altered")
    require(abs(failed["candidates"][0]["outer_envelope_width_cm"]-6.1)<.2,
            "negative control no longer reproduces sideways width")
    require(failed["meta_sha256_after"]==SHA_META and failed["map_sha256_after"]==SHA_MAP,
            "negative-control test mutated source")

    require(stage["status"]=="MH5_NATIVE_GOGGLES_AXES_RESTORED_TWO_BOUNDS_HYPOTHESES_RECORDED",
            "corrected spatial review falsely marked")
    require(stage["candidate_rotation_pitch_yaw_roll_deg"]==[90.,180.,0.],
            "corrected orientation drift")
    require(len(stage["candidates"])==2,"candidate count changed")
    labels=[c["label"] for c in stage["candidates"]]
    require(labels==["at_eye_height_hypothesis","above_brow_hypothesis"],
            "trial identity changed")
    for c in stage["candidates"]:
        actual=[c["outer_envelope_width_cm"],c["outer_envelope_forward_depth_cm"],
                c["outer_envelope_vertical_height_cm"]]
        require(all(abs(a-b)<.2 for a,b in zip(actual,EXPECTED)),
                "world AABB dimensions changed")
        require(c["no_collisions_or_head_fit_established"] is True and
                c["meaning"]=="PROVISIONAL_BROAD_PHASE_BOUNDS_NOT_FACIAL_FIT",
                "AABB proximity overclaimed as physical fit")
        require(c["source_landmark_inside_AABB_count"]==
                len(c["source_landmark_inside_AABB_indices"]),"proximity count drift")
        require(c["source_landmark_within_1cm_of_AABB_count"]>=
                c["source_landmark_inside_AABB_count"],"distance hierarchy drift")
    require((stage["candidates"][0]["source_landmark_inside_AABB_count"],
             stage["candidates"][1]["source_landmark_inside_AABB_count"])==(18,1),
            "native AABB broad-phase baseline changed")
    require(stage["meta_sha256_after"]==SHA_META and stage["map_sha256_after"]==SHA_MAP,
            "source asset altered during placement")
    for k in ("actual_mesh_intersection_proven","fit_approved",
              "attachment_socket_approved","native_gpu_fitting_screenshot",
              "native_points_anatomically_named","rigged_game_character",
              "production_or_canon_promoted","character_asset_saved","level_saved"):
        require(stage[k] is False,"false approval or unauthorized edit: "+k)
    return {"status":"NATIVE_RECEIPTS_VALID_GEOMETRY_ONLY", "candidate_count":2}

class MH5FitEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=[load(n) for n in
            ("native_import01.json","native_axis_search01.json",
             "native_spatial_review01.json","native_spatial_review02.json")]

    def test_exact_native_evidence_and_hold(self):
        self.assertEqual(verify_claims(*self.inputs)["candidate_count"],2)

    def test_noncanonical_approval_rejected(self):
        for key in ("fit_approved","actual_mesh_intersection_proven",
                    "native_gpu_fitting_screenshot","production_or_canon_promoted",
                    "character_asset_saved","level_saved"):
            inputs=copy.deepcopy(self.inputs)
            inputs[3][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify_claims(*inputs)

    def test_wrong_axis_and_false_negative_control_rejected(self):
        inputs=copy.deepcopy(self.inputs)
        inputs[3]["candidate_rotation_pitch_yaw_roll_deg"]=[0,180,90]
        with self.assertRaises(ValueError):verify_claims(*inputs)
        inputs=copy.deepcopy(self.inputs)
        inputs[2]["status"]="PASS"
        with self.assertRaises(ValueError):verify_claims(*inputs)

    def test_source_hash_drift_rejected(self):
        inputs=copy.deepcopy(self.inputs)
        inputs[3]["map_sha256_after"]="unverified"
        with self.assertRaises(ValueError):verify_claims(*inputs)

if __name__=="__main__":
    unittest.main()
