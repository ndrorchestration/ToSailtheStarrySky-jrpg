"""Read-only conservative V4 wing/habitation AABB audit; NOT physics clearance.

Native review binaries are private and are NOT committed to Git. The auditor
takes their paths explicitly, checks known SHA-256s and the saved .umap digest,
and produces a HOLD finding. glTF-to-UE axis and authored yaw/roll composition
are a bounded review approximation, NOT an Unreal collision sweep.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

REPO = Path(__file__).resolve().parents[2]
STAGE = REPO / "unreal/Tools/stage_aureate_v4_coupled_habitation_native.py"
STAGE_LF_SHA = "520990a7800ce46822998bcc93e36af1b87d7c4e23bcb4cdd8f7523b9979d12d"
SOURCES = {
    "bridge": "a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506",
    "quarters": "69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0",
    "wing": "04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73",
}
REVIEW_MAP_SHA = "14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362"
PIVOT = (40.0, 0.0, 72.0)
ORIGINS = {"bridge": (170.0, 0.0, 133.0), "quarters": (0.0, 0.0, 0.0)}
FORE_WINGS = {
    "FORE_PORT": ((145.0, -99.0, 55.0), -80.0, -8.0),
    "FORE_STARBOARD": ((145.0, 99.0, 55.0), 80.0, 8.0),
}


class EnvelopeAuditHold(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_stage(stage: Path = STAGE) -> None:
    raw = stage.read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(raw).hexdigest() != STAGE_LF_SHA:
        raise EnvelopeAuditHold("Review-stage actor layout changed; re-audit required")
    src = raw.decode("utf-8")
    for token in (
        'place("CENTRAL_CURVED_QUARTERS_REVIEW",quarters_mesh,(0,0,0))',
        'place("FORWARD_GEODESIC_GLASS_DOME_REVIEW",bridge_mesh,(170,0,133))',
        'place("COUPLED_HABITATION_PIVOT_REVIEW",cube,(40,0,72)',
        '("FORE_PORT",(145,-99,55),(0,-80,-8))',
        '("FORE_STARBOARD",(145,99,55),(0,80,8))',
        'unreal.Rotator(0,17.5,0)',
    ):
        if token not in src:
            raise EnvelopeAuditHold("Native-stage layout token missing: " + token)


def glb_aabb(path: Path, expected_sha: str):
    if not path.is_file() or digest(path) != expected_sha:
        raise EnvelopeAuditHold("Private GLB missing or mismatched: " + path.name)
    data = path.read_bytes()
    if len(data) < 32 or data[:4] != b"glTF" or struct.unpack_from("<I", data, 8)[0] != len(data):
        raise EnvelopeAuditHold("Invalid glTF binary header or length")
    chunk_length = struct.unpack_from("<I", data, 12)[0]
    if data[16:20] != b"JSON" or chunk_length < 2 or 20 + chunk_length > len(data):
        raise EnvelopeAuditHold("Invalid glTF JSON section")
    model = json.loads(data[20:20 + chunk_length])
    if len(model.get("materials", [])) != 3 or len(model.get("meshes", [])) != 1:
        raise EnvelopeAuditHold("Review source material or mesh topology drift")
    bounds = []
    for prim in model["meshes"][0]["primitives"]:
        index = prim.get("attributes", {}).get("POSITION")
        acc = model["accessors"][index]
        mi, ma = acc.get("min"), acc.get("max")
        if not mi or not ma or len(mi) != 3 or len(ma) != 3:
            raise EnvelopeAuditHold("Unbounded POSITION accessor")
        if not all(math.isfinite(v) for v in mi + ma):
            raise EnvelopeAuditHold("Nonfinite glTF mesh geometry")
        if any(lo > hi for lo, hi in zip(mi, ma)):
            raise EnvelopeAuditHold("Invalid glTF min/max")
        bounds.append((mi, ma))
    if not bounds:
        raise EnvelopeAuditHold("No vertices in source model")
    low = tuple(min(a[0][i] for a in bounds) for i in range(3))
    high = tuple(max(a[1][i] for a in bounds) for i in range(3))
    # Conservative imported orientation observed in UE static mesh extents:
    # glTF x, y-up, z-side -> UE x, y-side, z-up. Signed axis/articulated
    # collision results still require native validation.
    return tuple(
        (x * 100, z * 100, y * 100)
        for x, y, z in itertools.product(*zip(low, high))
    )


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def rotate(p, yaw_deg=0.0, roll_deg=0.0):
    x, y, z = p
    t = math.radians(roll_deg)
    y, z = y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t)
    t = math.radians(yaw_deg)
    return (x * math.cos(t) - y * math.sin(t),
            x * math.sin(t) + y * math.cos(t), z)


def aabb(corners):
    return (
        tuple(min(p[i] for p in corners) for i in range(3)),
        tuple(max(p[i] for p in corners) for i in range(3)),
    )


def wing_box(corners, position, yaw, roll):
    return aabb(add(rotate(p, yaw, roll), position) for p in corners)


def habitat_box(corners, position, pivot_yaw):
    return aabb(
        add(rotate(subtract(add(p, position), PIVOT), pivot_yaw), PIVOT)
        for p in corners
    )


def axis_gaps(a, b):
    """Positive separation per world axis. All zero means AABB overlap."""
    result = []
    for i in range(3):
        if a[1][i] < b[0][i]:
            result.append(b[0][i] - a[1][i])
        elif b[1][i] < a[0][i]:
            result.append(a[0][i] - b[1][i])
        else:
            result.append(0.0)
    return result


def boxes_overlap(a, b):
    return all(v <= 0 for v in axis_gaps(a, b))


def calculate(bridge, quarters, wing):
    wing_boxes = {
        name: wing_box(wing, location, yaw, roll)
        for name, (location, yaw, roll) in FORE_WINGS.items()
    }
    poses = {}
    for degree in (-17.5, 0.0, 17.5):
        row = {}
        for name, corners in (("bridge", bridge), ("quarters", quarters)):
            hbox = habitat_box(corners, ORIGINS[name], degree)
            row[name] = {
                wing_name: {
                    "axis_separations_cm": [round(v, 3) for v in axis_gaps(hbox, wbox)],
                    "conservative_aabb_overlap": boxes_overlap(hbox, wbox),
                }
                for wing_name, wbox in wing_boxes.items()
            }
        poses[str(degree)] = row

    # AABB overlap threshold is a REVIEW ALERT, not a collision or a safe angle.
    first_conservative_overlap = {}
    for side, sign in (("FORE_PORT", -1), ("FORE_STARBOARD", 1)):
        first_conservative_overlap[side] = {}
        for name, corners in (("bridge", bridge), ("quarters", quarters)):
            threshold = None
            for n in range(0, 176):  # 0.0 .. 17.5 degrees in 0.1-degree steps
                degree = sign * n * 0.1
                current = habitat_box(corners, ORIGINS[name], degree)
                if boxes_overlap(current, wing_boxes[side]):
                    threshold = round(abs(degree), 1)
                    break
            first_conservative_overlap[side][name] = threshold

    b_rest = habitat_box(bridge, ORIGINS["bridge"], 0)
    q_rest = habitat_box(quarters, ORIGINS["quarters"], 0)
    return {
        "status": "CONSERVATIVE_AABB_OVERLAP_REVIEW_HOLD_NOT_NATIVE_COLLISION_PROOF",
        "basis": "hash-pinned private GLB POSITION bounds + authored review map source transforms",
        "authority": "NONCANONICAL_DISPOSABLE_SKYBOURNE_REVIEW_ONLY",
        "glb_to_ue_axis_assumption": "x,z,y in centimeters; no independent native scene collision result",
        "pivot_yaw_17_5_degrees_is_temporary_not_canon": True,
        "resting_habitation_vertical_ranges_cm": {
            "bridge": [round(b_rest[0][2], 3), round(b_rest[1][2], 3)],
            "quarters": [round(q_rest[0][2], 3), round(q_rest[1][2], 3)],
        },
        "nominal_vertical_bridge_top_over_quarters_shell_top_cm": round(b_rest[1][2] - q_rest[1][2], 3),
        "crew_floor_height_and_occupiable_volume": "UNDEFINED_NOT_MEASURED",
        "fore_wing_envelope_review": poses,
        "first_conservative_aabb_overlap_magnitude_deg_not_a_safe_limit": first_conservative_overlap,
        "full_3d_mesh_collision_or_swept_clearance_verified": False,
        "pressure_envelope_and_docking_seal_verified": False,
        "creator_visual_approval": False,
        "production_gameplay_modified": False,
        "starbourne_player_unlocked": False,
    }


def audit_files(bridge: Path, quarters: Path, wing: Path, map_file: Path):
    verify_stage()
    if not map_file.is_file() or digest(map_file) != REVIEW_MAP_SHA:
        raise EnvelopeAuditHold("Review map absent/drifted; no model inference")
    input_paths = {"bridge": bridge, "quarters": quarters, "wing": wing}
    corners = {k: glb_aabb(p, SOURCES[k]) for k, p in input_paths.items()}
    result = calculate(corners["bridge"], corners["quarters"], corners["wing"])
    result["input_sha256"] = dict(SOURCES)
    result["saved_review_map_sha256_unchanged"] = digest(map_file)
    result["authoring_stage_sha256_lf"] = STAGE_LF_SHA
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bridge-glb", type=Path, required=True)
    p.add_argument("--quarters-glb", type=Path, required=True)
    p.add_argument("--wing-glb", type=Path, required=True)
    p.add_argument("--map-file", type=Path, required=True)
    p.add_argument("--receipt", type=Path,
                   help="Optional NEW report JSON outside checkout and native Content; refuses overwrite")
    args = p.parse_args()
    result = audit_files(args.bridge_glb, args.quarters_glb, args.wing_glb, args.map_file)
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        out = args.receipt.resolve()
        if out.exists() or not out.parent.is_dir():
            raise EnvelopeAuditHold("Refuse overwrite or nonexistent output directory")
        if out.is_relative_to(REPO.resolve()) or out.is_relative_to(args.map_file.resolve().parent):
            raise EnvelopeAuditHold("Refuse receipt inside tracked repo or native asset directory")
        out.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
