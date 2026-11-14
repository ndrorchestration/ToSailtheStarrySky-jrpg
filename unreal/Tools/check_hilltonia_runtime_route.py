#!/usr/bin/env python3
"""Assess real native Hilltonia route logs without granting any approval.

Requires actual Unreal PlayerCharacter WAYPOINT and SAMPLE log lines and
complete dock-town-forest-dock chronology. A successful log inspection is
NOT proof of native build provenance, audiovisual approval, or map release;
verify a separate exact-head native build receipt before citing it.

Examples:
  python unreal/Tools/check_hilltonia_runtime_route.py --log unreal/Saved/Logs/ToSailTheStarrySky.log

This tool is read-only. It does not alter gameplay, a saved map, or evidence.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re

EXPECTED = (
    "DOCK_TOWN_SEAM", "TOWN_MAIN_STREET", "VILLAGE_SQUARE",
    "TOWN_WEST_END", "VILLAGE_SQUARE", "WOODLAND_APPROACH",
    "FOREST_EDGE", "WOODLAND_APPROACH", "VILLAGE_SQUARE",
    "TOWN_MAIN_STREET", "DOCK_TOWN_SEAM"
)
WAYPOINTS = {
    "DOCK_TOWN_SEAM": (-3650., -150., 240.),
    "TOWN_MAIN_STREET": (-5350., -150., 270.),
    "VILLAGE_SQUARE": (-7350., -150., 280.),
    "TOWN_WEST_END": (-9050., -150., 270.),
    "WOODLAND_APPROACH": (-7350., -1450., 260.),
    "FOREST_EDGE": (-7350., -3120., 260.),
}
RECORD = re.compile(
    r"TSTSS_HILLTONIA_ROUTE_(WAYPOINT|SAMPLE) "
    r"map=V5 name=([A-Z_]+) "
    r"time=(-?\d+(?:\.\d+)?) x=(-?\d+(?:\.\d+)?) "
    r"y=(-?\d+(?:\.\d+)?) z=(-?\d+(?:\.\d+)?) "
    r"grounded=([01]) footing=([01])"
)
MAX_SPEED_CM_PER_SECOND = 1000.0
MIN_ELAPSED_SECONDS = 30.0
MIN_HEARTBEAT_SAMPLES = 8


class RouteNotEstablished(ValueError):
    """The supplied log cannot establish an accepted review-route traversal."""


@dataclass(frozen=True)
class Record:
    kind: str
    name: str
    time: float
    x: float
    y: float
    z: float
    grounded: int
    footing: int


def parse(text: str) -> list[Record]:
    records = []
    for line in text.splitlines():
        if "TSTSS_HILLTONIA_ROUTE_" not in line:
            continue
        # A partial, corrupted or wrong-map route record must not simply be
        # ignored while the remaining valid lines make a run appear complete.
        match = RECORD.search(line)
        if (match is None or line.count("TSTSS_HILLTONIA_ROUTE_") != 1
                or line[match.end():].strip()):
            raise RouteNotEstablished("Malformed or unscoped Hilltonia route record")
        kind, name, *fields = match.groups()
        time, x, y, z = map(float, fields[:4])
        grounded, footing = map(int, fields[4:])
        if not all(math.isfinite(n) for n in (time, x, y, z)):
            raise RouteNotEstablished("Nonfinite native route value")
        records.append(Record(kind, name, time, x, y, z, grounded, footing))
    return records


def assess(text: str) -> dict:
    records = parse(text)
    if not records:
        raise RouteNotEstablished("No native Hilltonia player route telemetry found")
    events = [r for r in records if r.kind == "WAYPOINT"]
    samples = [r for r in records if r.kind == "SAMPLE"]
    if tuple(r.name for r in events) != EXPECTED:
        raise RouteNotEstablished(
            "Incomplete or unordered player round trip: "
            + ",".join(r.name for r in events)
        )
    if len(samples) < MIN_HEARTBEAT_SAMPLES:
        raise RouteNotEstablished("Insufficient live player location heartbeats")
    start_time, end_time = records[0].time, records[-1].time
    if end_time - start_time < MIN_ELAPSED_SECONDS:
        raise RouteNotEstablished("Traversal duration too short to substantiate walking")
    fall_recovery = "TSTSS_REVIEW_FALL_RETURN " in text
    fall_denied = "TSTSS_REVIEW_FALL_RETURN_REJECT " in text
    if fall_recovery or fall_denied:
        raise RouteNotEstablished("Fall/recovery event present; route requires separate review")

    # Heartbeats are emitted on a real 2-second world-time cadence. A
    # duplicated timestamp or burst of copied samples cannot prove a walk.
    for previous, current in zip(samples, samples[1:]):
        if current.time - previous.time < 1.0:
            raise RouteNotEstablished("Repeated or too-fast route heartbeat")

    traveled_cm = 0.0
    for index, rec in enumerate(records):
        if rec.grounded != 1 or rec.footing != 1:
            raise RouteNotEstablished(
                f"Unsupported or airborne player sample at record {index}"
            )
        matching = next((
            name for name, (x, y, radius) in WAYPOINTS.items()
            if math.hypot(rec.x - x, rec.y - y) <= radius + 0.15
        ), "UNMARKED")
        if rec.kind == "WAYPOINT":
            if rec.name != matching:
                raise RouteNotEstablished(
                    f"Waypoint {rec.name} outside measured route radius"
                )
        elif rec.name != matching:
            raise RouteNotEstablished("Sample waypoint label disagrees with pawn position")
        if index:
            prev = records[index - 1]
            elapsed = rec.time - prev.time
            distance = math.dist((rec.x, rec.y, rec.z), (prev.x, prev.y, prev.z))
            if elapsed < 0:
                raise RouteNotEstablished("Route timestamps are not increasing")
            if (elapsed == 0 and distance > 1.0) or (
                elapsed > 0 and distance / elapsed > MAX_SPEED_CM_PER_SECOND
            ):
                raise RouteNotEstablished(
                    f"Implausible movement or teleport between records {index-1} and {index}"
                )
            traveled_cm += distance
        # Match the active Unreal pawn's bounded geographic instrumentation:
        # records outside the scene region are not real V5 Hilltonia samples.
        if not (-9650. <= rec.x <= -3400. and -3650. <= rec.y <= 1200.):
            raise RouteNotEstablished("Pawn left bounded Hilltonia review region")

    if traveled_cm < 15000.:
        raise RouteNotEstablished("Too little measured travel for harbor–forest return")
    return {
        "status": "REVIEW_ROUTE_LOG_CONSISTENT_NOT_NATIVE_ATTESTATION",
        "review_map": "FirstWake_PreludeInteraction_V5_VisualReview",
        "waypoint_events": len(events),
        "heartbeat_samples": len(samples),
        "elapsed_seconds": round(end_time - start_time, 2),
        "measured_distance_cm": round(traveled_cm, 1),
        "required_order": list(EXPECTED),
        "all_grounded_and_five_point_supported": True,
        "native_receipt_confirmed": False,
        "source_revision_confirmed": False,
        "creator_visual_approval": False,
        "shipping_or_canon_authorization": False,
    }


def main(argv=None) -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--log", type=Path, required=True)
    options = arg.parse_args(argv)
    try:
        summary = assess(options.log.read_text(encoding="utf-8", errors="replace"))
    except (OSError, RouteNotEstablished) as exc:
        print(json.dumps({
            "status": "HOLD_ROUTE_NOT_ESTABLISHED",
            "reason": str(exc),
            "native_receipt_confirmed": False,
            "creator_visual_approval": False,
        }, indent=2))
        return 2
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
