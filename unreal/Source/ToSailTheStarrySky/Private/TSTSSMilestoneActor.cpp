#include "TSTSSMilestoneActor.h"
#include "TSTSSAudioSubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

#if WITH_EDITOR
namespace
{
// Preserve consumed E-marker pass-through in standalone Editor Game and PIE,
// but never in unrelated, networked, failed-V3/V4, or shipping worlds.
bool IsAuthorizedReviewMilestoneWorld(const UWorld* World, const FString& Label)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")))
    {
        return false;
    }
    const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
    return (Label.StartsWith(TEXT("TSTSS_PRELUDE_REVIEW_")) &&
            (Scene == TEXT("FirstWake_PreludeInteraction_V2") ||
             Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))) ||
           (Label.StartsWith(TEXT("TSTSS_SPLASHDOWN_GREYBOX_")) &&
            Scene == TEXT("VS05_DenithFuelShanty"));
}
}
#endif

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
    // Audio is cosmetic and fires only AFTER the authoritative story state accepted the action.
    if (UWorld* AudioWorld = GetWorld())
    {
        if (UTSTSSAudioSubsystem* Audio = AudioWorld->GetSubsystem<UTSTSSAudioSubsystem>())
        {
            Audio->EmitCue(bIsInspectionStation
                ? FName(TEXT("repair.station_inspect.success"))
                : FName(TEXT("story.first_wake.milestone")), GetActorLocation());
        }
    }

#if WITH_EDITOR
    // These bright, solid review cubes are *not* production interaction art.
    // After a successful E press these non-shipping review markers must
    // stop hiding later E prompts in PIE AND standalone Editor Game mode.
    // Deny all production, unrelated and failed V3/V4 Worlds; never touch
    // gameplay saves, other actors, water authority or rejected markers.
    const UWorld* World = GetWorld();
    if (IsAuthorizedReviewMilestoneWorld(World, GetActorLabel()) &&
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
    if (!IsValid(State) ||
        !IsAuthorizedReviewMilestoneWorld(World, GetActorLabel()) ||
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
