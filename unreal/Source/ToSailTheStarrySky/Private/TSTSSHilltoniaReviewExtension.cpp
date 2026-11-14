#include "TSTSSHilltoniaReviewExtension.h"

#if WITH_EDITOR
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"

namespace
{
constexpr const TCHAR* TownLabel = TEXT("TSTSS_V5_REVIEW_HILLTONIA_TOWN");
constexpr const TCHAR* V5Map = TEXT("FirstWake_PreludeInteraction_V5_VisualReview");
// Coordinates are centimeters in the existing harbor local frame.
// Seaward is +Y; landward and the wooded slopes are -Y. The dock
// collision floor is X=-3750..2550 and Y=-700..700 at Z=0.
// The new westward road joins that floor, without touching the seven
// story-marker traces from X=-2200..1175 and Y=0.
constexpr float RoadFirstX = -3650.f;
constexpr float RoadLastX = -9050.f;
constexpr float RoadStep = 600.f;
constexpr float RoadCenterY = -150.f;

bool Eligible(UWorld* World)
{
    if (!World ||
        (World->WorldType != EWorldType::PIE &&
         World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != V5Map)
    {
        return false;
    }
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (It->GetActorLabel() == TownLabel) return false;
    }
    return true;
}

UInstancedStaticMeshComponent* Make(
    AActor* Owner, USceneComponent* Root, const TCHAR* Name,
    UStaticMesh* Mesh, UMaterialInterface* Material, bool bSolid)
{
    auto* Component = NewObject<UInstancedStaticMeshComponent>(Owner, Name);
    Component->SetMobility(EComponentMobility::Movable);
    Component->SetupAttachment(Root);
    Component->SetStaticMesh(Mesh);
    Component->SetMaterial(0, Material);
    // Only the new landward walkways and village building shells/trunks
    // are collidable. The original seven E traces retain all authority.
    Component->SetCollisionEnabled(
        bSolid ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    Component->SetCollisionResponseToAllChannels(bSolid ? ECR_Block : ECR_Ignore);
    Component->SetCollisionObjectType(bSolid ? ECC_WorldStatic : ECC_WorldDynamic);
    Component->SetGenerateOverlapEvents(false);
    Owner->AddInstanceComponent(Component);
    Component->RegisterComponent();
    return Component;
}

void Place(UInstancedStaticMeshComponent* Component,
           float X, float Y, float Z, float SX, float SY, float SZ,
           float Yaw = 0.f, float Roll = 0.f)
{
    Component->AddInstance(FTransform(
        FRotator(0.f, Yaw, Roll), FVector(X, Y, Z),
        FVector(SX, SY, SZ)));
}

void WayfindingSign(AActor* Owner, USceneComponent* Root,
                    const TCHAR* ComponentName, const TCHAR* Caption,
                    const FVector& Location, float Yaw)
{
    // Fixed local-to-map sign, deliberately NO collision or interaction.
    // Wayfinding must never become a gameplay/quest milestone.
    auto* Text = NewObject<UTextRenderComponent>(Owner, ComponentName);
    Text->SetMobility(EComponentMobility::Movable);
    Text->SetupAttachment(Root);
    Text->SetText(FText::FromString(Caption));
    Text->SetWorldSize(62.f);
    Text->SetTextRenderColor(FColor(233, 220, 172));
    Text->SetRelativeLocation(Location);
    Text->SetRelativeRotation(FRotator(0.f, Yaw, 0.f));
    Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Owner->AddInstanceComponent(Text);
    Text->RegisterComponent();
}

void TownSigns(AActor* Owner, USceneComponent* Root)
{
    // Main arrival is visible from the original dock end, off the walkable
    // street. The three following signboards are on the verge, not on-road.
    WayfindingSign(Owner, Root, TEXT("HilltoniaLandwardEntrySign"),
        TEXT("HILLTONIA  |  WOODLAND ROAD"),
        FVector(-4290.f, -690.f, 340.f), 0.f);
    WayfindingSign(Owner, Root, TEXT("HilltoniaWoodlandTurnoffSign"),
        TEXT("HILLTONIA  |  FOREST TRAIL"),
        FVector(-7070.f, -690.f, 330.f), 0.f);
    WayfindingSign(Owner, Root, TEXT("HilltoniaForestEdgeReturnSign"),
        TEXT("FOREST EDGE  |  RETURN TO HILLTONIA"),
        FVector(-7000.f, -2940.f, 325.f), 90.f);
    WayfindingSign(Owner, Root, TEXT("HilltoniaTownWestReturnSign"),
        TEXT("TOWN END  |  RETURN TO HARBOR"),
        FVector(-8750.f, -680.f, 315.f), 0.f);
}
}

namespace TSTSSHilltoniaReviewExtension
{
bool Apply(UWorld* World, UMaterialInterface* Timber,
           UMaterialInterface* Stone, UMaterialInterface* Brass,
           UMaterialInterface* Canopy)
{
    if (!Eligible(World) || !IsValid(Timber) || !IsValid(Stone) ||
        !IsValid(Brass) || !IsValid(Canopy)) return false;

    UStaticMesh* Cube = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Cylinder = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    UStaticMesh* Sphere = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (!IsValid(Cube) || !IsValid(Cylinder) || !IsValid(Sphere))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_HILLTONIA_HOLD missing primitive mesh; no town applied"));
        return false;
    }
    AActor* Owner = World->SpawnActor<AActor>(
        AActor::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
    if (!IsValid(Owner)) return false;
    Owner->SetActorLabel(TownLabel);
    Owner->SetActorEnableCollision(true);
    auto* Root = NewObject<USceneComponent>(Owner, TEXT("HilltoniaVisualRoot"));
    Owner->AddInstanceComponent(Root);
    Owner->SetRootComponent(Root);
    Root->SetMobility(EComponentMobility::Movable);
    Root->RegisterComponent();

    auto* Ground = Make(Owner, Root, TEXT("HilltoniaLandwardGround"),
                        Cube, Canopy, true);
    auto* Road = Make(Owner, Root, TEXT("HilltoniaWorldStaticFootpath"),
                      Cube, Stone, true);
    auto* Buildings = Make(Owner, Root, TEXT("HilltoniaSolidTimberHouses"),
                           Cube, Timber, true);
    auto* Roofs = Make(Owner, Root, TEXT("HilltoniaPitchedRoofs"),
                       Cube, Brass, false);
    auto* Trim = Make(Owner, Root, TEXT("HilltoniaTownGreenAndDetail"),
                      Cube, Timber, false);
    auto* TreeTrunks = Make(Owner, Root, TEXT("HilltoniaWoodlandTrunks"),
                            Cylinder, Timber, true);
    auto* TreeCrowns = Make(Owner, Root, TEXT("HilltoniaDeciduousCanopies"),
                            Sphere, Canopy, false);
    auto* RollingHills = Make(Owner, Root, TEXT("HilltoniaWoodedSlopeBackdrop"),
                              Sphere, Canopy, false);

    // Actual land mass, not houses hovering over the original ocean plane.
    // Grass/soil surface is Z=-10cm, ten centimeters below the road top.
    // The first 250cm meets the old dock edge without overlapping any
    // First Wake E marker. The water remains exposed to the seaward (+Y)
    // side. This is flat, playable prototype ground, NOT a final Landscape.
    Place(Ground, -7000.f, -1300.f, -90.f, 70.f, 58.f, 1.6f);
    // A second contiguous forest foothill shelf extends the landward
    // ground beneath the tree line, without making scenic ridges solid.
    Place(Ground, -7350.f, -4950.f, -140.f, 63.f, 20.f, 2.6f);

    // Dock-to-town road: 10 overlapping 620-cm ground sections, full top
    // surface at Z=0. Its first 310 cm overlap the original dock floor,
    // while all town collision begins safely west of the first E marker.
    int32 RoadSegments = 0;
    for (float X = RoadFirstX; X >= RoadLastX; X -= RoadStep)
    {
        Place(Road, X, RoadCenterY, -30.f, 6.2f, 7.8f, .6f);
        ++RoadSegments;
    }
    // A perpendicular accessible woodland lane joins the village square.
    // The landward end is a forest-edge vista, not a new quest gate.
    for (int32 Step = 0; Step < 6; ++Step)
    {
        Place(Road, -7350.f, -620.f - 500.f * Step, -30.f,
              3.6f, 5.2f, .6f);
        ++RoadSegments;
    }

    // Small northern-temperate port town: timber houses, stony foundations,
    // rain-shedding roofs and the civic/market square. Decorative facade
    // details are never a new E target or save-progress authority.
    int32 Homes = 0;
    for (const float X : {-5050.f, -6250.f, -8500.f})
    {
        for (const float Y : {-1090.f, 900.f})
        {
            Place(Buildings, X, Y, 158.f, 7.0f, 5.4f, 3.16f);
            Place(Roofs, X, Y - 143.f, 341.f, 7.7f, 3.8f, .25f, 0.f, -23.f);
            Place(Roofs, X, Y + 143.f, 341.f, 7.7f, 3.8f, .25f, 0.f, 23.f);
            // Door facing the cobbled road; ornamental only.
            Place(Trim, X + 165.f, Y > 0.f ? Y - 276.f : Y + 276.f,
                  110.f, 1.1f, .08f, 2.2f);
            ++Homes;
        }
    }
    // A modest hall and an open market green anchor Hilltonia rather than
    // implying a metropolis or pre-established special fuel-cache plot.
    Place(Buildings, -7450.f, 1110.f, 190.f, 9.2f, 6.3f, 3.8f);
    Place(Roofs, -7450.f, 930.f, 401.f, 10.f, 4.2f, .25f, 0.f, -25.f);
    Place(Roofs, -7450.f, 1290.f, 401.f, 10.f, 4.2f, .25f, 0.f, 25.f);
    Place(Trim, -7000.f, 585.f, 100.f, 2.6f, 1.2f, .9f);
    Place(Trim, -7000.f, 585.f, 222.f, 2.9f, 1.45f, .11f);

    // Oak/maple/beech/birch-compatible deciduous silhouettes in the
    // adjacent north-temperate woodland. Review-only spheres are NOT
    // approved species meshes or final seasonally authored canopy colors.
    int32 Trees = 0;
    for (int32 Row = 0; Row < 4; ++Row)
    {
        for (int32 Column = 0; Column < 8; ++Column)
        {
            const float X = -4950.f - Column * 640.f +
                ((Row & 1) ? -135.f : 0.f);
            const float Y = -1900.f - Row * 670.f +
                ((Column & 1) ? -95.f : 0.f);
            // Keep a clearing around the supported woodland lane at
            // X=-7350, so tree trunks do not intercept road collision.
            if (FMath::Abs(X + 7350.f) < 420.f &&
                Y < -1500.f && Y > -3400.f) continue;
            const float Height = 280.f + ((Row + Column) % 3) * 42.f;
            Place(TreeTrunks, X, Y, Height * .5f, .55f, .55f, Height / 100.f);
            Place(TreeCrowns, X, Y, Height + 105.f,
                  2.5f + (Column % 3) * .28f, 2.5f, 2.7f);
            ++Trees;
        }
    }
    // Layered low rolling slopes behind the woodland, purely visual;
    // not a collision/terrain promise and not a world-latitude simulator.
    for (int32 Ridge = 0; Ridge < 4; ++Ridge)
    {
        Place(RollingHills, -5800.f - Ridge * 1250.f,
              -5450.f, -185.f, 25.f, 18.f, 10.f);
    }
    // A visible landward threshold: sign is a preview wayfinder,
    // not a travel teleport, prompt or interactive progression marker.
    Place(TreeTrunks, -4280.f, -600.f, 155.f, .55f, .55f, 3.1f);
    Place(Trim, -4280.f, -610.f, 322.f, 4.5f, .24f, 1.1f);
    TownSigns(Owner, Root);

    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_HILLTONIA_REVIEW_APPLIED land_ground_sections=2 road_segments=%d homes=%d hall=1 wayfinding_signs=4 deciduous_trees=%d town=Hilltonia forest=temperate world_north_latitude_provisional=1 road_collision=WorldStatic seven_firstwake_markers_unchanged=1 saved_map_unchanged=1"),
        RoadSegments, Homes, Trees);
    return true;
}
}
#endif
