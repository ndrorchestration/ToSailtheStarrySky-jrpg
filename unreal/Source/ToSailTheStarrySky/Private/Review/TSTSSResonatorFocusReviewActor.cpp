#include "Review/TSTSSResonatorFocusReviewActor.h"
#include "Review/TSTSSResonatorFocusHUD.h"
#include "Combat/TSTSSPulseAreaMath.h"
#include "TSTSSResonatorVfxActor.h"
#include "Camera/CameraComponent.h"
#include "Components/PointLightComponent.h"
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
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Sound/SoundBase.h"
#include "UObject/UObjectGlobals.h"

namespace
{
const FName FocusCenteringSkill(TEXT("Ender_Centering"));
const FName FocusPulseSkill(TEXT("Ender_ResonantPulse"));
const FName IoniaArt(TEXT("Review_FocusIoniaStrike"));
const FName FoeArt(TEXT("Review_FocusFoeStrike"));
const FName FocusOpponentId(TEXT("ReviewFocusFoe"));
const FName FocusOpponentHighId(TEXT("ReviewFocusFoeElevated"));
const FName FocusOpponentOutsideId(TEXT("ReviewFocusFoeOutside"));

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
    // The original empty review map had no direct lights. These opt-in,
    // collision-free lights make the GREYBOX battlefield visible without
    // making any artistic or canonical material claim.
    ArenaKeyLight=CreateDefaultSubobject<UPointLightComponent>(
        TEXT("FocusWarmKeyLight"));
    ArenaKeyLight->SetupAttachment(ReviewRoot);
    ArenaKeyLight->SetRelativeLocation(FVector(180.f,-200.f,440.f));
    ArenaKeyLight->SetIntensity(30000.f);
    ArenaKeyLight->SetAttenuationRadius(2000.f);
    ArenaKeyLight->SetLightColor(FLinearColor(1.f,.81f,.59f));
    ArenaKeyLight->SetCastShadows(false);
    ArenaFillLight=CreateDefaultSubobject<UPointLightComponent>(
        TEXT("FocusTealFillLight"));
    ArenaFillLight->SetupAttachment(ReviewRoot);
    ArenaFillLight->SetRelativeLocation(FVector(430.f,100.f,340.f));
    ArenaFillLight->SetIntensity(18000.f);
    ArenaFillLight->SetAttenuationRadius(1700.f);
    ArenaFillLight->SetLightColor(FLinearColor(.25f,.81f,1.f));
    ArenaFillLight->SetCastShadows(false);
    EnderProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("EnderReviewProxy"));
    IoniaProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("IoniaReviewProxy"));
    FoeProxy=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FoeReviewProxy"));
    FoeHighProxy=CreateDefaultSubobject<UStaticMeshComponent>(
        TEXT("FoeElevatedReviewProxy"));
    FoeOutsideProxy=CreateDefaultSubobject<UStaticMeshComponent>(
        TEXT("FoeOutsideReviewProxy"));
    EnderProxy->SetupAttachment(ReviewRoot);
    IoniaProxy->SetupAttachment(ReviewRoot);
    FoeProxy->SetupAttachment(ReviewRoot);
    FoeHighProxy->SetupAttachment(ReviewRoot);
    FoeOutsideProxy->SetupAttachment(ReviewRoot);
    EnderProxy->SetRelativeLocation(FVector(0.f,-100.f,80.f));
    IoniaProxy->SetRelativeLocation(FVector(0.f,-390.f,80.f));
    FoeProxy->SetRelativeLocation(FVector(500.f,-190.f,80.f));
    // Opt-in review proof: elevated foe is 391 cm from Ender in true 3D,
    // outside foe 724 cm away. Relative positions are revalidated at runtime.
    FoeHighProxy->SetRelativeLocation(FVector(200.f,100.f,350.f));
    FoeOutsideProxy->SetRelativeLocation(FVector(680.f,-100.f,330.f));
    EnderProxy->SetRelativeScale3D(FVector(.50f,.50f,1.45f));
    IoniaProxy->SetRelativeScale3D(FVector(.50f,.50f,1.30f));
    FoeProxy->SetRelativeScale3D(FVector(.85f,.75f,1.55f));
    FoeHighProxy->SetRelativeScale3D(FVector(.70f,.70f,1.0f));
    FoeOutsideProxy->SetRelativeScale3D(FVector(.70f,.70f,1.0f));
    for(UStaticMeshComponent* Part:{
        EnderProxy.Get(),IoniaProxy.Get(),FoeProxy.Get(),
        FoeHighProxy.Get(),FoeOutsideProxy.Get()})
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
        UE_LOG(LogTemp,Warning,TEXT("TSTSS_FOCUS_BEGINPLAY_DENIED: optin/tag/world/manager missing"));
        SetActorTickEnabled(false);
        SetActorHiddenInGame(true);
        return;
    }
#if WITH_EDITOR
    // Native review convenience: an explicit launcher argument can opt in to
    // the three-foe proof in the original immutable V2 map. Never resave a
    // canonical asset or allow this flag outside the exact isolated review map.
    // Mandatory actor opt-in/tag/game-world checks above still apply.
    if (FParse::Param(FCommandLine::Get(), TEXT("TSTSSFocusMultiProbe")))
    {
        const FString MapName=GetWorld()->GetMapName();
        if (!MapName.EndsWith(TEXT("L_EnderCenteringPulseReview_V2")))
        {
            UE_LOG(LogTemp,Error,
                TEXT("TSTSS_FOCUS_MULTIFOE_CLI_DENIED: wrong review map"));
            SetActorTickEnabled(false);
            SetActorHiddenInGame(true);
            return;
        }
        bMultiEnemyPulseProofReview=true;
        UE_LOG(LogTemp,Display,
            TEXT("TSTSS_FOCUS_MULTIFOE_CLI_OPTIN: V2 map review only"));
    }
#endif
    // Capsule does not exist at /Engine/BasicShapes/Capsule.Capsule on this
    // exact Windows UE5.8.4 installation. Use a verified Engine Cube for all
    // visible provisional proxies until approved sculpt/rig assets are ready.
    UStaticMesh* Cube=LoadObject<UStaticMesh>(nullptr,
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    if(!Cube)
    {
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_BEGINPLAY_DENIED: Engine Cube mesh missing"));
        SetActorTickEnabled(false);
        return;
    }
    Ground->SetStaticMesh(Cube);
    EnderProxy->SetStaticMesh(Cube);
    IoniaProxy->SetStaticMesh(Cube);
    FoeProxy->SetStaticMesh(Cube);
    FoeHighProxy->SetStaticMesh(Cube);
    FoeOutsideProxy->SetStaticMesh(Cube);
    FoeHighProxy->SetVisibility(bMultiEnemyPulseProofReview);
    FoeOutsideProxy->SetVisibility(bMultiEnemyPulseProofReview);
    IoniaProxy->SetVisibility(bIoniaRecruitedForReview);
    if(!TryInitArena())
    {
        LastReviewEvent=TEXT("FOCUS REVIEW ADMISSION DENIED / NO SPELL GRANTS");
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_BEGINPLAY_DENIED: skill/party admission"));
        SetActorTickEnabled(false);
        return;
    }
    CenteringSfx=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/ResonatorFocus/Audio/SFX_Centering.SFX_Centering"));
    PulseSfx=LoadObject<USoundBase>(nullptr,
        TEXT("/Game/TSTSS/Review/ResonatorFocus/Audio/SFX_ResonantPulse.SFX_ResonantPulse"));
    LastReviewEvent=TEXT("READY: CAST CENTERING OR RESONANT PULSE");
    UE_LOG(LogTemp,Display,
        TEXT("TSTSS_FOCUS_COMBAT_ADMITTED: two spells; foes=%d multi_probe=%d"),
        bMultiEnemyPulseProofReview ? 3 : 1,
        bMultiEnemyPulseProofReview ? 1 : 0);
    TryAttachReviewPlayer();
    RefreshHUD();
#endif
}

void ATSTSSResonatorFocusReviewActor::TryAttachReviewPlayer()
{
#if !UE_BUILD_SHIPPING
    if(!bReviewReady || bInputBound || !GetWorld() || !GetWorld()->IsGameWorld())
        return;
    APlayerController* PC=UGameplayStatics::GetPlayerController(this,0);
    if(!PC) return; // BeginPlay may occur before the first local controller.
    if(!IsValid(ReviewHUD.Get()))
    {
        ReviewHUD=CreateWidget<UTSTSSResonatorFocusHUD>(
            PC,UTSTSSResonatorFocusHUD::StaticClass());
        if(!IsValid(ReviewHUD.Get()))
        {
            UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_UI_DENIED: UMG widget creation failed"));
            return;
        }
        ReviewHUD->AddToViewport(150);
    }
    EnableInput(PC);
    if(!InputComponent)
    {
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_UI_DENIED: actor input component missing"));
        return;
    }
    InputComponent->BindKey(EKeys::One,IE_Pressed,this,
        &ATSTSSResonatorFocusReviewActor::CastCenteringKey);
    InputComponent->BindKey(EKeys::Two,IE_Pressed,this,
        &ATSTSSResonatorFocusReviewActor::CastPulseKey);
    PC->SetViewTargetWithBlend(this,.35f);
    bInputBound=true;
    UE_LOG(LogTemp,Display,TEXT("TSTSS_FOCUS_INPUT_AND_HUD_BOUND: keys 1 and 2"));
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
    if(!IsValid(Source))
    {
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_INIT_DENIED: native spell table missing"));
        return false;
    }
    if(Source->GetRowStruct()!=FTSTSSBattleSkillRow::StaticStruct() ||
       Source->GetRowMap().Num()!=10)
    {
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_INIT_DENIED: spell table struct/row count mismatch"));
        return false;
    }
    const FTSTSSBattleSkillRow* C=Source->FindRow<FTSTSSBattleSkillRow>(
        FocusCenteringSkill,TEXT("focus review Centering"),false);
    const FTSTSSBattleSkillRow* P=Source->FindRow<FTSTSSBattleSkillRow>(
        FocusPulseSkill,TEXT("focus review Pulse"),false);
    if(!AcceptedFocusRow(C,FocusCenteringSkill) || !AcceptedFocusRow(P,FocusPulseSkill))
    {
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_INIT_DENIED: Centering/Pulse row contract mismatch"));
        return false;
    }
    // A future contributor cannot enable unapproved Correspondence or other
    // spells merely by adding them to the DataTable.
    for(const auto& Pair:Source->GetRowMap())
    {
        const FName Id=Pair.Key;
        const FTSTSSBattleSkillRow* Row=reinterpret_cast<const FTSTSSBattleSkillRow*>(
            Pair.Value);
        if(Id!=FocusCenteringSkill && Id!=FocusPulseSkill &&
           (!Row || Row->Admission!=ETSTSSBattleSkillAdmission::DesignOnly))
        {
            UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_INIT_DENIED: unselected spell executable"));
            return false;
        }
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
    TArray<FTSS_CombatParticipant> Foes{F};
    if (bMultiEnemyPulseProofReview)
    {
        // A bounded reviewer fixture, not a story encounter. Require Ionia
        // as the in-radius ally and the same positional authority as Pulse.
        if (!bIoniaRecruitedForReview || !IsValid(EnderProxy.Get()) ||
            !IsValid(IoniaProxy.Get()) || !IsValid(FoeHighProxy.Get()) ||
            !IsValid(FoeOutsideProxy.Get()))
            return false;
        const FVector Caster = EnderProxy->GetComponentLocation();
        const auto Inside = [&Caster](const FVector& Point)
        {
            return TSTSSPulseAreaMath::WithinSphere(
                Caster.X, Caster.Y, Caster.Z,
                Point.X, Point.Y, Point.Z,
                FTSTSSBattleSkillSystem::ResonantPulseRadiusCm);
        };
        if (!Inside(FoeProxy->GetComponentLocation()) ||
            !Inside(FoeHighProxy->GetComponentLocation()) ||
             Inside(FoeOutsideProxy->GetComponentLocation()) ||
            !Inside(IoniaProxy->GetComponentLocation()))
        {
            UE_LOG(LogTemp,Error,
                TEXT("TSTSS_FOCUS_MULTIFOE_HOLD: 600cm 3D geometry/ally mismatch"));
            return false;
        }
        FTSS_CombatParticipant Elevated=Member(
            FocusOpponentHighId,115,0,2,1,6,false);
        FTSS_CombatParticipant Outside=Member(
            FocusOpponentOutsideId,115,0,2,1,5,false);
        Elevated.LearnedSkills={FoeArt};
        Outside.LearnedSkills={FoeArt};
        Foes.Add(Elevated);
        Foes.Add(Outside);
    }
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
    bReviewReady=CombatManager->InitializeEncounter(Crew,Active,Foes);
    if(!bReviewReady)
        UE_LOG(LogTemp,Error,TEXT("TSTSS_FOCUS_INIT_DENIED: combat manager rejected roster"));
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
{
#if UE_BUILD_SHIPPING
    return false;
#else
    if (!bReviewReady || !IsValid(CombatManager.Get()) ||
        !IsValid(EnderProxy.Get()) || !IsValid(FoeProxy.Get()) ||
        CombatManager->GetCurrentPhase() != ETSS_CombatPhase::TurnSelection ||
        CombatManager->GetActiveParticipantId() != TEXT("Ender"))
        return false;

    // Actual PIE component world positions, not an enemy selected by a
    // UI or a forged narrative trigger. Every active combatant must have
    // an owned proxy; otherwise the spatial cast is denied before MP spend.
    TMap<FName, FVector> Positions;
    for (const FTSTSSCombatant& Unit : CombatManager->GetCombatantSnapshot())
    {
        if (Unit.CharacterId == TEXT("Ender"))
            Positions.Add(Unit.CharacterId, EnderProxy->GetComponentLocation());
        else if (Unit.CharacterId == TEXT("Ionia") &&
                 bIoniaRecruitedForReview && IsValid(IoniaProxy.Get()))
            Positions.Add(Unit.CharacterId, IoniaProxy->GetComponentLocation());
        else if (Unit.CharacterId == FocusOpponentId)
            Positions.Add(Unit.CharacterId, FoeProxy->GetComponentLocation());
        else if (bMultiEnemyPulseProofReview &&
                 Unit.CharacterId == FocusOpponentHighId &&
                 IsValid(FoeHighProxy.Get()))
            Positions.Add(Unit.CharacterId, FoeHighProxy->GetComponentLocation());
        else if (bMultiEnemyPulseProofReview &&
                 Unit.CharacterId == FocusOpponentOutsideId &&
                 IsValid(FoeOutsideProxy.Get()))
            Positions.Add(Unit.CharacterId, FoeOutsideProxy->GetComponentLocation());
        else
            return false;
    }
    FTSS_CombatCommand Command;
    Command.SourceParticipantId = TEXT("Ender");
    Command.TargetParticipantId = TEXT("Ender");  // caster-centered sphere
    Command.SkillId = FocusPulseSkill;
    // A read-only, nonshipping evidence point for the optional 3-foe
    // review fixture. The manager remains the sole damage/MP authority.
    // Record one before/after pair after the synchronous atomic action;
    // do not infer native acceptance or player-key provenance from logs.
    const bool bProof = bMultiEnemyPulseProofReview;
    const TArray<FTSTSSCombatant> Before = bProof
        ? CombatManager->GetCombatantSnapshot()
        : TArray<FTSTSSCombatant>();
    const bool bAccepted = CombatManager->SubmitResonantPulseArea(Command, Positions);
    if (bProof)
    {
        if (!bAccepted)
        {
            UE_LOG(LogTemp,Warning,TEXT("TSTSS_FOCUS_MULTIFOE_READBACK_DENIED"));
        }
        else
        {
            const TArray<FTSTSSCombatant> After =
                CombatManager->GetCombatantSnapshot();
            const auto Find = [](const TArray<FTSTSSCombatant>& Roster,
                                 FName Id) -> const FTSTSSCombatant*
            {
                for (const FTSTSSCombatant& Unit : Roster)
                    if (Unit.CharacterId == Id) return &Unit;
                return nullptr;
            };
            const FTSTSSCombatant* BE = Find(Before,TEXT("Ender"));
            const FTSTSSCombatant* AE = Find(After,TEXT("Ender"));
            const FTSTSSCombatant* BP = Find(Before,FocusOpponentId);
            const FTSTSSCombatant* AP = Find(After,FocusOpponentId);
            const FTSTSSCombatant* BH = Find(Before,FocusOpponentHighId);
            const FTSTSSCombatant* AH = Find(After,FocusOpponentHighId);
            const FTSTSSCombatant* BO = Find(Before,FocusOpponentOutsideId);
            const FTSTSSCombatant* AO = Find(After,FocusOpponentOutsideId);
            const FTSTSSCombatant* BI = Find(Before,TEXT("Ionia"));
            const FTSTSSCombatant* AI = Find(After,TEXT("Ionia"));
            if (!BE || !AE || !BP || !AP || !BH || !AH ||
                !BO || !AO || !BI || !AI)
            {
                UE_LOG(LogTemp,Warning,
                    TEXT("TSTSS_FOCUS_MULTIFOE_READBACK_INCOMPLETE"));
            }
            else
            {
                UE_LOG(LogTemp,Display,
                    TEXT("TSTSS_FOCUS_MULTIFOE_READBACK mp_spent=%d primary_hp_delta=%d elevated_hp_delta=%d outside_hp_delta=%d ionia_hp_delta=%d"),
                    BE->Resource-AE->Resource,
                    BP->Health-AP->Health,
                    BH->Health-AH->Health,
                    BO->Health-AO->Health,
                    BI->Health-AI->Health);
            }
        }
    }
    return bAccepted;
#endif
}
void ATSTSSResonatorFocusReviewActor::CastCenteringKey()
{
    if(!TryCastCentering())
        LastReviewEvent=TEXT("CENTERING DENIED: TURN, MP OR AUTHORIZATION");
    RefreshHUD();
}
void ATSTSSResonatorFocusReviewActor::CastPulseKey()
{
#if !UE_BUILD_SHIPPING
    // This reports the bound input-handler path, not physical keyboard provenance.
    // Keep it review-only and off for the default single-foe sandbox.
    if (bMultiEnemyPulseProofReview && bInputBound)
        UE_LOG(LogTemp,Display,
            TEXT("TSTSS_FOCUS_PULSE_KEY_CALLBACK: bound key 2 handler invoked"));
#endif
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
    UE_LOG(LogTemp,Display,TEXT("TSTSS_FOCUS_ACTION_ACCEPTED actor=%s skill=%s target=%s"),
        *ActorId.ToString(),*SkillId.ToString(),*TargetId.ToString());
    if(ActorId!=TEXT("Ender") ||
       (SkillId!=FocusCenteringSkill && SkillId!=FocusPulseSkill)) return;
    FTSTSSBattleSkillCue Accepted;
    Accepted.SkillId=SkillId;
    Accepted.ActorId=ActorId;
    Accepted.TargetId=TargetId;
    Accepted.VfxCueId=VfxCueId;
    Accepted.AnimationCueId=AnimationCueId;
    const FVector Origin=EnderProxy->GetComponentLocation();
    // Both accepted effects originate at Ender: Pulse now expands in
    // full 3D around the caster and never chases a chosen enemy.
    const FVector Target = Origin;
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
    if(!bInputBound) TryAttachReviewPlayer();
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
                else if(Actor==FocusOpponentId ||
                    (bMultiEnemyPulseProofReview &&
                     (Actor==FocusOpponentHighId || Actor==FocusOpponentOutsideId)))
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
    const FString FoeMode = bMultiEnemyPulseProofReview
        ? TEXT("THREE REVIEW FOES: TWO INSIDE (ONE ELEVATED), ONE OUTSIDE")
        : TEXT("ONE REVIEW FOE");
    ReviewHUD->SetReviewState(
        TEXT("ENDER / RESONATOR / TWO SPELLS / REVIEW ONLY"),
        State+TEXT("\n")+Units,LastReviewEvent,
        FString(TEXT("1  CENTERING: 5 MP, +15% PARTY PHYSICAL DEF, 3 ROUNDS\n"
                     "2  RESONANT PULSE: 3 MP, 600 CM ENEMY-ONLY 3D AOE\n"))+
        FoeMode+TEXT("; Ionia / enemy turns automated; NO CAMPAIGN SAVE"));
#endif
}
