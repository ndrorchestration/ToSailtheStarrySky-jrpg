#include "Enemies/TSTSSSliceEnemyReviewBattleConsole.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Components/SceneComponent.h"
#include "Components/TextRenderComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"

ATSTSSSliceEnemyReviewBattleConsole::ATSTSSSliceEnemyReviewBattleConsole()
{
    PrimaryActorTick.bCanEverTick = true;
    ReviewRoot = CreateDefaultSubobject<USceneComponent>(TEXT("ReviewRoot"));
    SetRootComponent(ReviewRoot);
    PreviewCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("EnemyReviewCamera"));
    PreviewCamera->SetupAttachment(ReviewRoot);
    PreviewCamera->SetRelativeLocation(FVector(0.f, -1450.f, 465.f));
    PreviewCamera->SetRelativeRotation(FRotator(-13.f, 90.f, 0.f));
    PreviewCamera->SetFieldOfView(60.f);
    ReviewSign = CreateDefaultSubobject<UTextRenderComponent>(TEXT("BattleInstructions"));
    ReviewSign->SetupAttachment(ReviewRoot);
    ReviewSign->SetWorldSize(24.f);
    ReviewSign->SetRelativeLocation(FVector(-230.f, -630.f, 265.f));
    ReviewSign->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
    ReviewSign->SetText(FText::FromString(
        TEXT("ENEMY BATTLE REVIEW / NO STORY PROGRESSION\n"
             "F7 Ender | F8 +Ionia | F9 after splashdown\n"
             "J strike foe 1 | K strike foe 2")));
    ReviewSign->SetTextRenderColor(FColor(150, 226, 244, 255));
    SetActorEnableCollision(false);
}

void ATSTSSSliceEnemyReviewBattleConsole::BeginPlay()
{
    Super::BeginPlay();
#if UE_BUILD_SHIPPING
    SetActorHiddenInGame(true);
    SetActorTickEnabled(false);
#else
    if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        PC->SetViewTargetWithBlend(this);
        EnableInput(PC);
        if (InputComponent)
        {
            InputComponent->BindKey(EKeys::F7, IE_Pressed, this,
                                    &ATSTSSSliceEnemyReviewBattleConsole::StartEnderOnly);
            InputComponent->BindKey(EKeys::F8, IE_Pressed, this,
                                    &ATSTSSSliceEnemyReviewBattleConsole::StartIoniaRecruited);
            InputComponent->BindKey(EKeys::F9, IE_Pressed, this,
                                    &ATSTSSSliceEnemyReviewBattleConsole::StartAfterSplashdown);
            InputComponent->BindKey(EKeys::J, IE_Pressed, this,
                                    &ATSTSSSliceEnemyReviewBattleConsole::StrikeFirst);
            InputComponent->BindKey(EKeys::K, IE_Pressed, this,
                                    &ATSTSSSliceEnemyReviewBattleConsole::StrikeSecond);
        }
    }
    RefreshStatus();
#endif
}

bool ATSTSSSliceEnemyReviewBattleConsole::TryStartPreview(ETSTSSSliceReviewPartyStage Stage)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    // Starting a new isolated review explicitly replaces the prior session,
    // never a campaign battle, and retains no persistent game state.
    UTSTSSSliceEnemyReviewSession* Next =
        NewObject<UTSTSSSliceEnemyReviewSession>(this);
    if (!IsValid(Next) || !Next->TryStart(ReviewWavePreset, Stage)) return false;
    Session = Next;
    RefreshStatus();
    return true;
#endif
}

bool ATSTSSSliceEnemyReviewBattleConsole::TryStrikePreview(int32 EnemySlot)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!IsValid(Session.Get()) || !Session->TryPlayerStrike(EnemySlot)) return false;
    RefreshStatus();
    return true;
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::StartEnderOnly()
{
    TryStartPreview(ETSTSSSliceReviewPartyStage::EnderOnly);
}
void ATSTSSSliceEnemyReviewBattleConsole::StartIoniaRecruited()
{
    TryStartPreview(ETSTSSSliceReviewPartyStage::IoniaRecruited);
}
void ATSTSSSliceEnemyReviewBattleConsole::StartAfterSplashdown()
{
    TryStartPreview(ETSTSSSliceReviewPartyStage::AfterSplashdown);
}
void ATSTSSSliceEnemyReviewBattleConsole::StrikeFirst() { TryStrikePreview(0); }
void ATSTSSSliceEnemyReviewBattleConsole::StrikeSecond() { TryStrikePreview(1); }

void ATSTSSSliceEnemyReviewBattleConsole::RefreshStatus()
{
#if !UE_BUILD_SHIPPING
    const FString Text = IsValid(Session.Get())
        ? Session->GetReviewStatus()
        : TEXT("F7: Ender | F8: Ionia | F9: Post-splashdown Lyra | J/K: Strike");
    if (GEngine && GetWorld() && GetWorld()->IsGameWorld())
    {
        // Non-persistent debug overlay. No UMG or production HUD implied.
        GEngine->AddOnScreenDebugMessage(87654321, 8.f, FColor::Cyan, Text);
    }
    StatusAge = 0.f;
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    StatusAge += DeltaSeconds;
    if (StatusAge >= 5.f) RefreshStatus();
#endif
}
