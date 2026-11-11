#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSHarborAudioZone.generated.h"

class UBoxComponent;
class ATSTSSAudioEnvironmentDirector;
class UPrimitiveComponent;

/** Optional map-placed sound-only trigger for the *local player*. No quest/physics mutation. */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSHarborAudioZone : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSHarborAudioZone();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="TSTSS|Audio|Zone")
    TObjectPtr<ATSTSSAudioEnvironmentDirector> HarborAudio;

private:
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Zone")
    TObjectPtr<UBoxComponent> Trigger;

    UFUNCTION()
    void OnPlayerEnter(UPrimitiveComponent* OverlapComponent, AActor* OtherActor,
                       UPrimitiveComponent* OtherComponent, int32 BodyIndex,
                       bool bFromSweep, const FHitResult& Sweep);

    UFUNCTION()
    void OnPlayerLeave(UPrimitiveComponent* OverlapComponent, AActor* OtherActor,
                       UPrimitiveComponent* OtherComponent, int32 BodyIndex);
};
