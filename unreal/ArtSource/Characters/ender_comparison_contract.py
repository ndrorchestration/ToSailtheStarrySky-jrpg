"""Unreal Engine 5.8 Ender V1/V2 art-review stage contract.

Pure Python, deliberately independent of Unreal so source CI can fail closed.
The geometry is noncanonical, all captured evidence needs native Editor QA.
"""
from dataclasses import asdict, dataclass
import json
from pathlib import Path

EXPECTED = {
    "EnderV1": {
        "sha256": "3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38",
        "asset_fragment": "/Game/ArtLookdev/Characters/EnderFidelityV1/",
        "receipt": "ender_fidelity_v1_native_intake.json",
    },
    "EnderV2": {
        "sha256": "e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8",
        "asset_fragment": "/Game/ArtLookdev/Characters/EnderFidelityV2/",
        "receipt": "ender_fidelity_v2_native_intake.json",
    },
}

# x increases right; +Y is Ender's native face-forward direction.
# All positions in Unreal centimeters, *not* generator source meters.
CANDIDATE_POSITIONS = {"EnderV1": (-115.0, 0.0, 0.0),
                       "EnderV2": (115.0, 0.0, 0.0)}
CAMERAS = (
    ("comparison_front", (0.0, 590.0, 108.0), -90.0, 43.0),
    ("comparison_three_quarter", (400.0, 400.0, 108.0), -135.0, 43.0),
)
# Front retains its previously verified perspective camera. One orthographic
# three-quarter camera eliminates perspective depth-dependent apparent scale.
CAMERA_PROJECTIONS = {
    "comparison_front": {"mode": "perspective"},
    "comparison_three_quarter": {"mode": "orthographic", "ortho_width_cm": 480.0},
}
CANON_HEIGHT = "Reson > Aepex > Ender > Ionia > Lyra"
MAP = "/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"


def check_project(project_dir):
    """Block any non-disposable project, including the real Unreal project."""
    project = Path(project_dir).resolve()
    if project.name != "CastAllSandbox":
        raise ValueError("Refusing non-disposable Unreal project")
    return project


def validate_native_intake(name, receipt):
    if name not in EXPECTED:
        raise ValueError("Unknown candidate")
    expected = EXPECTED[name]
    if receipt.get("status") != "NATIVE_IMPORT_PASS_ART_UNAPPROVED":
        raise ValueError("No native import proof")
    if receipt.get("source_sha256") != expected["sha256"]:
        raise ValueError("Source SHA mismatch")
    asset = receipt.get("asset")
    if not isinstance(asset, str) or not asset.startswith(expected["asset_fragment"]):
        raise ValueError("Wrong Unreal asset location")
    if receipt.get("visual_acceptance") is not False:
        raise ValueError("Review candidate was improperly marked approved")
    if receipt.get("creator_approval") is not False:
        raise ValueError("Unapproved creator status")
    if receipt.get("skin_or_rigged") is not False:
        raise ValueError("Study falsely marked skinned")
    if receipt.get("baseline_cast_unchanged") is not True:
        raise ValueError("Baseline cast integrity hold missing")
    return asset


def load_intake_receipts(project_dir):
    project = check_project(project_dir)
    directory = project / "Saved" / "CharacterLookdev"
    receipts = {}
    for name, info in EXPECTED.items():
        data = json.loads((directory / info["receipt"]).read_text(encoding="utf-8"))
        receipts[name] = validate_native_intake(name, data)
    return receipts


def review_plan():
    if set(CANDIDATE_POSITIONS) != set(EXPECTED):
        raise ValueError("Unexpected character selection")
    a, b = CANDIDATE_POSITIONS["EnderV1"], CANDIDATE_POSITIONS["EnderV2"]
    if abs(a[0] + b[0]) > 0.001 or a[1:] != b[1:]:
        raise ValueError("Comparison must be centered and depth matched")
    if not (160 <= b[0] - a[0] <= 280):
        raise ValueError("Insufficient separation or unusable framing")
    if [c[0] for c in CAMERAS] != ["comparison_front", "comparison_three_quarter"]:
        raise ValueError("Required native views missing")
    if CAMERAS[0][1][1] <= 0 or CAMERAS[0][2] != -90:
        raise ValueError("Camera must face source-native +Y front")
    if CAMERAS[1][2] != -135:
        raise ValueError("Noncomparable three-quarter angle")
    for _, pos, _, fov in CAMERAS:
        if any(not isinstance(v, (int, float)) for v in pos) or not 35 <= fov <= 55:
            raise ValueError("Invalid camera preset")
    if set(CAMERA_PROJECTIONS) != set(name for name, *_ in CAMERAS):
        raise ValueError("Missing camera projection contract")
    if CAMERA_PROJECTIONS["comparison_front"] != {"mode": "perspective"}:
        raise ValueError("Front camera unexpectedly changed")
    if CAMERA_PROJECTIONS["comparison_three_quarter"] != {
            "mode": "orthographic", "ortho_width_cm": 480.0}:
        raise ValueError("Three-quarter must use matched-scale orthographic projection")
    return {
        "camera_projections": CAMERA_PROJECTIONS,
        "status": "SOURCE_REVIEW_STAGE_ONLY_NOT_NATIVE_PROOF",
        "map": MAP,
        "candidate_positions_cm": CANDIDATE_POSITIONS,
        "cameras": CAMERAS,
        "height_order_canon": CANON_HEIGHT,
        "end_user_visual_approval": False,
        "approved_art_import": False,
        "source_character_models_unchanged": True,
    }
