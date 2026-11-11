#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSPartySliceReviewEquipment.h"
#include "TSTSSPartyGearMenuReviewWidget.generated.h"

class UButton;
class UTextBlock;

// Opt-in, transient review UI. Not an authoritative inventory or item-grant.
// The game pawn supplies only the verified opening/sea stage; the widget does
// not infer or issue Lyra recruitment, Story beats, combat powers or SaveGame.
UCLASS(Transient, NotBlueprintable)
class TOSAILTHESTARRYSKY_API UTSTSSPartyGearMenuReviewWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    // Rebuilds isolated test gear only by explicit request. No persistence.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Equipment|Review")
    bool TryBeginEquipmentReview(ETSTSSPartySliceReviewStage Stage);

    // Pure, fail-closed review toggle for automation and UI use. On failure
    // OutState remains unchanged and the input State is never modified.
    static bool TryApplyReviewToggle(
        const FTSTSSReviewGearState& State,
        ETSTSSPartySliceReviewStage Stage,
        FName CharacterId,
        ETSTSSReviewGearSlot Slot,
        bool bEquip,
        FTSTSSReviewGearState& OutState);

    // Non-granting refresh for opening -> splashdown only. Existing review
    // equipment choices survive; does not create Lyra's owned items.
    bool TryRefreshStoryStageReview(ETSTSSPartySliceReviewStage RequestedStage);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Equipment|Review")
    void CloseReview();

    UFUNCTION(BlueprintPure, Category="TSTSS|Equipment|Review")
    bool HasReviewState() const { return bInitialized; }

protected:
    virtual void NativeOnInitialized() override;

private:
    ETSTSSPartySliceReviewStage ActiveStage = ETSTSSPartySliceReviewStage::FirstWake;
    FTSTSSReviewGearState ReviewState;
    bool bInitialized = false;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> StageLabel;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> StatusLabel;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UTextBlock>> SlotLabels;

    UPROPERTY(Transient)
    TArray<TObjectPtr<UButton>> SlotButtons;

    void RefreshReviewLabels();
    bool TryToggleSlot(int32 Index);

    UFUNCTION() void ToggleEnderWeapon();
    UFUNCTION() void ToggleEnderArmor();
    UFUNCTION() void ToggleEnderAccessory();
    UFUNCTION() void ToggleIoniaWeapon();
    UFUNCTION() void ToggleIoniaArmor();
    UFUNCTION() void ToggleIoniaAccessory();
    UFUNCTION() void ToggleLyraWeapon();
    UFUNCTION() void ToggleLyraArmor();
    UFUNCTION() void ToggleLyraAccessory();
    UFUNCTION() void OnCloseClicked();
};
