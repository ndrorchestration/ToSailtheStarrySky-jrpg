#include "TSTSSMilestoneActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

ATSTSSMilestoneActor::ATSTSSMilestoneActor()
{
    PrimaryActorTick.bCanEverTick = false;
    InteractionMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InteractionMesh"));
    RootComponent = InteractionMesh;
    InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

bool ATSTSSMilestoneActor::TryActivate(UTSTSSFirstWakeState* State)
{
    if (!IsValid(State)) return false;
    // Only physics observations may establish sea contact and stable flotation.
    if (!bIsInspectionStation && (Milestone == ETSTSSFirstWakeBeat::SeaContact ||
        Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed)) return false;
    const bool bSucceeded = bIsInspectionStation
        ? State->InspectStation(InspectionStation)
        : State->AdvanceTo(Milestone);
    if (!bSucceeded) return false;
    OnMilestoneActivated();

#if WITH_EDITOR
    // These bright, solid review cubes are *not* production interaction art.
    // After a successful E press they must stop blocking the next marker's
    // camera ray and the reviewing pawn's route. This applies to the original
    // seven Prelude stops AND the three additive splashdown/recovery stops.
    // Never change failed/out-of-order gates, other actors, non-PIE worlds,
    // water physics, or gameplay saves.
    const UWorld* World = GetWorld();
    if (World && World->WorldType == EWorldType::PIE &&
        (GetActorLabel().StartsWith(TEXT("TSTSS_PRELUDE_REVIEW_")) ||
         GetActorLabel().StartsWith(TEXT("TSTSS_SPLASHDOWN_GREYBOX_"))) &&
        IsValid(InteractionMesh))
    {
        InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
        InteractionMesh->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
    }
#endif

    return true;
}
