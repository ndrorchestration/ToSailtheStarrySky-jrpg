#include "Misc/AutomationTest.h"
#include "Combat/TSS_CombatTurnManager.h"
#include "TSTSSCombatData.h"

// Character recruitment is story progression. Three active party slots is a
// full-party battle design contract; the opening must not force unrecruited
// Lyra, Reson, or Aepex into Ender's crew.
#if WITH_DEV_AUTOMATION_TESTS
namespace
{
    FTSS_CombatParticipant MakeRecruitmentFixture(const TCHAR* Id, bool bParty)
    {
        FTSS_CombatParticipant P;
        P.ParticipantId = FName(Id);
        P.Stats.CharacterId = P.ParticipantId;
        P.Stats.Health = 20;
        P.Stats.MaxHealth = 20;
        P.Stats.Resource = 0;
        P.Stats.MaxResource = 0;
        P.Stats.Attack = 1;
        P.Stats.Defense = 0;
        P.Agility = 10;
        P.bIsPlayerParty = bParty;
        // No learned spell, magic school, equipment or invented affinity.
        return P;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSProgressivePartySizeCoexistenceTest,
    "TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSProgressivePartySizeCoexistenceTest::RunTest(const FString& Parameters)
{
    TArray<FTSS_CombatParticipant> Recruited;
    Recruited.Add(MakeRecruitmentFixture(TEXT("Ender"), true));
    const TArray<FTSS_CombatParticipant> Enemies{
        MakeRecruitmentFixture(TEXT("ReviewOpponent"), false)
    };
    const TArray<FName> Solo{FName(TEXT("Ender"))};
    const TArray<FName> Duo{FName(TEXT("Ender")), FName(TEXT("Ionia"))};
    const TArray<FName> Trio{
        FName(TEXT("Ender")), FName(TEXT("Ionia")), FName(TEXT("Lyra"))
    };

    // FTSTSSCombatData validates a complete standard party, not the
    // number of recruited protagonists at each opening-story milestone.
    TArray<FTSTSSDataIssueEntry> Issues;
    TestFalse(TEXT("full-party validator rejects solo"),
              FTSTSSCombatData::ValidateActiveParty(Solo, Issues));
    TestTrue(TEXT("solo yields a recorded validator issue"), !Issues.IsEmpty());
    Issues.Reset();
    TestFalse(TEXT("full-party validator rejects duo"),
              FTSTSSCombatData::ValidateActiveParty(Duo, Issues));
    TestTrue(TEXT("duo yields a recorded validator issue"), !Issues.IsEmpty());
    Issues.Reset();
    TestTrue(TEXT("full-party validator accepts valid trio"),
             FTSTSSCombatData::ValidateActiveParty(Trio, Issues));
    TestTrue(TEXT("trio leaves no validation issues"), Issues.IsEmpty());

    UTSS_CombatTurnManager* Opening = NewObject<UTSS_CombatTurnManager>();
    if (!TestTrue(TEXT("Ender can begin early-story review encounter alone"),
        Opening->InitializeEncounter(Recruited, Solo, Enemies))) return false;
    TestEqual(TEXT("solo encounter has one active player and one opponent"),
              Opening->GetCombatantSnapshot().Num(), 2);
    TestEqual(TEXT("unrecruited characters are not reserves"),
              Opening->GetReservePartyIds().Num(), 0);

    Recruited.Add(MakeRecruitmentFixture(TEXT("Ionia"), true));
    UTSS_CombatTurnManager* AfterIonia = NewObject<UTSS_CombatTurnManager>();
    if (!TestTrue(TEXT("Ionia's recruitment enables two-player review encounter"),
        AfterIonia->InitializeEncounter(Recruited, Duo, Enemies))) return false;
    TestEqual(TEXT("two active players and one opponent"),
              AfterIonia->GetCombatantSnapshot().Num(), 3);
    TestEqual(TEXT("Lyra is not auto-recruited"),
              AfterIonia->GetReservePartyIds().Num(), 0);
    TestFalse(TEXT("unrecruited Lyra cannot be chosen"),
        NewObject<UTSS_CombatTurnManager>()->InitializeEncounter(
            Recruited, Trio, Enemies));

    Recruited.Add(MakeRecruitmentFixture(TEXT("Lyra"), true));
    UTSS_CombatTurnManager* AfterLyra = NewObject<UTSS_CombatTurnManager>();
    if (!TestTrue(TEXT("three recruited players enable normal three-active review"),
        AfterLyra->InitializeEncounter(Recruited, Trio, Enemies))) return false;
    TestEqual(TEXT("three active players and one opponent"),
              AfterLyra->GetCombatantSnapshot().Num(), 4);
    TestEqual(TEXT("no unrecruited fourth/fifth protagonist appears as reserve"),
              AfterLyra->GetReservePartyIds().Num(), 0);

    UTSS_CombatTurnManager* Overflow = NewObject<UTSS_CombatTurnManager>();
    const TArray<FName> InvalidFour{
        FName(TEXT("Ender")), FName(TEXT("Ionia")), FName(TEXT("Lyra")),
        FName(TEXT("Reson"))
    };
    TestFalse(TEXT("four active slots remain disallowed"),
              Overflow->InitializeEncounter(Recruited, InvalidFour, Enemies));
    TestTrue(TEXT("failed overflow leaves turn manager untouched"),
             Overflow->GetCurrentPhase() == ETSS_CombatPhase::NotStarted);
    return true;
}
#endif
