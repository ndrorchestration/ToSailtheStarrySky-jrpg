#include "Misc/AutomationTest.h"
#include "TSTSSCombatTurns.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSCombatTurnOrderTest,
    "TSTSS.Combat.TurnOrderAndAtomicity",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSCombatTurnOrderTest::RunTest(const FString& Parameters)
{
    FTSTSSCombatant Ender;
    Ender.CharacterId = TEXT("Ender");
    Ender.Health = 20; Ender.MaxHealth = 20;
    Ender.Resource = 5; Ender.MaxResource = 5;
    Ender.Attack = 2;

    FTSTSSCombatant Ionia = Ender;
    Ionia.CharacterId = TEXT("Ionia");

    FTSTSSCombatant Foe = Ender;
    Foe.CharacterId = TEXT("Foe");
    Foe.Health = 3; Foe.MaxHealth = 3;

    const TArray<FTSTSSCombatant> Roster{Ender, Ionia, Foe};
    const TArray<FName> Order{TEXT("Ender"), TEXT("Ionia"), TEXT("Foe")};
    FTSTSSCombatTurnState Initial;
    if (!TestTrue(TEXT("Valid roster starts"), FTSTSSCombatTurns::TryBegin(Roster, Order, Initial))) return false;
    if (!TestEqual(TEXT("Initial roster size"), Initial.Roster.Num(), 3)) return false;
    TestEqual(TEXT("Initial actor"), FTSTSSCombatTurns::CurrentActor(Initial), FName(TEXT("Ender")));

    FTSTSSCombatAction Action;
    Action.ActorId = TEXT("Ionia");
    Action.TargetId = TEXT("Foe");
    Action.Power = 3;
    FTSTSSCombatTurnState Result;
    TestFalse(TEXT("Out of turn rejected"), FTSTSSCombatTurns::TryAction(Initial, Action, Result));
    TestEqual(TEXT("Rejected output unchanged"), Result.AcceptedActions, 0);

    Action.ActorId = TEXT("Ender");
    if (!TestTrue(TEXT("Ender defeats Foe"), FTSTSSCombatTurns::TryAction(Initial, Action, Result))) return false;
    if (!TestEqual(TEXT("Knockout result roster size"), Result.Roster.Num(), 3)) return false;
    TestEqual(TEXT("Ionia follows"), FTSTSSCombatTurns::CurrentActor(Result), FName(TEXT("Ionia")));
    TestEqual(TEXT("Input foe is unaffected"), Initial.Roster[2].Health, 3);
    TestEqual(TEXT("Foe is knocked out"), Result.Roster[2].Health, 0);

    FTSTSSCombatAction Heal;
    Heal.ActorId = TEXT("Ionia");
    Heal.TargetId = TEXT("Ender");
    Heal.bHealing = true;
    Heal.Power = 1;
    FTSTSSCombatTurnState After;
    if (!TestTrue(TEXT("Ionia takes legal turn"), FTSTSSCombatTurns::TryAction(Result, Heal, After))) return false;
    TestEqual(TEXT("Round advances past unconscious final slot"), After.Round, 2);
    TestEqual(TEXT("Next actor wraps to Ender"), FTSTSSCombatTurns::CurrentActor(After), FName(TEXT("Ender")));
    TestEqual(TEXT("Accepted action count"), After.AcceptedActions, 2);

    // Port the Godot sole-survivor regression as a bounded turn-order fixture.
    // Encounter victory/termination authority is not provided by this primitive.
    FTSTSSCombatTurnState Survivor = After;
    Survivor.Roster[1].Health = 0;
    FTSTSSCombatAction SelfHit;
    SelfHit.ActorId = TEXT("Ender");
    SelfHit.TargetId = TEXT("Ender");
    SelfHit.Power = 1;
    FTSTSSCombatTurnState SurvivorNext;
    if (!TestTrue(TEXT("Sole survivor takes a turn"), FTSTSSCombatTurns::TryAction(
        Survivor, SelfHit, SurvivorNext))) return false;
    TestEqual(TEXT("Sole survivor wraps round"), SurvivorNext.Round, 3);
    TestEqual(TEXT("Sole survivor remains current actor"),
        FTSTSSCombatTurns::CurrentActor(SurvivorNext), FName(TEXT("Ender")));
    TestEqual(TEXT("Prior survivor state remains unchanged"), Survivor.Roster[0].Health, 20);
    TestEqual(TEXT("Accepted survivor action recorded"), SurvivorNext.AcceptedActions, 3);

    FTSTSSCombatTurnState BadStart = After;
    TArray<FName> DuplicateOrder{TEXT("Ender"), TEXT("Ender"), TEXT("Foe")};
    TestFalse(TEXT("Duplicate starting participants rejected"),
        FTSTSSCombatTurns::TryBegin(Roster, DuplicateOrder, BadStart));
    TestEqual(TEXT("Rejected begin preserves existing output"), BadStart.AcceptedActions, 2);

    FTSTSSCombatTurnState Invalid = Initial;
    Invalid.Order.Add(TEXT("Ender"));
    FTSTSSCombatTurnState Unchanged = After;
    TestFalse(TEXT("Invalid duplicate order rejected"), FTSTSSCombatTurns::TryAction(Invalid, Action, Unchanged));
    TestEqual(TEXT("Invalid state preserves output"), Unchanged.AcceptedActions, 2);
    // Counter bounds: no signed overflow, no wrapped turn/round authority.
    // A legal action that does not increment Round remains possible at max Round.
    FTSTSSCombatTurnState NearRoundLimit = Initial;
    NearRoundLimit.Round = MAX_int32;
    FTSTSSCombatAction BeforeWrap;
    BeforeWrap.ActorId = TEXT("Ender");
    BeforeWrap.TargetId = TEXT("Foe");
    BeforeWrap.Power = 0;
    FTSTSSCombatTurnState StillMaxRound;
    if (!TestTrue(TEXT("No-wrap action is legal at maximum round"),
        FTSTSSCombatTurns::TryAction(NearRoundLimit, BeforeWrap, StillMaxRound))) return false;
    TestEqual(TEXT("Round is unchanged before wrap"), StillMaxRound.Round, MAX_int32);
    TestEqual(TEXT("Accepted count advances once"), StillMaxRound.AcceptedActions, 1);
    TestEqual(TEXT("Actor advances at max round without wrap"),
              FTSTSSCombatTurns::CurrentActor(StillMaxRound), FName(TEXT("Ionia")));

    FTSTSSCombatTurnState RoundOverflow = Initial;
    RoundOverflow.Cursor = 2;
    RoundOverflow.Round = MAX_int32;
    FTSTSSCombatAction Wrap;
    Wrap.ActorId = TEXT("Foe");
    Wrap.TargetId = TEXT("Ender");
    Wrap.Power = 0;
    FTSTSSCombatTurnState UnchangedBound = After;
    const int32 PreRound = UnchangedBound.Round;
    const int32 PreAccepted = UnchangedBound.AcceptedActions;
    const int32 PreHealth = UnchangedBound.Roster[0].Health;
    TestFalse(TEXT("Maximum round cannot wrap"),
        FTSTSSCombatTurns::TryAction(RoundOverflow, Wrap, UnchangedBound));
    TestEqual(TEXT("Failed round overflow retains output round"), UnchangedBound.Round, PreRound);
    TestEqual(TEXT("Failed round overflow retains accepted actions"), UnchangedBound.AcceptedActions, PreAccepted);
    TestEqual(TEXT("Failed round overflow retains output health"), UnchangedBound.Roster[0].Health, PreHealth);
    TestEqual(TEXT("Round overflow leaves input unchanged"), RoundOverflow.Round, MAX_int32);

    FTSTSSCombatTurnState ActionsOverflow = Initial;
    ActionsOverflow.AcceptedActions = MAX_int32;
    TestFalse(TEXT("Maximum accepted-action counter denies action"),
        FTSTSSCombatTurns::TryAction(ActionsOverflow, BeforeWrap, UnchangedBound));
    TestEqual(TEXT("Failed action-count overflow retains output"), UnchangedBound.AcceptedActions, PreAccepted);
    TestEqual(TEXT("Failed action-count overflow preserves input"), ActionsOverflow.AcceptedActions, MAX_int32);
    return true;
}
#endif
