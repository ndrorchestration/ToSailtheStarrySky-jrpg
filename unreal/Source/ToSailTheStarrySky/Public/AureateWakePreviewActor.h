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
    virtual void OnConstruction(const FTransform& Transform) override;

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Preview")
    bool RequestForm(EAureateWakeForm RequestedForm);

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    EAureateWakeForm GetCurrentForm() const { return CurrentForm; }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    bool IsTransitioning() const { return bTransitioning; }

    /** Editor-review convenience only: finishes an already permitted ordinary-form transition. */
    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Preview")
    bool FinishOrdinaryPreviewTransitionForReview();

    /** Opt-in, noncanonical curved hull/deck and triangulated bridge frame study.
     * Disabled by default so the previously verified BasicShapes silhouette stays intact. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    bool bUseHullSilhouetteReview = false;

    /** Optional artist-created translucent material; a plain opaque sphere is never labeled glass. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    TObjectPtr<UMaterialInterface> OptionalCanopyGlassMaterial;

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Visuals")
    void RefreshHullSilhouetteReview();

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Visuals")
    int32 GetHullSilhouetteSectionCount() const { return HullSilhouetteSections.Num(); }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Visuals")
    int32 GetCanopyFramePieceCount() const { return CanopyFramePieces.Num(); }

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

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<USceneComponent> VesselRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> Hull;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> ForwardBridge;

    /** Optional noncollision review-only curved bow, midship, stern and open foredeck. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Visuals")
    TArray<TObjectPtr<UStaticMeshComponent>> HullSilhouetteSections;

    /** Hidden unless explicitly provided a canopy material and silhouette review is enabled. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Visuals")
    TObjectPtr<UStaticMeshComponent> CanopyShell;

    /** Triangulated bridge cage: intentionally stand-in geometry, not certified glazing. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Visuals")
    TArray<TObjectPtr<UStaticMeshComponent>> CanopyFramePieces;

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

    static FTransform WingPose(EAureateWakeForm Form, int32 WingIndex);
    static FTransform RootPivotedWingPose(EAureateWakeForm Form, int32 WingIndex);
    FTransform WingPoseForMesh(EAureateWakeForm Form, int32 WingIndex) const;
    static FTransform FoilPose(EAureateWakeForm Form, int32 FoilIndex);
    static FTransform Interpolate(const FTransform& Start, const FTransform& End, float Alpha);
    void SnapToForm(EAureateWakeForm Form);
    void UpdateWingRootMounts();
    void UpdateHydrofoilStruts();
    void UpdateHullSilhouetteVisibility();
};
