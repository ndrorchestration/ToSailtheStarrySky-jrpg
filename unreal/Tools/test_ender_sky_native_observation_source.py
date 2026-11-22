"""Source-only safety checks for private Ender sky observation and K travel.
Not a C++ build, native PIE run, screenshot, or animation proof.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
TICK = SOURCE.split("void ATSTSSExplorerCharacter::Tick(",1)[1].split(
    "void ATSTSSExplorerCharacter::",1)[0]
SAMPLE = TICK.split("// One read-only observation AFTER possession",1)[1].split(
    "// Measure only the exact private Ender ship pawn.",1)[0]
PROBE = TICK.split("// Review-only native K input, not a simulated launch/landing grant.",1)[1].split(
    "// Explicitly flagged editor-built -game title preview:",1)[0]

class EnderSkyObservation(unittest.TestCase):
    def test_sample_is_one_shot_and_scope_locked(self):
        checks = [
            "!bEnderPIEPossessionLogged", 'World->WorldType == EWorldType::PIE',
            'World->GetNetMode() == NM_Standalone', 'UEDPIE_',
            '_VS03_FirstWakeSky', 'Scene == TEXT("VS03_FirstWakeSky")',
            'TSTSSPrivateEnderSkyContinuityReview',
            'BP_EnderLocomotionPreview_NONCANONICAL_C',
            'ETSTSSFirstWakeBeat::Launched',
            'FirstWakeState->AreInspectionsComplete()',
            'World->GetTimeSeconds() >= 0.5f']
        for check in checks:
            with self.subTest(check=check): self.assertIn(check,SAMPLE)
        self.assertEqual(SAMPLE.count("bEnderPIEPossessionLogged = true;"),1)

    def test_sample_logs_actual_values_not_asserted_success(self):
        for check in ["PC->GetPawn() == this", "PC->GetViewTarget() == this",
                      "Body->IsRegistered()", "Body->GetSkeletalMeshAsset()",
                      "Body->GetNumBones() >= 80", "Body->IsVisible()",
                      "bFirstWakeThirdPersonReview", "FollowCamera->IsActive()",
                      "MovementMode == MOVE_Flying"]:
            with self.subTest(check=check): self.assertIn(check,SAMPLE)
        self.assertIn("TSTSS_PRIVATE_ENDER_SKY_OBSERVATION",SAMPLE)
        self.assertIn("animation_NOT_VERIFIED visual_NOT_APPROVED",SAMPLE)
        for forbidden in ["AdvanceTo(", "QueueShore(", "OpenLevel(", "SaveGameToSlot(",
                          "SetSkeletalMeshAsset(", "SetMovementMode(", "PC->Possess("]:
            self.assertNotIn(forbidden,SAMPLE)

    def test_launch_protected_by_two_explicit_flags_and_actual_input_key(self):
        for check in ["TSTSSPrivateLaunchInputProbe",
                      "TSTSSPrivateEnderSkyContinuityReview",
                      "bEarnedPrivateSkeletalSkyTransit",
                      'EndsWith(TEXT("_VS03_FirstWakeSky"))',
                      "BP_EnderLocomotionPreview_NONCANONICAL_C",
                      "FirstWakeState->AreInspectionsComplete()",
                      "bFirstWakeThirdPersonReview",
                      "GetMesh()->GetNumBones() >= 80",
                      "GetMesh()->IsVisible()",
                      "FirstWakeState->GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched",
                      "World->GetTimeSeconds() >= 6.f",
                      "PC->InputKey(FInputKeyEventArgs(",
                      "EKeys::K, IE_Pressed"]:
            with self.subTest(check=check): self.assertIn(check, PROBE)
        self.assertIn("bPrivateLaunchKDispatched = true",PROBE)
        self.assertNotIn("FirstWakeState->AdvanceTo(",PROBE)
        self.assertNotIn("UGameplayStatics::OpenLevel(",PROBE)

    def test_old_default_observer_still_has_own_sky_condition(self):
        self.assertIn("GetClass() == ATSTSSExplorerCharacter::StaticClass() ||", PROBE)
        self.assertIn("bEarnedPrivateSkeletalSkyTransit)", PROBE)
        self.assertIn('Scene == TEXT("VS03_FirstWakeSky") &&',PROBE)

    def test_private_k_mutation_checks_reject_missing_critical_gates(self):
        private = PROBE.split("const bool bEarnedPrivateSkeletalSkyTransit =",1)[1].split(
            "const bool bEarnedSkyTransit =",1)[0]
        gates = [
            "TSTSSPrivateEnderSkyContinuityReview", "FirstWakeState->AreInspectionsComplete()",
            'EndsWith(TEXT("_VS03_FirstWakeSky"))', "GetMesh()->GetNumBones() >= 80",
            "GetMesh()->IsVisible()", "BP_EnderLocomotionPreview_NONCANONICAL_C"]
        for gate in gates:
            with self.subTest(gate=gate):
                self.assertIn(gate,private)
                damaged=private.replace(gate, "REMOVED",1)
                self.assertFalse(all(g in damaged for g in gates))

    def test_no_unverified_native_claim(self):
        self.assertNotIn("native_PASS",SAMPLE)
        self.assertNotIn("visual_APPROVED",SAMPLE)
        self.assertNotIn("animation_VERIFIED",SAMPLE)

if __name__ == "__main__":
    unittest.main()
