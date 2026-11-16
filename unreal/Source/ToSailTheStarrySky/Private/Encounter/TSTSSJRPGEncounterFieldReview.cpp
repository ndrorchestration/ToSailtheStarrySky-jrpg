#include "Encounter/TSTSSJRPGEncounterFieldReview.h"
#include "Enemies/TSTSSSliceEnemyReviewBattleConsole.h"
#include "Encounter/TSTSSJRPGReviewPresentation.h"
#include "Encounter/TSTSSJRPGReviewSequenceHUD.h"
#include "Sound/SoundBase.h"
#include "Blueprint/UserWidget.h"
#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/InputComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UObjectGlobals.h"

namespace
{
    constexpr float WalkSpeedCmPerSecond=350.f;
    constexpr float SafeZoneRadiusCm=650.f;

    FString BiomeTitle(ETSTSSJRPGEncounterBiome Biome)
    {
        switch(Biome)
        {
        case ETSTSSJRPGEncounterBiome::HarborOutskirts: return TEXT("HARBOR OUTSKIRTS");
        case ETSTSSJRPGEncounterBiome::Woodland: return TEXT("WOODLAND");
        case ETSTSSJRPGEncounterBiome::Coast: return TEXT("COAST");
        case ETSTSSJRPGEncounterBiome::Highlands: return TEXT("HIGHLANDS");
        default: return TEXT("UNAUTHORIZED");
        }
    }

    FName ScriptedPreviewPreset(ETSTSSJRPGEncounterBiome Biome)
    {
        switch(Biome)
        {
        case ETSTSSJRPGEncounterBiome::HarborOutskirts:
            return TEXT("Review_HarborBanditCaptain");
        case ETSTSSJRPGEncounterBiome::Woodland:
            return TEXT("Review_WoodlandSentinel");
        case ETSTSSJRPGEncounterBiome::Coast:
            return TEXT("Review_CoastalShellbacks");
        case ETSTSSJRPGEncounterBiome::Highlands:
            return TEXT("Review_HighlandBristle");
        default:
            return NAME_None;
        }
    }
}

ATSTSSJRPGEncounterFieldReview::ATSTSSJRPGEncounterFieldReview()
{
    PrimaryActorTick.bCanEverTick=true;
    ReviewRoot=CreateDefaultSubobject<USceneComponent>(TEXT("FieldRoot"));
    SetRootComponent(ReviewRoot);
    ExplorerCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("FieldCamera"));
    ExplorerCamera->SetupAttachment(ReviewRoot);
    ExplorerCamera->SetRelativeLocation(FVector(-660.f,0.f,410.f));
    ExplorerCamera->SetRelativeRotation(FRotator(-21.f,0.f,0.f));
    ExplorerCamera->SetFieldOfView(74.f);
    ExplorerShape=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ReviewWalkMarker"));
    ExplorerShape->SetupAttachment(ReviewRoot);
    ExplorerShape->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ExplorerShape->SetGenerateOverlapEvents(false);
    ExplorerShape->SetRelativeScale3D(FVector(.40f,.40f,1.35f));
    ExplorerShape->SetRelativeLocation(FVector(0.f,0.f,65.f));
    ExplorerMarker=CreateDefaultSubobject<UTextRenderComponent>(TEXT("FieldReviewInstructions"));
    ExplorerMarker->SetupAttachment(ReviewRoot);
    ExplorerMarker->SetRelativeLocation(FVector(0.f,0.f,230.f));
    ExplorerMarker->SetRelativeRotation(FRotator(0.f,180.f,0.f));
    ExplorerMarker->SetWorldSize(19.f);
    ExplorerMarker->SetText(FText::FromString(TEXT("RANDOM ENCOUNTER REVIEW\nWASD explore")));
    Director=CreateDefaultSubobject<UTSTSSJRPGEncounterDirector>(
        TEXT("JRPGEncounterDirector"));
    SetActorEnableCollision(false);
}

void ATSTSSJRPGEncounterFieldReview::BeginPlay()
{
    Super::BeginPlay();
#if UE_BUILD_SHIPPING
    SetActorHiddenInGame(true);
    SetActorTickEnabled(false);
#else
    if (!bEnableReviewTraversal || !ActorHasTag(TEXT("TSTSSReviewOnly")) ||
        !GetWorld() || !GetWorld()->IsGameWorld())
    {
        SetActorHiddenInGame(true);
        SetActorTickEnabled(false);
        return;
    }
    UStaticMesh* Shape=LoadObject<UStaticMesh>(
        nullptr,TEXT("/Engine/BasicShapes/Capsule.Capsule"));
    if (!Shape)
    {
        Shape=LoadObject<UStaticMesh>(
            nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    }
    if (Shape) ExplorerShape->SetStaticMesh(Shape);

    int32 ConsoleCount=0;
    for (TActorIterator<ATSTSSSliceEnemyReviewBattleConsole> It(GetWorld());It;++It)
    {
        BattleConsole=*It;
        ++ConsoleCount;
    }
    if (ConsoleCount!=1 || !IsValid(BattleConsole.Get()) ||
        !IsValid(Director.Get()) ||
        !Director->TryConfigureReviewBiome(InitialBiome,11292026))
    {
        SetActorTickEnabled(false);
        return;
    }
    Biome=InitialBiome;
    SafeZoneOrigin=GetActorLocation();

    Presentation=NewObject<UTSTSSJRPGReviewPresentation>(this);
    RewardLedger=NewObject<UTSTSSJRPGReviewRewards>(this);
    if (!IsValid(Presentation.Get()) || !IsValid(RewardLedger.Get()))
    {
        SetActorTickEnabled(false);
        return;
    }
    EncounterSting=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/Audio/SFX_EncounterSting.SFX_EncounterSting"));
    VictoryFanfare=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/Audio/SFX_VictoryFanfare.SFX_VictoryFanfare"));
    RewardReveal=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/Audio/SFX_RewardReveal.SFX_RewardReveal"));
    ReturnWhoosh=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/Audio/SFX_ReturnWhoosh.SFX_ReturnWhoosh"));
    bReviewReady=true;
    BattleConsole->SetReviewHostedByEncounterDirector(true);
    LastEncounterMessage=TEXT("REVIEW ACTIVE / WALK OUT OF CAMP TO FIND FOES");
    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        SequenceHUD=CreateWidget<UTSTSSJRPGReviewSequenceHUD>(
            PC, UTSTSSJRPGReviewSequenceHUD::StaticClass());
        if (IsValid(SequenceHUD.Get()))
        {
            SequenceHUD->AddToViewport(150);
        }
        EnableInput(PC);
        InputComponent->BindKey(EKeys::W,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::PressForward);
        InputComponent->BindKey(EKeys::W,IE_Released,this,
            &ATSTSSJRPGEncounterFieldReview::ReleaseForward);
        InputComponent->BindKey(EKeys::S,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::PressBack);
        InputComponent->BindKey(EKeys::S,IE_Released,this,
            &ATSTSSJRPGEncounterFieldReview::ReleaseBack);
        InputComponent->BindKey(EKeys::A,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::PressLeft);
        InputComponent->BindKey(EKeys::A,IE_Released,this,
            &ATSTSSJRPGEncounterFieldReview::ReleaseLeft);
        InputComponent->BindKey(EKeys::D,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::PressRight);
        InputComponent->BindKey(EKeys::D,IE_Released,this,
            &ATSTSSJRPGEncounterFieldReview::ReleaseRight);
        InputComponent->BindKey(EKeys::One,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::ChooseEnder);
        InputComponent->BindKey(EKeys::Two,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::ChooseIonia);
        InputComponent->BindKey(EKeys::Three,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::ChooseLyra);
        InputComponent->BindKey(EKeys::P,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::CycleRate);
        InputComponent->BindKey(EKeys::V,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::CycleBiome);
        InputComponent->BindKey(EKeys::F2,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::TriggerScripted);

        InputComponent->BindKey(EKeys::Enter,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::ReturnAfterBattle);
        InputComponent->BindKey(EKeys::J,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::StrikePreviewEnemyOne);
        InputComponent->BindKey(EKeys::K,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::StrikePreviewEnemyTwo);
        InputComponent->BindKey(EKeys::Escape,IE_Pressed,this,
            &ATSTSSJRPGEncounterFieldReview::FleeReviewBattle);
    }
    RefreshFieldMarker();
    RefreshSequenceHUD();
#endif
}

FTSTSSJRPGEncounterContext
ATSTSSJRPGEncounterFieldReview::MakeWalkingContext() const
{
    FTSTSSJRPGEncounterContext Context;
    Context.bTraversalActive=bReviewReady && !bInBattle;
    Context.bAreaAuthorized=bReviewReady;
    Context.bPartyAuthorized=bReviewReady;
    Context.bSafeZone=FVector::Dist2D(GetActorLocation(),SafeZoneOrigin)
        <=SafeZoneRadiusCm;
    Context.bBattleActive=bInBattle;
    Context.Rate=EncounterRate;
    return Context;
}

void ATSTSSJRPGEncounterFieldReview::EnterReviewCamera()
{
#if !UE_BUILD_SHIPPING
    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        PC->SetViewTargetWithBlend(this,.6f);
        if (IsValid(BattleConsole.Get()))
        {
            BattleConsole->SetReviewHUDVisible(false);
            BattleConsole->DisableInput(PC);
        }
    }
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TrySetReviewBiome(
    ETSTSSJRPGEncounterBiome Next)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || bInBattle || !Director->TryConfigureReviewBiome(
        Next,11292026+static_cast<int32>(Next))) return false;
    Biome=Next;
    LastEncounterMessage=TEXT("REVIEW BIOME SELECTED / NO STORY PLACEMENT");
    RefreshFieldMarker();
    return true;
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TrySetReviewPartyStage(
    ETSTSSSliceReviewPartyStage Next)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || bInBattle ||
        static_cast<uint8>(Next)>static_cast<uint8>(
            ETSTSSSliceReviewPartyStage::AfterSplashdown)) return false;
    PartyStage=Next;
    RefreshFieldMarker();
    return true;
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TrySetReviewRate(
    ETSTSSJRPGEncounterRate Next)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || bInBattle ||
        static_cast<uint8>(Next)>static_cast<uint8>(
            ETSTSSJRPGEncounterRate::Increased)) return false;
    EncounterRate=Next;
    RefreshFieldMarker();
    return true;
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TryHandoffToBattle(
    const FTSTSSJRPGEncounterTicket& Ticket)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || bInBattle || !IsValid(BattleConsole.Get()) ||
        !IsValid(Presentation.Get()) || !IsValid(RewardLedger.Get()) ||
        Ticket.Serial<=0 || !Ticket.bReviewOnly) return false;
    if (!Presentation->TryBegin(Ticket.Serial))
    {
        Director->TryCancelPending(Ticket.Serial);
        return false;
    }
    // Stage 1: flash and encounter sting while the camera is still in the
    // world. Battle initialization and camera transfer occur after the fade.
    ActiveTicketSerial=Ticket.Serial;
    PendingWave=Ticket.ReviewWavePreset;
    LastReward=FTSTSSJRPGReviewReward();
    bRewardAwarded=false;
    bRetreated=false;
    bInBattle=true;
    bOutcomeReady=false;
    LastEncounterMessage=FString::Printf(TEXT("%s  /  %s"),
        Ticket.bScripted ? TEXT("SCRIPTED REVIEW") : TEXT("RANDOM REVIEW"),
        *Ticket.ReviewWavePreset.ToString());
    PlayReviewSound(EncounterSting.Get());
    RefreshSequenceHUD();
    return true;
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TryRequestExplicitScriptedWave()
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || bInBattle) return false;
    FTSTSSJRPGEncounterContext Context=MakeWalkingContext();
    Context.bScriptedEncounterApproved=true; // only an explicit reviewer command
    FTSTSSJRPGEncounterTicket Ticket;
    if (!Director->TryRequestScripted(
        ScriptedPreviewPreset(Biome),Context,Ticket)) return false;
    return TryHandoffToBattle(Ticket);
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TryRetreatReviewBattle()
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || !bInBattle || bOutcomeReady ||
        ActiveTicketSerial<=0 || !IsValid(BattleConsole.Get()) ||
        !IsValid(Director.Get()) || !IsValid(Presentation.Get()) ||
        Presentation->GetPhase()!=ETSTSSJRPGReviewSequencePhase::Combat ||
        BattleConsole->GetReviewBattlePhase()!=ETSS_CombatPhase::TurnSelection)
        return false;
    if (!Presentation->TryFlee(ActiveTicketSerial)) return false;
    // No loot, gold or XP. The outstanding ticket completes only after
    // the return-screen fade, to prevent another encounter mid-transition.
    bRetreated=true;
    LastEncounterMessage=TEXT("FLEEING / NO REWARDS");
    PlayReviewSound(ReturnWhoosh.Get());
    RefreshSequenceHUD();
    return true;
#endif
}

bool ATSTSSJRPGEncounterFieldReview::TryReturnToExploration()
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || !bInBattle || !bOutcomeReady ||
        ActiveTicketSerial<=0 || !IsValid(BattleConsole.Get()) ||
        !IsValid(Presentation.Get())) return false;
    const ETSS_CombatPhase Result=BattleConsole->GetReviewBattlePhase();
    if (Result!=ETSS_CombatPhase::Victory &&
        Result!=ETSS_CombatPhase::Defeat &&
        Result!=ETSS_CombatPhase::Draw) return false;
    if (!Presentation->TryDismissResult(ActiveTicketSerial)) return false;
    // Do not complete the encounter ticket until the out-transition finishes.
    PlayReviewSound(ReturnWhoosh.Get());
    RefreshSequenceHUD();
    return true;
#endif
}

void ATSTSSJRPGEncounterFieldReview::PlayReviewSound(USoundBase* Sound)
{
#if !UE_BUILD_SHIPPING
    if (IsValid(Sound) && GetWorld() && GetWorld()->IsGameWorld())
        UGameplayStatics::PlaySound2D(this,Sound);
#endif
}

void ATSTSSJRPGEncounterFieldReview::RefreshSequenceHUD()
{
#if !UE_BUILD_SHIPPING
    if (IsValid(SequenceHUD.Get()) && IsValid(Presentation.Get()))
    {
        SequenceHUD->UpdatePresentation(Presentation->GetPhase(),
            Presentation->GetPhaseProgress(),LastReward,bRewardAwarded,
            IsValid(RewardLedger.Get())?RewardLedger->GetGoldBalance():0);
    }
#endif
}

void ATSTSSJRPGEncounterFieldReview::FinishReturnToField()
{
#if !UE_BUILD_SHIPPING
    if (ActiveTicketSerial<=0 || !IsValid(Presentation.Get()) ||
        Presentation->GetPhase()!=ETSTSSJRPGReviewSequencePhase::ReturnReady ||
        !IsValid(Director.Get()) || !IsValid(BattleConsole.Get())) return;
    const ETSS_CombatPhase Battle=BattleConsole->GetReviewBattlePhase();
    const bool bVictorious=!bRetreated && Battle==ETSS_CombatPhase::Victory;
    if (!Director->TryCompleteBattle(ActiveTicketSerial)) return;
    if (!Presentation->TryFinishReturn(ActiveTicketSerial)) return;
    BattleConsole->SetVictoryCelebrationActive(false);
    BattleConsole->ResetReviewArena();
    if (!bVictorious && !bRetreated)
        SetActorLocation(SafeZoneOrigin);
    SetActorHiddenInGame(false);
    LastEncounterMessage=bRetreated
        ? TEXT("FLED / NO REWARD / EXPLORATION RESUMED")
        : bVictorious
        ? TEXT("VICTORY / GOLD, XP AND ITEMS ADDED TO REVIEW LEDGER")
        : TEXT("DEFEAT / RETURNED TO SAFE CAMP / NO REWARDS");
    ActiveTicketSerial=0;
    PendingWave=NAME_None;
    bInBattle=false;
    bOutcomeReady=false;
    bRetreated=false;
    EnterReviewCamera();
    RefreshSequenceHUD();
    RefreshFieldMarker();
#endif
}

void ATSTSSJRPGEncounterFieldReview::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    if (!bReviewReady || !IsValid(BattleConsole.Get()) ||
        !GetWorld() || !GetWorld()->IsGameWorld()) return;

    if (bInBattle)
    {
        if (!IsValid(Presentation.Get()) || !IsValid(Director.Get()) ||
            !IsValid(RewardLedger.Get())) return;
        const ETSTSSJRPGReviewSequencePhase Before=Presentation->GetPhase();
        Presentation->Advance(FMath::Clamp(DeltaSeconds,0.f,.2f));
        ETSTSSJRPGReviewSequencePhase Now=Presentation->GetPhase();

        // Stage 2: show the visual transition BEFORE entering battle.
        if (Now==ETSTSSJRPGReviewSequencePhase::BattleReveal &&
            Presentation->IsAwaitingBattleStart())
        {
            if (!BattleConsole->TryStartWavePreview(PendingWave,PartyStage) ||
                !Director->TryAcknowledgeBattleStart(ActiveTicketSerial))
            {
                BattleConsole->ResetReviewArena();
                Presentation->TryAbortBeforeCombat(ActiveTicketSerial);
                Director->TryCancelPending(ActiveTicketSerial);
                ActiveTicketSerial=0;
                PendingWave=NAME_None;
                bInBattle=false;
                LastEncounterMessage=TEXT("ENCOUNTER ADMISSION FAILED / RETURNED TO FIELD");
                EnterReviewCamera();
                RefreshSequenceHUD();
                return;
            }
            // The director is the authoritative owner of the encounter ticket.
            if (!Presentation->TryEnterCombat(ActiveTicketSerial)) return;
            SetActorHiddenInGame(true);
            if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
            {
                BattleConsole->DisableInput(PC);
                BattleConsole->SetReviewHUDVisible(true);
                PC->SetViewTargetWithBlend(BattleConsole.Get(),.42f);
            }
            Now=Presentation->GetPhase();
        }

        // Stage 3: real turn manager resolves combat, not the presentation.
        if (Now==ETSTSSJRPGReviewSequencePhase::Combat)
        {
            const ETSS_CombatPhase Battle=BattleConsole->GetReviewBattlePhase();
            if (Battle==ETSS_CombatPhase::Victory &&
                Presentation->TryResolveVictory(ActiveTicketSerial))
            {
                bOutcomeReady=true;
                // Stage 4: once-only, in-memory gold/loot/XP transaction
                // granted only AFTER the authoritative victory phase.
                FTSTSSJRPGReviewReward Earned;
                bRewardAwarded=RewardLedger->TryAwardOnce(
                    ActiveTicketSerial,PendingWave,
                    BattleConsole->GetReviewActivePartyIds(),Earned);
                if (bRewardAwarded) LastReward=Earned;
                BattleConsole->SetVictoryCelebrationActive(true);
                PlayReviewSound(VictoryFanfare.Get());
                LastEncounterMessage=bRewardAwarded
                    ? TEXT("VICTORY / FANFARE / CELEBRATION / REWARDS")
                    : TEXT("VICTORY / REVIEW REWARD ADMISSION DENIED");
            }
            else if ((Battle==ETSS_CombatPhase::Defeat ||
                      Battle==ETSS_CombatPhase::Draw) &&
                     Presentation->TryResolveDefeat(ActiveTicketSerial))
            {
                bOutcomeReady=true;
                LastEncounterMessage=TEXT("DEFEAT / NO REWARDS");
            }
        }
        Now=Presentation->GetPhase();
        if (Now==ETSTSSJRPGReviewSequencePhase::Rewards &&
            Before!=ETSTSSJRPGReviewSequencePhase::Rewards)
        {
            BattleConsole->SetVictoryCelebrationActive(false);
            PlayReviewSound(RewardReveal.Get());
        }
        if (Now==ETSTSSJRPGReviewSequencePhase::ReturnReady)
        {
            FinishReturnToField();
            return;
        }
        RefreshSequenceHUD();
        return;
    }

    if (APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        if (PC->GetViewTarget()!=this) EnterReviewCamera();
    }
    // Review sandbox intentionally bounded and collision-free. The actual
    // production movement component will supply validated physical travel.
    FVector Direction((bForward?1.f:0.f)-(bBack?1.f:0.f),
                      (bRight?1.f:0.f)-(bLeft?1.f:0.f),0.f);
    if (!Direction.IsNearlyZero() && FMath::IsFinite(DeltaSeconds) &&
        DeltaSeconds>0.f && DeltaSeconds<=.2f)
    {
        const FVector Delta=Direction.GetSafeNormal() *
            WalkSpeedCmPerSecond*DeltaSeconds;
        const FVector Location=GetActorLocation();
        FVector Next=Location+Delta;
        Next.X=FMath::Clamp(Next.X,SafeZoneOrigin.X-350.f,
                            SafeZoneOrigin.X+5300.f);
        Next.Y=FMath::Clamp(Next.Y,SafeZoneOrigin.Y-1500.f,
                            SafeZoneOrigin.Y+1500.f);
        const float RealDistance=FVector::Dist2D(Location,Next);
        if (RealDistance>0.f)
        {
            SetActorLocation(Next,false);
            FTSTSSJRPGEncounterTicket Ticket;
            if (Director->TryRecordWalking(RealDistance,MakeWalkingContext(),
                                           Ticket))
            {
                TryHandoffToBattle(Ticket);
            }
        }
    }

    MarkerRefreshTimer+=DeltaSeconds;
    if(MarkerRefreshTimer>=.4f)RefreshFieldMarker();
#endif
}

void ATSTSSJRPGEncounterFieldReview::RefreshFieldMarker()
{
#if !UE_BUILD_SHIPPING
    MarkerRefreshTimer=0.f;
    if (!IsValid(ExplorerMarker.Get()) || !IsValid(Director.Get())) return;
    const bool bSafe=FVector::Dist2D(GetActorLocation(),SafeZoneOrigin)
        <=SafeZoneRadiusCm;
    const FString Stage=PartyStage==ETSTSSSliceReviewPartyStage::EnderOnly
        ? TEXT("ENDER") : PartyStage==ETSTSSSliceReviewPartyStage::IoniaRecruited
        ? TEXT("ENDER + IONIA") : TEXT("ENDER + IONIA + LYRA");
    const FString Title=FString::Printf(
        TEXT("HYBRID JRPG ENCOUNTERS / REVIEW ONLY\n"
             "WASD WALK  1/2/3 PARTY STAGE  V BIOME  P ENCOUNTER RATE\n"
             "F2 SCRIPTED REVIEW CHALLENGE  ESC FLEE / ENTER RETURN\n"
             "BIOME: %s   STAGE: %s   RATE: %d   %s\n"
             "DISTANCE: %.0f cm   %s"),
        *BiomeTitle(Biome),*Stage,static_cast<int32>(EncounterRate),
        bSafe?TEXT("SAFE CAMP"):TEXT("FIELD / RANDOM"),
        Director->GetWalkingDistanceSinceBattleCm(),*LastEncounterMessage);
    ExplorerMarker->SetText(FText::FromString(Title));
    if (GEngine && GetWorld() && GetWorld()->IsGameWorld() && !bInBattle)
    {
        GEngine->AddOnScreenDebugMessage(8191901, .6f, FColor::Cyan, Title);
    }
#endif
}

void ATSTSSJRPGEncounterFieldReview::PressForward(){bForward=true;}
void ATSTSSJRPGEncounterFieldReview::ReleaseForward(){bForward=false;}
void ATSTSSJRPGEncounterFieldReview::PressBack(){bBack=true;}
void ATSTSSJRPGEncounterFieldReview::ReleaseBack(){bBack=false;}
void ATSTSSJRPGEncounterFieldReview::PressLeft(){bLeft=true;}
void ATSTSSJRPGEncounterFieldReview::ReleaseLeft(){bLeft=false;}
void ATSTSSJRPGEncounterFieldReview::PressRight(){bRight=true;}
void ATSTSSJRPGEncounterFieldReview::ReleaseRight(){bRight=false;}

void ATSTSSJRPGEncounterFieldReview::ChooseEnder()
{
    TrySetReviewPartyStage(ETSTSSSliceReviewPartyStage::EnderOnly);
}
void ATSTSSJRPGEncounterFieldReview::ChooseIonia()
{
    TrySetReviewPartyStage(ETSTSSSliceReviewPartyStage::IoniaRecruited);
}
void ATSTSSJRPGEncounterFieldReview::ChooseLyra()
{
    TrySetReviewPartyStage(ETSTSSSliceReviewPartyStage::AfterSplashdown);
}
void ATSTSSJRPGEncounterFieldReview::CycleRate()
{
    TrySetReviewRate(static_cast<ETSTSSJRPGEncounterRate>(
        (static_cast<uint8>(EncounterRate)+1)%4));
}
void ATSTSSJRPGEncounterFieldReview::CycleBiome()
{
    TrySetReviewBiome(static_cast<ETSTSSJRPGEncounterBiome>(
        (static_cast<uint8>(Biome)+1)%4));
}
void ATSTSSJRPGEncounterFieldReview::TriggerScripted()
{
    TryRequestExplicitScriptedWave();
}
void ATSTSSJRPGEncounterFieldReview::ReturnAfterBattle()
{
    TryReturnToExploration();
}
void ATSTSSJRPGEncounterFieldReview::StrikePreviewEnemyOne()
{
    if (bInBattle && IsValid(BattleConsole.Get()) &&
        IsValid(Presentation.Get()) &&
        Presentation->GetPhase()==ETSTSSJRPGReviewSequencePhase::Combat)
        BattleConsole->TryStrikePreview(0);
}
void ATSTSSJRPGEncounterFieldReview::StrikePreviewEnemyTwo()
{
    if (bInBattle && IsValid(BattleConsole.Get()) &&
        IsValid(Presentation.Get()) &&
        Presentation->GetPhase()==ETSTSSJRPGReviewSequencePhase::Combat)
        BattleConsole->TryStrikePreview(1);
}
void ATSTSSJRPGEncounterFieldReview::FleeReviewBattle()
{
    TryRetreatReviewBattle();
}
