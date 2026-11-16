"""Fail-closed postflight reader for a *native* opt-in Resonant Pulse log.

Requires a real UE5.8.4 game-world log (PIE or standalone -game). This checks
observable atomic HP/MP behavior and bound key-2 callback order; it DOES NOT certify a physical keypress,
rendered sphere, synchronized sound, exact Git SHA, or creator approval.
Keep original logs/screenshots and SHA custody separately.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ADMITTED = "TSTSS_FOCUS_COMBAT_ADMITTED: two spells; foes=3 multi_probe=1"
BOUND = "TSTSS_FOCUS_INPUT_AND_HUD_BOUND: keys 1 and 2"
KEY_CALLBACK = "TSTSS_FOCUS_PULSE_KEY_CALLBACK: bound key 2 handler invoked"
ACCEPTED = (
    "TSTSS_FOCUS_ACTION_ACCEPTED actor=Ender "
    "skill=Ender_ResonantPulse target=Ender"
)
PATTERN = re.compile(
    r"TSTSS_FOCUS_MULTIFOE_READBACK "
    r"mp_spent=(-?\d+) primary_hp_delta=(-?\d+) "
    r"elevated_hp_delta=(-?\d+) outside_hp_delta=(-?\d+) "
    r"ionia_hp_delta=(-?\d+)(?!\d)"
)
FIELDS = (
    "mp_spent",
    "primary_hp_delta",
    "elevated_hp_delta",
    "outside_hp_delta",
    "ionia_hp_delta",
)


def verify_log(text: str) -> dict[str, int]:
    if text.count(ADMITTED) != 1:
        raise ValueError("Expected exactly one admitted opt-in three-foe arena")
    if text.count(BOUND) != 1:
        raise ValueError("Expected exactly one focus input/HUD binding")
    if text.count(KEY_CALLBACK) != 1:
        raise ValueError("Expected exactly one bound key-2 handler callback")
    if text.count(ACCEPTED) != 1:
        raise ValueError("Expected exactly one Ender Pulse acceptance")
    for bad in (
        "TSTSS_FOCUS_MULTIFOE_READBACK_DENIED",
        "TSTSS_FOCUS_MULTIFOE_READBACK_INCOMPLETE",
    ):
        if bad in text:
            raise ValueError("Incomplete or rejected Pulse readback: " + bad)
    records = list(PATTERN.finditer(text))
    if len(records) != 1 or text.count("TSTSS_FOCUS_MULTIFOE_READBACK ") != 1:
        raise ValueError("Expected exactly one complete atomic Pulse readback")
    record = records[0]
    if text.index(ADMITTED) > text.index(BOUND):
        raise ValueError("Focus binding preceded arena admission")
    if text.index(BOUND) > text.index(KEY_CALLBACK):
        raise ValueError("Key callback preceded input/HUD binding")
    if text.index(KEY_CALLBACK) > text.index(ACCEPTED):
        raise ValueError("Pulse acceptance preceded key callback")
    if record.start() < text.index(ACCEPTED):
        raise ValueError("Readback preceded accepted action")
    result = dict(zip(FIELDS, (int(x) for x in record.groups())))
    if result["mp_spent"] != 3:
        raise ValueError("Pulse must spend exactly 3 MP once")
    for field in ("primary_hp_delta", "elevated_hp_delta"):
        if result[field] <= 0:
            raise ValueError("In-range foe did not take positive HP damage: " + field)
    for field in ("outside_hp_delta", "ionia_hp_delta"):
        if result[field] != 0:
            raise ValueError("Out-of-range enemy or in-range ally was damaged: " + field)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path, help="Exact-head Unreal game-world runtime log file")
    args = p.parse_args()
    try:
        data = verify_log(args.log.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError) as error:
        print("FAIL:", error)
        return 1
    print(json.dumps({
        "readback_contract": "PASS",
        "observed_deltas": data,
        "qualification": (
            "Log contract only; requires independent exact-head custody, "
            "witnessed keyboard gameplay (PIE or standalone), VFX/audio review and creator approval."
        )
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
