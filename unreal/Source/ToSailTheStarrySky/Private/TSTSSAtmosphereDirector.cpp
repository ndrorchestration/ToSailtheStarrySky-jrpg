#include "TSTSSAtmosphereDirector.h"
#include "TSTSSAudioSubsystem.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/VolumetricCloudComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
constexpr int32 RainCount = 112;
constexpr int32 SnowCount = 80;
constexpr float PrecipitationStep = 0.05f;
constexpr float Pi = 3.14159265358979323846f;

float NormalizedHour(float Hour)
{
    return FMath::Fmod(FMath::Fmod(Hour, 24.0f) + 24.0f, 24.0f);
}
}

ATSTSSAtmosphereDirector::ATSTSSAtmosphereDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("AtmosphereRoot"));
    RootComponent = SceneRoot;

    Sun = CreateDefaultSubobject<UDirectionalLightComponent>(TEXT("PrimarySun"));
    Sun->SetupAttachment(SceneRoot);
    Sun->SetMobility(EComponentMobility::Movable);
    Sun->SetAtmosphereSunLight(true);
    Sun->SetAtmosphereSunLightIndex(0);
    Sun->SetIntensity(80000.0f);
    Sun->SetCastVolumetricShadow(true);

    Moon = CreateDefaultSubobject<UDirectionalLightComponent>(TEXT("SecondaryMoon"));
    Moon->SetupAttachment(SceneRoot);
    Moon->SetMobility(EComponentMobility::Movable);
    Moon->SetAtmosphereSunLight(true);
    Moon->SetAtmosphereSunLightIndex(1);
    Moon->SetIntensity(0.0f);
    Moon->SetLightColor(FLinearColor(0.45f, 0.68f, 1.0f));

    Sky = CreateDefaultSubobject<USkyAtmosphereComponent>(TEXT("PhysicalSky"));
    Sky->SetupAttachment(SceneRoot);
    AmbientSky = CreateDefaultSubobject<USkyLightComponent>(TEXT("SkyBounce"));
    AmbientSky->SetupAttachment(SceneRoot);
    AmbientSky->SetMobility(EComponentMobility::Movable);
    AmbientSky->SetIntensity(0.75f);

    Clouds = CreateDefaultSubobject<UVolumetricCloudComponent>(TEXT("LayeredClouds"));
    Clouds->SetupAttachment(SceneRoot);
    Clouds->SetLayerBottomAltitude(1.8f);
    Clouds->SetLayerHeight(5.0f);

    HeightFog = CreateDefaultSubobject<UExponentialHeightFogComponent>(TEXT("CoastalVolumetricFog"));
    HeightFog->SetupAttachment(SceneRoot);
    HeightFog->SetFogDensity(0.008f);
    HeightFog->SetFogHeightFalloff(0.18f);
    HeightFog->SetVolumetricFog(true);

    StarDome = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("StarsAndAurora"));
    StarDome->SetupAttachment(SceneRoot);
    StarDome->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    StarDome->SetCastShadow(false);
    StarDome->SetMobility(EComponentMobility::Movable);
    StarDome->SetRelativeScale3D(FVector(40000.0f));
    StarDome->SetVisibility(false); // Never display the engine default opaque sphere.

    RainStreaks = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("CameraLocalRain"));
    RainStreaks->SetupAttachment(SceneRoot);
    RainStreaks->SetMobility(EComponentMobility::Movable);
    RainStreaks->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RainStreaks->SetCastShadow(false);
    RainStreaks->SetVisibility(false);

    SnowFlakes = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("CameraLocalSnow"));
    SnowFlakes->SetupAttachment(SceneRoot);
    SnowFlakes->SetMobility(EComponentMobility::Movable);
    SnowFlakes->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SnowFlakes->SetCastShadow(false);
    SnowFlakes->SetVisibility(false);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> Plane(TEXT("/Engine/BasicShapes/Plane.Plane"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (Plane.Succeeded())
    {
        RainStreaks->SetStaticMesh(Plane.Object);
        SnowFlakes->SetStaticMesh(Plane.Object);
    }
    if (Sphere.Succeeded())
    {
        StarDome->SetStaticMesh(Sphere.Object);
    }
}

FTSTSSAtmosphereProfile ATSTSSAtmosphereDirector::ProfileFor(ETSTSSWeather Weather, float ClockHours)
{
    FTSTSSAtmosphereProfile P;
    P.ClockHours = FMath::IsFinite(ClockHours) ? NormalizedHour(ClockHours) : 17.0f;
    switch (Weather)
    {
    case ETSTSSWeather::Clear:
        P.FogDensity = 0.004f; P.CloudCoverage = 0.22f; P.WindSpeed = 3.0f;
        P.FogTint = FLinearColor(0.48f, 0.66f, 0.80f); break;
    case ETSTSSWeather::CoastalMist:
        P.FogDensity = 0.018f; P.CloudCoverage = 0.46f; P.WindSpeed = 4.0f;
        P.FogTint = FLinearColor(0.41f, 0.58f, 0.64f); break;
    case ETSTSSWeather::Rain:
        P.FogDensity = 0.023f; P.CloudCoverage = 0.78f; P.RainIntensity = 0.65f;
        P.WindSpeed = 8.0f; P.FogTint = FLinearColor(0.35f, 0.47f, 0.55f); break;
    case ETSTSSWeather::Storm:
        P.FogDensity = 0.042f; P.CloudCoverage = 0.99f; P.RainIntensity = 1.0f;
        P.WindSpeed = 21.0f; P.FogTint = FLinearColor(0.24f, 0.35f, 0.45f); break;
    case ETSTSSWeather::Snow:
        P.FogDensity = 0.025f; P.CloudCoverage = 0.85f; P.SnowIntensity = 0.7f;
        P.WindSpeed = 5.0f; P.FogTint = FLinearColor(0.61f, 0.72f, 0.83f); break;
    case ETSTSSWeather::Blizzard:
        P.FogDensity = 0.070f; P.CloudCoverage = 1.0f; P.SnowIntensity = 1.0f;
        P.WindSpeed = 25.0f; P.FogTint = FLinearColor(0.60f, 0.71f, 0.79f); break;
    case ETSTSSWeather::AuroralVeil:
        P.AuroraIntensity = 0.72f;
        P.FogDensity = 0.010f; P.CloudCoverage = 0.20f; P.WindSpeed = 2.0f;
        P.FogTint = FLinearColor(0.15f, 0.35f, 0.37f); break;
    default:
        return ProfileFor(ETSTSSWeather::Clear, ClockHours);
    }
    return P;
}

FTSTSSAtmosphereProfile ATSTSSAtmosphereDirector::Interpolate(
    const FTSTSSAtmosphereProfile& A, const FTSTSSAtmosphereProfile& B, float T)
{
    const float S = FMath::Clamp(T, 0.0f, 1.0f);
    FTSTSSAtmosphereProfile R;
    // Shortest arc: 23:00 to 01:00 stays dark instead of flashing through noon.
    const float ClockDelta = FMath::Fmod(B.ClockHours - A.ClockHours + 36.0f, 24.0f) - 12.0f;
    R.ClockHours = NormalizedHour(A.ClockHours + ClockDelta * S);
    R.FogDensity = FMath::Lerp(A.FogDensity, B.FogDensity, S);
    R.FogFalloff = FMath::Lerp(A.FogFalloff, B.FogFalloff, S);
    R.CloudCoverage = FMath::Lerp(A.CloudCoverage, B.CloudCoverage, S);
    R.RainIntensity = FMath::Lerp(A.RainIntensity, B.RainIntensity, S);
    R.SnowIntensity = FMath::Lerp(A.SnowIntensity, B.SnowIntensity, S);
    R.AuroraIntensity = FMath::Lerp(A.AuroraIntensity, B.AuroraIntensity, S);
    R.WindSpeed = FMath::Lerp(A.WindSpeed, B.WindSpeed, S);
    R.FogTint = FMath::Lerp(A.FogTint, B.FogTint, S);
    return R;
}

void ATSTSSAtmosphereDirector::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    // A true Editor viewport preview, not just a BeginPlay-only runtime effect.
    DesiredWeather = InitialWeather;
    Current = ProfileFor(InitialWeather, InitialClockHours);
    From = To = Current;
    bBlending = false;
    if (VolumetricCloudMaterial)
    {
        DynamicCloudMaterial = UMaterialInstanceDynamic::Create(VolumetricCloudMaterial, this);
        Clouds->SetMaterial(DynamicCloudMaterial);
    }
    if (StarAuroraMaterial)
    {
        DynamicStarMaterial = UMaterialInstanceDynamic::Create(StarAuroraMaterial, this);
        StarDome->SetMaterial(0, DynamicStarMaterial);
    }
    if (RainMaterial) RainStreaks->SetMaterial(0, RainMaterial);
    if (SnowMaterial) SnowFlakes->SetMaterial(0, SnowMaterial);
    ApplyAtmosphere();
}

void ATSTSSAtmosphereDirector::BeginPlay()
{
    Super::BeginPlay();
    DesiredWeather = InitialWeather;
    Current = ProfileFor(InitialWeather, InitialClockHours);
    From = To = Current;
    InitializePrecipitation();
    ApplyAtmosphere();
    if (!bLowQuality) AmbientSky->RecaptureSky();
}

void ATSTSSAtmosphereDirector::TransitionTo(const FTSTSSAtmosphereProfile& Next, float Seconds)
{
    if (!FMath::IsFinite(Seconds) || Seconds < 0.0f)
    {
        return;
    }
    From = Current;
    To = Next;
    BlendElapsed = 0.0f;
    BlendDuration = FMath::Clamp(Seconds, 0.0f, 60.0f);
    bBlending = !bReducedMotion && BlendDuration > KINDA_SMALL_NUMBER;
    if (!bBlending)
    {
        Current = To;
        ApplyAtmosphere();
    }
}

void ATSTSSAtmosphereDirector::RequestWeather(ETSTSSWeather InWeather, float TransitionSeconds)
{
    if (static_cast<uint8>(InWeather) > static_cast<uint8>(ETSTSSWeather::AuroralVeil)
        || !FMath::IsFinite(TransitionSeconds) || TransitionSeconds < 0.0f)
    {
        return;
    }
    const ETSTSSWeather PreviousWeather = DesiredWeather;
    DesiredWeather = InWeather;
    TransitionTo(ProfileFor(DesiredWeather, bBlending ? To.ClockHours : Current.ClockHours), TransitionSeconds);

    // Accepted transitions may request only the corresponding audio; weather visuals
    // and sound may not certify a storm event, alter physics or advance story state.
    if (PreviousWeather != InWeather)
    {
        const FName WeatherEvent = InWeather == ETSTSSWeather::Storm
            ? FName(TEXT("weather.storm.begin"))
            : (PreviousWeather == ETSTSSWeather::Storm
                ? FName(TEXT("weather.storm.end")) : NAME_None);
        if (!WeatherEvent.IsNone())
        {
            if (UWorld* AudioWorld = GetWorld())
            {
                if (UTSTSSAudioSubsystem* Audio = AudioWorld->GetSubsystem<UTSTSSAudioSubsystem>())
                {
                    Audio->EmitCue(WeatherEvent, GetActorLocation());
                }
            }
        }
    }
}

void ATSTSSAtmosphereDirector::RequestTimeOfDay(float InClockHours, float TransitionSeconds)
{
    if (!FMath::IsFinite(InClockHours) || !FMath::IsFinite(TransitionSeconds) ||
        TransitionSeconds < 0.0f)
    {
        return;
    }
    TransitionTo(ProfileFor(DesiredWeather, InClockHours), TransitionSeconds);
}

void ATSTSSAtmosphereDirector::SetReducedMotion(bool bEnabled)
{
    bReducedMotion = bEnabled;
    if (bReducedMotion && bBlending)
    {
        bBlending = false;
        Current = To;
        ApplyAtmosphere();
    }
    RainStreaks->SetVisibility(!bReducedMotion && Current.RainIntensity > 0.01f && RainMaterial != nullptr);
    SnowFlakes->SetVisibility(!bReducedMotion && Current.SnowIntensity > 0.01f && SnowMaterial != nullptr);
    ApplyAtmosphere();
}

void ATSTSSAtmosphereDirector::SetLowQuality(bool bEnabled)
{
    bLowQuality = bEnabled;
    ApplyAtmosphere();
}

void ATSTSSAtmosphereDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.0f) return;
    if (bAutoplayReviewCycle && !bReducedMotion)
    {
        DemoAccumulator += DeltaSeconds;
        if (DemoAccumulator >= 9.0f)
        {
            DemoAccumulator = FMath::Fmod(DemoAccumulator, 9.0f);
            DemoStep = (DemoStep + 1) % 5;
            switch (DemoStep)
            {
            case 0: PreviewHarborGoldenHour(); break;
            case 1: RequestWeather(ETSTSSWeather::Clear, 3.0f); RequestTimeOfDay(12.5f, 3.0f); break;
            case 2: RequestWeather(ETSTSSWeather::Storm, 3.0f); RequestTimeOfDay(19.0f, 3.0f); break;
            case 3: RequestWeather(ETSTSSWeather::Snow, 3.0f); RequestTimeOfDay(22.0f, 3.0f); break;
            case 4: RequestWeather(ETSTSSWeather::AuroralVeil, 3.0f); RequestTimeOfDay(23.0f, 3.0f); break;
            }
        }
    }
    if (bBlending)
    {
        BlendElapsed = FMath::Min(BlendElapsed + DeltaSeconds, BlendDuration);
        const float T = FMath::Clamp(BlendElapsed / BlendDuration, 0.0f, 1.0f);
        const float Ease = T * T * (3.0f - 2.0f * T);
        Current = Interpolate(From, To, Ease);
        const bool bArrived = T >= 1.0f;
        if (bArrived) bBlending = false;
        ApplyAtmosphere();
        // Rebuild sky-bounce only when settled, never every animation frame.
        if (bArrived && !bLowQuality) AmbientSky->RecaptureSky();
    }
    if (!bReducedMotion)
    {
        PrecipitationAccumulator += DeltaSeconds;
        if (PrecipitationAccumulator >= PrecipitationStep)
        {
            UpdatePrecipitation(PrecipitationAccumulator);
            PrecipitationAccumulator = 0.0f;
        }
    }
}

void ATSTSSAtmosphereDirector::ApplyAtmosphere()
{
    if (!Sun || !Moon || !HeightFog || !Clouds) return;
    const float Hour = NormalizedHour(Current.ClockHours);
    const float Elevation = 75.0f * FMath::Sin((Hour - 6.0f) * Pi / 12.0f);
    const float DayFactor = FMath::Clamp((Elevation + 2.0f) / 13.0f, 0.0f, 1.0f);
    const float NightFactor = FMath::Clamp((2.0f - Elevation) / 15.0f, 0.0f, 1.0f);
    const float Overcast = FMath::Clamp(Current.CloudCoverage, 0.0f, 1.0f);
    Sun->SetWorldRotation(FRotator(-Elevation, 175.0f, 0.0f));
    Sun->SetIntensity(85000.0f * DayFactor * (1.0f - Overcast * 0.67f));
    const float Warmth = FMath::Clamp(Elevation / 30.0f, 0.0f, 1.0f);
    Sun->SetLightColor(FMath::Lerp(FLinearColor(1.0f, 0.54f, 0.29f),
                                   FLinearColor(1.0f, 0.96f, 0.87f), Warmth));
    Moon->SetWorldRotation(FRotator(Elevation, -5.0f, 0.0f));
    Moon->SetIntensity(0.3f * NightFactor);
    HeightFog->SetFogDensity(FMath::Clamp(Current.FogDensity, 0.0f, 0.09f));
    HeightFog->SetFogHeightFalloff(Current.FogFalloff);
    HeightFog->SetFogInscatteringColor(Current.FogTint * FMath::Lerp(0.24f, 1.0f, DayFactor));
    AmbientSky->SetIntensity(FMath::Lerp(0.23f, 0.85f, DayFactor) *
                             (1.0f - Overcast * 0.35f));
    Clouds->SetLayerHeight(FMath::Lerp(2.8f, 6.4f, Overcast));
    Clouds->SetVisibility(!bLowQuality && VolumetricCloudMaterial != nullptr && Overcast > 0.05f);
    if (DynamicCloudMaterial)
    {
        DynamicCloudMaterial->SetScalarParameterValue(TEXT("CloudCoverage"), Overcast);
    }
    if (DynamicStarMaterial)
    {
        DynamicStarMaterial->SetScalarParameterValue(TEXT("NightFactor"), NightFactor);
        DynamicStarMaterial->SetScalarParameterValue(TEXT("MotionScale"), bReducedMotion ? 0.0f : 1.0f);
        DynamicStarMaterial->SetScalarParameterValue(TEXT("AuroraStrength"), Current.AuroraIntensity);
    }
    StarDome->SetVisibility(StarAuroraMaterial != nullptr);
    RainStreaks->SetVisibility(!bReducedMotion && RainMaterial != nullptr && Current.RainIntensity > 0.01f);
    SnowFlakes->SetVisibility(!bReducedMotion && SnowMaterial != nullptr && Current.SnowIntensity > 0.01f);
}

FVector ATSTSSAtmosphereDirector::SeededOffset(int32 Index, float Width, float Height)
{
    const float X = FMath::Frac(FMath::Sin(static_cast<float>(Index * 127 + 31) * 0.1731f) * 13758.5453f);
    const float Y = FMath::Frac(FMath::Sin(static_cast<float>(Index * 71 + 53) * 0.3391f) * 8749.1283f);
    const float Z = FMath::Frac(FMath::Sin(static_cast<float>(Index * 47 + 97) * 0.6113f) * 6345.3913f);
    return FVector((X - 0.5f) * Width, (Y - 0.5f) * Width, Z * Height - Height * 0.25f);
}

void ATSTSSAtmosphereDirector::InitializePrecipitation()
{
    if (VolumetricCloudMaterial)
    {
        DynamicCloudMaterial = UMaterialInstanceDynamic::Create(VolumetricCloudMaterial, this);
        Clouds->SetMaterial(DynamicCloudMaterial);
    }
    if (StarAuroraMaterial)
    {
        DynamicStarMaterial = UMaterialInstanceDynamic::Create(StarAuroraMaterial, this);
        StarDome->SetMaterial(0, DynamicStarMaterial);
    }
    if (RainMaterial) RainStreaks->SetMaterial(0, RainMaterial);
    if (SnowMaterial) SnowFlakes->SetMaterial(0, SnowMaterial);
    RainStreaks->ClearInstances();
    SnowFlakes->ClearInstances();
    RainOffsets.Reset(RainCount);
    SnowOffsets.Reset(SnowCount);
    for (int32 I = 0; I < RainCount; ++I)
    {
        RainOffsets.Add(SeededOffset(I, 1800.0f, 1200.0f));
        RainStreaks->AddInstance(FTransform::Identity);
    }
    for (int32 I = 0; I < SnowCount; ++I)
    {
        SnowOffsets.Add(SeededOffset(I + 1000, 1500.0f, 950.0f));
        SnowFlakes->AddInstance(FTransform::Identity);
    }
}

void ATSTSSAtmosphereDirector::UpdatePrecipitation(float DeltaSeconds)
{
    const APlayerCameraManager* Camera = UGameplayStatics::GetPlayerCameraManager(this, 0);
    const FVector Center = Camera ? Camera->GetCameraLocation() : GetActorLocation();
    const float CameraYaw = Camera ? Camera->GetCameraRotation().Yaw : 0.0f;
    const FRotator Facing(90.0f, CameraYaw, 0.0f);
    const FVector Wind(Current.WindSpeed * DeltaSeconds * 12.0f, 0.0f, 0.0f);
    const int32 MaxRain = bLowQuality ? 28 : RainCount;
    const int32 MaxSnow = bLowQuality ? 22 : SnowCount;
    const int32 VisibleRain = FMath::RoundToInt(MaxRain * FMath::Clamp(Current.RainIntensity, 0.0f, 1.0f));
    const int32 VisibleSnow = FMath::RoundToInt(MaxSnow * FMath::Clamp(Current.SnowIntensity, 0.0f, 1.0f));
    for (int32 I = 0; I < RainOffsets.Num(); ++I)
    {
        FVector& P = RainOffsets[I];
        P += Wind + FVector(0.0f, 0.0f, -2100.0f * DeltaSeconds);
        if (P.Z < -350.0f) P.Z += 1200.0f;
        if (P.X > 900.0f) P.X -= 1800.0f;
        const FVector Scale = I < VisibleRain ? FVector(0.013f, 0.38f, 0.013f) : FVector::ZeroVector;
        RainStreaks->UpdateInstanceTransform(I, FTransform(Facing, Center + P, Scale), true, I == RainOffsets.Num() - 1, true);
    }
    for (int32 I = 0; I < SnowOffsets.Num(); ++I)
    {
        FVector& P = SnowOffsets[I];
        P += Wind * 0.5f + FVector(7.0f * DeltaSeconds, 0.0f, -105.0f * DeltaSeconds);
        if (P.Z < -300.0f) P.Z += 950.0f;
        if (P.X > 750.0f) P.X -= 1500.0f;
        const FVector Scale = I < VisibleSnow ? FVector(0.023f, 0.023f, 0.023f) : FVector::ZeroVector;
        SnowFlakes->UpdateInstanceTransform(I, FTransform(Facing, Center + P, Scale), true, I == SnowOffsets.Num() - 1, true);
    }
}

void ATSTSSAtmosphereDirector::PreviewHarborGoldenHour()
{
    RequestWeather(ETSTSSWeather::CoastalMist, 0.0f);
    RequestTimeOfDay(17.0f, 0.0f);
}
void ATSTSSAtmosphereDirector::PreviewSkyDaylight()
{
    RequestWeather(ETSTSSWeather::Clear, 0.0f);
    RequestTimeOfDay(12.5f, 0.0f);
}
void ATSTSSAtmosphereDirector::PreviewStormDusk()
{
    RequestWeather(ETSTSSWeather::Storm, 0.0f);
    RequestTimeOfDay(19.0f, 0.0f);
}
void ATSTSSAtmosphereDirector::PreviewSnowNight()
{
    RequestWeather(ETSTSSWeather::Snow, 0.0f);
    RequestTimeOfDay(22.0f, 0.0f);
}
void ATSTSSAtmosphereDirector::PreviewAuroraNight()
{
    RequestWeather(ETSTSSWeather::AuroralVeil, 0.0f);
    RequestTimeOfDay(23.0f, 0.0f);
}
