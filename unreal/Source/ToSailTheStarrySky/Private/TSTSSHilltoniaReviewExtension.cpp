#include "TSTSSHilltoniaReviewExtension.h"
#include "UObject/Package.h"

#if WITH_EDITOR
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
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
// Local +X is east toward the dock and -X is west toward Greenwood.
// -Y is north. The dock
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

void ExtendHarborWater(AActor* Owner, USceneComponent* Root,
                       const UStaticMeshComponent* Source)
{
    if (!IsValid(Source) || !IsValid(Source->GetStaticMesh()) ||
        !IsValid(Source->GetMaterial(0)) ||
        !Source->GetComponentQuat().Equals(FQuat::Identity))
    {
        return;
    }

    // Repeat the authored plane at its original texel density. The V5
    // ocean material is authored for ordinary static mesh components.
    const FVector Scale = Source->GetComponentTransform().GetScale3D();
    const FVector FullSize = Source->GetStaticMesh()->GetBounds().BoxExtent * Scale * 2.0;
    if (FullSize.ContainsNaN() || FullSize.X <= 0.0 || FullSize.Y <= 0.0) return;

    constexpr int32 RingRadius = 2;
    for (int32 Y = -RingRadius; Y <= RingRadius; ++Y)
    {
        for (int32 X = -RingRadius; X <= RingRadius; ++X)
        {
            if (X == 0 && Y == 0) continue;
            auto* Tile = NewObject<UStaticMeshComponent>(Owner, NAME_None, RF_Transient);
            Tile->SetMobility(EComponentMobility::Movable);
            Tile->SetupAttachment(Root);
            Tile->SetStaticMesh(Source->GetStaticMesh());
            Tile->SetMaterial(0, Source->GetMaterial(0));
            Tile->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Tile->SetGenerateOverlapEvents(false);
            Tile->SetCastShadow(false);
            Tile->SetRelativeScale3D(Scale);
            Tile->SetRelativeLocation(Source->GetComponentLocation() +
                FVector(X * FullSize.X, Y * FullSize.Y, 0.0));
            Owner->AddInstanceComponent(Tile);
            Tile->RegisterComponent();
        }
    }
}

void WayfindingSign(AActor* Owner, USceneComponent* Root,
                    const TCHAR* ComponentName, const TCHAR* Caption,
                    const FVector& Location, float Yaw,
                    UStaticMesh* BoardMesh, UMaterialInterface* BoardMaterial)
{
    // A thin opaque backing separates two readable faces. Every component is
    // decorative and has no collision, interaction or story authority.
    if (!IsValid(BoardMesh) || !IsValid(BoardMaterial)) return;
    const FRotator FrontRotation(0.f, Yaw, 0.f);
    const FVector FaceNormal = FrontRotation.Vector();
    const FString BoardName = FString::Printf(TEXT("%s_Backboard"), ComponentName);
    auto* Board = NewObject<UStaticMeshComponent>(Owner, FName(*BoardName));
    Board->SetMobility(EComponentMobility::Movable);
    Board->SetupAttachment(Root);
    Board->SetStaticMesh(BoardMesh);
    Board->SetMaterial(0, BoardMaterial);
    Board->SetRelativeLocation(Location);
    Board->SetRelativeRotation(FrontRotation);
    const float Width = FMath::Clamp(FCString::Strlen(Caption) * .24f, 3.f, 10.f);
    Board->SetRelativeScale3D(FVector(.12f, Width, .8f));
    Board->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Owner->AddInstanceComponent(Board);
    Board->RegisterComponent();

    const auto AddFace = [&](const TCHAR* Suffix, const FVector& Position, float FaceYaw)
    {
        const FString Name = FString::Printf(TEXT("%s_%s"), ComponentName, Suffix);
        auto* Text = NewObject<UTextRenderComponent>(Owner, FName(*Name));
        Text->SetMobility(EComponentMobility::Movable);
        Text->SetupAttachment(Root);
        Text->SetText(FText::FromString(Caption));
        Text->SetWorldSize(40.f);
        Text->SetHorizontalAlignment(EHTA_Center);
        Text->SetVerticalAlignment(EVRTA_TextCenter);
        Text->SetTextRenderColor(FColor(233, 220, 172));
        Text->SetRelativeLocation(Position);
        Text->SetRelativeRotation(FRotator(0.f, FaceYaw, 0.f));
        Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Owner->AddInstanceComponent(Text);
        Text->RegisterComponent();
    };
    AddFace(TEXT("Front"), Location + FaceNormal * 10.f, Yaw);
    AddFace(TEXT("Back"), Location - FaceNormal * 10.f, Yaw + 180.f);
}

// Native TextRender lettering stays vector-sharp at play distance. No generated
// concept image is substituted for a physical quest target in the review map.
void NoticeLettering(AActor* Owner, USceneComponent* Root,
                     const TCHAR* Name, const TCHAR* Caption,
                     const FVector& Position, float WorldSize,
                     const FColor& Ink)
{
    auto* Text = NewObject<UTextRenderComponent>(Owner, Name);
    Text->SetMobility(EComponentMobility::Movable);
    Text->SetupAttachment(Root);
    Text->SetText(FText::FromString(Caption));
    Text->SetWorldSize(WorldSize);
    Text->SetHorizontalAlignment(EHTA_Center);
    Text->SetVerticalAlignment(EVRTA_TextCenter);
    Text->SetTextRenderColor(Ink);
    Text->SetRelativeLocation(Position);
    Text->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
    Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Owner->AddInstanceComponent(Text);
    Text->RegisterComponent();
}

void TownSigns(AActor* Owner, USceneComponent* Root,
               UStaticMesh* Cube, UMaterialInterface* Timber)
{
    // Main arrival is visible from the original dock end, off the walkable
    // street. The three following signboards are on the verge, not on-road.
    WayfindingSign(Owner, Root, TEXT("HilltoniaLandwardEntrySign"),
        TEXT("HILLTONIA  |  WOODLAND ROAD"),
        FVector(-4290.f, -690.f, 340.f), 0.f, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaWoodlandTurnoffSign"),
        TEXT("GREENWOOD WEST  |  HARBOR EAST"),
        FVector(-7070.f, -690.f, 330.f), 0.f, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaForestEdgeReturnSign"),
        TEXT("FOREST EDGE  |  RETURN TO HILLTONIA"),
        FVector(-7000.f, -2940.f, 325.f), 90.f, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaTownWestReturnSign"),
        TEXT("TOWN END  |  RETURN TO HARBOR"),
        FVector(-8750.f, -680.f, 315.f), 0.f, Cube, Timber);
}
}

namespace TSTSSHilltoniaReviewExtension
{
bool Apply(UWorld* World, UMaterialInterface* Timber,
           UMaterialInterface* Stone, UMaterialInterface* Brass,
           UMaterialInterface* Canopy, const UStaticMeshComponent* HarborWater)
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
    auto* WestRoad = Make(Owner, Root, TEXT("HilltoniaWestForestRoad"),
                          Cube, Stone, true);
    auto* CoastalBuffer = Make(Owner, Root, TEXT("HilltoniaCoastalBuffer"),
                               Cube, Canopy, true);
    auto* WesternGround = Make(Owner, Root, TEXT("HilltoniaWesternGround"),
                               Cube, Canopy, true);
    auto* WestTrees = Make(Owner, Root, TEXT("HilltoniaWestForestTrunks"),
                           Cylinder, Timber, true);
    auto* WestCrowns = Make(Owner, Root, TEXT("HilltoniaWestForestCrowns"),
                            Sphere, Canopy, false);
    auto* WestUnderstory = Make(Owner, Root, TEXT("HilltoniaWestUnderstory"),
                                Sphere, Canopy, false);
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
    // Backdrop trees and understory are cosmetic pending collision and art review.
    auto* BackdropTrunks = Make(Owner, Root, TEXT("HilltoniaBackdropTrunks"),
                                Cylinder, Timber, false);
    auto* BackdropCrowns = Make(Owner, Root, TEXT("HilltoniaBackdropCrowns"),
                                Sphere, Canopy, false);
    auto* Understory = Make(Owner, Root, TEXT("HilltoniaUnderstory"),
                            Sphere, Canopy, false);
    auto* GreenBorder = Make(Owner, Root, TEXT("HilltoniaMarketGreenBorder"),
                              Cube, Stone, false);
    auto* GreenSurface = Make(Owner, Root, TEXT("HilltoniaMarketGreenSurface"),
                               Cube, Canopy, false);
    auto* RollingHills = Make(Owner, Root, TEXT("HilltoniaWoodedSlopeBackdrop"),
                              Sphere, Canopy, false);
    auto* ShoreSlopes = Make(Owner, Root, TEXT("HilltoniaSubmergedShoreSlopes"),
                             Sphere, Canopy, false);
    // Decorative civic landmark, adapted from PR #850 to the inland layout.
    UMaterialInterface* Ocean = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/TSTSS/Review/VerticalSlice/M_VS_Ocean.M_VS_Ocean"));
    auto* FountainBasin = Make(Owner, Root, TEXT("HilltoniaRoundStoneFountain"),
                               Cylinder, Stone, true);
    auto* FountainRim = Make(Owner, Root, TEXT("HilltoniaFountainStoneRim"),
                             Cube, Stone, true);
    auto* FountainSpout = Make(Owner, Root, TEXT("HilltoniaFountainBrassSpout"),
                               Cylinder, Brass, false);
    auto* FountainWater = IsValid(Ocean)
        ? Make(Owner, Root, TEXT("HilltoniaFountainDecorativeWater"),
               Cylinder, Ocean, false) : nullptr;
    auto* NoticePosts = Make(Owner, Root, TEXT("HilltoniaPostingBoardPosts"),
                             Cube, Timber, true);
    auto* NoticePanel = Make(Owner, Root, TEXT("HilltoniaPostingBoardPanel"),
                             Cube, Timber, true);
    NoticePanel->ComponentTags.Add(TEXT("TSTSS_HILLTONIA_FLYER"));
    auto* NoticeRoof = Make(Owner, Root, TEXT("HilltoniaPostingBoardGable"),
                            Cube, Timber, false);
    auto* NoticeSheet = Make(Owner, Root, TEXT("HilltoniaPostingBoardFlyerPaper"),
                             Cube, Brass, false);
    // Approved concept study: low gabled noticeboard, visible readable flyer,
    // wooden name plaque, layered paper notices, brass fittings and warm lamp.
    // These are geometry-only preview accents, NOT imported concept pixels.
    auto* NoticeHeader = Make(Owner, Root, TEXT("HilltoniaPostingBoardNamePlaque"),
                              Cube, Timber, false);
    auto* NoticePlaqueTrim = Make(Owner, Root, TEXT("HilltoniaPostingBoardPlaqueTrim"),
                                  Cube, Brass, false);
    auto* NoticePinnedPapers = Make(Owner, Root, TEXT("HilltoniaPostingBoardOtherNotices"),
                                    Cube, Stone, false);
    auto* NoticePaperInk = Make(Owner, Root, TEXT("HilltoniaPostingBoardInkRules"),
                                Cube, Timber, false);
    auto* NoticeTacks = Make(Owner, Root, TEXT("HilltoniaPostingBoardBrassTacks"),
                             Sphere, Brass, false);
    auto* NoticeSeal = Make(Owner, Root, TEXT("HilltoniaPostingBoardGearSeal"),
                            Cylinder, Brass, false);
    auto* NoticeLantern = Make(Owner, Root, TEXT("HilltoniaPostingBoardLanternFixture"),
                               Cube, Brass, false);
    auto* NoticeFlowers = Make(Owner, Root, TEXT("HilltoniaPostingBoardFlowerPlanters"),
                               Sphere, Canopy, false);
    auto* NoticePots = Make(Owner, Root, TEXT("HilltoniaPostingBoardPlanterPots"),
                            Cylinder, Stone, false);

    // Actual land mass, not houses hovering over the original ocean plane.
    // Grass/soil surface is Z=-10cm, ten centimeters below the road top.
    // The first 250cm meets the old dock edge without overlapping any
    // First Wake E marker. The coastal buffer below extends the land south;
    // the original dock continues east into the visual-only water plane.
    // These flat prototype shelves are NOT a final Landscape.
    Place(Ground, -7000.f, -1300.f, -90.f, 70.f, 58.f, 1.6f);
    // A second contiguous forest foothill shelf extends the landward
    // ground beneath the tree line, without making scenic ridges solid.
    Place(Ground, -7350.f, -4950.f, -140.f, 63.f, 20.f, 2.6f);
    // Dry land buffers the town from the seaward edge, while the existing
    // dock and its markers continue east over water. All are review shelves.
    Place(CoastalBuffer, -7000.f, 3250.f, -90.f, 70.f, 37.f, 1.6f);
    Place(WesternGround, -14000.f, -1300.f, -90.f, 80.f, 70.f, 1.6f);
    // The shallow banks meet the water below the walkable shelves. They
    // dress the coast without changing dock footing or blocking E traces.
    Place(ShoreSlopes, -7850.f, 4550.f, -110.f, 98.f, 39.f, 1.8f);
    Place(ShoreSlopes, -12550.f, 1790.f, -105.f, 101.f, 30.f, 1.7f);
    Place(ShoreSlopes, -16300.f, -1000.f, -116.f, 51.f, 86.f, 1.9f);
    Place(ShoreSlopes, -12200.f, -4310.f, -110.f, 107.f, 34.f, 1.8f);
    ExtendHarborWater(Owner, Root, HarborWater);

    // Dock-to-town road: 10 overlapping 620-cm ground sections, full top
    // surface at Z=0. Its first 310 cm overlap the original dock floor,
    // while all town collision begins safely west of the first E marker.
    int32 RoadSegments = 0;
    for (float X = RoadFirstX; X >= RoadLastX; X -= RoadStep)
    {
        Place(Road, X, RoadCenterY, -30.f, 6.2f, 7.8f, .6f);
        ++RoadSegments;
    }
    // Extend the SAME east-west street beyond town into Greenwood, with
    // 20cm overlaps and the same walkable width and top height.
    for (int32 Step = 0; Step < 11; ++Step)
    {
        Place(WestRoad, -9650.f - 600.f * Step, RoadCenterY, -30.f,
              6.2f, 7.8f, .6f);
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
    for (const float X : {-5750.f, -6950.f, -9200.f})
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
    Place(Buildings, -8150.f, 1110.f, 190.f, 9.2f, 6.3f, 3.8f);
    Place(Roofs, -8150.f, 930.f, 401.f, 10.f, 4.2f, .25f, 0.f, -25.f);
    Place(Roofs, -8150.f, 1290.f, 401.f, 10.f, 4.2f, .25f, 0.f, 25.f);
    // Visual only: keep clear of the moved hall, homes and east-west road.
    // The board has no quest authority; a future interaction owns acceptance.
    constexpr float FountainX = -7770.f;
    constexpr float FountainY = 500.f;
    Place(FountainBasin, FountainX, FountainY, 18.f, 3.2f, 3.2f, .55f);
    for (int32 Segment = 0; Segment < 12; ++Segment)
    {
        const float Angle = (2.f * PI * Segment) / 12.f;
        Place(FountainRim, FountainX + 132.f * FMath::Cos(Angle),
              FountainY + 132.f * FMath::Sin(Angle), 70.f,
              .52f, .82f, .32f, FMath::RadiansToDegrees(Angle));
    }
    if (FountainWater)
    {
        Place(FountainWater, FountainX, FountainY, 61.f, 2.38f, 2.38f, .05f);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_HILLTONIA_FOUNTAIN_WATER_HOLD"));
    }
    Place(FountainSpout, FountainX, FountainY, 112.f, .27f, .27f, 1.02f);

    constexpr float BoardX = -7380.f;
    constexpr float BoardY = 440.f;
    // Keep the approved SHORT roof profile and existing E-query component.
    // These coordinates stay outside the road, fountain and nearest house.
    Place(NoticePosts, BoardX - 110.f, BoardY, 119.f, .18f, .23f, 2.38f);
    Place(NoticePosts, BoardX + 110.f, BoardY, 119.f, .18f, .23f, 2.38f);
    Place(NoticePanel, BoardX, BoardY, 174.f, 2.55f, .22f, 1.42f);
    Place(NoticeSheet, BoardX, BoardY - 13.f, 180.f, 1.78f, .045f, 1.12f);
    // Shallow gable and lintel shelter the flyer. No roof E interception.
    Place(NoticeRoof, BoardX, BoardY, 244.f, 2.65f, .32f, .16f);
    Place(NoticeRoof, BoardX, BoardY - 35.f, 260.f, 2.95f, .79f, .10f, 0.f, -25.f);
    Place(NoticeRoof, BoardX, BoardY + 35.f, 260.f, 2.95f, .79f, .10f, 0.f, 25.f);
    // Plaque faces the landward player approach. All adornments have
    // NoCollision and lack the flyer interaction tag.
    Place(NoticeHeader, BoardX, BoardY - 80.f, 269.f, 2.20f, .095f, .39f);
    Place(NoticePlaqueTrim, BoardX, BoardY - 87.f, 249.f, 2.22f, .07f, .04f);
    Place(NoticePlaqueTrim, BoardX, BoardY - 87.f, 288.f, 2.22f, .07f, .04f);
    NoticeLettering(Owner, Root, TEXT("HilltoniaPostingBoardPlaqueText"),
        TEXT("HILLTONIA\nPOSTING BOARD"),
        FVector(BoardX, BoardY - 87.f, 269.f), 14.f, FColor(230, 202, 145));

    // Guaranteed spelling is authored as native text rather than baked into
    // concept-art pixels; the central headline is readable at walking range.
    NoticeLettering(Owner, Root, TEXT("HilltoniaPostingFlyerPreview"),
        TEXT("ENGINEER\nWANTED"),
        FVector(BoardX, BoardY - 18.f, 202.f), 25.f, FColor(45, 37, 28));
    NoticeLettering(Owner, Root, TEXT("HilltoniaPostingFlyerCaptain"),
        TEXT("CAPTAIN IONIA"),
        FVector(BoardX, BoardY - 18.f, 139.f), 14.f, FColor(58, 46, 34));
    Place(NoticeSeal, BoardX, BoardY - 20.f, 165.f,
          .17f, .17f, .04f, 0.f, 90.f);
    for (const float SignX : {-80.f, 80.f})
    {
        for (const float SignZ : {132.f, 229.f})
        {
            Place(NoticeTacks, BoardX + SignX, BoardY - 19.f, SignZ,
                  .055f, .04f, .055f);
        }
    }
    // Layered smaller notices and ornamental printed rules, deliberately
    // noninteractive. The single tagged panel still owns flyer discovery.
    for (const float Side : {-1.f, 1.f})
    {
        const float SideX = BoardX + Side * 105.f;
        Place(NoticePinnedPapers, SideX, BoardY - 13.f,
              Side < 0.f ? 185.f : 176.f, .42f, .04f, .65f);
        Place(NoticeTacks, SideX, BoardY - 18.f, 204.f, .05f, .04f, .05f);
        for (int32 Rule = 0; Rule < 4; ++Rule)
        {
            Place(NoticePaperInk, SideX, BoardY - 17.f,
                  192.f - Rule * 12.f, .22f - Rule * .02f, .013f, .012f);
        }
    }
    // A small warm practical lantern and unobtrusive planters echo the
    // approved lookdev, without adding quest triggers or solid obstacles.
    Place(NoticeLantern, BoardX + 153.f, BoardY - 72.f,
          226.f, .46f, .34f, .08f);
    Place(NoticeLantern, BoardX + 166.f, BoardY - 89.f,
          201.f, .22f, .22f, .37f);
    Place(NoticeTacks, BoardX + 166.f, BoardY - 100.f,
          202.f, .18f, .18f, .20f);
    for (const float Side : {-1.f, 1.f})
    {
        const float FlowerX = BoardX + Side * 152.f;
        Place(NoticePots, FlowerX, BoardY + 147.f, 27.f,
              .47f, .47f, .53f);
        Place(NoticeFlowers, FlowerX, BoardY + 147.f, 74.f,
              .63f, .63f, .58f);
    }
    auto* LanternLight = NewObject<UPointLightComponent>(
        Owner, TEXT("HilltoniaPostingBoardWarmLanternLight"));
    LanternLight->SetMobility(EComponentMobility::Movable);
    LanternLight->SetupAttachment(Root);
    LanternLight->SetRelativeLocation(
        FVector(BoardX + 166.f, BoardY - 103.f, 201.f));
    LanternLight->SetIntensity(270.f);
    LanternLight->SetAttenuationRadius(260.f);
    LanternLight->SetLightColor(FLinearColor(1.f, .68f, .38f));
    LanternLight->SetCastShadows(false);
    Owner->AddInstanceComponent(LanternLight);
    LanternLight->RegisterComponent();

    // Exact-head D3D11 visual QA found dark ink unreadable on the blue Stone sheet.
    // Keep the approved short gable and illuminate only the sheet locally.
    // Soft fill reveals the printed sheet beneath the gable. The narrow cone
    // and short attenuation keep the surrounding square on its existing light.
    auto* FlyerFill = NewObject<USpotLightComponent>(Owner, TEXT("HilltoniaPostingFlyerFill"));
    FlyerFill->SetMobility(EComponentMobility::Movable);
    FlyerFill->SetupAttachment(Root);
    const FVector FillPosition(BoardX, BoardY - 115.f, 220.f);
    const FVector FlyerCenter(BoardX, BoardY - 13.f, 180.f);
    FlyerFill->SetRelativeLocation(FillPosition);
    FlyerFill->SetRelativeRotation((FlyerCenter - FillPosition).Rotation());
    FlyerFill->SetInnerConeAngle(30.f);
    FlyerFill->SetOuterConeAngle(38.f);
    FlyerFill->SetAttenuationRadius(190.f);
    FlyerFill->SetIntensity(1350.f);
    FlyerFill->SetLightColor(FLinearColor(1.f, .91f, .78f));
    FlyerFill->SetCastShadows(false);
    Owner->AddInstanceComponent(FlyerFill);
    FlyerFill->RegisterComponent();

    // The Green is a small open, decorative market landmark beside the
    // square, not an interactive market or a new quest authority.
    Place(GreenBorder, -7480.f, 1400.f, -9.f, 3.0f, 3.0f, .04f);
    Place(GreenSurface, -7480.f, 1400.f, -5.f, 2.6f, 2.6f, .04f);

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
    // Greenwood straddles the west road with a broad clear lane.
    int32 WestTreeCount = 0;
    for (int32 Side : {-1, 1})
    {
        for (int32 Row = 0; Row < 2; ++Row)
        {
            for (int32 Column = 0; Column < 8; ++Column)
            {
                const float X = -12450.f - Column * 550.f - Row * 180.f;
                const float Y = Side * (1050.f + Row * 650.f);
                const float Height = 450.f + ((Row + Column) % 4) * 55.f;
                Place(WestTrees, X, Y, Height * .5f - 10.f, .55f, .55f, Height / 100.f);
                // Overlapping lobes and low shrubs are a denser greybox,
                // not approved or species-specific foliage.
                Place(WestCrowns, X, Y, Height + 100.f, 2.8f, 2.7f, 2.8f);
                Place(WestCrowns, X - 85.f, Y + Side * 60.f, Height + 55.f,
                      1.9f, 2.1f, 1.9f);
                Place(WestCrowns, X + 90.f, Y - Side * 50.f, Height + 35.f,
                      1.8f, 1.9f, 1.8f);
                Place(WestUnderstory, X + 150.f, Y + Side * 130.f, 35.f,
                      1.1f, .9f, .9f);
                ++WestTreeCount;
            }
        }
    }
    // Extra non-colliding tree and shrub silhouettes make Greenwood
    // denser on the existing forest shelf; not species-approved assets.
    for (int32 Row = 0; Row < 3; ++Row)
    {
        for (int32 Column = 0; Column < 10; ++Column)
        {
            const float X = -4800.f - Column * 540.f +
                ((Row & 1) ? -125.f : 0.f);
            const float Y = -4150.f - Row * 500.f +
                ((Column & 1) ? -60.f : 0.f);
            const float Height = 330.f + ((Row + Column) % 4) * 35.f;
            Place(BackdropTrunks, X, Y, Height * .5f - 10.f,
                  .48f, .48f, Height / 100.f);
            Place(BackdropCrowns, X, Y, Height + 100.f,
                  2.8f, 2.6f, 2.8f);
            Place(Understory, X + 140.f, Y + 120.f, 35.f,
                  1.0f, .8f, .9f);
        }
    }
    // The Cinemap reference steps inland from the shore. Use the existing
    // Hilltonia material set for three scenic terraces behind the woodland
    // shelf. These sit beyond the current playable forest lane.
    auto* TerraceStone = Make(Owner, Root, TEXT("HilltoniaTerraceRetainingStone"),
                              Cube, Stone, false);
    auto* TerraceGrass = Make(Owner, Root, TEXT("HilltoniaTerraceGrass"),
                              Cube, Canopy, false);
    auto* TerraceWalls = Make(Owner, Root, TEXT("HilltoniaTerraceHouseWalls"),
                              Cube, Timber, false);
    auto* TerraceRoofs = Make(Owner, Root, TEXT("HilltoniaTerraceHouseRoofs"),
                              Cube, Brass, false);

    struct FTerrace
    {
        float CenterX;
        float FrontY;
        float Width;
        float Elevation;
        int32 HouseCount;
    };
    constexpr float TerraceDepth = 1800.f;
    constexpr FTerrace Terraces[] = {
        {-7250.f, -5800.f, 5700.f, 220.f, 5},
        {-6900.f, -7300.f, 5000.f, 610.f, 4},
        {-6400.f, -8800.f, 3900.f, 1100.f, 3},
    };
    for (const FTerrace& Terrace : Terraces)
    {
        const float CenterY = Terrace.FrontY - TerraceDepth * .5f;
        const float StoneHeight = Terrace.Elevation + 100.f;
        Place(TerraceStone, Terrace.CenterX, CenterY,
              Terrace.Elevation - 20.f - StoneHeight * .5f,
              Terrace.Width / 100.f, TerraceDepth / 100.f, StoneHeight / 100.f);
        Place(TerraceGrass, Terrace.CenterX, CenterY, Terrace.Elevation - 10.f,
              (Terrace.Width + 20.f) / 100.f, TerraceDepth / 100.f, .2f);

        for (int32 House = 0; House < Terrace.HouseCount; ++House)
        {
            // Keep roof overhangs well inside the shelf and stagger the
            // street fronts so successive tiers read as separate rows.
            const float Offset = (House + .5f) / Terrace.HouseCount - .5f;
            const float X = Terrace.CenterX + Offset * (Terrace.Width - 560.f);
            const float Y = Terrace.FrontY - 530.f - (House % 2) * 240.f;
            const float WallHeight = 275.f + (House % 3) * 32.f;
            Place(TerraceStone, X, Y, Terrace.Elevation + 14.f, 5.8f, 4.7f, .28f);
            Place(TerraceWalls, X, Y, Terrace.Elevation + 28.f + WallHeight * .5f,
                  5.4f, 4.2f, WallHeight / 100.f);
            const float RoofZ = Terrace.Elevation + 60.f + WallHeight;
            Place(TerraceRoofs, X, Y - 116.f, RoofZ, 6.0f, 2.7f, .20f, 0.f, -25.f);
            Place(TerraceRoofs, X, Y + 116.f, RoofZ, 6.0f, 2.7f, .20f, 0.f, 25.f);
        }
    }
    // A broad low base runs into the back of the retaining walls. Overlapping
    // crests sit farther inland and their lower halves are submerged or buried.
    Place(RollingHills, -7200.f, -11000.f, -1310.f, 121.f, 110.f, 40.f);
    Place(RollingHills, -10200.f, -11150.f, -930.f, 80.f, 92.f, 27.f);
    Place(RollingHills, -4800.f, -11500.f, -960.f, 85.f, 100.f, 29.f);
    Place(RollingHills, -8400.f, -13500.f, -1280.f, 102.f, 81.f, 55.f);
    Place(RollingHills, -5200.f, -13950.f, -1420.f, 94.f, 84.f, 56.f);
    // The reference harbor has an open mouth, a curved outer breakwater,
    // and a lighthouse at its tip. Set it against the coastal buffer on
    // the far side of the water from the playable eastward dock.
    auto* BreakwaterBase = Make(Owner, Root, TEXT("HilltoniaOuterBreakwaterBase"),
                                Cube, Stone, false);
    auto* BreakwaterCoping = Make(Owner, Root, TEXT("HilltoniaOuterBreakwaterCoping"),
                                  Cube, Timber, false);
    const FVector2D BreakwaterPath[] = {
        FVector2D(-3800.f, 4380.f),
        FVector2D(-2750.f, 4680.f),
        FVector2D(-1450.f, 4900.f),
        FVector2D(-50.f, 4900.f),
        FVector2D(1230.f, 4650.f),
        FVector2D(2270.f, 4140.f),
        FVector2D(2940.f, 3420.f),
        FVector2D(3220.f, 2600.f),
    };
    for (int32 Segment = 1; Segment < static_cast<int32>(UE_ARRAY_COUNT(BreakwaterPath)); ++Segment)
    {
        const FVector2D Start = BreakwaterPath[Segment - 1];
        const FVector2D End = BreakwaterPath[Segment];
        const FVector2D Direction = End - Start;
        const FVector2D Center = (Start + End) * .5;
        const float Yaw = FMath::RadiansToDegrees(FMath::Atan2(Direction.Y, Direction.X));
        const float Length = (Direction.Size() + 185.f) / 100.f;
        Place(BreakwaterBase, Center.X, Center.Y, -24.f, Length, 4.80f, 2.08f, Yaw);
        Place(BreakwaterCoping, Center.X, Center.Y, 93.f, Length, 3.35f, .26f, Yaw);
    }

    auto* LighthouseStone = Make(Owner, Root, TEXT("HilltoniaLighthouseStone"),
                                 Cylinder, Stone, false);
    auto* LighthouseTrim = Make(Owner, Root, TEXT("HilltoniaLighthouseGallery"),
                                Cylinder, Timber, false);
    auto* LighthouseLantern = Make(Owner, Root, TEXT("HilltoniaLighthouseLantern"),
                                   Cylinder, Brass, false);
    auto* LighthouseCap = Make(Owner, Root, TEXT("HilltoniaLighthouseCap"),
                               Sphere, Timber, false);
    const FVector2D Lighthouse = BreakwaterPath[UE_ARRAY_COUNT(BreakwaterPath) - 1];
    Place(LighthouseStone, Lighthouse.X, Lighthouse.Y, 41.f, 6.1f, 6.1f, 2.10f);
    Place(LighthouseStone, Lighthouse.X, Lighthouse.Y, 422.f, 3.40f, 3.40f, 5.52f);
    Place(LighthouseTrim, Lighthouse.X, Lighthouse.Y, 715.f, 4.25f, 4.25f, .40f);
    Place(LighthouseLantern, Lighthouse.X, Lighthouse.Y, 803.f, 2.65f, 2.65f, 1.36f);
    Place(LighthouseCap, Lighthouse.X, Lighthouse.Y, 875.f, 3.25f, 3.25f, 1.18f);

    // A visible landward threshold: sign is a preview wayfinder,
    // not a travel teleport, prompt or interactive progression marker.
    Place(TreeTrunks, -4280.f, -600.f, 155.f, .55f, .55f, 3.1f);
    Place(Trim, -4280.f, -610.f, 322.f, 4.5f, .24f, 1.1f);
    TownSigns(Owner, Root, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaMarketGreenSign"),
        TEXT("THE GREEN  |  MARKET"),
        FVector(-7480.f, 1250.f, 310.f), 0.f, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaGreenwoodSign"),
        TEXT("GREENWOOD  |  FOREST EDGE"),
        FVector(-7000.f, -3600.f, 330.f), 90.f, Cube, Timber);

    WayfindingSign(Owner, Root, TEXT("HilltoniaWestRoadSign"),
        TEXT("GREENWOOD WEST  |  HILLTONIA EAST"),
        FVector(-12100.f, -690.f, 310.f), 0.f, Cube, Timber);
    WayfindingSign(Owner, Root, TEXT("HilltoniaWestForestSign"),
        TEXT("GREENWOOD  |  HARBOR EAST"),
        FVector(-15000.f, -690.f, 310.f), 0.f, Cube, Timber);

    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_HILLTONIA_REVIEW_APPLIED coastal_buffer=1 western_ground=1 western_road_segments=11 west_forest_trees=%d land_ground_sections=2 road_segments=%d homes=%d hall=1 wayfinding_signs=8 deciduous_trees=%d town=Hilltonia forest=temperate world_north_latitude_provisional=1 road_collision=WorldStatic seven_firstwake_markers_unchanged=1 saved_map_unchanged=1"),
        WestTreeCount, RoadSegments, Homes, Trees);
    return true;
}
}
#endif
