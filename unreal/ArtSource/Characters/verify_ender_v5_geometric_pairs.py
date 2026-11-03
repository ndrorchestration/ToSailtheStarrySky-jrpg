"""Read-only geometric mirror audit of 79 native MetaHuman indices.

Geometric sides and central-plane proximity are NOT anatomical labels:
eye / nose / chin identity, 2D correspondence and likeness remain unknown.
No Unreal asset mutation, image publication, sculpt, or gameplay changes.
"""
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "ReviewEvidence" / "2026-11-02" / "EnderV5LandmarkAtlas"
SOURCE = BASE / "native_landmark_index.json"
REPORT = BASE / "TechnicalAtlas" / "v5_native_geometric_pairs.json"
SOURCE_SHA = "9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed"
CENTER_TOLERANCE_CM = 0.08
PAIR_MAX_RESIDUAL_CM = 0.15

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def read_source(path=SOURCE):
    binary = Path(path).read_bytes()
    require(hashlib.sha256(binary).hexdigest() == SOURCE_SHA,
            "Native source byte hash changed")
    return json.loads(binary)

def derive(data):
    require(data.get("point_count") == 79, "Unexpected landmark count")
    rows = data.get("points")
    require(isinstance(rows, list) and len(rows) == 79, "Unexpected point array")
    require([x.get("index") for x in rows] == list(range(79)),
            "Index order is not canonical")
    for row in rows:
        xyz = row.get("xyz_cm")
        require(isinstance(xyz, list) and len(xyz) == 3 and
                all(type(v) in (int,float) and math.isfinite(v) for v in xyz),
                "Invalid or nonfinite coordinates")
    positive = [x for x in rows if x["xyz_cm"][0] > CENTER_TOLERANCE_CM]
    negative = [x for x in rows if x["xyz_cm"][0] < -CENTER_TOLERANCE_CM]
    middle = [x for x in rows if abs(x["xyz_cm"][0]) <= CENTER_TOLERANCE_CM]
    require((len(negative),len(positive),len(middle)) == (32,32,15),
            "Unexpected mirrored partition")

    def distance(a,b):
        x,y=a["xyz_cm"],b["xyz_cm"]
        return math.sqrt((x[0]+y[0])**2 + (x[1]-y[1])**2 + (x[2]-y[2])**2)

    pairs = []
    for right in positive:
        left = min(negative, key=lambda x: (distance(right,x),x["index"]))
        inverse = min(positive, key=lambda x: (distance(x,left),x["index"]))
        require(inverse["index"] == right["index"], "Mirror relation not reciprocal")
        delta = distance(right,left)
        require(delta <= PAIR_MAX_RESIDUAL_CM, "Mirror pair error too large")
        pairs.append({"negative_x_index":left["index"],
                      "positive_x_index":right["index"],
                      "mirror_residual_cm":round(delta,5)})
    pairs.sort(key=lambda x:x["negative_x_index"])
    require(len(set(p["negative_x_index"] for p in pairs))==32,
            "Mirror pairing not one-to-one")
    return {
        "schema_version":1,
        "source_native_json_sha256":SOURCE_SHA,
        "source_engine":data.get("engine"),
        "source_landmark_count":79,
        "classification":"MODEL_SPACE_GEOMETRIC_SYMMETRY_ONLY",
        "x_center_threshold_cm":CENTER_TOLERANCE_CM,
        "max_allowed_pair_residual_cm":PAIR_MAX_RESIDUAL_CM,
        "observed_max_pair_residual_cm":max(p["mirror_residual_cm"] for p in pairs),
        "negative_x_count":32,"positive_x_count":32,"near_centerline_count":15,
        "near_centerline_indices":sorted(x["index"] for x in middle),
        "mirror_pairs":pairs,
        "point_indices_anatomically_labeled":False,
        "image_space_coordinates_registered":False,
        "approved_source_face_correspondence_established":False,
        "secondary_shipdeck_used_for_face_landmarks":False,
        "hair_conflict_resolved":False,
        "face_sculpted":False,
        "artist_likeness_approved":False,
        "canonical_art_promoted":False,
        "status":"TECHNICAL_PAIRING_VERIFIED_SEMANTIC_MAPPING_HOLD"
    }

def verify_report(data, report):
    expected = derive(data)
    require(report==expected, "Native geometric report drift or false promotion")
    return expected

if __name__=="__main__":
    result=verify_report(read_source(),json.loads(REPORT.read_text(encoding="utf-8")))
    print("V5_GEOMETRIC_PAIRING_PASS",result["negative_x_count"],
          result["positive_x_count"],result["near_centerline_count"],
          result["observed_max_pair_residual_cm"],"SEMANTIC_MAPPING_HOLD")
