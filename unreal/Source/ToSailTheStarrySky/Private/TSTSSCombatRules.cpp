#include "TSTSSCombatRules.h"

bool UTSTSSCombatRules::TryApplyAction(const TArray<FTSTSSCombatant>& Roster,
                                      const FTSTSSCombatAction& Action,
                                      TArray<FTSTSSCombatant>& OutRoster)
{
    int32 ActorIndex = INDEX_NONE;
    int32 TargetIndex = INDEX_NONE;
    if (Action.ActorId.IsNone() || Action.TargetId.IsNone() ||
        Action.ResourceCost < 0 || Action.Power < 0)
    {
        return false;
    }

    for (int32 Index = 0; Index < Roster.Num(); ++Index)
    {
        const FTSTSSCombatant& Unit = Roster[Index];
        if (Unit.CharacterId.IsNone() || Unit.MaxHealth <= 0 || Unit.MaxResource < 0 ||
            Unit.Health < 0 || Unit.Health > Unit.MaxHealth ||
            Unit.Resource < 0 || Unit.Resource > Unit.MaxResource ||
            Unit.Attack < 0 || Unit.Defense < 0)
        {
            return false;
        }
        for (int32 Other = 0; Other < Index; ++Other)
        {
            if (Roster[Other].CharacterId == Unit.CharacterId)
            {
                return false;
            }
        }
        if (Unit.CharacterId == Action.ActorId) ActorIndex = Index;
        if (Unit.CharacterId == Action.TargetId) TargetIndex = Index;
    }

    if (ActorIndex == INDEX_NONE || TargetIndex == INDEX_NONE)
    {
        return false;
    }
    const FTSTSSCombatant& Actor = Roster[ActorIndex];
    if (Actor.Health <= 0 || Actor.Resource < Action.ResourceCost)
    {
        return false;
    }
    if (!Action.bHealing && Roster[TargetIndex].Health <= 0)
    {
        return false;
    }

    TArray<FTSTSSCombatant> Next = Roster;
    Next[ActorIndex].Resource -= Action.ResourceCost;
    const int64 Strength = static_cast<int64>(Action.Power) + Actor.Attack;
    if (Action.bHealing)
    {
        const int64 NewHealth = static_cast<int64>(Next[TargetIndex].Health) + Strength;
        Next[TargetIndex].Health = static_cast<int32>(FMath::Min<int64>(
            Next[TargetIndex].MaxHealth, NewHealth));
    }
    else
    {
        const int64 RawDamage = FMath::Max<int64>(
            1, Strength - Next[TargetIndex].Defense);
        Next[TargetIndex].Health = static_cast<int32>(FMath::Max<int64>(
            0, static_cast<int64>(Next[TargetIndex].Health) - RawDamage));
    }
    OutRoster = MoveTemp(Next);
    return true;
}
