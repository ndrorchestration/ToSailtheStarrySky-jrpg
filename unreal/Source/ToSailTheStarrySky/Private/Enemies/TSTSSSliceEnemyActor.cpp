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

    UStaticMeshComponent* MakePiece(AActor* Owner, const FName Name,
                                    USceneComponent* Parent)
    {
        UStaticMeshComponent* Piece = Owner->CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Piece->SetupAttachment(Parent);
        Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Piece->SetGenerateOverlapEvents(false);
        return Piece;
    }
}

ATSTSSSliceEnemyActor::ATSTSSSliceEnemyActor()
{
    PrimaryActorTick.bCanEverTick = true;
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("ReviewRoot"));
    SetRootComponent(Root);
    VisualRoot = CreateDefaultSubobject<USceneComponent>(TEXT("VisualRoot"));
    VisualRoot->SetupAttachment(Root);
    Core = MakePiece(this, TEXT("Core"), VisualRoot);
    Crown = MakePiece(this, TEXT("Crown"), VisualRoot);
    LeftFin = MakePiece(this, TEXT("LeftFin"), VisualRoot);
    RightFin = MakePiece(this, TEXT("RightFin"), VisualRoot);
    LowerLeft = MakePiece(this, TEXT("LowerLeft"), VisualRoot);
    LowerRight = MakePiece(this, TEXT("LowerRight"), VisualRoot);
    EyeLeft = MakePiece(this, TEXT("EyeLeft"), VisualRoot);
    EyeRight = MakePiece(this, TEXT("EyeRight"), VisualRoot);
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
    const float Speed = Kind == ETSTSSSliceEnemyKind::DockSkitter ? 1.6f : 1.f;
    const float Hover = Kind == ETSTSSSliceEnemyKind::DockSkitter ? 3.f : 9.f;
    VisualRoot->SetRelativeLocation(
        FVector(0.f, 0.f, FMath::Sin(IdleTime * Speed * 1.7f) * Hover));
    VisualRoot->SetRelativeRotation(
        FRotator(0.f, FMath::Sin(IdleTime * Speed * .7f) * 11.f, 0.f));
}
