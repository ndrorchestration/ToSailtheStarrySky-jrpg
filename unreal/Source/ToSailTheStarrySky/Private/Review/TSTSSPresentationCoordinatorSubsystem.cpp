#include "Review/TSTSSPresentationCoordinatorSubsystem.h"

#include "Engine/World.h"

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
    // World.GetMapName in PIE is prefixed UEDPIE_<index>_; use exact
    // documented map suffix, not caller-supplied creative label.
    const bool bMapMatches = MapName.EndsWith(Authored.SourceMap,
        ESearchCase::CaseSensitive);
    const bool bHarborReviewCopy =
        (Moment == ETSTSSPresentationMoment::DockEstablish
            || Moment == ETSTSSPresentationMoment::IoniaConversation)
        && MapName.EndsWith(TEXT("M_DenithHarborBokehStudy"),
                            ESearchCase::CaseSensitive);
    if (!bMapMatches && !bHarborReviewCopy)
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

void UTSTSSPresentationCoordinatorSubsystem::SetReviewEnabled(bool bEnabled)
{
#if WITH_EDITOR
    const UWorld* World = GetWorld();
    if (!World || World->WorldType != EWorldType::PIE) return;
    bReviewEnabled = bEnabled;
    if (!bReviewEnabled) ResetReviewIntent();
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

    const ETSTSSWeather Weather = IsValid(Atmosphere)
        ? Atmosphere->GetTargetWeather() : ETSTSSWeather::Clear;
    const FTSTSSPresentationIntent Result = ResolveForReview(
        StoryState, Moment, World->GetMapName(), Weather,
        bReducedMotion, bGameplayClarityOverride);
    CurrentIntent = Result; // Non-authoritative, transient presentation receipt.
    OnReviewIntentChanged.Broadcast(CurrentIntent);
    return Result;
}

void UTSTSSPresentationCoordinatorSubsystem::ResetReviewIntent()
{
    CurrentIntent = FTSTSSPresentationIntent();
    CurrentIntent.Reason = TEXT("CLEARED_ON_STORY_RESET_OR_SCENE_EXIT");
    OnReviewIntentChanged.Broadcast(CurrentIntent);
}

void UTSTSSPresentationCoordinatorSubsystem::Deinitialize()
{
    bReviewEnabled = false;
    CurrentIntent = FTSTSSPresentationIntent();
    Super::Deinitialize();
}
