#include "Review/TSTSSPresentationCoordinatorSubsystem.h"

#include "Engine/World.h"
#include "TSTSSExplorerCharacter.h"
#include "Kismet/GameplayStatics.h"

/**
 * This implementation is deliberately only a decision-and-notification path.
 * It MUST NOT apply post-process, start sound, spawn an actor, modify climate,
 * advance a milestone, inspect water physics, or change SaveGame content.
 */
namespace
{
struct FAuthoredMoment
{
    const TCHAR* SourceMap;
    const TCHAR* Shot;
    const TCHAR* Look;
    const TCHAR* SoundIntent;
    bool bEligibleForOpticalFocus;
    bool bEligibleForFocusRack;
    bool bRequiresDeepFocus;
};

FAuthoredMoment DescribeMoment(ETSTSSPresentationMoment Moment)
{
    switch (Moment)
    {
    case ETSTSSPresentationMoment::DockEstablish:
        return {TEXT("VS01_DenithHarbor"), TEXT("FW01_Dock_Establish"),
                TEXT("harbor_dusk"), TEXT("harbor_rope_wind_waves"),
                false, false, true};
    case ETSTSSPresentationMoment::IoniaConversation:
        return {TEXT("VS01_DenithHarbor"), TEXT("FW02_Ionia_Conversation"),
                TEXT("harbor_dusk"), TEXT("intimate_dialogue_harbor_lanterns"),
                true, true, false};
    case ETSTSSPresentationMoment::EngineInspection:
        return {TEXT("VS02_AureateInteriors"), TEXT("FW03_Engine_Inspection"),
                TEXT("engineering"), TEXT("mechanical_hum_gauge_resonance"),
                true, true, false};
    case ETSTSSPresentationMoment::EngineAwakening:
        return {TEXT("VS02_AureateInteriors"), TEXT("FW04_Engine_Awakening"),
                TEXT("engineering"), TEXT("subtle_harmonic_response"),
                true, true, false};
    case ETSTSSPresentationMoment::FirstWakeLiftoff:
        return {TEXT("VS03_FirstWakeSky"), TEXT("FW05_FirstWake_Liftoff"),
                TEXT("ascent"), TEXT("hull_wind_rigging_engine_ascent"),
                false, false, true};
    case ETSTSSPresentationMoment::EmergencySplashdown:
        return {TEXT("VS04_SplashdownSea"), TEXT("FW06_Emergency_Splashdown"),
                TEXT("sea_contact"), TEXT("storm_spray_hull_water_impact"),
                false, false, true};
    case ETSTSSPresentationMoment::ShoreExploration:
        return {TEXT("VS06_SplashdownShore"), TEXT("FW07_Shore_Exploration"),
                TEXT("shore_aftermath"), TEXT("shore_surf_wind_distant_settlement"),
                false, false, true};
    case ETSTSSPresentationMoment::LyraIntroduction:
        return {TEXT("VS06_SplashdownShore"), TEXT("FW08_Lyra_Introduction"),
                TEXT("shore_aftermath"), TEXT("human_conversation_and_soft_surf"),
                true, true, false};
    case ETSTSSPresentationMoment::NightSkyWonder:
        // This look MUST remain unset until a native shore-night look exists.
        return {TEXT("VS06_SplashdownShore"), TEXT("FW09_NightSky_Wonder"),
                nullptr, TEXT("quiet_night_wind_distant_sea"),
                false, false, true};
    default:
        return {nullptr, nullptr, nullptr, nullptr, false, false, true};
    }
}

bool WeatherCompatible(ETSTSSPresentationMoment Moment, ETSTSSWeather Weather)
{
    if (Moment == ETSTSSPresentationMoment::NightSkyWonder)
    {
        return Weather == ETSTSSWeather::Clear
            || Weather == ETSTSSWeather::CoastalMist
            || Weather == ETSTSSWeather::AuroralVeil;
    }

    if (Moment == ETSTSSPresentationMoment::EngineInspection
        || Moment == ETSTSSPresentationMoment::EngineAwakening
        || Moment == ETSTSSPresentationMoment::FirstWakeLiftoff
        || Moment == ETSTSSPresentationMoment::EmergencySplashdown
        || Moment == ETSTSSPresentationMoment::ShoreExploration
        || Moment == ETSTSSPresentationMoment::LyraIntroduction)
    {
        return Weather == ETSTSSWeather::Clear
            || Weather == ETSTSSWeather::CoastalMist
            || Weather == ETSTSSWeather::Rain
            || Weather == ETSTSSWeather::Storm;
    }

    // The harbor establish / hiring study allows clear, mist, or rain only.
    return Weather == ETSTSSWeather::Clear
        || Weather == ETSTSSWeather::CoastalMist
        || Weather == ETSTSSWeather::Rain;
}

bool HasStoryPrerequisite(const UTSTSSFirstWakeState* State,
                          ETSTSSPresentationMoment Moment)
{
    if (!IsValid(State)) return false;

    const bool bStarted = State->HasStarted();
    const ETSTSSFirstWakeBeat Beat = State->GetCurrentBeat();
    const uint8 Ordinal = static_cast<uint8>(Beat);
    const auto AtLeast = [Ordinal, bStarted](ETSTSSFirstWakeBeat Required) {
        return bStarted && Ordinal >= static_cast<uint8>(Required);
    };

    switch (Moment)
    {
    case ETSTSSPresentationMoment::DockEstablish:
        // Exploration may begin before the flyer interaction is accepted.
        return !bStarted || Beat == ETSTSSFirstWakeBeat::FlyerDiscovered
            || Beat == ETSTSSFirstWakeBeat::IoniaHired;
    case ETSTSSPresentationMoment::IoniaConversation:
        return bStarted && (Beat == ETSTSSFirstWakeBeat::FlyerDiscovered
            || Beat == ETSTSSFirstWakeBeat::IoniaHired);
    case ETSTSSPresentationMoment::EngineInspection:
        return bStarted && (Beat == ETSTSSFirstWakeBeat::BoardedAureateWake
            || Beat == ETSTSSFirstWakeBeat::EngineeringChecked);
    case ETSTSSPresentationMoment::EngineAwakening:
        return State->AreInspectionsComplete()
            && (Beat == ETSTSSFirstWakeBeat::BoardedAureateWake
                || Beat == ETSTSSFirstWakeBeat::EngineeringChecked);
    case ETSTSSPresentationMoment::FirstWakeLiftoff:
        return Beat == ETSTSSFirstWakeBeat::Launched && bStarted;
    case ETSTSSPresentationMoment::EmergencySplashdown:
        // A camera MUST NOT promote Launched into SeaContact/FlotationConfirmed.
        return bStarted && (Beat == ETSTSSFirstWakeBeat::SeaContact
            || Beat == ETSTSSFirstWakeBeat::FlotationConfirmed);
    case ETSTSSPresentationMoment::ShoreExploration:
    case ETSTSSPresentationMoment::LyraIntroduction:
    case ETSTSSPresentationMoment::NightSkyWonder:
        return AtLeast(ETSTSSFirstWakeBeat::FlotationConfirmed);
    default:
        return false;
    }
}
} // namespace

bool UTSTSSPresentationCoordinatorSubsystem::DoesSupportWorldType(
    const EWorldType::Type WorldType) const
{
#if WITH_EDITOR
    return WorldType == EWorldType::PIE;
#else
    return false;
#endif
}

FTSTSSPresentationIntent UTSTSSPresentationCoordinatorSubsystem::ResolveForReview(
    const UTSTSSFirstWakeState* StoryState,
    ETSTSSPresentationMoment Moment,
    const FString& MapName,
    ETSTSSWeather WorldWeather,
    bool bReducedMotion,
    bool bGameplayClarityOverride)
{
    FTSTSSPresentationIntent Intent;
    Intent.Weather = WorldWeather;
    Intent.Reason = TEXT("DENIED_UNKNOWN_MOMENT");

    const FAuthoredMoment Authored = DescribeMoment(Moment);
    if (!Authored.SourceMap || !Authored.Shot)
    {
        return Intent;
    }
    // Accept ONLY the exact supported native map name. PIE adds the
    // "UEDPIE_<index>_" prefix. EndsWith alone would admit a spoofed map
    // such as FakeVS02_AureateInteriors, so strip that precise prefix first.
    FString NativeMapName = MapName;
    if (NativeMapName.StartsWith(TEXT("UEDPIE_"), ESearchCase::CaseSensitive))
    {
        FString PIEIndex;
        FString Unprefixed;
        const FString Remainder = NativeMapName.RightChop(7);
        if (!Remainder.Split(TEXT("_"), &PIEIndex, &Unprefixed)
            || PIEIndex.IsEmpty() || !PIEIndex.IsNumeric())
        {
            Intent.Reason = TEXT("DENIED_INVALID_PIE_MAP_PREFIX");
            return Intent;
        }
        NativeMapName = Unprefixed;
    }
    const bool bMapMatches = NativeMapName.Equals(Authored.SourceMap,
        ESearchCase::CaseSensitive);
    const bool bHarborReviewCopy =
        (Moment == ETSTSSPresentationMoment::DockEstablish
            || Moment == ETSTSSPresentationMoment::IoniaConversation)
        && NativeMapName.Equals(TEXT("M_DenithHarborBokehStudy"),
                                ESearchCase::CaseSensitive);
    const bool bEngineReviewCopy =
        (Moment == ETSTSSPresentationMoment::EngineInspection
            || Moment == ETSTSSPresentationMoment::EngineAwakening)
        && NativeMapName.Equals(TEXT("M_EnginePresentationReview"),
                                ESearchCase::CaseSensitive);
    if (!bMapMatches && !bHarborReviewCopy && !bEngineReviewCopy)
    {
        Intent.Reason = TEXT("DENIED_WRONG_NATIVE_MAP");
        return Intent;
    }
    if (!HasStoryPrerequisite(StoryState, Moment))
    {
        Intent.Reason = TEXT("DENIED_AUTHORITATIVE_STORY_PREREQUISITE");
        return Intent;
    }
    if (!WeatherCompatible(Moment, WorldWeather))
    {
        Intent.Reason = TEXT("DENIED_WEATHER_NOT_IN_REVIEW_LOOK");
        return Intent;
    }
    if (!Authored.Look)
    {
        Intent.Reason = TEXT("HOLD_UNRESOLVED_SHORE_NIGHT_LIGHTING");
        return Intent;
    }

    Intent.bEligible = true;
    Intent.ShotId = FName(Authored.Shot);
    Intent.LightingLookId = FName(Authored.Look);
    Intent.AudioIntentId = FName(Authored.SoundIntent);
    const bool bCameraSafe = !bReducedMotion && !bGameplayClarityOverride;
    Intent.bAllowCinematicFocus = Authored.bEligibleForOpticalFocus && bCameraSafe;
    Intent.bAllowFocusRack = Authored.bEligibleForFocusRack && bCameraSafe;
    Intent.bRequireDeepFocus = Authored.bRequiresDeepFocus || !bCameraSafe;
    Intent.Reason = bCameraSafe
        ? TEXT("REVIEW_INTENT_READ_ONLY_NOT_RENDERED")
        : TEXT("REVIEW_INTENT_CLARITY_OVERRIDE_NO_FOCUS_RACK");
    return Intent;
}

bool UTSTSSPresentationCoordinatorSubsystem::MatchesStorySnapshot(
    const UTSTSSFirstWakeState* State,
    uint64 ObservedGeneration,
    bool bObservedStarted,
    ETSTSSFirstWakeBeat ObservedBeat,
    uint8 ObservedInspectionMask)
{
    return IsValid(State)
        && State->GetRestoreGeneration() == ObservedGeneration
        && State->HasStarted() == bObservedStarted
        && State->GetCurrentBeat() == ObservedBeat
        && State->GetInspectionMask() == ObservedInspectionMask;
}

void UTSTSSPresentationCoordinatorSubsystem::HandleAcceptedStoryChange()
{
    // Invoked ONLY after a valid story transition, inspection, physics gate
    // or restore/reset. Invalidate the old camera/look cue immediately.
    PublishNeutral(TEXT("CLEARED_AFTER_ACCEPTED_FIRST_WAKE_CHANGE"));
}

void UTSTSSPresentationCoordinatorSubsystem::ClearObservedSource()
{
    if (StoryChangedHandle.IsValid())
    {
        if (UTSTSSFirstWakeState* Bound = ObservedStory.Get())
        {
            Bound->OnAcceptedChange().Remove(StoryChangedHandle);
        }
        StoryChangedHandle.Reset();
    }
    ObservedStory.Reset();
    ObservedAtmosphere.Reset();
    ObservedRestoreGeneration = 0;
    ObservedBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    ObservedInspectionMask = 0;
    bObservedStarted = false;
    ObservedWeather = ETSTSSWeather::Clear;
    ObservedClockHours = 0.0f;
}

void UTSTSSPresentationCoordinatorSubsystem::PublishNeutral(const FString& Reason)
{
    ClearObservedSource();
    CurrentIntent = FTSTSSPresentationIntent();
    CurrentIntent.Reason = Reason;
    OnReviewIntentChanged.Broadcast(CurrentIntent);
}

FTSTSSPresentationIntent UTSTSSPresentationCoordinatorSubsystem::GetCurrentIntent() const
{
    if (!CurrentIntent.bEligible)
    {
        return CurrentIntent;
    }

    const UWorld* World = GetWorld();
    const ATSTSSExplorerCharacter* Player = World
        ? Cast<ATSTSSExplorerCharacter>(UGameplayStatics::GetPlayerPawn(World, 0))
        : nullptr;
    const UTSTSSFirstWakeState* State = IsValid(Player)
        ? Player->GetFirstWakeState() : nullptr;
    const ATSTSSAtmosphereDirector* Atmosphere = ObservedAtmosphere.Get();
    if (!bReviewEnabled || !World || World->WorldType != EWorldType::PIE
        || !IsValid(Player)
        || !IsValid(State)
        || State != ObservedStory.Get()
        || !MatchesStorySnapshot(State, ObservedRestoreGeneration,
                                  bObservedStarted, ObservedBeat,
                                  ObservedInspectionMask)
        || !IsValid(Atmosphere)
        || Atmosphere->GetWorld() != World
        || Atmosphere->GetTargetWeather() != ObservedWeather
        || !FMath::IsNearlyEqual(
            Atmosphere->GetAtmosphereProfile().ClockHours,
            ObservedClockHours, 0.1f))
    {
        // Const getter intentionally does not broadcast: callers must treat
        // stale or missing source snapshots as neutral until republished.
        FTSTSSPresentationIntent Expired;
        Expired.Reason = TEXT("EXPIRED_STORY_OR_WORLD_SNAPSHOT");
        return Expired;
    }
    return CurrentIntent;
}

void UTSTSSPresentationCoordinatorSubsystem::SetReviewEnabled(bool bEnabled)
{
#if WITH_EDITOR
    const UWorld* World = GetWorld();
    if (!World || World->WorldType != EWorldType::PIE) return;
    bReviewEnabled = bEnabled;
    if (!bReviewEnabled)
    {
        ResetReviewIntent();
    }
#else
    (void)bEnabled;
#endif
}

FTSTSSPresentationIntent UTSTSSPresentationCoordinatorSubsystem::TryPublishMoment(
    const UTSTSSFirstWakeState* StoryState,
    const ATSTSSAtmosphereDirector* Atmosphere,
    ETSTSSPresentationMoment Moment,
    bool bReducedMotion,
    bool bGameplayClarityOverride)
{
    FTSTSSPresentationIntent Denied;
    Denied.Reason = TEXT("DISABLED_OR_NOT_PIE");
    const UWorld* World = GetWorld();
    if (!bReviewEnabled || !World || World->WorldType != EWorldType::PIE)
    {
        return Denied;
    }

    // The caller does not define truth. Bind to the ACTUAL player-owned state
    // to prevent a transient or caller-created UObject from manufacturing an
    // apparently valid milestone. This is presentation gating, not security.
    const ATSTSSExplorerCharacter* Player =
        Cast<ATSTSSExplorerCharacter>(UGameplayStatics::GetPlayerPawn(World, 0));
    UTSTSSFirstWakeState* ActualStory = IsValid(Player)
        ? Player->GetFirstWakeState() : nullptr;
    if (!IsValid(ActualStory) || ActualStory != StoryState)
    {
        PublishNeutral(TEXT("DENIED_UNBOUND_PLAYER_STORY_STATE"));
        return CurrentIntent;
    }
    // No inferred "clear weather" when the world owner is absent or from
    // another level. An unmerged atmosphere draft is an explicit blocker.
    if (!IsValid(Atmosphere) || Atmosphere->GetWorld() != World)
    {
        PublishNeutral(TEXT("DENIED_MISSING_WORLD_ATMOSPHERE"));
        return CurrentIntent;
    }

    const ETSTSSWeather Weather = Atmosphere->GetTargetWeather();
    const FTSTSSPresentationIntent Result = ResolveForReview(
        ActualStory, Moment, World->GetMapName(), Weather,
        bReducedMotion, bGameplayClarityOverride);
    if (!Result.bEligible)
    {
        PublishNeutral(Result.Reason);
        return CurrentIntent;
    }

    ClearObservedSource();
    CurrentIntent = Result; // Read-only; no renderer, weather, or audio writes.
    ObservedStory = ActualStory;
    StoryChangedHandle = ActualStory->OnAcceptedChange().AddUObject(
        this, &UTSTSSPresentationCoordinatorSubsystem::HandleAcceptedStoryChange);
    ObservedAtmosphere = Atmosphere;
    ObservedRestoreGeneration = ActualStory->GetRestoreGeneration();
    bObservedStarted = ActualStory->HasStarted();
    ObservedBeat = ActualStory->GetCurrentBeat();
    ObservedInspectionMask = ActualStory->GetInspectionMask();
    ObservedWeather = Weather;
    ObservedClockHours = Atmosphere->GetAtmosphereProfile().ClockHours;
    OnReviewIntentChanged.Broadcast(CurrentIntent);
    return CurrentIntent;
}

void UTSTSSPresentationCoordinatorSubsystem::ResetReviewIntent()
{
    PublishNeutral(TEXT("CLEARED_ON_STORY_RESET_OR_SCENE_EXIT"));
}

void UTSTSSPresentationCoordinatorSubsystem::Deinitialize()
{
    bReviewEnabled = false;
    ClearObservedSource();
    CurrentIntent = FTSTSSPresentationIntent();
    Super::Deinitialize();
}
