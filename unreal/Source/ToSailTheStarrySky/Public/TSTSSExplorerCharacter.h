#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSExplorerCharacter.generated.h"

class USkeletalMesh;
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
    UFUNCTION(BlueprintCallable, Category="TSTSS|First Wake")
    UTSTSSFirstWakeState* GetFirstWakeState() const { return FirstWakeState; }
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
    // PIE-only, explicitly assigned candidate. Blank by default; does not grant gameplay authority.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<USkeletalMesh> EnderSliceReviewBody;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<UStaticMesh> EnderSliceReviewGoggles;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    TSoftObjectPtr<UStaticMesh> EnderSliceReviewStaff;
    // Disabled until the character's head clearance and staff grip are reviewed.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    bool bShowEnderReviewGoggles = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    bool bShowEnderReviewStaff = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FName EnderReviewHeadBone = TEXT("head");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FName EnderReviewGripBone = TEXT("l_hand");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FTransform EnderReviewGogglesLocalOffset = FTransform::Identity;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Ender|SliceReview")
    FTransform EnderReviewStaffLocalOffset = FTransform::Identity;
#endif
private:
#if WITH_EDITOR
    // Changes only the spawned PIE pawn; never saves/overwrites the SkeletalMesh asset or level.
    void ApplyEnderSliceReviewAppearance();
#endif
#if WITH_EDITORONLY_DATA
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Ender|SliceReview")
    TObjectPtr<UStaticMeshComponent> EnderReviewGogglesComponent;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Ender|SliceReview")
    TObjectPtr<UStaticMeshComponent> EnderReviewStaffComponent;
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
