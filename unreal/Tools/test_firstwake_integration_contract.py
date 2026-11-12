#!/usr/bin/env python3
"""Engine-free guard for the First Wake interaction integration experiment.

Checks the presence of source-level authority boundaries and test assertions;
does NOT execute Unreal, simulate actual collisions or prove PIE playability.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp"
MILESTONE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp"
WATER = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSWaterLandingGate.cpp"
STATE = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSFirstWakeState.h"
VERIFIER = ROOT / "Tools/Verify-Unreal.ps1"

TEST_MARKERS = (
    '"TSTSS.FirstWake.InteractionToSplashdown"',
    'World->SpawnActor<ATSTSSMilestoneActor>()',
    'Trigger->TryActivate(Story)',
    'Cannot hire Ionia before discovering flyer',
    'Ionia is hired before boarding',
    'Engineering clearance blocked until every inspection',
    'Inspect(ETSTSSInspectionStation::Lift)',
    'Inspect(ETSTSSInspectionStation::Pressure)',
    'Inspect(ETSTSSInspectionStation::Reserve)',
    'First flight genuinely launches',
    'Generic interaction cannot manufacture sea contact',
    'Generic interaction cannot manufacture flotation',
    'WaterGate->Observe(0.1f, false, 0.f, Story)',
    'WaterGate->Observe(0.1f, true, 180.f, Story)',
    'for (int32 Step = 0; Step < 10; ++Step)',
    'Contact gap invalidates transient flotation timer',
    'for (int32 Step = 0; Step < 21; ++Step)',
    'Chapter 1 Act 1 begins ONLY at sustained flotation',
    'ActivateBeat(ETSTSSFirstWakeBeat::EmptyReserveInspected)',
    'ActivateBeat(ETSTSSFirstWakeBeat::ReturnedToBerth)',
    'Snapshot->IsStructurallyValid()',
    'Restored->Restore(Snapshot->bFirstWakeStarted',
    'New game reset returns to Prelude',
    'World->DestroyWorld(false)',
)
ACTOR_MARKERS = (
    'State->InspectStation(InspectionStation)',
    'State->AdvanceTo(Milestone)',
    'Milestone == ETSTSSFirstWakeBeat::SeaContact',
    'Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed',
)
WATER_MARKERS = (
    'Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::SeaContact)',
    'Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::FlotationConfirmed)',
    'StableContactSeconds < 2.f',
    'if (!bHullTouchesWater)',
)
STORY_MARKERS = (
    'return bStarted && static_cast<uint8>(CurrentBeat) >=',
    'static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed);',
)

def contract(sources):
    misses = []
    # Scope the actor's authority assertions to TryActivate itself:
    # a separate read-only helper must never satisfy a missing physics guard.
    start = "bool ATSTSSMilestoneActor::TryActivate("
    end = "\n#if WITH_EDITOR\nvoid ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore("
    if start not in sources["actor"]:
        misses.append("actor: TryActivate entrypoint absent")
        actor_gate = ""
    else:
        actor_gate = sources["actor"].split(start, 1)[1].split(end, 1)[0]
    for key, required in (
        ("test", TEST_MARKERS), ("actor", ACTOR_MARKERS),
        ("water", WATER_MARKERS), ("story", STORY_MARKERS),
    ):
        for marker in required:
            examined = actor_gate if key == "actor" else sources[key]
            if marker not in examined:
                misses.append(f"{key}: {marker}")
    found = re.findall(
        r'IMPLEMENT_SIMPLE_AUTOMATION_TEST\s*\(\s*\w+\s*,\s*"([^"]+)"',
        sources["test"], re.S
    )
    if found != ["TSTSS.FirstWake.InteractionToSplashdown"]:
        misses.append("native test registration is missing or duplicated")
    if sources["verify"].count("'TSTSS.FirstWake.InteractionToSplashdown'") != 1:
        misses.append("native JSON verifier does not require test exactly once")
    return misses

class FirstWakeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {
            key: path.read_text(encoding="utf-8")
            for key, path in {
                "test": TEST, "actor": MILESTONE, "water": WATER,
                "story": STATE, "verify": VERIFIER,
            }.items()
        }

    def test_current_source_contract(self):
        self.assertEqual(contract(self.sources), [])

    @staticmethod
    def mutate_real_activation_guard(text: str, old: str, new: str) -> str:
        # New read-only review visibility helpers may contain the same enum.
        # Negative controls must mutate the *authoritative* TryActivate body,
        # not the first cosmetic occurrence in the translation unit.
        entry = "bool ATSTSSMilestoneActor::TryActivate("
        before, sep, body = text.partition(entry)
        if not sep or old not in body.split(
            "\n#if WITH_EDITOR\nvoid ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(", 1
        )[0]:
            raise AssertionError("native activation guard missing from fixture")
        return before + sep + body.replace(old, new, 1)

    def test_forged_contact_negative_control(self):
        mutated = dict(self.sources)
        mutated["actor"] = self.mutate_real_activation_guard(
            mutated["actor"], "Milestone == ETSTSSFirstWakeBeat::SeaContact",
            "Milestone == ETSTSSFirstWakeBeat::Launched")
        self.assertTrue(contract(mutated))

    def test_lost_flotation_guard_negative_control(self):
        mutated = dict(self.sources)
        mutated["actor"] = self.mutate_real_activation_guard(
            mutated["actor"], "Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed",
            "Milestone == ETSTSSFirstWakeBeat::EngineeringChecked")
        self.assertTrue(contract(mutated))

    def test_changed_physics_threshold_negative_control(self):
        mutated = dict(self.sources)
        mutated["water"] = mutated["water"].replace(
            "StableContactSeconds < 2.f", "StableContactSeconds < 0.f", 1)
        self.assertTrue(contract(mutated))

    def test_early_chapter_boundary_negative_control(self):
        mutated = dict(self.sources)
        mutated["story"] = mutated["story"].replace(
            'static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed);',
            'static_cast<uint8>(ETSTSSFirstWakeBeat::SeaContact);', 1)
        self.assertTrue(contract(mutated))

    def test_removed_required_native_assertion_negative_control(self):
        mutated = dict(self.sources)
        mutated["test"] = mutated["test"].replace(
            "Generic interaction cannot manufacture flotation",
            "Generic interaction can forge flotation", 1)
        self.assertTrue(contract(mutated))

    def test_native_report_inventory_negative_control(self):
        mutated = dict(self.sources)
        mutated["verify"] = mutated["verify"].replace(
            "'TSTSS.FirstWake.InteractionToSplashdown'", "", 1)
        self.assertTrue(contract(mutated))

if __name__ == "__main__":
    unittest.main(verbosity=2)
