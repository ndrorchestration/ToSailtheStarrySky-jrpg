#include "TSTSSReviewRouteGate.h"
#include "TSTSSExplorerCharacter.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

ATSTSSReviewRouteGate::ATSTSSReviewRouteGate()
{
    PrimaryActorTick.bCanEverTick = false;
    InteractionMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ReviewGateInteraction"));
    RootComponent = InteractionMesh;
    InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionMesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

void ATSTSSReviewRouteGate::BeginPlay()
{
    Super::BeginPlay();
    // The editor serializes its BasicShapes cube as BlockAll. In PIE, E
    // still hits this gate, but it must never become a solid route obstacle.
    if (InteractionMesh)
    {
        InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        InteractionMesh->SetCollisionResponseToAllChannels(ECR_Ignore);
        InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    }
}

bool ATSTSSReviewRouteGate::TryTraverse(ATSTSSExplorerCharacter* Player)
{
#if WITH_EDITOR
    const UWorld* World = GetWorld();
    if (bTriggered || !World || World->WorldType != EWorldType::PIE ||
        !IsValid(Player) || Player->GetWorld() != World)
    {
        return false;
    }
    UGameInstance* Instance = World->GetGameInstance();
    UTSTSSReviewRouteSession* Session = Instance
        ? Instance->GetSubsystem<UTSTSSReviewRouteSession>() : nullptr;
    FString Destination;
    if (!Session ||
        !Session->ArmNextStage(World, DepartureStage, Player->GetFirstWakeState(), Destination))
    {
        return false;
    }
    // Opening a map cannot grant a story milestone. In particular this
    // never writes SeaContact or FlotationConfirmed to any state object.
    bTriggered = true;
    UE_LOG(LogTemp, Display, TEXT("TSTSS_REVIEW_TRAVEL_REQUESTED destination=%s"),
           *Destination);
    UGameplayStatics::OpenLevel(this, FName(*Destination), true);
    return true;
#else
    (void)Player;
    return false;
#endif
}
