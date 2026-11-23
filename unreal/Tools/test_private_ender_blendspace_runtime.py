"""Source guards for new draft-only Ender private AnimBP runtime lease."""
import unittest
from pathlib import Path
TEXT=(Path(__file__).resolve().parents[1]/
 "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
H=(Path(__file__).resolve().parents[1]/
 "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
KEY="void ATSTSSExplorerCharacter::TryEnderPrivateBlendSpaceReview(uint8 MotionBand)"
assert TEXT.count(KEY)==1
METHOD=TEXT.split(KEY,1)[1].split("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",1)[0]
BASE=TEXT.split("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",1)[1].split("void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()",1)[0]

class PrivateEnderBlendSpaceRuntimeTest(unittest.TestCase):
 def test_only_opt_in_private_lease(self):
  for guard in ("TSTSSPrivateEnderAnimationReview","TSTSSPrivateEnderSpineFixV1",
   "TSTSSPrivateEnderBlendSpaceV1","IsPrivateEnderStandaloneAnimation(World, this)",
   "bAllowEnderPIERootMotionExtractionReview","IsPlayerControlled()",
   "World->WorldType != EWorldType::Game","World->WorldType != EWorldType::PIE"):
   with self.subTest(guard=guard):self.assertIn(guard,METHOD)
 def test_exact_local_ignored_binary_assets(self):
  for part in ("BlendReview_PRIVATE/ABP_EnderIdleWalkRun_V1_PRIVATE",
   "BlendReview_PRIVATE/BS_EnderIdleWalkRun_V1_NONCANONICAL",
   "ABP_EnderIdleWalkRun_V1_PRIVATE_C","UBlendSpace1D","LoadClass<UAnimInstance>"):
   with self.subTest(part=part):self.assertIn(part,METHOD)
  self.assertNotIn("LoadObject<UAnimSequence>",METHOD)
 def test_animation_owner_and_skeleton_never_overridden(self):
  for guard in ("Body->GetSkeletalMeshAsset() != EnderSliceReviewBody.Get()",
   "Body->GetAnimClass() != nullptr","Body->GetAnimInstance() != nullptr",
   "Body->GetAnimationMode() != EAnimationMode::AnimationBlueprint",
   "Blend->GetSkeleton() != Skeleton","Candidate->GetPathName() != ExactClassPath",
   "Body->GetAnimClass()->GetPathName() != ExactClassPath",
   "animation_owner_changed"):
   with self.subTest(guard=guard):self.assertIn(guard,METHOD)
 def test_transient_only_with_root_motion_ignore(self):
  self.assertIn("Body->SetAnimInstanceClass(Candidate);",METHOD)
  self.assertIn("Active->SetRootMotionMode(ERootMotionMode::IgnoreRootMotion);",METHOD)
  self.assertIn("FindFProperty<FDoubleProperty>(Candidate, TEXT(\"SpeedCmS\"))",METHOD)
  for forbidden in ("OpenLevel(","SaveGame(","LoadGameFromSlot(","SetActorLocation(",
    "SetWorldLocation(","Body->PlayAnimation("):
    self.assertNotIn(forbidden,METHOD)
 def test_flag_preempts_legacy_without_fallback(self):
  guard=BASE.split("if (!bEnderPIEAnimPreviewChecked)",1)[0]
  self.assertIn("if (FParse::Param(FCommandLine::Get(), TEXT(\"TSTSSPrivateEnderBlendSpaceV1\")))",guard)
  self.assertIn("TryEnderPrivateBlendSpaceReview(MotionBand);",guard)
  self.assertIn("return;",guard)
  self.assertIn("Body->PlayAnimation(Next, true);",BASE)
 def test_private_scope_never_authorizes_production(self):
  self.assertIn("IsPrivateEnderPIESpineFixBinding",TEXT)
  self.assertIn("BP_EnderLocomotionPreview_NONCANONICAL_C",TEXT)
  self.assertIn("FirstWake_PreludeInteraction_V5_VisualReview",TEXT)
  self.assertIn("VS02_AureateInteriors",TEXT)
  self.assertNotIn("Starbourne",METHOD)
 def test_editor_only_fields_and_telemetry(self):
  self.assertIn("#if WITH_EDITOR",H)
  self.assertIn("bool bEnderPrivateBlendReviewChecked = false;",H)
  self.assertIn("bool bEnderPrivateBlendReviewActive = false;",H)
  self.assertIn("TSTSS_ENDER_PRIVATE_BLENDSPACE_BOUND",METHOD)
  self.assertIn("TSTSS_ENDER_PRIVATE_BLENDSPACE_BAND",METHOD)
  self.assertIn("TSTSS_ENDER_PRIVATE_BLENDSPACE_HOLD",METHOD)
 def test_guard_removal_caught(self):
  for val in ("TSTSSPrivateEnderAnimationReview","TSTSSPrivateEnderSpineFixV1",
   "TSTSSPrivateEnderBlendSpaceV1","IsPrivateEnderStandaloneAnimation(World, this)",
   "Body->GetAnimClass() != nullptr","Blend->GetSkeleton() != Skeleton"):
   with self.subTest(val=val):
    self.assertNotIn(val,METHOD.replace(val,"MUTATED",1))
if __name__=="__main__":unittest.main()
