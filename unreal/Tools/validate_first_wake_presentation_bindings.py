#!/usr/bin/env python3
"""Fail-closed, source-only reconciliation of First Wake cinematic bindings.

Deliberately NOT an Unreal runtime director, PPV controller, audio-event binder,
SaveGame adapter or gameplay authority. No dependencies on separate draft PRs.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from validate_first_wake_focus_profiles import validate as validate_focus

PROJECT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT / "DataSource/Cinematics/FirstWakePresentationBindings.review.json"
FOCUS = PROJECT / "DataSource/Cinematics/FirstWakeFocusProfiles.review.json"
MAPS = {
    "VS01_DenithHarbor", "VS02_AureateInteriors",
    "VS03_FirstWakeSky", "VS04_SplashdownSea",
    "VS05_DenithFuelShanty", "VS06_SplashdownShore",
}
LOOKS = {
    "harbor_day", "harbor_dusk", "harbor_night_review", "engineering",
    "bridge", "ascent", "auroral_twilight", "phase_drift",
    "storm_descent", "sea_contact", "shore_aftermath",
}
WEATHERS = {
    "Clear", "CoastalMist", "Rain", "Storm", "Snow",
    "Blizzard", "AuroralVeil",
}
PRIORITIES = [
    "ACCESSIBILITY_AND_SAFE_READABILITY",
    "ACTIVE_GAMEPLAY_NAVIGATION_COMBAT_INTERACTION",
    "VERIFIED_STORY_AUTHORED_CINEMATIC",
    "WORLD_ENVIRONMENT_AND_SPATIAL_DEPTH",
    "OPTIONAL_AESTHETIC_LOOKDEV",
]


def require(condition: bool, why: str):
    if not condition:
        raise ValueError("HOLD: " + why)


def verify(data: dict, focus: dict) -> dict:
    require(isinstance(data, dict), "root must be JSON object")
    validate_focus(focus)
    require(data.get("schema") == "tstss.firstwake.presentation.bindings.review.v1",
            "unknown integration schema")
    require(data.get("status") == "SOURCE_CONTRACT_ONLY_NOT_RUNTIME_CONNECTED",
            "no runtime integration is established")
    require(data.get("engine") == "Unreal Engine 5.8.4", "engine drift")
    require(data.get("expected_focus_profile") ==
            "unreal/DataSource/Cinematics/FirstWakeFocusProfiles.review.json",
            "wrong focus authority")
    refs = data.get("external_dependencies") or {}
    for name, number in (("lighting_look_library", 796),
                         ("world_weather_source", 798),
                         ("focus_profile_source", 815),
                         ("playable_convergence", 813),
                         ("route_traversal", 814),
                         ("audio", 804)):
        require((refs.get(name) or {}).get("pr") == number,
                "missing/incorrect dependency " + name)
    require(refs["lighting_look_library"].get("status") ==
            "SEPARATE_UNMERGED_REVIEW_SOURCE", "lighting unexpectedly promoted")
    require(refs["world_weather_source"].get("status") ==
            "SEPARATE_UNMERGED_REVIEW_SOURCE", "weather unexpectedly promoted")
    require(refs["audio"].get("status") ==
            "UNVERIFIED_RUNTIME_BINDING_NO_EVENT_ASSERTED", "audio claims unproven")
    require(set(data.get("valid_lighting_look_ids", [])) == LOOKS and
            len(data["valid_lighting_look_ids"]) == len(LOOKS),
            "lighting presets drift from pinned #796")
    require(set(data.get("maps", [])) == MAPS and
            len(data["maps"]) == len(MAPS),
            "mapped six-map review route drift")
    require(set(refs["world_weather_source"].get("weather_modes", [])) == WEATHERS,
            "weather IDs drift from pinned #798")
    owner = data.get("proposed_single_owner") or {}
    require(set(owner) == {
        "world_time_weather_sky_fog", "shot_focus_and_dof",
        "tone_exposure_bloom", "audio_playback_and_mix",
        "navigation_and_progression", "magic_vfx",
    }, "a required owner channel was lost or duplicated")
    require("no duplicate sky/light actors" in owner["world_time_weather_sky_fog"],
            "duplicated sky/lighting authorship")
    require(data.get("proposed_arbitration_priority") == PRIORITIES,
            "priority hierarchy drift")
    flow = data.get("data_flow") or {}
    for key in ("commit_or_save_game_mutation",
                "cinematics_can_unlock_story",
                "bokeh_can_fake_distance_scattering",
                "visuals_can_replace_physical_sea_contact"):
        require(flow.get(key) is False, "unsafe presentation->gameplay write " + key)
    safe = data.get("procedural_safeguards") or {}
    for key in ("review_only", "starbourne_gated",
                "no_global_postprocess_edits",
                "no_extra_lighting_actor_spawns",
                "source_validation_required",
                "native_approval_required"):
        require(safe.get(key) is True, "missing safety gate " + key)
    require(safe.get("production_content_modified") is False,
            "production content modification not authorized")
    require(safe.get("render_admission") == "NOT_RUN",
            "cannot assert native visual admission")
    require(safe.get("allowed_party_members") ==
            ["Ender", "Ionia", "Lyra_POST_SPLASHDOWN_ONLY"],
            "premature/unavailable party members")
    items = data.get("bindings")
    require(isinstance(items, list) and len(items) == 9,
            "exactly nine scene bindings required")
    from_focus = focus["shots"]
    ids = [s["id"] for s in from_focus]
    require([x.get("focus_shot") for x in items if isinstance(x, dict)] == ids,
            "exact shot ordering/identity mismatch")
    for item, shot in zip(items, from_focus):
        name = shot["id"]
        require(item.get("map") in MAPS, name + " unknown native scene")
        require(item.get("camera_mode") == shot["camera_state"],
                name + " focus/scene mode mismatch")
        look = item.get("lighting_look")
        if look is None:
            require(name == "FW09_NightSky_Wonder" and
                    item.get("lighting_bind_status") ==
                    "BLOCKED_MISSING_SHORE_NIGHT_LOOK",
                    "unverified missing-look fallback")
        else:
            require(look in LOOKS, name + " unknown lighting preset")
            require(item.get("lighting_bind_status") ==
                    "EXTERNAL_DRAFT_REFERENCE_NOT_INTEGRATED",
                    name + " lighting cannot claim integration")
        modes = item.get("allowed_weather_modes")
        require(isinstance(modes, list) and bool(modes)
                and set(modes).issubset(WEATHERS),
                name + " weather mismatch")
        require(item.get("output_authority") == "PRESENTATION_INTENT_ONLY",
                name + " illegal game/state output")
        require(item.get("native_provenance") == "NOT_ESTABLISHED",
                name + " native execution not proven")
        require(item.get("audio_binding_status") ==
                "SEMANTIC_UNBOUND_NO_AUDIO_EVENT_ASSERTED",
                name + " fabricated audio event")
        require(isinstance(item.get("audio_intent"), str)
                and bool(item["audio_intent"]) and
                isinstance(item.get("accessibility_and_gameplay_gate"), str),
                name + " missing sensory intent/safety")
    checks = {item["focus_shot"]: item for item in items}
    require(checks["FW06_Emergency_Splashdown"]["story_phase_semantic_only"] ==
            "PHYSICAL_SEA_CONTACT_REQUIRED",
            "sea contact cannot be inferred from a camera cut")
    require(checks["FW08_Lyra_Introduction"]["story_phase_semantic_only"] ==
            "POST_SPLASHDOWN_LYRA_INTRO_ONLY",
            "Lyra cannot precede physical splashdown")
    require(checks["FW09_NightSky_Wonder"]["lighting_look"] is None,
            "do not misbind harbor night sky to shore night")
    return {
        "status": "SOURCE_BINDINGS_VALID_NOT_INTEGRATED",
        "mapped_scenes": len(items), "linked_look_refs": 8,
        "missing_look": "FW09_SHORE_NIGHT",
        "runtime_applied": False, "native_render_passed": False,
    }


def self_test(data: dict, focus: dict):
    def run(name, mutate):
        changed = copy.deepcopy(data)
        mutate(changed)
        try:
            verify(changed, focus)
        except ValueError:
            print("PASS negative:", name)
            return
        raise AssertionError("FAIL OPEN: " + name)

    run("duplicate scene", lambda d: d["bindings"][1].update(
        focus_shot="FW01_Dock_Establish"))
    run("unapproved look", lambda d: d["bindings"][3].update(
        lighting_look="magic_global_override"))
    run("premature Lyra", lambda d: d["bindings"][7].update(
        story_phase_semantic_only="PRELAUNCH_LYRA"))
    run("fake sea contact", lambda d: d["bindings"][5].update(
        story_phase_semantic_only="CUTSCENE_SAYS_SPLASHDOWN"))
    run("world ownership conflict", lambda d: d["proposed_single_owner"].update(
        world_time_weather_sky_fog="Two independent sky actors"))
    run("story mutation", lambda d: d["data_flow"].update(
        cinematics_can_unlock_story=True))
    run("missing accessibility", lambda d: d["proposed_arbitration_priority"].pop(0))
    run("gameplay lens authority", lambda d: d["bindings"][0].update(
        output_authority="GRANT_PLAYER_PROGRESS"))
    run("false audio binding", lambda d: d["bindings"][0].update(
        audio_binding_status="AUDIO_NATIVE_PASS"))
    run("Starbourne unlock", lambda d: d["procedural_safeguards"].update(
        starbourne_gated=False))
    run("fake shore night", lambda d: d["bindings"][8].update(
        lighting_look="harbor_night_review"))
    print("PASS positive and 11 negative integration checks")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    focus = json.loads(FOCUS.read_text(encoding="utf-8"))
    print(json.dumps(verify(data, focus), indent=2))
    if a.self_test:
        self_test(data, focus)


if __name__ == "__main__":
    main()
