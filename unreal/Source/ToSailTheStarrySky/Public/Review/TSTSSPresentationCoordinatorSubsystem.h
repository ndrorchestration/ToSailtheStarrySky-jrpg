#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSAtmosphereDirector.h"
#include "TSTSSPresentationCoordinatorSubsystem.generated.h"

/**
 * Request names are authored SHOT INTENT, not observed events or progression
 * authority. The caller must come from an accepted action / approved scene.
 */
UENUM(BlueprintType)
enum class ETSTSSPresentationMoment : uint8
{
    None,
    DockEstablish,
    IoniaConversation,
    EngineInspection,
    EngineAwakening,
    FirstWakeLiftoff,
    EmergencySplashdown,
    ShoreExploration,
    LyraIntroduction,
    NightSkyWonder
};

/** Read-only rendering *intent*. No material, sound, actor or SaveGame side effects. */
USTRUCT(BlueprintType)
struct FTSTSSPresentationIntent
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    bool bEligible = false;

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    FName ShotId = NAME_None;

    /** Existing #796 profile name, never permission to spawn its separate lights. */
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    FName LightingLookId = NAME_None;

    /** Semantic soundscape descriptor, not a registered/audio-playable event ID. */
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    FName AudioIntentId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    ETSTSSWeather Weather = ETSTSSWeather::Clear;

    /** True only for *authored* opt-in shots with gameplay clarity restored. */
    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    bool bAllowCinematicFocus = false;

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    bool bAllowFocusRack = false;

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    bool bRequireDeepFocus = true;

    UPROPERTY(BlueprintReadOnly, Category="TSTSS|Cinematics|Review")
    FString Reason = TEXT("NOT_EVALUATED");
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
    FTSTSSReviewPresentationIntentChanged, const FTSTSSPresentationIntent&, Intent);

/**
 * Thin view-only coordinator; no Tick, camera spawn, lens/lighting writes,
 * sound playback, story transitions or particle casts.
 *
 * PIE-only. Disabled by default. Explicit review Blueprints may opt-in and
 * subscribe to OnReviewIntentChanged. Consumers remain responsible for
 * accessibility, actual authorized focus targets and ownership arbitration.
 */
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSPresentationCoordinatorSubsystem final
    : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintAssignable, Category="TSTSS|Cinematics|Review")
    FTSTSSReviewPresentationIntentChanged OnReviewIntentChanged;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Cinematics|Review")
    void SetReviewEnabled(bool bEnabled);

    UFUNCTION(BlueprintPure, Category="TSTSS|Cinematics|Review")
    bool IsReviewEnabled() const { return bReviewEnabled; }

    /**
     * Reads the caller-supplied story snapshot and existing atmosphere.
     * The story UObject itself must be sourced from the actual game state
     * by the consuming level, not constructed to manufacture permission.
     * Rejects non-PIE and unsupported map names. Failures publish a neutral
     * intent, preventing a stale cinematic view from surviving a denial.
     */
    UFUNCTION(BlueprintCallable, Category="TSTSS|Cinematics|Review")
    FTSTSSPresentationIntent TryPublishMoment(
        const UTSTSSFirstWakeState* StoryState,
        const ATSTSSAtmosphereDirector* Atmosphere,
        ETSTSSPresentationMoment Moment,
        bool bReducedMotion,
        bool bGameplayClarityOverride);

    UFUNCTION(BlueprintPure, Category="TSTSS|Cinematics|Review")
    FTSTSSPresentationIntent GetCurrentIntent() const { return CurrentIntent; }

    UFUNCTION(BlueprintCallable, Category="TSTSS|Cinematics|Review")
    void ResetReviewIntent();

    /** Stateless policy; accessible to existing native tests without PIE. */
    static FTSTSSPresentationIntent ResolveForReview(
        const UTSTSSFirstWakeState* StoryState,
        ETSTSSPresentationMoment Moment,
        const FString& MapName,
        ETSTSSWeather WorldWeather,
        bool bReducedMotion,
        bool bGameplayClarityOverride);

    virtual void Deinitialize() override;

protected:
    virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

private:
    /** All effects are opt-in. No map automatically enables this subsystem. */
    bool bReviewEnabled = false;

    UPROPERTY(Transient)
    FTSTSSPresentationIntent CurrentIntent;
};
