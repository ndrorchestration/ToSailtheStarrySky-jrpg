#!/usr/bin/env python3
"""Source-lock the First Wake opt-in CineCamera lens receiver.

This is intentionally not a UE C++ build, UHT parse, PIE capture, or visual
acceptance. Runtime lens writes remain confined to a dormant authored camera
on a verified disposable review map after an explicit review action.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
MODULE = PROJECT / "Source/ToSailTheStarrySky"
HEADER = MODULE / "Public/Review/TSTSSReviewFocusReceiver.h"
SOURCE = MODULE / "Private/Review/TSTSSReviewFocusReceiver.cpp"
COORD = MODULE / "Private/Review/TSTSSPresentationCoordinatorSubsystem.cpp"
BUILDSPEC = MODULE / "ToSailTheStarrySky.Build.cs"
TEST = MODULE / "Private/Tests/TSTSSAtmosphereDirectorTests.cpp"
PROFILES = PROJECT / "DataSource/Cinematics/FirstWakeFocusProfiles.review.json"

FORBIDDEN_SOURCE = (
    "->AdvanceTo(", "->AdvanceWaterBeat(", "->InspectStation(",
    "->Restore(", "->Reset(", "->RequestWeather(",
    "->RequestTimeOfDay(", "->EmitCue(", "->StopCue(",
    "->SetCategoryVolume(", "->SetMuted(", "SpawnActor(",
    "SetViewTarget(", "OpenLevel(", "SaveGameToSlot(",
    "SetActorRotation(", "EditorAssetLibrary.duplicate_asset("
)


def require(ok: bool, reason: str):
    if not ok:
        raise ValueError("HOLD: " + reason)


def validate(source: str, header: str, coord: str,
             builds: str, native_tests: str, profiles: dict) -> dict:
    require(profiles.get("schema") == "tstss.firstwake.dynamic_focus.review.v1",
            "unexpected lens profile schema")
    items = {x["id"]: x for x in profiles["shots"]}
    require("CinematicCamera" in builds,
            "missing CinematicCamera module dependency")
    require('"TSTSSReviewFocusReceiver.generated.h"' in header,
            "missing Unreal generated header for receiver")
    require("UCLASS(Blueprintable)" in header and
            "public AActor" in header,
            "receiver actor declaration missing")
    require("bExplicitReviewOptIn = false" in header,
            "receiver must be disabled by default")
    require("TObjectPtr<ACineCameraActor> StagedReviewCamera" in header
            and "TObjectPtr<AActor> AuthoredEngineFocusAnchor" in header,
            "camera and focus target must be assigned, never discovered by arbitrary ray")
    require("DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam" not in source,
            "receiver cannot declare second competing presentation coordinator")
    require("IsFocusCueApplicable(" in source and "Moment ==" in source,
            "shot eligibility missing")
    require('FName(TEXT("FW03_Engine_Inspection"))' in source and
            'FName(TEXT("FW04_Engine_Awakening"))' in source,
            "only two engineering moments eligible")
    require(source.count("World->WorldType != EWorldType::PIE") == 2
            and "#if WITH_EDITOR" in source,
            "both BeginPlay and lens-apply PIE admission checks required")
    require("bExplicitReviewOptIn" in source and
            "TSTSS_BOKEH_ENGINE_REVIEW_" in source and
            "TSTSS_VS_REVIEW_" in source,
            "isolated explicit camera and source focus anchor guards missing")
    require("StagedReviewCamera->GetWorld() != World" in source
            and "AuthoredEngineFocusAnchor->GetWorld() != World" in source,
            "review camera and anchor must belong to current world")
    require("Player->GetViewTarget() == StagedReviewCamera" in source,
            "must reject active player camera to avoid stealing game view")
    require("FocusCm >= 65.f" in source and "FocusCm <= 12000.f" in source
            and "FMath::IsFinite(FocusCm)" in source,
            "distance and nan guard missing")
    require("Settings.FocusMethod = ECameraFocusMethod::Manual" in source and
            "Settings.ManualFocusDistance = FocusCm" in source and
            "Cine->SetFocusSettings(Settings)" in source,
            "manual UE camera focus API missing")
    require("Cine->SetFocusSettings(OriginalFocus)" in source
            and "Cine->SetCurrentFocalLength(OriginalFocalLength)" in source
            and "Cine->SetCurrentAperture(OriginalAperture)" in source,
            "restore camera to original owned lens state")
    require("OnReviewIntentChanged.AddDynamic(" in source
            and "OnReviewIntentChanged.RemoveDynamic(" in source,
            "presentation event delegate must bind and clean up")
    require("GetWorldTimerManager().SetTimer(" in source
            and "0.25f, true" in source
            and "ClearTimer(FocusGuardTimer)" in source,
            "bounded low-rate expiry checker must clean up")
    require("!Coordinator->GetCurrentIntent().bEligible" in source
            and "!Coordinator->GetCurrentIntent().bAllowCinematicFocus" in source,
            "stale story/weather/visibility intent must revoke focus")
    require("!Coordinator->IsReviewEnabled()" in source
            and "AtmosphereCount != 1" in source,
            "no implicit run or multiple atmosphere owner support")
    require("TryPublishMoment(" in source
            and "false, false" in source,
            "only explicitly called authored review can request focus")
    require("!Intent.bAllowCinematicFocus" in source and
            "!Intent.bAllowFocusRack" in source and
            "Intent.bRequireDeepFocus" in source,
            "must defer to actual reduced-motion and gameplay clarity")
    require(not any(s in source for s in FORBIDDEN_SOURCE),
            "receiver illegally mutates gameplay, map, audio or view target")
    require("PrimaryActorTick.bCanEverTick = false" in source,
            "no per-frame actor tick")
    require("bHasSavedLens = false" in source,
            "focus owner must release applied lens state")
    require('NativeMapName.Equals(TEXT("M_EnginePresentationReview")' in coord,
            "coordinator does not allow exact isolated engine review map")
    require("!bMapMatches && !bHarborReviewCopy && !bEngineReviewCopy" in coord,
            "map alias bypasses strict scene denial")
    inspect=items.get("FW03_Engine_Inspection")
    reveal=items.get("FW04_Engine_Awakening")
    require(inspect is not None and reveal is not None,
            "engine focus profiles missing")
    require(inspect["lens_mm"] == 65 and inspect["f_stop"] == 2.8,
            "FW03 lens profile drift")
    require(reveal["lens_mm"] == 50 and reveal["f_stop"] == 4,
            "FW04 lens profile drift")
    require("SetCurrentFocalLength(bInspection ? 65.f : 50.f)" in source
            and "SetCurrentAperture(bInspection ? 2.8f : 4.0f)" in source,
            "C++ optical lens not source-locked to data profiles")
    require('#include "Review/TSTSSReviewFocusReceiver.h"' in native_tests
            and "IsFocusCueApplicable(" in native_tests
            and "UEDPIE_1_M_EnginePresentationReview" in native_tests,
            "native registered automation missing lens-receiver assertions")
    require("IsFocusCueApplicable(" in header
            and "RequestAuthoredEngineFocus(" in header,
            "Blueprint adapter and native pure policy API missing")
    return {
        "status": "CINE_RECEIVER_SOURCE_VALID_NOT_NATIVE_COMPILED",
        "engine_profiles": 2,
        "native_test_identity_added": False,
        "live_camera_modified": False,
        "runtime_native_status": "UNVERIFIED",
    }


def negative_fixtures(source, header, coord, builds, tests, profiles):
    cases = [
        ("lose explicit operator opt-in", "header",
         "bExplicitReviewOptIn = false", "bExplicitReviewOptIn = true"),
        ("accept non-PIE", "source",
         "World->WorldType != EWorldType::PIE", "false"),
        ("target player camera", "source",
         "Player->GetViewTarget() == StagedReviewCamera", "false"),
        ("allow foreign camera", "source",
         "StagedReviewCamera->GetWorld() != World", "false"),
        ("allow unreviewed focus anchor", "source",
         "TSTSS_VS_REVIEW_", "TSTSS_OTHER_"),
        ("remove lens restore", "source",
         "Cine->SetFocusSettings(OriginalFocus)", "// missing"),
        ("bypass coordinator", "source",
         "!Coordinator->IsReviewEnabled()", "false"),
        ("disable stale cue expiry", "source",
         "!Coordinator->GetCurrentIntent().bEligible", "false"),
        ("mutate weather", "source",
         "PrimaryActorTick.bCanEverTick = false",
         "PrimaryActorTick.bCanEverTick = false;\n->RequestWeather("),
        ("wrong optical lens", "source",
         "SetCurrentAperture(bInspection ? 2.8f : 4.0f)",
         "SetCurrentAperture(bInspection ? 1.2f : 4.0f)"),
        ("remove module dependency", "builds",
         '"CinematicCamera"', '"SomeOtherModule"'),
        ("fake engine map admission", "coord",
         'NativeMapName.Equals(TEXT("M_EnginePresentationReview")',
         'NativeMapName.EndsWith(TEXT("M_EnginePresentationReview")'),
        ("unregistered native assertions", "tests",
         '#include "Review/TSTSSReviewFocusReceiver.h"', "// missing"),
    ]
    originals = {
        "source": source, "header": header, "coord": coord,
        "builds": builds, "tests": tests, "profiles": profiles,
    }
    for title, key, before, after in cases:
        require(before in originals[key], "invalid fixture: " + title)
        case = dict(originals)
        case[key] = case[key].replace(before, after, 1)
        try:
            validate(case["source"], case["header"], case["coord"],
                     case["builds"], case["tests"], case["profiles"])
        except ValueError:
            print("PASS negative:", title)
        else:
            raise AssertionError("FAIL OPEN: " + title)
    altered_profiles = copy.deepcopy(profiles)
    next(x for x in altered_profiles["shots"]
         if x["id"] == "FW03_Engine_Inspection")["f_stop"] = 1.2
    try:
        validate(source, header, coord, builds, tests, altered_profiles)
    except ValueError:
        print("PASS negative: lens/profile drift")
    else:
        raise AssertionError("FAIL OPEN: lens/profile drift")
    print("PASS positive and", len(cases)+1, "negative source-lock fixtures")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    coord = COORD.read_text(encoding="utf-8")
    builds = BUILDSPEC.read_text(encoding="utf-8")
    tests = TEST.read_text(encoding="utf-8")
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    print(json.dumps(validate(source, header, coord, builds, tests, profiles),
                     indent=2))
    if a.self_test:
        negative_fixtures(source, header, coord, builds, tests, profiles)


if __name__ == "__main__":
    main()
