#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSAudioEnvironmentDirector.generated.h"

class UAudioComponent;
class USceneComponent;
class USoundBase;
class ATSTSSAtmosphereDirector;

/**
 * Optional, map-placed harbor soundscape. Assets are deliberately unset: no
 * sampled sound is shipped, referenced, or assumed rights-cleared by this actor.
 * Audio consumes weather rendering values but never controls climate, story,
 * physics, saves, or player abilities.
 */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSAudioEnvironmentDirector : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSAudioEnvironmentDirector();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio|Environment")
    void SetHarborZoneAudible(bool bAudible);

    UFUNCTION(BlueprintPure, Category="TSTSS|Audio|Environment")
    bool IsHarborZoneAudible() const { return bHarborZoneAudible; }

    /** Each field expects an approved, seamless looping SoundCue/Wave/MetaSound. */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Harbor")
    TObjectPtr<USoundBase> SurfLoop = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Harbor")
    TObjectPtr<USoundBase> GullLoop = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Harbor")
    TObjectPtr<USoundBase> MarketLoop = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Weather")
    TObjectPtr<USoundBase> WindLoop = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Weather")
    TObjectPtr<USoundBase> RainLoop = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Weather")
    TObjectPtr<USoundBase> StormBedLoop = nullptr;

    /** Disabled by default until intentionally placed/configured in a review map. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Environment")
    bool bHarborZoneAudible = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Environment",
              meta=(ClampMin="0.5", ClampMax="12.0"))
    float GainInterpSpeed = 2.5f;

private:
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<USceneComponent> AudioAnchor;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> Surf;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> Gulls;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> Market;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> Wind;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> Rain;
    UPROPERTY(VisibleAnywhere, Category="TSTSS|Audio|Components")
    TObjectPtr<UAudioComponent> StormBed;

    TWeakObjectPtr<ATSTSSAtmosphereDirector> WeatherSource;
    float SurfGain = 0.0f;
    float GullGain = 0.0f;
    float MarketGain = 0.0f;
    float WindGain = 0.0f;
    float RainGain = 0.0f;
    float StormGain = 0.0f;

    static void StartIfBound(UAudioComponent* Component, USoundBase* Asset);
    void ApplyGain(UAudioComponent* Component, float Target, float& Current,
                   float DeltaSeconds, float CategoryGain);
};
