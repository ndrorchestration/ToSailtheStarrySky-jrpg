"""Source-only acceptance checks for the First Wake cinematic shot manifest.

No rendering or native Unreal claims are made by this validator.
"""
from __future__ import annotations

import json
from pathlib import Path

BEATS = (
    "harbor_flyer", "engine_diagnosis", "ionia_commands", "launch",
    "sky_ascent", "phase_drift", "emergency_descent", "sea_contact",
    "stable_flotation", "shoreline_aftermath",
)
DEFAULT_PATH = Path(__file__).resolve().parents[1] / "DataSource" / "Cinematics" / "FirstWakeShotPlan.review.json"


def validate_plan(plan: dict) -> list[str]:
    errors: list[str] = []
    if plan.get("schema") != "tstss.firstwake.cinematic-shots.v0.1":
        errors.append("unknown schema")
    if plan.get("review_status") != "SOURCE_CANDIDATE" or plan.get("approval_status") != "CREATOR_PENDING":
        errors.append("source plan cannot claim production/creator acceptance")
    if plan.get("proposed_art_direction") is not True:
        errors.append("proposed direction must not be mistaken for canon")
    shots = plan.get("shots", [])
    if not isinstance(shots, list) or [s.get("beat") for s in shots if isinstance(s, dict)] != list(BEATS):
        errors.append("missing, extra, duplicated or reordered story beats")
        return errors
    if [s.get("id") for s in shots] != [f"FW-CIN-{n:02d}" for n in range(1, len(BEATS) + 1)]:
        errors.append("unstable/duplicated shot IDs")
    for shot in shots:
        sid = shot["id"]
        actors = set(shot.get("subjects", []))
        if not 18 <= shot.get("lens_mm", 0) <= 100:
            errors.append(f"{sid}: invalid proposed focal length")
        if not isinstance(shot.get("location"), str) or len(shot["location"].strip()) < 3:
            errors.append(f"{sid}: missing location")
        for field in ("composition", "movement", "lighting", "vfx", "interaction_handoff"):
            if not isinstance(shot.get(field), str) or len(shot[field].strip()) < 12:
                errors.append(f"{sid}: missing {field} direction")
        if shot.get("requires_native_capture") is not True:
            errors.append(f"{sid}: native capture gate required")
        if shot.get("final_art_verified") or shot.get("creator_accepted") or shot.get("evidence"):
            errors.append(f"{sid}: unearned art acceptance/evidence")
        if actors.intersection({"Reson", "Aepex"}):
            errors.append(f"{sid}: late-party appearance in Prelude")
        if shot["beat"] != "shoreline_aftermath" and actors.intersection({"Lyra", "Talen"}):
            errors.append(f"{sid}: Lyra/Talen appeared before Splashdown")
        if "Talen" in shot.get("playable_subjects", []):
            errors.append(f"{sid}: Talen must never be playable")
        if shot["beat"] == "stable_flotation" and shot.get("min_continuous_pretransition_world_seconds", 0) < 2.0:
            errors.append(f"{sid}: insufficient directly witnessed flotation window")
    if "native" not in str(plan.get("evidence_policy", "")).lower():
        errors.append("native evidence provenance absent")
    return errors


def load_plan(path: Path = DEFAULT_PATH) -> dict:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


if __name__ == "__main__":
    import sys
    failures = validate_plan(load_plan())
    for error in failures:
        print(error, file=sys.stderr)
    print("First Wake cinematic source contract PASS" if not failures else "FAIL")
    sys.exit(bool(failures))
