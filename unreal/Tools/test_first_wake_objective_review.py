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
        self.assertIn('const bool bLoaded = LoadFirstWake(TEXT("first_wake_quick"));', self.explorer)
        self.assertIn("TSTSSInteractionReach::IsInsidePlayerReach(", self.explorer)
        self.assertIn("TSTSSInteractionReach::GetCameraTraceLength(", self.explorer)

    def test_quicksave_load_feedback_is_result_bound(self):
        self.assertIn('const bool bSaved = SaveFirstWake(TEXT("first_wake_quick"));', self.explorer)
        self.assertIn("ShowFirstWakeReviewSaveLoadStatus(false, bSaved);", self.explorer)
        self.assertIn('const bool bLoaded = LoadFirstWake(TEXT("first_wake_quick"));', self.explorer)
        self.assertIn("if (bLoaded)", self.explorer)
        self.assertIn("ShowFirstWakeReviewSaveLoadStatus(true, bLoaded);", self.explorer)
        self.assertIn("load failed; no progress restored", self.explorer)
        self.assertIn("save failed; progress not confirmed", self.explorer)
        self.assertIn("story progress saved; position not saved", self.explorer)
        self.assertIn("story progress loaded; position unchanged", self.explorer)
        self.assertIn("bSucceeded ? FColor::Green : FColor::Red", self.explorer)

    def test_review_status_is_non_shipping_and_read_only(self):
        section = self.explorer.split("void ShowFirstWakeReviewSaveLoadStatus", 1)[1].split(
            "void ShowFirstWakeReviewObjective", 1
        )[0]
        self.assertIn("#if !UE_BUILD_SHIPPING", section)
        self.assertIn("#else", section)
        self.assertIn("GEngine->AddOnScreenDebugMessage(", section)
        for prohibited in ("SaveProgress(", "Restore(", "AdvanceTo("):
            self.assertNotIn(prohibited, section)

    def test_j_recall_is_read_only_and_exposed_by_review_input(self):
        config = (ROOT / "Config/DefaultInput.ini").read_text(encoding="utf-8")
        explorer_header = (PUBLIC / "TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
        self.assertIn('+ActionMappings=(ActionName="ReviewObjective",Key=J)', config)
        self.assertIn('BindAction(TEXT("ReviewObjective"), IE_Pressed', self.explorer)
        self.assertIn('&ATSTSSExplorerCharacter::ShowObjectiveReview', self.explorer)
        self.assertIn("void ShowObjectiveReview();", explorer_header)
        handler = self.explorer.split(
            "void ATSTSSExplorerCharacter::ShowObjectiveReview()", 1
        )[1].split("void ATSTSSExplorerCharacter::QuickSave()", 1)[0]
        self.assertIn("ShowFirstWakeReviewObjective(FirstWakeState);", handler)
        for forbidden in ("AdvanceTo(", "InspectStation(", "SaveFirstWake(", "LoadFirstWake("):
            self.assertNotIn(forbidden, handler)
        self.assertIn("[J to recall]", self.explorer)

    def test_portable_compiled_probe_is_present(self):
        code = (ROOT / "Tools/check_first_wake_objective_compiled.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("FString UTSTSSFirstWakeState::GetReviewObjectiveText() const", code)
        self.assertIn("semantic mutation control rejected wrong objective", code)

    def test_rejected_in_reach_milestone_provides_truthful_review_hint(self):
        self.assertIn("void ShowFirstWakeReviewBlockedInteraction(", self.explorer)
        self.assertIn("First Wake (review): no progress; objective:", self.explorer)
        self.assertIn("FColor::Yellow", self.explorer)
        self.assertIn("if (Milestone->TryActivate(FirstWakeState))", self.explorer)
        # The rejected branch must stay inside both the camera hit test and
        # the player-reach gate, not claim a failed interaction at a distance.
        section = self.explorer.split("void ATSTSSExplorerCharacter::Interact()", 1)[1].split(
            "void ATSTSSExplorerCharacter::ShowObjectiveReview()", 1
        )[0]
        self.assertLess(section.index("LineTraceSingleByChannel"),
                        section.index("IsInsidePlayerReach("))
        self.assertLess(section.index("IsInsidePlayerReach("),
                        section.index("Milestone->TryActivate(FirstWakeState)"))
        self.assertIn(
            "else\n                {\n"
            "                    // A valid, in-reach marker rejected the state transition.",
            section,
        )
        self.assertIn("ShowFirstWakeReviewBlockedInteraction(FirstWakeState);", section)
        helper = self.explorer.split("void ShowFirstWakeReviewBlockedInteraction(", 1)[1].split(
            "void ShowFirstWakeReviewObjective(", 1
        )[0]
        self.assertIn("#if !UE_BUILD_SHIPPING", helper)
        self.assertNotIn("AdvanceTo(", helper)
        self.assertNotIn("InspectStation(", helper)

    def test_pie_acceptance_matrix_cannot_omit_player_safety_gates(self):
        matrix = (ROOT / "Docs/FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md").read_text(
            encoding="utf-8"
        )
        for number in range(1, 13):
            self.assertIn(f"| P{number:02d} |", matrix)
        for gate in ("SOURCE_HEAD=", "NATIVE_AUTOMATION_25=", "PIE_E_AND_OCCLUSION=",
                     "PIE_J_OBJECTIVE=", "PIE_F5_F9_STORY_SAVE=",
                     "CLEAN_TREE_BEFORE=", "CLEAN_TREE_AFTER=", "NOT_TESTED",
                     "NOT_AUTHORIZED", "first_wake_quick.sav",
                     "UE 5.8.4 isolated PIE acceptance matrix"):
            self.assertIn(gate, matrix)
        self.assertIn("never overwrite or delete", matrix)
        self.assertIn("player world position does **not** rewind", matrix)

    def test_native_regression_registered_for_exact_head_verification(self):
        name = "TSTSS.FirstWake.ReviewObjectivesAreReadOnly"
        self.assertIn(name, self.test_file)
        self.assertIn(name, self.verifier)
        for gate in ("Reading objective never edits beat", "Reading objective never edits mask",
                     "Cue cannot forge sea contact", "Restore genuine flotation state"):
            self.assertIn(gate, self.test_file)


if __name__ == "__main__":
    unittest.main()
