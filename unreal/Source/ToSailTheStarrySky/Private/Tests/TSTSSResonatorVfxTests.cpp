#include "Misc/AutomationTest.h"
#include "TSTSSResonatorVfxActor.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Engine/DataTable.h"
#include "Review/TSTSSResonatorFocusGameMode.h"
#include "GameFramework/SpectatorPawn.h"
#include "GameFramework/HUD.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSResonatorCueContractTest,
    "TSTSS.Magic.ResonatorCueContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSResonatorCueContractTest::RunTest(const FString& Parameters)
{
    struct FPair { FName Spell; FName Visual; };
    const FPair ApprovedReviewPairs[] = {
        {TEXT("Ender_ResonantPulse"), TEXT("VFX.Ender.ResonantPulse")},
        {TEXT("Ender_Centering"), TEXT("VFX.Ender.Centering")},
        {TEXT("Ender_TuningLance"), TEXT("VFX.Ender.TuningLance")},
        {TEXT("Ender_EchoMend"), TEXT("VFX.Ender.EchoMend")},
        {TEXT("Ender_CorrespondenceThread"), TEXT("VFX.Ender.CorrespondenceThread")},
        {TEXT("Ender_LatticeBreak"), TEXT("VFX.Ender.LatticeBreak")},
        {TEXT("Ender_MindRipple"), TEXT("VFX.Ender.MindRipple")},
        {TEXT("Ender_FocusHarmonic"), TEXT("VFX.Ender.FocusHarmonic")},
        {TEXT("Ender_ConcordanceBurst"), TEXT("VFX.Ender.ConcordanceBurst")},
        {TEXT("Ender_ThoughtChord"), TEXT("VFX.Ender.ThoughtChord")}
    };
    for (const FPair& Pair : ApprovedReviewPairs)
    {
        TestTrue(TEXT("registered review visual"), ATSTSSResonatorVfxActor::IsKnownCue(Pair.Visual));
        FTSTSSBattleSkillCue Accepted;
        Accepted.ActorId = TEXT("Ender");
        Accepted.TargetId = TEXT("Foe");
        Accepted.SkillId = Pair.Spell;
        Accepted.VfxCueId = Pair.Visual;
        TestTrue(TEXT("accepted cue pair"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Accepted));
        Accepted.SkillId = TEXT("UnrelatedSpell");
        TestFalse(TEXT("mismatched spell cannot spawn this cue"),
                  ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Accepted));
    }
    FTSTSSBattleSkillCue Invalid;
    Invalid.ActorId = TEXT("Ender");
    Invalid.TargetId = TEXT("Foe");
    Invalid.SkillId = TEXT("Ender_ResonantPulse");
    Invalid.VfxCueId = TEXT("VFX.Unknown");
    TestFalse(TEXT("unregistered visual denied"), ATSTSSResonatorVfxActor::IsKnownCue(Invalid.VfxCueId));
    TestFalse(TEXT("unregistered visual rejected"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));
    Invalid.VfxCueId = TEXT("VFX.Ender.ResonantPulse");
    Invalid.ActorId = TEXT("Ionia");
    TestFalse(TEXT("other caster denied"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));
    Invalid.ActorId = TEXT("Ender");
    Invalid.TargetId = NAME_None;
    TestFalse(TEXT("missing target denied"), ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Invalid));

    const ATSTSSResonatorFocusGameMode* FocusMode =
        GetDefault<ATSTSSResonatorFocusGameMode>();
    if (!TestNotNull(TEXT("isolated Resonator review GameMode available"),FocusMode))
        return false;
    TestTrue(TEXT("focus review never spawns First Wake explorer pawn"),
        FocusMode->DefaultPawnClass==ASpectatorPawn::StaticClass());
    TestTrue(TEXT("focus review never draws First Wake objective HUD"),
        FocusMode->HUDClass==AHUD::StaticClass());
    TestTrue(TEXT("focus starts players as spectators"),
        FocusMode->IsFocusSpectatorStartEnabled());

    // Focused, ACTUAL turn-authority tests for the two playable Resonator
    // review spells. No arbitrary review light/animation grants a skill.
    FTSTSSCombatant Ender;
    Ender.CharacterId=TEXT("Ender");
    Ender.Health=50; Ender.MaxHealth=50;
    Ender.Resource=30; Ender.MaxResource=30;
    Ender.Attack=2; Ender.Defense=4;
    FTSTSSCombatant Ionia=Ender;
    Ionia.CharacterId=TEXT("Ionia"); Ionia.Defense=6; Ionia.Attack=1;
    FTSTSSCombatant Enemy=Ender;
    Enemy.CharacterId=TEXT("Foe"); Enemy.Health=180; Enemy.MaxHealth=180;
    Enemy.Defense=2; Enemy.Attack=1;
    FTSTSSBattleSkillState Start;
    if (!TestTrue(TEXT("native combat order initialized"),
        FTSTSSCombatTurns::TryBegin({Ender,Enemy,Ionia},
            {TEXT("Ender"),TEXT("Foe"),TEXT("Ionia")},Start.Combat)))
        return false;
    TMap<FName,FName> Sides;
    Sides.Add(TEXT("Ender"),TEXT("Party"));
    Sides.Add(TEXT("Ionia"),TEXT("Party"));
    Sides.Add(TEXT("Foe"),TEXT("Opponents"));
    FTSTSSBattleSkillKnowledge Learned;
    Learned.LearnedByActor.Add(TEXT("Ender"),TSet<FName>{
        TEXT("Ender_Centering"),TEXT("Ender_ResonantPulse")});
    Learned.LearnedByActor.Add(TEXT("Ionia"),TSet<FName>{TEXT("Review_IoniaTap")});
    Learned.LearnedByActor.Add(TEXT("Foe"),TSet<FName>{
        TEXT("Review_FoeStrike"),TEXT("Review_FoeSpell")});
    Learned.MasteryByActor.FindOrAdd(TEXT("Ender")).Add(
        TEXT("ResonanceHarmonic"),1);
    Learned.MasteryByActor.FindOrAdd(TEXT("Foe")).Add(
        TEXT("PsychicPsion"),1);

    FTSTSSBattleSkillRow Centering;
    Centering.SkillId=TEXT("Ender_Centering");
    Centering.Kind=ETSTSSBattleSkillKind::Spell;
    Centering.Admission=ETSTSSBattleSkillAdmission::ReviewExecutable;
    Centering.Target=ETSTSSBattleSkillTarget::Self;
    Centering.Power=0;
    Centering.ResourceCost=5;
    Centering.RequiredSchool=TEXT("ResonanceHarmonic");
    Centering.RequiredMasteryRank=1;
    Centering.bPartyPhysicalDefenseBuff=true;
    Centering.PhysicalDefenseBuffPercent=15;
    Centering.BuffDurationRounds=3;
    Centering.VfxCueId=TEXT("VFX.Ender.Centering");

    FTSTSSBattleSkillRow Pulse;
    Pulse.SkillId=TEXT("Ender_ResonantPulse");
    Pulse.Kind=ETSTSSBattleSkillKind::Spell;
    Pulse.Admission=ETSTSSBattleSkillAdmission::ReviewExecutable;
    Pulse.Target=ETSTSSBattleSkillTarget::Enemy;
    Pulse.Power=6;
    Pulse.ResourceCost=3;
    Pulse.RequiredSchool=TEXT("ResonanceHarmonic");
    Pulse.RequiredMasteryRank=1;
    Pulse.VfxCueId=TEXT("VFX.Ender.ResonantPulse");

    FTSTSSBattleSkillRow FoeStrike;
    FoeStrike.SkillId=TEXT("Review_FoeStrike");
    FoeStrike.Kind=ETSTSSBattleSkillKind::JobArt;
    FoeStrike.Admission=ETSTSSBattleSkillAdmission::ReviewExecutable;
    FoeStrike.Target=ETSTSSBattleSkillTarget::Enemy;
    FoeStrike.Power=7;
    FTSTSSBattleSkillRow IoniaTap=FoeStrike;
    IoniaTap.SkillId=TEXT("Review_IoniaTap");
    IoniaTap.Power=0;
    FTSTSSBattleSkillRow FoeSpell=FoeStrike;
    FoeSpell.SkillId=TEXT("Review_FoeSpell");
    FoeSpell.Kind=ETSTSSBattleSkillKind::Spell;
    FoeSpell.RequiredSchool=TEXT("PsychicPsion");
    FoeSpell.RequiredMasteryRank=1;

    auto Cast=[&](const FTSTSSBattleSkillState& In,
        const TCHAR* Actor,const TCHAR* Target,
        const FTSTSSBattleSkillRow& Spell,
        FTSTSSBattleSkillState& Out) -> bool
    {
        FTSTSSBattleSkillCue Accepted;
        return FTSTSSBattleSkillSystem::TryUseRow(
            In,Learned,Sides,TEXT("Party"),TEXT("Opponents"),
            FName(Actor),FName(Target),Spell.SkillId,Spell,Out,Accepted);
    };

    FTSTSSBattleSkillState DeniedResult;
    FTSTSSBattleSkillCue DeniedCue;
    DeniedCue.VfxCueId=TEXT("PreserveOnDenied");
    FTSTSSBattleSkillRow Unapproved=Centering;
    Unapproved.Admission=ETSTSSBattleSkillAdmission::DesignOnly;
    TestFalse(TEXT("unapproved Centering does not act"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start,Learned,Sides,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),TEXT("Ender"),Centering.SkillId,Unapproved,
            DeniedResult,DeniedCue));
    TestEqual(TEXT("failed spell preserves cue"),
        DeniedCue.VfxCueId,FName(TEXT("PreserveOnDenied")));
    FTSTSSBattleSkillKnowledge NoMastery=Learned;
    NoMastery.MasteryByActor.Remove(TEXT("Ender"));
    TestFalse(TEXT("Centering not auto-granted by job"),
        FTSTSSBattleSkillSystem::TryUseRow(
            Start,NoMastery,Sides,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),TEXT("Ender"),Centering.SkillId,Centering,
            DeniedResult,DeniedCue));
    FTSTSSBattleSkillRow WrongBonus=Centering;
    WrongBonus.PhysicalDefenseBuffPercent=90;
    TestFalse(TEXT("oversized protection cannot be substituted"),
        Cast(Start,TEXT("Ender"),TEXT("Ender"),WrongBonus,DeniedResult));
    FTSTSSBattleSkillRow WrongOwner=Centering;
    TestFalse(TEXT("Centering cannot target another ally as self"),
        Cast(Start,TEXT("Ender"),TEXT("Ionia"),WrongOwner,DeniedResult));
    FTSTSSBattleSkillState Insufficient=Start;
    Insufficient.Combat.Roster[0].Resource=4;
    TestFalse(TEXT("insufficient MP blocks Centering without side effects"),
        Cast(Insufficient,TEXT("Ender"),TEXT("Ender"),Centering,DeniedResult));

    FTSTSSBattleSkillState AfterCentering;
    if (!TestTrue(TEXT("Centering executed through real skill executor"),
        Cast(Start,TEXT("Ender"),TEXT("Ender"),Centering,AfterCentering)))
        return false;
    TestEqual(TEXT("Centering charged exactly 5 MP"),
        AfterCentering.Combat.Roster[0].Resource,25);
    TestEqual(TEXT("Centering does not damage or heal caster"),
        AfterCentering.Combat.Roster[0].Health,50);
    TestEqual(TEXT("Centering advances one turn"),
        AfterCentering.Combat.AcceptedActions,1);
    TestEqual(TEXT("Ender and Ionia buffed, foe not"),
        AfterCentering.ActivePhysicalDefenseBuffs.Num(),2);
    TestTrue(TEXT("Ionia's status exists"),
        AfterCentering.ActivePhysicalDefenseBuffs.Contains(TEXT("Ionia")));
    TestFalse(TEXT("enemy not protected"),
        AfterCentering.ActivePhysicalDefenseBuffs.Contains(TEXT("Foe")));
    TestEqual(TEXT("three rounds retained"),
        AfterCentering.ActivePhysicalDefenseBuffs.FindRef(
            TEXT("Ionia")).ExpiresAtRound-AfterCentering.Combat.Round,3);
    TestEqual(TEXT("base defense never modified"),
        AfterCentering.Combat.Roster[2].Defense,6);

    FTSTSSBattleSkillState AfterFoeStrike;
    if (!TestTrue(TEXT("enemy strikes against Centering physical bonus"),
        Cast(AfterCentering,TEXT("Foe"),TEXT("Ionia"),
            FoeStrike,AfterFoeStrike))) return false;
    TestEqual(TEXT("physical damage reduced by +1 low-level defense"),
        AfterFoeStrike.Combat.Roster[2].Health,49);
    FTSTSSBattleSkillState Unprotected=AfterCentering;
    Unprotected.ActivePhysicalDefenseBuffs.Empty();
    FTSTSSBattleSkillState WithoutBuff;
    if (!TestTrue(TEXT("unbuffed comparison action accepted"),
        Cast(Unprotected,TEXT("Foe"),TEXT("Ionia"),
            FoeStrike,WithoutBuff))) return false;
    TestEqual(TEXT("without Centering physical blow deals 2"),
        WithoutBuff.Combat.Roster[2].Health,48);
    FTSTSSBattleSkillState VsSpell;
    if (!TestTrue(TEXT("enemy magical damage accepted"),
        Cast(AfterCentering,TEXT("Foe"),TEXT("Ionia"),
            FoeSpell,VsSpell))) return false;
    TestEqual(TEXT("Centering cannot protect from magic attack"),
        VsSpell.Combat.Roster[2].Health,48);

    FTSTSSBattleSkillState AfterIonia;
    if (!TestTrue(TEXT("Ionia can advance the authoritative turn"),
        Cast(AfterFoeStrike,TEXT("Ionia"),TEXT("Foe"),
            IoniaTap,AfterIonia))) return false;
    TestEqual(TEXT("full combat round counted"),
        AfterIonia.Combat.Round,2);

    FTSTSSBattleSkillState AfterPulse;
    FTSTSSBattleSkillCue PulseCue;
    TMap<FName,FVector> Positions;
    Positions.Add(TEXT("Ender"),FVector(0.f,0.f,0.f));
    Positions.Add(TEXT("Ionia"),FVector(0.f,150.f,0.f)); // Ally inside sphere.
    Positions.Add(TEXT("Foe"),FVector(450.f,0.f,0.f));
    TArray<FName> PulseTargets;
    TestFalse(TEXT("legacy single-target Pulse MUST NOT execute"),
        FTSTSSBattleSkillSystem::TryUseRow(
            AfterIonia,Learned,Sides,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),TEXT("Foe"),Pulse.SkillId,Pulse,
            AfterPulse,PulseCue));
    if (!TestTrue(TEXT("Resonant Pulse admitted as caster-centered enemy PBAoE"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            AfterIonia,Learned,Sides,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,Positions,AfterPulse,PulseCue,PulseTargets)))
        return false;
    TestEqual(TEXT("Pulse spend exactly 3 MP"),AfterPulse.Combat.Roster[0].Resource,22);
    TestEqual(TEXT("Pulse advances exactly one accepted turn"),
        AfterPulse.Combat.AcceptedActions,AfterIonia.Combat.AcceptedActions+1);
    TestEqual(TEXT("Pulse damages only in-radius enemy"),
        AfterPulse.Combat.Roster[1].Health,173);
    TestEqual(TEXT("Pulse does not hurt Ionia inside sphere"),
        AfterPulse.Combat.Roster[2].Health,AfterIonia.Combat.Roster[2].Health);
    TestEqual(TEXT("one enemy hit in three-combatant review"),PulseTargets.Num(),1);
    TestEqual(TEXT("Pulse exact accepted VFX"),
        PulseCue.VfxCueId,FName(TEXT("VFX.Ender.ResonantPulse")));
    TestTrue(TEXT("Pulse VFX allowed by accepted-cue contract"),
        ATSTSSResonatorVfxActor::IsAcceptedEnderCue(PulseCue));

    FTSTSSBattleSkillState Refresh;
    if (!TestTrue(TEXT("refresh Centering after one round"),
        Cast(AfterIonia,TEXT("Ender"),TEXT("Ender"),
            Centering,Refresh))) return false;
    TestEqual(TEXT("refresh cannot stack second +15 percent"),
        Refresh.ActivePhysicalDefenseBuffs.FindRef(TEXT("Ionia")).Percent,15);
    TestEqual(TEXT("refresh retains only one status per active ally"),
        Refresh.ActivePhysicalDefenseBuffs.Num(),2);
    TestEqual(TEXT("refresh extends to three remaining rounds"),
        Refresh.ActivePhysicalDefenseBuffs.FindRef(
            TEXT("Ionia")).ExpiresAtRound-Refresh.Combat.Round,3);

    FTSTSSBattleSkillState Next=AfterPulse;
    FTSTSSBattleSkillState Temporary;
    for (int32 I=0;I<2;++I)
    {
        if (!TestTrue(TEXT("foe turn advances"),
            Cast(Next,TEXT("Foe"),TEXT("Ionia"),FoeStrike,Temporary))) return false;
        if (!TestTrue(TEXT("Ionia turn advances"),
            Cast(Temporary,TEXT("Ionia"),TEXT("Foe"),IoniaTap,Next))) return false;
        if (I==0)
        {
            FTSTSSBattleSkillCue NextPulseCue;
            TArray<FName> NextPulseTargets;
            if (!TestTrue(TEXT("Ender can recast area Pulse next round"),
                FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
                    Next,Learned,Sides,TEXT("Party"),TEXT("Opponents"),
                    TEXT("Ender"),Pulse,Positions,Temporary,
                    NextPulseCue,NextPulseTargets))) return false;
            Next=MoveTemp(Temporary);
        }
    }
    TestEqual(TEXT("after three rounds the status has expired"),
        Next.Combat.Round,4);
    TestFalse(TEXT("Ionia has no lingering Centering"),
        Next.ActivePhysicalDefenseBuffs.Contains(TEXT("Ionia")));
    TestFalse(TEXT("Ender has no lingering Centering"),
        Next.ActivePhysicalDefenseBuffs.Contains(TEXT("Ender")));

    // Multi-enemy spatial controls: one cost, one turn, never harm allies,
    // never hit out-of-range enemies and reject missing/worldless geometry.
    FTSTSSCombatant Near=Enemy;
    Near.CharacterId=TEXT("FoeNear"); Near.Health=90; Near.MaxHealth=90;
    Near.Defense=1;
    FTSTSSCombatant Far=Near;
    Far.CharacterId=TEXT("FoeFar");
    FTSTSSBattleSkillState WideStart;
    if (!TestTrue(TEXT("wide encounter initialized"),
        FTSTSSCombatTurns::TryBegin(
            {Ender,Ionia,Enemy,Near,Far},
            {TEXT("Ender"),TEXT("Ionia"),TEXT("Foe"),
             TEXT("FoeNear"),TEXT("FoeFar")},WideStart.Combat))) return false;
    TMap<FName,FName> WideFactions=Sides;
    WideFactions.Add(TEXT("FoeNear"),TEXT("Opponents"));
    WideFactions.Add(TEXT("FoeFar"),TEXT("Opponents"));
    TMap<FName,FVector> WidePositions=Positions;
    WidePositions.Add(TEXT("FoeNear"),FVector(0.f,0.f,500.f));
    WidePositions.Add(TEXT("FoeFar"),FVector(601.f,0.f,0.f));
    FTSTSSBattleSkillState WideAfter;
    FTSTSSBattleSkillCue WideCue;
    TArray<FName> WideTargets;
    if (!TestTrue(TEXT("Pulse hits multiple foes from full 3D distance"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            WideStart,Learned,WideFactions,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,WidePositions,WideAfter,WideCue,WideTargets)))
        return false;
    TestEqual(TEXT("two enemies within radius hit"),WideTargets.Num(),2);
    TestEqual(TEXT("stable first target by name"),WideTargets[0],FName(TEXT("Foe")));
    TestEqual(TEXT("Ender MP cost not multiplied by number of foes"),
        WideAfter.Combat.Roster[0].Resource,27);
    TestEqual(TEXT("Pulse accepts one turn with two enemies"),
        WideAfter.Combat.AcceptedActions,1);
    TestEqual(TEXT("Ender own HP unchanged"),WideAfter.Combat.Roster[0].Health,50);
    TestEqual(TEXT("Ionia inside radius takes no damage"),
        WideAfter.Combat.Roster[1].Health,50);
    TestEqual(TEXT("first enemy takes nonphysical 6+2-2 damage"),
        WideAfter.Combat.Roster[2].Health,174);
    TestEqual(TEXT("second in-radius enemy takes full spell damage"),
        WideAfter.Combat.Roster[3].Health,83);
    TestEqual(TEXT("out-of-radius enemy unaffected"),
        WideAfter.Combat.Roster[4].Health,90);

    TMap<FName,FVector> MissingPosition=WidePositions;
    MissingPosition.Remove(TEXT("FoeNear"));
    FTSTSSBattleSkillState Preserved=WideAfter;
    FTSTSSBattleSkillCue PreservedCue;
    PreservedCue.VfxCueId=TEXT("PreservedCue");
    TArray<FName> PreservedTargets{TEXT("Sentinel")};
    TestFalse(TEXT("missing enemy coordinate refuses entire cast"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            WideStart,Learned,WideFactions,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,MissingPosition,Preserved,
            PreservedCue,PreservedTargets));
    TestEqual(TEXT("failed area cast preserves MP ledger"),
        Preserved.Combat.Roster[0].Resource,27);
    TestEqual(TEXT("failed area cast preserves cue"),
        PreservedCue.VfxCueId,FName(TEXT("PreservedCue")));
    TestEqual(TEXT("failed area cast preserves targets"),
        PreservedTargets[0],FName(TEXT("Sentinel")));

    TMap<FName,FVector> OutOfReach=WidePositions;
    OutOfReach.Add(TEXT("Foe"),FVector(601.f,0.f,0.f));
    OutOfReach.Add(TEXT("FoeNear"),FVector(0.f,0.f,601.f));
    TestFalse(TEXT("no in-range enemies must not charge MP or skip a turn"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            WideStart,Learned,WideFactions,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,OutOfReach,Preserved,
            PreservedCue,PreservedTargets));

    FTSTSSBattleSkillKnowledge Unlearned=Learned;
    Unlearned.LearnedByActor.FindOrAdd(TEXT("Ender")).Remove(Pulse.SkillId);
    TestFalse(TEXT("area shape cannot bypass learned skill authorization"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            WideStart,Unlearned,WideFactions,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,WidePositions,Preserved,
            PreservedCue,PreservedTargets));

    FTSTSSBattleSkillState LowMP=WideStart;
    LowMP.Combat.Roster[0].Resource=2;
    TestFalse(TEXT("area spell insufficient MP fails atomically"),
        FTSTSSBattleSkillSystem::TryUseResonantPulseArea(
            LowMP,Learned,WideFactions,TEXT("Party"),TEXT("Opponents"),
            TEXT("Ender"),Pulse,WidePositions,Preserved,
            PreservedCue,PreservedTargets));

    // The public combat-manager component is the production-facing authority.
    // It must report effective defense without forging persistent stats.
    UDataTable* ReviewSkills=NewObject<UDataTable>(GetTransientPackage());
    ReviewSkills->RowStruct=FTSTSSBattleSkillRow::StaticStruct();
    ReviewSkills->AddRow(Centering.SkillId,Centering);
    ReviewSkills->AddRow(Pulse.SkillId,Pulse);
    ReviewSkills->AddRow(IoniaTap.SkillId,IoniaTap);
    ReviewSkills->AddRow(FoeStrike.SkillId,FoeStrike);
    FTSS_CombatParticipant PartyEnder;
    PartyEnder.ParticipantId=TEXT("Ender"); PartyEnder.Stats=Ender;
    PartyEnder.Agility=30; PartyEnder.bIsPlayerParty=true;
    PartyEnder.LearnedSkills={TEXT("Ender_Centering"),TEXT("Ender_ResonantPulse")};
    PartyEnder.MasteryRanks.Add(TEXT("ResonanceHarmonic"),1);
    FTSS_CombatParticipant PartyIonia;
    PartyIonia.ParticipantId=TEXT("Ionia"); PartyIonia.Stats=Ionia;
    PartyIonia.Agility=20; PartyIonia.bIsPlayerParty=true;
    PartyIonia.LearnedSkills={TEXT("Review_IoniaTap")};
    FTSS_CombatParticipant BattleFoe;
    BattleFoe.ParticipantId=TEXT("Foe"); BattleFoe.Stats=Enemy;
    BattleFoe.Agility=10; BattleFoe.bIsPlayerParty=false;
    BattleFoe.LearnedSkills={TEXT("Review_FoeStrike")};
    UTSS_CombatTurnManager* Manager=NewObject<UTSS_CombatTurnManager>(
        GetTransientPackage());
    Manager->SkillTable=ReviewSkills;
    if (!TestTrue(TEXT("manager initializes authorized Ender/Ionia party"),
        Manager->InitializeEncounter({PartyEnder,PartyIonia},
            {TEXT("Ender"),TEXT("Ionia")},{BattleFoe}))) return false;
    FTSS_CombatCommand Cmd;
    Cmd.SourceParticipantId=TEXT("Ender");
    Cmd.TargetParticipantId=TEXT("Ender");
    Cmd.SkillId=Centering.SkillId;
    FTSS_CombatCommand LegacyPulse=Cmd;
    LegacyPulse.SkillId=Pulse.SkillId;
    LegacyPulse.TargetParticipantId=TEXT("Foe");
    TestFalse(TEXT("combat manager disallows legacy targeted Pulse"),
        Manager->SubmitCommand(LegacyPulse));
    if (!TestTrue(TEXT("manager admits Centering on actual turn"),
        Manager->SubmitCommand(Cmd))) return false;
    TestEqual(TEXT("manager reports Ionia's three-round status"),
        Manager->GetCenteringRoundsRemaining(TEXT("Ionia")),3);
    TestEqual(TEXT("manager exposes effective Ionia defense 7"),
        Manager->GetCenteringEffectiveDefense(TEXT("Ionia")),7);
    TestEqual(TEXT("manager never buffs an absent Lyra"),
        Manager->GetCenteringRoundsRemaining(TEXT("Lyra")),0);

    UTSS_CombatTurnManager* PulseManager=NewObject<UTSS_CombatTurnManager>(
        GetTransientPackage());
    PulseManager->SkillTable=ReviewSkills;
    if (!TestTrue(TEXT("separate pulse area manager initialized"),
        PulseManager->InitializeEncounter({PartyEnder,PartyIonia},
            {TEXT("Ender"),TEXT("Ionia")},{BattleFoe}))) return false;
    FTSS_CombatCommand SpatialPulse=LegacyPulse;
    SpatialPulse.TargetParticipantId=TEXT("Ender"); // caster-centered
    if (!TestTrue(TEXT("manager routes admitted caster-centered Pulse area"),
        PulseManager->SubmitResonantPulseArea(SpatialPulse,Positions))) return false;
    TestEqual(TEXT("manager debits only one pulse cost"),
        PulseManager->GetCombatantSnapshot()[0].Resource,27);
    TestEqual(TEXT("manager opponent damaged"),
        PulseManager->GetCombatantSnapshot()[2].Health,174);
    TestEqual(TEXT("manager ally never damaged"),
        PulseManager->GetCombatantSnapshot()[1].Health,50);
    return true;
}

#endif
