#include "Misc/AutomationTest.h"
#include "TSTSSCombatAbilities.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAbilityGateTest,
    "TSTSS.Combat.AbilityAuthorization",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSAbilityGateTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender"); Ender.Health = 10; Ender.MaxHealth = 20;
    Ender.Resource = 5; Ender.MaxResource = 5;
    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = TEXT("Foe"); Foe.Health = 8; Foe.MaxHealth = 8;
    FTSTSSCombatTurnState State;
    if (!TestTrue(TEXT("Begin"), FTSTSSCombatTurns::TryBegin(
        {Ender, Foe}, {TEXT("Ender"), TEXT("Foe")}, State))) return false;
    FTSTSSAbilitySpec Strike;
    Strike.AbilityId = TEXT("Strike"); Strike.Power = 3; Strike.Cost = 2;
    Strike.Target = FTSTSSAbilitySpec::ETarget::Enemy;
    TMap<FName, FTSTSSAbilitySpec> Catalog;
    Catalog.Add(Strike.AbilityId, Strike);
    TMap<FName, TSet<FName>> Learned;
    TMap<FName, FName> Teams;
    Teams.Add(TEXT("Ender"), TEXT("crew")); Teams.Add(TEXT("Foe"), TEXT("enemy"));
    FTSTSSCombatTurnState Output;
    TestFalse(TEXT("Unlearned blocked"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Ender"), TEXT("Foe"), TEXT("Strike"), Catalog, Learned, Teams, TEXT("crew"), TEXT("enemy"), Output));
    Learned.Add(TEXT("Ender"), TSet<FName>{TEXT("Strike")});
    TestFalse(TEXT("Enemy skill cannot target ally"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Ender"), TEXT("Ender"), TEXT("Strike"), Catalog, Learned, Teams, TEXT("crew"), TEXT("enemy"), Output));
    if (!TestTrue(TEXT("Learned enemy skill accepted"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Ender"), TEXT("Foe"), TEXT("Strike"), Catalog, Learned, Teams, TEXT("crew"), TEXT("enemy"), Output))) return false;
    if (!TestTrue(TEXT("Accepted action returns complete roster"), Output.Roster.Num() == 2)) return false;
    TestEqual(TEXT("Target damaged"), Output.Roster[1].Health, 4);
    TestEqual(TEXT("Resource spent"), Output.Roster[0].Resource, 3);
    TestEqual(TEXT("Input preserved"), State.Roster[1].Health, 8);
    // Rejected requests must not overwrite an already accepted result.
    const int32 AcceptedHealth = Output.Roster[1].Health;
    const int32 AcceptedResources = Output.Roster[0].Resource;
    TMap<FName, FName> MissingFaction = Teams;
    MissingFaction.Remove(TEXT("Foe"));
    TestFalse(TEXT("Missing target faction blocked"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Ender"), TEXT("Foe"), TEXT("Strike"), Catalog, Learned, MissingFaction, TEXT("crew"), TEXT("enemy"), Output));
    TestEqual(TEXT("Rejected faction preserves output HP"), Output.Roster[1].Health, AcceptedHealth);

    FTSTSSAbilitySpec Invalid = Strike;
    Invalid.Cost = -1;
    Catalog.Add(TEXT("Strike"), Invalid);
    TestFalse(TEXT("Negative ability cost blocked"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Ender"), TEXT("Foe"), TEXT("Strike"), Catalog, Learned, Teams, TEXT("crew"), TEXT("enemy"), Output));
    TestEqual(TEXT("Rejected spec preserves resources"), Output.Roster[0].Resource, AcceptedResources);

    Catalog.Add(TEXT("Strike"), Strike);
    TMap<FName, TSet<FName>> FoeLearned;
    FoeLearned.Add(TEXT("Foe"), TSet<FName>{TEXT("Strike")});
    TestFalse(TEXT("Out-of-turn actor blocked"), FTSTSSCombatAbilities::TryUse(
        State, TEXT("Foe"), TEXT("Ender"), TEXT("Strike"), Catalog,
        FoeLearned, Teams, TEXT("crew"), TEXT("enemy"), Output));
    TestEqual(TEXT("Out-of-turn rejection preserves output"), Output.Roster[1].Health, AcceptedHealth);
    TestEqual(TEXT("Input turn remains unchanged"), State.AcceptedActions, 0);
    FTSTSSCombatTurnState Finished = Output;
    Finished.Roster[1].Health = 0;
    FTSTSSCombatTurnState TerminalOutput = Output;
    TestFalse(TEXT("Completed encounter blocks learned ability"),
        FTSTSSCombatAbilities::TryUse(Finished, TEXT("Ender"), TEXT("Foe"),
            TEXT("Strike"), Catalog, Learned, Teams, TEXT("crew"), TEXT("enemy"), TerminalOutput));
    TestEqual(TEXT("Terminal rejection preserves output"), TerminalOutput.AcceptedActions, Output.AcceptedActions);

    return true;
}
#endif
