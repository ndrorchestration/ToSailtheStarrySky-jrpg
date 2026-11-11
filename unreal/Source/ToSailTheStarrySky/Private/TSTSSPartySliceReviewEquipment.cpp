#include "TSTSSPartySliceReviewEquipment.h"

namespace
{
    bool AddAndEquip(
        FTSTSSReviewGearState& State, FName Owner, FName ItemId,
        ETSTSSReviewGearSlot Slot, FName WeaponClass, int32 Attack, int32 Defense)
    {
        if (State.OwnedInstances.Contains(ItemId)) return false;
        FTSTSSReviewGearInstance Item;
        Item.InstanceId = ItemId;
        Item.OwnerId = Owner;
        Item.Slot = Slot;
        Item.WeaponClass = WeaponClass;
        Item.AttackBonus = Attack;
        Item.DefenseBonus = Defense;
        State.OwnedInstances.Add(ItemId, Item);
        FTSTSSReviewGearState Candidate;
        if (!FTSTSSReviewEquipment::TryEquip(
                State, Owner, Slot, ItemId, Candidate))
        {
            return false;
        }
        State = MoveTemp(Candidate);
        return true;
    }
}

bool FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
    ETSTSSPartySliceReviewStage Stage, FName CharacterId)
{
    if (Stage != ETSTSSPartySliceReviewStage::FirstWake &&
        Stage != ETSTSSPartySliceReviewStage::AfterSplashdown &&
        Stage != ETSTSSPartySliceReviewStage::LyraRecruited)
    {
        return false;
    }
    return CharacterId == TEXT("Ender") || CharacterId == TEXT("Ionia") ||
        (CharacterId == TEXT("Lyra") &&
         Stage == ETSTSSPartySliceReviewStage::LyraRecruited);
}

bool FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(
    ETSTSSPartySliceReviewStage Stage, FTSTSSReviewGearState& OutState)
{
    if (Stage != ETSTSSPartySliceReviewStage::FirstWake &&
        Stage != ETSTSSPartySliceReviewStage::AfterSplashdown &&
        Stage != ETSTSSPartySliceReviewStage::LyraRecruited) return false;

    FTSTSSReviewGearState Candidate;
    const auto Weapon = ETSTSSReviewGearSlot::Weapon;
    const auto Armor = ETSTSSReviewGearSlot::Armor;
    const auto Accessory = ETSTSSReviewGearSlot::Accessory;

    if (!AddAndEquip(Candidate, TEXT("Ender"), TEXT("Ender.ResonanceStaff"),
            Weapon, TEXT("Staff"), 3, 0) ||
        !AddAndEquip(Candidate, TEXT("Ender"), TEXT("Ender.EngineersVest"),
            Armor, NAME_None, 0, 3) ||
        !AddAndEquip(Candidate, TEXT("Ender"), TEXT("Ender.SealedAviatorGoggles"),
            Accessory, NAME_None, 0, 1) ||
        !AddAndEquip(Candidate, TEXT("Ionia"), TEXT("Ionia.CaptainSaber"),
            Weapon, TEXT("Blade"), 2, 0) ||
        !AddAndEquip(Candidate, TEXT("Ionia"), TEXT("Ionia.CaptainsCoat"),
            Armor, NAME_None, 0, 3) ||
        !AddAndEquip(Candidate, TEXT("Ionia"), TEXT("Ionia.EarthCompass"),
            Accessory, NAME_None, 0, 1))
    {
        return false;
    }

    if (Stage == ETSTSSPartySliceReviewStage::LyraRecruited &&
        (!AddAndEquip(Candidate, TEXT("Lyra"), TEXT("Lyra.WaterFocus"),
             Weapon, TEXT("Focus"), 1, 0) ||
         !AddAndEquip(Candidate, TEXT("Lyra"), TEXT("Lyra.TravelCoat"),
             Armor, NAME_None, 0, 2) ||
         !AddAndEquip(Candidate, TEXT("Lyra"), TEXT("Lyra.WaterPendant"),
             Accessory, NAME_None, 0, 1)))
    {
        return false;
    }

    OutState = MoveTemp(Candidate);
    return true;
}
