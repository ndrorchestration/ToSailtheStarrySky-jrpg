#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSAudioSubsystem.h"
#include "TSTSSAudioCueBankActor.generated.h"

/** Optional placement in review level: binds approved SoundBase assets at BeginPlay.
    Without a placed bank and valid assets, gameplay stays safely silent. */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSAudioCueBankActor : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSAudioCueBankActor();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="TSTSS|Audio|Review")
    TArray<FTSTSSAudioCue> Cues;
};
