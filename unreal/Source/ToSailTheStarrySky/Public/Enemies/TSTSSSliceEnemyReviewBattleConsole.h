#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Enemies/TSTSSSliceEnemyReviewSession.h"
#include "TSTSSSliceEnemyReviewBattleConsole.generated.h"

class USceneComponent;
class UCameraComponent;
class UTextRenderComponent;

// Only for a neutral sandbox .umap. No First Wake or shipping placement.
// In PIE: F7 Ender, F8 with recruited Ionia, F9 post-splashdown Lyra;
// J/K attack enemy 1/2. No input or auto-spawn outside deliberate review.
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSSliceEnemyReviewBattleConsole : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSSliceEnemyReviewBattleConsole();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Enemy Review")
    FName ReviewWavePreset = TEXT("Review_HarborBanditPatrol");

    UFUNCTION(BlueprintCallable, Category="TSTSS|Enemy Review")
    bool TryStartPreview(ETSTSSSliceReviewPartyStage Stage);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Enemy Review")
    bool TryStrikePreview(int32 EnemySlot);

    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Enemy Review")
    TObjectPtr<USceneComponent> ReviewRoot;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Enemy Review")
    TObjectPtr<UCameraComponent> PreviewCamera;

    UPROPERTY(VisibleAnywhere, Category="TSTSS|Enemy Review")
    TObjectPtr<UTextRenderComponent> ReviewSign;

    UPROPERTY(Transient)
    TObjectPtr<UTSTSSSliceEnemyReviewSession> Session;

    void StartEnderOnly();
    void StartIoniaRecruited();
    void StartAfterSplashdown();
    void StrikeFirst();
    void StrikeSecond();
    void RefreshStatus();
    float StatusAge = 0.f;
};
