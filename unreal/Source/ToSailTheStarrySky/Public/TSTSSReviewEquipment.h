#pragma once

#include "CoreMinimal.h"
#include "TSTSSBattleSkillSystem.h"

// Volatile developer-fixture equipment only. No UPROPERTY, SaveGame, asset grant,
// loot registration, cosmetic attachment, or automatic combat permission.
enum class ETSTSSReviewGearSlot : uint8
{
    Weapon,
    Armor,
    Accessory
};

struct FTSTSSReviewGearInstance
{
    FName InstanceId = NAME_None;
    FName OwnerId = NAME_None;
    ETSTSSReviewGearSlot Slot = ETSTSSReviewGearSlot::Weapon;
    FName WeaponClass = NAME_None;
    int32 AttackBonus = 0;
    int32 DefenseBonus = 0;
};

struct FTSTSSReviewGearSlots
{
    FName WeaponInstance = NAME_None;
    FName ArmorInstance = NAME_None;
    FName AccessoryInstance = NAME_None;
};

struct FTSTSSReviewGearState
{
    // Test-owned instances are supplied by the caller. Neither API grants items.
    TMap<FName, FTSTSSReviewGearInstance> OwnedInstances;
    TMap<FName, FTSTSSReviewGearSlots> EquippedByCharacter;
};

class TOSAILTHESTARRYSKY_API FTSTSSReviewEquipment
{
public:
    // Atomic swap, undo or invalid request. Failed calls preserve OutState.
    static bool TryEquip(
        const FTSTSSReviewGearState& State, FName CharacterId,
        ETSTSSReviewGearSlot Slot, FName RequestedInstance,
        FTSTSSReviewGearState& OutState);

    // One-time *pre-battle* projection from unmodified base roster values.
    // The caller must never project on an already equipped combat snapshot.
    // This is not a live inventory, damage resolver or executable permission.
    static bool TryProjectAtBattleStart(
        const FTSTSSReviewGearState& State,
        const TArray<FTSTSSCombatant>& BaseRoster,
        const FTSTSSBattleSkillKnowledge& BaseKnowledge,
        TArray<FTSTSSCombatant>& OutRoster,
        FTSTSSBattleSkillKnowledge& OutKnowledge);

private:
    static bool Validate(const FTSTSSReviewGearState& State);
};
