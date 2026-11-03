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

    /** Optional 100-cm +X authored strut. One rigid visual link per wing, review only. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Visuals")
    TObjectPtr<UStaticMesh> AuthoredRootSupportMesh;

    /** Reconcile strut geometry without changing ship state, buoyancy or wing count. */
    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Visuals")
    void RefreshRootSupports();

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetRootSupportCount() const { return WingRootSupports.Num(); }

    UFUNCTION(BlueprintCallable, Category="Aureate Wake|Visuals")
    void RefreshWingMeshes();

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetWingCount() const { return Wings.Num(); }

    UFUNCTION(BlueprintPure, Category="Aureate Wake|Preview")
    int32 GetHydrofoilCount() const { return Hydrofoils.Num(); }

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<USceneComponent> VesselRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> Hull;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TObjectPtr<UStaticMeshComponent> ForwardBridge;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> Wings;

    /** Four independent hull-to-root telescope visuals; never counted as wings. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> WingRootSupports;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Aureate Wake|Preview")
    TArray<TObjectPtr<UStaticMeshComponent>> Hydrofoils;

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
    void UpdateRootSupportTransforms();
};
