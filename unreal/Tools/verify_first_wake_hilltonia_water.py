"""Creator-route First Wake sea-proxy log contract, adapted from PR #849.

Log parsing does not independently authenticate the UE runtime, Aureate hull
buoyancy, cinematic footage, or gameplay. Legacy 7E harbor route is rejected.
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

FLYER_READ = "TSTSS_HILLTONIA_FLYER_READ"
FLYER_ACCEPT = "TSTSS_HILLTONIA_FLYER_ACCEPT"
E_TARGETS = (
    "TSTSS_PRELUDE_REVIEW_IoniaHiring",
    "TSTSS_PRELUDE_REVIEW_AureateBoarding",
    "TSTSS_ENGINEROOM_REVIEW_LiftStation",
    "TSTSS_ENGINEROOM_REVIEW_PressureStation",
    "TSTSS_ENGINEROOM_REVIEW_ReserveStation",
    "TSTSS_ENGINEROOM_REVIEW_EngineeringApproval",
)
MAPS = tuple("/Game/TSTSS/Review/VerticalSlice/" + name for name in (
    "VS02_AureateInteriors", "VS03_FirstWakeSky", "VS04_SplashdownSea",
))
TRACE_CVAR = 'tstss.FirstWake.WaterTrace = "1"'
PHYSICS_LIMIT = 6000

def demand(value: bool, message: str) -> None:
    if not value:
        raise ValueError("HOLD: " + message)

def analyze(raw: str) -> dict:
    demand("PIE: Server logged in" in raw, "no native-style PIE login marker")
    demand(TRACE_CVAR in raw, "water trace CVar not confirmed ON")
    demand(raw.count(FLYER_READ) == 1 and raw.count(FLYER_ACCEPT) == 1,
           "read and explicit accept must both be logged once")
    events = re.findall(r"TSTSS_PIE_REVIEW_E_ACCEPT target=(\S+)", raw)
    demand(tuple(events) == E_TARGETS,
           "new route requires Ionia/ship E, then four shipboard E markers")
    travel = re.findall(
        r"TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=(\S+)",
        raw)
    demand(tuple(travel) == MAPS,
           "legacy coastal shanty or wrong/skipped journey gate")
    demand("TSTSS_LYRA_RECRUITED" not in raw,
           "premature Lyra recruitment in first-flight sea proof")
    for dest in MAPS:
        demand(raw.count("TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + dest) == 1
               and raw.count("LogLoad: LoadMap: " + dest) == 1,
               "missing or duplicated ordered load")

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
    contact_marker = ("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS world_sec="
                      + entry["world_sec"])
    flotation_marker = ("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS world_sec="
                        + landing["world_sec"])
    demand(raw.count(contact_marker) == raw.count(flotation_marker) == 1,
           "ambiguous water boundary telemetry")
    order = [
        FLYER_READ, FLYER_ACCEPT,
        *["TSTSS_PIE_REVIEW_E_ACCEPT target=" + x for x in E_TARGETS[:2]],
        "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + MAPS[0],
        "LogLoad: LoadMap: " + MAPS[0],
        *["TSTSS_PIE_REVIEW_E_ACCEPT target=" + x for x in E_TARGETS[2:]],
        "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + MAPS[1],
        "LogLoad: LoadMap: " + MAPS[1],
        "TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=" + MAPS[2],
        "LogLoad: LoadMap: " + MAPS[2],
        "TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS",
        contact_marker, flotation_marker,
    ]
    indices = [raw.index(x) for x in order]
    demand(all(a < b for a,b in zip(indices, indices[1:])),
           "player/boarding/engineering/launch/water chronology violation")
    return {
        "status":"HILLTONIA_LOG_CONTRACT_PASS_NATIVE_NOT_AUTHENTICATED",
        "source_verifier_provenance":"PR849_PHYSICS_ONLY",
        "flyer_read_explicitly_accepted":True,
        "shipboard_signoff_in_order":True,
        "earned_E_count":len(events),
        "review_map_order":list(MAPS),
        "direct_log_physics_samples":len(physical),
        "source_restore_generation":generation,
        "contact_world_s":float(entry["world_sec"]),
        "flotation_world_s":float(landing["world_sec"]),
        "direct_preflotation_stable_s":round(observed_before,4),
        "direct_postflotation_stable_s":round(observed_after,4),
        "tagged_water_immersion_in_log":True,
        "actual_hull_ship_mesh_approved":False,
        "native_player_flight_verified":False,
        "cinematic_visual_approved":False,
        "disk_restart_verified":False,
        "human_keyboard_playthrough":False,
        "lyra_recruitment_verified":False,
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
        review_source_head=args.head,
        review_sea_map_sha256=args.map_sha256,
        review_log_sha256=digest(args.log),
        verifier_sha256=digest(Path(__file__)),
    )
    with args.out.open("x", encoding="utf-8") as target:
        json.dump(result, target, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
