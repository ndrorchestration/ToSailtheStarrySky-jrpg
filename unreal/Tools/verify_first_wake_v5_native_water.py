"""Fail-closed validator for earned V5 → ship → sky → sea native water telemetry.

The V5 sea adapter begins existence *after* launch, so unlike the separate V3
single-map DRY/PHYSICS contract, no prelaunch dry sample can be expected here.
This checker never claims production hull flight, cinema or disk persistence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from verify_first_wake_water_frame_trace import parse_samples
from verify_first_wake_postflotation_stability import _connected, _physical_good

E_TARGETS = tuple("TSTSS_PRELUDE_REVIEW_" + name for name in (
    "FlyerDiscovery", "IoniaHiring", "AureateBoarding", "LiftStation",
    "PressureStation", "ReserveStation", "EngineeringApproval",
))
MAPS = tuple("/Game/TSTSS/Review/VerticalSlice/" + name for name in (
    "VS02_AureateInteriors", "VS03_FirstWakeSky",
    "VS04_SplashdownSea", "VS05_DenithFuelShanty",
))
TRACE_CVAR = 'tstss.FirstWake.WaterTrace = "1"'
PHYSICS_LIMIT = 6000


def demand(value: bool, message: str) -> None:
    if not value:
        raise ValueError("HOLD: " + message)


def analyze(raw: str) -> dict:
    demand("PIE: Server logged in" in raw, "no real PIE player login")
    demand(TRACE_CVAR in raw, "water trace CVar not confirmed ON")
    events = re.findall(r"TSTSS_PIE_REVIEW_E_ACCEPT target=(\S+)", raw)
    demand(tuple(events) == E_TARGETS, "seven earned E milestones differ")

    travel = re.findall(
        r"TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=(\S+)",
        raw,
    )
    demand(tuple(travel) == MAPS, "unexpected or skipped V5 K travel")
    positions = [raw.index("TSTSS_PIE_REVIEW_E_ACCEPT target=" + E_TARGETS[-1])]
    for dest in MAPS:
        queued = "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + dest
        loaded = "LogLoad: LoadMap: " + dest
        demand(raw.count(queued) == 1 and raw.count(loaded) == 1,
               "missing or duplicated native K and map load")
        positions.extend([raw.index(queued), raw.index(loaded)])

    samples = parse_samples(raw)
    dry = [s for s in samples if s["phase"] == "DRY"]
    physical = [s for s in samples if s["phase"] == "PHYSICS"]
    demand(not dry, "mixed V3 dry-lab trace in V5 sea-only proof")
    demand(1 <= len(physical) <= PHYSICS_LIMIT, "no bounded sea physics samples")
    demand(physical[0].get("sim") == "1"
           and physical[0].get("beat_before") == "4"
           and physical[0].get("beat_after") == "4"
           and physical[0].get("immersed") == "0"
           and physical[0].get("stable_sec") == "0.0000",
           "V5 first sea frame is not dry launched physics")
    contact = [i for i, s in enumerate(physical)
               if (s.get("beat_before"), s.get("beat_after")) == ("4", "5")]
    flotation = [i for i, s in enumerate(physical)
                 if (s.get("beat_before"), s.get("beat_after")) == ("5", "6")]
    demand(len(contact) == len(flotation) == 1 and
           0 < contact[0] < flotation[0], "exact water contact and flotation boundaries missing")
    entry_i, land_i = contact[0], flotation[0]
    entry, landing = physical[entry_i], physical[land_i]
    generation = landing.get("restore_gen", "")
    demand(generation and entry.get("restore_gen") == generation,
           "contact and flotation belong to different timelines")
    demand(entry.get("tagged_overlap") == entry.get("immersed") ==
           entry.get("sim") == "1", "contact frame lacks real tagged immersion")
    demand(float(entry.get("submersion", "-1")) > 0.01 and
           float(entry.get("hull_bottom_z_cm", "inf")) <
           float(entry.get("water_surface_z_cm", "-inf")),
           "contact frame hull did not penetrate water surface")
    demand(_physical_good(landing, generation) and
           float(landing["stable_sec"]) >= 2.0,
           "flotation frame is not a stable immersed physics sample")

    # Walk backward through actual qualifying 5→5 sampled physics. The FIRST
    # qualifying sample is a time anchor, never credited as a prior dt.
    start = land_i
    prior = landing
    for i in range(land_i - 1, entry_i, -1):
        row = physical[i]
        if ((row.get("beat_before"), row.get("beat_after")) != ("5", "5")
                or not _physical_good(row, generation) or not _connected(row, prior)):
            break
        start = i
        prior = row
    observed_before = float(landing["world_sec"]) - float(physical[start]["world_sec"])
    demand(observed_before >= 2.0, "not two directly observed preflotation seconds")
    pre = physical[start:land_i + 1]
    demand(float(pre[0]["stable_sec"]) <= 0.005,
           "stable preflotation witness omits its zero-timer anchor")
    for older, newer in zip(pre, pre[1:]):
        increment = float(newer["stable_sec"]) - float(older["stable_sec"])
        step = float(newer["dt"])
        demand(abs(increment - step) <= max(0.002, step * 0.15),
               "native stable counter disagrees with frame times")
    demand(float(landing["stable_sec"]) <= observed_before + 0.005,
           "native stable counter overstates actual world time")

    # Independently verify at least two seconds AFTER the granted gate.
    end = land_i
    prior = landing
    for i in range(land_i + 1, len(physical)):
        row = physical[i]
        if ((row.get("beat_before"), row.get("beat_after")) != ("6", "6")
                or not _physical_good(row, generation) or not _connected(prior, row)):
            break
        end = i
        prior = row
    observed_after = float(physical[end]["world_sec"]) - float(landing["world_sec"])
    demand(observed_after >= 2.0, "postflotation stability window incomplete")

    first_physics = raw.index("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS")
    contact_marker = "TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS world_sec=" + entry["world_sec"]
    flotation_marker = "TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS world_sec=" + landing["world_sec"]
    demand(raw.count(contact_marker) == raw.count(flotation_marker) == 1,
           "ambiguous boundary event placement in native log")
    # The physical actor must only begin AFTER the sea-level arrival.
    positions.extend([first_physics, raw.index(contact_marker), raw.index(flotation_marker)])
    # The postflotation K to coastal map is queued only after the water proof.
    end_queue = "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + MAPS[3]
    positions.append(raw.index(end_queue))
    # The ordered route: earned E7, K/load ship, K/load sky,
    # K/load sea, physics begins, contact, flotation, K/load coast.
    expected_order = [
        positions[0], positions[1], positions[2],
        positions[3], positions[4], positions[5], positions[6],
        positions[9], positions[10], positions[11],
        positions[7], positions[8],
    ]
    demand(all(a < b for a, b in zip(expected_order, expected_order[1:])),
           "native level or water chronology out of order")

    return {
        "status": "DIRECT_NATIVE_V5_MULTIMAP_PROXY_FLOATATION_PASS",
        "earned_E_count": len(events),
        "native_level_order": list(MAPS),
        "v5_was_launched_before_adapter_spawn": True,
        "prelaunch_dry_hull_verified_in_same_map": False,
        "direct_native_physics_samples": len(physical),
        "source_restore_generation": generation,
        "contact_entry_world_s": float(entry["world_sec"]),
        "flotation_world_s": float(landing["world_sec"]),
        "stable_seconds_at_transition": float(landing["stable_sec"]),
        "direct_preflotation_stable_s": round(observed_before, 4),
        "direct_postflotation_stable_s": round(observed_after, 4),
        "pre_stable_frame_count": len(pre),
        "post_stable_frame_count": end - land_i + 1,
        "tagged_water_immersion_verified_in_proxy": True,
        "actual_hull_ship_mesh_approved": False,
        "native_player_flight_verified": False,
        "cinematic_visual_approved": False,
        "disk_restart_verified": False,
        "human_keyboard_playthrough": False,
    }


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--map-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.log.is_symlink() or args.map.is_symlink():
        raise ValueError("HOLD immutable receipt exists or untrusted symlink")
    git_head = subprocess.check_output(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True,
    ).strip()
    if git_head != args.head or digest(args.map) != args.map_sha256:
        raise ValueError("HOLD exact source or sea-map custody")
    result = analyze(args.log.read_text(encoding="utf-8", errors="replace"))
    result.update(
        native_source_head=args.head,
        native_sea_map_sha256=args.map_sha256,
        native_log_sha256=digest(args.log),
        verifier_sha256=digest(Path(__file__)),
    )
    with args.out.open("x", encoding="utf-8") as target:
        json.dump(result, target, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
