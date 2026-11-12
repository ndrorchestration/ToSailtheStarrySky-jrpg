#include "TSTSSV5HarborReviewDressing.h"

#if WITH_EDITOR
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"

namespace
{
constexpr const TCHAR* DressingLabel = TEXT("TSTSS_V5_REVIEW_HARBOR_DRESSING");
constexpr int32 BoardColumns = 70;
constexpr int32 BoardRows = 5;
// Original V5 floor extends X=-3750..2550 and Y=-700..700.
// All new art is intentionally noncolliding. The existing floor alone
// remains authoritative for walkability and fall-recovery support.
bool IsEligibleReview(UWorld* World)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))
    {
        return false;
    }
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (It->GetActorLabel() == DressingLabel)
        {
            return false; // No duplicate dressing during reload or BeginPlay.
        }
    }
    return true;
}

UInstancedStaticMeshComponent* MakeVisualComponent(
    AActor* Owner, USceneComponent* Root, const TCHAR* ComponentName,
    UStaticMesh* Mesh, UMaterialInterface* Material)
{
    UInstancedStaticMeshComponent* Component =
        NewObject<UInstancedStaticMeshComponent>(Owner, ComponentName);
    Component->SetMobility(EComponentMobility::Movable);
    Component->SetupAttachment(Root);
    Component->SetStaticMesh(Mesh);
    Component->SetMaterial(0, Material);
    Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Component->SetCollisionResponseToAllChannels(ECR_Ignore);
    Component->SetGenerateOverlapEvents(false);
    Owner->AddInstanceComponent(Component);
    Component->RegisterComponent();
    return Component;
}

void AddBox(UInstancedStaticMeshComponent* Component,
            float X, float Y, float Z, float SX, float SY, float SZ,
            float Roll = 0.f)
{
    // Engine BasicShapes/Cube measures 100 cm at unit scale.
    Component->AddInstance(FTransform(
        FRotator(0.f, 0.f, Roll),
        FVector(X, Y, Z), FVector(SX, SY, SZ)));
}

void AddCylinder(UInstancedStaticMeshComponent* Component,
                 float X, float Y, float Z, float SX, float SY, float SZ)
{
    Component->AddInstance(FTransform(
        FRotator::ZeroRotator, FVector(X, Y, Z), FVector(SX, SY, SZ)));
}
}

namespace TSTSSV5HarborReviewDressing
{
bool Apply(UWorld* World, UMaterialInterface* Timber,
           UMaterialInterface* Stone, UMaterialInterface* Brass,
           UMaterialInterface* Aether)
{
    if (!IsEligibleReview(World) || !IsValid(Timber) || !IsValid(Stone) ||
        !IsValid(Brass) || !IsValid(Aether))
    {
        return false;
    }
    UStaticMesh* Cube = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Cylinder = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    if (!IsValid(Cube) || !IsValid(Cylinder))
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_V5_DRESSING_HOLD missing BasicShapes"));
        return false;
    }
    AActor* Owner = World->SpawnActor<AActor>(
        AActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
    if (!IsValid(Owner))
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_V5_DRESSING_HOLD actor_spawn"));
        return false;
    }
    Owner->SetActorLabel(DressingLabel);
    Owner->SetActorEnableCollision(false);
    USceneComponent* Root = NewObject<USceneComponent>(Owner, TEXT("ReviewVisualRoot"));
    Owner->AddInstanceComponent(Root);
    Owner->SetRootComponent(Root);
    Root->SetMobility(EComponentMobility::Movable);
    Root->RegisterComponent();

    auto* Boards = MakeVisualComponent(
        Owner, Root, TEXT("DockDeckTimber"), Cube, Timber);
    auto* Quay = MakeVisualComponent(
        Owner, Root, TEXT("QuayStoneEdges"), Cube, Stone);
    auto* Rails = MakeVisualComponent(
        Owner, Root, TEXT("MooringBrassAndRails"), Cube, Brass);
    auto* Posts = MakeVisualComponent(
        Owner, Root, TEXT("MooringWoodAndCrates"), Cube, Timber);
    auto* Round = MakeVisualComponent(
        Owner, Root, TEXT("BollardsAndBarrels"), Cylinder, Stone);
    auto* Canvas = MakeVisualComponent(
        Owner, Root, TEXT("MerchantAwnings"), Cube, Aether);

    // 350 individual 62 cm transverse planks, five long deck lanes.
    // Repeated seam and stagger silhouettes remain readable when texture
    // mips flatten at medium distance; the original collision floor is
    // unchanged. Decorative top is +0.9 cm above original Z=0 walkway.
    int32 DeckPlanks = 0;
    for (int32 Column = 0; Column < BoardColumns; ++Column)
    {
        for (int32 Lane = 0; Lane < BoardRows; ++Lane)
        {
            const float X = -3000.f + 65.f * Column +
                ((Lane & 1) ? 27.f : 0.f);
            const float Y = -370.f + 185.f * Lane;
            AddBox(Boards, X, Y, -3.0f, .625f, 1.78f, .078f);
            ++DeckPlanks;
        }
    }

    // Broken-out dock perimeter and safety-readable contrast lines,
    // deliberately outside the player interaction corridor |Y| <= 370.
    for (int32 Segment = 0; Segment < 9; ++Segment)
    {
        const float X = -2750.f + 500.f * Segment;
        for (const float Side : {-1.f, 1.f})
        {
            AddBox(Quay, X, Side * 525.f, -6.f, 4.9f, .21f, .19f);
        }
    }

    int32 RailPosts = 0;
    for (int32 Step = 0; Step < 9; ++Step)
    {
        const float X = -2760.f + Step * 495.f;
        for (const float Side : {-1.f, 1.f})
        {
            // A clear gap in the seaward rail near the gangway: decorative
            // access intent only, not a newly authorized playable dock exit.
            if (Side > 0.f && X > -1600.f && X < -550.f)
            {
                continue;
            }
            AddBox(Posts, X, Side * 545.f, 70.f, .24f, .24f, 1.5f);
            AddBox(Rails, X, Side * 545.f, 151.f, .37f, .37f, .17f);
            ++RailPosts;
        }
    }
    for (int32 Segment = 0; Segment < 8; ++Segment)
    {
        const float X = -2515.f + Segment * 495.f;
        for (const float Side : {-1.f, 1.f})
        {
            if (Side > 0.f && X > -1600.f && X < -550.f)
            {
                continue;
            }
            AddBox(Rails, X, Side * 545.f, 153.f, 4.95f, .12f, .13f);
        }
    }

    // Mooring hardware, cargo, and pitched rooflines. None is interactive
    // and none may occlude the existing seven E visibility-trace markers
    // (all on central Y=0). Their collision stays entirely disabled.
    int32 Props = 0;
    for (const float X : {-2580.f, -1220.f, 640.f})
    {
        AddCylinder(Round, X, 607.f, 39.f, .47f, .47f, .78f);
        AddCylinder(Round, X, -607.f, 39.f, .47f, .47f, .78f);
        Props += 2;
    }
    for (const float X : {-2520.f, -1500.f, -350.f, 1060.f})
    {
        AddBox(Posts, X, -602.f, 52.f, .83f, .80f, 1.02f);
        AddBox(Rails, X, -602.f, 103.f, .88f, .10f, .075f);
        Props += 2;
    }
    for (const float X : {-2090.f, -480.f, 1060.f})
    {
        AddCylinder(Round, X, 608.f, 43.f, .43f, .43f, .86f);
        Props += 1;
    }

    // Storehouse volume exists in the original V5 review map at
    // (-3200, 650, 350), size (500 x 400 x 700 cm). This dressing is
    // additional roofline, lintel, door, and frame rather than a new building.
    AddBox(Quay, -3200.f, 650.f, 695.f, 5.5f, 4.3f, .21f);
    AddBox(Posts, -3200.f, 540.f, 744.f, 5.45f, 2.25f, .19f, -15.f);
    AddBox(Posts, -3200.f, 760.f, 744.f, 5.45f, 2.25f, .19f, 15.f);
    AddBox(Quay, -2941.f, 650.f, 152.f, .12f, 1.36f, 2.88f);
    AddBox(Posts, -2930.f, 650.f, 143.f, .11f, 1.13f, 2.64f);
    AddBox(Rails, -2920.f, 693.f, 142.f, .11f, .09f, .10f);
    Props += 6;

    // Three readable market stalls on the inland edge of the walkway.
    for (const float X : {-1840.f, -300.f, 1020.f})
    {
        for (const float Offset : {-105.f, 105.f})
        {
            AddBox(Posts, X + Offset, -635.f, 105.f,
                   .15f, .15f, 2.1f);
        }
        AddBox(Canvas, X, -635.f, 222.f, 2.75f, 1.60f, .085f, 8.f);
        AddBox(Posts, X, -650.f, 40.f, 2.25f, .85f, .8f);
        Props += 4;
    }

    // Three warm harbor practicals at visual-side locations. They are not
    // gameplay objectives, not story triggers and carry no collision.
    int32 PracticalLights = 0;
    for (int32 Index = 0; Index < 3; ++Index)
    {
        const float X = -2420.f + 1610.f * Index;
        AddBox(Posts, X, -530.f, 122.f, .15f, .15f, 2.5f);
        AddBox(Rails, X, -530.f, 257.f, .34f, .34f, .13f);
        UPointLightComponent* Light = NewObject<UPointLightComponent>(
            Owner, *FString::Printf(TEXT("ReviewLantern_%d"), Index));
        Light->SetMobility(EComponentMobility::Movable);
        Light->SetupAttachment(Root);
        Light->SetRelativeLocation(FVector(X, -530.f, 245.f));
        Light->SetLightColor(FLinearColor(1.f, .70f, .45f));
        Light->SetIntensity(700.f);
        Light->SetAttenuationRadius(560.f);
        Light->SetCastShadows(false);
        Light->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Owner->AddInstanceComponent(Light);
        Light->RegisterComponent();
        ++PracticalLights;
    }

    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_V5_DRESSING_APPLIED deck_planks=%d rail_posts=%d props=%d lights=%d collision=disabled source_map_unchanged=1"),
        DeckPlanks, RailPosts, Props, PracticalLights);
    return true;
}
}
#endif
