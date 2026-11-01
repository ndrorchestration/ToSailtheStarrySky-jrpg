#!/usr/bin/env python3
"""Revalidate an existing Aureate Wake review packet without Unreal or writes.

This is a source/asset-integrity gate only; NOT native import, continuous
collision proof, gameplay integration, screenshots, or art acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

TOOLS = Path(__file__).resolve().parent
UNREAL_ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from import_aureate_wing_review import preflight as wing_preflight
from import_aureate_root_support_review import preflight as support_preflight
from audit_aureate_wing_clearance import (
    assert_source_contract, audit, read_vertices,
)
from capture_first_wake_review import capture_plan

SOURCE_PATHS = (
    "unreal/Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp",
    "unreal/Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h",
    "unreal/Tools/audit_aureate_wing_clearance.py",
    "unreal/Tools/import_aureate_wing_review.py",
    "unreal/Tools/import_aureate_root_support_review.py",
    "unreal/Tools/capture_first_wake_review.py",
    "unreal/Tools/build_first_wake_benchmark.py",
    "unreal/Tools/author_aureate_wing_glb.py",
    "unreal/Tools/author_aureate_root_support.py",
)
STAGE_AUTHORITY = "PREPARED_SOURCE_SCREEN_PASS_NOT_NATIVE_VERIFIED"
REVIEW_ASSET_STATUS = "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"


class PacketHold(ValueError):
    pass


def packet_file(packet: Path, relative: str) -> Path:
    """Allow existing ordinary files only, never a symlink escaping the packet."""
    root = packet.resolve(strict=True)
    item = root / relative
    real = item.resolve(strict=True)
    if not real.is_relative_to(root) or not real.is_file():
        raise PacketHold("Invalid or escaping packet file: " + relative)
    return real


def source_state(unreal_root: Path, baseline: str) -> dict:
    """Prove that reviewed ship pose/capture source still matches packet baseline."""
    if not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise PacketHold("Packet source_head.txt must be an exact 40-character commit SHA")
    repo = unreal_root.resolve() .parent

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo), *args], text=True,
            capture_output=True, check=False, timeout=15,
        )

    head = git("rev-parse", "HEAD")
    if head.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()):
        raise PacketHold("Cannot identify current source HEAD")
    if git("cat-file", "-e", baseline + "^{commit}").returncode != 0:
        raise PacketHold("Packet's pinned source commit is unavailable")
    if git("merge-base", "--is-ancestor", baseline, "HEAD").returncode != 0:
        raise PacketHold("Packet source is not an ancestor of current source")
    if git("diff", "--quiet", baseline, "HEAD", "--", *SOURCE_PATHS).returncode != 0:
        raise PacketHold("Ship pose, generator, or camera source diverged from packet")
    if git("diff", "--quiet", "HEAD", "--", *SOURCE_PATHS).returncode != 0:
        raise PacketHold("Uncommitted changes affect reviewed ship/camera source")
    return {"packet_source_sha": baseline, "current_source_sha": head.stdout.strip(),
            "reviewed_source_unchanged": True}


def read_clearance_receipt(path: Path) -> dict:
    # Windows PowerShell 5.1 Out-File produces UTF-16LE JSON by default.
    # Accept only UTF-8 and BOM-identified UTF-16LE without rewriting custody.
    data = path.read_bytes()
    if len(data) > 20000:
        raise PacketHold("Clearance receipt is unexpectedly large")
    if data.startswith(b"\xff\xfe"):
        text = data.decode("utf-16")
    elif data.startswith(b"\xfe\xff"):
        raise PacketHold("Unexpected UTF-16 big-endian clearance receipt")
    else:
        text = data.decode("utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise PacketHold("Clearance receipt must be a JSON object")
    return value


def check_recomputed_clearance(saved: dict, computed: dict) -> None:
    if not isinstance(saved, dict) or saved != computed:
        raise PacketHold("Saved clearance receipt differs from fresh 900-point-budget/20-step calculation")
    if (computed["checked_directed_transitions"], computed["checked_poses"],
        computed["wing_instances"], computed["mesh_sample_points"]) != (6, 126, 4, 1240):
        raise PacketHold("Ordinary-form pose/sample inventory deviated from prepared packet")
    if computed["minimum_proxy_aabb_clearance_cm"] < 10:
        raise PacketHold("Static sampled proxy clearance below the conservative threshold")
    if computed["minimum_interwing_aabb_clearance_cm"] < 10:
        raise PacketHold("Sampled wing-pair clearance below the conservative threshold")


def validate_camera_plan(plan: dict) -> None:
    shots = plan.get("shots", [])
    if (plan.get("resolution") != [1920, 1080] or
        len(shots) != 4 or len({s["filename"] for s in shots}) != 4 or
        [s["sequence"] for s in shots] != [1, 2, 3, 4] or
        [s["story_stage"] for s in shots] != ["Prelude"] * 3 + ["Chapter 1 Act 1"] or
        plan.get("native_render_verified") is not False or
        plan.get("approved_art") is not False):
        raise PacketHold("Camera plan is not the four-shot, unapproved review contract")


def verify_packet(packet: Path, unreal_root: Path = UNREAL_ROOT) -> dict:
    packet = packet.resolve(strict=True)
    base = packet_file(packet, "source_head.txt").read_text(encoding="ascii").strip()
    provenance = source_state(unreal_root, base)

    wing = packet_file(packet, "wing/AureateWake_Wing_Lookdev.glb")
    wing_manifest = packet_file(packet, "wing/AureateWake_Wing_Manifest.json")
    texture = packet_file(packet, "wing/AureateWake_Wing_Albedo.png")
    support = packet_file(packet, "support/AureateWake_RootSupport_Lookdev.glb")
    support_manifest = packet_file(packet, "support/AureateWake_RootSupport_Manifest.json")
    saved_receipt = packet_file(packet, "wing_clearance.json")

    wing_info = wing_preflight(wing, wing_manifest)
    support_info = support_preflight(support, support_manifest)
    meta = json.loads(wing_manifest.read_text(encoding="utf-8"))
    support_meta = json.loads(support_manifest.read_text(encoding="utf-8"))
    if (meta.get("status") != REVIEW_ASSET_STATUS or
        support_meta.get("status") != REVIEW_ASSET_STATUS or
        meta.get("sha256", {}).get(texture.name) != hashlib.sha256(texture.read_bytes()).hexdigest()):
        raise PacketHold("Wing texture hash or noncanonical asset provenance disagrees")
    if not texture.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise PacketHold("Expected a PNG albedo texture")
    if wing_info["membrane_span_cm"] != 280 or support_info["strut_length_cm"] != 100:
        raise PacketHold("Wing/support measurements unexpectedly changed")

    cpp = (unreal_root / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp")
    header = (unreal_root / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h")
    assert_source_contract(cpp.read_text(encoding="utf-8"), header.read_text(encoding="utf-8"))
    vertices, primitive_counts = read_vertices(wing, per_primitive=900)
    computed = audit(vertices, steps=20)
    computed["source_primitive_vertex_counts"] = primitive_counts
    saved = read_clearance_receipt(saved_receipt)
    check_recomputed_clearance(saved, computed)
    plan = capture_plan("ShipReview20261101")
    validate_camera_plan(plan)
    return {
        "status": STAGE_AUTHORITY,
        "provenance": provenance,
        "wing_sha256": wing_info["sha256"],
        "support_sha256": support_info["sha256"],
        "wing_span_cm": wing_info["membrane_span_cm"],
        "support_length_cm": support_info["strut_length_cm"],
        "clearance": computed,
        "camera_count": 4,
        "camera_resolution": [1920, 1080],
        "orbiter_authorized": False,
        "native_import_verified": False,
        "native_capture_verified": False,
        "continuous_collision_verified": False,
        "creator_visual_approval": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True,
                        help="Existing Saved/ReviewPreparation_* directory (never modified)")
    args = parser.parse_args()
    try:
        print(json.dumps(verify_packet(args.packet), indent=2, sort_keys=True))
        return 0
    except (PacketHold, OSError, ValueError, KeyError, IndexError,
            subprocess.SubprocessError) as exc:
        print("REVIEW PACKET HOLD: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
