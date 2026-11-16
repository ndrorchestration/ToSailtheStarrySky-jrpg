"""Fail-closed source audit for the new First Wake ship-engine room location.

Contract-only: never substitute this audit for UE native build or actual PIE.
"""
from pathlib import Path
import unittest
import json

ROOT = Path(__file__).resolve().parents[1]
TRAVEL = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text()
PLAYER = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text()
MARKER = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp").read_text()
STATE = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp").read_text()
OLD_MAP = ROOT/"Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
SHIP_MAP = ROOT/"Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"

class EngineRoomReboardSourceContract(unittest.TestCase):
    def test_boarding_precedes_engineering(self):
        nav=TRAVEL.split("FString UTSTSSReviewShoreTravelSubsystem::NextReviewMap(",1)[1].split(
            "bool UTSTSSReviewShoreTravelSubsystem::IsEligible(",1)[0]
        self.assertIn("Beat == ETSTSSFirstWakeBeat::BoardedAureateWake",nav)
        self.assertIn("SourceMap == VisualReviewPreludeName",nav)
        self.assertIn("State->AreInspectionsComplete()",nav)
        self.assertLess(nav.index("Beat == ETSTSSFirstWakeBeat::BoardedAureateWake"),
                        nav.index("if (!State->AreInspectionsComplete())"))
        self.assertIn("SourceMap == PreludeName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked",nav)
        self.assertIn("SourceMap == ShipName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked",nav)

    def test_k_boarding_never_grants_launch(self):
        segment=TRAVEL.split("bool UTSTSSReviewShoreTravelSubsystem::QueueShore(",1)[1].split(
            "bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(",1)[0]
        self.assertIn("SourceMap != VisualReviewPreludeName",segment)
        self.assertIn("SourceMap == ShipName || SourceMap == OpticalName",segment)
        self.assertIn("AdvanceTo(ETSTSSFirstWakeBeat::Launched)",segment)
        self.assertIn("PendingInspectionMask = State->GetInspectionMask()",segment)
        self.assertIn("PendingBeat = State->GetCurrentBeat()",segment)
        self.assertIn("bPending = true",segment)

    def test_harbor_mechanical_markers_are_fully_retired_not_repurposed(self):
        self.assertIn("IsRetiredV5HarborEngineeringMarker",MARKER)
        self.assertIn("bInspection || Beat == ETSTSSFirstWakeBeat::EngineeringChecked",MARKER)
        self.assertIn("SetActorHiddenInGame(true);",MARKER)
        self.assertIn("SetActorEnableCollision(false);",MARKER)
        activate=MARKER.split("bool ATSTSSMilestoneActor::TryActivate(",1)[1]
        self.assertLess(activate.index("IsRetiredV5HarborEngineeringMarker"),
                        activate.index("State->InspectStation(InspectionStation)"))
        self.assertIn("TSTSS_ENGINEROOM_REVIEW_",MARKER)

    def test_room_uses_unchanged_state_bits_and_engine_authority(self):
        self.assertIn("State->InspectStation(InspectionStation)",MARKER)
        self.assertIn("State->AdvanceTo(Milestone)",MARKER)
        self.assertIn("State->AreInspectionsComplete()",MARKER)
        self.assertIn("CurrentBeat != ETSTSSFirstWakeBeat::BoardedAureateWake",STATE)
        self.assertIn("InspectionMask |= Bit;",STATE)
        self.assertIn("SavedInspectionMask",STATE)
        self.assertNotIn("InspectionMask = 0x07",PLAYER)

    def test_engine_room_spawn_requires_earned_arrival_and_is_atomically_staged(self):
        region=PLAYER.split("void StageEarnedEngineRoomReview(",1)[1].split(
            "ATSTSSExplorerCharacter::ATSTSSExplorerCharacter()",1)[0]
        for must in ("World->WorldType != EWorldType::PIE",
                     "World->GetNetMode() != NM_Standalone",
                     'TEXT("VS02_AureateInteriors")',
                     "State->GetCurrentBeat() != ETSTSSFirstWakeBeat::BoardedAureateWake",
                     'TEXT("TSTSS_ENGINEROOM_REVIEW_%s")',
                     "Spawned.Num() != UE_ARRAY_COUNT(Placements)",
                     "Marker->Destroy()", "SetActorLocation(",
                     "save_mutation=0"):
            self.assertIn(must,region)
        self.assertEqual(region.count('TEXT("LiftStation")'),1)
        self.assertEqual(region.count('TEXT("PressureStation")'),1)
        self.assertEqual(region.count('TEXT("ReserveStation")'),1)
        self.assertEqual(region.count('TEXT("EngineeringApproval")'),1)
        self.assertIn("if (Travel->ConsumeShoreArrival(World, FirstWakeState))",PLAYER)
        self.assertIn("StageEarnedEngineRoomReview(World, FirstWakeState, this);",PLAYER)

    def test_shipped_maps_untouched_and_dev_optics_separate(self):
        self.assertTrue(OLD_MAP.exists())
        self.assertTrue(SHIP_MAP.exists())
        self.assertIn("QueueOpticalInspection",TRAVEL)
        self.assertIn("SourceMap == OpticalName",TRAVEL)
        self.assertIn("World->GetNetMode() != NM_Standalone",TRAVEL)
        self.assertNotIn("OpenLevel(this, FName(TEXT(\"VS03_FirstWakeSky\")",PLAYER)

    def test_layout_manifest_bounded_and_matches_source(self):
        plan = json.loads((ROOT/"DataSource/Integration/FirstWakeEngineRoomReboard.review.json").read_text())
        self.assertEqual(plan["status"], "RESEARCH_REVIEW_LAYOUT_NOT_NATIVE_VERIFIED_OR_CREATOR_ART_APPROVED")
        self.assertEqual(plan["target_review_map"], "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors")
        self.assertFalse(plan["savegame_schema_changed"])
        self.assertFalse(plan["starbourne_unlocked"])
        self.assertEqual(plan["interaction_reach_cm"], 300)
        self.assertEqual(plan["optical_proximity_cm"], 450)
        self.assertEqual(len(plan["stations"]), 4)
        self.assertEqual([x["story_bit"] for x in plan["stations"][:3]],[1,2,4])
        self.assertEqual(plan["stations"][-1]["requires_mask"],7)
        deck=plan["authored_world_static_bounds_cm"]["MainWalkableDeck"]
        bridge=plan["authored_world_static_bounds_cm"]["BridgeDeck"]
        radius=plan["review_player_capsule_radius_cm"]
        px,py,pz=plan["review_entry_cm"]
        self.assertGreater(px-radius,bridge["x_max"])
        self.assertLess(px+radius,deck["x_max"])
        self.assertLess(abs(py)+radius,deck["y_max"])
        self.assertGreater(pz,deck["top_z"])
        for station in plan["stations"]:
            x,y,z=station["location_cm"]
            self.assertTrue(deck["x_min"]+radius < x < deck["x_max"]-radius)
            self.assertTrue(abs(y)+radius < deck["y_max"])
            self.assertGreater(z, deck["top_z"])
            pos=tuple(station["location_cm"])
            literal=f'FVector({pos[0]}.f, {pos[1]}.f, {pos[2]}.f)'
            self.assertIn(literal, PLAYER)
        self.assertIn("FVector(-350.f, -90.f, 140.f)",PLAYER)
        self.assertIn("enclosed physical engine room in actual Aureate Wake hull",
                      plan["production_requirements_not_established"])

    def test_engine_room_native_assertions_preserve_38_test_registry(self):
        source = (ROOT/"Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeReviewObjectiveTests.cpp").read_text()
        verifier = (ROOT/"Tools/Verify-Unreal.ps1").read_text()
        self.assertEqual(verifier.count("'TSTSS.FirstWake.ReviewObjectivesAreReadOnly'"), 1)
        self.assertNotIn("TSTSS.FirstWake.EngineRoomReboardAuthority",verifier)
        self.assertFalse((ROOT/"Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeEngineRoomReboardTests.cpp").exists())
        for assertion in ("Shipboard LIFT inspection accepts only once",
                          "Duplicate shipboard LIFT inspection rejected",
                          "LIFT alone cannot permit sky departure",
                          "Partially inspected V5 still routes to engine room",
                          "Two checks cannot permit sky departure",
                          "All three without signoff still cannot depart",
                          "Earned engineering signoff"):
            self.assertIn(assertion,source)

    def test_new_objective_mentions_engine_room(self):
        self.assertIn("Enter engine room; inspect the levitation LIFT",STATE)

if __name__=="__main__":
    unittest.main()
