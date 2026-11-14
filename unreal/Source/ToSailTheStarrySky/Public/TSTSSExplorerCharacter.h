#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSExplorerCharacter.generated.h"

UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSExplorerCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ATSTSSExplorerCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
#if !UE_BUILD_SHIPPING
    // Cosmetic aim prompt from the same camera trace and pawn reach as E.
    FString GetReviewAimStatus() const;
#endif
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    UTSTSSFirstWakeState* GetFirstWakeState() const { return FirstWakeState; }
    // Runtime review adapter for ship UI/Blueprint requests. Reports
    // authorization only; does not alter geometry or unlock modes.
    UFUNCTION(BlueprintPure, Category="TSTSS|Ship|Review")
    FName GetActiveReviewShipMode() const
    {
        return IsValid(FirstWakeState) ? FirstWakeState->GetReviewShipMode() : NAME_None;
    }
    UFUNCTION(BlueprintPure, Category="TSTSS|Ship|Review")
    bool CanUseReviewShipMode(FName RequestedMode) const
    {
        return IsValid(FirstWakeState) &&
            FirstWakeState->IsReviewShipModeAuthorized(RequestedMode);
    }
    UFUNCTION(BlueprintCallable, Category="TSTSS|Interaction")
    void Interact();
    UFUNCTION(BlueprintCallable, Category="TSTSS|Save")
    bool SaveFirstWake(const FString& Slot);
    UFUNCTION(BlueprintCallable, Category="TSTSS|Save")
    bool LoadFirstWake(const FString& Slot);
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Camera")
    TObjectPtr<class USpringArmComponent> CameraBoom;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Camera")
    TObjectPtr<class UCameraComponent> FollowCamera;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|First Wake")
    TObjectPtr<UTSTSSFirstWakeState> FirstWakeState;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Interaction")
    float InteractionDistance = 300.f;
private:
#if !UE_BUILD_SHIPPING
    bool HasSupportedReviewFooting(const UWorld* World, const FVector& PawnLocation) const;
    FVector LastSupportedReviewLocation = FVector::ZeroVector;
    bool bHasSupportedReviewLocation = false;
#if WITH_EDITOR
    // Local evidence probes only; never serialized, and never grant a beat.
    FName LastHilltoniaProbeWaypoint = NAME_None;
    float NextHilltoniaProbeTimeSeconds = 0.f;
#endif
#endif
    void MoveForward(float Value);
    void MoveRight(float Value);
    void Turn(float Value);
    void LookUp(float Value);
    void QuickSave();
    void QuickLoad();
    void ShowObjectiveReview();
#if WITH_EDITOR
    void ReviewContinue();
    void ReviewShoreTravel();
    bool SaveReviewContinueBinding(const FString& Slot);
    bool bPendingReviewContinue = false;
    FString PendingReviewContinueDigest;
    float PendingReviewContinueExpireWorldSeconds = 0.f;
    uint64 PendingReviewContinueRestoreGeneration = 0;
    bool bPendingReviewContinueStarted = false;
    ETSTSSFirstWakeBeat PendingReviewContinueBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    uint8 PendingReviewContinueInspectionMask = 0;
#endif
    // PIE reviews never inherit another session's quicksave ownership.
    UPROPERTY(Transient)
    bool bPIEReviewQuickSlotOwned = false;
};
