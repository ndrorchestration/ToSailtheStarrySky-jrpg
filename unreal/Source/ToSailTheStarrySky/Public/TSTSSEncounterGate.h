#pragma once

#include "CoreMinimal.h"
#include "TSTSSCombatTurns.h"

// Review-only encounter status. Faction ownership must come from an authorized setup.
enum class ETSTSSEncounterOutcome : uint8 { Invalid, Ongoing, Victory, Defeat, Draw };

class TOSAILTHESTARRYSKY_API FTSTSSEncounterGate
{
public:
    static ETSTSSEncounterOutcome Evaluate(
        const FTSTSSCombatTurnState& State,
        const TMap<FName, FName>& Factions,
        FName PartyFaction,
        FName OpponentFaction);

    static bool TryAction(const FTSTSSCombatTurnState& State,
                          const TMap<FName, FName>& Factions,
                          FName PartyFaction, FName OpponentFaction,
                          const FTSTSSCombatAction& Action,
                          FTSTSSCombatTurnState& OutState);
};
