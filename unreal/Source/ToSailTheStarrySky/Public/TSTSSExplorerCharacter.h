#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TSTSSFirstWakeState.h"
#include "TimerManager.h"
#include "TSTSSExplorerCharacter.generated.h"

class USkeletalMesh;
class UAnimSequence;
class UStaticMesh;
class UStaticMeshComponent;

UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSExplorerCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    ATSTSSExplorerCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaSeconds) override;
#if !UE_BUILD_SHIPPING
    // Cosmetic aim prompt from the same camera trace and pawn reach as E.
    FString GetReviewAimStatus() const;
#if WITH_EDITOR
    bool HasHilltoniaOpening() const { return bHilltoniaOpeningActive; }
    bool IsHilltoniaFlyerOpen() const;
    bool GetHilltoniaCaptainWaypoint(FVector& Location) const;
    bool GetEngineeringIntercomCaption(FString& Subtitle, FString& NextCheck) const;
#endif
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
#if WITH_EDITORONLY_DATA
    // Explicitly assigned by a PRIVATE, editor-only review Blueprint.
    // Unset by default; never points at a canonical or packaged character.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<USkeletalMesh> EnderSliceReviewBody;
    // Imported privately with proven game rights; never bundled or enabled by default.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<UStaticMesh> EnderSliceReviewHair;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<UStaticMesh> EnderSliceReviewGoggles;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<UStaticMesh> EnderSliceReviewStaff;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    bool bShowEnderReviewHair = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    bool bShowEnderReviewGoggles = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    bool bShowEnderReviewStaff = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FName EnderReviewHeadBone = TEXT("head");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FName EnderReviewGripBone = TEXT("l_hand");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FTransform EnderReviewHairLocalOffset = FTransform::Identity;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FTransform EnderReviewGogglesLocalOffset = FTransform::Identity;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FTransform EnderReviewStaffLocalOffset = FTransform::Identity;
    // Three explicit PRIVATE, matching-skeleton clips (in-place or opt-in
    // extract-and-discard root motion). None are
    // assigned by default; preview is opt-in and never production locomotion.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Animation")
    bool bEnableEnderPIELocomotionPreview = false;
    // Explicit PRIVATE opt-in: extract-and-discard source root motion; never move capsule.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Animation")
    bool bAllowEnderPIERootMotionExtractionReview = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Animation")
    TSoftObjectPtr<UAnimSequence> EnderPIEIdleAnimation;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Animation")
    TSoftObjectPtr<UAnimSequence> EnderPIEWalkAnimation;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Animation")
    TSoftObjectPtr<UAnimSequence> EnderPIERunAnimation;
    // Transient references survive PIE garbage collection but never persist.
    UPROPERTY(Transient)
    TObjectPtr<UAnimSequence> EnderPIEIdleLoaded;
    UPROPERTY(Transient)
    TObjectPtr<UAnimSequence> EnderPIEWalkLoaded;
    UPROPERTY(Transient)
    TObjectPtr<UAnimSequence> EnderPIERunLoaded;
    // Opt-in, editor-only review input. Never changes shipping movement.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview|Movement")
    bool bEnableEnderPIEWalkRunControls = false;
#endif
private:
#if WITH_EDITORONLY_DATA
    // Inert hidden review components; never production character equipment.
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Ender|SliceReview")
    TObjectPtr<UStaticMeshComponent> EnderReviewHairComponent;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Ender|SliceReview")
    TObjectPtr<UStaticMeshComponent> EnderReviewGogglesComponent;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Ender|SliceReview")
    TObjectPtr<UStaticMeshComponent> EnderReviewStaffComponent;
#endif
#if WITH_EDITOR
    void ApplyEnderSliceReviewAppearance();
    void TryEnderPIELocomotionPreview(uint8 MotionBand);
    void PressEnderPIEReviewSprint();
    void ReleaseEnderPIEReviewSprint();
    void TryEnderPIEWalkRunControls();
    void RestoreEnderPIEWalkRunControls();
    bool bEnderPIEWalkRunChecked = false;
    bool bEnderPIEWalkRunActive = false;
    bool bEnderPIESprintHeld = false;
    float EnderPIEOriginalMaxWalkSpeed = 0.f;
    float EnderPIELastAssignedMaxWalkSpeed = 0.f;
    bool bEnderPIEAnimPreviewChecked = false;
    bool bEnderPIEAnimPreviewActive = false;
    bool bEnderPIERootMotionExtractionActive = false;
    uint8 LastEnderPIEAnimBand = 255;
#endif
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
    // Retry only while the runtime-instanced WorldStatic road settles;
    // a failed admission never grants a story beat or a player teleport.
    bool StartHilltoniaOpening(UWorld* World);
    void SetupFirstWakeThirdPersonReview(UWorld* World);
    void ToggleFirstWakeBokehReview();
    void UpdateFirstWakeBokehReview(float DeltaSeconds);
    bool bFirstWakeThirdPersonReview = false;
    float EnderCameraSweepElapsed = 0.f;
    bool bEnderCameraSweepLogged = false;
    // Runtime-only diagnostic state; never serialized or enabled in shipping.
    bool bEnderPIEPossessionLogged = false;
    uint8 LastEnderPIEMotionBand = 255;
    bool bFirstWakeBokehReview = false;
    float FirstWakeReviewFstop = 9.f;
    void AcceptHilltoniaFlyer();
    void DeclineHilltoniaFlyer();
    bool IsHilltoniaFlyerHit(const FHitResult& Hit) const;
    bool bTryHilltoniaOpening = false;
    uint8 HilltoniaOpeningAttemptCount = 0;
    bool bHilltoniaOpeningActive = false;
    bool bHilltoniaFlyerRead = false;
    // Explicitly flagged PIE-only native Enter input probe; not save/state authority.
    uint8 PrivateFlyerKeyProbePhase = 0;
    uint64 HilltoniaFlyerGeneration = 0;
    FVector HilltoniaFlyerHit = FVector::ZeroVector;
    TWeakObjectPtr<class ATSTSSMilestoneActor> HilltoniaCaptain;
    // Cosmetic, current-pawn caption only. Never serialized or story authority.
    FString FirstWakeIntercomSubtitle;
    FString FirstWakeIntercomNextCheck;
    float FirstWakeIntercomStartedSeconds = 0.f;
    float FirstWakeIntercomExpiresSeconds = 0.f;
    uint64 FirstWakeIntercomGeneration = 0;
    ETSTSSFirstWakeBeat FirstWakeIntercomBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    uint8 FirstWakeIntercomMask = 0;
    void ReviewShoreTravel();
    void ReviewOpticalInspectionTravel();
    void ToggleEngineFocusPreview();
    void VerifyEngineFocusPreview();
    void RestoreEngineFocusPreview();
    TWeakObjectPtr<class ACineCameraActor> EngineFocusPreviewCamera;
    TWeakObjectPtr<class APlayerController> EngineFocusPreviewController;
    FTimerHandle EngineFocusPreviewGuardTimer;
    double EngineFocusPreviewStartedSeconds = 0.0;
    double EngineFocusPreviewDeadlineSeconds = 0.0;
    bool bEngineFocusPreviewOwnsCoordinatorEnable = false;
    bool bEngineFocusPreviewIgnoredMove = false;
    bool bEngineFocusPreviewIgnoredLook = false;
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
