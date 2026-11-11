#include "TSTSSHarborAudioZone.h"
#include "TSTSSAudioEnvironmentDirector.h"

#include "Components/BoxComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

ATSTSSHarborAudioZone::ATSTSSHarborAudioZone()
{
    PrimaryActorTick.bCanEverTick = false;
    Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("HarborSoundOnlyOverlap"));
    RootComponent = Trigger;
    Trigger->InitBoxExtent(FVector(400.f, 400.f, 200.f));
    Trigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Trigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    Trigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    Trigger->SetGenerateOverlapEvents(true);
}

void ATSTSSHarborAudioZone::BeginPlay()
{
    Super::BeginPlay();
    Trigger->OnComponentBeginOverlap.AddDynamic(this, &ATSTSSHarborAudioZone::OnPlayerEnter);
    Trigger->OnComponentEndOverlap.AddDynamic(this, &ATSTSSHarborAudioZone::OnPlayerLeave);
    // BeginPlay can occur after overlap state was established by actor placement.
    APlayerController* Player = UGameplayStatics::GetPlayerController(this, 0);
    if (IsValid(HarborAudio) && IsValid(Player) && IsValid(Player->GetPawn()) &&
        Trigger->IsOverlappingActor(Player->GetPawn()))
    {
        HarborAudio->SetHarborZoneAudible(true);
    }
}

void ATSTSSHarborAudioZone::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (IsValid(HarborAudio)) HarborAudio->SetHarborZoneAudible(false);
    Super::EndPlay(EndPlayReason);
}

void ATSTSSHarborAudioZone::OnPlayerEnter(
    UPrimitiveComponent* /*OverlapComponent*/, AActor* OtherActor,
    UPrimitiveComponent* /*OtherComponent*/, int32 /*BodyIndex*/,
    bool /*bFromSweep*/, const FHitResult& /*Sweep*/)
{
    APlayerController* Player = UGameplayStatics::GetPlayerController(this, 0);
    if (IsValid(HarborAudio) && IsValid(Player) && Player->GetPawn() == OtherActor)
    {
        HarborAudio->SetHarborZoneAudible(true);
    }
}

void ATSTSSHarborAudioZone::OnPlayerLeave(
    UPrimitiveComponent* /*OverlapComponent*/, AActor* OtherActor,
    UPrimitiveComponent* /*OtherComponent*/, int32 /*BodyIndex*/)
{
    APlayerController* Player = UGameplayStatics::GetPlayerController(this, 0);
    if (IsValid(HarborAudio) && IsValid(Player) && Player->GetPawn() == OtherActor)
    {
        HarborAudio->SetHarborZoneAudible(false);
    }
}
