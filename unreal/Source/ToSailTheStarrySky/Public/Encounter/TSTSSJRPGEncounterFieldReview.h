#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Encounter/TSTSSJRPGEncounterDirector.h"
#include "Enemies/TSTSSSliceEnemyReviewSession.h"
#include "Encounter/TSTSSJRPGReviewRewards.h"
#include "TSTSSJRPGEncounterFieldReview.generated.h"

class UCameraComponent;
class USceneComponent;
class UTextRenderComponent;
class UStaticMeshComponent;
class UTSTSSJRPGEncounterDirector;
class ATSTSSSliceEnemyReviewBattleConsole;
class UTSTSSJRPGReviewPresentation;
class UTSTSSJRPGReviewSequenceHUD;
class USoundBase;

// Self-contained opt-in 3D walking encounter laboratory. Never placed in any
// campaign level, serialized SaveGame, or shipping battle. The reusable
// UTSTSSJRPGEncounterDirector can later be mounted on authorized exploration.
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSJRPGEncounterFieldReview : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSJRPGEncounterFieldReview();

    // Must be explicitly set true by the dedicated V2 review map and also
    // carry the TSTSSReviewOnly actor tag.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Encounters|Review")
    bool bEnableReviewTraversal = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Encounters|Review")
    ETSTSSJRPGEncounterBiome InitialBiome =
        ETSTSSJRPGEncounterBiome::HarborOutskirts;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TrySetReviewBiome(ETSTSSJRPGEncounterBiome Biome);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TrySetReviewPartyStage(ETSTSSSliceReviewPartyStage Stage);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TrySetReviewRate(ETSTSSJRPGEncounterRate Rate);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TryRequestExplicitScriptedWave();

    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TryReturnToExploration();

    // Explicit preview flee, never a production reward/quest outcome.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Encounters|Review")
    bool TryRetreatReviewBattle();

    UFUNCTION(BlueprintPure, Category="TSTSS|Encounters|Review")
    bool IsReviewBattleActive() const { return bInBattle; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Encounters|Review")
    UTSTSSJRPGEncounterDirector* GetEncounterDirector() const
    { return Director.Get(); }

    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Encounters|Review")
    TObjectPtr<USceneComponent> ReviewRoot;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Encounters|Review")
    TObjectPtr<UCameraComponent> ExplorerCamera;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Encounters|Review")
    TObjectPtr<UStaticMeshComponent> ExplorerShape;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Encounters|Review")
    TObjectPtr<UTextRenderComponent> ExplorerMarker;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Encounters|Review")
    TObjectPtr<UTSTSSJRPGEncounterDirector> Director;

    UPROPERTY(Transient)
    TObjectPtr<ATSTSSSliceEnemyReviewBattleConsole> BattleConsole;

    UPROPERTY(Transient)
    TObjectPtr<UTSTSSJRPGReviewPresentation> Presentation;

    UPROPERTY(Transient)
    TObjectPtr<UTSTSSJRPGReviewRewards> RewardLedger;

    UPROPERTY(Transient)
    TObjectPtr<UTSTSSJRPGReviewSequenceHUD> SequenceHUD;

    // Loaded only in the opt-in review world from original, authored review
    // SFX assets. Missing assets suppress sound; no unrelated asset fallback.
    UPROPERTY(Transient) TObjectPtr<USoundBase> EncounterSting;
    UPROPERTY(Transient) TObjectPtr<USoundBase> VictoryFanfare;
    UPROPERTY(Transient) TObjectPtr<USoundBase> RewardReveal;
    UPROPERTY(Transient) TObjectPtr<USoundBase> ReturnWhoosh;

    FTSTSSJRPGReviewReward LastReward;
    FName PendingWave=NAME_None;
    bool bRewardAwarded=false;
    bool bRetreated=false;

    bool bReviewReady=false;
    bool bInBattle=false;
    bool bOutcomeReady=false;
    bool bForward=false;
    bool bBack=false;
    bool bLeft=false;
    bool bRight=false;
    int32 ActiveTicketSerial=0;
    FVector SafeZoneOrigin=FVector::ZeroVector;
    FString LastEncounterMessage;
    ETSTSSSliceReviewPartyStage PartyStage=ETSTSSSliceReviewPartyStage::EnderOnly;
    ETSTSSJRPGEncounterRate EncounterRate=ETSTSSJRPGEncounterRate::Normal;
    ETSTSSJRPGEncounterBiome Biome=ETSTSSJRPGEncounterBiome::HarborOutskirts;
    float MarkerRefreshTimer=0.f;

    FTSTSSJRPGEncounterContext MakeWalkingContext() const;
    bool TryHandoffToBattle(const FTSTSSJRPGEncounterTicket& Ticket);
    void RefreshFieldMarker();
    void EnterReviewCamera();
    void RefreshSequenceHUD();
    void PlayReviewSound(USoundBase* Sound);
    void FinishReturnToField();

    void PressForward(); void ReleaseForward();
    void PressBack(); void ReleaseBack();
    void PressLeft(); void ReleaseLeft();
    void PressRight(); void ReleaseRight();
    void ChooseEnder(); void ChooseIonia(); void ChooseLyra();
    void CycleRate(); void CycleBiome();
    void TriggerScripted();

    void ReturnAfterBattle();
    void StrikePreviewEnemyOne();
    void StrikePreviewEnemyTwo();
    void FleeReviewBattle();
};
