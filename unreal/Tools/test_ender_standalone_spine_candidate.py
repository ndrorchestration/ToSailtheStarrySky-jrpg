"""Guard for an explicit private-only noncanonical spine-candidate comparison."""
from pathlib import Path
import unittest
CPP=(Path(__file__).resolve().parents[1]/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")

def admitted(src):
    try:
        p=src.split("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",1)[1].split("void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()",1)[0]
        candidate=p.split("// Private spine-fix candidate comparison:",1)[1].split("const bool bAnyRootMotion",1)[0]
        return all(x in candidate for x in (
            'IsPrivateEnderStandaloneAnimation(World, this)',
            'TEXT("TSTSSPrivateEnderSpineFixV1")',
            'bAllowEnderPIERootMotionExtractionReview',
            'Animations_SpineFixV1_PRIVATE/MF_Unarmed_Walk_Fwd_EnderSpineFixV1_PRIVATE',
            'Animations_SpineFixV1_PRIVATE/MF_Unarmed_Jog_Fwd_EnderSpineFixV1_PRIVATE',
            '!IsValid(CandidateWalk)', '!IsValid(CandidateRun)', 'return;',
            'Walk = CandidateWalk', 'Run = CandidateRun',
        )) and all(x in p for x in (
            'bSpineFixCandidate &&', 'Walk->GetPathName() ==',
            'Run->GetPathName() ==', 'Walk->GetSkeleton() != BoundSkeleton',
            'Run->GetSkeleton() != BoundSkeleton', 'ERootMotionMode::IgnoreRootMotion',
            'CurrentNode->GetCurrentAsset() != PreviouslyRequested',
        ))
    except IndexError:
        return False

class CandidateGuardTests(unittest.TestCase):
    def test_only_explicit_private_candidate_is_admitted(self):
        self.assertTrue(admitted(CPP), "Private corrective-candidate review path is absent")

    def test_guard_removals_are_rejected(self):
        self.assertTrue(admitted(CPP))
        for gate in ('TSTSSPrivateEnderSpineFixV1',
                     'IsPrivateEnderStandaloneAnimation(World, this)',
                     'bAllowEnderPIERootMotionExtractionReview',
                     '!IsValid(CandidateWalk)', '!IsValid(CandidateRun)',
                     'bSpineFixCandidate &&',
                     'Walk->GetSkeleton() != BoundSkeleton',
                     'Run->GetSkeleton() != BoundSkeleton',
                     'CurrentNode->GetCurrentAsset() != PreviouslyRequested'):
            with self.subTest(gate=gate):
                self.assertFalse(admitted(CPP.replace(gate, 'REMOVED_GUARD')))

if __name__=="__main__":
    unittest.main()
