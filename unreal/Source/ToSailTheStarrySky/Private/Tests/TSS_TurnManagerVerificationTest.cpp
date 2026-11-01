#include "Misc/AutomationTest.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Engine/DataTable.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    FTSS_CombatParticipant MakeUnit(
        const TCHAR* Id, bool bPlayer, int32 Speed, int32 Health=20)
    {
        FTSS_CombatParticipant Unit;
        Unit.ParticipantId = FName(Id);
        Unit.Stats.CharacterId = Unit.ParticipantId;
        Unit.Stats.Health = Health;
        Unit.Stats.MaxHealth = 20;
        Unit.Stats.Resource = 10;
        Unit.Stats.MaxResource = 10;
        Unit.Stats.Attack = 1;
        Unit.bIsPlayerParty = bPlayer;
        Unit.Agility = Speed;
        Unit.LearnedSkills.Add(bPlayer ? FName(TEXT("ReviewStrike")) :
                                        FName(TEXT("ReviewClaw")));
        return Unit;
    }

    UDataTable* MakeReviewTable()
    {
        UDataTable* Table = NewObject<UDataTable>();
        Table->RowStruct = FTSTSSBattleSkillRow::StaticStruct();
        FTSTSSBattleSkillRow Strike;
        Strike.SkillId = TEXT("ReviewStrike");
        Strike.Kind = ETSTSSBattleSkillKind::JobArt;
        Strike.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
        Strike.Power = 3;
        Strike.Target = ETSTSSBattleSkillTarget::Enemy;
        Table->AddRow(Strike.SkillId, Strike);
        FTSTSSBattleSkillRow Claw = Strike;
        Claw.SkillId = TEXT("ReviewClaw");
        Claw.Power = 1;
        Table->AddRow(Claw.SkillId, Claw);
        return Table;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSSTurnManagerInitiativeTest,
    "TSTSS.Combat.InitiativeAndActiveParty",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSSTurnManagerInitiativeTest::RunTest(const FString& Parameters)
{
    UTSS_CombatTurnManager* Manager = NewObject<UTSS_CombatTurnManager>();
    TArray<FTSS_CombatParticipant> Five;
    Five.Add(MakeUnit(TEXT("Ender"), true, 15));
    Five.Add(MakeUnit(TEXT("Ionia"), true, 10));
    Five.Add(MakeUnit(TEXT("Lyra"), true, 20));
    Five.Add(MakeUnit(TEXT("Reson"), true, 12));
    Five.Add(MakeUnit(TEXT("Aepex"), true, 18));
    TArray<FTSS_CombatParticipant> Foes{MakeUnit(TEXT("VoidWatcher"), false, 14)};
    const TArray<FName> Chosen{TEXT("Ender"), TEXT("Ionia"), TEXT("Lyra")};

    TestFalse(TEXT("must explicitly choose three or fewer active"),
        Manager->InitializeEncounter(Five,
            {TEXT("Ender"), TEXT("Ionia"), TEXT("Lyra"), TEXT("Reson")}, Foes));
    TestFalse(TEXT("unknown protagonist cannot join active party"),
        Manager->InitializeEncounter(Five, {TEXT("Talen")}, Foes));
    TestFalse(TEXT("duplicate active player rejected"),
        Manager->InitializeEncounter(Five, {TEXT("Ender"), TEXT("Ender")}, Foes));
    TestEqual(TEXT("failed init leaves phase alone"), Manager->GetCurrentPhase(),
              ETSS_CombatPhase::NotStarted);

    TArray<FTSS_CombatParticipant> Duplicate = Five;
    Duplicate[4].ParticipantId = TEXT("Ender");
    Duplicate[4].Stats.CharacterId = TEXT("Ender");
    TestFalse(TEXT("duplicate roster id rejected"),
        Manager->InitializeEncounter(Duplicate, Chosen, Foes));
    Foes[0].ParticipantId = TEXT("Ender");
    Foes[0].Stats.CharacterId = TEXT("Ender");
    TestFalse(TEXT("enemy cannot impersonate party"),
        Manager->InitializeEncounter(Five, Chosen, Foes));
    Foes[0] = MakeUnit(TEXT("VoidWatcher"), false, 14);

    if (!TestTrue(TEXT("five recruited and three selected initialize"),
        Manager->InitializeEncounter(Five, Chosen, Foes))) return false;
    TestEqual(TEXT("first initiative: Lyra"), Manager->GetActiveParticipantId(),
              FName(TEXT("Lyra")));
    TestEqual(TEXT("only three combatants and one enemy"),
              Manager->GetCombatantSnapshot().Num(), 4);
    TestEqual(TEXT("two reserve members preserved"),
              Manager->GetReservePartyIds().Num(), 2);
    TestTrue(TEXT("Aepex on bench"),
             Manager->GetReservePartyIds().Contains(TEXT("Aepex")));
    TestTrue(TEXT("Reson on bench"),
             Manager->GetReservePartyIds().Contains(TEXT("Reson")));
    TestFalse(TEXT("cannot restart a live encounter"),
              Manager->InitializeEncounter(Five, Chosen, Foes));

    // A nonconfigured ability table cannot silently advance an actor.
    FTSS_CombatCommand Unconfigured;
    Unconfigured.SourceParticipantId = TEXT("Lyra");
    Unconfigured.TargetParticipantId = TEXT("VoidWatcher");
    Unconfigured.SkillId = TEXT("ReviewStrike");
    TestFalse(TEXT("null table blocks command"), Manager->SubmitCommand(Unconfigured));
    TestEqual(TEXT("rejection retains actor"),
              Manager->GetActiveParticipantId(), FName(TEXT("Lyra")));

    Manager->SkillTable = MakeReviewTable();
    FTSS_CombatCommand Wrong = Unconfigured;
    Wrong.SourceParticipantId = TEXT("Ender");
    TestFalse(TEXT("out of turn is rejected"), Manager->SubmitCommand(Wrong));
    Wrong = Unconfigured; Wrong.TargetParticipantId = TEXT("Ender");
    TestFalse(TEXT("cannot attack ally"), Manager->SubmitCommand(Wrong));
    if (!TestTrue(TEXT("Lyra executes admitted skill"),
        Manager->SubmitCommand(Unconfigured))) return false;
    TestEqual(TEXT("Ender follows Lyra"), Manager->GetActiveParticipantId(),
              FName(TEXT("Ender")));
    TestEqual(TEXT("accepted skill decreased enemy health"),
              Manager->GetCombatantSnapshot()[3].Health, 16);
    Unconfigured.SourceParticipantId = TEXT("Ender");
    if (!TestTrue(TEXT("Ender acts second"),
        Manager->SubmitCommand(Unconfigured))) return false;
    TestEqual(TEXT("enemy follows Ender"), Manager->GetActiveParticipantId(),
              FName(TEXT("VoidWatcher")));
    FTSS_CombatCommand Claw;
    Claw.SourceParticipantId = TEXT("VoidWatcher");
    Claw.TargetParticipantId = TEXT("Lyra");
    Claw.SkillId = TEXT("ReviewClaw");
    if (!TestTrue(TEXT("enemy acts third"),
        Manager->SubmitCommand(Claw))) return false;
    TestEqual(TEXT("Ionia follows foe"), Manager->GetActiveParticipantId(),
              FName(TEXT("Ionia")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSSTurnManagerVictoryDefeatTest,
    "TSTSS.Combat.TurnManagerTerminalOutcomes",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSSTurnManagerVictoryDefeatTest::RunTest(const FString& Parameters)
{
    UDataTable* Table = MakeReviewTable();
    UTSS_CombatTurnManager* Victory = NewObject<UTSS_CombatTurnManager>();
    Victory->SkillTable = Table;
    TArray<FTSS_CombatParticipant> Player{MakeUnit(TEXT("Ender"), true, 25)};
    TArray<FTSS_CombatParticipant> Foes{MakeUnit(TEXT("Foe"), false, 10, 3)};
    if (!TestTrue(TEXT("victory fixture initializes"),
        Victory->InitializeEncounter(Player, {TEXT("Ender")}, Foes))) return false;
    FTSS_CombatCommand Strike;
    Strike.SourceParticipantId = TEXT("Ender");
    Strike.TargetParticipantId = TEXT("Foe");
    Strike.SkillId = TEXT("ReviewStrike");
    if (!TestTrue(TEXT("lethal action accepted"),
        Victory->SubmitCommand(Strike))) return false;
    TestEqual(TEXT("zero HP after lethal attack"),
              Victory->GetCombatantSnapshot()[1].Health, 0);
    TestEqual(TEXT("terminal victory state"), Victory->GetCurrentPhase(),
              ETSS_CombatPhase::Victory);
    TestTrue(TEXT("no actor available after terminal encounter"),
             Victory->GetActiveParticipantId().IsNone());
    TestFalse(TEXT("no second command after victory"), Victory->SubmitCommand(Strike));

    UTSS_CombatTurnManager* Defeat = NewObject<UTSS_CombatTurnManager>();
    Defeat->SkillTable = Table;
    Player[0].Stats.Health = 1;
    Foes[0] = MakeUnit(TEXT("Foe"), false, 30);
    if (!TestTrue(TEXT("defeat fixture initializes"),
        Defeat->InitializeEncounter(Player, {TEXT("Ender")}, Foes))) return false;
    TestEqual(TEXT("faster enemy starts"), Defeat->GetActiveParticipantId(),
              FName(TEXT("Foe")));
    FTSS_CombatCommand EnemyStrike;
    EnemyStrike.SourceParticipantId = TEXT("Foe");
    EnemyStrike.TargetParticipantId = TEXT("Ender");
    EnemyStrike.SkillId = TEXT("ReviewClaw");
    if (!TestTrue(TEXT("enemy lethal action resolves"),
        Defeat->SubmitCommand(EnemyStrike))) return false;
    TestEqual(TEXT("loss recognized"), Defeat->GetCurrentPhase(),
              ETSS_CombatPhase::Defeat);
    TestFalse(TEXT("dead party cannot submit action"),
              Defeat->SubmitCommand(Strike));
    return true;
}
#endif
