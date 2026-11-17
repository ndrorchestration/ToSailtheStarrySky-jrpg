"""Source-only gate for Ender's actual skeletal pawn versus legacy static lookdev.

This is NOT a UE build, animation playback, visual likeness test, or creator approval.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")


def review_setup(src):
    return src.split(
        "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(", 1
    )[1].split(
        "void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview(", 1
    )[0]


def skeletal_precedes_static(src):
    block = review_setup(src)
    start = block.find("USkeletalMeshComponent* SkeletalBody = GetMesh();")
    fallback = block.find("UStaticMesh* Body =")
    if start < 0 or fallback < 0 or start >= fallback:
        return False
    priority = block[start:fallback]
    return all(x in priority for x in (
        "SkeletalBody->IsRegistered()",
        "SkeletalBody->GetSkeletalMeshAsset()",
        "SkeletalBody->GetNumBones() > 0",
        "SkeletalBody->IsVisible()",
        "TSTSS_ENDER_SKELETAL_REVIEW_PRESENT",
        "return;",
    ))


class EnderSkeletalPriorityTests(unittest.TestCase):
    def test_private_or_review_skeletal_candidate_not_hidden_by_static_mesh(self):
        self.assertTrue(skeletal_precedes_static(SOURCE))
        block = review_setup(SOURCE)
        self.assertLess(
            block.index("TSTSS_ENDER_SKELETAL_REVIEW_PRESENT"),
            block.index("LoadObject<UStaticMesh>"),
        )
        self.assertIn("animation_NOT_VERIFIED art_NOT_APPROVED", block)

    def test_skeleton_priority_is_scoped_to_existing_review_maps(self):
        block = review_setup(SOURCE)
        self.assertIn('World->GetNetMode() != NM_Standalone', block)
        self.assertIn('World->WorldType != EWorldType::PIE', block)
        self.assertIn('World->WorldType != EWorldType::Game', block)
        self.assertIn('StartsWith(TEXT("/Game/TSTSS/Review/"))', block)
        self.assertIn('Scene != TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', block)
        self.assertIn('Scene != TEXT("VS02_AureateInteriors")', block)
        self.assertIn(
            "#if WITH_EDITOR\\nvoid ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()",
            SOURCE,
        )
        editor_segment = SOURCE.split(
            "void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", 1
        )[1].split(
            "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(", 1
        )[0]
        self.assertNotIn("#endif", editor_segment)

    def test_fallback_retains_existing_provisional_static_lookdev(self):
        block = review_setup(SOURCE)
        self.assertIn("FPackageName::RegisterMountPoint", block)
        self.assertIn("Visual->SetStaticMesh(Body)", block)
        self.assertIn("Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision)", block)
        self.assertIn("AddInstanceComponent(Visual)", block)
        self.assertIn("static_lookdev=1", block)
        for forbidden in ("AdvanceTo(", "SaveGameToSlot(", "OpenLevel(", "SetSkeletalMeshAsset("):
            self.assertNotIn(forbidden, block)

    def test_mutation_removing_priority_return_is_caught(self):
        block = review_setup(SOURCE)
        priority = block.split("USkeletalMeshComponent* SkeletalBody = GetMesh();", 1)[1].split(
            "// Local Ender V2 look-development package.", 1
        )[0]
        self.assertEqual(priority.count("return;"), 1)
        damaged = SOURCE.replace(priority, priority.replace("return;", "/* missing return */"), 1)
        self.assertFalse(skeletal_precedes_static(damaged))

    def test_mutation_allowing_invalid_or_invisible_skeleton_is_caught(self):
        for guard in (
            "SkeletalBody->IsRegistered()",
            "SkeletalBody->GetSkeletalMeshAsset()",
            "SkeletalBody->GetNumBones() > 0",
            "SkeletalBody->IsVisible()",
        ):
            with self.subTest(guard=guard):
                self.assertFalse(skeletal_precedes_static(SOURCE.replace(
                    guard, "/* missing skeletal eligibility */", 1
                )))


if __name__ == "__main__":
    unittest.main()
