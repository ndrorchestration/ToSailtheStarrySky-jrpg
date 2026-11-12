#!/usr/bin/env python3
"""Offline, fail-closed validation for First Wake cinematic focus REVIEW data.

This tool never imports Unreal, alters game state, writes maps, or asserts
native gameplay/render success. It is only a source data preflight.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

DEFAULT_PATH = (
    Path(__file__).resolve().parents[1]
    / "DataSource" / "Cinematics" / "FirstWakeFocusProfiles.review.json"
)
SHOT_IDS = {
    "FW01_Dock_Establish", "FW02_Ionia_Conversation",
    "FW03_Engine_Inspection", "FW04_Engine_Awakening",
    "FW05_FirstWake_Liftoff", "FW06_Emergency_Splashdown",
    "FW07_Shore_Exploration", "FW08_Lyra_Introduction",
    "FW09_NightSky_Wonder",
}
STATES = {
    "EXPLORATION", "DIALOGUE", "INSPECT", "REVEAL",
    "ESTABLISH", "ACTION", "AWE",
}
WEATHERS = {
    "Clear", "CoastalMist", "Rain", "Storm", "Snow",
    "Blizzard", "AuroralVeil",
}


def demand(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("HOLD: " + reason)


def validate(data: dict) -> dict:
    demand(isinstance(data, dict), "invalid root")
    demand(data.get("schema") == "tstss.firstwake.dynamic_focus.review.v1",
           "unknown schema")
    demand(data.get("engine") == "Unreal Engine 5.8.4", "engine drift")
    demand(data.get("implementation_status") == "DATA_ONLY_NOT_CONNECTED_TO_RUNTIME",
           "data cannot claim native implementation")
    demand(data.get("use_for_gameplay") is False, "unapproved gameplay activation")
    outputs = data.get("outputs") or {}
    demand(outputs.get("review_root") == "/Game/TSTSS/Review/DynamicFocus_V1",
           "review sandbox path drift")
    for key in ("must_duplicate_existing_level",):
        demand(outputs.get(key) is True, "unsafe review output: " + key)
    for key in ("allow_source_map_overwrite", "allow_save_game_mutation",
                "allow_story_progress_mutation"):
        demand(outputs.get(key) is False, "unsafe write permission: " + key)
    guard = data.get("guardrails") or {}
    for key in ("protect_hud_and_interaction_prompts",
                "protect_traversal_ledge_visibility",
                "protect_enemy_targeting",
                "reduced_motion_disables_rack_focus",
                "never_artificially_unlock_story_states"):
        demand(guard.get(key) is True, "missing protection: " + key)
    demand(guard.get("allow_rapid_autofocus_in_combat") is False,
           "combat focus pumping is disallowed")
    demand(guard.get("forbidden_ship_mode") == "Starbourne",
           "Starbourne must remain gated")
    demand(set(guard.get("excluded_party_members", [])) == {"Reson", "Aepex"},
           "slice party roster gate")
    demand(0 < guard.get("max_gameplay_blur_radius_viewport_percent", -1) <= 0.65,
           "gameplay blur budget exceeded")
    demand(0 < guard.get("max_cinematic_blur_radius_viewport_percent", -1) <= 2.0,
           "cinematic blur budget exceeded")
    demand(set((data.get("weather_policy") or {}).keys()) == WEATHERS,
           "weather modes changed")
    domains = data.get("visual_effect_domains") or {}
    demand(set(domains) == {
        "bokeh", "bloom", "atmospheric_perspective", "diffraction", "parallax"
    }, "optical and atmospheric effects must stay distinct")
    lens = data.get("lens") or {}
    demand(lens.get("filmback_width_mm") == 36
           and lens.get("filmback_height_mm") == 24,
           "unreviewed camera filmback")
    demand(4 <= lens.get("diaphragm_blades", -1) <= 16,
           "unreal diaphragm limits")
    shots = data.get("shots")
    demand(isinstance(shots, list) and len(shots) == len(SHOT_IDS),
           "nine exact review beats required")
    demand({s.get("id") for s in shots if isinstance(s, dict)} == SHOT_IDS,
           "unknown/missing/duplicate beat")
    for shot in shots:
        name = shot["id"]
        demand(shot.get("camera_state") in STATES, name + " invalid state")
        demand(isinstance(shot.get("lens_mm"), (int, float))
               and 14 <= shot["lens_mm"] <= 100,
               name + " lens out of range")
        demand(isinstance(shot.get("f_stop"), (int, float))
               and 1.8 <= shot["f_stop"] <= 16,
               name + " unphysical f-stop")
        demand(shot.get("focus_mode") in {
            "manual", "actor_eye_tracking", "tracked_subject"
        }, name + " unknown focus target")
        demand(isinstance(shot.get("focus_cm"), (int, float))
               and shot["focus_cm"] >= 50, name + " focus distance")
        demand(isinstance(shot.get("rack_focus_seconds"), (int, float))
               and 0 <= shot["rack_focus_seconds"] <= 5,
               name + " focus speed")
        demand(isinstance(shot.get("max_blur_percent"), (int, float))
               and 0 <= shot["max_blur_percent"] <=
               guard["max_cinematic_blur_radius_viewport_percent"],
               name + " blur bounds")
        demand(bool(shot.get("world_drivers")), name + " needs world drivers")
        if shot["camera_state"] in ("EXPLORATION", "ACTION"):
            demand(shot["max_blur_percent"] <=
                   guard["max_gameplay_blur_radius_viewport_percent"],
                   name + " gameplay blur/readability failure")
            demand(shot["rack_focus_seconds"] == 0,
                   name + " cinematic focus pull during traversal/action")
    night = next(s for s in shots if s["id"] == "FW09_NightSky_Wonder")
    demand(night["focus_mode"] == "manual" and night["focus_cm"] >= 100000,
           "night sky must focus near infinity in awe shot")
    splash = next(s for s in shots if s["id"] == "FW06_Emergency_Splashdown")
    demand(splash["f_stop"] >= 5.6,
           "splashdown action horizon must stay legible")
    lyra = next(s for s in shots if s["id"] == "FW08_Lyra_Introduction")
    demand("post-splashdown" in lyra.get("notes", "").lower(),
           "Lyra introduction must follow splashdown")
    qa = data.get("qa") or {}
    for key in ("native_capture_required", "exact_commit_required",
                "compare_dof_on_off", "verify_reduced_motion",
                "verify_ledge_navigation", "creator_approval_required"):
        demand(qa.get(key) is True, "missing native or creator review gate: " + key)
    return {"status": "SOURCE_PROFILE_VALID", "shot_count": len(shots),
            "engine": data["engine"], "runtime_admission": "NOT_ESTABLISHED"}


def self_test(data: dict) -> None:
    cases = []
    def add(name, mutator):
        altered = copy.deepcopy(data)
        mutator(altered)
        cases.append((name, altered))
    add("unsafe map writes", lambda d: d["outputs"].update(
        allow_source_map_overwrite=True))
    add("Starbourne unlock", lambda d: d["guardrails"].update(
        forbidden_ship_mode="Skyborne"))
    add("too much gameplay blur", lambda d: d["shots"][0].update(
        max_blur_percent=3.0))
    add("unreviewed aperture", lambda d: d["shots"][2].update(
        f_stop=0.4))
    add("missing scene", lambda d: d["shots"].pop())
    add("premature Lyra", lambda d: d["shots"][7].update(
        notes="Recruit from the beginning"))
    add("night sky near-focus", lambda d: d["shots"][8].update(
        focus_cm=100))
    add("claim runtime", lambda d: d.update(
        implementation_status="NATIVE_VERIFIED"))
    for name, item in cases:
        try:
            validate(item)
        except ValueError:
            print("PASS negative:", name)
        else:
            raise AssertionError("FAIL OPEN: " + name)
    print("PASS positive and", len(cases), "negative validation cases")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=Path, default=DEFAULT_PATH)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8"))
    print(json.dumps(validate(data), indent=2))
    if args.self_test:
        self_test(data)


if __name__ == "__main__":
    main()
