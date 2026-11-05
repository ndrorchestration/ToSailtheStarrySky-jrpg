#pragma once

#include "CoreMinimal.h"
#include "TSTSSCombatRules.h"

// Isolated, deterministic turn authority. No world, encounter, or UI permission.
struct FTSTSSCombatTurnState
{
    TArray<FTSTSSCombatant> Roster;
    TArray<FName> Order;
    int32 Cursor = 0;
    int32 Round = 1;
    int32 AcceptedActions = 0;
};

class TOSAILTHESTARRYSKY_API FTSTSSCombatTurns
{
public:
    static bool TryBegin(const TArray<FTSTSSCombatant>& Roster,
                         const TArray<FName>& OrderedIds,
                         FTSTSSCombatTurnState& OutState);
    static FName CurrentActor(const FTSTSSCombatTurnState& State);
    static bool TryAction(const FTSTSSCombatTurnState& State,
                          const FTSTSSCombatAction& Action,
                          FTSTSSCombatTurnState& OutState);

private:
    static bool IsValid(const FTSTSSCombatTurnState& State);
};
