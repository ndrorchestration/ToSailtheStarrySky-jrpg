#include "Misc/AutomationTest.h"
#include "Enemies/TSTSSSliceEnemyReviewAI.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Enemies/TSTSSSliceEnemyReviewSession.h"
#include "Enemies/TSTSSSliceEnemyReviewBattleConsole.h"

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

    // Real review-battle session without spawning a level, mutating a save,
    // adding a class skill or overriding the authoritative turn manager.
    UTSTSSSliceEnemyReviewSession* Unknown =
        NewObject<UTSTSSSliceEnemyReviewSession>(GetTransientPackage());
    TestFalse(TEXT("unknown wave cannot start"),
        Unknown->TryStart(TEXT("not_a_wave"),
            ETSTSSSliceReviewPartyStage::EnderOnly));
    TestNull(TEXT("denied wave has no combat manager"), Unknown->GetReviewManager());
    TestFalse(TEXT("invalid party stage cannot authorize new characters"),
        Unknown->TryStart(TEXT("Review_HarborBanditPatrol"),
            static_cast<ETSTSSSliceReviewPartyStage>(255)));
    TestNull(TEXT("invalid stage preserves unstarted state"),
             Unknown->GetReviewManager());

    UTSTSSSliceEnemyReviewSession* First =
        NewObject<UTSTSSSliceEnemyReviewSession>(GetTransientPackage());
    if (!TestTrue(TEXT("Ender-only sandbox starts"),
        First->TryStart(TEXT("Review_HarborBanditPatrol"),
            ETSTSSSliceReviewPartyStage::EnderOnly))) return false;
    const TArray<FName> FirstCrew = First->GetReviewActivePartyIds();
    TestEqual(TEXT("first act permits only Ender"), FirstCrew.Num(), 1);
    TestEqual(TEXT("Ender remains explicit first member"),
        FirstCrew[0], FName(TEXT("Ender")));
    TestFalse(TEXT("Ionia not unlocked by sandbox default"),
        FirstCrew.Contains(TEXT("Ionia")));
    TestFalse(TEXT("Lyra not silently recruited by sandbox default"),
        FirstCrew.Contains(TEXT("Lyra")));
    TestNotNull(TEXT("sandbox delegates to real combat manager"),
        First->GetReviewManager());
    TestEqual(TEXT("only two review enemies"), First->GetReviewEnemyIds().Num(), 2);
    const UDataTable* Table = First->GetReviewManager()->SkillTable.Get();
    if (!TestNotNull(TEXT("sandbox has isolated transient skill table"), Table))
        return false;
    TestEqual(TEXT("only one player strike added to 30 enemy actions"),
              Table->GetRowMap().Num(), 31);
    const FTSTSSBattleSkillRow* Strike =
        Table->FindRow<FTSTSSBattleSkillRow>(
            TEXT("SliceReview_PlayerStrike"), TEXT("review stage"), false);
    if (!TestNotNull(TEXT("temporary strike exists only in sandbox"), Strike))
        return false;
    TestTrue(TEXT("review strike explicitly admitted"),
        Strike->Admission == ETSTSSBattleSkillAdmission::ReviewExecutable);
    TestFalse(TEXT("unauthorized third target slot refused"),
        First->TryPlayerStrike(2));
    TestFalse(TEXT("negative slot refused"), First->TryPlayerStrike(-1));
    TestFalse(TEXT("session cannot restart or silently change party"),
        First->TryStart(TEXT("Review_HarborBanditPatrol"),
            ETSTSSSliceReviewPartyStage::AfterSplashdown));

    // The implementation's startup pumps the AI until a player's turn.
    TestEqual(TEXT("review control reaches Ender after fast foes"),
        First->GetReviewManager()->GetActiveParticipantId(), FName(TEXT("Ender")));
    FTSS_CombatCommand Spoof;
    Spoof.SourceParticipantId = TEXT("Ender");
    Spoof.TargetParticipantId = First->GetReviewEnemyIds()[0];
    Spoof.SkillId = TEXT("SliceReview_CaptainHeavyBlow");
    TestFalse(TEXT("review player cannot borrow bandit ability"),
        First->GetReviewManager()->SubmitCommand(Spoof));
    if (!TestTrue(TEXT("J-style strike resolved through real manager"),
        First->TryPlayerStrike(0))) return false;

    UTSTSSSliceEnemyReviewSession* Middle =
        NewObject<UTSTSSSliceEnemyReviewSession>(GetTransientPackage());
    if (!TestTrue(TEXT("Ionia-recruited stage explicitly starts"),
        Middle->TryStart(TEXT("Review_WoodlandSporeline"),
            ETSTSSSliceReviewPartyStage::IoniaRecruited))) return false;
    TestEqual(TEXT("Middle stage has exactly two protagonists"),
              Middle->GetReviewActivePartyIds().Num(), 2);
    TestFalse(TEXT("Middle stage never includes Lyra"),
              Middle->GetReviewActivePartyIds().Contains(TEXT("Lyra")));

    UTSTSSSliceEnemyReviewSession* Late =
        NewObject<UTSTSSSliceEnemyReviewSession>(GetTransientPackage());
    if (!TestTrue(TEXT("after-splashdown stage explicitly starts"),
        Late->TryStart(TEXT("Review_HarborBanditPatrol"),
            ETSTSSSliceReviewPartyStage::AfterSplashdown))) return false;
    TestEqual(TEXT("after-splashdown review has three canonical members"),
              Late->GetReviewActivePartyIds().Num(), 3);
    TestTrue(TEXT("Lyra appears only after explicit stage selection"),
             Late->GetReviewActivePartyIds().Contains(TEXT("Lyra")));

    for (int32 Step = 0; Step < 16 &&
         Late->GetReviewManager()->GetCurrentPhase() == ETSS_CombatPhase::TurnSelection;
         ++Step)
    {
        const FName Active = Late->GetReviewManager()->GetActiveParticipantId();
        if (!Late->GetReviewActivePartyIds().Contains(Active))
        {
            if (!TestTrue(TEXT("enemy turn uses existing AI authority"),
                          Late->TryAdvanceEnemyTurns())) return false;
            continue;
        }
        const TArray<FTSTSSCombatant> Snapshot =
            Late->GetReviewManager()->GetCombatantSnapshot();
        int32 TargetSlot = INDEX_NONE;
        const TArray<FName> Ids = Late->GetReviewEnemyIds();
        for (int32 Index = 0; Index < Ids.Num(); ++Index)
        {
            const FTSTSSCombatant* Enemy = Snapshot.FindByPredicate(
                [Id=Ids[Index]](const FTSTSSCombatant& U) {
                    return U.CharacterId == Id && U.Health > 0;
                });
            if (Enemy) {TargetSlot = Index; break;}
        }
        if (!TestTrue(TEXT("living target found before victory"),
                      TargetSlot != INDEX_NONE)) return false;
        if (!TestTrue(TEXT("player strike accepted through real manager"),
                      Late->TryPlayerStrike(TargetSlot))) return false;
    }
    TestEqual(TEXT("finite isolated post-splashdown battle reaches victory"),
        Late->GetReviewManager()->GetCurrentPhase(), ETSS_CombatPhase::Victory);

    TestNotNull(TEXT("review battle console C++ actor registered"),
        ATSTSSSliceEnemyReviewBattleConsole::StaticClass());
    return true;
}
#endif
