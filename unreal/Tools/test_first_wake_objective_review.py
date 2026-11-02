"""Source-only First Wake review objective safety and integration checks.

These tests cannot establish a native UE compile, PIE input, or visual acceptance.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "Source/ToSailTheStarrySky/Private"
PUBLIC = ROOT / "Source/ToSailTheStarrySky/Public"


class ReviewObjectiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = (PRIVATE / "TSTSSFirstWakeState.cpp").read_text(encoding="utf-8")
        cls.header = (PUBLIC / "TSTSSFirstWakeState.h").read_text(encoding="utf-8")
        cls.explorer = (PRIVATE / "TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
        cls.test_file = (PRIVATE / "Tests/TSTSSFirstWakeReviewObjectiveTests.cpp").read_text(encoding="utf-8")
        cls.verifier = (ROOT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")

    def test_read_only_blueprint_objective_contract(self):
        self.assertIn('UFUNCTION(BlueprintPure, Category="TSTSS|First Wake|Review")', self.header)
        self.assertIn("FString GetReviewObjectiveText() const;", self.header)
        func = self.state.split("FString UTSTSSFirstWakeState::GetReviewObjectiveText() const", 1)[1].split(
            "bool UTSTSSFirstWakeState::AdvanceTo", 1
        )[0]
        self.assertIn("switch (CurrentBeat)", func)
        self.assertIn("if (!bStarted)", func)
        for mutating in ("AdvanceTo(", "AdvanceWaterBeat(", "InspectStation(", "SaveProgress(",
                         "LoadProgress(", "CurrentBeat =", "InspectionMask =", "bStarted ="):
            self.assertNotIn(mutating, func)

    def test_review_copy_covers_every_existing_story_beat(self):
        for beat in ("FlyerDiscovered", "IoniaHired", "BoardedAureateWake",
                     "EngineeringChecked", "Launched", "SeaContact",
                     "FlotationConfirmed", "EmptyReserveInspected", "ReturnedToBerth"):
            self.assertIn("case ETSTSSFirstWakeBeat::" + beat + ":", self.state)
        self.assertIn("(InspectionMask & 0x01u)", self.state)
        self.assertIn("(InspectionMask & 0x02u)", self.state)
        self.assertIn("(InspectionMask & 0x04u)", self.state)
        self.assertIn("Find Ionia's flyer", self.state)

    def test_onscreen_cue_does_not_override_story_authorization(self):
        self.assertIn("#if !UE_BUILD_SHIPPING", self.explorer)
        self.assertIn("GEngine->AddOnScreenDebugMessage(", self.explorer)
        self.assertIn("First Wake (review):", self.explorer)
        self.assertIn("if (Milestone->TryActivate(FirstWakeState))", self.explorer)
        self.assertIn("if (LoadFirstWake(TEXT(\"first_wake_quick\")))", self.explorer)
        self.assertIn("TSTSSInteractionReach::IsInsidePlayerReach(", self.explorer)
        self.assertIn("TSTSSInteractionReach::GetCameraTraceLength(", self.explorer)

    def test_native_regression_registered_for_exact_head_verification(self):
        name = "TSTSS.FirstWake.ReviewObjectivesAreReadOnly"
        self.assertIn(name, self.test_file)
        self.assertIn(name, self.verifier)
        for gate in ("Reading objective never edits beat", "Reading objective never edits mask",
                     "Cue cannot forge sea contact", "Restore genuine flotation state"):
            self.assertIn(gate, self.test_file)


if __name__ == "__main__":
    unittest.main()
