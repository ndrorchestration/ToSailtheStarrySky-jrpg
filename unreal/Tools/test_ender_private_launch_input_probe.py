"""Source-only bounds for the private First Wake K input-route diagnostic.
Native PIE receipt is separately required; source assertions alone prove no gameplay.
"""
from pathlib import Path
import unittest

U=Path(__file__).resolve().parents[1]
CPP=(U/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
H=(U/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
B=CPP.split("// Review-only native K input, not a simulated launch/landing grant.",1)[1].split("// Explicitly flagged editor-built -game title preview:",1)[0]

class PrivateLaunchInputContract(unittest.TestCase):
    def test_explicit_unique_flag_and_private_pie(self):
        self.assertEqual(B.count("TSTSSPrivateLaunchInputProbe"),1)
        for token in ("World->WorldType == EWorldType::PIE",
                      "World->GetNetMode() == NM_Standalone",
                      "bReviewNamespace",
                      '"/Game/TSTSS/Review/VerticalSlice/UEDPIE_"',
                      "IsPlayerControlled()"):
            self.assertIn(token,B)

    def test_ship_must_have_exact_private_ender_and_earned_signoff(self):
        for token in ('Scene == TEXT("VS02_AureateInteriors")',
                      "GetClass()->GetPathName() ==",
                      "BP_EnderLocomotionPreview_NONCANONICAL_C",
                      "ETSTSSFirstWakeBeat::EngineeringChecked",
                      "FirstWakeState->AreInspectionsComplete()"):
            self.assertIn(token,B)

    def test_sky_is_observer_only_and_delayed(self):
        for token in ('Scene == TEXT("VS03_FirstWakeSky")',
                      "GetClass() == ATSTSSExplorerCharacter::StaticClass()",
                      "ETSTSSFirstWakeBeat::Launched",
                      "World->GetTimeSeconds() >= 6.f"):
            self.assertIn(token,B)
        self.assertNotIn("VS04_SplashdownSea",B)

    def test_native_action_not_direct_story_or_physics(self):
        self.assertEqual(B.count("PC->InputKey("),1)
        self.assertIn("EKeys::K, IE_Pressed",B)
        for forbidden in ("AdvanceTo(", "AdvanceWaterBeat(", "QueueShore(", "OpenLevel(",
                          "SetActorLocation(", "TeleportTo(", "SaveGame", "SetSimulatePhysics("):
            self.assertNotIn(forbidden,B)

    def test_single_use_and_inert_by_default(self):
        self.assertIn("bool bPrivateLaunchKDispatched = false;",H)
        self.assertIn("!bPrivateLaunchKDispatched",B)
        self.assertIn("bPrivateLaunchKDispatched = true;",B)
        self.assertIn("return;",B.split("PC->InputKey(",1)[1])
        self.assertIn('BindAction(TEXT("ReviewShoreTravel"), IE_Pressed,',CPP)
        self.assertIn("this, &ATSTSSExplorerCharacter::ReviewShoreTravel);",CPP)
        self.assertIn('ActionName="ReviewShoreTravel",Key=K',
                      (U/"Config/DefaultInput.ini").read_text(encoding="utf-8"))

    def test_editor_only_scope(self):
        prefix=CPP.split("// Review-only native K input, not a simulated launch/landing grant.",1)[0]
        tick=prefix.index("void ATSTSSExplorerCharacter::Tick(")
        self.assertIn("#if WITH_EDITOR",prefix[tick:])
        self.assertIn("TSTSS_PRIVATE_LAUNCH_K_PROBE",B)

if __name__=="__main__":
    unittest.main()
