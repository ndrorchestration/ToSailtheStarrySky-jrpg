#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Enemies/TSTSSSliceEnemyCatalog.h"
#include "TSTSSSliceEnemyActor.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UPointLightComponent;
class UTextRenderComponent;

// Place this actor in a disposable Unreal review map. It constructs genuine 3D
// static-mesh silhouettes from engine primitives; no finalized art is claimed.
// Visuals never execute attacks, write saves, or alter quest/combat state.
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSSliceEnemyActor : public AActor
{
    GENERATED_BODY()

public:
    ATSTSSSliceEnemyActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Slice Review")
    ETSTSSSliceEnemyKind Kind = ETSTSSSliceEnemyKind::HarmonicShear;

    // Must be unique among ALL combatants in an encounter.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Slice Review")
    FName InstanceId = TEXT("SliceEnemy_01");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Slice Review")
    bool bReducedMotion = false;

    // Pure data projection. To fight, a separate, deliberate review encounter
    // must pass the resulting participant to UTSS_CombatTurnManager.
    UFUNCTION(BlueprintCallable, Category="TSTSS|Slice Review")
    bool TryBuildReviewParticipant(FTSS_CombatParticipant& Out) const;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Slice Review")
    bool TryGetReviewDescriptor(FTSTSSSliceEnemyDescriptor& Out) const;

    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<USceneComponent> Root;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<USceneComponent> VisualRoot;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> Core;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> Crown;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> LeftFin;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> RightFin;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> LowerLeft;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> LowerRight;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> EyeLeft;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UStaticMeshComponent> EyeRight;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UPointLightComponent> Glow;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Slice Review")
    TObjectPtr<UTextRenderComponent> ReviewLabel;

    UStaticMeshComponent* MakePiece(const TCHAR* Name);

    float IdleTime = 0.f;
};
