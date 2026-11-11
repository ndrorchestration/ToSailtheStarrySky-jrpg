#include "Misc/AutomationTest.h"
#include "Enemies/TSTSSSliceEnemyCatalog.h"
#include "Enemies/TSTSSSliceEnemyActor.h"
#include "Engine/DataTable.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSliceEnemyReviewCatalogTest,
    "TSTSS.Slice.Enemies.RegistryAndAdmission",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSSliceEnemyReviewCatalogTest::RunTest(const FString& Parameters)
{
    const ETSTSSSliceEnemyKind AllKinds[] = {
        ETSTSSSliceEnemyKind::HarmonicShear,
        ETSTSSSliceEnemyKind::AetherLeakWisp,
        ETSTSSSliceEnemyKind::DockSkitter
    };
    TSet<FName> Archetypes;
    TSet<FName> Skills;
    for (const ETSTSSSliceEnemyKind Kind : AllKinds)
    {
        FTSTSSSliceEnemyDescriptor Definition;
        if (!TestTrue(TEXT("registered kind resolves"),
            FTSTSSSliceEnemyCatalog::TryDescribe(Kind, Definition))) return false;
        TestFalse(TEXT("story placement is never automatically approved"),
                  Definition.bStoryPlacementApproved);
        TestTrue(TEXT("valid HP/resource/balance ranges"),
            Definition.MaxHP > 0 && Definition.MaxHP <= 100 &&
            Definition.MaxResource >= 0 && Definition.MaxResource <= 20 &&
            Definition.Attack >= 0 && Definition.Attack <= 10 &&
            Definition.Defense >= 0 && Definition.Defense <= 10 &&
            Definition.Agility >= 0 && Definition.Agility <= 30);
        TestFalse(TEXT("unique archetype identity"),
                  Archetypes.Contains(Definition.ArchetypeId));
        Archetypes.Add(Definition.ArchetypeId);
        TestEqual(TEXT("two defined actions per creature"),
                  Definition.AbilityIds.Num(), 2);
        for (const FName Skill : Definition.AbilityIds)
        {
            TestFalse(TEXT("no duplicated abilities across creatures"),
                      Skills.Contains(Skill));
            Skills.Add(Skill);
        }

        const FName InstanceId(
            *FString::Printf(TEXT("ReviewEnemy_%d"), static_cast<int32>(Kind)));
        FTSS_CombatParticipant Unit;
        if (!TestTrue(TEXT("encounter participant is constructed"),
            FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
                Kind, InstanceId, Unit))) return false;
        TestEqual(TEXT("participant matches unique ID"), Unit.Stats.CharacterId, InstanceId);
        TestEqual(TEXT("HP matches catalog"), Unit.Stats.Health, Definition.MaxHP);
        TestEqual(TEXT("resource matches catalog"),
                  Unit.Stats.Resource, Definition.MaxResource);
        TestEqual(TEXT("agility matches catalog"), Unit.Agility, Definition.Agility);
        TestFalse(TEXT("creature cannot belong to player party"), Unit.bIsPlayerParty);
        TestEqual(TEXT("creature knows only its two review actions"),
                  Unit.LearnedSkills.Num(), 2);
    }

    FTSTSSSliceEnemyDescriptor Preserve;
    Preserve.DisplayName = TEXT("sentinel");
    TestFalse(TEXT("unknown kind denied"),
        FTSTSSSliceEnemyCatalog::TryDescribe(
            static_cast<ETSTSSSliceEnemyKind>(255), Preserve));
    TestEqual(TEXT("unknown kind preserves output"),
              Preserve.DisplayName, FString(TEXT("sentinel")));
    FTSS_CombatParticipant InvalidOut;
    InvalidOut.ParticipantId = TEXT("unchanged");
    TestFalse(TEXT("empty ID denied"),
        FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
            ETSTSSSliceEnemyKind::HarmonicShear, NAME_None, InvalidOut));
    TestFalse(TEXT("protagonist spoof denied"),
        FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
            ETSTSSSliceEnemyKind::HarmonicShear, TEXT("Ender"), InvalidOut));
    TestFalse(TEXT("unknown kind denied at participant boundary"),
        FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
            static_cast<ETSTSSSliceEnemyKind>(255), TEXT("Unknown"), InvalidOut));
    TestEqual(TEXT("rejections preserve output"), InvalidOut.ParticipantId,
              FName(TEXT("unchanged")));

    UDataTable* DesignOnly = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
        GetTransientPackage());
    if (!TestNotNull(TEXT("review DataTable exists"), DesignOnly)) return false;
    TestEqual(TEXT("all six enemy-only rows authored"),
              DesignOnly->GetRowMap().Num(), 6);
    for (const FName Skill : Skills)
    {
        const FTSTSSBattleSkillRow* Row =
            DesignOnly->FindRow<FTSTSSBattleSkillRow>(
                Skill, TEXT("slice catalog review"), false);
        if (!TestNotNull(TEXT("row found by skill ID"), Row)) return false;
        TestEqual(TEXT("row ID matches key"), Row->SkillId, Skill);
        TestTrue(TEXT("unapproved row is not executable"),
            Row->Admission == ETSTSSBattleSkillAdmission::DesignOnly);
        TestTrue(TEXT("not silently treated as an elemental spell"),
            Row->Kind == ETSTSSBattleSkillKind::JobArt);
    }
    TestNotNull(TEXT("actor class available to editor"),
                ATSTSSSliceEnemyActor::StaticClass());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSliceEnemyCombatGateTest,
    "TSTSS.Slice.Enemies.RealTurnManagerBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSSliceEnemyCombatGateTest::RunTest(const FString& Parameters)
{
    FTSS_CombatParticipant Ender;
    Ender.ParticipantId = TEXT("Ender");
    Ender.Stats.CharacterId = Ender.ParticipantId;
    Ender.Stats.Health = Ender.Stats.MaxHealth = 20;
    Ender.Stats.Resource = Ender.Stats.MaxResource = 10;
    Ender.Stats.Attack = 1;
    Ender.Stats.Defense = 0;
    Ender.Agility = 5;
    Ender.bIsPlayerParty = true;

    FTSS_CombatParticipant Foe;
    if (!TestTrue(TEXT("valid existing Wind Shear maps to current manager"),
        FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
            ETSTSSSliceEnemyKind::HarmonicShear, TEXT("Shear_01"), Foe))) return false;
    UTSS_CombatTurnManager* Denied = NewObject<UTSS_CombatTurnManager>();
    Denied->SkillTable = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
        GetTransientPackage());
    if (!TestTrue(TEXT("isolated 1v1 begins"),
        Denied->InitializeEncounter({Ender}, {TEXT("Ender")}, {Foe}))) return false;
    TestEqual(TEXT("faster enemy has initiative"),
              Denied->GetActiveParticipantId(), FName(TEXT("Shear_01")));
    FTSS_CombatCommand Gale;
    Gale.SourceParticipantId = TEXT("Shear_01");
    Gale.TargetParticipantId = TEXT("Ender");
    Gale.SkillId = TEXT("SliceReview_GaleForce");
    const int32 BeforeRound = Denied->GetCurrentRound();
    TestFalse(TEXT("design-only Gale never executes"),
              Denied->SubmitCommand(Gale));
    TestEqual(TEXT("denial preserves phase"),
              Denied->GetCurrentPhase(), ETSS_CombatPhase::TurnSelection);
    TestEqual(TEXT("denial preserves turn"), Denied->GetCurrentRound(), BeforeRound);
    // Snapshot must outlive any pointer returned by FindByPredicate.
    const TArray<FTSTSSCombatant> DeniedSnapshot = Denied->GetCombatantSnapshot();
    const FTSTSSCombatant* BeforeEnder = DeniedSnapshot.FindByPredicate(
        [](const FTSTSSCombatant& Value) { return Value.CharacterId == TEXT("Ender"); });
    if (!TestNotNull(TEXT("Ender remains in denied encounter"), BeforeEnder)) return false;
    TestEqual(TEXT("denied action cannot change HP"), BeforeEnder->Health, 20);

    UTSS_CombatTurnManager* Explicit = NewObject<UTSS_CombatTurnManager>();
    Explicit->SkillTable = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
        GetTransientPackage(), true);
    if (!TestTrue(TEXT("explicitly opted-in review encounter begins"),
        Explicit->InitializeEncounter({Ender}, {TEXT("Ender")}, {Foe}))) return false;
    FTSS_CombatCommand Wrong = Gale;
    Wrong.SourceParticipantId = TEXT("Ender");
    TestFalse(TEXT("cannot act as wrong active source"), Explicit->SubmitCommand(Wrong));
    if (!TestTrue(TEXT("only explicit review admission resolves through real manager"),
        Explicit->SubmitCommand(Gale))) return false;
    const TArray<FTSTSSCombatant> After = Explicit->GetCombatantSnapshot();
    const FTSTSSCombatant* ResultEnder = After.FindByPredicate(
        [](const FTSTSSCombatant& Value) {return Value.CharacterId == TEXT("Ender");});
    if (!TestNotNull(TEXT("Ender still present after authorized review action"),
                     ResultEnder)) return false;
    TestEqual(TEXT("Gale power 2 plus attack 2 resolves exactly once"),
              ResultEnder->Health, 16);
    TestEqual(TEXT("next turn belongs to Ender"),
              Explicit->GetActiveParticipantId(), FName(TEXT("Ender")));
    TestFalse(TEXT("enemy cannot act twice in a turn"), Explicit->SubmitCommand(Gale));
    return true;
}
#endif
