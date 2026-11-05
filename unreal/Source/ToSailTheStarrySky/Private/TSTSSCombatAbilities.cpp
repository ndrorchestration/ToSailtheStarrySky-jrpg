#include "TSTSSCombatAbilities.h"
#include "TSTSSEncounterGate.h"

bool FTSTSSCombatAbilities::TryUse(
    const FTSTSSCombatTurnState& State, FName ActorId, FName TargetId,
    FName AbilityId, const TMap<FName, FTSTSSAbilitySpec>& Catalog,
    const TMap<FName, TSet<FName>>& Learned,
    const TMap<FName, FName>& Factions,
    FName PartyFaction, FName OpponentFaction,
    FTSTSSCombatTurnState& OutState)
{
    if (ActorId.IsNone() || TargetId.IsNone() || AbilityId.IsNone()) return false;
    const FTSTSSAbilitySpec* Ability = Catalog.Find(AbilityId);
    const TSet<FName>* Known = Learned.Find(ActorId);
    const FName* ActorFaction = Factions.Find(ActorId);
    const FName* TargetFaction = Factions.Find(TargetId);
    if (!Ability || Ability->AbilityId != AbilityId || !Known ||
        !Known->Contains(AbilityId) || !ActorFaction || !TargetFaction ||
        ActorFaction->IsNone() || TargetFaction->IsNone() ||
        Ability->Power < 0 || Ability->Cost < 0) return false;
    const bool bAllies = *ActorFaction == *TargetFaction;
    switch (Ability->Target)
    {
    case FTSTSSAbilitySpec::ETarget::Self:
        if (ActorId != TargetId) return false;
        break;
    case FTSTSSAbilitySpec::ETarget::Ally:
        if (!bAllies) return false;
        break;
    case FTSTSSAbilitySpec::ETarget::Enemy:
        if (bAllies) return false;
        break;
    default: return false;
    }

    FTSTSSCombatAction Action;
    Action.ActorId = ActorId;
    Action.TargetId = TargetId;
    Action.ResourceCost = Ability->Cost;
    Action.Power = Ability->Power;
    Action.bHealing = Ability->bHealing;
    return FTSTSSEncounterGate::TryAction(State, Factions, PartyFaction,
                                        OpponentFaction, Action, OutState);
}
