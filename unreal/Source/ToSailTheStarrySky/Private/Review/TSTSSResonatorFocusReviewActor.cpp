#include "Review/TSTSSResonatorFocusReviewActor.h"
#include "Review/TSTSSResonatorFocusHUD.h"
#include "TSTSSResonatorVfxActor.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Blueprint/UserWidget.h"
#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "UObject/UObjectGlobals.h"

namespace
{
const FName FocusCenteringSkill(TEXT("Ender_Centering"));
const FName FocusPulseSkill(TEXT("Ender_ResonantPulse"));
const FName IoniaArt(TEXT("Review_FocusIoniaStrike"));
const FName FoeArt(TEXT("Review_FocusFoeStrike"));
const FName FocusOpponentId(TEXT("ReviewFocusFoe"));

FTSS_CombatParticipant Member(FName Id,int32 HP,int32 MP,
                                int32 Attack,int32 Defense,int32 Initiative,
                                bool bPlayer)
{
    FTSS_CombatParticipant Unit;
    Unit.ParticipantId=Id;
    Unit.Stats.CharacterId=Id;
    Unit.Stats.Health=HP;
    Unit.Stats.MaxHealth=HP;
    Unit.Stats.Resource=MP;
    Unit.Stats.MaxResource=MP;
    Unit.Stats.Attack=Attack;
    Unit.Stats.Defense=Defense;
    Unit.Agility=Initiative;
    Unit.bIsPlayerParty=bPlayer;
    return Unit;
}
FTSTSSBattleSkillRow ReviewArt(FName Id,int32 Power)
{
    FTSTSSBattleSkillRow Row;
    Row.SkillId=Id;
    Row.Kind=ETSTSSBattleSkillKind::JobArt;
    Row.Admission=ETSTSSBattleSkillAdmission::ReviewExecutable;
    Row.Target=ETSTSSBattleSkillTarget::Enemy;
    Row.Power=Power;
    return Row;
}
bool AcceptedFocusRow(const FTSTSSBattleSkillRow* Row,FName Id)
{
    if (!Row || Row->SkillId!=Id ||
        Row->Kind!=ETSTSSBattleSkillKind::Spell ||
        Row->Admission!=ETSTSSBattleSkillAdmission::ReviewExecutable ||
        Row->RequiredSchool!=TEXT("ResonanceHarmonic") ||
        Row->RequiredMasteryRank!=1 ||
        !Row->RequiredSecondarySchool.IsNone() ||
        Row->RequiredSecondaryRank!=0) return false;
    if (Id==FocusCenteringSkill)
        return Row->Target==ETSTSSBattleSkillTarget::Self &&
            Row->bPartyPhysicalDefenseBuff &&
            Row->PhysicalDefenseBuffPercent==15 &&
            Row->BuffDurationRounds==3 &&
            Row->ResourceCost==5 && Row->Power==0 &&
            !Row->bHealing && Row->VfxCueId==TEXT("VFX.Ender.Centering");
    if (Id==FocusPulseSkill)
        return Row->Target==ETSTSSBattleSkillTarget::Enemy &&
            !Row->bPartyPhysicalDefenseBuff &&
            Row->PhysicalDefenseBuffPercent==0 &&
            Row->BuffDurationRounds==0 &&
            Row->ResourceCost==3 && Row->Power==6 &&
            !Row->bHealing && Row->VfxCueId==TEXT("VFX.Ender.ResonantPulse");
    return false;
}
}

ATSTSSResonatorFocusReviewActor::ATSTSSResonatorFocusReviewActor()
{
    PrimaryActorTick.bCanEverTick=true;
    bFindCameraComponentWhenViewTarget=true;
    ReviewRoot=CreateDefaultSubobject<USceneComponent>(TEXT("FocusRoot"));
    RootComponent=ReviewRoot;
    ReviewCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("FocusCamera"));
    ReviewCamera->SetupAttachment(ReviewRoot);
    ReviewCamera->SetRelativeLocation(FVector(-780.f,0.f,425.f));
    ReviewCamera->SetRelativeRotation(FRotator(-20.f,0.f,0.f));
    ReviewCamera->SetFieldOfView(68.f);
    Ground=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FocusGround"));
    Ground->SetupAttachment(ReviewRoot);
    Ground->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Ground->SetRelativeLocation(FVector(220.f,-145.f,-75.f));
    Ground->SetRelativeScale3D(FVector(12.f,9.f,.1f));
    EnderProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("EnderReviewProxy"));
    IoniaProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("IoniaReviewProxy"));
    FoeProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FoeReviewProxy"));
    EnderProxy->SetupAttachment(ReviewRoot);
    IoniaProxy->SetupAttachment(ReviewRoot);
    FoeProxy->SetupAttachment(ReviewRoot);
    EnderProxy->SetRelativeLocation(FVector(0.f,-100.f,80.f));
    IoniaProxy->SetRelativeLocation(FVector(0.f,-390.f,80.f));
    FoeProxy->SetRelativeLocation(FVector(500.f,-190.f,80.f));
    EnderProxy->SetRelativeScale3D(FVector(.50f,.50f,1.45f));
    IoniaProxy->SetRelativeScale3D(FVector(.50f,.50f,1.30f));
    FoeProxy->SetRelativeScale3D(FVector(.85f,.75f,1.55f));
    for(UStaticMeshComponent* Part:{EnderProxy.Get(),IoniaProxy.Get(),FoeProxy.Get()})
    {
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Part->SetGenerateOverlapEvents(false);
    }
    Label=CreateDefaultSubobject<UTextRenderComponent>(TEXT("FocusReviewLabel"));
    Label->SetupAttachment(ReviewRoot);
    Label->SetRelativeLocation(FVector(330.f,0.f,240.f));
    Label->SetRelativeRotation(FRotator(0.f,180.f,0.f));
    Label->SetWorldSize(30.f);
    Label->SetText(FText::FromString(TEXT(
        "ENDER / RESONATOR\\n1 CENTERING   2 RESONANT PULSE")));
    Label->SetTextRenderColor(FColor(113,233,195));
    CombatManager=CreateDefaultSubobject<UTSS_CombatTurnManager>(
        TEXT("AuthoritativeReviewCombat"));
    SetActorEnableCollision(false);
}

void ATSTSSResonatorFocusReviewActor::BeginPlay()
{
    Super::BeginPlay();
#if UE_BUILD_SHIPPING
    SetActorTickEnabled(false);
    SetActorHiddenInGame(true);
#else
    if (!bEnableFocusReview || !ActorHasTag(TEXT("TSTSSReviewOnly")) ||
        !GetWorld() || !GetWorld()->IsGameWorld() || !IsValid(CombatManager.Get()))
    {
        SetActorTickEnabled(false);
        SetActorHiddenInGame(true);
        return;
    }
    UStaticMesh* Capsule=LoadObject<UStaticMesh>(nullptr,
        TEXT("/Engine/BasicShapes/Capsule.Capsule"));
    UStaticMesh* Cube=LoadObject<UStaticMesh>(nullptr,
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(Capsule)
    {
        EnderProxy->SetStaticMesh(Capsule);
        IoniaProxy->SetStaticMesh(Capsule);
        FoeProxy->SetStaticMesh(Capsule);
    }
    if(Cube) Ground->SetStaticMesh(Cube);
    IoniaProxy->SetVisibility(bIoniaRecruitedForReview);
    if(!TryInitArena())
    {
        LastReviewEvent=TEXT("FOCUS REVIEW ADMISSION DENIED / NO SPELL GRANTS");
        SetActorTickEnabled(false);
        return;
    }
    CenteringSfx=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/ResonatorFocus/Audio/SFX_Centering.SFX_Centering"));
    PulseSfx=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/ResonatorFocus/Audio/SFX_ResonantPulse.SFX_ResonantPulse"));
    LastReviewEvent=TEXT("READY: CAST CENTERING OR RESONANT PULSE");
    if(APlayerController* PC=UGameplayStatics::GetPlayerController(this,0))
    {
        PC->SetViewTargetWithBlend(this,.35f);
        ReviewHUD=CreateWidget<UTSTSSResonatorFocusHUD>(
            PC,UTSTSSResonatorFocusHUD::StaticClass());
        if(IsValid(ReviewHUD.Get())) ReviewHUD->AddToViewport(150);
        EnableInput(PC);
        InputComponent->BindKey(EKeys::One,IE_Pressed,this,
            &ATSTSSResonatorFocusReviewActor::CastCenteringKey);
        InputComponent->BindKey(EKeys::Two,IE_Pressed,this,
            &ATSTSSResonatorFocusReviewActor::CastPulseKey);
    }
    RefreshHUD();
#endif
}

bool ATSTSSResonatorFocusReviewActor::TryInitArena()
{
#if UE_BUILD_SHIPPING
    return false;
#else
    UDataTable* Source=LoadObject<UDataTable>(nullptr,TEXT(
        "/Game/TSTSS/Review/ResonatorFocus/DT_EnderResonatorFocusReview."
        "DT_EnderResonatorFocusReview"));
    if(!IsValid(Source) || Source->GetRowStruct()!=FTSTSSBattleSkillRow::StaticStruct() ||
       Source->GetRowMap().Num()!=10) return false;
    const FTSTSSBattleSkillRow* C=Source->FindRow<FTSTSSBattleSkillRow>(
        FocusCenteringSkill,TEXT("focus review Centering"),false);
    const FTSTSSBattleSkillRow* P=Source->FindRow<FTSTSSBattleSkillRow>(
        FocusPulseSkill,TEXT("focus review Pulse"),false);
    if(!AcceptedFocusRow(C,FocusCenteringSkill) || !AcceptedFocusRow(P,FocusPulseSkill)) return false;
    // A future contributor cannot enable unapproved Correspondence or other
    // spells merely by adding them to the DataTable.
    for(const auto& Pair:Source->GetRowMap())
    {
        const FName Id=Pair.Key;
        const FTSTSSBattleSkillRow* Row=reinterpret_cast<const FTSTSSBattleSkillRow*>(
            Pair.Value);
        if(Id!=FocusCenteringSkill && Id!=FocusPulseSkill &&
           (!Row || Row->Admission!=ETSTSSBattleSkillAdmission::DesignOnly))
            return false;
    }
    AcceptedReviewTable=NewObject<UDataTable>(this);
    if(!AcceptedReviewTable) return false;
    AcceptedReviewTable->RowStruct=FTSTSSBattleSkillRow::StaticStruct();
    AcceptedReviewTable->AddRow(FocusCenteringSkill,*C);
    AcceptedReviewTable->AddRow(FocusPulseSkill,*P);
    AcceptedReviewTable->AddRow(IoniaArt,ReviewArt(IoniaArt,3));
    AcceptedReviewTable->AddRow(FoeArt,ReviewArt(FoeArt,6));

    FTSS_CombatParticipant E=Member(TEXT("Ender"),60,30,5,3,20,true);
    E.LearnedSkills={FocusCenteringSkill,FocusPulseSkill}; // Only explicit isolated reviewer loadout.
    E.MasteryRanks.Add(TEXT("ResonanceHarmonic"),1);
    FTSS_CombatParticipant I=Member(TEXT("Ionia"),70,0,3,6,10,true);
    I.LearnedSkills={IoniaArt};
    FTSS_CombatParticipant F=Member(FocusOpponentId,145,0,3,1,7,false);
    F.LearnedSkills={FoeArt};
    TArray<FTSS_CombatParticipant> Crew{E};
    TArray<FName> Active{E.ParticipantId};
    if(bIoniaRecruitedForReview)
    {
        Crew.Add(I);
        Active.Add(I.ParticipantId);
    }
    CombatManager->SkillTable=AcceptedReviewTable;
    CombatManager->OnSkillAccepted.AddDynamic(this,
        &ATSTSSResonatorFocusReviewActor::OnAcceptedSkill);
    bReviewReady=CombatManager->InitializeEncounter(Crew,Active,{F});
    return bReviewReady;
#endif
}

bool ATSTSSResonatorFocusReviewActor::TryCast(FName Skill,FName Target)
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if(!bReviewReady || !IsValid(CombatManager.Get()) ||
       CombatManager->GetCurrentPhase()!=ETSS_CombatPhase::TurnSelection ||
       CombatManager->GetActiveParticipantId()!=TEXT("Ender"))
        return false;
    FTSS_CombatCommand Command;
    Command.SourceParticipantId=TEXT("Ender");
    Command.TargetParticipantId=Target;
    Command.SkillId=Skill;
    return CombatManager->SubmitCommand(Command);
#endif
}
bool ATSTSSResonatorFocusReviewActor::TryCastCentering()
{return TryCast(FocusCenteringSkill,TEXT("Ender"));}
bool ATSTSSResonatorFocusReviewActor::TryCastResonantPulse()
{return TryCast(FocusPulseSkill,FocusOpponentId);}
void ATSTSSResonatorFocusReviewActor::CastCenteringKey()
{
    if(!TryCastCentering())
        LastReviewEvent=TEXT("CENTERING DENIED: TURN, MP OR AUTHORIZATION");
    RefreshHUD();
}
void ATSTSSResonatorFocusReviewActor::CastPulseKey()
{
    if(!TryCastResonantPulse())
        LastReviewEvent=TEXT("PULSE DENIED: TURN, MP OR AUTHORIZATION");
    RefreshHUD();
}

void ATSTSSResonatorFocusReviewActor::PlaySound(USoundBase* Cue)
{
#if !UE_BUILD_SHIPPING
    if (IsValid(Cue) && GetWorld() && GetWorld()->IsGameWorld())
        UGameplayStatics::PlaySound2D(this,Cue);
#endif
}

void ATSTSSResonatorFocusReviewActor::OnAcceptedSkill(
    FName SkillId,FName ActorId,FName TargetId,
    FName VfxCueId,FName AnimationCueId)
{
#if !UE_BUILD_SHIPPING
    LastReviewEvent=FString::Printf(TEXT("%s USED %s"),
        *ActorId.ToString(),*SkillId.ToString());
    if(ActorId!=TEXT("Ender") ||
       (SkillId!=FocusCenteringSkill && SkillId!=FocusPulseSkill)) return;
    FTSTSSBattleSkillCue Accepted;
    Accepted.SkillId=SkillId;
    Accepted.ActorId=ActorId;
    Accepted.TargetId=TargetId;
    Accepted.VfxCueId=VfxCueId;
    Accepted.AnimationCueId=AnimationCueId;
    const FVector Origin=EnderProxy->GetComponentLocation();
    const FVector Target=SkillId==FocusCenteringSkill
        ? Origin : FoeProxy->GetComponentLocation();
    if(ATSTSSResonatorVfxActor::IsAcceptedEnderCue(Accepted))
        ATSTSSResonatorVfxActor::SpawnFromAcceptedCue(
            GetWorld(),Accepted,Origin,Target);
    PlaySound(SkillId==FocusCenteringSkill?CenteringSfx.Get():PulseSfx.Get());
    RefreshHUD();
#endif
}

void ATSTSSResonatorFocusReviewActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    if(!bReviewReady || !IsValid(CombatManager.Get()) ||
       !GetWorld() || !GetWorld()->IsGameWorld())return;
    const ETSS_CombatPhase Phase=CombatManager->GetCurrentPhase();
    if(Phase==ETSS_CombatPhase::TurnSelection)
    {
        const FName Actor=CombatManager->GetActiveParticipantId();
        if(Actor!=TEXT("Ender"))
        {
            AutoTurnCountdown-=FMath::Clamp(DeltaSeconds,0.f,.1f);
            if(AutoTurnCountdown<=0.f)
            {
                FTSS_CombatCommand Command;
                Command.SourceParticipantId=Actor;
                if(Actor==TEXT("Ionia"))
                {
                    Command.SkillId=IoniaArt;
                    Command.TargetParticipantId=FocusOpponentId;
                }
                else if(Actor==FocusOpponentId)
                {
                    Command.SkillId=FoeArt;
                    Command.TargetParticipantId=bIoniaRecruitedForReview
                        ? FName(TEXT("Ionia")) : FName(TEXT("Ender"));
                    // Never target an already incapacitated party member.
                    for(const FTSTSSCombatant& Unit:CombatManager->GetCombatantSnapshot())
                    {
                        if(Unit.CharacterId==Command.TargetParticipantId &&
                           Unit.Health<=0)
                            Command.TargetParticipantId=TEXT("Ender");
                    }
                }
                if(!Command.SkillId.IsNone())
                {
                    if(!CombatManager->SubmitCommand(Command))
                    {
                        LastReviewEvent=TEXT("REVIEW AI ACTION DENIED: NO SKIP");
                        bReviewReady=false;
                    }
                }
                AutoTurnCountdown=.75f;
            }
        }
        else AutoTurnCountdown=.75f;
    }
    UiRefreshCountdown+=DeltaSeconds;
    if(UiRefreshCountdown>=.2f)
    {
        UiRefreshCountdown=0.f;
        RefreshHUD();
    }
#endif
}
void ATSTSSResonatorFocusReviewActor::RefreshHUD()
{
#if !UE_BUILD_SHIPPING
    if(!IsValid(ReviewHUD.Get()) || !IsValid(CombatManager.Get()))return;
    FString Units;
    const int32 Round=CombatManager->GetCurrentRound();
    for(const FTSTSSCombatant& Unit:CombatManager->GetCombatantSnapshot())
    {
        const int32 Remaining=CombatManager->GetCenteringRoundsRemaining(
            Unit.CharacterId);
        Units+=FString::Printf(TEXT("%s   HP %d/%d   MP %d/%d\n"
             "     Physical DEF %d%s\n"),
            *Unit.CharacterId.ToString(),Unit.Health,Unit.MaxHealth,
            Unit.Resource,Unit.MaxResource,
            CombatManager->GetCenteringEffectiveDefense(Unit.CharacterId),
            Remaining>0?*FString::Printf(TEXT("  / CENTERING %d ROUND(S)"),Remaining)
                :TEXT(""));
    }
    const ETSS_CombatPhase Phase=CombatManager->GetCurrentPhase();
    const FString State=Phase==ETSS_CombatPhase::Victory
        ? TEXT("VICTORY / RESTART REVIEW FOR ANOTHER BATTLE")
        : Phase==ETSS_CombatPhase::Defeat
        ? TEXT("DEFEAT / RESTART REVIEW")
        : FString::Printf(TEXT("ROUND %d / ACTIVE: %s"),
            Round,*CombatManager->GetActiveParticipantId().ToString());
    ReviewHUD->SetReviewState(
        TEXT("ENDER / RESONATOR / TWO SPELLS / REVIEW ONLY"),
        State+TEXT("\n")+Units,LastReviewEvent,
        TEXT("1  CENTERING: 5 MP, +15% PHYSICAL DEF, 3 ROUNDS\n"
             "2  RESONANT PULSE: 3 MP, SINGLE ENEMY\n"
             "Ionia / enemy turns automated; NO CAMPAIGN SAVE"));
#endif
}
