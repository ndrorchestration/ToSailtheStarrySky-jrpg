"""Fail-closed artist-reference selection gate for Ender V5 (no source images)."""
from __future__ import annotations
import json
from pathlib import Path

POLICY_PATH = Path(__file__).with_name("ender_v5_reference_priority.json")
FEATURES = (
    "image_left_eye_center", "image_right_eye_center", "nose_tip", "chin_point"
)
APPROVED_NAMES = {
    "Aetherwake: Steampunk Skybound Crew.png",
    "Aetherwake: JRPG Character Design Board.png",
    "Ender: Solarpunk RPG Character Sheet.png",
}
EXPECTED_PRIORITY = "FIRST_APPROVED_FACES_PREFERRED"
EXPECTED_SECONDARY = "CLOTHING_MATERIALS_EQUIPMENT_LIGHTING_ONLY"

def require(condition, description):
    if not condition:
        raise ValueError(description)

def verify_reference_policy(p):
    require(isinstance(p, dict), "Reference policy must be an object")
    require(p.get("schema_version") == 1, "Unexpected contract schema")
    require(p.get("program") == "To Sail the Starry Sky", "Wrong project")
    require(p.get("character") == "Ender", "Wrong character")
    require(p.get("creator_priority") == EXPECTED_PRIORITY,
            "Primary facial authority changed")
    require(p.get("primary_source_selection") == "REQUIRES_EXPLICIT_ARTIST_CONFIRMATION",
            "An unreviewed primary image was silently selected")
    refs = p.get("earlier_face_reference_candidates")
    require(isinstance(refs, list) and len(refs) == 3,
            "Unexpected original-reference inventory")
    require({r.get("name") for r in refs} == APPROVED_NAMES,
            "Original facial reference inventory drift")
    for r in refs:
        sha = r.get("sha256")
        require(isinstance(sha, str) and len(sha) == 64 and
                all(c in "0123456789abcdef" for c in sha),
                "Source reference hash invalid")
        require(r.get("role") in
                ("OLDER_REALISTIC_FACE_CANDIDATE", "APPROVED_INDIVIDUAL_CROSSCHECK"),
                "Reference role unexpected")
    require(p.get("secondary_shipdeck_usage") == EXPECTED_SECONDARY,
            "Secondary artwork scope promoted")
    require(p.get("secondary_shipdeck_facial_landmarks_authorized") is False,
            "Secondary image must not generate facial landmarks")
    require(p.get("image_space_coordinates_published") is False and
            p.get("original_reference_image_copied_into_repository") is False,
            "Private source or candidate coordinates improperly published")
    require(p.get("private_annotation_status") == "PROVISIONAL_NOT_CREATOR_REVIEWED",
            "Private candidate measurements falsely reviewed")
    require(p.get("native_landmark_count_verified") == 79,
            "Native index contract drift")
    require(p.get("native_semantic_mapping_status") ==
            "UNMAPPED_REQUIRES_HUMAN_REVIEW", "Native index mappings overclaimed")
    points = p.get("proposal_points")
    require(isinstance(points, list) and len(points) == 4,
            "Four-image-feature scope changed")
    require(tuple(entry.get("name") for entry in points) == FEATURES,
            "Image-plane feature identity/order changed")
    for entry in points:
        require(entry.get("image_x_px") is None and
                entry.get("image_y_px") is None and
                entry.get("native_index") is None and
                entry.get("artist_verified") is False,
                "Unapproved 2D or 3D landmark correspondence published")
    require(p.get("hair_color_conflict") == "HOLD_REQUIRES_CREATOR_RESOLUTION",
            "Hair color conflict silently resolved")
    require(p.get("facial_sculpt_approved") is False and
            p.get("canonical_face_asset_promoted") is False,
            "Unverified facial asset promoted")
    return {
        "status": "SOURCE_AUTHORITY_RECORDED_MAPPING_HOLD",
        "earlier_candidate_count": len(refs),
        "unmapped_features": list(FEATURES),
        "native_landmark_count": 79,
        "private_art_copied": False,
    }

if __name__ == "__main__":
    print(json.dumps(verify_reference_policy(json.loads(
        POLICY_PATH.read_text(encoding="utf-8"))), sort_keys=True))
