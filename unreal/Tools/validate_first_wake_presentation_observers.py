#!/usr/bin/env python3
"""Source-only custody regression for First Wake cinematic core event binding.

This verifies that the optional view adapter listens only to accepted state,
expires stale cues, binds to real player state and never changes gameplay.
NOT evidence of C++ compilation, PIE, camera output or audible sound.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
PATHS = {
    "state_h": ROOT / "Public/TSTSSFirstWakeState.h",
    "state_cpp": ROOT / "Private/TSTSSFirstWakeState.cpp",
    "coord_h": ROOT / "Public/Review/TSTSSPresentationCoordinatorSubsystem.h",
    "coord_cpp": ROOT / "Private/Review/TSTSSPresentationCoordinatorSubsystem.cpp",
    "explorer_cpp": ROOT / "Private/TSTSSExplorerCharacter.cpp",
    "native_test": ROOT / "Private/Tests/TSTSSAtmosphereDirectorTests.cpp",
}


def demand(test: bool, reason: str):
    if not test:
        raise ValueError("HOLD: " + reason)


def source_section(text: str, entry: str, next_entry: str):
    start = text.find(entry)
    end = text.find(next_entry, start + len(entry))
    demand(start >= 0 and end > start, "missing function boundaries: " + entry)
    return text[start:end]


def verify(rows: dict[str, str]) -> dict:
    sh, sc = rows["state_h"], rows["state_cpp"]
    ch, cc = rows["coord_h"], rows["coord_cpp"]
    ex, nt = rows["explorer_cpp"], rows["native_test"]

    demand("DECLARE_MULTICAST_DELEGATE(FTSTSSFirstWakeStateChanged)" in sh
           and "OnAcceptedChange() { return AcceptedChange; }" in sh,
           "native state observer definition missing")
    demand("FTSTSSFirstWakeStateChanged AcceptedChange;" in sh,
           "observer backing field missing")
    expected = [
        ("AdvanceTo(", "AdvanceWaterBeat(", 2),
        ("AdvanceWaterBeat(", "InspectStation(", 2),
        ("InspectStation(", "Reset()", 1),
        ("Reset()", "Restore(", 1),
    ]
    for before, after, count in expected:
        sec = source_section(sc,
            "UTSTSSFirstWakeState::" + before,
            "UTSTSSFirstWakeState::" + after)
        demand(sec.count("AcceptedChange.Broadcast();") == count,
               before + " accepted change signal count")
    tail = sc.split("bool UTSTSSFirstWakeState::Restore(", 1)
    demand(len(tail) == 2 and
           tail[1].count("AcceptedChange.Broadcast();") == 1,
           "restore accepted change signal count")
    demand(sc.count("AcceptedChange.Broadcast();") == 7,
           "total source observer signal count drift")
    demand("AcceptedChange.Broadcast();\n        return true;" in sc,
           "successful transitions must signal")
    demand("AcceptedChange.Broadcast();\n    return true;" in sc,
           "successful station/restore must signal")

    demand("bReviewEnabled = false" in ch,
           "preview must be disabled by default")
    demand("TWeakObjectPtr<UTSTSSFirstWakeState> ObservedStory" in ch
           and "FDelegateHandle StoryChangedHandle" in ch,
           "weak source binding and delegate lifetime guard missing")
    demand("ObservedRestoreGeneration" in ch
           and "ObservedWeather" in ch
           and "ObservedClockHours" in ch,
           "scene snapshot freshness data missing")
    demand("DoesSupportWorldType" in cc
           and "WorldType == EWorldType::PIE" in cc,
           "PIE-only admission missing")
    demand("GetPlayerPawn(World, 0)" in cc
           and "ActualStory != StoryState" in cc
           and "DENIED_UNBOUND_PLAYER_STORY_STATE" in cc,
           "caller-created story forgery guard missing")
    demand("DENIED_MISSING_WORLD_ATMOSPHERE" in cc
           and "Atmosphere->GetWorld() != World" in cc,
           "weather must originate from actual current level")
    demand("NativeMapName.Equals(Authored.SourceMap" in cc
           and "NativeMapName.Equals(TEXT(\"M_DenithHarborBokehStudy\")" in cc
           and "PIEIndex.IsNumeric()" in cc,
           "native map must be exactly matched after verified PIE prefix")
    demand("MapName.EndsWith(Authored.SourceMap" not in cc,
           "suffix spoofing bug restored")
    demand("StoryChangedHandle = ActualStory->OnAcceptedChange().AddUObject" in cc
           and "Bound->OnAcceptedChange().Remove(StoryChangedHandle)" in cc
           and "HandleAcceptedStoryChange" in cc,
           "accepted change observer must bind/clean up")
    demand("PublishNeutral(TEXT(\"CLEARED_AFTER_ACCEPTED_FIRST_WAKE_CHANGE\"))" in cc,
           "accepted transition must revoke old presentation")
    demand("EXPIRED_STORY_OR_WORLD_SNAPSHOT" in cc
           and "MatchesStorySnapshot(State, ObservedRestoreGeneration" in cc
           and "Atmosphere->GetTargetWeather() != ObservedWeather" in cc
           and "ObservedClockHours, 0.1f" in cc,
           "read-only getters must fail closed after state or world drift")
    demand("!bReducedMotion && !bGameplayClarityOverride" in cc,
           "gameplay and reduced-motion focus gate missing")
    danger = ["->AdvanceTo(", "->AdvanceWaterBeat(", "->InspectStation(",
              "->RequestWeather(", "->RequestTimeOfDay(", "->EmitCue(",
              "SaveGameToSlot(", "SpawnActor(", "OpenLevel(", "SetViewTarget("]
    demand(not any(token in cc for token in danger),
           "coordinator cannot write gameplay or render directly")

    accept = ex.find("if (Milestone->TryActivate(FirstWakeState))")
    publish = ex.find("Review->TryPublishMoment(", accept)
    demand(accept >= 0 and publish > accept,
           "cosmetic event must follow accepted E interaction")
    demand("if (Review->IsReviewEnabled())" in ex[accept:publish]
           and "ETSTSSPresentationMoment::EngineInspection" in ex[accept:publish]
           and "ETSTSSPresentationMoment::IoniaConversation" in ex[accept:publish],
           "opt-in interaction-to-presentation bridge missing")
    demand(re.search(r"Review->TryPublishMoment\(\s*FirstWakeState,\s*Atmosphere,\s*Moment,\s*true,\s*true\s*\)", ex) is not None,
           "interactive pawn must request clarity-first and motion-safe intent")
    demand("WorldType == EWorldType::PIE" in ex[accept:publish],
           "no non-PIE player adapter")
    demand("TestFalse(TEXT(\"Spoofed map suffix" in nt,
           "native regression for spoofed maps missing")
    demand("Story->OnAcceptedChange().AddLambda" in nt
           and "Story->OnAcceptedChange().Remove(Observer)" in nt,
           "native observer test must release its captured stack lambda")
    demand("MatchesStorySnapshot" in nt,
           "native test must check restore generation invalidation")

    return {
        "status": "SOURCE_OBSERVER_BRIDGE_VALID_NOT_NATIVE_COMPILED",
        "events_expected": 7,
        "real_player_bound": True,
        "active_gameplay_focus_override": True,
        "renderer_or_gameplay_writes": False,
        "native_execution": "NOT_ESTABLISHED",
    }


def self_test(rows: dict[str, str]):
    cases = [
        ("drop story broadcast",
         "state_cpp", "AcceptedChange.Broadcast();", "/* event missing */"),
        ("missing delegate cleanup",
         "coord_cpp", "Bound->OnAcceptedChange().Remove(StoryChangedHandle)",
         "// broken cleanup"),
        ("disable player ownership check",
         "coord_cpp", "ActualStory != StoryState", "false"),
        ("allow map suffix spoof",
         "coord_cpp", "NativeMapName.Equals(Authored.SourceMap", "MapName.EndsWith(Authored.SourceMap"),
        ("disable PIE gate",
         "coord_cpp", "WorldType == EWorldType::PIE", "false"),
        ("invent default allowed weather",
         "coord_cpp", "DENIED_MISSING_WORLD_ATMOSPHERE", "DEFAULT_CLEAR"),
        ("skip state generation",
         "coord_cpp", "MatchesStorySnapshot(State, ObservedRestoreGeneration", "MatchesStorySnapshot(State, 999"),
        ("disable red motion",
         "coord_cpp", "!bReducedMotion && !bGameplayClarityOverride", "true"),
        ("unaccepted interaction",
         "explorer_cpp", "if (Milestone->TryActivate(FirstWakeState))", "if (true)"),
        ("no observer test cleanup",
         "native_test", "Story->OnAcceptedChange().Remove(Observer)", "// leaked observer"),
    ]
    for title, key, before, after in cases:
        demand(before in rows[key], "invalid adversarial fixture: " + title)
        altered = dict(rows)
        altered[key] = altered[key].replace(before, after, 1)
        try:
            verify(altered)
        except ValueError:
            print("PASS negative:", title)
        else:
            raise AssertionError("FAIL OPEN: " + title)
    print("PASS positive and", len(cases), "negative observer fixtures")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    rows = {key: path.read_text(encoding="utf-8") for key, path in PATHS.items()}
    print(json.dumps(verify(rows), indent=2))
    if a.self_test:
        self_test(rows)


if __name__ == "__main__":
    main()
