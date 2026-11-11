#include "Enemies/TSTSSSliceEnemyReviewBattleConsole.h"
#include "Enemies/TSTSSSliceEnemyReviewHUD.h"
#include "Enemies/TSTSSSliceEnemyActor.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/SceneComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Blueprint/UserWidget.h"

namespace
{
    const FName ReviewWaves[] = {
        TEXT("Review_HarborBanditPatrol"),
        TEXT("Review_HarborBanditCaptain"),
        TEXT("Review_WoodlandSporeline"),
        TEXT("Review_WoodlandSentinel"),
        TEXT("Review_CoastalHunters"),
        TEXT("Review_CoastalShellbacks"),
        TEXT("Review_HighlandStalkers"),
        TEXT("Review_HighlandBristle")
    };
    constexpr int32 WaveCount = UE_ARRAY_COUNT(ReviewWaves);

    FString DisplayWave(FName Id)
    {
        FString Name = Id.ToString();
        Name.RemoveFromStart(TEXT("Review_"));
        Name.ReplaceInline(TEXT("_"), TEXT(" "));
        return Name;
    }
}

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
             "Q/E change waves | F7 Ender | F8 +Ionia | F9 +Lyra\n"
             "J strike foe 1 | K strike foe 2 | R reset")));
    ReviewSign->SetTextRenderColor(FColor(150, 226, 244, 255));
    // Lightweight named actors for review-only victory choreography.
    // These are not canonical Ender/Ionia/Lyra meshes or rigged animations.
    EnderVictoryProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VictoryEnderProxy"));
    IoniaVictoryProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VictoryIoniaProxy"));
    LyraVictoryProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VictoryLyraProxy"));
    EnderVictoryProxy->SetupAttachment(ReviewRoot);
    IoniaVictoryProxy->SetupAttachment(ReviewRoot);
    LyraVictoryProxy->SetupAttachment(ReviewRoot);
    EnderVictoryProxy->SetRelativeLocation(FVector(-450.f,-310.f,75.f));
    IoniaVictoryProxy->SetRelativeLocation(FVector(-240.f,-310.f,75.f));
    LyraVictoryProxy->SetRelativeLocation(FVector(-30.f,-310.f,75.f));
    EnderVictoryLabel=CreateDefaultSubobject<UTextRenderComponent>(TEXT("VictoryEnderName"));
    IoniaVictoryLabel=CreateDefaultSubobject<UTextRenderComponent>(TEXT("VictoryIoniaName"));
    LyraVictoryLabel=CreateDefaultSubobject<UTextRenderComponent>(TEXT("VictoryLyraName"));
    EnderVictoryLabel->SetupAttachment(EnderVictoryProxy);
    IoniaVictoryLabel->SetupAttachment(IoniaVictoryProxy);
    LyraVictoryLabel->SetupAttachment(LyraVictoryProxy);
    EnderVictoryLabel->SetRelativeLocation(FVector(0.f,0.f,125.f));
    IoniaVictoryLabel->SetRelativeLocation(FVector(0.f,0.f,125.f));
    LyraVictoryLabel->SetRelativeLocation(FVector(0.f,0.f,125.f));
    EnderVictoryLabel->SetWorldSize(30.f);
    IoniaVictoryLabel->SetWorldSize(30.f);
    LyraVictoryLabel->SetWorldSize(30.f);
    EnderVictoryLabel->SetText(FText::FromString(TEXT("ENDER")));
    IoniaVictoryLabel->SetText(FText::FromString(TEXT("IONIA")));
    LyraVictoryLabel->SetText(FText::FromString(TEXT("LYRA")));
    EnderVictoryLabel->SetTextRenderColor(FColor(112,228,183));
    IoniaVictoryLabel->SetTextRenderColor(FColor(255,213,107));
    LyraVictoryLabel->SetTextRenderColor(FColor(112,193,255));
    for (UStaticMeshComponent* Proxy : {EnderVictoryProxy.Get(),
         IoniaVictoryProxy.Get(),LyraVictoryProxy.Get()})
    {
        Proxy->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Proxy->SetGenerateOverlapEvents(false);
        Proxy->SetRelativeScale3D(FVector(.6f,.6f,1.3f));
        Proxy->SetVisibility(false,true);
    }
    SetActorEnableCollision(false);
}

void ATSTSSSliceEnemyReviewBattleConsole::BeginPlay()
{
    Super::BeginPlay();
#if UE_BUILD_SHIPPING
    SetActorHiddenInGame(true);
    SetActorTickEnabled(false);
#else
    if (UWorld* World = GetWorld())
    {
        if (World->IsGameWorld())
        {

            CaptureReviewActors();
            UStaticMesh* ReviewCapsule=LoadObject<UStaticMesh>(
                nullptr,TEXT("/Engine/BasicShapes/Capsule.Capsule"));
            if (IsValid(ReviewCapsule))
            {
                EnderVictoryProxy->SetStaticMesh(ReviewCapsule);
                IoniaVictoryProxy->SetStaticMesh(ReviewCapsule);
                LyraVictoryProxy->SetStaticMesh(ReviewCapsule);
            }
            SetVictoryCelebrationActive(false);
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
                    InputComponent->BindKey(EKeys::Q, IE_Pressed, this,
                        &ATSTSSSliceEnemyReviewBattleConsole::SelectPreviousWave);
                    InputComponent->BindKey(EKeys::E, IE_Pressed, this,
                        &ATSTSSSliceEnemyReviewBattleConsole::SelectNextWave);
                    InputComponent->BindKey(EKeys::R, IE_Pressed, this,
                        &ATSTSSSliceEnemyReviewBattleConsole::ResetReviewArena);
                }
                ReviewHUD = CreateWidget<UTSTSSSliceEnemyReviewHUD>(
                    PC, UTSTSSSliceEnemyReviewHUD::StaticClass());
                if (IsValid(ReviewHUD.Get()))
                {
                    ReviewHUD->AddToViewport(80);
                }
            }
        }
    }
    RefreshStatus();
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::CaptureReviewActors()
{
#if !UE_BUILD_SHIPPING
    if (!GetWorld() || !GetWorld()->IsGameWorld()) return;
    GalleryActors.Reset();
    SavedGalleryTransforms.Reset();
    for (TActorIterator<ATSTSSSliceEnemyActor> It(GetWorld()); It; ++It)
    {
        ATSTSSSliceEnemyActor* Actor=*It;
        if (!IsValid(Actor)) continue;
        GalleryActors.Add(Actor);
        SavedGalleryTransforms.Add(Actor->GetActorTransform());
    }
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::PresentCurrentWave()
{
#if !UE_BUILD_SHIPPING
    if (!GetWorld() || !GetWorld()->IsGameWorld() ||
        !IsValid(Session.Get())) return;
    if (GalleryActors.Num()!=15) CaptureReviewActors();
    ActiveEnemyActors.Reset();
    for (ATSTSSSliceEnemyActor* Actor : GalleryActors)
    {
        if (IsValid(Actor)) Actor->SetActorHiddenInGame(true);
    }
    for (int32 Slot=0;Slot<2;++Slot)
    {
        ETSTSSSliceEnemyKind Kind=ETSTSSSliceEnemyKind::HarmonicShear;
        if (!Session->TryGetReviewEnemyKind(Slot, Kind)) return;
        ATSTSSSliceEnemyActor* Match=nullptr;
        for (ATSTSSSliceEnemyActor* Actor:GalleryActors)
        {
            if (IsValid(Actor) && Actor->Kind==Kind &&
                !ActiveEnemyActors.Contains(Actor))
            {
                Match=Actor;
                break;
            }
        }
        if (!IsValid(Match))
        {
            // Missing visuals may never make combat use the wrong creature.
            ActiveEnemyActors.Reset();
            return;
        }
        Match->SetActorHiddenInGame(false);
        Match->SetActorLocation(GetActorLocation() +
            FVector(Slot==0 ? -260.f : 260.f, 180.f, 0.f));
        ActiveEnemyActors.Add(Match);
    }
#endif
}

bool ATSTSSSliceEnemyReviewBattleConsole::TryStartPreview(
    ETSTSSSliceReviewPartyStage Stage)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    UTSTSSSliceEnemyReviewSession* Next =
        NewObject<UTSTSSSliceEnemyReviewSession>(this);
    if (!IsValid(Next) || !Next->TryStart(ReviewWavePreset, Stage)) return false;

    if (IsValid(Session.Get()) && IsValid(Session->GetReviewManager()))
    {
        Session->GetReviewManager()->OnSkillAccepted.RemoveDynamic(
            this, &ATSTSSSliceEnemyReviewBattleConsole::OnReviewSkillAccepted);
    }
    Session=Next;
    if (IsValid(Session->GetReviewManager()))
    {
        Session->GetReviewManager()->OnSkillAccepted.AddDynamic(
            this, &ATSTSSSliceEnemyReviewBattleConsole::OnReviewSkillAccepted);
    }
    LastActionText=TEXT("REVIEW STARTED  /  NO REWARDS OR SAVES");
    PresentCurrentWave();
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

bool ATSTSSSliceEnemyReviewBattleConsole::TryStartWavePreview(
    FName WavePreset, ETSTSSSliceReviewPartyStage Stage)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (IsValid(Session.Get()) || WavePreset.IsNone()) return false;
    const FName Before=ReviewWavePreset;
    ReviewWavePreset=WavePreset;
    if (!TryStartPreview(Stage))
    {
        ReviewWavePreset=Before;
        return false;
    }
    return true;
#endif
}

ETSS_CombatPhase ATSTSSSliceEnemyReviewBattleConsole::GetReviewBattlePhase() const
{
#if UE_BUILD_SHIPPING
    return ETSS_CombatPhase::NotStarted;
#else
    return (IsValid(Session.Get()) && IsValid(Session->GetReviewManager()))
        ? Session->GetReviewManager()->GetCurrentPhase()
        : ETSS_CombatPhase::NotStarted;
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::SetVictoryCelebrationActive(
    bool bActive)
{
#if !UE_BUILD_SHIPPING
    bVictoryCelebrating = bActive && IsValid(Session.Get()) &&
        IsValid(Session->GetReviewManager()) &&
        Session->GetReviewManager()->GetCurrentPhase()==ETSS_CombatPhase::Victory;
    VictoryCelebrationTime=0.f;
    const TArray<FName> Members=bVictoryCelebrating
        ? Session->GetReviewActivePartyIds() : TArray<FName>();
    EnderVictoryProxy->SetVisibility(Members.Contains(TEXT("Ender")),true);
    IoniaVictoryProxy->SetVisibility(Members.Contains(TEXT("Ionia")),true);
    LyraVictoryProxy->SetVisibility(Members.Contains(TEXT("Lyra")),true);
    for(UStaticMeshComponent* Marker : {EnderVictoryProxy.Get(),
        IoniaVictoryProxy.Get(),LyraVictoryProxy.Get()})
    {
        const FVector Loc=Marker->GetRelativeLocation();
        Marker->SetRelativeLocation(FVector(Loc.X,Loc.Y,75.f));
        Marker->SetRelativeRotation(FRotator::ZeroRotator);
    }
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::SetReviewHostedByEncounterDirector(
    bool bHosted)
{
#if !UE_BUILD_SHIPPING
    bHostedByEncounterDirector=bHosted;
    RefreshStatus();
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::SetReviewHUDVisible(bool bVisible)
{
#if !UE_BUILD_SHIPPING
    if (IsValid(ReviewHUD.Get()))
    {
        ReviewHUD->SetVisibility(bVisible
            ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    }
#endif
}

bool ATSTSSSliceEnemyReviewBattleConsole::TryChangeReviewWave(int32 Delta)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (IsValid(Session.Get()) || (Delta!=-1 && Delta!=1)) return false;
    int32 Index=INDEX_NONE;
    for (int32 I=0;I<WaveCount;++I)
    {
        if (ReviewWaves[I]==ReviewWavePreset){Index=I;break;}
    }
    if (Index==INDEX_NONE) return false;
    ReviewWavePreset=ReviewWaves[(Index+Delta+WaveCount)%WaveCount];
    LastActionText=TEXT("SELECTED WAVE / PRESS F7, F8 OR F9");
    RefreshStatus();
    return true;
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::ResetReviewArena()
{
#if !UE_BUILD_SHIPPING
    SetVictoryCelebrationActive(false);
    if (IsValid(Session.Get()) && IsValid(Session->GetReviewManager()))
    {
        Session->GetReviewManager()->OnSkillAccepted.RemoveDynamic(
            this, &ATSTSSSliceEnemyReviewBattleConsole::OnReviewSkillAccepted);
    }
    Session=nullptr;
    ActiveEnemyActors.Reset();
    if (GetWorld() && GetWorld()->IsGameWorld())
    {
        for (int32 I=0;I<GalleryActors.Num();++I)
        {
            ATSTSSSliceEnemyActor* Actor=GalleryActors[I];
            if (!IsValid(Actor)) continue;
            if (SavedGalleryTransforms.IsValidIndex(I))
            {
                Actor->SetActorTransform(SavedGalleryTransforms[I]);
            }
            Actor->SetActorHiddenInGame(false);
        }
    }
    LastActionText=TEXT("WAVE RESET / SELECT PARTY TO START");
    RefreshStatus();
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::OnReviewSkillAccepted(
    FName SkillId, FName ActorId, FName TargetId,
    FName VfxCueId, FName AnimationCueId)
{
#if !UE_BUILD_SHIPPING
    LastActionText=FString::Printf(TEXT("%s  USED  %s  ON  %s"),
        *ActorId.ToString(),*SkillId.ToString(),*TargetId.ToString());
    if (IsValid(Session.Get()) && IsValid(Session->GetReviewManager()))
    {
        const TArray<FName> Ids=Session->GetReviewEnemyIds();
        const TArray<FTSTSSCombatant> Snapshot=
            Session->GetReviewManager()->GetCombatantSnapshot();
        for(int32 Slot=0;Slot<2;++Slot)
        {
            if (!Ids.IsValidIndex(Slot) || TargetId!=Ids[Slot] ||
                !ActiveEnemyActors.IsValidIndex(Slot)) continue;
            ATSTSSSliceEnemyActor* Target=ActiveEnemyActors[Slot].Get();
            if (!IsValid(Target)) continue;
            const FTSTSSCombatant* Result=Snapshot.FindByPredicate(
                [TargetId](const FTSTSSCombatant& Unit){
                    return Unit.CharacterId==TargetId;
                });
            Target->PlayReviewHitReaction(Result && Result->Health<=0);
        }
    }
    if (IsValid(ReviewImpactSound.Get()) && GetWorld() &&
        GetWorld()->IsGameWorld())
    {
        UGameplayStatics::PlaySound2D(this, ReviewImpactSound.Get());
    }
    RefreshStatus();
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
void ATSTSSSliceEnemyReviewBattleConsole::SelectPreviousWave()
{
    TryChangeReviewWave(-1);
}
void ATSTSSSliceEnemyReviewBattleConsole::SelectNextWave()
{
    TryChangeReviewWave(1);
}

void ATSTSSSliceEnemyReviewBattleConsole::RefreshStatus()
{
#if !UE_BUILD_SHIPPING
    FString Phase=TEXT("SELECT A PARTY TO BEGIN");
    TArray<FTSTSSCombatant> Snapshot;
    TArray<FName> Enemies;
    if (IsValid(Session.Get()) && IsValid(Session->GetReviewManager()))
    {
        const UTSS_CombatTurnManager* Manager=Session->GetReviewManager();
        const ETSS_CombatPhase Current=Manager->GetCurrentPhase();
        switch(Current)
        {
        case ETSS_CombatPhase::Victory: Phase=TEXT("VICTORY / REVIEW COMPLETE");break;
        case ETSS_CombatPhase::Defeat: Phase=TEXT("DEFEAT / PRESS R TO RETRY");break;
        case ETSS_CombatPhase::Draw: Phase=TEXT("DRAW / PRESS R TO RETRY");break;
        case ETSS_CombatPhase::TurnSelection:
            Phase=FString::Printf(TEXT("CURRENT TURN: %s"),
                                 *Manager->GetActiveParticipantId().ToString());
            break;
        default: Phase=TEXT("RESOLVING REVIEW ACTION");break;
        }
        Snapshot=Manager->GetCombatantSnapshot();
        Enemies=Session->GetReviewEnemyIds();
        if (Current==ETSS_CombatPhase::Victory && LastActionText.Find(
            TEXT("VICTORY"), ESearchCase::IgnoreCase)==INDEX_NONE)
        {
            LastActionText+=TEXT("  /  VICTORY");
            if (IsValid(ReviewVictorySound.Get()) && GetWorld() &&
                GetWorld()->IsGameWorld())
            {
                UGameplayStatics::PlaySound2D(this,ReviewVictorySound.Get());
            }
        }
    }
    if (IsValid(ReviewHUD.Get()))
    {
        ReviewHUD->UpdateReviewHUD(DisplayWave(ReviewWavePreset), Phase,
                                   LastActionText,Snapshot,Enemies,
                                   bHostedByEncounterDirector);
    }
    else if (GEngine && GetWorld() && GetWorld()->IsGameWorld())
    {
        GEngine->AddOnScreenDebugMessage(87654321, 5.f, FColor::Cyan,
            Phase+TEXT("\n")+DisplayWave(ReviewWavePreset)+TEXT("\n")
            +LastActionText);
    }
    StatusAge=0.f;
#endif
}

void ATSTSSSliceEnemyReviewBattleConsole::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    StatusAge+=DeltaSeconds;
    if(bVictoryCelebrating && IsValid(Session.Get()) &&
       IsValid(Session->GetReviewManager()) &&
       Session->GetReviewManager()->GetCurrentPhase()==ETSS_CombatPhase::Victory)
    {
        VictoryCelebrationTime+=FMath::Max(0.f,DeltaSeconds);
        UStaticMeshComponent* Proxies[]={
            EnderVictoryProxy.Get(),IoniaVictoryProxy.Get(),LyraVictoryProxy.Get()};
        for(int32 Index=0;Index<3;++Index)
        {
            UStaticMeshComponent* Marker=Proxies[Index];
            if (!IsValid(Marker) || !Marker->IsVisible()) continue;
            const float T=VictoryCelebrationTime*6.5f+Index*1.7f;
            const float Jump=FMath::Max(0.f,FMath::Sin(T))*42.f;
            const float Cheer=FMath::Sin(T*.6f)*12.f;
            const FVector Loc=Marker->GetRelativeLocation();
            Marker->SetRelativeLocation(FVector(Loc.X,Loc.Y,75.f+Jump));
            Marker->SetRelativeRotation(FRotator(0.f,Cheer,0.f));
        }
    }
    if(StatusAge>=2.0f) RefreshStatus();
#endif
}
