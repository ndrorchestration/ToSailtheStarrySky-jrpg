#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSBattleSkillSystem.h"
#include "TSTSSResonatorVfxActor.generated.h"

class UInstancedStaticMeshComponent;
class UPointLightComponent;
class USceneComponent;

// Self-contained 3D review renderer. Spawning visuals does NOT execute or unlock a spell.
// The combat path must first return an accepted FTSTSSBattleSkillCue.
UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSResonatorVfxActor : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSResonatorVfxActor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    // Used only for a manually placed PIE review actor. Has no gameplay consequence.
    UPROPERTY(EditAnywhere, Category="TSTSS|Review Only")
    FName PreviewCueId = NAME_None;

    UPROPERTY(EditAnywhere, Category="TSTSS|Review Only")
    FVector PreviewTargetOffset = FVector(340.f, 0.f, 0.f);

    UPROPERTY(EditAnywhere, Category="TSTSS|Review Only")
    bool bLoopReview = true;

    static bool IsKnownCue(FName CueId);
    static bool IsAcceptedEnderCue(const FTSTSSBattleSkillCue& AcceptedCue);

    // C++ integration point; call ONLY after FTSTSSBattleSkillSystem::TryUse... succeeds.
    // Never call after a failed/DesignOnly spell. No independent authorization here.
    static ATSTSSResonatorVfxActor* SpawnFromAcceptedCue(
        UWorld* World, const FTSTSSBattleSkillCue& AcceptedCue,
        const FVector& CasterWorld, const FVector& TargetWorld);

private:
    UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> SceneRoot;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UInstancedStaticMeshComponent> RingMeshes;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UInstancedStaticMeshComponent> MoteMeshes;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UInstancedStaticMeshComponent> CoreMesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UPointLightComponent> CastLight;

    FName RunningCue = NAME_None;
    FVector TargetOffset = FVector::ZeroVector;
    FLinearColor CueTint = FLinearColor::White;
    float Age = 0.f;
    float Duration = 2.2f;
    int32 Style = 0;
    bool bPlaying = false;
    bool bReviewInstance = false;
#if WITH_EDITOR
    float ReviewCaptureElapsed = 0.f;
    bool bReviewCaptureRequested = false;
    float ReviewSequenceElapsed = 0.f;
    int32 ReviewSequenceStage = 0;
    float ReviewSweepElapsed = 0.f;
    float ReviewSweepCameraMovedAt = 0.f;
    int32 ReviewSweepIndex = 0;
    bool bReviewSweepCameraMoved = false;
    bool bReviewSweepBlockedLogged = false;
#endif

    bool StartCue(FName CueId, const FVector& RelativeTarget, bool bReview);
    void UpdateVisuals(float TimeSeconds);
};
