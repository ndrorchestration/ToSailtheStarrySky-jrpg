#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TSTSSPartySliceReviewEquipment.h"
#include "TSTSSPartyGearReviewMountComponent.generated.h"

class UStaticMeshComponent;

UENUM(BlueprintType)
enum class ETSTSSPartyGearPreviewSlot : uint8
{
    Weapon,
    Armor,
    Accessory
};

// REVIEW ONLY: 3D equipment on caller-supplied mesh mounts.
// The actor/Blueprint owns the mount positions; NO rig/socket fit is claimed.
// Explicit opt-in only: never grants gear, advances story or writes SaveGame.
UCLASS(ClassGroup=(TSTSS), meta=(BlueprintSpawnableComponent))
class TOSAILTHESTARRYSKY_API UTSTSSPartyGearReviewMountComponent final : public UActorComponent
{
    GENERATED_BODY()

public:
    UTSTSSPartyGearReviewMountComponent();

    // Caller must independently establish story/recruitment state; this is
    // a review display, not an authoritative recruitment or inventory service.
    // All three components must belong to this actor and be distinct.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Party Equipment|Review")
    bool TryInitializeReviewDisplay(
        FName CharacterId,
        ETSTSSPartySliceReviewStage Stage,
        UStaticMeshComponent* WeaponMount,
        UStaticMeshComponent* ArmorMount,
        UStaticMeshComponent* AccessoryMount);

    // Actually changes the transient owner-checked ledger AND mounted mesh.
    // No asset grants, consumables, skills, class unlocks or persistent changes.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Party Equipment|Review")
    bool TrySetReviewSlotEquipped(ETSTSSPartyGearPreviewSlot Slot, bool bEquip);

    UFUNCTION(BlueprintPure, Category="TSTSS|Party Equipment|Review")
    FName GetReviewCharacterId() const { return ActiveCharacterId; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Party Equipment|Review")
    FName GetEquippedReviewItem(ETSTSSPartyGearPreviewSlot Slot) const;

private:
    UPROPERTY(Transient)
    TObjectPtr<UStaticMeshComponent> WeaponView;

    UPROPERTY(Transient)
    TObjectPtr<UStaticMeshComponent> ArmorView;

    UPROPERTY(Transient)
    TObjectPtr<UStaticMeshComponent> AccessoryView;

    UPROPERTY(Transient)
    FName ActiveCharacterId = NAME_None;

    UPROPERTY(Transient)
    ETSTSSPartySliceReviewStage ActiveStage = ETSTSSPartySliceReviewStage::FirstWake;

    FTSTSSReviewGearState ReviewState;
    bool bReviewInitialized = false;

    UStaticMeshComponent* GetView(ETSTSSPartyGearPreviewSlot Slot) const;
};
