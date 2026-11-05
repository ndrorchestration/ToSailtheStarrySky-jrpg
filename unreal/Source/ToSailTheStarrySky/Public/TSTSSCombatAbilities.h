#pragma once

#include "CoreMinimal.h"
#include "TSTSSCombatTurns.h"

// Review-only, data-driven ability permission gate. The owning progression system
// must provide learned abilities and faction assignments explicitly.
struct FTSTSSAbilitySpec
{
    FName AbilityId = NAME_None;
    int32 Power = 0;
    int32 Cost = 0;
    bool bHealing = false;
    enum class ETarget : uint8 { Self, Ally, Enemy } Target = ETarget::Enemy;
};

class TOSAILTHESTARRYSKY_API FTSTSSCombatAbilities
{
public:
    static bool TryUse(const FTSTSSCombatTurnState& State, FName ActorId,
                       FName TargetId, FName AbilityId,
                       const TMap<FName, FTSTSSAbilitySpec>& Catalog,
                       const TMap<FName, TSet<FName>>& Learned,
                       const TMap<FName, FName>& Factions,
                       FName PartyFaction, FName OpponentFaction,
                       FTSTSSCombatTurnState& OutState);
};
