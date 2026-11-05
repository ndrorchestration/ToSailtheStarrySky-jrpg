#include "Misc/AutomationTest.h"
#include "TSTSSEncounterGate.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSEncounterGateTest,
    "TSTSS.Combat.EncounterCompletion",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSEncounterGateTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Hero;
    Hero.CharacterId = TEXT("Ender"); Hero.Health = 10; Hero.MaxHealth = 10;
    Hero.Resource = 5; Hero.MaxResource = 5;
    FTSTSSCombatant Enemy = Hero;
    Enemy.CharacterId = TEXT("Foe"); Enemy.Health = 2; Enemy.MaxHealth = 2;
    FTSTSSCombatTurnState Initial;
    if (!TestTrue(TEXT("Begin"), FTSTSSCombatTurns::TryBegin(
        {Hero, Enemy}, {TEXT("Ender"), TEXT("Foe")}, Initial))) return false;
    TMap<FName, FName> Factions;
    Factions.Add(TEXT("Ender"), TEXT("crew"));
    Factions.Add(TEXT("Foe"), TEXT("enemy"));
    const FName Crew(TEXT("crew")), Enemies(TEXT("enemy"));
    TestTrue(TEXT("Initially ongoing"),
        FTSTSSEncounterGate::Evaluate(Initial, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Ongoing);

    FTSTSSCombatAction Strike;
    Strike.ActorId = TEXT("Ender"); Strike.TargetId = TEXT("Foe"); Strike.Power = 3;
    FTSTSSCombatTurnState Won;
    if (!TestTrue(TEXT("Lethal action accepted"),
        FTSTSSEncounterGate::TryAction(Initial, Factions, Crew, Enemies, Strike, Won))) return false;
    TestTrue(TEXT("Victory detected"),
        FTSTSSEncounterGate::Evaluate(Won, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Victory);
    FTSTSSCombatTurnState Unchanged = Won;
    TestFalse(TEXT("Victory prevents further actions"),
        FTSTSSEncounterGate::TryAction(Won, Factions, Crew, Enemies, Strike, Unchanged));
    TestEqual(TEXT("Rejected action preserves output"), Unchanged.AcceptedActions, Won.AcceptedActions);
    TestEqual(TEXT("Initial remains unchanged"), Initial.Roster[1].Health, 2);

    FTSTSSCombatTurnState Defeat = Initial;
    Defeat.Roster[0].Health = 0;
    TestTrue(TEXT("Defeat detected"),
        FTSTSSEncounterGate::Evaluate(Defeat, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Defeat);
    FTSTSSCombatTurnState Draw = Defeat;
    Draw.Roster[1].Health = 0;
    TestTrue(TEXT("Draw detected"),
        FTSTSSEncounterGate::Evaluate(Draw, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Draw);
    FTSTSSCombatTurnState BadStats = Initial;
    BadStats.Roster[0].Attack = -1;
    TestTrue(TEXT("Negative attack invalidates encounter"),
        FTSTSSEncounterGate::Evaluate(BadStats, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Invalid);
    BadStats = Initial;
    BadStats.Roster[1].Defense = -1;
    TestTrue(TEXT("Negative defense invalidates encounter"),
        FTSTSSEncounterGate::Evaluate(BadStats, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Invalid);
    FTSTSSCombatTurnState Preserved = Won;
    TestFalse(TEXT("Invalid statistics cannot execute an action"),
        FTSTSSEncounterGate::TryAction(BadStats, Factions, Crew, Enemies, Strike, Preserved));
    TestEqual(TEXT("Invalid-stat action preserves output"), Preserved.AcceptedActions, Won.AcceptedActions);
    Factions.Remove(TEXT("Foe"));
    TestTrue(TEXT("Missing faction rejected"),
        FTSTSSEncounterGate::Evaluate(Initial, Factions, Crew, Enemies) == ETSTSSEncounterOutcome::Invalid);
    return true;
}
#endif
