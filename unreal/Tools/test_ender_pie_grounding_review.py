"""Fail-closed source checks for exact opt-in Ender mesh grounding in V5/VS02 PIE."""
import unittest
from pathlib import Path

CPP=(Path(__file__).resolve().parents[1]/
     "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
LEASE=CPP.split("bool IsPrivateEnderPIESpineFixBinding(",1)[1].split(
    "bool IsPrivateEnderStandaloneAnimation(",1)[0]
APPEAR=CPP.split("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()",1)[1].split(
    "void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",1)[0]

class EnderPIEGroundingReview(unittest.TestCase):
    def test_private_pie_grounding_uses_existing_exact_lease(self):
        self.assertIn("const bool bPrivatePIESpineFix = IsPrivateEnderPIESpineFixBinding(World, this);",APPEAR)
        self.assertIn("if ((bPrivateStandalone || bPrivatePIESpineFix) && IsValid(GetCapsuleComponent()) &&",APPEAR)
        self.assertEqual(APPEAR.count("IsPrivateEnderPIESpineFixBinding(World, this)"),1)
        self.assertIn("IsPrivateEnderStandaloneBinding(World, this)",APPEAR)
        self.assertIn("IsPrivateEnderShipBinding(World, this)",APPEAR)

    def test_lease_rejects_ordinary_worlds_and_requires_both_flags(self):
        for guard in ("World->WorldType != EWorldType::PIE",
                      "World->GetNetMode() != NM_Standalone",
                      "TSTSSPrivateEnderAnimationReview",
                      "TSTSSPrivateEnderSpineFixV1",
                      "BP_EnderLocomotionPreview_NONCANONICAL_C"):
            with self.subTest(guard=guard): self.assertIn(guard,LEASE)
        for prohibited in ("VS03_FirstWakeSky","VS04_SplashdownSea",
                           "WorldType == EWorldType::Game"):
            self.assertNotIn(prohibited,LEASE)

    def test_exact_map_package_and_runtime_scene_both_required(self):
        for guard in (
            "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/UEDPIE_",
            "_FirstWake_PreludeInteraction_V5_VisualReview",
            'Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            "/Game/TSTSS/Review/VerticalSlice/UEDPIE_",
            "_VS02_AureateInteriors",
            'Scene == TEXT("VS02_AureateInteriors")',
            "Package.StartsWith(","Package.EndsWith(",
            "return bPrelude || bInteriors;"):
            with self.subTest(guard=guard): self.assertIn(guard,LEASE)

    def test_existing_component_alignment_safety_guards_retained(self):
        for guard in (
            "Body->GetAttachParent() == GetCapsuleComponent()",
            "Body->GetRelativeLocation().IsNearlyZero(0.1f)",
            "Body->GetComponentScale().Equals(FVector(1.f), 0.01f)",
            "HeightCm >= 140.f && HeightCm <= 220.f",
            "Correction >= -120.f && Correction <= -45.f",
            "Body->AddWorldOffset(FVector(0.f, 0.f, Correction))",
            "TSTSS_PRIVATE_ENDER_GROUNDING_REVIEW"):
            with self.subTest(guard=guard): self.assertIn(guard,APPEAR)
        self.assertNotIn("SaveGame(",APPEAR)
        self.assertNotIn("OpenLevel(",APPEAR)

    def test_guard_removals_are_rejected(self):
        required=["World->WorldType != EWorldType::PIE",
                  "TSTSSPrivateEnderAnimationReview",
                  "TSTSSPrivateEnderSpineFixV1",
                  "return bPrelude || bInteriors;"]
        for guard in required:
            with self.subTest(guard=guard):
                self.assertNotIn(guard,LEASE.replace(guard,"REMOVED_GUARD"))
        self.assertNotIn("IsPrivateEnderPIESpineFixBinding(World, this)",
                         APPEAR.replace("IsPrivateEnderPIESpineFixBinding(World, this)","REMOVED_GUARD"))

if __name__=="__main__":unittest.main()
