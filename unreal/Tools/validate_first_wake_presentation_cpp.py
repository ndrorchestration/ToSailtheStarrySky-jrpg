#!/usr/bin/env python3
"""Cross-check Unreal C++ presentation-intent resolver against reviewed JSON.

Never claims UHT/C++ compile or PIE tests. No Unreal process or filesystem writes.
Native test registry remains at the existing exact 35 names.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from validate_first_wake_presentation_bindings import verify as verify_bindings

TOOLS = Path(__file__).resolve().parent
PROJECT = TOOLS.parent
SOURCE = PROJECT / "Source/ToSailTheStarrySky/Private/Review/TSTSSPresentationCoordinatorSubsystem.cpp"
HEADER = PROJECT / "Source/ToSailTheStarrySky/Public/Review/TSTSSPresentationCoordinatorSubsystem.h"
BINDINGS = PROJECT / "DataSource/Cinematics/FirstWakePresentationBindings.review.json"
FOCUS = PROJECT / "DataSource/Cinematics/FirstWakeFocusProfiles.review.json"

ENUM_TO_SHOT = {
    "DockEstablish": "FW01_Dock_Establish",
    "IoniaConversation": "FW02_Ionia_Conversation",
    "EngineInspection": "FW03_Engine_Inspection",
    "EngineAwakening": "FW04_Engine_Awakening",
    "FirstWakeLiftoff": "FW05_FirstWake_Liftoff",
    "EmergencySplashdown": "FW06_Emergency_Splashdown",
    "ShoreExploration": "FW07_Shore_Exploration",
    "LyraIntroduction": "FW08_Lyra_Introduction",
    "NightSkyWonder": "FW09_NightSky_Wonder",
}

CASE_PATTERN = re.compile(
    r"case ETSTSSPresentationMoment::(?P<moment>\w+):\s*(?://[^\n]*\n\s*)*"
    r"return \{TEXT\(\"(?P<map>[^\"]+)\"\),\s*TEXT\(\"(?P<shot>[^\"]+)\"\),\s*"
    r"(?:(?:TEXT\(\"(?P<look>[^\"]+)\"\))|(?P<unbound>nullptr)),\s*"
    r"TEXT\(\"(?P<audio>[^\"]+)\"\),\s*"
    r"(?P<focus>true|false),\s*(?P<rack>true|false),\s*"
    r"(?P<deep>true|false)\};",
    re.S
)

FORBIDDEN_WRITES = [
    "->AdvanceTo(", "->AdvanceWaterBeat(", "->InspectStation(",
    "->Restore(", "->Reset(", "->RequestWeather(",
    "->RequestTimeOfDay(", "->EmitCue(", "->StopCue(",
    "->SetCategoryVolume(", "->SetMuted(", "SpawnActor(",
    "SetViewTarget(", "SetActorRotation(", "SetFocusSettings(",
    "OpenLevel(", "SaveGameToSlot(", "duplicate_asset(",
]


def demand(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError("HOLD: " + msg)


def parse_cases(source: str) -> dict[str, dict]:
    entries = {}
    for match in CASE_PATTERN.finditer(source):
        row = match.groupdict()
        name = row["moment"]
        demand(name not in entries, "duplicate C++ scene case: " + name)
        entries[name] = row
    return entries


def validate_cpp(source: str, header: str, bindings: dict, focus: dict):
    verify_bindings(bindings, focus)
    demand('#include "Review/TSTSSPresentationCoordinatorSubsystem.h"' in source,
           "C++ implementation include path")
    demand('"TSTSSPresentationCoordinatorSubsystem.generated.h"' in header,
           "UHT generated header required")
    demand("class TOSAILTHESTARRYSKY_API UTSTSSPresentationCoordinatorSubsystem" in header
           and "public UWorldSubsystem" in header, "must use world-scoped Unreal subsystem")
    demand("FTSTSSPresentationIntent" in header and
           "OnReviewIntentChanged" in header and
           "BlueprintAssignable" in header, "Blueprint bridge not exposed")
    demand("bReviewEnabled = false" in header,
           "review must be opt-in and disabled by default")
    demand("DoesSupportWorldType" in source and
           "WorldType == EWorldType::PIE" in source and
           "#if WITH_EDITOR" in source, "PIE-only review boundary missing")
    demand("World->GetMapName()" in source and
           "DENIED_WRONG_NATIVE_MAP" in source, "real world map check absent")
    demand("GetCurrentBeat()" in source and "AreInspectionsComplete()" in source,
           "story read-only getters missing")
    demand("HasStoryPrerequisite(StoryState, Moment)" in source and
           "DENIED_AUTHORITATIVE_STORY_PREREQUISITE" in source,
           "accepted story guard missing")
    demand("WeatherCompatible(Moment, WorldWeather)" in source and
           "DENIED_WEATHER_NOT_IN_REVIEW_LOOK" in source,
           "owned world-weather guard missing")
    demand("bReducedMotion &&" not in source or
           "!bReducedMotion && !bGameplayClarityOverride" in source,
           "accessibility condition missing")
    demand("!bReducedMotion && !bGameplayClarityOverride" in source,
           "review must obey reduced motion and gameplay clarity")
    demand("HOLD_UNRESOLVED_SHORE_NIGHT_LIGHTING" in source,
           "missing shore-night look must fail closed")
    demand("OnReviewIntentChanged.Broadcast(CurrentIntent)" in source,
           "presentation event must be observable but never applied")
    demand("CurrentIntent = FTSTSSPresentationIntent()" in source,
           "must clear stale cue")
    demand("bReviewEnabled = bEnabled" in source, "explicit opt-in missing")
    demand("GetTargetWeather()" in source and
           "ETSTSSWeather::Clear" in source,
           "weather read-only snapshot / deterministic fallback missing")
    demand(not any(token in source for token in FORBIDDEN_WRITES),
           "coordinator contains an unauthorized world/gameplay/audio write")
    case_rows = parse_cases(source)
    demand(set(case_rows) == set(ENUM_TO_SHOT),
           "C++ moment enumeration/shot inventory mismatch")
    header_names = set(re.findall(
        r"^\s*(\w+),?\s*$",
        header.split("enum class ETSTSSPresentationMoment", 1)[1]
              .split("};", 1)[0].split("{", 1)[1], flags=re.M))
    demand(header_names == set(ENUM_TO_SHOT) | {"None"},
           "header enum misses or adds moments")
    rows = {x["focus_shot"]: x for x in bindings["bindings"]}
    for moment, expected_shot in ENUM_TO_SHOT.items():
        row = case_rows[moment]
        ref = rows[expected_shot]
        demand(row["shot"] == expected_shot, moment + " wrong shot id")
        demand(row["map"] == ref["map"], moment + " wrong real world level")
        demand(row["look"] == ref["lighting_look"],
               moment + " wrong lighting source / fabricated shore-night look")
        demand(row["audio"] == ref["audio_intent"],
               moment + " invented or mismatched audio event")
        if ref["camera_mode"] in ("EXPLORATION", "ACTION", "ESTABLISH", "AWE"):
            demand(row["focus"] == "false" and row["rack"] == "false"
                   and row["deep"] == "true",
                   moment + " fails low-risk gameplay/wide focus")
        elif ref["camera_mode"] in ("DIALOGUE", "INSPECT", "REVEAL"):
            demand(row["focus"] == "true", moment + " missing author attention")
    return {
        "status": "CPP_SOURCE_CONTRACT_VALID_NOT_NATIVE_COMPILED",
        "shot_cases": len(case_rows),
        "runtime_status": "UNVERIFIED",
        "audio_status": "SEMANTIC_ONLY_NOT_BOUND",
        "world_writes": "NOT_PRESENT_IN_SOURCE",
    }


def self_test(source: str, header: str, bindings: dict, focus: dict):
    changes = [
        ("fake sound playback", lambda s,h: (s + "\n->EmitCue(",h)),
        ("fake map transition", lambda s,h: (s + "\nOpenLevel(",h)),
        ("default enabled", lambda s,h: (s,h.replace(
            "bReviewEnabled = false", "bReviewEnabled = true"))),
        ("starbourne look fabrication", lambda s,h: (s.replace(
            "nullptr, TEXT(\"quiet_night_wind_distant_sea\")",
            "TEXT(\"shore_night_fabricated\"), TEXT(\"quiet_night_wind_distant_sea\")"),h)),
        ("incorrect weather", lambda s,h: (s.replace(
            "WeatherCompatible(Moment, WorldWeather)",
            "WeatherCompatible(Moment, ETSTSSWeather::Clear)"),h)),
        ("remove story guard", lambda s,h: (s.replace(
            "HasStoryPrerequisite(StoryState, Moment)", "true"),h)),
        ("false sea-contact authority", lambda s,h: (s + "\n->AdvanceWaterBeat(",h)),
        ("camera autopilot", lambda s,h: (s + "\nSetViewTarget(",h)),
        ("wrong world level", lambda s,h: (s.replace(
            'TEXT("VS02_AureateInteriors"), TEXT("FW03_Engine_Inspection")',
            'TEXT("VS01_DenithHarbor"), TEXT("FW03_Engine_Inspection")'),h)),
        ("remove PIE-only", lambda s,h: (s.replace(
            "WorldType == EWorldType::PIE", "true"),h))
    ]
    for name, fn in changes:
        altered_source, altered_header = fn(source,header)
        try:
            validate_cpp(altered_source,altered_header,bindings,focus)
        except ValueError:
            print("PASS negative:",name)
        else:
            raise AssertionError("FAIL OPEN: " + name)
    print("PASS positive and",len(changes),"negative source-contract tests")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
    focus = json.loads(FOCUS.read_text(encoding="utf-8"))
    print(json.dumps(validate_cpp(source,header,bindings,focus),indent=2))
    if args.self_test:
        self_test(source,header,bindings,focus)


if __name__ == "__main__":
    main()
