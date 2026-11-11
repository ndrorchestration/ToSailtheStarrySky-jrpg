#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "TSTSSAudioSubsystem.generated.h"

class USoundBase;
class UAudioComponent;

/** Audio mix categories: strictly cosmetic; never confer gameplay authority. */
UENUM(BlueprintType)
enum class ETSTSSAudioCategory : uint8
{
    Master, Music, Voice, Ambience, SFX, UI
};

/** Register actual SoundBase assets at runtime through a level review-bank actor. */
USTRUCT(BlueprintType)
struct FTSTSSAudioCue
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio")
    FName EventId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio")
    TObjectPtr<USoundBase> Sound = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio")
    ETSTSSAudioCategory Category = ETSTSSAudioCategory::SFX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio")
    bool bSpatial = true;

    /** True means hold and stop the AudioComponent; the SoundBase itself must loop. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio")
    bool bLooping = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio", meta=(ClampMin="0.0", ClampMax="1.0"))
    float Gain = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio", meta=(ClampMin="0.0"))
    float CooldownSeconds = 0.08f;
};

UCLASS()
class TOSAILTHESTARRYSKY_API UTSTSSAudioSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Deinitialize() override;

    /** Rejects missing/unusable sound objects. Does not load external files. */
    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio")
    bool RegisterCue(const FTSTSSAudioCue& Cue);

    /** True means a configured sound was emitted; audio NEVER advances any gameplay state. */
    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio")
    bool EmitCue(FName EventId, FVector Location);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio")
    bool StopCue(FName EventId, float FadeOutSeconds = 0.15f);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio")
    void SetCategoryVolume(ETSTSSAudioCategory Category, float Volume);

    UFUNCTION(BlueprintPure, Category="TSTSS|Audio")
    float GetCategoryVolume(ETSTSSAudioCategory Category) const;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio")
    void SetMuted(bool bInMuted);

    UFUNCTION(BlueprintPure, Category="TSTSS|Audio")
    bool IsMuted() const { return bMuted; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Audio")
    bool HasCue(FName EventId) const;

    /** Local review receipt only; not a proof of audible hardware output. */
    UFUNCTION(BlueprintPure, Category="TSTSS|Audio")
    FString GetLastAudioReceipt() const { return LastReceipt; }

private:
    UPROPERTY(Transient)
    TMap<FName, FTSTSSAudioCue> Registered;

    UPROPERTY(Transient)
    TMap<FName, TObjectPtr<UAudioComponent>> ActiveLoops;

    TMap<FName, double> LastPlayedSeconds;
    TMap<ETSTSSAudioCategory, float> CategoryVolumes;
    bool bMuted = false;
    FString LastReceipt;

    float EffectiveVolume(const FTSTSSAudioCue& Cue) const;
    void RefreshLoopVolumes();
};
