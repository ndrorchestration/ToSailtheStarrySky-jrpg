"""Static admission checks for the editor-only native Enter input probe.

The test cannot establish an actual key event or gameplay outcome. Those require
source-exact native PIE logs, checked separately, with a clean guarded host.
"""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
CPP=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
HEADER=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
BLOCK=CPP.split("// An opt-in diagnostic must exercise the real Enter action binding.",1)[1].split("// Review-only native K input, not a simulated launch/landing grant.",1)[0]


class PrivateFlyerKeyProbeContract(unittest.TestCase):
    def test_single_opt_in_and_private_map(self):
        self.assertEqual(BLOCK.count('TSTSSPrivateFlyerInputProbe'),1)
        self.assertIn('World->WorldType == EWorldType::PIE',BLOCK)
        self.assertIn('World->GetNetMode() == NM_Standalone',BLOCK)
        self.assertIn('Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',BLOCK)
        self.assertIn('UEDPIE_',BLOCK)
        self.assertIn('bReviewNamespace',BLOCK)

    def test_exact_private_pawn_and_possession(self):
        self.assertIn('GetClass()->GetPathName() ==',BLOCK)
        self.assertIn('BP_EnderLocomotionPreview_NONCANONICAL_C',BLOCK)
        self.assertIn('IsPlayerControlled()',BLOCK)
        self.assertIn('bHilltoniaOpeningActive',BLOCK)

    def test_enters_only_when_real_flyer_modal_is_open(self):
        self.assertRegex(BLOCK,r'PrivateFlyerKeyProbePhase\s*==\s*0\s*&&\s*IsHilltoniaFlyerOpen\(\)')
        self.assertIn('PC->PlayerInput',BLOCK)
        self.assertIn('PrivateFlyerKeyProbePhase = 1;',BLOCK)
        self.assertIn('PrivateFlyerKeyProbePhase = 2;',BLOCK)
        self.assertIn('PrivateFlyerKeyProbePhase < 2',BLOCK)
        self.assertIn('uint8 PrivateFlyerKeyProbePhase = 0;',HEADER)

    def test_sends_real_controller_input_not_story_mutation(self):
        self.assertEqual(BLOCK.count('PC->InputKey('),2)
        self.assertIn('EKeys::Enter, IE_Pressed',BLOCK)
        self.assertIn('EKeys::Enter, IE_Released',BLOCK)
        for token in ('AdvanceTo(', 'AcceptHilltoniaFlyer(', 'SetActorLocation(', 'TeleportTo(', 'SaveGame'):
            self.assertNotIn(token,BLOCK)

    def test_flyer_player_binding_unchanged(self):
        self.assertIn('BindAction(TEXT("AcceptHilltoniaFlyer"), IE_Pressed,',CPP)
        self.assertIn('this, &ATSTSSExplorerCharacter::AcceptHilltoniaFlyer);',CPP)
        inp=(ROOT/"Config/DefaultInput.ini").read_text(encoding="utf-8")
        self.assertIn('ActionName="AcceptHilltoniaFlyer",Key=Enter',inp)

    def test_feature_is_strictly_editor_only(self):
        start=CPP.index('void ATSTSSExplorerCharacter::Tick(')
        before=CPP[:CPP.index('// An opt-in diagnostic must exercise the real Enter action binding.')]
        self.assertIn('#if WITH_EDITOR',before[start:])
        self.assertIn('TSTSS_PRIVATE_FLYER_KEY_PROBE',BLOCK)


if __name__=="__main__":
    unittest.main()
