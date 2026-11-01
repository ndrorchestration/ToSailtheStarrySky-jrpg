#include "Misc/AutomationTest.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "TSTSSCombatSkillReconciliation.h"
#include "Engine/DataTable.h"

// Crosses the ACTUAL Unreal combat component boundary, not only the
// standalone BattleSkillSystem gate. No production gameplay is modified.
// The test fixture is not an approved spell or a player skill unlock.
#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    FTSS_CombatParticipant MakeIsolatedReviewUnit(
        const TCHAR* Id, bool bPlayer, int32 Speed)
    {
        FTSS_CombatParticipant Unit;
        Unit.ParticipantId = FName(Id);
        Unit.Stats.CharacterId = Unit.ParticipantId;
        Unit.Stats.Health = 20;
        Unit.Stats.MaxHealth = 20;
        Unit.Stats.Resource = 10;
        Unit.Stats.MaxResource = 10;
        Unit.Stats.Attack = 1;
        Unit.Stats.Defense = 0;
        Unit.Agility = Speed;
        Unit.bIsPlayerParty = bPlayer;
        return Unit;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSDesignOnlyTurnManagerDenialTest,
    "TSTSS.CombatIntegration.DesignOnlyTurnManagerDenial",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSDesignOnlyTurnManagerDenialTest::RunTest(const FString& Parameters)
{
    FTSTSSActionDefRow Proposal;
    Proposal.ActionId = TEXT("NoncanonicalDesignProbe");
    Proposal.Category = ETSTSSActionCategory::Spell;
    Proposal.Target = ETSTSSActionTarget::Enemy;
    Proposal.Power = 3;
    Proposal.Cost = 2;
    Proposal.UnlockLevel = 1;
    Proposal.Learners.Add(FName(TEXT("Ender")));
    // Test-only approval flag checks that even a source-approved row does
    // NOT become executable merely by entering the authoring catalog.
    Proposal.Approval = ETSTSSApproval::CreatorApproved;
    Proposal.Affinity = ETSTSSLight::Spirit;

    TMap<FName, FTSTSSBattleSkillRow> DesignCatalog;
    if (!TestTrue(TEXT("design-only source conversion succeeds"),
        FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {Proposal}, DesignCatalog))) return false;
    const FTSTSSBattleSkillRow* Design = DesignCatalog.Find(Proposal.ActionId);
    if (!TestNotNull(TEXT("converted design row exists"), Design)) return false;
    if (!TestTrue(TEXT("converted row has denied admission"),
        Design->Admission == ETSTSSBattleSkillAdmission::DesignOnly)) return false;

    // Simulate even a mistakenly overgenerous authored learned/mastery
    // configuration. Admission must STILL deny entry at SubmitCommand.
    FTSTSSBattleSkillRow ArmedReview = *Design;
    ArmedReview.RequiredSchool = TEXT("FixtureSchool");
    ArmedReview.RequiredMasteryRank = 1;
    UDataTable* ReviewTable = NewObject<UDataTable>();
    ReviewTable->RowStruct = FTSTSSBattleSkillRow::StaticStruct();
    ReviewTable->AddRow(ArmedReview.SkillId, ArmedReview);

    FTSS_CombatParticipant Ender =
        MakeIsolatedReviewUnit(TEXT("Ender"), true, 20);
    Ender.LearnedSkills.Add(Proposal.ActionId);
    Ender.MasteryRanks.Add(TEXT("FixtureSchool"), 5);
    FTSS_CombatParticipant Opponent =
        MakeIsolatedReviewUnit(TEXT("NoncanonOpponent"), false, 5);

    UTSS_CombatTurnManager* Manager = NewObject<UTSS_CombatTurnManager>();
    Manager->SkillTable = ReviewTable;
    if (!TestTrue(TEXT("review encounter initializes without granting spells"),
        Manager->InitializeEncounter({Ender}, {FName(TEXT("Ender"))},
                                     {Opponent}))) return false;

    const TArray<FTSTSSCombatant> Before = Manager->GetCombatantSnapshot();
    const int32 BeforeRound = Manager->GetCurrentRound();
    const FName BeforeActor = Manager->GetActiveParticipantId();
    FTSS_CombatCommand Command;
    Command.SourceParticipantId = TEXT("Ender");
    Command.TargetParticipantId = TEXT("NoncanonOpponent");
    Command.SkillId = Proposal.ActionId;

    TestFalse(TEXT("DesignOnly skill rejected at actual turn-manager entry"),
              Manager->SubmitCommand(Command));
    TestTrue(TEXT("turn phase remains selecting action"),
        Manager->GetCurrentPhase() == ETSS_CombatPhase::TurnSelection);
    TestEqual(TEXT("current actor unchanged on denied design ability"),
              Manager->GetActiveParticipantId(), BeforeActor);
    TestEqual(TEXT("current round unchanged"), Manager->GetCurrentRound(),
              BeforeRound);
    const TArray<FTSTSSCombatant> After = Manager->GetCombatantSnapshot();
    if (!TestEqual(TEXT("roster size preserved"), After.Num(),
                   Before.Num())) return false;
    for (int32 Index = 0; Index < Before.Num(); ++Index)
    {
        TestEqual(TEXT("combatant identity preserved"),
                  After[Index].CharacterId, Before[Index].CharacterId);
        TestEqual(TEXT("HP preserved"), After[Index].Health, Before[Index].Health);
        TestEqual(TEXT("resource preserved"), After[Index].Resource,
                  Before[Index].Resource);
    }
    // Positive control: change ONLY admission to ReviewExecutable in a
    // separate synthetic test-only DataTable and a fresh encounter. If this
    // cannot execute, the preceding denial might have been caused by a
    // broken actor turn, target, knowledge, or DataTable configuration rather
    // than the intended admission gate. No runtime/production row is modified.
    FTSTSSBattleSkillRow SyntheticExecutable = ArmedReview;
    SyntheticExecutable.Admission = ETSTSSBattleSkillAdmission::ReviewExecutable;
    UDataTable* ExplicitReviewTable = NewObject<UDataTable>();
    ExplicitReviewTable->RowStruct = FTSTSSBattleSkillRow::StaticStruct();
    ExplicitReviewTable->AddRow(SyntheticExecutable.SkillId, SyntheticExecutable);

    UTSS_CombatTurnManager* PositiveManager =
        NewObject<UTSS_CombatTurnManager>();
    PositiveManager->SkillTable = ExplicitReviewTable;
    if (!TestTrue(TEXT("synthetic opt-in encounter initializes"),
        PositiveManager->InitializeEncounter({Ender},
            {FName(TEXT("Ender"))}, {Opponent}))) return false;
    if (!TestEqual(TEXT("positive control actor is Ender"),
        PositiveManager->GetActiveParticipantId(),
        FName(TEXT("Ender")))) return false;
    if (!TestTrue(TEXT("only explicitly admitted synthetic skill executes"),
        PositiveManager->SubmitCommand(Command))) return false;

    const TArray<FTSTSSCombatant> Accepted =
        PositiveManager->GetCombatantSnapshot();
    if (!TestEqual(TEXT("positive control roster size"), Accepted.Num(), 2))
        return false;
    const FTSTSSCombatant* AcceptedEnder =
        Accepted.FindByPredicate([](const FTSTSSCombatant& Unit) {
            return Unit.CharacterId == FName(TEXT("Ender"));
        });
    const FTSTSSCombatant* AcceptedFoe =
        Accepted.FindByPredicate([](const FTSTSSCombatant& Unit) {
            return Unit.CharacterId == FName(TEXT("NoncanonOpponent"));
        });
    if (!TestNotNull(TEXT("positive control Ender exists"), AcceptedEnder) ||
        !TestNotNull(TEXT("positive control opponent exists"), AcceptedFoe))
        return false;
    TestEqual(TEXT("explicit opt-in consumes synthetic resource cost"),
              AcceptedEnder->Resource, 8);
    TestEqual(TEXT("explicit opt-in deals synthetic attack plus skill damage"),
              AcceptedFoe->Health, 16);
    TestTrue(TEXT("positive control advanced to opponent's turn"),
             PositiveManager->GetActiveParticipantId() ==
                 FName(TEXT("NoncanonOpponent")));

    // All of this is WITH_DEV_AUTOMATION_TESTS-only. A successful artificial
    // admission proves a functioning comparison path, NOT creator permission
    // to grant the character a real spell or ship production game content.
    return true;
}
#endif
