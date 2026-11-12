#include "TSTSSAudioEnvironmentDirector.h"

#include "TSTSSAtmosphereDirector.h"
#include "TSTSSAudioSubsystem.h"

#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

ATSTSSAudioEnvironmentDirector::ATSTSSAudioEnvironmentDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    AudioAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("AudioAnchor"));
    RootComponent = AudioAnchor;

    Surf = CreateDefaultSubobject<UAudioComponent>(TEXT("HarborSurf"));
    Gulls = CreateDefaultSubobject<UAudioComponent>(TEXT("HarborGulls"));
    Market = CreateDefaultSubobject<UAudioComponent>(TEXT("HarborMarket"));
    Wind = CreateDefaultSubobject<UAudioComponent>(TEXT("OutdoorWind"));
    Rain = CreateDefaultSubobject<UAudioComponent>(TEXT("RainBed"));
    StormBed = CreateDefaultSubobject<UAudioComponent>(TEXT("StormBed"));

    for (UAudioComponent* Component : {Surf.Get(), Gulls.Get(), Market.Get(),
                                      Wind.Get(), Rain.Get(), StormBed.Get()})
    {
        Component->SetupAttachment(AudioAnchor);
        Component->bAutoActivate = false;
        Component->SetVolumeMultiplier(0.0f);
        Component->bAllowSpatialization = false; // Non-positional ambience beds.
    }
}

void ATSTSSAudioEnvironmentDirector::StartIfBound(UAudioComponent* Component, USoundBase* Asset)
{
    if (IsValid(Component) && IsValid(Asset))
    {
        Component->SetSound(Asset);
        Component->SetVolumeMultiplier(0.0f);
        Component->Play();
    }
}

void ATSTSSAudioEnvironmentDirector::BeginPlay()
{
    Super::BeginPlay();
    if (UWorld* World = GetWorld())
    {
        WeatherSource = Cast<ATSTSSAtmosphereDirector>(
            UGameplayStatics::GetActorOfClass(World, ATSTSSAtmosphereDirector::StaticClass()));
    }
    StartIfBound(Surf, SurfLoop);
    StartIfBound(Gulls, GullLoop);
    StartIfBound(Market, MarketLoop);
    StartIfBound(Wind, WindLoop);
    StartIfBound(Rain, RainLoop);
    StartIfBound(StormBed, StormBedLoop);
}

void ATSTSSAudioEnvironmentDirector::SetHarborZoneAudible(bool bAudible)
{
    bHarborZoneAudible = bAudible;
}

void ATSTSSAudioEnvironmentDirector::ApplyGain(
    UAudioComponent* Component, float Target, float& Current,
    float DeltaSeconds, float CategoryGain)
{
    if (!IsValid(Component)) return;
    const float Effective = FMath::Clamp(Target * CategoryGain, 0.0f, 1.0f);
    Current = FMath::FInterpTo(Current, Effective, DeltaSeconds, GainInterpSpeed);
    Component->SetVolumeMultiplier(Current);
}

void ATSTSSAudioEnvironmentDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.0f) return;
    UWorld* World = GetWorld();
    if (!World) return;

    UTSTSSAudioSubsystem* Audio = World->GetSubsystem<UTSTSSAudioSubsystem>();
    const bool bSilent = Audio && Audio->IsMuted();
    const float GlobalGain = Audio && !bSilent
        ? Audio->GetCategoryVolume(ETSTSSAudioCategory::Master) *
          Audio->GetCategoryVolume(ETSTSSAudioCategory::Ambience)
        : (!Audio ? 1.0f : 0.0f);

    // Missing atmospheric actor is safe and quiet. It never implies a storm.
    FTSTSSAtmosphereProfile Profile;
    if (WeatherSource.IsValid())
    {
        Profile = WeatherSource->GetAtmosphereProfile();
    }
    else
    {
        Profile = ATSTSSAtmosphereDirector::ProfileFor(ETSTSSWeather::Clear, 12.0f);
    }

    const float Daylight = FMath::Clamp((Profile.ClockHours - 5.0f) / 2.0f, 0.0f, 1.0f) *
                           FMath::Clamp((21.0f - Profile.ClockHours) / 2.0f, 0.0f, 1.0f);
    const float HarborGain = bHarborZoneAudible ? 1.0f : 0.0f;
    const float RainIntensity = FMath::Clamp(Profile.RainIntensity, 0.0f, 1.0f);
    const float WindStrength = FMath::Clamp(Profile.WindSpeed / 25.0f, 0.0f, 1.0f);

    ApplyGain(Surf, 0.45f * HarborGain * (0.85f + RainIntensity * 0.15f),
              SurfGain, DeltaSeconds, GlobalGain);
    ApplyGain(Gulls, 0.40f * HarborGain * Daylight * (1.0f - 0.70f * RainIntensity),
              GullGain, DeltaSeconds, GlobalGain);
    ApplyGain(Market, 0.34f * HarborGain * Daylight * (1.0f - 0.50f * RainIntensity),
              MarketGain, DeltaSeconds, GlobalGain);
    ApplyGain(Wind, HarborGain * WindStrength * 0.75f,
              WindGain, DeltaSeconds, GlobalGain);
    ApplyGain(Rain, HarborGain * RainIntensity * 0.75f,
              RainGain, DeltaSeconds, GlobalGain);
    ApplyGain(StormBed, HarborGain * FMath::Clamp((RainIntensity - 0.65f) / 0.35f,
                                                 0.0f, 1.0f) * 0.38f,
              StormGain, DeltaSeconds, GlobalGain);
}

void ATSTSSAudioEnvironmentDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    for (UAudioComponent* Component : {Surf.Get(), Gulls.Get(), Market.Get(),
                                      Wind.Get(), Rain.Get(), StormBed.Get()})
    {
        if (IsValid(Component)) Component->Stop();
    }
    Super::EndPlay(EndPlayReason);
}
