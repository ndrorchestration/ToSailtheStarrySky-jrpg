"""Source gates for exact private Ender named floor toe trace.

This is telemetry, not a certified planted-foot, inverse-kinematics,
retarget or production locomotion implementation.
"""
import unittest
from pathlib import Path

CPP = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
TAG = 'TSTSS_ENDER_NAMED_FOOT_TRACE'
START = CPP.index('            // Separate opt-in, READ-ONLY collision truth:')
END = CPP.index('    // Only scoped review worlds advertise live interaction.', START)
SCOPE = CPP[START:END]


class NamedToeFloorSourceTests(unittest.TestCase):
    def test_only_private_explicit_grounded_preview(self):
        self.assertEqual(CPP.count('TSTSS_ENDER_NAMED_FOOT_TRACE t='),1)
        for guard in ('bEnderPrivateBlendReviewActive',
                      'TSTSSPrivateEnderNamedFootTraceV1',
                      'TSTSSPrivateEnderFootDetail',
                      'TSTSSPrivateEnderAnimationReview',
                      'TSTSSPrivateEnderSpineFixV1',
                      'TSTSSPrivateEnderBlendSpaceV1'):
            with self.subTest(guard=guard):
                self.assertIn(guard,SCOPE)
        self.assertIn('IsPrivateEnderStandaloneAnimation(World, this)',CPP[:START])

    def test_observes_engine_floor_not_only_foot_height(self):
        for required in ('GetCharacterMovement()->CurrentFloor.HitResult',
                         'World->LineTraceSingleByChannel(',
                         'ECC_Visibility','TraceParams.AddIgnoredActor(this)',
                         'ToeHit.ImpactPoint.Z','GroundHit.GetActor()',
                         'GroundHit.GetComponent()',
                         'ToeHit.GetComponent() == GroundComponent',
                         'ToeHit.GetActor() == GroundActor',
                         'movement_floor_walkable=%d'):
            with self.subTest(required=required):
                self.assertIn(required,SCOPE)

    def test_readonly_and_always_identifies_blocker_as_unverified(self):
        for forbidden in ('SetActorLocation(', 'SetWorldLocation(',
                          'SetAnimationMode(', 'SetAnimInstanceClass(',
                          'PlayAnimation(', 'SavePackage(', 'SpawnActor(',
                          'AddIgnoredComponents(', 'SetCollisionEnabled(',
                          'GEngine->AddOnScreenDebugMessage('):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,SCOPE)
        for field in ('actor=%s','component=%s','floor_actor=%s','floor_component=%s',
                      'match_actor=%d','match_component=%d','hit=%d'):
            self.assertIn(field,SCOPE)


if __name__ == '__main__':
    unittest.main()
