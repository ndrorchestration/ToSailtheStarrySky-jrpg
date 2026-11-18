"""Ender editor-only optional hair, goggles and staff presentation source contract.

All visual assets remain private and OFF by default. Passing these tests does not
establish Unreal compilation, accessory fit, valid game license, PIE or art approval.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")


def review_appearance(src):
    return src.split("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", 1)[1].split(
        "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(", 1
    )[0]


def bounded(src):
    part = review_appearance(src)
    before = part.split("const auto AttachEnderReviewPart =", 1)[0]
    attach = part.split("const auto AttachEnderReviewPart =", 1)[1]
    return all(s in before for s in (
        "World->WorldType != EWorldType::PIE",
        "World->GetNetMode() != NM_Standalone",
        "EnderSliceReviewBody.IsNull()",
        'Scene != TEXT("VS02_AureateInteriors")',
        "Body->SetSkeletalMeshAsset(Candidate)",
    )) and all(s in attach for s in (
        "if (!bEnabled) return;",
        "Asset.IsNull()",
        "Bone.IsNone()",
        "Body->DoesSocketExist(Bone)",
        "Offset.ContainsNaN()",
        "Asset.LoadSynchronous()",
        "if (!IsValid(Part))",
        "SnapToTargetNotIncludingScale",
        "Preview->SetRelativeTransform(Offset)",
        "Preview->SetVisibility(true)",
        "TSTSS_ENDER_ACCESSORY_HOLD",
        "fit_NOT_VERIFIED art_NOT_APPROVED",
    ))


class EnderAccessorySourceTests(unittest.TestCase):
    def test_three_components_are_editor_only_hidden_and_nonblocking(self):
        ctor = CPP.split("ATSTSSExplorerCharacter::ATSTSSExplorerCharacter()", 1)[1].split(
            "void ATSTSSExplorerCharacter::BeginPlay()", 1
        )[0]
        self.assertIn("#if WITH_EDITOR", ctor)
        for kind in ("Hair", "Goggles", "Staff"):
            self.assertIn(f'EnderSlice{kind}_REVIEW_ONLY', ctor)
            self.assertIn(f"EnderReview{kind}Component", HDR)
            self.assertIn(f"bShowEnderReview{kind} = false;", HDR)
            self.assertIn(f"EnderSliceReview{kind}", HDR)
        self.assertIn("Part->SetVisibility(false);", ctor)
        self.assertIn("Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);", ctor)
        self.assertIn("Part->SetGenerateOverlapEvents(false);", ctor)
        self.assertIn("#if WITH_EDITORONLY_DATA", HDR)
        self.assertTrue(bounded(CPP))

    def test_review_uses_actual_existing_skeletal_pawn_and_no_authority_changes(self):
        block = review_appearance(CPP)
        self.assertLess(block.index("Body->SetSkeletalMeshAsset(Candidate)"),
                        block.index("const auto AttachEnderReviewPart ="))
        for kind in ("HAIR", "GOGGLES", "STAFF"):
            self.assertIn(f'TEXT("{kind}")', block)
        for forbidden in ("SaveGameToSlot(", "OpenLevel(", "AdvanceTo(",
                          "SetMovementMode(", "SetActorLocation(",
                          "SpawnActor<", "CreateDefaultSubobject<"):
            self.assertNotIn(forbidden, block)
        self.assertNotIn("Genesis9MergedFBXRigReview_20261109_NONCANONICAL", block)

    def test_mutations_are_detected_in_real_attachment_function(self):
        block = review_appearance(CPP)
        for required in ("if (!bEnabled) return;", "Asset.IsNull()",
                         "Body->DoesSocketExist(Bone)", "Offset.ContainsNaN()",
                         "if (!IsValid(Part))", "Preview->SetVisibility(true)",
                         "fit_NOT_VERIFIED art_NOT_APPROVED"):
            with self.subTest(required=required):
                damaged = CPP.replace(block, block.replace(required, "/* removed */"), 1)
                self.assertFalse(bounded(damaged))


if __name__ == "__main__":
    unittest.main()
