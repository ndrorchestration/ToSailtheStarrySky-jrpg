#include "Misc/AutomationTest.h"
#include "Enemies/TSTSSSliceEnemyReviewAI.h"
#include "Combat/TSS_CombatTurnManager.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSSliceEnemyReviewAIProbe,
    "TSTSS.Slice.Enemies.AuthorizedAIAndFallback",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSSliceEnemyReviewAIProbe::RunTest(const FString& Parameters)
{
    FTSS_CombatParticipant Ender;
    Ender.ParticipantId = TEXT("Ender");
    Ender.Stats.CharacterId = Ender.ParticipantId;
    Ender.Stats.Health = Ender.Stats.MaxHealth = 20;
    Ender.Stats.Resource = Ender.Stats.MaxResource = 10;
    Ender.Stats.Attack = 1;
    Ender.Agility = 5;
    Ender.bIsPlayerParty = true;
    FTSS_CombatParticipant Wisp;
    if (!TestTrue(TEXT("Wisp built"), FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(
        ETSTSSSliceEnemyKind::AetherLeakWisp, TEXT("Wisp_01"), Wisp))) return false;

    UTSS_CombatTurnManager* Denied = NewObject<UTSS_CombatTurnManager>();
    Denied->SkillTable = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(GetTransientPackage());
    if (!TestTrue(TEXT("design-only encounter begins"),
        Denied->InitializeEncounter({Ender}, {TEXT("Ender")}, {Wisp}))) return false;
    TestFalse(TEXT("default denied AI cannot act"),
        UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
            Denied, ETSTSSSliceEnemyKind::AetherLeakWisp, TEXT("Wisp_01")));
    TestFalse(TEXT("wrong archetype cannot impersonate Wisp"),
        UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
            Denied, ETSTSSSliceEnemyKind::DockSkitter, TEXT("Wisp_01")));
    TestEqual(TEXT("refused action retains active turn"),
              Denied->GetActiveParticipantId(), FName(TEXT("Wisp_01")));

    UTSS_CombatTurnManager* Allowed = NewObject<UTSS_CombatTurnManager>();
    Allowed->SkillTable = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
        GetTransientPackage(), true);
    if (!TestTrue(TEXT("opt-in encounter begins"),
        Allowed->InitializeEncounter({Ender}, {TEXT("Ender")}, {Wisp}))) return false;
    if (!TestTrue(TEXT("AI resolves through existing manager"),
        UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
            Allowed, ETSTSSSliceEnemyKind::AetherLeakWisp, TEXT("Wisp_01")))) return false;
    const TArray<FTSTSSCombatant> After = Allowed->GetCombatantSnapshot();
    const FTSTSSCombatant* Hurt = After.FindByPredicate(
        [](const FTSTSSCombatant& U) {return U.CharacterId == TEXT("Ender");});
    const FTSTSSCombatant* Actor = After.FindByPredicate(
        [](const FTSTSSCombatant& U) {return U.CharacterId == TEXT("Wisp_01");});
    if (!TestNotNull(TEXT("Ender in result"), Hurt) ||
        !TestNotNull(TEXT("Wisp in result"), Actor)) return false;
    TestEqual(TEXT("WispSurge power plus attack"), Hurt->Health, 16);
    TestEqual(TEXT("WispSurge resource charge"), Actor->Resource, 5);
    TestFalse(TEXT("out-of-turn repeat denied"),
        UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
            Allowed, ETSTSSSliceEnemyKind::AetherLeakWisp, TEXT("Wisp_01")));

    Wisp.Stats.Resource = 0;
    UTSS_CombatTurnManager* Fallback = NewObject<UTSS_CombatTurnManager>();
    Fallback->SkillTable = FTSTSSSliceEnemyCatalog::MakeReviewSkillTable(
        GetTransientPackage(), true);
    if (!TestTrue(TEXT("resource-starved encounter begins"),
        Fallback->InitializeEncounter({Ender}, {TEXT("Ender")}, {Wisp}))) return false;
    if (!TestTrue(TEXT("AI uses free skill as fallback"),
        UTSTSSSliceEnemyReviewAI::TryActReviewEnemy(
            Fallback, ETSTSSSliceEnemyKind::AetherLeakWisp, TEXT("Wisp_01")))) return false;
    const TArray<FTSTSSCombatant> Result = Fallback->GetCombatantSnapshot();
    const FTSTSSCombatant* FallbackTarget = Result.FindByPredicate(
        [](const FTSTSSCombatant& U) {return U.CharacterId == TEXT("Ender");});
    if (!TestNotNull(TEXT("fallback target exists"), FallbackTarget)) return false;
    TestEqual(TEXT("Spark power plus attack, not Surge"), FallbackTarget->Health, 18);
    return true;
}
#endif
