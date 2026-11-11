#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TSTSSPartySliceReviewEquipment.h"
#include "TSTSSPartyGearMenuReviewWidget.generated.h"

class UButton;
class UTextBlock;
class UVerticalBox;
class UTSTSSFirstWakeState;
class UTSTSSSaveGame;

enum class ETSTSSReviewMenuPage : uint8
{
    Status, Inventory, Equipment, Magic, Skills, Jobs,
    Formation, Journal, Ship, System
};

enum class ETSTSSShipReviewPage : uint8
{
    Overview, Engineering, Configurations, Crew, Navigation, Upgrades, Cargo
};

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

    // Non-granting refresh between First Wake and splashdown (including
    // quickload rewinds). Existing review choices survive, no Lyra grant.
    bool TryRefreshStoryStageReview(ETSTSSPartySliceReviewStage RequestedStage);

    // Read-only story source, never authorizes recruitment or ship transitions.
    bool TryBindFirstWakeStoryForReview(UTSTSSFirstWakeState* State);

    // Only caller-supplied, structurally validated loaded save snapshots
    // matching the active First Wake story may be projected. This is NOT
    // a live combat state, loot grant or SaveGame write.
    static bool TryProjectValidatedSavedRosterForReview(
        const UTSTSSSaveGame* Save,
        ETSTSSPartySliceReviewStage Stage,
        TArray<FTSTSSCombatant>& OutRoster);
    bool TryBindLoadedSaveRosterForReview(const UTSTSSSaveGame* Save);
    void ClearLoadedSaveRosterForReview();

    // Navigable character/system/ship menu. Equipment is the G shortcut.
    void OpenPageForReview(ETSTSSReviewMenuPage Page);

    // The review menu has no executable ship transformation authority.
    static bool IsShipConfigurationSelectableForReview(FName ConfigurationId);

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

    UPROPERTY(Transient)
    TObjectPtr<UVerticalBox> ContentColumn;

    UPROPERTY(Transient)
    TObjectPtr<UTSTSSFirstWakeState> StoryReviewState;

    TArray<FTSTSSCombatant> LoadedSavedRosterSnapshot;
    bool bHasValidLoadedRosterSnapshot = false;

    ETSTSSReviewMenuPage ActivePage = ETSTSSReviewMenuPage::Equipment;
    ETSTSSShipReviewPage ActiveShipPage = ETSTSSShipReviewPage::Overview;

    void RenderReviewPage();
    void RenderEquipmentPage();
    void RenderShipPage();
    void ChangeShipPage(ETSTSSShipReviewPage NewPage);
    void AddPageLine(const FString& Value, int32 Size = 16,
        FLinearColor Color = FLinearColor(0.80f, 0.86f, 0.88f, 1.f),
        float Gap = 9.f);
    void AddPageHeading(const FString& Value);
    UFUNCTION() void OpenStatusTab();
    UFUNCTION() void OpenInventoryTab();
    UFUNCTION() void OpenEquipmentTab();
    UFUNCTION() void OpenMagicTab();
    UFUNCTION() void OpenSkillsTab();
    UFUNCTION() void OpenJobsTab();
    UFUNCTION() void OpenFormationTab();
    UFUNCTION() void OpenJournalTab();
    UFUNCTION() void OpenShipTab();
    UFUNCTION() void OpenSystemTab();
    UFUNCTION() void OpenShipOverview();
    UFUNCTION() void OpenShipEngineering();
    UFUNCTION() void OpenShipConfigurations();
    UFUNCTION() void OpenShipCrew();
    UFUNCTION() void OpenShipNavigation();
    UFUNCTION() void OpenShipUpgrades();
    UFUNCTION() void OpenShipCargo();

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
