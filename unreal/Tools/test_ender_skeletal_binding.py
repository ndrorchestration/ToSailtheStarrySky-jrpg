"""Review-only private Ender skeletal bind, engine-free source/negative controls.

Historical private Genesis 9 meshes/Blueprints are intentionally NOT tracked.
Passing these tests does not establish UHT/UBT compilation, PIE motion,
animation quality, Ender's likeness, or creator approval.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")


def binding(src):
    return src.split("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", 1)[1].split(
        "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(", 1
    )[0]


def eligible(src):
    b = binding(src)
    return all(term in b for term in (
        "World->WorldType != EWorldType::PIE",
        "World->GetNetMode() != NM_Standalone",
        'StartsWith(\n            TEXT("/Game/TSTSS/Review/"))',
        "EnderSliceReviewBody.IsNull()",
        'Scene != TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
        'Scene != TEXT("VS02_AureateInteriors")',
        "IsValid(Candidate->GetSkeleton())",
        "Bones.GetNum() < 80",
        "Bones.GetNum() > 450",
        'Bones.FindBoneIndex(FName(TEXT("head")))',
        'Bones.FindBoneIndex(FName(TEXT("l_hand")))',
        "Body->SetSkeletalMeshAsset(Candidate)",
        "Body->SetVisibility(true)",
    ))


class PrivateEnderSkeletalBindingSourceTests(unittest.TestCase):
    def test_private_unassigned_blueprint_property_is_editor_only(self):
        self.assertIn("class USkeletalMesh;", HDR)
        self.assertIn(
            '#if WITH_EDITORONLY_DATA\n    // Explicitly assigned by a PRIVATE, editor-only review Blueprint.',
            HDR,
        )
        self.assertIn("TSoftObjectPtr<USkeletalMesh> EnderSliceReviewBody;", HDR)
        self.assertIn("void ApplyEnderSliceReviewAppearance();", HDR)
        self.assertNotIn("ConstructorHelpers::FObjectFinder", binding(CPP))
        self.assertNotIn("Genesis9MergedFBXRigReview_20261109_NONCANONICAL", binding(CPP))

    def test_binding_runs_before_third_person_fallback(self):
        begin = CPP.split("void ATSTSSExplorerCharacter::BeginPlay()", 1)[1].split(
            "void ATSTSSExplorerCharacter::Tick(", 1
        )[0] if "void ATSTSSExplorerCharacter::Tick(" in CPP.split("void ATSTSSExplorerCharacter::BeginPlay()", 1)[1] else CPP.split(
            "void ATSTSSExplorerCharacter::BeginPlay()", 1
        )[1].split("bool ATSTSSExplorerCharacter::HasSupportedReviewFooting(", 1)[0]
        self.assertLess(
            begin.index("ApplyEnderSliceReviewAppearance();"),
            begin.index("SetupFirstWakeThirdPersonReview(GetWorld());"),
        )
        self.assertTrue(eligible(CPP))
        self.assertIn("TSTSS_ENDER_SLICE_REVIEW_MESH_BOUND", binding(CPP))
        self.assertIn("animation_NOT_VERIFIED art_NOT_APPROVED", binding(CPP))

    def test_binder_no_story_save_or_map_mutation(self):
        b = binding(CPP)
        for denied in (
            "Advance", "SaveGameToSlot", "SetCurrentBeat",
            "OpenLevel(", "SetActorLocation(", "Rename(",
            "SaveLoadedAsset(", "SetMovementMode(",
        ):
            with self.subTest(denied=denied):
                self.assertNotIn(denied, b)
        self.assertIn("#if WITH_EDITOR\nvoid ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", CPP)

    def test_mutation_dropping_pie_or_review_namespace_is_detected(self):
        for element in (
            "World->WorldType != EWorldType::PIE",
            "World->GetNetMode() != NM_Standalone",
            'StartsWith(\n            TEXT("/Game/TSTSS/Review/"))',
            'Scene != TEXT("VS02_AureateInteriors")',
        ):
            with self.subTest(element=element):
                self.assertFalse(eligible(CPP.replace(element, "/* removed gate */", 1)))

    def test_mutation_dropping_bones_or_actual_mesh_bind_is_detected(self):
        for element in (
            "Bones.GetNum() < 80",
            'Bones.FindBoneIndex(FName(TEXT("head")))',
            'Bones.FindBoneIndex(FName(TEXT("l_hand")))',
            "Body->SetSkeletalMeshAsset(Candidate)",
            "Body->SetVisibility(true)",
        ):
            with self.subTest(element=element):
                self.assertFalse(eligible(CPP.replace(element, "/* removed essential */", 1)))


if __name__ == "__main__":
    unittest.main()
