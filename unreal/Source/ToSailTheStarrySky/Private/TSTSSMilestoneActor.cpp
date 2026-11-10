#include "TSTSSMilestoneActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

ATSTSSMilestoneActor::ATSTSSMilestoneActor()
{
    PrimaryActorTick.bCanEverTick = false;
    InteractionMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InteractionMesh"));
    RootComponent = InteractionMesh;
    InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionMesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

void ATSTSSMilestoneActor::BeginPlay()
{
    Super::BeginPlay();
    // The existing saved review map explicitly serialized BlockAll on these
    // meshes. Reapply pass-through collision in PIE without rewriting the map.
    // The E visibility ray still hits each marker; pawn movement does not.
    InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionMesh->SetCollisionResponseToAllChannels(ECR_Ignore);
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

#if WITH_EDITOR
void ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(
    const UTSTSSFirstWakeState* State)
{
    // This is visual review collision state only. Never grants story beats,
    // changes water contact, or touches real production actor collision.
    const UWorld* World = GetWorld();
    if (!IsValid(State) || !World || World->WorldType != EWorldType::PIE ||
        !IsValid(InteractionMesh))
    {
        return;
    }
    const FString Label = GetActorLabel();
    if (!Label.StartsWith(TEXT("TSTSS_PRELUDE_REVIEW_")) &&
        !Label.StartsWith(TEXT("TSTSS_SPLASHDOWN_GREYBOX_")))
    {
        return;
    }
    // Actor-driven sea contact/flotation remains impossible even in review.
    if (!bIsInspectionStation &&
        (Milestone == ETSTSSFirstWakeBeat::SeaContact ||
         Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed))
    {
        return;
    }

    bool bAlreadyConsumed = false;
    if (bIsInspectionStation)
    {
        const uint8 StationBit =
            static_cast<uint8>(1u << static_cast<uint8>(InspectionStation));
        bAlreadyConsumed = State->HasStarted() &&
            (State->GetInspectionMask() & StationBit) != 0;
    }
    else
    {
        bAlreadyConsumed = State->HasStarted() &&
            static_cast<uint8>(State->GetCurrentBeat()) >=
            static_cast<uint8>(Milestone);
    }
    const ECollisionResponse ReviewResponse =
        bAlreadyConsumed ? ECR_Ignore : ECR_Block;
    InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ReviewResponse);
    // Restoring a marker must not restore the old walking obstruction.
    InteractionMesh->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
}
#endif
