#include "Enemies/TSTSSSliceEnemyActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/UObjectGlobals.h"

namespace
{
    void PositionPiece(UStaticMeshComponent* Part, UStaticMesh* Mesh,
                       const FVector& Position, const FVector& Scale,
                       const FRotator& Rotation = FRotator::ZeroRotator)
    {
        Part->SetStaticMesh(Mesh);
        Part->SetRelativeLocationAndRotation(Position, Rotation);
        Part->SetRelativeScale3D(Scale);
        Part->SetVisibility(Mesh != nullptr);
    }

    void TintPiece(UStaticMeshComponent* Part, UMaterialInterface* Material,
                   const FLinearColor& Tint)
    {
        if (!Material || !Part->GetStaticMesh()) return;
        Part->SetMaterial(0, Material);
        if (UMaterialInstanceDynamic* Dynamic =
            Part->CreateDynamicMaterialInstance(0, Material))
        {
            // Engine BasicShapeMaterial supports a Color override; the point
            // light and contrasting silhouettes also work if it does not.
            Dynamic->SetVectorParameterValue(TEXT("Color"), Tint);
        }
    }

}

UStaticMeshComponent* ATSTSSSliceEnemyActor::MakePiece(const TCHAR* Name)
{
    UStaticMeshComponent* Piece = CreateDefaultSubobject<UStaticMeshComponent>(FName(Name));
    Piece->SetupAttachment(VisualRoot);
    Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Piece->SetGenerateOverlapEvents(false);
    return Piece;
}

ATSTSSSliceEnemyActor::ATSTSSSliceEnemyActor()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("ReviewRoot"));
    SetRootComponent(Root);
    VisualRoot = CreateDefaultSubobject<USceneComponent>(TEXT("VisualRoot"));
    VisualRoot->SetupAttachment(Root);
    Core = MakePiece(TEXT("Core"));
    Crown = MakePiece(TEXT("Crown"));
    LeftFin = MakePiece(TEXT("LeftFin"));
    RightFin = MakePiece(TEXT("RightFin"));
    LowerLeft = MakePiece(TEXT("LowerLeft"));
    LowerRight = MakePiece(TEXT("LowerRight"));
    EyeLeft = MakePiece(TEXT("EyeLeft"));
    EyeRight = MakePiece(TEXT("EyeRight"));
    Glow = CreateDefaultSubobject<UPointLightComponent>(TEXT("AtmosphericGlow"));
    Glow->SetupAttachment(VisualRoot);
    Glow->SetIntensity(1700.f);
    Glow->SetAttenuationRadius(370.f);
    Glow->SetCastShadows(false);
    ReviewLabel = CreateDefaultSubobject<UTextRenderComponent>(TEXT("ReviewOnlyName"));
    ReviewLabel->SetupAttachment(Root);
    ReviewLabel->SetHorizontalAlignment(EHTA_Center);
    ReviewLabel->SetWorldSize(23.f);
    ReviewLabel->SetRelativeLocation(FVector(0.f, 0.f, 270.f));
    ReviewLabel->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));
    SetActorEnableCollision(false);
}

bool ATSTSSSliceEnemyActor::TryBuildReviewParticipant(
    FTSS_CombatParticipant& Out) const
{
    return FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant(Kind, InstanceId, Out);
}

bool ATSTSSSliceEnemyActor::TryGetReviewDescriptor(
    FTSTSSSliceEnemyDescriptor& Out) const
{
    return FTSTSSSliceEnemyCatalog::TryDescribe(Kind, Out);
}

void ATSTSSSliceEnemyActor::RefreshReviewGeometry()
{
#if !UE_BUILD_SHIPPING
    OnConstruction(GetActorTransform());
#endif
}

void ATSTSSSliceEnemyActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    // Engine-built primitives guarantee a geometry fallback with no imported
    // .uasset dependencies. Replace only after native art/visual approval.
    UStaticMesh* Sphere = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    UStaticMesh* Cube = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Cone = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cone.Cone"));
    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));

    FLinearColor Primary(0.12f, 0.68f, 0.77f);
    FLinearColor Accent(0.9f, 0.73f, 0.38f);
    switch (Kind)
    {
    case ETSTSSSliceEnemyKind::HarmonicShear:
        // Split vortex silhouette: tapered crown, orbiting wind spars.
        PositionPiece(Core, Sphere, FVector(0, 0, 135), FVector(.58f, .58f, 1.02f));
        PositionPiece(Crown, Cone, FVector(0, 0, 213), FVector(.54f, .54f, .8f));
        PositionPiece(LeftFin, Cube, FVector(0, -68, 145),
                      FVector(.15f, 1.55f, .15f), FRotator(15, -22, 42));
        PositionPiece(RightFin, Cube, FVector(0, 68, 112),
                      FVector(.15f, 1.42f, .15f), FRotator(-15, 24, -36));
        PositionPiece(LowerLeft, Cone, FVector(-15, -42, 67),
                      FVector(.23f, .23f, .66f), FRotator(0, 30, 180));
        PositionPiece(LowerRight, Cone, FVector(15, 42, 73),
                      FVector(.27f, .27f, .64f), FRotator(0, -35, 180));
        PositionPiece(EyeLeft, Sphere, FVector(38, -22, 168), FVector(.15f));
        PositionPiece(EyeRight, Sphere, FVector(38, 22, 168), FVector(.15f));
        Primary = FLinearColor(.09f, .74f, .82f);
        Accent = FLinearColor(.95f, .73f, .43f);
        break;
    case ETSTSSSliceEnemyKind::AetherLeakWisp:
        // Hovering lumen core and satellite motes, readable at a distance.
        PositionPiece(Core, Sphere, FVector(0, 0, 124), FVector(.68f));
        PositionPiece(Crown, Sphere, FVector(0, 0, 180), FVector(.22f));
        PositionPiece(LeftFin, Sphere, FVector(-32, -79, 152), FVector(.29f));
        PositionPiece(RightFin, Sphere, FVector(26, 80, 105), FVector(.26f));
        PositionPiece(LowerLeft, Cube, FVector(0, -49, 125),
                      FVector(.12f, 1.05f, .1f), FRotator(0, 0, 32));
        PositionPiece(LowerRight, Cube, FVector(0, 49, 110),
                      FVector(.1f, .94f, .1f), FRotator(0, 0, -27));
        PositionPiece(EyeLeft, Sphere, FVector(48, -15, 135), FVector(.095f));
        PositionPiece(EyeRight, Sphere, FVector(48, 15, 135), FVector(.095f));
        Primary = FLinearColor(.44f, .30f, .91f);
        Accent = FLinearColor(.17f, .92f, .92f);
        break;
    case ETSTSSSliceEnemyKind::DockSkitter:
        // Low armored chassis with four angled legs and paired eye stalks.
        PositionPiece(Core, Sphere, FVector(0, 0, 76), FVector(.88f, .68f, .42f));
        PositionPiece(Crown, Cone, FVector(57, 0, 80),
                      FVector(.38f, .38f, .55f), FRotator(0, 0, -75));
        PositionPiece(LeftFin, Cube, FVector(-19, -78, 58),
                      FVector(.2f, 1.02f, .17f), FRotator(15, 0, 24));
        PositionPiece(RightFin, Cube, FVector(-19, 78, 58),
                      FVector(.2f, 1.02f, .17f), FRotator(-15, 0, -24));
        PositionPiece(LowerLeft, Cube, FVector(39, -65, 34),
                      FVector(.19f, .83f, .17f), FRotator(0, 25, -20));
        PositionPiece(LowerRight, Cube, FVector(39, 65, 34),
                      FVector(.19f, .83f, .17f), FRotator(0, -25, 20));
        PositionPiece(EyeLeft, Sphere, FVector(43, -26, 112), FVector(.14f));
        PositionPiece(EyeRight, Sphere, FVector(43, 26, 112), FVector(.14f));
        Primary = FLinearColor(.5f, .26f, .14f);
        Accent = FLinearColor(1.f, .75f, .22f);
        break;
    case ETSTSSSliceEnemyKind::BanditCutpurse:
        // Review-only distinct silhouette for Quayside Cutpurse.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 110.f), FVector(0.34f, 0.34f, 0.63f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 178.f), FVector(0.25f, 0.25f, 0.26f));
        PositionPiece(LeftFin, Cube, FVector(0.f, -42.f, 132.f), FVector(0.15f, 0.5f, 0.16f), FRotator(0.f, 0.f, 24.f));
        PositionPiece(RightFin, Cone, FVector(20.f, 43.f, 122.f), FVector(0.21f, 0.21f, 0.54f), FRotator(0.f, 0.f, 32.f));
        PositionPiece(LowerLeft, Cube, FVector(0.f, -20.f, 43.f), FVector(0.18f, 0.18f, 0.76f));
        PositionPiece(LowerRight, Cube, FVector(0.f, 22.f, 43.f), FVector(0.18f, 0.18f, 0.76f));
        PositionPiece(EyeLeft, Sphere, FVector(22.f, -13.f, 184.f), FVector(0.09f, 0.09f, 0.09f));
        PositionPiece(EyeRight, Sphere, FVector(22.f, 13.f, 184.f), FVector(0.09f, 0.09f, 0.09f));
        Primary = FLinearColor(0.23f, 0.22f, 0.19f);
        Accent = FLinearColor(0.84f, 0.69f, 0.4f);
        break;
    case ETSTSSSliceEnemyKind::BanditSlinger:
        // Review-only distinct silhouette for Quayside Slinger.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 111.f), FVector(0.37f, 0.31f, 0.66f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 179.f), FVector(0.25f, 0.27f, 0.25f));
        PositionPiece(LeftFin, Cube, FVector(0.f, -55.f, 137.f), FVector(0.12f, 0.95f, 0.13f), FRotator(0.f, 0.f, 20.f));
        PositionPiece(RightFin, Cube, FVector(12.f, 48.f, 134.f), FVector(0.13f, 0.75f, 0.13f), FRotator(0.f, 0.f, -32.f));
        PositionPiece(LowerLeft, Cube, FVector(0.f, -21.f, 43.f), FVector(0.17f, 0.17f, 0.75f));
        PositionPiece(LowerRight, Cube, FVector(0.f, 21.f, 43.f), FVector(0.17f, 0.17f, 0.75f));
        PositionPiece(EyeLeft, Sphere, FVector(23.f, -12.f, 185.f), FVector(0.08f, 0.08f, 0.08f));
        PositionPiece(EyeRight, Sphere, FVector(23.f, 12.f, 185.f), FVector(0.08f, 0.08f, 0.08f));
        Primary = FLinearColor(0.3f, 0.35f, 0.29f);
        Accent = FLinearColor(0.94f, 0.55f, 0.29f);
        break;
    case ETSTSSSliceEnemyKind::BanditCaptain:
        // Review-only distinct silhouette for Bandit Captain.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 128.f), FVector(0.54f, 0.48f, 0.81f));
        PositionPiece(Crown, Cone, FVector(0.f, 0.f, 237.f), FVector(0.39f, 0.39f, 0.6f));
        PositionPiece(LeftFin, Cube, FVector(0.f, -65.f, 157.f), FVector(0.24f, 0.79f, 0.24f), FRotator(0.f, 0.f, 15.f));
        PositionPiece(RightFin, Cube, FVector(0.f, 65.f, 153.f), FVector(0.24f, 0.85f, 0.24f), FRotator(0.f, 0.f, -17.f));
        PositionPiece(LowerLeft, Cube, FVector(0.f, -32.f, 49.f), FVector(0.25f, 0.25f, 0.84f));
        PositionPiece(LowerRight, Cube, FVector(0.f, 32.f, 49.f), FVector(0.25f, 0.25f, 0.84f));
        PositionPiece(EyeLeft, Sphere, FVector(34.f, -17.f, 197.f), FVector(0.11f, 0.11f, 0.11f));
        PositionPiece(EyeRight, Sphere, FVector(34.f, 17.f, 197.f), FVector(0.11f, 0.11f, 0.11f));
        Primary = FLinearColor(0.31f, 0.24f, 0.17f);
        Accent = FLinearColor(0.96f, 0.68f, 0.26f);
        break;
    case ETSTSSSliceEnemyKind::Thornvine:
        // Review-only distinct silhouette for Thornvine Creeper.
        PositionPiece(Core, Cone, FVector(0.f, 0.f, 96.f), FVector(0.65f, 0.65f, 1.28f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 176.f), FVector(0.43f, 0.49f, 0.28f));
        PositionPiece(LeftFin, Cube, FVector(-3.f, -67.f, 118.f), FVector(0.19f, 1.42f, 0.18f), FRotator(0.f, 0.f, -28.f));
        PositionPiece(RightFin, Cube, FVector(-3.f, 69.f, 127.f), FVector(0.19f, 1.43f, 0.18f), FRotator(0.f, 0.f, 29.f));
        PositionPiece(LowerLeft, Cone, FVector(0.f, -30.f, 31.f), FVector(0.34f, 0.31f, 0.68f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(LowerRight, Cone, FVector(0.f, 30.f, 31.f), FVector(0.34f, 0.31f, 0.68f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(EyeLeft, Sphere, FVector(30.f, -15.f, 146.f), FVector(0.1f, 0.1f, 0.1f));
        PositionPiece(EyeRight, Sphere, FVector(30.f, 15.f, 146.f), FVector(0.1f, 0.1f, 0.1f));
        Primary = FLinearColor(0.15f, 0.47f, 0.18f);
        Accent = FLinearColor(0.96f, 0.35f, 0.47f);
        break;
    case ETSTSSSliceEnemyKind::Sporecap:
        // Review-only distinct silhouette for Sporecap Stalker.
        PositionPiece(Core, Cone, FVector(0.f, 0.f, 87.f), FVector(0.32f, 0.35f, 1.18f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 166.f), FVector(1.12f, 0.95f, 0.42f));
        PositionPiece(LeftFin, Sphere, FVector(0.f, -64.f, 160.f), FVector(0.26f, 0.27f, 0.22f));
        PositionPiece(RightFin, Sphere, FVector(0.f, 65.f, 163.f), FVector(0.26f, 0.27f, 0.22f));
        PositionPiece(LowerLeft, Cone, FVector(-10.f, -28.f, 40.f), FVector(0.25f, 0.25f, 0.6f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(LowerRight, Cone, FVector(-10.f, 28.f, 40.f), FVector(0.25f, 0.25f, 0.6f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(EyeLeft, Sphere, FVector(31.f, -16.f, 101.f), FVector(0.1f, 0.1f, 0.1f));
        PositionPiece(EyeRight, Sphere, FVector(31.f, 16.f, 101.f), FVector(0.1f, 0.1f, 0.1f));
        Primary = FLinearColor(0.48f, 0.25f, 0.58f);
        Accent = FLinearColor(0.99f, 0.75f, 0.45f);
        break;
    case ETSTSSSliceEnemyKind::RootSentinel:
        // Review-only distinct silhouette for Root Sentinel.
        PositionPiece(Core, Cube, FVector(0.f, 0.f, 112.f), FVector(0.75f, 0.73f, 1.65f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 227.f), FVector(0.86f, 0.82f, 0.55f));
        PositionPiece(LeftFin, Cube, FVector(-7.f, -92.f, 143.f), FVector(0.29f, 1.31f, 0.26f), FRotator(0.f, 0.f, 35.f));
        PositionPiece(RightFin, Cube, FVector(-7.f, 92.f, 143.f), FVector(0.29f, 1.31f, 0.26f), FRotator(0.f, 0.f, -35.f));
        PositionPiece(LowerLeft, Cone, FVector(0.f, -42.f, 36.f), FVector(0.4f, 0.4f, 0.95f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(LowerRight, Cone, FVector(0.f, 42.f, 36.f), FVector(0.4f, 0.4f, 0.95f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(EyeLeft, Sphere, FVector(42.f, -24.f, 166.f), FVector(0.16f, 0.16f, 0.16f));
        PositionPiece(EyeRight, Sphere, FVector(42.f, 24.f, 166.f), FVector(0.16f, 0.16f, 0.16f));
        Primary = FLinearColor(0.29f, 0.34f, 0.17f);
        Accent = FLinearColor(0.62f, 0.95f, 0.3f);
        break;
    case ETSTSSSliceEnemyKind::ReefEel:
        // Review-only distinct silhouette for Reef Eel.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 113.f), FVector(0.56f, 0.32f, 0.4f));
        PositionPiece(Crown, Sphere, FVector(49.f, 0.f, 121.f), FVector(0.35f, 0.31f, 0.29f));
        PositionPiece(LeftFin, Cube, FVector(-56.f, -13.f, 107.f), FVector(1.f, 0.17f, 0.19f), FRotator(0.f, 24.f, -22.f));
        PositionPiece(RightFin, Cube, FVector(-98.f, 0.f, 67.f), FVector(0.55f, 0.21f, 0.18f), FRotator(0.f, -22.f, 34.f));
        PositionPiece(LowerLeft, Cone, FVector(0.f, -33.f, 116.f), FVector(0.25f, 0.24f, 0.4f), FRotator(0.f, 0.f, -35.f));
        PositionPiece(LowerRight, Cone, FVector(0.f, 33.f, 116.f), FVector(0.25f, 0.24f, 0.4f), FRotator(0.f, 0.f, 35.f));
        PositionPiece(EyeLeft, Sphere, FVector(71.f, -15.f, 133.f), FVector(0.095f, 0.095f, 0.095f));
        PositionPiece(EyeRight, Sphere, FVector(71.f, 15.f, 133.f), FVector(0.095f, 0.095f, 0.095f));
        Primary = FLinearColor(0.11f, 0.47f, 0.55f);
        Accent = FLinearColor(0.44f, 0.95f, 0.82f);
        break;
    case ETSTSSSliceEnemyKind::TidefinRaptor:
        // Review-only distinct silhouette for Tidefin Hunter.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 104.f), FVector(0.93f, 0.5f, 0.38f));
        PositionPiece(Crown, Cone, FVector(76.f, 0.f, 113.f), FVector(0.4f, 0.38f, 0.76f), FRotator(0.f, -72.f, 0.f));
        PositionPiece(LeftFin, Cone, FVector(0.f, -49.f, 112.f), FVector(0.33f, 0.27f, 0.63f), FRotator(0.f, 0.f, 60.f));
        PositionPiece(RightFin, Cone, FVector(0.f, 49.f, 112.f), FVector(0.33f, 0.27f, 0.63f), FRotator(0.f, 0.f, -60.f));
        PositionPiece(LowerLeft, Cone, FVector(-52.f, -35.f, 74.f), FVector(0.25f, 0.25f, 0.47f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(LowerRight, Cone, FVector(-52.f, 35.f, 74.f), FVector(0.25f, 0.25f, 0.47f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(EyeLeft, Sphere, FVector(55.f, -24.f, 126.f), FVector(0.1f, 0.1f, 0.1f));
        PositionPiece(EyeRight, Sphere, FVector(55.f, 24.f, 126.f), FVector(0.1f, 0.1f, 0.1f));
        Primary = FLinearColor(0.14f, 0.36f, 0.53f);
        Accent = FLinearColor(0.88f, 0.74f, 0.42f);
        break;
    case ETSTSSSliceEnemyKind::ShellbackCrab:
        // Review-only distinct silhouette for Shellback Crab.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 80.f), FVector(1.f, 0.88f, 0.45f));
        PositionPiece(Crown, Sphere, FVector(0.f, 0.f, 116.f), FVector(0.86f, 0.75f, 0.35f));
        PositionPiece(LeftFin, Cone, FVector(46.f, -94.f, 81.f), FVector(0.45f, 0.42f, 0.66f), FRotator(0.f, 0.f, 70.f));
        PositionPiece(RightFin, Cone, FVector(46.f, 94.f, 81.f), FVector(0.45f, 0.42f, 0.66f), FRotator(0.f, 0.f, -70.f));
        PositionPiece(LowerLeft, Cube, FVector(-40.f, -73.f, 33.f), FVector(0.22f, 1.05f, 0.18f), FRotator(0.f, 0.f, 25.f));
        PositionPiece(LowerRight, Cube, FVector(-40.f, 73.f, 33.f), FVector(0.22f, 1.05f, 0.18f), FRotator(0.f, 0.f, -25.f));
        PositionPiece(EyeLeft, Sphere, FVector(67.f, -26.f, 115.f), FVector(0.12f, 0.12f, 0.12f));
        PositionPiece(EyeRight, Sphere, FVector(67.f, 26.f, 115.f), FVector(0.12f, 0.12f, 0.12f));
        Primary = FLinearColor(0.35f, 0.27f, 0.37f);
        Accent = FLinearColor(0.97f, 0.67f, 0.36f);
        break;
    case ETSTSSSliceEnemyKind::CliffLynx:
        // Review-only distinct silhouette for Cliff Lynx.
        PositionPiece(Core, Sphere, FVector(-10.f, 0.f, 95.f), FVector(0.85f, 0.42f, 0.39f));
        PositionPiece(Crown, Sphere, FVector(57.f, 0.f, 120.f), FVector(0.36f, 0.37f, 0.39f));
        PositionPiece(LeftFin, Cone, FVector(60.f, -26.f, 164.f), FVector(0.16f, 0.16f, 0.3f));
        PositionPiece(RightFin, Cone, FVector(60.f, 26.f, 164.f), FVector(0.16f, 0.16f, 0.3f));
        PositionPiece(LowerLeft, Cube, FVector(-50.f, -35.f, 43.f), FVector(0.18f, 0.18f, 0.68f));
        PositionPiece(LowerRight, Cube, FVector(35.f, 35.f, 43.f), FVector(0.18f, 0.18f, 0.68f));
        PositionPiece(EyeLeft, Sphere, FVector(82.f, -19.f, 131.f), FVector(0.1f, 0.1f, 0.1f));
        PositionPiece(EyeRight, Sphere, FVector(82.f, 19.f, 131.f), FVector(0.1f, 0.1f, 0.1f));
        Primary = FLinearColor(0.57f, 0.46f, 0.28f);
        Accent = FLinearColor(0.96f, 0.86f, 0.43f);
        break;
    case ETSTSSSliceEnemyKind::Bristleboar:
        // Review-only distinct silhouette for Bristleboar.
        PositionPiece(Core, Sphere, FVector(-15.f, 0.f, 96.f), FVector(1.12f, 0.75f, 0.65f));
        PositionPiece(Crown, Cone, FVector(82.f, 0.f, 97.f), FVector(0.46f, 0.48f, 0.72f), FRotator(0.f, -65.f, 0.f));
        PositionPiece(LeftFin, Cone, FVector(-42.f, -32.f, 176.f), FVector(0.25f, 0.25f, 0.42f), FRotator(0.f, 0.f, -20.f));
        PositionPiece(RightFin, Cone, FVector(2.f, 32.f, 175.f), FVector(0.24f, 0.24f, 0.46f), FRotator(0.f, 0.f, 20.f));
        PositionPiece(LowerLeft, Cube, FVector(-61.f, -46.f, 39.f), FVector(0.29f, 0.29f, 0.76f));
        PositionPiece(LowerRight, Cube, FVector(41.f, 46.f, 39.f), FVector(0.29f, 0.29f, 0.76f));
        PositionPiece(EyeLeft, Sphere, FVector(65.f, -39.f, 131.f), FVector(0.13f, 0.13f, 0.13f));
        PositionPiece(EyeRight, Sphere, FVector(65.f, 39.f, 131.f), FVector(0.13f, 0.13f, 0.13f));
        Primary = FLinearColor(0.43f, 0.28f, 0.2f);
        Accent = FLinearColor(0.99f, 0.76f, 0.34f);
        break;
    case ETSTSSSliceEnemyKind::NightGlider:
        // Review-only distinct silhouette for Night Glider.
        PositionPiece(Core, Sphere, FVector(0.f, 0.f, 136.f), FVector(0.54f, 0.39f, 0.31f));
        PositionPiece(Crown, Sphere, FVector(39.f, 0.f, 148.f), FVector(0.28f, 0.27f, 0.26f));
        PositionPiece(LeftFin, Cube, FVector(-9.f, -104.f, 137.f), FVector(0.18f, 2.04f, 0.12f), FRotator(12.f, 0.f, 19.f));
        PositionPiece(RightFin, Cube, FVector(-9.f, 104.f, 137.f), FVector(0.18f, 2.04f, 0.12f), FRotator(-12.f, 0.f, -19.f));
        PositionPiece(LowerLeft, Cone, FVector(-43.f, -37.f, 93.f), FVector(0.2f, 0.2f, 0.67f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(LowerRight, Cone, FVector(-43.f, 37.f, 93.f), FVector(0.2f, 0.2f, 0.67f), FRotator(0.f, 0.f, 180.f));
        PositionPiece(EyeLeft, Sphere, FVector(57.f, -14.f, 155.f), FVector(0.095f, 0.095f, 0.095f));
        PositionPiece(EyeRight, Sphere, FVector(57.f, 14.f, 155.f), FVector(0.095f, 0.095f, 0.095f));
        Primary = FLinearColor(0.29f, 0.23f, 0.42f);
        Accent = FLinearColor(0.43f, 0.86f, 0.97f);
        break;
    default:
        return;
    }

    for (UStaticMeshComponent* Part :
        {Core.Get(), Crown.Get(), LeftFin.Get(), RightFin.Get(),
         LowerLeft.Get(), LowerRight.Get()})
    {
        TintPiece(Part, BasicMaterial, Primary);
    }
    TintPiece(EyeLeft, BasicMaterial, Accent);
    TintPiece(EyeRight, BasicMaterial, Accent);
    Glow->SetLightColor(Primary.ToFColor(true));
    Glow->SetRelativeLocation(FVector(25.f, 0.f, 135.f));
    ReviewLabel->SetTextRenderColor(Accent.ToFColor(true));
    FTSTSSSliceEnemyDescriptor Definition;
    if (FTSTSSSliceEnemyCatalog::TryDescribe(Kind, Definition))
    {
        ReviewLabel->SetText(FText::FromString(Definition.DisplayName + TEXT(" / REVIEW")));
    }
    IdleTime = 0.f;
    VisualRoot->SetRelativeTransform(FTransform::Identity);
}

void ATSTSSSliceEnemyActor::BeginPlay()
{
    Super::BeginPlay();
#if UE_BUILD_SHIPPING
    // A review primitive cannot accidentally become shipped enemy placement.
    SetActorHiddenInGame(true);
    SetActorTickEnabled(false);
#endif
}

void ATSTSSSliceEnemyActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bReducedMotion)
    {
        VisualRoot->SetRelativeLocation(FVector::ZeroVector);
        VisualRoot->SetRelativeRotation(FRotator::ZeroRotator);
        return;
    }
    IdleTime += DeltaSeconds;
    const bool bFloating = Kind == ETSTSSSliceEnemyKind::HarmonicShear ||
                           Kind == ETSTSSSliceEnemyKind::AetherLeakWisp ||
                           Kind == ETSTSSSliceEnemyKind::ReefEel ||
                           Kind == ETSTSSSliceEnemyKind::TidefinRaptor ||
                           Kind == ETSTSSSliceEnemyKind::NightGlider;
    const float Speed = bFloating ? 1.f : 1.6f;
    const float Hover = bFloating ? 9.f : 2.5f;
    VisualRoot->SetRelativeLocation(
        FVector(0.f, 0.f, FMath::Sin(IdleTime * Speed * 1.7f) * Hover));
    VisualRoot->SetRelativeRotation(
        FRotator(0.f, FMath::Sin(IdleTime * Speed * .7f) * 11.f, 0.f));
}
