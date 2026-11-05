#include "TSTSSEncounterGate.h"

ETSTSSEncounterOutcome FTSTSSEncounterGate::Evaluate(
    const FTSTSSCombatTurnState& State, const TMap<FName, FName>& Factions,
    FName PartyFaction, FName OpponentFaction)
{
    if (PartyFaction.IsNone() || OpponentFaction.IsNone() ||
        PartyFaction == OpponentFaction || State.Order.IsEmpty() ||
        State.Order.Num() != State.Roster.Num()) return ETSTSSEncounterOutcome::Invalid;

    TSet<FName> Seen;
    int32 PartyCount = 0, OpponentCount = 0;
    int32 PartyAlive = 0, OpponentAlive = 0;
    for (const FTSTSSCombatant& Unit : State.Roster)
    {
        if (Unit.CharacterId.IsNone() || Seen.Contains(Unit.CharacterId) ||
            !State.Order.Contains(Unit.CharacterId) || Unit.MaxHealth <= 0 ||
            Unit.Health < 0 || Unit.Health > Unit.MaxHealth ||
            Unit.MaxResource < 0 || Unit.Resource < 0 ||
            Unit.Resource > Unit.MaxResource || Unit.Attack < 0 ||
            Unit.Defense < 0) return ETSTSSEncounterOutcome::Invalid;
        Seen.Add(Unit.CharacterId);
        const FName* Faction = Factions.Find(Unit.CharacterId);
        if (!Faction) return ETSTSSEncounterOutcome::Invalid;
        if (*Faction == PartyFaction) { ++PartyCount; if (Unit.Health > 0) ++PartyAlive; }
        else if (*Faction == OpponentFaction) { ++OpponentCount; if (Unit.Health > 0) ++OpponentAlive; }
        else return ETSTSSEncounterOutcome::Invalid;
    }
    if (PartyCount == 0 || OpponentCount == 0 ||
        State.Cursor < 0 || State.Cursor >= State.Order.Num() ||
        State.Round < 1 || State.AcceptedActions < 0) return ETSTSSEncounterOutcome::Invalid;
    if (PartyAlive == 0 && OpponentAlive == 0) return ETSTSSEncounterOutcome::Draw;
    if (OpponentAlive == 0) return ETSTSSEncounterOutcome::Victory;
    if (PartyAlive == 0) return ETSTSSEncounterOutcome::Defeat;
    return ETSTSSEncounterOutcome::Ongoing;
}

bool FTSTSSEncounterGate::TryAction(
    const FTSTSSCombatTurnState& State, const TMap<FName, FName>& Factions,
    FName PartyFaction, FName OpponentFaction, const FTSTSSCombatAction& Action,
    FTSTSSCombatTurnState& OutState)
{
    if (Evaluate(State, Factions, PartyFaction, OpponentFaction) !=
        ETSTSSEncounterOutcome::Ongoing) return false;
    FTSTSSCombatTurnState Candidate;
    if (!FTSTSSCombatTurns::TryAction(State, Action, Candidate)) return false;
    if (Evaluate(Candidate, Factions, PartyFaction, OpponentFaction) ==
        ETSTSSEncounterOutcome::Invalid) return false;
    OutState = MoveTemp(Candidate);
    return true;
}
