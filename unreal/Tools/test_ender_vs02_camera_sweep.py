"""Source contracts for exact-private VS02 camera-sweep diagnostics only."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
HEADER = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")

def diagnostic(src: str) -> str:
    return src.split("// Measure the private standalone ship camera", 1)[1].split(
        "    if (bTryHilltoniaOpening)", 1)[0]

def admitted(src: str) -> bool:
    return all(token in diagnostic(src) for token in (
        '!bEnderCameraSweepLogged', 'Scene == TEXT("VS02_AureateInteriors")',
        'bPrivateStandaloneShipWorld',
        'FParse::Param(FCommandLine::Get(), TEXT("TSTSSPrivateEnderCameraSweep"))',
        'BP_EnderLocomotionPreview_NONCANONICAL_C', 'IsValid(CameraBoom)',
        'IsValid(FollowCamera)', 'EnderCameraSweepElapsed >= 3.f'))

class CameraSweepSourceTest(unittest.TestCase):
    def test_private_admission(self):
        self.assertTrue(admitted(CPP))
        self.assertIn('const bool bPrivateStandaloneShipWorld = IsPrivateEnderStandaloneShip(World);', CPP)
        self.assertIn('float EnderCameraSweepElapsed = 0.f;', HEADER)
        self.assertIn('bool bEnderCameraSweepLogged = false;', HEADER)

    def test_negative_scope_mutation(self):
        for token in ('bPrivateStandaloneShipWorld',
                      'TSTSSPrivateEnderCameraSweep',
                      'Scene == TEXT("VS02_AureateInteriors")'):
            with self.subTest(token=token):
                body = diagnostic(CPP)
                mutated = CPP.replace(body, body.replace(token, 'REMOVED_GUARD', 1), 1)
                self.assertFalse(admitted(mutated))

    def test_matching_sphere_probe_and_collision_state(self):
        body = diagnostic(CPP)
        for token in ('GetUnfixedCameraPosition()', 'IsCollisionFixApplied()',
                      'SweepSingleByChannel(', 'CameraBoom->ProbeChannel',
                      'FCollisionShape::MakeSphere(CameraBoom->ProbeSize)',
                      'hit_component=%s'):
            self.assertIn(token, body)

    def test_no_camera_or_gameplay_writes(self):
        body = diagnostic(CPP)
        for forbidden in ('SetActorLocation(', 'SetWorldLocation(',
                          'TargetArmLength =', 'ProbeSize =', 'SetCollision',
                          'SaveGame', 'AcceptHilltoniaFlyer(', 'SetViewTarget'):
            self.assertNotIn(forbidden, body)

if __name__ == '__main__':
    unittest.main()
