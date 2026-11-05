#include "TSTSSCombatTurns.h"

bool FTSTSSCombatTurns::IsValid(const FTSTSSCombatTurnState& State)
{
    if (State.Order.IsEmpty() || State.Order.Num() != State.Roster.Num() ||
        State.Cursor < 0 || State.Cursor >= State.Order.Num() ||
        State.Round < 1 || State.AcceptedActions < 0)
    {
        return false;
    }
    TSet<FName> Seen;
    for (const FName Id : State.Order)
    {
        if (Id.IsNone() || Seen.Contains(Id)) return false;
        Seen.Add(Id);
        int32 Matches = 0;
        for (const FTSTSSCombatant& Unit : State.Roster)
        {
            if (Unit.CharacterId == Id) ++Matches;
        }
        if (Matches != 1) return false;
    }
    for (const FTSTSSCombatant& Unit : State.Roster)
    {
        if (Unit.CharacterId.IsNone() || Unit.MaxHealth <= 0 ||
            Unit.Health < 0 || Unit.Health > Unit.MaxHealth ||
            Unit.MaxResource < 0 || Unit.Resource < 0 ||
            Unit.Resource > Unit.MaxResource || Unit.Attack < 0 || Unit.Defense < 0)
            return false;
    }
    return true;
}

bool FTSTSSCombatTurns::TryBegin(const TArray<FTSTSSCombatant>& Roster,
                                 const TArray<FName>& OrderedIds,
                                 FTSTSSCombatTurnState& OutState)
{
    FTSTSSCombatTurnState Candidate;
    Candidate.Roster = Roster;
    Candidate.Order = OrderedIds;
    if (!IsValid(Candidate)) return false;
    for (const FTSTSSCombatant& Unit : Roster)
    {
        if (Unit.Health <= 0) return false;
    }
    OutState = MoveTemp(Candidate);
    return true;
}

FName FTSTSSCombatTurns::CurrentActor(const FTSTSSCombatTurnState& State)
{
    if (!IsValid(State)) return NAME_None;
    for (int32 Offset = 0; Offset < State.Order.Num(); ++Offset)
    {
        const FName Id = State.Order[(State.Cursor + Offset) % State.Order.Num()];
        for (const FTSTSSCombatant& Unit : State.Roster)
        {
            if (Unit.CharacterId == Id && Unit.Health > 0) return Id;
        }
    }
    return NAME_None;
}

bool FTSTSSCombatTurns::TryAction(const FTSTSSCombatTurnState& State,
                                 const FTSTSSCombatAction& Action,
                                 FTSTSSCombatTurnState& OutState)
{
    const FName Active = CurrentActor(State);
    if (Active.IsNone() || Action.ActorId != Active) return false;
    if (!State.Order.Contains(Action.TargetId)) return false;

    TArray<FTSTSSCombatant> NextRoster;
    if (!UTSTSSCombatRules::TryApplyAction(State.Roster, Action, NextRoster)) return false;

    FTSTSSCombatTurnState Candidate = State;
    Candidate.Roster = MoveTemp(NextRoster);
    const int32 ActorIndex = State.Order.IndexOfByKey(Active);
    Candidate.Cursor = (ActorIndex + 1) % State.Order.Num();
    const FName NextActor = CurrentActor(Candidate);
    if (!NextActor.IsNone())
    {
        const int32 NextIndex = Candidate.Order.IndexOfByKey(NextActor);
        if (NextIndex <= ActorIndex) ++Candidate.Round;
    }
    else if (ActorIndex == State.Order.Num() - 1)
    {
        ++Candidate.Round;
    }
    ++Candidate.AcceptedActions;
    OutState = MoveTemp(Candidate);
    return true;
}
