#pragma once

#include "CoreMinimal.h"
#include "TSTSSCombatData.h"
#include "TSTSSBattleSkillSystem.h"

// Safely normalizes data-authoring metadata without providing live gameplay permission.
// Source PR #665 remains authoritative for baseline/order validation; source PR #662
// remains authoritative for learned/mastery/equipment/explicit-admission execution.
class TOSAILTHESTARRYSKY_API FTSTSSCombatSkillReconciliation
{
public:
    // Supported source kinds: Spell and WeaponTechnique only.
    // Other categories require explicit authoring classification, not a guessed JobArt.
    // All outputs are DesignOnly irrespective of CreatorApproved provenance.
    // On failure, OutSkills is unchanged.
    static bool TryPrepareDesignOnly(
        const TArray<FTSTSSActionDefRow>& Actions,
        TMap<FName, FTSTSSBattleSkillRow>& OutSkills);
};
