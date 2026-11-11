#include "TSTSSAudioCueBankActor.h"
#include "Engine/World.h"

ATSTSSAudioCueBankActor::ATSTSSAudioCueBankActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ATSTSSAudioCueBankActor::BeginPlay()
{
    Super::BeginPlay();
    UWorld* World = GetWorld();
    if (!World) return;
    UTSTSSAudioSubsystem* Audio = World->GetSubsystem<UTSTSSAudioSubsystem>();
    if (!Audio) return;
    for (const FTSTSSAudioCue& Cue : Cues)
    {
        Audio->RegisterCue(Cue); // invalid assets are denied without affecting story/physics
    }
}
