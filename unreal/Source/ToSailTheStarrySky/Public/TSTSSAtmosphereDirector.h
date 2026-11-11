#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSAtmosphereDirector.generated.h"

class USceneComponent;
class UDirectionalLightComponent;
class USkyAtmosphereComponent;
class USkyLightComponent;
class UExponentialHeightFogComponent;
class UVolumetricCloudComponent;
class UStaticMeshComponent;
class UInstancedStaticMeshComponent;
class UMaterialInterface;
class UMaterialInstanceDynamic;

UENUM(BlueprintType)
enum class ETSTSSWeather : uint8
{
    Clear UMETA(DisplayName="Clear"),
    CoastalMist UMETA(DisplayName="Coastal mist"),
    Rain UMETA(DisplayName="Rain"),
    Storm UMETA(DisplayName="Storm"),
    Snow UMETA(DisplayName="Snow"),
    Blizzard UMETA(DisplayName="Blizzard"),
    AuroralVeil UMETA(DisplayName="Auroral veil")
};

/** Rendering-only values. They MUST NOT be treated as world, quest, or physics evidence. */
USTRUCT(BlueprintType)
struct FTSTSSAtmosphereProfile
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite) float ClockHours = 17.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float FogDensity = 0.008f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float FogFalloff = 0.18f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CloudCoverage = 0.35f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float RainIntensity = 0.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float SnowIntensity = 0.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float AuroraIntensity = 0.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WindSpeed = 4.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FLinearColor FogTint = FLinearColor(0.49f, 0.64f, 0.73f);
};

UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSAtmosphereDirector : public AActor
{
    GENERATED_BODY()

public:
    ATSTSSAtmosphereDirector();
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    /** Interruptible, independent of story gates, world time progression, and saves. */
    UFUNCTION(BlueprintCallable, Category="TSTSS|Atmosphere")
    void RequestWeather(ETSTSSWeather InWeather, float TransitionSeconds = 2.5f);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Atmosphere")
    void RequestTimeOfDay(float InClockHours, float TransitionSeconds = 3.0f);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Atmosphere")
    void SetReducedMotion(bool bEnabled);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Atmosphere")
    void SetLowQuality(bool bEnabled);

    UFUNCTION(BlueprintPure, Category="TSTSS|Atmosphere")
    FTSTSSAtmosphereProfile GetAtmosphereProfile() const { return Current; }

    UFUNCTION(BlueprintPure, Category="TSTSS|Atmosphere")
    ETSTSSWeather GetTargetWeather() const { return DesiredWeather; }

    UFUNCTION(CallInEditor, Category="TSTSS|Atmosphere|Preview")
    void PreviewHarborGoldenHour();
    UFUNCTION(CallInEditor, Category="TSTSS|Atmosphere|Preview")
    void PreviewSkyDaylight();
    UFUNCTION(CallInEditor, Category="TSTSS|Atmosphere|Preview")
    void PreviewStormDusk();
    UFUNCTION(CallInEditor, Category="TSTSS|Atmosphere|Preview")
    void PreviewSnowNight();
    UFUNCTION(CallInEditor, Category="TSTSS|Atmosphere|Preview")
    void PreviewAuroraNight();

    static FTSTSSAtmosphereProfile ProfileFor(ETSTSSWeather Weather, float ClockHours);
    static FTSTSSAtmosphereProfile Interpolate(const FTSTSSAtmosphereProfile& A,
                                               const FTSTSSAtmosphereProfile& B, float T);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Initial")
    ETSTSSWeather InitialWeather = ETSTSSWeather::CoastalMist;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Initial",
              meta=(ClampMin="0.0", ClampMax="24.0"))
    float InitialClockHours = 17.0f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Review")
    bool bAutoplayReviewCycle = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Access")
    bool bReducedMotion = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Access")
    bool bLowQuality = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Assets")
    TObjectPtr<UMaterialInterface> VolumetricCloudMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Assets")
    TObjectPtr<UMaterialInterface> StarAuroraMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Assets")
    TObjectPtr<UMaterialInterface> RainMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Atmosphere|Assets")
    TObjectPtr<UMaterialInterface> SnowMaterial;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<USceneComponent> SceneRoot;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UDirectionalLightComponent> Sun;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UDirectionalLightComponent> Moon;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<USkyAtmosphereComponent> Sky;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<USkyLightComponent> AmbientSky;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UVolumetricCloudComponent> Clouds;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UExponentialHeightFogComponent> HeightFog;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UStaticMeshComponent> StarDome;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UInstancedStaticMeshComponent> RainStreaks;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Atmosphere|Components")
    TObjectPtr<UInstancedStaticMeshComponent> SnowFlakes;

private:
    FTSTSSAtmosphereProfile Current;
    FTSTSSAtmosphereProfile From;
    FTSTSSAtmosphereProfile To;
    ETSTSSWeather DesiredWeather = ETSTSSWeather::CoastalMist;
    float BlendElapsed = 0.0f;
    float BlendDuration = 0.0f;
    float PrecipitationAccumulator = 0.0f;
    float DemoAccumulator = 0.0f;
    int32 DemoStep = 0;
    bool bBlending = false;
    TArray<FVector> RainOffsets;
    TArray<FVector> SnowOffsets;
    UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> DynamicStarMaterial;
    UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> DynamicCloudMaterial;

    void TransitionTo(const FTSTSSAtmosphereProfile& Next, float Seconds);
    void ApplyAtmosphere();
    void InitializePrecipitation();
    void UpdatePrecipitation(float DeltaSeconds);
    static FVector SeededOffset(int32 Index, float Width, float Height);
};
