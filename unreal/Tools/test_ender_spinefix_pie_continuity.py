"""Exact private PIE admission for the proven noncanonical spine-corrected
Ender locomotion clips. No production character/ship/world authorization.
"""
import unittest
from pathlib import Path

R=Path(__file__).resolve().parents[1]
CPP=(R/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HELPER=CPP.split("bool IsPrivateEnderPIESpineFixBinding(",1)[1].split(
    "bool IsPrivateEnderStandaloneAnimation(",1)[0]
OLD=CPP.split("bool IsPrivateEnderStandaloneAnimation(",1)[1].split(
    "void ApplyCoastalRecoveryReviewSignage(",1)[0]
ANIM=CPP.split("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",1)[1].split(
    "void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()",1)[0]

class ExactPIESpineFixContinuity(unittest.TestCase):
    def test_two_explicit_flags_and_exclusively_editor_pie(self):
        for token in ('World->WorldType != EWorldType::PIE',
                      'World->GetNetMode() != NM_Standalone',
                      'TSTSSPrivateEnderAnimationReview',
                      'TSTSSPrivateEnderSpineFixV1',
                      'BP_EnderLocomotionPreview_NONCANONICAL_C'):
            self.assertIn(token,HELPER)
        self.assertNotIn('WorldType == EWorldType::Game',HELPER)

    def test_exact_pie_package_and_scene_both_required(self):
        for token in (
            '/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/UEDPIE_',
            '_FirstWake_PreludeInteraction_V5_VisualReview',
            'Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            '/Game/TSTSS/Review/VerticalSlice/UEDPIE_',
            '_VS02_AureateInteriors',
            'Scene == TEXT("VS02_AureateInteriors")',
            'Package.StartsWith(', 'Package.EndsWith(',
            'return bPrelude || bInteriors;'):
            self.assertIn(token,HELPER)
        self.assertNotIn('VS03_FirstWakeSky',HELPER)
        self.assertNotIn('VS04_SplashdownSea',HELPER)

    def test_all_gates_fail_if_removed(self):
        for token in ('EWorldType::PIE','NM_Standalone',
                      'TSTSSPrivateEnderAnimationReview',
                      'TSTSSPrivateEnderSpineFixV1',
                      'BP_EnderLocomotionPreview_NONCANONICAL_C',
                      'UEDPIE_', 'Package.EndsWith(',
                      'return bPrelude || bInteriors;'):
            with self.subTest(token=token):
                self.assertNotIn(token,HELPER.replace(token,"MISSING_GUARD"))

    def test_prior_game_review_preserved_and_pie_explicit(self):
        self.assertIn('IsPrivateEnderStandaloneBinding(World, Pawn)',OLD)
        self.assertIn('IsPrivateEnderStandaloneShip(World)',OLD)
        self.assertIn('IsPrivateEnderPIESpineFixBinding(World, Pawn)',OLD)
        self.assertIn('TSTSSPrivateEnderAnimationReview',OLD)
        self.assertNotIn('TSTSSPrivateEnderSpineFixV1',OLD)

    def test_existing_clip_provenance_owner_and_root_extraction_gates(self):
        for token in (
            'IsPrivateEnderStandaloneAnimation(World, this)',
            'TSTSSPrivateEnderSpineFixV1',
            'bAllowEnderPIERootMotionExtractionReview',
            'Animations_SpineFixV1_PRIVATE/MF_Unarmed_Walk_Fwd_EnderSpineFixV1_PRIVATE',
            'Animations_SpineFixV1_PRIVATE/MF_Unarmed_Jog_Fwd_EnderSpineFixV1_PRIVATE',
            'CandidateWalk','CandidateRun',
            'Walk->GetSkeleton() != BoundSkeleton',
            'Run->GetSkeleton() != BoundSkeleton',
            'EnderPIEIdleLoaded = Idle',
            'CurrentNode->GetCurrentAsset() != PreviouslyRequested',
            'ERootMotionMode::IgnoreRootMotion'):
            self.assertIn(token,ANIM)
        for forbidden in ('AdvanceTo(', 'OpenLevel(', 'SaveGame(',
                          'SetActorLocation(', 'SetActorTransform(',
                          'SetSimulatePhysics(', 'SetMovementMode('):
            self.assertNotIn(forbidden,HELPER+OLD)

if __name__=="__main__":unittest.main()
