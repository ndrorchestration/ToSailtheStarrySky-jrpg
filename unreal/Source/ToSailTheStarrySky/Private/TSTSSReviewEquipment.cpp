#include "TSTSSReviewEquipment.h"
#include "TSTSSJobClassSystem.h"

namespace
{
    FName* MutableSlot(FTSTSSReviewGearSlots& Slots, ETSTSSReviewGearSlot Slot)
    {
        switch (Slot)
        {
        case ETSTSSReviewGearSlot::Weapon: return &Slots.WeaponInstance;
        case ETSTSSReviewGearSlot::Armor: return &Slots.ArmorInstance;
        case ETSTSSReviewGearSlot::Accessory: return &Slots.AccessoryInstance;
        default: return nullptr;
        }
    }

    bool CheckEquippedInstance(
        FName CharacterId, FName InstanceId, ETSTSSReviewGearSlot Slot,
        const FTSTSSReviewGearState& State, TSet<FName>& Seen)
    {
        if (InstanceId.IsNone()) return true;
        if (Seen.Contains(InstanceId)) return false;
        const FTSTSSReviewGearInstance* Item = State.OwnedInstances.Find(InstanceId);
        if (!Item || Item->OwnerId != CharacterId || Item->Slot != Slot) return false;
        Seen.Add(InstanceId);
        return true;
    }
}

bool FTSTSSReviewEquipment::Validate(const FTSTSSReviewGearState& State)
{
    for (const TPair<FName, FTSTSSReviewGearInstance>& Pair : State.OwnedInstances)
    {
        const FTSTSSReviewGearInstance& Item = Pair.Value;
        if (Pair.Key.IsNone() || Item.InstanceId != Pair.Key ||
            !FTSTSSJobClassSystem::IsProtagonist(Item.OwnerId) ||
            Item.AttackBonus < 0 || Item.AttackBonus > 30 ||
            Item.DefenseBonus < 0 || Item.DefenseBonus > 30)
        {
            return false;
        }
        switch (Item.Slot)
        {
        case ETSTSSReviewGearSlot::Weapon:
            if (Item.WeaponClass.IsNone()) return false;
            break;
        case ETSTSSReviewGearSlot::Armor:
        case ETSTSSReviewGearSlot::Accessory:
            if (!Item.WeaponClass.IsNone()) return false;
            break;
        default:
            return false;
        }
    }

    TSet<FName> Seen;
    for (const TPair<FName, FTSTSSReviewGearSlots>& Pair : State.EquippedByCharacter)
    {
        if (!FTSTSSJobClassSystem::IsProtagonist(Pair.Key) ||
            !CheckEquippedInstance(Pair.Key, Pair.Value.WeaponInstance,
                ETSTSSReviewGearSlot::Weapon, State, Seen) ||
            !CheckEquippedInstance(Pair.Key, Pair.Value.ArmorInstance,
                ETSTSSReviewGearSlot::Armor, State, Seen) ||
            !CheckEquippedInstance(Pair.Key, Pair.Value.AccessoryInstance,
                ETSTSSReviewGearSlot::Accessory, State, Seen))
        {
            return false;
        }
    }
    return true;
}

bool FTSTSSReviewEquipment::TryEquip(
    const FTSTSSReviewGearState& State, FName CharacterId,
    ETSTSSReviewGearSlot Slot, FName RequestedInstance,
    FTSTSSReviewGearState& OutState)
{
    if (!Validate(State) || !FTSTSSJobClassSystem::IsProtagonist(CharacterId))
        return false;

    if (!RequestedInstance.IsNone())
    {
        const FTSTSSReviewGearInstance* Item = State.OwnedInstances.Find(RequestedInstance);
        if (!Item || Item->OwnerId != CharacterId || Item->Slot != Slot) return false;
    }

    FTSTSSReviewGearState Candidate = State;
    FName* Current = MutableSlot(Candidate.EquippedByCharacter.FindOrAdd(CharacterId), Slot);
    if (!Current || *Current == RequestedInstance) return false;
    *Current = RequestedInstance;
    if (!Validate(Candidate)) return false;

    OutState = MoveTemp(Candidate);
    return true;
}

bool FTSTSSReviewEquipment::TryProjectAtBattleStart(
    const FTSTSSReviewGearState& State,
    const TArray<FTSTSSCombatant>& BaseRoster,
    const FTSTSSBattleSkillKnowledge& BaseKnowledge,
    TArray<FTSTSSCombatant>& OutRoster,
    FTSTSSBattleSkillKnowledge& OutKnowledge)
{
    if (!Validate(State) || BaseRoster.IsEmpty()) return false;
    TArray<FTSTSSCombatant> Candidate = BaseRoster;
    FTSTSSBattleSkillKnowledge NextKnowledge = BaseKnowledge;
    TSet<FName> SeenActors;
    for (FTSTSSCombatant& Unit : Candidate)
    {
        if (Unit.CharacterId.IsNone() || SeenActors.Contains(Unit.CharacterId) ||
            Unit.MaxHealth <= 0 || Unit.Health < 0 || Unit.Health > Unit.MaxHealth ||
            Unit.MaxResource < 0 || Unit.Resource < 0 || Unit.Resource > Unit.MaxResource ||
            Unit.Attack < 0 || Unit.Defense < 0) return false;
        SeenActors.Add(Unit.CharacterId);
        if (!FTSTSSJobClassSystem::IsProtagonist(Unit.CharacterId)) continue;

        // Explicitly replace any caller-supplied weapon-class claim with verified
        // gear evidence; learned skills/mastery stay untouched.
        NextKnowledge.WeaponClassByActor.Remove(Unit.CharacterId);
        const FTSTSSReviewGearSlots* Slots = State.EquippedByCharacter.Find(Unit.CharacterId);
        if (!Slots) continue;

        int64 Attack = Unit.Attack;
        int64 Defense = Unit.Defense;
        const FName Instances[] =
            {Slots->WeaponInstance, Slots->ArmorInstance, Slots->AccessoryInstance};
        for (const FName Instance : Instances)
        {
            if (Instance.IsNone()) continue;
            const FTSTSSReviewGearInstance& Item = State.OwnedInstances.FindChecked(Instance);
            Attack += Item.AttackBonus;
            Defense += Item.DefenseBonus;
            if (Item.Slot == ETSTSSReviewGearSlot::Weapon)
                NextKnowledge.WeaponClassByActor.Add(Unit.CharacterId, Item.WeaponClass);
        }
        if (Attack > MAX_int32 || Defense > MAX_int32) return false;
        Unit.Attack = static_cast<int32>(Attack);
        Unit.Defense = static_cast<int32>(Defense);
    }

    OutRoster = MoveTemp(Candidate);
    OutKnowledge = MoveTemp(NextKnowledge);
    return true;
}
