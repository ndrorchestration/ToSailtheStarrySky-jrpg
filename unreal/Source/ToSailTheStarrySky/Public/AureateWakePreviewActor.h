#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AureateWakePreviewActor.generated.h"

class UStaticMeshComponent;
class USceneComponent;
class UMaterialInterface;
class UStaticMesh;
class UMaterialInstanceDynamic;

UENUM(BlueprintType)
enum class EAureateWakeForm : uint8
{
    Skyborne,
    Seaborne,
    Submersible,
    Orbiter
};

/** Noncanonical geometric preview. Does NOT simulate buoyancy, pressure, sail thrust, or navigation. */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API AAureateWakePreviewActor : public AActor
{
    GENERATED_BODY()

public:
    AAureateWakePreviewActor();
    virtual void Tick(float DeltaSeconds) override;
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Preview")
    bool RequestForm(EAureateWakeForm RequestedForm);

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    EAureateWakeForm GetCurrentForm() const { return CurrentForm; }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    bool IsTransitioning() const { return bTransitioning; }

    /** Editor-review convenience only: finishes an already permitted ordinary-form transition. */
    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Preview")
    bool FinishOrdinaryPreviewTransitionForReview();

    /** Deliberately false by default. Orbiter is a story-gated mode, not unlocked by UI. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Preview")
    bool bAllowOrbiterPreview = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Preview", meta=(ClampMin="0.1"))
    float TransitionSeconds = 2.5f;

    /** Optional creator-authored translucent/iridescent wing material; no material asset is included yet. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    TObjectPtr<UMaterialInterface> WingMaterial;

    /** Lerp scalar used by optional shader: 0 atmospheric membrane, 1 Orbiter photovoltaic/light-sail display. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Visuals")
    float OrbiterSailBlend = 0.f;

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Preview")
    void RefreshWingMaterials();

    /** Artist-supplied reusable wing mesh. Never changes wing identity or quantity. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    TObjectPtr<UStaticMesh> AuthoredWingMesh;

    /** Opt-in review pose for root-pivoted +X 280cm wing art. Default cube posing is unchanged. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    bool bUseRootPivotedWingPose = false;

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Visuals")
    void RefreshWingMeshes();

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetWingCount() const { return Wings.Num(); }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetHydrofoilCount() const { return Hydrofoils.Num(); }

    /** Temporary visual-only root brackets, four for four wings; not structural proof. */
    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetWingRootMountCount() const { return WingRootMounts.Num(); }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetHydrofoilStrutCount() const { return HydrofoilStruts.Num(); }

    /** REVIEW ONLY: a coupled bridge + living-quarters pivot. Default false preserves legacy art. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Bridge Review")
    bool bPreviewCentralBridgeHabitation = false;

    /** Editable *review* poses, NOT creator-approved form angles or gameplay constraints. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Bridge Review")
    FRotator SkyborneHabitationReviewRotation = FRotator::ZeroRotator;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Bridge Review")
    FRotator SeaborneHabitationReviewRotation = FRotator::ZeroRotator;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Bridge Review")
    FRotator SubmersibleHabitationReviewRotation = FRotator::ZeroRotator;

    /** Toggle only while idle. Never authorizes Orbiter or a physical attachment. */
    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Bridge Review")
    bool RefreshCentralBridgeHabitationReview();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<USceneComponent> VesselRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> Hull;

    /** Independent rotating review frame; coupled dome/quarters both attach here. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Bridge Review")
    TObjectPtr<USceneComponent> BridgeHabitationPivot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> ForwardBridge;

    /** Hidden, collision-free cuboid stand-in for living quarters (NOT designed interior). */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Bridge Review")
    TObjectPtr<UStaticMeshComponent> LivingQuartersEnvelope;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> Wings;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> Hydrofoils;

    /** Noncanonical proxy links from the provisional hull side to the wing pivots. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> WingRootMounts;

    /** Review-only hydrofoil support struts; no buoyancy/load engineering claim. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> HydrofoilStruts;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    EAureateWakeForm CurrentForm = EAureateWakeForm::Skyborne;

private:
    /** Keep legacy cube mesh until an authored wing and explicit review pose are both selected. */
    UPROPERTY(Transient)
    TObjectPtr<UStaticMesh> OriginalCubeWingMesh;

    bool bTransitioning = false;
    float TransitionElapsed = 0.f;
    EAureateWakeForm TargetForm = EAureateWakeForm::Skyborne;
    UPROPERTY(Transient)
    TArray<TObjectPtr<UMaterialInstanceDynamic>> DynamicWingMaterials;
    float StartSailBlend = 0.f;
    float TargetSailBlend = 0.f;
    TArray<FTransform> StartWingTransforms;
    TArray<FTransform> TargetWingTransforms;
    TArray<FTransform> StartFoilTransforms;
    TArray<FTransform> TargetFoilTransforms;
    FQuat StartHabitationReviewRotation = FQuat::Identity;
    FQuat TargetHabitationReviewRotation = FQuat::Identity;
    /** Latch review participation at request time; mid-flight editor toggles are deferred. */
    bool bHabitationReviewLatchedForTransition = false;

    static FTransform WingPose(EAureateWakeForm Form, int32 WingIndex);
    static FTransform RootPivotedWingPose(EAureateWakeForm Form, int32 WingIndex);
    FTransform WingPoseForMesh(EAureateWakeForm Form, int32 WingIndex) const;
    static FTransform FoilPose(EAureateWakeForm Form, int32 FoilIndex);
    /** Reject non-finite editor rotations before any bridge pose or transition mutates. */
    bool HasFiniteHabitationReviewRotation(EAureateWakeForm Form) const;
    FQuat HabitationReviewRotationForForm(EAureateWakeForm Form) const;
    static FTransform Interpolate(const FTransform& Start, const FTransform& End, float Alpha);
    void SnapToForm(EAureateWakeForm Form);
    void UpdateWingRootMounts();
    void UpdateHydrofoilStruts();
};
