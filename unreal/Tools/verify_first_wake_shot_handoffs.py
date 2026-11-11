"""Read-only shot-to-story source reconciliation for the First Wake review candidate.

No native Unreal, Sequencer, visual capture or approval is implied by PASS.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_FILE = ROOT / "DataSource/Cinematics/FirstWakeRuntimeShotHandoffs.review.json"
SHOTS_FILE = ROOT / "DataSource/Cinematics/FirstWakeShotPlan.review.json"
STATE_HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSFirstWakeState.h"
STATE_IMPL = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp"
WATER_IMPL = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSWaterLandingGate.cpp"

EXPECTED_BEATS = (
    "FlyerDiscovered", "IoniaHired", "BoardedAureateWake",
    "EngineeringChecked", "Launched", "SeaContact",
    "FlotationConfirmed", "EmptyReserveInspected", "ReturnedToBerth",
)
# Shot prerequisites are conservative source-review ranges, not automatic story
# transitions or an authorization for Sequencer to change the First Wake state.
EXPECTED_CUES = (
    ("PRE_START", "FlyerDiscovered", "player_interaction", 0, False),
    ("IoniaHired", "BoardedAureateWake", "engineering_interaction", 0, False),
    ("BoardedAureateWake", "EngineeringChecked", "captain_signoff", 7, False),
    ("EngineeringChecked", "Launched", "player_authorized_launch", 7, False),
    ("Launched", "Launched", "cinematic_review_only", 7, False),
    ("Launched", "Launched", "cinematic_review_only", 7, False),
    ("Launched", "Launched", "cinematic_review_only", 7, False),
    ("Launched", "SeaContact", "native_water_gate", 7, True),
    ("SeaContact", "FlotationConfirmed", "native_water_gate", 7, True),
    ("FlotationConfirmed", "EmptyReserveInspected", "post_splashdown_interaction", 7, False),
)


def load_inputs():
    return (
        json.loads(BRIDGE_FILE.read_text(encoding="utf-8")),
        json.loads(SHOTS_FILE.read_text(encoding="utf-8")),
        STATE_HEADER.read_text(encoding="utf-8"),
        STATE_IMPL.read_text(encoding="utf-8"),
        WATER_IMPL.read_text(encoding="utf-8"),
    )


def validate_bridge(bridge, plan, header, story_cpp, water_cpp):
    errors = []
    if bridge.get("schema") != "tstss.firstwake.runtime-shot-handoff.v0.1":
        errors.append("unknown handoff schema")
    if bridge.get("source_plan") != SHOTS_FILE.name or bridge.get("engine") != "Unreal Engine 5.8.4":
        errors.append("source/engine provenance mismatch")
    if bridge.get("status") != "SOURCE_CANDIDATE_NOT_RUNTIME":
        errors.append("unsupported implementation promotion")
    if any(bridge.get(k) is not False for k in (
        "runtime_emits_shot_cues", "native_pie_verified",
        "native_lit_verified", "creator_accepted",
    )):
        errors.append("unearned runtime, visual or creator approval")

    enum = re.search(
        r"enum\s+class\s+ETSTSSFirstWakeBeat\s*:\s*uint8\s*\{([^}]+)\}",
        header, flags=re.S,
    )
    parsed = tuple(re.findall(r"^\s*([A-Za-z]\w*)\s*(?:,|$)",
                              enum.group(1), re.M)) if enum else ()
    if parsed != EXPECTED_BEATS:
        errors.append("runtime story enum changed or reordered")
    if "ETSTSSFirstWakeBeat::FlotationConfirmed" not in header or (
        "AdvanceWaterBeat" not in header
    ):
        errors.append("Prelude/Chapter boundary or water authority missing")
    for marker in (
        "RequestedBeat == ETSTSSFirstWakeBeat::SeaContact",
        "RequestedBeat == ETSTSSFirstWakeBeat::FlotationConfirmed",
        "CurrentBeat == ETSTSSFirstWakeBeat::Launched",
        "CurrentBeat == ETSTSSFirstWakeBeat::SeaContact",
    ):
        if marker not in story_cpp:
            errors.append("runtime authority marker missing: " + marker)
    for marker in (
        "Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::SeaContact)",
        "Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::FlotationConfirmed)",
        "if (StableContactSeconds < 2.f) return false;",
        "bHasPreviousStableSample", "ObservedRestoreGeneration != RestoreGeneration",
    ):
        if marker not in water_cpp:
            errors.append("physical water witness marker missing: " + marker)

    gate = bridge.get("water_gate", {})
    if not isinstance(gate, dict) or (
        gate.get("source_class") != "UTSTSSWaterLandingGate"
        or gate.get("source_method") != "Observe"
        or gate.get("transition_beat") != "FlotationConfirmed"
        or gate.get("min_continuous_pretransition_world_seconds") != 2
        or gate.get("trace_required") is not True
    ):
        errors.append("strict two-second native water evidence contract missing")

    mappings = bridge.get("mappings", [])
    shots = plan.get("shots", [])
    if not isinstance(mappings, list) or not isinstance(shots, list) or (
        len(mappings) != len(shots) or len(mappings) != 10
    ):
        return errors + ["ten-shot runtime handoff count mismatch"]

    for i, (mapping, shot, expected) in enumerate(
        zip(mappings, shots, EXPECTED_CUES), start=1
    ):
        if not isinstance(mapping, dict) or not isinstance(shot, dict):
            errors.append(f"shot {i}: invalid shot/handoff object")
            continue
        shot_id = f"FW-CIN-{i:02d}"
        if mapping.get("shot_id") != shot_id or shot.get("id") != shot_id or (
            mapping.get("beat") != shot.get("beat")
        ):
            errors.append(f"shot {i}: shot ID or narrative handoff drift")
        got = tuple(mapping.get(k) for k in (
            "earliest_state", "latest_state", "trigger",
            "inspection_mask", "water_witness",
        ))
        if got != expected:
            errors.append(f"{shot_id}: runtime state/cue boundary drift")
        if any(mapping.get(k) is not False for k in (
            "auto_advance_story", "creator_accepted"
        )):
            errors.append(f"{shot_id}: cinematic plan cannot authorize progression or acceptance")
        if mapping.get("needs_native_render") is not True or mapping.get("evidence") != []:
            errors.append(f"{shot_id}: no native render evidence established")
        if mapping.get("water_witness") and mapping.get("trigger") != "native_water_gate":
            errors.append(f"{shot_id}: water progression cannot be synthetic")
        if mapping.get("earliest_state") == "PRE_START" and i != 1:
            errors.append(f"{shot_id}: only harbor shot may precede story start")
        if i < 10 and any(actor in shot.get("subjects", []) for actor in ("Lyra", "Talen")):
            errors.append(f"{shot_id}: early Lyra/Talen appearance")
    if shots[8].get("min_continuous_pretransition_world_seconds") != 2:
        errors.append("shot 9 must require exactly two witnessed seconds")
    if "Starbourne" not in bridge.get("story_policy", ""):
        # Story policy must explicitly prohibit early Starbourne unlock.
        errors.append("Starbourne restriction not represented in source handoff")
    return errors


if __name__ == "__main__":
    failures = validate_bridge(*load_inputs())
    for f in failures:
        print("HOLD: " + f, file=sys.stderr)
    print("PASS: source-checked cinematic/story/water handoffs (NO UE/PIE/render)" if not failures
          else "FAIL: shot handoff source contract")
    sys.exit(bool(failures))
