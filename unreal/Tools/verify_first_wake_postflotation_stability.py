"""Bounded independent witness of observed post-flotation physical stability.

Does NOT convert pre-transition 1.9943s into 2s; PRE-transition strict
proof remains a separate HOLD. This checks 2+ real observed world seconds
AFTER native FlotationConfirmed with continuous tagged immersion and
subthreshold physical velocity. Pure read-only verification, never physics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

from verify_first_wake_water_frame_trace import parse_samples

EXPECTED = [
    "TSTSS_PRELUDE_REVIEW_" + n for n in (
        "FlyerDiscovery", "IoniaHiring", "AureateBoarding", "LiftStation",
        "PressureStation", "ReserveStation", "EngineeringApproval")
] + [
    "TSTSS_SPLASHDOWN_GREYBOX_" + n for n in
    ("LaunchMarker", "EmptyReserveMarker", "ReturnBerthMarker")
]
NUMERIC = (
    "world_sec", "dt", "hull_z_cm", "hull_bottom_z_cm",
    "water_surface_z_cm", "submersion", "vertical_speed_cm_s",
    "stable_sec",
)
REQUIRED = NUMERIC + (
    "tagged_overlap", "immersed", "sim", "restore_gen",
    "beat_before", "beat_after"
)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def head_of(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True).strip()

def _physical_good(row: dict, generation: str) -> bool:
    if not all(field in row for field in REQUIRED):
        raise ValueError("incomplete native physics sample")
    for field in NUMERIC:
        try:
            value = float(row[field])
        except ValueError as exc:
            raise ValueError("nonnumeric native physics sample " + field) from exc
        if not math.isfinite(value):
            raise ValueError("nonfinite native physics sample " + field)
    return (
        row["sim"] == "1"
        and row["tagged_overlap"] == "1"
        and row["immersed"] == "1"
        and row["restore_gen"] == generation
        and float(row["submersion"]) > 0.01
        and float(row["hull_bottom_z_cm"]) < float(row["water_surface_z_cm"])
        and abs(float(row["vertical_speed_cm_s"])) <= 25.0
        and 0.0 < float(row["dt"]) <= 0.25
    )

def _connected(older: dict, newer: dict) -> bool:
    gap = float(newer["world_sec"]) - float(older["world_sec"])
    return (
        0.0 < gap <= 0.25
        and abs(gap - float(newer["dt"])) <= 0.0002
    )

def analyze(text: str) -> dict:
    if "PIE: Server logged in" not in text:
        raise ValueError("missing actual Unreal PIE player login")
    if 'tstss.FirstWake.WaterTrace = "1"' not in text:
        raise ValueError("review-only native telemetry CVar not confirmed ON")
    events = re.findall(r"TSTSS_PIE_REVIEW_E_ACCEPT target=(\S+)", text)
    if events != EXPECTED:
        raise ValueError("ten ordered genuine native story interactions missing")
    samples = parse_samples(text)
    physical = [x for x in samples if x.get("phase") == "PHYSICS"]
    if not physical or len(physical) > 6000:
        raise ValueError("bounded native physical frames missing")
    first_physical = next(i for i, x in enumerate(samples)
                          if x["phase"] == "PHYSICS")
    prelaunch = samples[:first_physical]
    if not any(x.get("phase") == "DRY" and x.get("sim") == "0"
               and float(x.get("stable_sec", "-1")) == 0
               for x in prelaunch):
        raise ValueError("genuine prelaunch dry frame missing")
    if len([x for x in samples if x.get("phase") == "DRY"]) > 30:
        raise ValueError("dry sample cap exceeded")
    transitions = [
        i for i, x in enumerate(physical)
        if x.get("beat_before") == "5" and x.get("beat_after") == "6"
    ]
    if len(transitions) != 1:
        raise ValueError("exactly one native flotation boundary required")
    i = transitions[0]
    landing = physical[i]
    if float(landing.get("stable_sec", "0")) < 2.0:
        raise ValueError("original game gate did not report 2-second stability")
    generation = landing.get("restore_gen", "")
    if not _physical_good(landing, generation):
        raise ValueError("native transition row is not physically qualifying")

    # Explicit, separate pre-transition strict check: no delta-time
    # credited before the first fully qualifying sampled endpoint.
    prior = landing
    start_index = i
    for j in range(i - 1, -1, -1):
        row = physical[j]
        if not _physical_good(row, generation) or not _connected(row, prior):
            break
        start_index = j
        prior = row
    before_seconds = (
        float(landing["world_sec"]) - float(physical[start_index]["world_sec"])
    )

    # Direct AFTER-boundary witness: the first fully qualifying endpoint
    # is the native transition row; do not credit the earlier unobserved
    # fraction of the preceding frame. Each later endpoint must have
    # actually been sampled; gaps or invalid data fail closed.
    start = float(landing["world_sec"])
    last = landing
    count = 1
    for row in physical[i + 1:]:
        if not _physical_good(row, generation) or not _connected(last, row):
            break
        last = row
        count += 1
    duration = float(last["world_sec"]) - start
    if duration < 2.0:
        raise ValueError("no continuous observed 2-second postflotation window")

    return {
        "status": "DIRECT_NATIVE_POST_FLOTATION_TWO_SECONDS_PASS",
        "claim_scope": "observed post-transition real hull-water stability only",
        "pre_transition_exact_2s_status":
            "PASS" if before_seconds >= 2.0 else "HOLD_BELOW_TWO_SECONDS",
        "pre_transition_directly_observed_seconds": round(before_seconds, 4),
        "native_gate_reported_stable_seconds": float(landing["stable_sec"]),
        "landing_transition_world_seconds": start,
        "post_transition_continuous_seconds": round(duration, 4),
        "post_transition_contiguous_frames": count,
        "post_transition_last_world_seconds": float(last["world_sec"]),
        "dry_samples": len([x for x in samples if x.get("phase") == "DRY"]),
        "physical_samples": len(physical),
        "accepted_story_markers": events,
        "real_ue_pie_login": True,
        "water_tracing_cvar_enabled": True,
        "tagged_immersion_and_25cm_s_velocity_satisfied": True,
        "same_restore_generation": generation,
        "valid_world_clock_delta_continuity": True,
        "authorizes_player_ship_flight": False,
        "authorizes_cinematic_landing": False,
        "proves_disk_restart": False,
        "protected_main_merged": False,
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--capture-checkout", type=Path, required=True)
    p.add_argument("--capture-head", required=True)
    p.add_argument("--map", type=Path, required=True)
    p.add_argument("--map-sha256", required=True)
    p.add_argument("--validator-checkout", type=Path, required=True)
    p.add_argument("--validator-head", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError("refuse to overwrite evidence")
    if head_of(a.capture_checkout) != a.capture_head:
        raise ValueError("native capture-source SHA mismatch")
    if head_of(a.validator_checkout) != a.validator_head:
        raise ValueError("independent validation-source SHA mismatch")
    if digest(a.map) != a.map_sha256:
        raise ValueError("native map SHA mismatch")
    if a.map.is_symlink() or a.log.is_symlink():
        raise ValueError("symlinked map/log not permitted")
    result = analyze(a.log.read_text(encoding="utf-8", errors="replace"))
    result.update({
        "native_capture_source_head": a.capture_head,
        "independent_validator_source_head": a.validator_head,
        "native_map_sha256": a.map_sha256,
        "native_log_sha256": digest(a.log),
        "source_provenance": "CVAR_ENABLED_UNREAL_5_8_4_D3D11_NATIVE_PIE",
    })
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("x", encoding="utf-8") as file:
        json.dump(result, file, indent=2, sort_keys=True)
    print(result["status"], str(a.out))

if __name__ == "__main__":
    main()
