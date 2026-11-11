#include "Misc/AutomationTest.h"
#include "Enemies/TSTSSSliceEnemyReviewAI.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "Enemies/TSTSSSliceEnemyReviewSession.h"
#include "Enemies/TSTSSSliceEnemyReviewBattleConsole.h"
#include "Encounter/TSTSSJRPGEncounterDirector.h"
#include "Encounter/TSTSSJRPGEncounterFieldReview.h"
#include "Encounter/TSTSSJRPGReviewPresentation.h"
#include "Encounter/TSTSSJRPGReviewRewards.h"
#include <limits>

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

    TestNotNull(TEXT("opt-in review explorer C++ actor registered"),
        ATSTSSJRPGEncounterFieldReview::StaticClass());

    // Hybrid FF-style walking encounter selector. It never initializes combat,
    // and must be explicitly authorized by traversal, party and area scope.
    UTSTSSJRPGEncounterDirector* Director =
        NewObject<UTSTSSJRPGEncounterDirector>(GetTransientPackage());
    FTSTSSJRPGEncounterTicket DeniedTicket;
    DeniedTicket.Serial=771;
    FTSTSSJRPGEncounterContext Region;
    TestFalse(TEXT("unconfigured region refuses walking encounter"),
        Director->TryRecordWalking(300.f,Region,DeniedTicket));
    TestEqual(TEXT("denied request preserves output"),DeniedTicket.Serial,771);
    TestFalse(TEXT("unknown biome enum refused"),
        Director->TryConfigureReviewBiome(
            static_cast<ETSTSSJRPGEncounterBiome>(255),17));
    TestTrue(TEXT("explicit harbor review profile configured"),
        Director->TryConfigureReviewBiome(
            ETSTSSJRPGEncounterBiome::HarborOutskirts,17));
    for (int32 I=0;I<25;++I)
    {
        TestFalse(TEXT("unauthorized profile never rolls"),
            Director->TryRecordWalking(300.f,Region,DeniedTicket));
    }
    TestEqual(TEXT("denied traversal cannot bank ambush progress"),
        Director->GetWalkingDistanceSinceBattleCm(),0.f);
    Region.bTraversalActive=true;
    Region.bAreaAuthorized=true;
    Region.bPartyAuthorized=true;
    Region.bSafeZone=false;
    FTSTSSJRPGEncounterTicket Selected;
    TestFalse(TEXT("teleport jump rejected"),
        Director->TryRecordWalking(99999.f,Region,Selected));
    TestFalse(TEXT("negative distance rejected"),
        Director->TryRecordWalking(-1.f,Region,Selected));
    TestFalse(TEXT("nonfinite distance rejected"),
        Director->TryRecordWalking(std::numeric_limits<float>::quiet_NaN(),Region,Selected));
    TestFalse(TEXT("scripted event denied without separate authority"),
        Director->TryRequestScripted(TEXT("Review_HarborBanditCaptain"),
                                      Region,Selected));
    TestFalse(TEXT("unrelated biome script refused"),
        Director->TryRequestScripted(TEXT("Review_CoastalHunters"),
                                      Region,Selected));

    UTSTSSJRPGEncounterDirector* Mirror =
        NewObject<UTSTSSJRPGEncounterDirector>(GetTransientPackage());
    TestTrue(TEXT("reproducible exact-seed director initialized"),
        Mirror->TryConfigureReviewBiome(
            ETSTSSJRPGEncounterBiome::HarborOutskirts,17));
    bool bEncounter=false;
    for(int32 Step=0;Step<45;++Step)
    {
        FTSTSSJRPGEncounterTicket FirstTicket;
        FTSTSSJRPGEncounterTicket SecondTicket;
        const bool A=Director->TryRecordWalking(300.f,Region,FirstTicket);
        const bool B=Mirror->TryRecordWalking(300.f,Region,SecondTicket);
        if (!TestEqual(TEXT("seeded encounter parity"),A,B))return false;
        if (A)
        {
            TestEqual(TEXT("seeded preset parity"),
                FirstTicket.ReviewWavePreset,SecondTicket.ReviewWavePreset);
            TestEqual(TEXT("rare/common selection remains a legal harbor wave"),
                FirstTicket.Biome,ETSTSSJRPGEncounterBiome::HarborOutskirts);
            TestFalse(TEXT("random encounter is not scripted"),
                FirstTicket.bScripted);
            TestTrue(TEXT("random output is noncanonical review"),
                FirstTicket.bReviewOnly);
            TestTrue(TEXT("minimum walk prevents instant interruptions"),
                Director->GetWalkingDistanceSinceBattleCm()>=1800.f);
            TestTrue(TEXT("pity counter guarantees within cap"),
                Director->GetWalkingDistanceSinceBattleCm()<=5700.f);
            TestFalse(TEXT("duplicate pending encounter refused"),
                Director->TryRecordWalking(300.f,Region,DeniedTicket));
            TestFalse(TEXT("pending ticket cannot be overwritten by new biome"),
                Director->TryConfigureReviewBiome(
                    ETSTSSJRPGEncounterBiome::Woodland,13));
            TestFalse(TEXT("incorrect ticket cannot start battle"),
                Director->TryAcknowledgeBattleStart(FirstTicket.Serial+1));
            TestFalse(TEXT("unstarted ticket cannot complete"),
                Director->TryCompleteBattle(FirstTicket.Serial));
            TestFalse(TEXT("wrong ticket cannot be canceled"),
                Director->TryCancelPending(FirstTicket.Serial+1));
            TestTrue(TEXT("ticket acknowledged once for real battle"),
                Director->TryAcknowledgeBattleStart(FirstTicket.Serial));
            TestFalse(TEXT("ticket replay blocked"),
                Director->TryAcknowledgeBattleStart(FirstTicket.Serial));
            TestFalse(TEXT("wrong ticket completion refused"),
                Director->TryCompleteBattle(FirstTicket.Serial+1));
            TestTrue(TEXT("correct ticket completion returns to traversal"),
                Director->TryCompleteBattle(FirstTicket.Serial));
            TestFalse(TEXT("battle ticket not sticky after return"),
                Director->HasOutstandingTicket());
            bEncounter=true;
            break;
        }
    }
    TestTrue(TEXT("fixed-distance random selection eventually occurs"),bEncounter);

    // Explicitly scripted captain encounter remains a separate authority,
    // never a random boss story claim or an implicit quest progression.
    Region.bScriptedEncounterApproved=true;
    FTSTSSJRPGEncounterTicket BossTicket;
    TestFalse(TEXT("scripted cross-biome spoof refused"),
        Director->TryRequestScripted(TEXT("Review_WoodlandSentinel"),
                                      Region,BossTicket));
    TestTrue(TEXT("explicit same-biome scripted encounter admitted"),
        Director->TryRequestScripted(TEXT("Review_HarborBanditCaptain"),
                                      Region,BossTicket));
    TestTrue(TEXT("scripted ticket provenance recorded"),BossTicket.bScripted);
    TestTrue(TEXT("scripted ticket consumed exactly once"),
        Director->TryAcknowledgeBattleStart(BossTicket.Serial));
    TestFalse(TEXT("started battle cannot be canceled"),
        Director->TryCancelPending(BossTicket.Serial));
    TestTrue(TEXT("scripted ticket completed"),
        Director->TryCompleteBattle(BossTicket.Serial));
    FTSTSSJRPGEncounterTicket AbortedTicket;
    TestTrue(TEXT("explicit second scripted review issued"),
        Director->TryRequestScripted(TEXT("Review_HarborBanditCaptain"),
                                      Region,AbortedTicket));
    TestTrue(TEXT("unstarted failed scene handoff can be canceled"),
        Director->TryCancelPending(AbortedTicket.Serial));
    TestFalse(TEXT("canceled ticket cannot be acknowledged"),
        Director->TryAcknowledgeBattleStart(AbortedTicket.Serial));

    Region.bSafeZone=true;
    TestFalse(TEXT("safe zone never selects encounter"),
        Director->TryRecordWalking(300.f,Region,Selected));
    TestEqual(TEXT("safe zone resets danger meter"),
        Director->GetWalkingDistanceSinceBattleCm(),0.f);
    Region.bSafeZone=false;
    Region.bShipTravel=true;
    TestFalse(TEXT("ship travel cannot select walking encounters"),
        Director->TryRecordWalking(300.f,Region,Selected));
    Region.bShipTravel=false;
    Region.Rate=ETSTSSJRPGEncounterRate::Off;
    TestFalse(TEXT("accessibility off disables encounters"),
        Director->TryRecordWalking(300.f,Region,Selected));

    // Full ordered audiovisual/reward sequence is a separate deterministic
    // control-plane gate, independent of random selection or narrative state.
    UTSTSSJRPGReviewPresentation* Sequence=
        NewObject<UTSTSSJRPGReviewPresentation>(GetTransientPackage());
    TestFalse(TEXT("cannot enter unstarted battle"),
        Sequence->TryEnterCombat(51));
    TestTrue(TEXT("encounter intro flashes before battle"),
        Sequence->TryBegin(51));
    TestFalse(TEXT("same encounter cannot begin twice"),Sequence->TryBegin(51));
    TestEqual(TEXT("encounter flash first"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::EncounterFlash);
    TestFalse(TEXT("battle may not skip audiovisual cue"),
        Sequence->TryEnterCombat(51));
    TestFalse(TEXT("wrong ticket cannot abort"),
        Sequence->TryAbortBeforeCombat(52));
    TestTrue(TEXT("valid flash frame"),
        Sequence->Advance(.21f));
    TestFalse(TEXT("nonfinite progress denied"),
        Sequence->Advance(std::numeric_limits<float>::quiet_NaN()));
    TestTrue(TEXT("flash completes"),Sequence->Advance(.21f));
    TestEqual(TEXT("battle reveal after encounter flash"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::BattleReveal);
    TestFalse(TEXT("battle reveal cannot be cut short"),
        Sequence->TryEnterCombat(51));
    TestTrue(TEXT("battle reveal frame one"),Sequence->Advance(.18f));
    TestTrue(TEXT("battle reveal frame two"),Sequence->Advance(.18f));
    TestTrue(TEXT("battle admission at transition boundary"),
        Sequence->TryEnterCombat(51));
    TestEqual(TEXT("authoritative battle phase"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::Combat);
    TestFalse(TEXT("cannot confirm victory on wrong ticket"),
        Sequence->TryResolveVictory(52));
    TestFalse(TEXT("cannot dismiss unfinished battle"),
        Sequence->TryDismissResult(51));
    TestTrue(TEXT("authoritative victory starts fanfare"),
        Sequence->TryResolveVictory(51));
    TestEqual(TEXT("victory fanfare precedes celebration"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::VictoryFanfare);
    TestFalse(TEXT("victory cannot award repeatedly through phase replay"),
        Sequence->TryResolveVictory(51));
    for(int32 I=0;I<8;++I) Sequence->Advance(.2f);
    TestEqual(TEXT("party celebration occurs after fanfare"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::Celebration);
    TestFalse(TEXT("rewards cannot be dismissed during celebration"),
        Sequence->TryDismissResult(51));
    for(int32 I=0;I<7;++I) Sequence->Advance(.2f);
    TestEqual(TEXT("victory celebration precedes loot screen"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::Rewards);

    UTSTSSJRPGReviewRewards* Ledger=
        NewObject<UTSTSSJRPGReviewRewards>(GetTransientPackage());
    FTSTSSJRPGReviewReward Receipt;
    Receipt.TicketSerial=9876;
    const TArray<FName> ReviewParty={TEXT("Ender"),TEXT("Ionia")};
    TestFalse(TEXT("unknown wave has no reward"),
        Ledger->TryAwardOnce(51,TEXT("Review_UnknownWave"),ReviewParty,Receipt));
    TestFalse(TEXT("unrecruited-only party has no reward"),
        Ledger->TryAwardOnce(51,TEXT("Review_HarborBanditPatrol"),
            {TEXT("Lyra")},Receipt));
    TestEqual(TEXT("failed reward leaves caller receipt alone"),
        Receipt.TicketSerial,9876);
    TestEqual(TEXT("unauthorized reward never changes gold"),
        Ledger->GetGoldBalance(),0);
    TestTrue(TEXT("verified victory review reward awarded"),
        Ledger->TryAwardOnce(51,TEXT("Review_HarborBanditPatrol"),
            ReviewParty,Receipt));
    TestEqual(TEXT("received review gold"),Receipt.GoldEarned,18);
    TestEqual(TEXT("received review XP per active member"),
        Receipt.XpEachPartyMember,12);
    TestEqual(TEXT("received an inventory object"),Receipt.Items.Num(),1);
    TestEqual(TEXT("review wallet updated exactly once"),
        Ledger->GetGoldBalance(),18);
    TestEqual(TEXT("Ender XP ledger updated"),Ledger->GetExperienceTotal(TEXT("Ender")),12);
    TestEqual(TEXT("Ionia XP ledger updated"),Ledger->GetExperienceTotal(TEXT("Ionia")),12);
    TestEqual(TEXT("Lyra never silently awarded"),
        Ledger->GetExperienceTotal(TEXT("Lyra")),0);
    TestEqual(TEXT("loot tracked in inventory ledger"),
        Ledger->GetItemCount(TEXT("Review_SalvagedRope")),1);
    TestFalse(TEXT("same victory ticket cannot be farmed"),
        Ledger->TryAwardOnce(51,TEXT("Review_HarborBanditPatrol"),
            ReviewParty,Receipt));
    TestEqual(TEXT("duplicate reward leaves gold unchanged"),
        Ledger->GetGoldBalance(),18);

    TestTrue(TEXT("Enter only after rewards"),
        Sequence->TryDismissResult(51));
    TestFalse(TEXT("return fade cannot be skipped"),
        Sequence->TryFinishReturn(51));
    for(int32 I=0;I<3;++I) Sequence->Advance(.2f);
    TestEqual(TEXT("return flash before overworld"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::ReturnReady);
    TestTrue(TEXT("finish returns to the exploration state"),
        Sequence->TryFinishReturn(51));
    TestEqual(TEXT("state reset for second encounter"),
        Sequence->GetPhase(),ETSTSSJRPGReviewSequencePhase::Exploration);
    TestFalse(TEXT("old ticket cannot dismiss twice"),
        Sequence->TryDismissResult(51));

    UTSTSSJRPGReviewPresentation* AbortedPresentation=
        NewObject<UTSTSSJRPGReviewPresentation>(GetTransientPackage());
    TestTrue(TEXT("abort path begins"),AbortedPresentation->TryBegin(72));
    TestTrue(TEXT("aborting before battle allowed"),
        AbortedPresentation->TryAbortBeforeCombat(72));
    TestFalse(TEXT("aborted encounter cannot enter combat"),
        AbortedPresentation->TryEnterCombat(72));
    TestTrue(TEXT("aborted control returns idle"),
        AbortedPresentation->GetPhase()==ETSTSSJRPGReviewSequencePhase::Exploration);

    UTSTSSJRPGReviewPresentation* Flee=
        NewObject<UTSTSSJRPGReviewPresentation>(GetTransientPackage());
    TestTrue(TEXT("flee scenario begins"),Flee->TryBegin(73));
    Flee->Advance(.21f);Flee->Advance(.21f);
    Flee->Advance(.18f);Flee->Advance(.18f);
    TestTrue(TEXT("flee scenario enters combat"),Flee->TryEnterCombat(73));
    TestTrue(TEXT("explicit flee begins return without rewards"),
        Flee->TryFlee(73));
    TestEqual(TEXT("flee never passes fanfare/reward screen"),
        Flee->GetPhase(),ETSTSSJRPGReviewSequencePhase::ReturnFlash);
    TestFalse(TEXT("flee cannot be promoted to victory"),
        Flee->TryResolveVictory(73));
    Flee->Advance(.2f);Flee->Advance(.2f);Flee->Advance(.2f);
    TestTrue(TEXT("flee ends with exploration return"),
        Flee->TryFinishReturn(73));
    TestFalse(TEXT("flee never awarded gold"),Ledger->WasTicketAwarded(73));

    UTSTSSJRPGReviewPresentation* Defeated=
        NewObject<UTSTSSJRPGReviewPresentation>(GetTransientPackage());
    TestTrue(TEXT("defeat begins"),Defeated->TryBegin(74));
    Defeated->Advance(.21f);Defeated->Advance(.21f);
    Defeated->Advance(.18f);Defeated->Advance(.18f);
    TestTrue(TEXT("defeat combat admitted"),Defeated->TryEnterCombat(74));
    TestTrue(TEXT("defeat enters result without victory rewards"),
        Defeated->TryResolveDefeat(74));
    TestEqual(TEXT("defeat result screen"),Defeated->GetPhase(),
        ETSTSSJRPGReviewSequencePhase::Defeat);
    TestFalse(TEXT("defeat cannot become victory"),
        Defeated->TryResolveVictory(74));
    TestFalse(TEXT("defeat does not generate reward ticket"),
        Ledger->WasTicketAwarded(74));
    TestTrue(TEXT("defeat can return without rewards"),
        Defeated->TryDismissResult(74));
    Defeated->Advance(.2f);Defeated->Advance(.2f);Defeated->Advance(.2f);
    TestTrue(TEXT("defeat return resolves"),Defeated->TryFinishReturn(74));

    return true;
}
#endif
