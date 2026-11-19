#include "TSTSSMilestoneActor.h"
#include "Components/StaticMeshComponent.h"

ATSTSSMilestoneActor::ATSTSSMilestoneActor()
{
    PrimaryActorTick.bCanEverTick = false;
    InteractionMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InteractionMesh"));
    RootComponent = InteractionMesh;
    InteractionMesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    InteractionMesh->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
}

bool ATSTSSMilestoneActor::IsManualBeatAllowed(const ETSTSSFirstWakeBeat Beat)
{
    switch (Beat)
    {
    case ETSTSSFirstWakeBeat::FlyerDiscovered:
    case ETSTSSFirstWakeBeat::IoniaHired:
    case ETSTSSFirstWakeBeat::BoardedAureateWake:
    case ETSTSSFirstWakeBeat::EngineeringChecked:
    case ETSTSSFirstWakeBeat::Launched:
    case ETSTSSFirstWakeBeat::EmptyReserveInspected:
    case ETSTSSFirstWakeBeat::ReturnedToBerth:
        return true;
    default:
        return false;
    }
}

bool ATSTSSMilestoneActor::TryActivate(UTSTSSFirstWakeState* State)
{
    if (!IsValid(State)) return false;
    if (!bIsInspectionStation && !IsManualBeatAllowed(Milestone)) return false;
    const bool bSucceeded = bIsInspectionStation
        ? State->InspectStation(InspectionStation)
        : State->AdvanceTo(Milestone);
    if (!bSucceeded) return false;
    OnMilestoneActivated();
    return true;
}
