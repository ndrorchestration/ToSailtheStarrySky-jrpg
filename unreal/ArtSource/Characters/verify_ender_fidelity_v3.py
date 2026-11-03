"""Fail-closed geometry/provenance review for noncanonical Ender V3.

GLB structural, triangle, normals, source hashes and head-landmark checks.
Engine-free source QA does not imply native import, rigging or art acceptance.
"""
import hashlib
import json
import math
from pathlib import Path
from build_ender_fidelity_v3 import BASELINES, COLOR_HOLD, LANDMARKS, ORDER
from verify_ender_fidelity_v1 import check as strict_check

REQUIRED = (
    "V3 face sculpt orbital cheek chin planes",
    "V3 L lower orbital fold", "V3 R lower orbital fold",
    "V3 swept front lock 00", "V3 swept front lock 27",
    "V3 L temple lock 00", "V3 R temple lock 07",
    "V3 nape sweep 17",
    "Sculpt nose tip", "Sculpt goggle ring -1 outer",
    "V2 L tailored waistcoat cloth", "V2 R tailored waistcoat cloth",
    "Full staff", "Center hand wrap",
)

def verify(folder):
    folder=Path(folder)
    receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "NONCANONICAL_UNRIGGED_HEAD_LANDMARK_V3_STUDY"
    assert receipt["version"]=="ender_head_landmark_v3"
    assert receipt["height_order_canon"] == ORDER
    assert receipt["pinned_predecessors"] == BASELINES
    assert receipt["head_landmarks_source_m"] == {k:list(v) for k,v in LANDMARKS.items()}
    assert receipt["hair_color_state"] == COLOR_HOLD
    assert receipt["source_baseline_untouched"] is True
    assert receipt["reference_space_measured_from_approved_image"] is False
    for name in ("approved_art_replaced","production_pawn_changed",
                 "skin_or_rigged","creator_approval","art_approval","gameplay_ready"):
        assert receipt[name] is False, name
    landmarks=receipt["head_landmarks_source_m"]
    assert landmarks["left_eye_center"][0] < 0 < landmarks["right_eye_center"][0]
    assert abs(landmarks["left_eye_center"][0]+landmarks["right_eye_center"][0])<1e-6
    assert 1.47 < landmarks["nose_tip"][1] < 1.50
    assert landmarks["nose_tip"][1] > landmarks["mouth_center"][1] > landmarks["chin_center"][1]
    proof=strict_check(folder/receipt["source"]["file"],receipt,required_parts=REQUIRED)
    assert 14500 <= proof["triangles"] <= 26000
    assert 175 <= proof["named_parts"] <= 240
    for relative,sha in BASELINES.items():
        p=Path(__file__).resolve().parent/relative
        assert hashlib.sha256(p.read_bytes()).hexdigest()==sha, "Predecessor mutation"
    return {**proof, "status":"V3_SOURCE_GEOMETRY_PASS_ART_HOLD",
            "approval":False,"native_import_verified":False}

if __name__=="__main__":
    import sys
    print(json.dumps(verify(Path(sys.argv[1])),indent=2))
