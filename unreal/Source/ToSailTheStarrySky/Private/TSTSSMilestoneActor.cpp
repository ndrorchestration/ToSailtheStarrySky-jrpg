#include "TSTSSMilestoneActor.h"
#include "TSTSSAudioSubsystem.h"
#include "Components/StaticMeshComponent.h"
#if WITH_EDITOR
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#endif
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
#if WITH_EDITOR
    // Cosmetic local review beacon. No collision or shipping UI authority.
    ReviewBeacon = CreateDefaultSubobject<UTextRenderComponent>(TEXT("ReviewBeacon"));
    ReviewBeacon->SetupAttachment(InteractionMesh);
    ReviewBeacon->SetRelativeLocation(FVector(0.f, 0.f, 55.f));
    ReviewBeacon->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));
    ReviewBeacon->SetHorizontalAlignment(EHTA_Center);
    ReviewBeacon->SetWorldSize(40.f);
    ReviewBeacon->SetTextRenderColor(FColor(255, 239, 177));
    ReviewBeacon->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReviewBeacon->SetVisibility(false);
    // Slate backing is visual only; no collisions, shadows, or E ray.
    ReviewBeaconBackdrop = CreateDefaultSubobject<UStaticMeshComponent>(
        TEXT("ReviewBeaconBackdrop"));
    ReviewBeaconBackdrop->SetupAttachment(InteractionMesh);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PanelMesh(
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (PanelMesh.Succeeded())
    {
        ReviewBeaconBackdrop->SetStaticMesh(PanelMesh.Object);
    }
    ReviewBeaconBackdrop->SetRelativeLocation(FVector(8.f, 0.f, 55.f));
    ReviewBeaconBackdrop->SetRelativeScale3D(FVector(.09f, 6.2f, .68f));
    ReviewBeaconBackdrop->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReviewBeaconBackdrop->SetCollisionResponseToAllChannels(ECR_Ignore);
    ReviewBeaconBackdrop->SetGenerateOverlapEvents(false);
    ReviewBeaconBackdrop->SetCastShadow(false);
    ReviewBeaconBackdrop->SetVisibility(false);

    // Distinct authored review props are noncolliding visuals. The original
    // InteractionMesh remains the *only* E trace target and story authority.
    ReviewObjectProxy = CreateDefaultSubobject<UStaticMeshComponent>(
        TEXT("ReviewObjectProxy"));
    ReviewObjectProxy->SetupAttachment(InteractionMesh);
    ReviewObjectProxy->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReviewObjectProxy->SetCollisionResponseToAllChannels(ECR_Ignore);
    ReviewObjectProxy->SetGenerateOverlapEvents(false);
    ReviewObjectProxy->SetVisibility(false);
#endif
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
#if WITH_EDITOR
    if (ReviewBeacon) ReviewBeacon->SetVisibility(false);
    if (ReviewBeaconBackdrop) ReviewBeaconBackdrop->SetVisibility(false);
    if (ReviewObjectProxy) ReviewObjectProxy->SetVisibility(false);
#endif
}

#if WITH_EDITOR
FString ATSTSSMilestoneActor::GetReviewDisplayName() const
{
    if (bIsInspectionStation)
    {
        switch (InspectionStation)
        {
        case ETSTSSInspectionStation::Lift: return TEXT("INSPECT LIFT");
        case ETSTSSInspectionStation::Pressure: return TEXT("CHECK PRESSURE");
        case ETSTSSInspectionStation::Reserve: return TEXT("CHECK RESERVES");
        default: return TEXT("INSPECT SYSTEM");
        }
    }
    switch (Milestone)
    {
    case ETSTSSFirstWakeBeat::FlyerDiscovered: return TEXT("READ IONIA'S FLYER");
    case ETSTSSFirstWakeBeat::IoniaHired: return TEXT("SPEAK TO IONIA");
    case ETSTSSFirstWakeBeat::BoardedAureateWake: return TEXT("BOARD AUREATE WAKE");
    case ETSTSSFirstWakeBeat::EngineeringChecked: return TEXT("ENGINEERING SIGNOFF");
    case ETSTSSFirstWakeBeat::EmptyReserveInspected: return TEXT("CHECK EMPTY RESERVES");
    case ETSTSSFirstWakeBeat::ReturnedToBerth: return TEXT("RETURN TO BERTH");
    default: return TEXT("REVIEW INTERACTION");
    }
}

bool ATSTSSMilestoneActor::IsReviewActionable(const UTSTSSFirstWakeState* State) const
{
    if (!IsValid(State) || !IsAuthorizedReviewMilestoneWorld(GetWorld(), GetActorLabel()) ||
        Milestone == ETSTSSFirstWakeBeat::SeaContact ||
        Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed)
    {
        return false;
    }
    if (bIsInspectionStation)
    {
        const uint8 Index = static_cast<uint8>(InspectionStation);
        return Index <= 2 && State->HasStarted() &&
            State->GetCurrentBeat() == ETSTSSFirstWakeBeat::BoardedAureateWake &&
            (State->GetInspectionMask() & (1u << Index)) == 0;
    }
    if (!State->HasStarted())
    {
        return Milestone == ETSTSSFirstWakeBeat::FlyerDiscovered;
    }
    const int32 Current = static_cast<int32>(State->GetCurrentBeat());
    const int32 Requested = static_cast<int32>(Milestone);
    if (Requested != Current + 1 || Requested >
        static_cast<int32>(ETSTSSFirstWakeBeat::ReturnedToBerth))
    {
        return false;
    }
    if (Milestone == ETSTSSFirstWakeBeat::EngineeringChecked)
    {
        return State->AreInspectionsComplete();
    }
    return true;
}

void ATSTSSMilestoneActor::EnsureV5ReviewObjectProxy()
{
    const UWorld* World = GetWorld();
    if (bReviewProxyInitialized || !IsValid(ReviewObjectProxy) ||
        !IsAuthorizedReviewMilestoneWorld(World, GetActorLabel()) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))
    {
        return;
    }
    bReviewProxyInitialized = true;

    // Canon: review props, not representations of approved cast or ship art.
    // Every named source asset already exists in the integrated MultipathV1
    // object kit. A missing asset leaves the existing old cube untouched.
    const TCHAR* AssetName = nullptr;
    if (bIsInspectionStation)
    {
        switch (InspectionStation)
        {
        case ETSTSSInspectionStation::Lift: AssetName = TEXT("LiftResonator"); break;
        case ETSTSSInspectionStation::Pressure: AssetName = TEXT("PressureRegulator"); break;
        case ETSTSSInspectionStation::Reserve: AssetName = TEXT("ReserveTank"); break;
        default: return;
        }
    }
    else
    {
        switch (Milestone)
        {
        case ETSTSSFirstWakeBeat::FlyerDiscovered: AssetName = TEXT("FlyerPodium"); break;
        case ETSTSSFirstWakeBeat::IoniaHired: AssetName = TEXT("CaptainDesk"); break;
        case ETSTSSFirstWakeBeat::BoardedAureateWake: AssetName = TEXT("GangwayAnchor"); break;
        case ETSTSSFirstWakeBeat::EngineeringChecked: AssetName = TEXT("SignoffPlinth"); break;
        default: return;
        }
    }
    const FString Name(AssetName);
    const FString Path = FString::Printf(
        TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/%s/%s/StaticMeshes/%s.%s"),
        *Name, *Name, *Name, *Name);
    UStaticMesh* Asset = LoadObject<UStaticMesh>(nullptr, *Path);
    if (!IsValid(Asset))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_V5_OBJECT_PROXY_HOLD missing=%s"), *Path);
        return;
    }
    const FBoxSphereBounds Bounds = Asset->GetBounds();
    const FVector Extents = Bounds.BoxExtent;
    if (Extents.ContainsNaN() || Extents.GetMax() <= KINDA_SMALL_NUMBER)
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_V5_OBJECT_PROXY_HOLD invalid_bounds=%s"), *Path);
        return;
    }
    // Scale each real import to a plausible marker footprint, avoiding
    // overlarge mesh collision/visibility changes in the playable corridor.
    constexpr float MaxHalfXY = 80.f;
    constexpr float MaxHalfZ = 108.f;
    const double XY = FMath::Max(Extents.X, Extents.Y);
    const double TargetScale = FMath::Clamp(
        FMath::Min(MaxHalfXY / FMath::Max(XY, 0.01),
                   MaxHalfZ / FMath::Max(Extents.Z, 0.01)), 0.002, 20.);
    if (!FMath::IsFinite(TargetScale)) return;
    ReviewObjectProxy->SetStaticMesh(Asset);
    // Face the more planar flyer/desk set pieces toward the incoming dock
    // player; use true local bounds and rotate the pivot offset as well.
    const bool bFrontFacingReviewProp = !bIsInspectionStation &&
        (Milestone == ETSTSSFirstWakeBeat::FlyerDiscovered ||
         Milestone == ETSTSSFirstWakeBeat::IoniaHired);
    const FQuat ProxyRotation = bFrontFacingReviewProp
        ? FRotator(0.f, 90.f, 0.f).Quaternion()
        : FQuat::Identity;
    ReviewObjectProxy->SetWorldRotation(ProxyRotation);
    ReviewObjectProxy->SetWorldScale3D(FVector(TargetScale));
    const FVector TargetCenter = GetActorLocation() +
        FVector(0.f, 0.f, -65.f + Extents.Z * TargetScale);
    ReviewObjectProxy->SetWorldLocation(
        TargetCenter - ProxyRotation.RotateVector(Bounds.Origin * TargetScale));
    ReviewObjectProxy->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReviewObjectProxy->SetCollisionResponseToAllChannels(ECR_Ignore);
    ReviewObjectProxy->SetGenerateOverlapEvents(false);
    bReviewProxyReady = true;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_V5_OBJECT_PROXY_APPLIED asset=%s collision=disabled original_E_trace_preserved=1"),
        *Name);
}

void ATSTSSMilestoneActor::UpdateReviewBeacon(const UTSTSSFirstWakeState* State)
{
    if (!IsValid(ReviewBeacon) ||
        !IsAuthorizedReviewMilestoneWorld(GetWorld(), GetActorLabel()))
    {
        return;
    }
    const bool bAvailable = IsReviewActionable(State);
    EnsureV5ReviewObjectProxy();
    if (bReviewBeaconInitialized && bReviewBeaconAvailable == bAvailable)
    {
        return;
    }
    bReviewBeaconInitialized = true;
    bReviewBeaconAvailable = bAvailable;
    // Consumed review markers cannot visually occlude later objectives.
    // Cosmetic visibility only: the existing collision/story gates stay intact.
    const bool bConsumed = bIsInspectionStation
        ? (State->HasStarted() &&
           (State->GetInspectionMask() &
            (1u << static_cast<uint8>(InspectionStation))) != 0)
        : (State->HasStarted() &&
           static_cast<uint8>(State->GetCurrentBeat()) >=
           static_cast<uint8>(Milestone));
    if (IsValid(InteractionMesh))
    {
        InteractionMesh->SetVisibility(!bConsumed && !bReviewProxyReady, false);
    }
    if (bReviewProxyReady && IsValid(ReviewObjectProxy))
    {
        ReviewObjectProxy->SetVisibility(!bConsumed, false);
    }
    // Only the currently permitted E marker advertises an E prompt.
    ReviewBeacon->SetVisibility(bAvailable);
    if (IsValid(ReviewBeaconBackdrop))
    {
        ReviewBeaconBackdrop->SetVisibility(bAvailable);
        if (bAvailable)
        {
            if (UMaterialInterface* Slate = LoadObject<UMaterialInterface>(
                nullptr, TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/TSTSS_dark_iron.TSTSS_dark_iron")))
            {
                ReviewBeaconBackdrop->SetMaterial(0, Slate);
            }
        }
    }
    if (bAvailable)
    {
        ReviewBeacon->SetText(FText::FromString(
            FString::Printf(TEXT("[E]  %s"), *GetReviewDisplayName())));
        ReviewBeacon->SetTextRenderColor(FColor(255, 239, 177));
    }

    // Reuse existing local review-material assets; this changes only the
    // rendered material of the additive marker, never collision/story.
    const TCHAR* MaterialPath = bAvailable
        ? TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/TSTSS_brass.TSTSS_brass")
        : TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/TSTSS_dark_iron.TSTSS_dark_iron");
    if (IsValid(InteractionMesh))
    {
        if (UMaterialInterface* Look = LoadObject<UMaterialInterface>(nullptr, MaterialPath))
        {
            InteractionMesh->SetMaterial(0, Look);
        }
    }
}
#endif

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
