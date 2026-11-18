"""Fail-closed source contract for editor-only PRIVATE PIE sprint-edge probe.
This diagnostic does not test real keyboard input, animations, or visuals.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")

def block(text):
    return text.split("bool ATSTSSExplorerCharacter::ProbePrivatePIESprintEdge(", 1)[1].split(
        "void ATSTSSExplorerCharacter::PressEnderPIEReviewSprint()", 1
    )[0]

GATES = (
    "#if WITH_EDITOR",
    'TEXT("TSTSSPrivateEnderSprintProbe")',
    "World->WorldType != EWorldType::PIE",
    "World->GetNetMode() != NM_Standalone",
    'TEXT("/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/")',
    'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
    'TEXT("BP_EnderLocomotionPreview_NONCANONICAL_C")',
    "!bEnableEnderPIEWalkRunControls",
    "!bFirstWakeThirdPersonReview",
    "!IsPlayerControlled()",
    "PC->IsMoveInputIgnored()",
    "IsHilltoniaFlyerOpen()",
    "EngineFocusPreviewCamera.IsValid()",
    "Movement->IsMovingOnGround()",
    "!bEnderPIEWalkRunActive",
    "bEnderPIESprintHeld == bPressed",
    "PressEnderPIEReviewSprint();",
    "ReleaseEnderPIEReviewSprint();",
    "Movement->MaxWalkSpeed",
    "bPressed ? 600.f : 260.f",
    "synthetic_action_not_keyboard=1",
    "#else",
    "return false;",
    "#endif",
)

def scope_passes(src):
    b = block(src)
    # These fragments legitimately appear twice: testing only presence
    # would miss deleting one of the two independent safety behaviors.
    repeated = {"#if WITH_EDITOR": 2, "Movement->MaxWalkSpeed": 2, "return false;": 2}
    return all(b.count(x) >= repeated.get(x, 1) for x in GATES)

class PrivatePIESprintEdgeSourceContract(unittest.TestCase):
    def test_ue_reflected_diagnostic_not_a_normal_key_binding(self):
        self.assertIn("UFUNCTION(BlueprintCallable, Category=\"TSTSS|Ender|PrivatePIE\", meta=(DevelopmentOnly))", HEADER)
        self.assertIn("bool ProbePrivatePIESprintEdge(bool bPressed);", HEADER)
        self.assertIn("bool ATSTSSExplorerCharacter::ProbePrivatePIESprintEdge(bool bPressed)", CPP)
        self.assertTrue(scope_passes(CPP))
        setup = CPP.split("void ATSTSSExplorerCharacter::SetupPlayerInputComponent(", 1)[1].split(
            "void ATSTSSExplorerCharacter::MoveForward(", 1)[0]
        self.assertNotIn("ProbePrivatePIESprintEdge(", setup)
        self.assertIn('BindAction(TEXT("EnderPIEReviewSprint"), IE_Pressed', setup)
        self.assertIn('BindAction(TEXT("EnderPIEReviewSprint"), IE_Released', setup)

    def test_diagnostic_has_no_asset_story_or_movement_custody(self):
        b = block(CPP)
        for forbidden in (
            "SaveGameToSlot(", "LoadGameFromSlot(", "OpenLevel(", "AdvanceTo(",
            "SetActorLocation(", "TeleportTo(", "AddMovementInput(",
            "LoadObject<", "SetSkeletalMeshAsset(", "SetStaticMesh(",
            "SetFieldOfView(", "SetActorTransform(",
        ):
            with self.subTest(operation=forbidden):
                self.assertNotIn(forbidden, b)

    def test_all_admission_guards_survive_negative_mutations(self):
        b = block(CPP)
        for guard in GATES:
            with self.subTest(guard=guard):
                mutated = CPP.replace(b, b.replace(guard, "REMOVED", 1), 1)
                self.assertFalse(scope_passes(mutated))

    def test_explicit_editor_only_false_non_editor_route(self):
        b = block(CPP)
        self.assertIn("#if WITH_EDITOR", b)
        self.assertIn("#else\n    (void)bPressed;\n    return false;\n#endif", b)
        self.assertIn("synthetic_action_not_keyboard=1 art_NOT_APPROVED", b)
        self.assertNotIn("keyboard_VERIFIED", b)
        self.assertNotIn("playback_VERIFIED", b)

if __name__ == "__main__":
    unittest.main()
