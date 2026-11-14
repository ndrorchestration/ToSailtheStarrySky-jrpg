"""Source-only negative tests for earned O-key optical handoff; not native PIE."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp"
PLAYER=ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
PLAYER_H=ROOT/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h"
GAME=ROOT/"Config/DefaultInput.ini"
class OpticalHandoffSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=SOURCE.read_text(encoding="utf-8")
        cls.player=PLAYER.read_text(encoding="utf-8")
        cls.header=PLAYER_H.read_text(encoding="utf-8")
        cls.ini=GAME.read_text(encoding="utf-8")
    def test_handoff_scope_and_one_use_ticket(self):
        s=self.s.split("bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(",1)[1].split("bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(",1)[0]
        for term in ('World->WorldType != EWorldType::PIE','World->GetNetMode() != NM_Standalone',
                     'bPending','!= ShipName','ETSTSSFirstWakeBeat::EngineeringChecked',
                     '!State->AreInspectionsComplete()','State->IsSeabourneRecoveryLocked()',
                     '!FPackageName::DoesPackageExist(OpticalPackage)',
                     'PendingBeat = State->GetCurrentBeat()',
                     'PendingInspectionMask = State->GetInspectionMask()',
                     'PendingMapPackage = OpticalPackage','bPending = true'):
            self.assertIn(term,s,term)
        for term in ('State->AdvanceTo(', 'State->Restore(', 'SaveProgress(',
                     'LoadProgress(', 'SeaContact', 'FlotationConfirmed',
                     'SetActorLocation(', 'Starbourne'):
            self.assertNotIn(term,s,term)
        self.assertIn('/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview',self.s)
    def test_sailing_route_requires_real_launch(self):
        self.assertIn('SourceMap == ShipName || SourceMap == OpticalName',self.s)
        self.assertIn('!State->AdvanceTo(ETSTSSFirstWakeBeat::Launched)',self.s)
        self.assertIn('SourceMap == ShipName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked',self.s)
        self.assertIn('SourceMap == OpticalName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked',self.s)
        self.assertIn('const bool bHadTicket = bPending;',self.s)
        self.assertIn('bPending = false;',self.s)
    def test_opt_in_input_separate_from_c_and_k(self):
        for name,key in (("ReviewOpticalInspectionTravel","O"),("EngineFocusPreview","C"),("ReviewShoreTravel","K")):
            self.assertEqual(self.ini.count(f'+ActionMappings=(ActionName="{name}",Key={key})'),1)
        self.assertIn('void ReviewOpticalInspectionTravel();',self.header)
        b=self.player.split('void ATSTSSExplorerCharacter::ReviewOpticalInspectionTravel()',1)[1].split('#endif',1)[0]
        self.assertIn('Travel->QueueOpticalInspection(World, FirstWakeState)',b)
        self.assertIn('UGameplayStatics::OpenLevel(this, FName(*Destination))',b)
        self.assertNotIn('State->Restore(',b)
        self.assertNotIn('AdvanceTo(',b)
        self.assertEqual(self.player.count('BindAction(TEXT("ReviewOpticalInspectionTravel"), IE_Pressed'),1)
    def test_prompts_only_follow_earned_arrival_ticket(self):
        region=self.player.split('if (Travel->ConsumeShoreArrival(World, FirstWakeState))',1)[1].split(
            'if (Scene == TEXT("VS03_FirstWakeSky")',1)[0]
        self.assertIn('ETSTSSFirstWakeBeat::EngineeringChecked && GEngine',region)
        self.assertIn('Scene == TEXT("VS02_AureateInteriors")',region)
        self.assertIn('Scene == TEXT("M_EnginePresentationReview")',region)
        self.assertIn('press [C] for 4s',region)
    def test_original_shore_and_save_code_preserved(self):
        for term in ('void ATSTSSExplorerCharacter::ReviewShoreTravel()',
                     'void ATSTSSExplorerCharacter::QuickSave()',
                     'void ATSTSSExplorerCharacter::QuickLoad()',
                     'HasSupportedReviewFooting','TSTSSReviewGrounding::ShouldRecover'):
            self.assertIn(term,self.player,term)
if __name__=="__main__":unittest.main()
