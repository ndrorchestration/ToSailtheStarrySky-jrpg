#include "TSTSSPartyGearReviewMountComponent.h"

#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Actor.h"
#include "UObject/UObjectGlobals.h"

namespace
{
    ETSTSSReviewGearSlot ToLedgerSlot(ETSTSSPartyGearPreviewSlot Slot)
    {
        switch (Slot)
        {
        case ETSTSSPartyGearPreviewSlot::Weapon: return ETSTSSReviewGearSlot::Weapon;
        case ETSTSSPartyGearPreviewSlot::Armor: return ETSTSSReviewGearSlot::Armor;
        case ETSTSSPartyGearPreviewSlot::Accessory: return ETSTSSReviewGearSlot::Accessory;
        default: return static_cast<ETSTSSReviewGearSlot>(255);
        }
    }

    FName EquippedId(const FTSTSSReviewGearSlots& Slots, ETSTSSPartyGearPreviewSlot Slot)
    {
        switch (Slot)
        {
        case ETSTSSPartyGearPreviewSlot::Weapon: return Slots.WeaponInstance;
        case ETSTSSPartyGearPreviewSlot::Armor: return Slots.ArmorInstance;
        case ETSTSSPartyGearPreviewSlot::Accessory: return Slots.AccessoryInstance;
        default: return NAME_None;
        }
    }

    // Allowlist, never an arbitrary user/Blueprint-controlled asset path.
    const TCHAR* ItemSuffix(FName Owner, ETSTSSPartyGearPreviewSlot Slot)
    {
        if (Owner == TEXT("Ender"))
        {
            switch (Slot)
            {
            case ETSTSSPartyGearPreviewSlot::Weapon: return TEXT("ResonanceStaff");
            case ETSTSSPartyGearPreviewSlot::Armor: return TEXT("EngineersVest");
            case ETSTSSPartyGearPreviewSlot::Accessory: return TEXT("SealedAviatorGoggles");
            default: return nullptr;
            }
        }
        if (Owner == TEXT("Ionia"))
        {
            switch (Slot)
            {
            case ETSTSSPartyGearPreviewSlot::Weapon: return TEXT("CaptainSaber");
            case ETSTSSPartyGearPreviewSlot::Armor: return TEXT("CaptainsCoat");
            case ETSTSSPartyGearPreviewSlot::Accessory: return TEXT("EarthCompass");
            default: return nullptr;
            }
        }
        if (Owner == TEXT("Lyra"))
        {
            switch (Slot)
            {
            case ETSTSSPartyGearPreviewSlot::Weapon: return TEXT("WaterFocus");
            case ETSTSSPartyGearPreviewSlot::Armor: return TEXT("TravelCoat");
            case ETSTSSPartyGearPreviewSlot::Accessory: return TEXT("WaterPendant");
            default: return nullptr;
            }
        }
        return nullptr;
    }

    UStaticMesh* FindReviewedMesh(FName CharacterId, ETSTSSPartyGearPreviewSlot Slot)
    {
        const TCHAR* Suffix = ItemSuffix(CharacterId, Slot);
        if (!Suffix) return nullptr;
        const FString Owner = CharacterId.ToString();
        const FString AssetName = Owner + TEXT("_") + Suffix + TEXT("_REVIEW");
        const FString AssetPath = FString::Printf(
            TEXT("/Game/TSTSS/Review/PartyEquipment/%s/%s/StaticMeshes/%s.%s"),
            *Owner, *AssetName, *AssetName, *AssetName);
        return LoadObject<UStaticMesh>(nullptr, *AssetPath);
    }

    bool IsOwnedMount(AActor* Actor, const UStaticMeshComponent* View)
    {
        return IsValid(Actor) && IsValid(View) && View->GetOwner() == Actor;
    }
}

UTSTSSPartyGearReviewMountComponent::UTSTSSPartyGearReviewMountComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

UStaticMeshComponent* UTSTSSPartyGearReviewMountComponent::GetView(
    ETSTSSPartyGearPreviewSlot Slot) const
{
    switch (Slot)
    {
    case ETSTSSPartyGearPreviewSlot::Weapon: return WeaponView.Get();
    case ETSTSSPartyGearPreviewSlot::Armor: return ArmorView.Get();
    case ETSTSSPartyGearPreviewSlot::Accessory: return AccessoryView.Get();
    default: return nullptr;
    }
}

FName UTSTSSPartyGearReviewMountComponent::GetEquippedReviewItem(
    ETSTSSPartyGearPreviewSlot Slot) const
{
    if (!bReviewInitialized || !FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
            ActiveStage, ActiveCharacterId) || !GetView(Slot))
    {
        return NAME_None;
    }
    const FTSTSSReviewGearSlots* Slots = ReviewState.EquippedByCharacter.Find(ActiveCharacterId);
    return Slots ? EquippedId(*Slots, Slot) : NAME_None;
}

bool UTSTSSPartyGearReviewMountComponent::TryInitializeReviewDisplay(
    FName CharacterId, ETSTSSPartySliceReviewStage Stage,
    UStaticMeshComponent* WeaponMount,
    UStaticMeshComponent* ArmorMount,
    UStaticMeshComponent* AccessoryMount)
{
    if (!FTSTSSPartySliceReviewEquipment::IsMemberAvailable(Stage, CharacterId) ||
        !IsOwnedMount(GetOwner(), WeaponMount) ||
        !IsOwnedMount(GetOwner(), ArmorMount) ||
        !IsOwnedMount(GetOwner(), AccessoryMount) ||
        WeaponMount == ArmorMount || WeaponMount == AccessoryMount ||
        ArmorMount == AccessoryMount)
    {
        return false;
    }

    FTSTSSReviewGearState Candidate;
    if (!FTSTSSPartySliceReviewEquipment::TryBuildEquippedReviewFixture(Stage, Candidate))
        return false;
    const FTSTSSReviewGearSlots* Slots = Candidate.EquippedByCharacter.Find(CharacterId);
    if (!Slots || Slots->WeaponInstance.IsNone() ||
        Slots->ArmorInstance.IsNone() || Slots->AccessoryInstance.IsNone())
        return false;

    UStaticMesh* Assets[3] = {
        FindReviewedMesh(CharacterId, ETSTSSPartyGearPreviewSlot::Weapon),
        FindReviewedMesh(CharacterId, ETSTSSPartyGearPreviewSlot::Armor),
        FindReviewedMesh(CharacterId, ETSTSSPartyGearPreviewSlot::Accessory)
    };
    if (!Assets[0] || !Assets[1] || !Assets[2]) return false;

    // Do not mutate the display or inventory until all ownership and assets
    // validate. Roll back an engine-level assignment failure.
    UStaticMeshComponent* Views[3] = {WeaponMount, ArmorMount, AccessoryMount};
    UStaticMesh* Previous[3] = {
        Views[0]->GetStaticMesh(), Views[1]->GetStaticMesh(), Views[2]->GetStaticMesh()
    };
    for (int32 Index=0; Index<3; ++Index)
    {
        if (!Views[Index]->SetStaticMesh(Assets[Index]))
        {
            for (int32 Rollback=0; Rollback<=Index; ++Rollback)
                Views[Rollback]->SetStaticMesh(Previous[Rollback]);
            return false;
        }
    }

    ReviewState = MoveTemp(Candidate);
    ActiveCharacterId = CharacterId;
    ActiveStage = Stage;
    WeaponView = WeaponMount;
    ArmorView = ArmorMount;
    AccessoryView = AccessoryMount;
    bReviewInitialized = true;
    return true;
}

bool UTSTSSPartyGearReviewMountComponent::TrySetReviewSlotEquipped(
    ETSTSSPartyGearPreviewSlot Slot, bool bEquip)
{
    UStaticMeshComponent* View = GetView(Slot);
    if (!bReviewInitialized || !IsOwnedMount(GetOwner(), View) ||
        !FTSTSSPartySliceReviewEquipment::IsMemberAvailable(ActiveStage, ActiveCharacterId))
        return false;
    const FTSTSSReviewGearSlots* Current = ReviewState.EquippedByCharacter.Find(ActiveCharacterId);
    if (!Current) return false;

    const FName ExistingId = EquippedId(*Current, Slot);
    const TCHAR* Suffix = ItemSuffix(ActiveCharacterId, Slot);
    if (!Suffix) return false;
    const FName DesiredId = bEquip
        ? FName(*(ActiveCharacterId.ToString() + TEXT(".") + Suffix))
        : NAME_None;
    if (ExistingId == DesiredId) return false;

    FTSTSSReviewGearState Candidate;
    if (!FTSTSSReviewEquipment::TryEquip(
        ReviewState, ActiveCharacterId, ToLedgerSlot(Slot), DesiredId, Candidate))
        return false;

    UStaticMesh* NextMesh = bEquip ? FindReviewedMesh(ActiveCharacterId, Slot) : nullptr;
    if (bEquip && !NextMesh) return false;
    if (!View->SetStaticMesh(NextMesh)) return false;

    ReviewState = MoveTemp(Candidate);
    return true;
}

bool UTSTSSPartyGearReviewMountComponent::TryAttachToSkeletalSocketsReview(
    USkeletalMeshComponent* Rig,
    FName WeaponSocket, FName ArmorSocket, FName AccessorySocket)
{
    UStaticMeshComponent* Views[3] = {
        WeaponView.Get(), ArmorView.Get(), AccessoryView.Get()
    };
    const FName Sockets[3] = {
        WeaponSocket, ArmorSocket, AccessorySocket
    };
    if (!bReviewInitialized || !IsValid(Rig) ||
        Rig->GetOwner() != GetOwner() || !Rig->IsRegistered() ||
        !IsValid(Rig->GetSkeletalMeshAsset()) ||
        !FTSTSSPartySliceReviewEquipment::IsMemberAvailable(
            ActiveStage, ActiveCharacterId) ||
        Sockets[0].IsNone() || Sockets[1].IsNone() || Sockets[2].IsNone() ||
        Sockets[0] == Sockets[1] || Sockets[0] == Sockets[2] ||
        Sockets[1] == Sockets[2])
    {
        return false;
    }

    for (int32 Index=0; Index<3; ++Index)
    {
        if (!IsOwnedMount(GetOwner(), Views[Index]) ||
            !Views[Index]->IsRegistered() ||
            !Rig->DoesSocketExist(Sockets[Index]))
        {
            return false;
        }
    }
    // Validate all three sockets and owners before attempting a scene mutation.
    // Preserve parents and local transforms in case a component rejects attach.
    USceneComponent* PreviousParents[3];
    FName PreviousSockets[3];
    FTransform PreviousTransforms[3];
    for (int32 Index=0; Index<3; ++Index)
    {
        PreviousParents[Index] = Views[Index]->GetAttachParent();
        PreviousSockets[Index] = Views[Index]->GetAttachSocketName();
        PreviousTransforms[Index] = Views[Index]->GetRelativeTransform();
    }

    for (int32 Index=0; Index<3; ++Index)
    {
        if (!Views[Index]->AttachToComponent(
            Rig, FAttachmentTransformRules::SnapToTargetNotIncludingScale,
            Sockets[Index]))
        {
            for (int32 Rollback=0; Rollback<=Index; ++Rollback)
            {
                if (PreviousParents[Rollback])
                {
                    Views[Rollback]->AttachToComponent(
                        PreviousParents[Rollback],
                        FAttachmentTransformRules::KeepRelativeTransform,
                        PreviousSockets[Rollback]);
                }
                else
                {
                    Views[Rollback]->DetachFromComponent(
                        FDetachmentTransformRules::KeepRelativeTransform);
                }
                Views[Rollback]->SetRelativeTransform(PreviousTransforms[Rollback]);
            }
            return false;
        }
    }
    return true;
}
