"""Source contract for opt-in Ender PIE walk and held-Shift sprint.

Source-only negative mutation assertions; never claim native input or animation.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
INPUT = (ROOT / "Config/DefaultInput.ini").read_text(encoding="utf8")


def controls(src):
    return src.split("void ATSTSSExplorerCharacter::TryEnderPIEWalkRunControls()", 1)[1].split(
        "void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", 1
    )[0]


def holds_lease(src):
    b = controls(src)
    return all(gate in b for gate in (
        "bEnableEnderPIEWalkRunControls",
        "bFirstWakeThirdPersonReview", "IsPlayerControlled()",
        "World->WorldType == EWorldType::PIE",
        "World->GetNetMode() == NM_Standalone",
        'TEXT("/Game/TSTSS/Review/")',
        'Scene != TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
        'Scene != TEXT("VS02_AureateInteriors")',
        "RestoreEnderPIEWalkRunControls()",
        "bEnderPIEWalkRunChecked",
        "FMath::IsFinite(PriorSpeed)",
        "PriorSpeed < 180.f", "PriorSpeed > 900.f",
        "EnderPIEOriginalMaxWalkSpeed = PriorSpeed",
        "bEnderPIEWalkRunActive = true",
        "Movement->MaxWalkSpeed",
        "EnderPIELastAssignedMaxWalkSpeed",
        "bEnderPIESprintHeld", "PC->IsMoveInputIgnored()",
        "IsHilltoniaFlyerOpen()", "EngineFocusPreviewCamera.IsValid()",
        "WalkSpeedCmS = 260.f", "RunSpeedCmS = 480.f",
        "movement_owner_changed", "animation_NOT_VERIFIED"
    ))


class EnderPIEWalkRunTests(unittest.TestCase):
    def test_off_by_default_and_input_bound_only_in_editor_pie(self):
        self.assertIn("bool bEnableEnderPIEWalkRunControls = false;", HDR)
        self.assertIn("#if WITH_EDITORONLY_DATA", HDR)
        self.assertEqual(INPUT.count('+ActionMappings=(ActionName="EnderPIEReviewSprint",Key=LeftShift)'), 1)
        bind = CPP.split("void ATSTSSExplorerCharacter::SetupPlayerInputComponent(", 1)[1].split(
            "void ATSTSSExplorerCharacter::MoveForward(", 1)[0]
        self.assertIn("#if WITH_EDITOR", bind)
        self.assertIn("InputWorld->WorldType == EWorldType::PIE", bind)
        self.assertIn('BindAction(TEXT("EnderPIEReviewSprint"), IE_Pressed', bind)
        self.assertIn('BindAction(TEXT("EnderPIEReviewSprint"), IE_Released', bind)
        self.assertTrue(holds_lease(CPP))

    def test_lease_restored_only_when_owned(self):
        lease = CPP.split("void ATSTSSExplorerCharacter::RestoreEnderPIEWalkRunControls()", 1)[1].split(
            "void ATSTSSExplorerCharacter::TryEnderPIEWalkRunControls()", 1
        )[0]
        for required in ("if (!bEnderPIEWalkRunActive)",
                         "IsNearlyEqual(Movement->MaxWalkSpeed",
                         "EnderPIELastAssignedMaxWalkSpeed",
                         "Movement->MaxWalkSpeed = EnderPIEOriginalMaxWalkSpeed",
                         "TSTSS_ENDER_PIE_WALKRUN_RESTORED"):
            self.assertIn(required, lease)
        endplay = CPP.split("void ATSTSSExplorerCharacter::EndPlay(", 1)[1].split(
            "void ATSTSSExplorerCharacter::ToggleEngineFocusPreview(", 1
        )[0]
        self.assertIn("RestoreEnderPIEWalkRunControls();", endplay)
        for banned in ("SaveGameToSlot(", "OpenLevel(", "AdvanceTo(",
                       "SetActorLocation(", "TeleportTo(", "AddMovementInput("):
            self.assertNotIn(banned, controls(CPP))
            self.assertNotIn(banned, lease)

    def test_only_explicit_review_pawn_owns_speed(self):
        tick = CPP.split("void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)", 1)[1].split(
            "void ATSTSSExplorerCharacter::EndPlay(", 1
        )[0]
        self.assertIn("TryEnderPIEWalkRunControls();", tick)
        self.assertIn("bReviewNamespace", tick)
        self.assertIn("World->WorldType == EWorldType::PIE", tick)
        self.assertIn("World->GetNetMode() == NM_Standalone", tick)
        self.assertIn("bFirstWakeThirdPersonReview", tick)
        self.assertIn("IsPlayerControlled()", tick)
        self.assertIn("TSTSS_ENDER_PIE_VELOCITY_BAND", tick)
        self.assertIn("LastEnderPIEMotionBand", tick)
        self.assertTrue(holds_lease(CPP))

    def test_mutations_remove_critical_scope_or_owner_guards(self):
        block = controls(CPP)
        for required in (
            "bEnableEnderPIEWalkRunControls",
            "bFirstWakeThirdPersonReview", "IsPlayerControlled()",
            "World->WorldType == EWorldType::PIE",
            "World->GetNetMode() == NM_Standalone",
            'TEXT("/Game/TSTSS/Review/")',
            'Scene != TEXT("VS02_AureateInteriors")',
            "FMath::IsFinite(PriorSpeed)",
            "PriorSpeed < 180.f", "PriorSpeed > 900.f",
            "EnderPIELastAssignedMaxWalkSpeed",
            "PC->IsMoveInputIgnored()",
            "IsHilltoniaFlyerOpen()",
            "EngineFocusPreviewCamera.IsValid()",
            "WalkSpeedCmS = 260.f",
            "RunSpeedCmS = 480.f",
            "movement_owner_changed",
        ):
            with self.subTest(gate=required):
                altered = CPP.replace(block, block.replace(required, "/* removed */"), 1)
                self.assertFalse(holds_lease(altered))


if __name__ == "__main__":
    unittest.main()
