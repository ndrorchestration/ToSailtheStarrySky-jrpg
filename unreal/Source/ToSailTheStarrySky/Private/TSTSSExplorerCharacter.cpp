#include "TSTSSExplorerCharacter.h"
#include "UObject/Package.h"
#include "TSTSSReviewGrounding.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSPersistence.h"
#include "TSTSSInteractionReach.h"
#include "TSTSSSaveGame.h"
#include "TSTSSReviewShoreTravelSubsystem.h"
#include "Engine/GameInstance.h"
#if WITH_EDITOR
#include "TSTSSV5HarborReviewDressing.h"
#include "TSTSSHilltoniaReviewExtension.h"
#include "TSTSSHilltoniaRouteTelemetry.h"
#include "AureateWakePreviewActor.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/PostProcessVolume.h"
#include "Materials/MaterialInterface.h"
#endif
#include "Components/StaticMeshComponent.h"
#if WITH_EDITOR
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#endif
#include "Engine/StaticMesh.h"
#include "Engine/TextRenderActor.h"
#include "Components/TextRenderComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Kismet/GameplayStatics.h"
#include "CollisionQueryParams.h"
#if WITH_EDITOR
#include "Review/TSTSSPresentationCoordinatorSubsystem.h"
#include "TSTSSAtmosphereDirector.h"
#include "CineCameraActor.h"
#include "CineCameraComponent.h"
#include "HAL/PlatformTime.h"
#include "EngineUtils.h"
#include "TSTSSReviewContinueManifest.h"
#include "IO/IoHash.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#endif

namespace
{
// This review slot captures story/inspection state, not pawn location.
void ShowFirstWakeReviewSaveLoadStatus(const bool bLoad, const bool bSucceeded)
{
#if !UE_BUILD_SHIPPING
    if (!GEngine) return;
    const TCHAR* Message = bLoad
        ? (bSucceeded
            ? TEXT("First Wake (review): story progress loaded; position unchanged")
            : TEXT("First Wake (review): load failed; no progress restored"))
        : (bSucceeded
            ? TEXT("First Wake (review): story saved; F9 does not move pawn; F7 Continue can restore position")
            : TEXT("First Wake (review): save failed; progress not confirmed"));
    GEngine->AddOnScreenDebugMessage(
        -1, 8.f, bSucceeded ? FColor::Green : FColor::Red, Message);
#else
    (void)bLoad;
    (void)bSucceeded;
#endif
}

// Rejected interactions show the current objective, without implying the
// engine determined why the milestone was refused (order, repetition, etc.).
void ShowFirstWakeReviewProtectedSlotWarning(const bool bLoad)
{
#if !UE_BUILD_SHIPPING
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 8.f, FColor::Red,
            bLoad
                ? TEXT("First Wake (review): no quicksave made in this PIE session")
                : TEXT("First Wake (review): existing PIE quicksave protected; refusing overwrite"));
    }
#else
    (void)bLoad;
#endif
}

void ShowFirstWakeReviewBlockedInteraction(const UTSTSSFirstWakeState* State)
{
#if !UE_BUILD_SHIPPING
    if (GEngine && IsValid(State))
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 5.f, FColor::Yellow,
            FString::Printf(TEXT("First Wake (review): no progress; objective: %s"),
                            *State->GetReviewObjectiveText()));
    }
#else
    (void)State;
#endif
}

void ShowFirstWakeReviewObjective(const UTSTSSFirstWakeState* State)
{
#if !UE_BUILD_SHIPPING
    if (GEngine && IsValid(State))
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 8.f, FColor::Cyan,
            FString::Printf(TEXT("First Wake (review): %s%s  [J to recall]"),
                *State->GetReviewObjectiveText(),
                State->IsSeabourneRecoveryLocked()
                    ? TEXT(" | Aureate Wake: Seabourne only (flight locked)")
                    : TEXT("")));
    }
#else
    (void)State;
#endif
}

#if WITH_EDITOR
void ApplyCoastalRecoveryReviewSignage(UWorld* World)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().Contains(TEXT("/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) != TEXT("VS05_DenithFuelShanty"))
    {
        return;
    }
    // The existing .umap retains its legacy save-compatible identifier.
    // Replace its rejected in-world fuel-cache signage at runtime only.
    // This is NOT approval of a new location name or ship art.
    for (TActorIterator<ATextRenderActor> Sign(World); Sign; ++Sign)
    {
        if (IsValid(*Sign) &&
            Sign->GetActorLabel() == TEXT("TSTSS_VS_REVIEW_FuelShop") &&
            IsValid(Sign->GetTextRender()))
        {
            Sign->GetTextRender()->SetText(
                FText::FromString(TEXT("COASTAL RECOVERY  |  Survey the ship")));
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_REVIEW_COASTAL_REFIT legacy_map=VS05 sign_replaced=1 saved_assets_unchanged=1"));
        }
    }
}
void ApplySeabourneReviewExposure(UWorld* World)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().Contains(TEXT("/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("L_CoastalShip_SeabourneReview"))
    {
        return;
    }

    // An unsaved, review-only postprocess balances the default sky's extreme
    // brightness. It is not a cinematic art approval or global exposure change.
    if (APostProcessVolume* Volume =
        World->SpawnActor<APostProcessVolume>(FVector::ZeroVector, FRotator::ZeroRotator))
    {
        Volume->bUnbound = true;
        Volume->Priority = 105.f;
        Volume->Settings.bOverride_AutoExposureBias = true;
        Volume->Settings.AutoExposureBias = -2.2f;
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_SEABOURNE_REVIEW_EXPOSURE_APPLIED bias=-2.2 map_asset_unchanged=1"));
    }
}
// Provisional review-map player-view exposure, justified only by a
// same-head native D3D11 PIE A/B. This is not production look approval.
void ApplyOpticalReviewPlayerExposure(UWorld* World, UCameraComponent* Camera)
{
    if (!World || World->WorldType != EWorldType::PIE ||
        World->GetNetMode() != NM_Standalone || !IsValid(Camera) ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(
            TEXT("/Game/TSTSS/Review/EngineFocus_V1/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("M_EnginePresentationReview"))
    {
        return;
    }

    // Keep the physical sky and sun; control only this disposable review
    // player's camera. Do not modify global renderer settings or other maps.
    Camera->PostProcessSettings.bOverride_AutoExposureBias = true;
    Camera->PostProcessSettings.AutoExposureBias = -6.0f;
    Camera->PostProcessBlendWeight = 1.0f;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_OPTICAL_PLAYER_EXPOSURE_REVIEW_ONLY bias=-6 sky_enabled=1 map_asset_unchanged=1"));
}

bool ApplyV5HarborReviewLookdev(UWorld* World)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone || !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))
    {
        return false;
    }
    // Source-locked V5 static blockout only. Existing imported material
    // assets provide the first harbor palette; no source .umap is saved.
    struct FLook
    {
        const TCHAR* Label;
        const TCHAR* Material;
        const TCHAR* PBRFamily;
    };
    const FLook Palette[] =
    {
        {TEXT("TSTSS_PRELUDE_REVIEW_Harbor_TraversalFloor"), TEXT("TSTSS_wood"), TEXT("timber")},
        {TEXT("TSTSS_PRELUDE_REVIEW_Ocean_VISUAL_ONLY_NO_BUOYANCY"), TEXT("TSTSS_teal_glass"), TEXT("ocean")},
        {TEXT("TSTSS_PRELUDE_REVIEW_QuaysideWall"), TEXT("TSTSS_dark_iron"), TEXT("stone")},
        {TEXT("TSTSS_PRELUDE_REVIEW_GangwayVisualMarker"), TEXT("TSTSS_brass"), TEXT("brass")},
        {TEXT("TSTSS_PRELUDE_REVIEW_EngineBayVisualMarker"), TEXT("TSTSS_patina"), TEXT("aether")},
        {TEXT("TSTSS_PRELUDE_REVIEW_HarborStorehouseBlockout"), TEXT("TSTSS_wood"), TEXT("timber")}
    };
    const FString MaterialRoot =
        TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/");
    const FString PBRRoot = TEXT("/Game/TSTSS/Review/PreludePBRV1/");
    UMaterialInterface* Loaded[UE_ARRAY_COUNT(Palette)] = {};
    UMaterialInterface* PBRLoaded[UE_ARRAY_COUNT(Palette)] = {};
    AStaticMeshActor* Found[UE_ARRAY_COUNT(Palette)] = {};
    bool bCompletePBRPack = true;
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Palette); ++Index)
    {
        const FString Name = Palette[Index].Material;
        const FString ObjectPath = MaterialRoot + Name + TEXT(".") + Name;
        Loaded[Index] = LoadObject<UMaterialInterface>(nullptr, *ObjectPath);
        if (!IsValid(Loaded[Index]))
        {
            UE_LOG(LogTemp, Warning,
                TEXT("TSTSS_V5_LOOKDEV_HOLD missing material=%s"), *ObjectPath);
            return false; // Never partially re-skin a failed asset inventory.
        }
        // Optional 512px albedo/normal/ORM native imports. All-or-nothing:
        // no mixed partially imported PBR palette may influence the review.
        const FString Family = Palette[Index].PBRFamily;
        const FString Package = PBRRoot + TEXT("M_FW_") + Family;
        PBRLoaded[Index] = LoadObject<UMaterialInterface>(
            nullptr, *(Package + TEXT(".M_FW_") + Family));
        if (!IsValid(PBRLoaded[Index])) bCompletePBRPack = false;
    }
    for (TActorIterator<AStaticMeshActor> It(World); It; ++It)
    {
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Palette); ++Index)
        {
            if (It->GetActorLabel() == Palette[Index].Label)
            {
                Found[Index] = *It;
            }
        }
    }
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Palette); ++Index)
    {
        if (!IsValid(Found[Index]) ||
            !IsValid(Found[Index]->GetStaticMeshComponent()))
        {
            UE_LOG(LogTemp, Warning,
                TEXT("TSTSS_V5_LOOKDEV_HOLD missing geometry=%s"), Palette[Index].Label);
            return false;
        }
    }
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Palette); ++Index)
    {
        // Material override affects visual slot 0, not collision or footing.
        Found[Index]->GetStaticMeshComponent()->SetMaterial(
            0, bCompletePBRPack ? PBRLoaded[Index] : Loaded[Index]);
    }

    // V5 screenshot is severely overexposed; this scoped, unbound local
    // postprocess is intentionally provisional and never saved to a map.
    if (APostProcessVolume* Exposure =
        World->SpawnActor<APostProcessVolume>(FVector::ZeroVector, FRotator::ZeroRotator))
    {
        Exposure->bUnbound = true;
        Exposure->Priority = 100.f;
        Exposure->Settings.bOverride_AutoExposureBias = true;
        Exposure->Settings.AutoExposureBias = -2.2f;
    }
    // A separate unsaved harbor-dressing actor makes the first real PBR
    // texture pass readable as dock architecture instead of a single floor.
    // A partial or missing PBR asset set must never create mismatched props.
    bool bTownReady = false;
    if (bCompletePBRPack)
    {
        const bool bDockReady = TSTSSV5HarborReviewDressing::Apply(
            World, PBRLoaded[0], PBRLoaded[2], PBRLoaded[3], PBRLoaded[4]);
        // Town/woodland review extension is opt-in behind the same scoped
        // V5 harbor gate, but has its own WorldStatic walking route.
        // It cannot instantiate when the base harbor dressing failed.
        if (bDockReady)
        {
            UMaterialInterface* Canopy = LoadObject<UMaterialInterface>(
                nullptr, TEXT("/Game/TSTSS/Review/VerticalSlice/M_VS_Green.M_VS_Green"));
            if (IsValid(Canopy))
            {
                bTownReady = TSTSSHilltoniaReviewExtension::Apply(
                    World, PBRLoaded[0], PBRLoaded[2], PBRLoaded[3], Canopy);
            }
            else
            {
                UE_LOG(LogTemp, Warning,
                    TEXT("TSTSS_HILLTONIA_HOLD missing forest material; town not spawned"));
            }
        }
    }
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_V5_LOOKDEV_APPLIED material_slots=6 pbr=%d exposure_bias=-2.2 source_map_unchanged=1"),
        bCompletePBRPack ? 1 : 0);
    return bTownReady;
}
#endif

#if WITH_EDITOR
constexpr const TCHAR* ReviewPrimarySlot = TEXT("tstss_prelude_pie_quick");
constexpr const TCHAR* ReviewManifestSlot = TEXT("tstss_prelude_pie_manifest_v1");

FString BoundReviewMapPackage(const UWorld* World)
{
    if (!World || !World->GetOutermost()) return FString();
    return FPackageName::GetLongPackagePath(World->GetOutermost()->GetName()) +
        TEXT("/") + UGameplayStatics::GetCurrentLevelName(World, true);
}

FString BoundReviewProjectRoot()
{
    return FPaths::ConvertRelativePathToFull(FPaths::ProjectDir());
}

// BLAKE3 truncated to 160 bits is an integrity binding between two
// SaveGame files, not an authentication signature or source-commit proof.
bool DigestExactReviewPrimary(const FString& Slot, FString& OutDigest)
{
    OutDigest.Reset();
    if (Slot != ReviewPrimarySlot) return false;
    const FString Path = FPaths::Combine(
        FPaths::ProjectSavedDir(), TEXT("SaveGames"), Slot + TEXT(".sav"));
    TArray<uint8> Bytes;
    if (!FFileHelper::LoadFileToArray(Bytes, *Path) ||
        Bytes.IsEmpty() || Bytes.Num() > 262144)
    {
        return false;
    }
    OutDigest = LexToString(FIoHash::HashBuffer(Bytes.GetData(),
        static_cast<uint64>(Bytes.Num())));
    return OutDigest.Len() == 40;
}

bool LoadBoundReviewContinueCandidate(const UWorld* World, const FString& Slot,
    UTSTSSSaveGame*& OutSave, UTSTSSReviewContinueManifest*& OutManifest,
    FString& OutDigest)
{
    OutSave = nullptr;
    OutManifest = nullptr;
    OutDigest.Reset();
    if (!World || World->WorldType != EWorldType::PIE ||
        Slot != ReviewPrimarySlot ||
        !UGameplayStatics::DoesSaveGameExist(Slot, 0) ||
        !UGameplayStatics::DoesSaveGameExist(ReviewManifestSlot, 0) ||
        !DigestExactReviewPrimary(Slot, OutDigest))
    {
        return false;
    }
    UTSTSSSaveGame* Save = UTSTSSPersistence::LoadProgress(Slot);
    UTSTSSReviewContinueManifest* Manifest =
        Cast<UTSTSSReviewContinueManifest>(
            UGameplayStatics::LoadGameFromSlot(ReviewManifestSlot, 0));
    if (!IsValid(Save) || !IsValid(Manifest) ||
        !Manifest->IsBoundFor(Save, Slot, BoundReviewProjectRoot(),
            BoundReviewMapPackage(World), OutDigest))
    {
        return false;
    }
    OutSave = Save;
    OutManifest = Manifest;
    return true;
}
#endif

#if WITH_EDITOR
// Provisional, unsaved harbor staging. The existing milestone actors retain
// all story authority; the ship and captain meshes are noncolliding review art.
void StageDockedWakeReview(UWorld* World)
{
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone || !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))
    {
        return;
    }

    ATSTSSMilestoneActor* Captain = nullptr;
    ATSTSSMilestoneActor* Board = nullptr;
    int32 CaptainCount = 0, BoardCount = 0;
    for (TActorIterator<ATSTSSMilestoneActor> It(World); It; ++It)
    {
        if (It->GetActorLabel() == TEXT("TSTSS_PRELUDE_REVIEW_IoniaHiring"))
        {
            Captain = *It;
            ++CaptainCount;
        }
        if (It->GetActorLabel() == TEXT("TSTSS_PRELUDE_REVIEW_AureateBoarding"))
        {
            Board = *It;
            ++BoardCount;
        }
    }
    UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (CaptainCount != 1 || BoardCount != 1 || !IsValid(Captain) ||
        !IsValid(Board) || !IsValid(Cube) || !IsValid(Sphere))
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_DOCKED_WAKE_REVIEW_HOLD markers_or_meshes"));
        return;
    }

    AAureateWakePreviewActor* Ship = World->SpawnActor<AAureateWakePreviewActor>(
        AAureateWakePreviewActor::StaticClass(), FVector(-900.f, 950.f, 70.f),
        FRotator::ZeroRotator);
    AActor* CaptainVisual = World->SpawnActor<AActor>(
        AActor::StaticClass(), FVector(-1250.f, 200.f, 0.f), FRotator::ZeroRotator);
    if (!IsValid(Ship) || !IsValid(CaptainVisual))
    {
        if (IsValid(Ship)) Ship->Destroy();
        if (IsValid(CaptainVisual)) CaptainVisual->Destroy();
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_DOCKED_WAKE_REVIEW_HOLD spawn"));
        return;
    }
    Ship->SetActorLabel(TEXT("TSTSS_DOCKED_WAKE_REVIEW_SHIP_PROXY"));
    Ship->SetActorScale3D(FVector(2.f));
    Ship->SetActorEnableCollision(false);
    CaptainVisual->SetActorLabel(TEXT("TSTSS_DOCKED_WAKE_REVIEW_IONIA_PROXY"));
    CaptainVisual->SetActorEnableCollision(false);
    USceneComponent* Root = NewObject<USceneComponent>(CaptainVisual, TEXT("CaptainVisualRoot"));
    CaptainVisual->AddInstanceComponent(Root);
    CaptainVisual->SetRootComponent(Root);
    Root->SetMobility(EComponentMobility::Movable);
    Root->RegisterComponent();
    // AActor had no root at spawn, so explicitly place the registered root.
    if (!CaptainVisual->SetActorLocation(FVector(-1250.f, 200.f, 0.f)))
    {
        Ship->Destroy();
        CaptainVisual->Destroy();
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_DOCKED_WAKE_REVIEW_HOLD captain_placement"));
        return;
    }
    UMaterialInterface* Coat = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/TSTSS_dark_iron.TSTSS_dark_iron"));
    UMaterialInterface* Hair = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/TSTSS/Review/MultipathV1/ObjectImports/HarborLantern/HarborLantern/Materials/TSTSS_brass.TSTSS_brass"));
    auto AddPart = [&](const TCHAR* Name, UStaticMesh* Mesh, const FVector& Location,
                       const FVector& Scale, UMaterialInterface* Material)
    {
        UStaticMeshComponent* Part = NewObject<UStaticMeshComponent>(CaptainVisual, FName(Name));
        Part->SetMobility(EComponentMobility::Movable);
        Part->SetupAttachment(Root);
        Part->SetStaticMesh(Mesh);
        if (IsValid(Material)) Part->SetMaterial(0, Material);
        Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        CaptainVisual->AddInstanceComponent(Part);
        Part->RegisterComponent();
        Part->SetRelativeLocation(Location);
        Part->SetRelativeScale3D(Scale);
    };
    // Human-shaped stand-in, not approved Ionia character art.
    AddPart(TEXT("Coat"), Cube, FVector(0, 0, 100), FVector(.42f, .24f, .90f), Coat);
    AddPart(TEXT("Head"), Sphere, FVector(0, 0, 166), FVector(.29f, .29f, .34f), nullptr);
    AddPart(TEXT("Hair"), Sphere, FVector(0, 0, 179), FVector(.31f, .31f, .22f), Hair);
    AddPart(TEXT("LegL"), Cube, FVector(0, -12, 31), FVector(.14f, .12f, .62f), Coat);
    AddPart(TEXT("LegR"), Cube, FVector(0, 12, 31), FVector(.14f, .12f, .62f), Coat);

    UStaticMeshComponent* Target = Cast<UStaticMeshComponent>(Board->GetRootComponent());
    const FVector OldCaptain = Captain->GetActorLocation();
    const FVector OldBoard = Board->GetActorLocation();
    if (!IsValid(Target) ||
        !Captain->SetActorLocation(FVector(-1250.f, 200.f, 90.f)) ||
        !Board->SetActorLocation(FVector(-900.f, 790.f, 90.f)))
    {
        Captain->SetActorLocation(OldCaptain);
        Board->SetActorLocation(OldBoard);
        Ship->Destroy();
        CaptainVisual->Destroy();
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_DOCKED_WAKE_REVIEW_HOLD relocation"));
        return;
    }
    Target->SetWorldScale3D(FVector(5.f, 2.6f, 1.6f));
    Captain->Tags.AddUnique(TEXT("TSTSS_DOCKED_WAKE_STAGED"));
    Board->Tags.AddUnique(TEXT("TSTSS_DOCKED_WAKE_STAGED"));
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_DOCKED_WAKE_REVIEW_APPLIED ship=proxy ionia=proxy saved_map_unchanged=1"));
}

// Source-scoped, disposable runtime engineering markers. The existing VS02
// ship interior has real deck/engine proxies but no authoritative E actors.
// Never save these transients to maps or elevate them to production room art.
void StageEarnedEngineRoomReview(UWorld* World, UTSTSSFirstWakeState* State,
    ATSTSSExplorerCharacter* Pawn)
{
    if (!World ||
        (World->WorldType != EWorldType::PIE &&
         World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone || !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) ||
        UGameplayStatics::GetCurrentLevelName(World, true) !=
            TEXT("VS02_AureateInteriors") ||
        !IsValid(State) || !State->HasStarted() || !IsValid(Pawn) ||
        (State->GetCurrentBeat() != ETSTSSFirstWakeBeat::BoardedAureateWake &&
         State->GetCurrentBeat() != ETSTSSFirstWakeBeat::EngineeringChecked))
    {
        return;
    }
    UStaticMesh* MarkerMesh = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (!IsValid(MarkerMesh))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_ENGINE_ROOM_REVIEW_HOLD missing marker mesh"));
        return;
    }
    struct FReviewMarkerPlacement
    {
        const TCHAR* Name;
        FVector Location;
        bool bInspection;
        ETSTSSInspectionStation Station;
        ETSTSSFirstWakeBeat Milestone;
    };
    // Never stage E targets inside the raised, solid Forecastle. The
    // original review ship has no approved stair/ramp up to its top:
    // Forecastle X=650..1250, Y=-400..400, Z=15..135 cm.
    // Keep reserve next to its physical gauge and the signoff on the
    // lower main deck, with a capsule-clear approach from the hatch.
    // These are provisional in-memory placements, NOT a ship room build.
    const FReviewMarkerPlacement Placements[] =
    {
        {TEXT("LiftStation"), FVector(-220.f, -90.f, 140.f), true,
         ETSTSSInspectionStation::Lift, ETSTSSFirstWakeBeat::BoardedAureateWake},
        {TEXT("PressureStation"), FVector(250.f, -90.f, 140.f), true,
         ETSTSSInspectionStation::Pressure, ETSTSSFirstWakeBeat::BoardedAureateWake},
        {TEXT("ReserveStation"), FVector(570.f, -180.f, 140.f), true,
         ETSTSSInspectionStation::Reserve, ETSTSSFirstWakeBeat::BoardedAureateWake},
        {TEXT("EngineeringApproval"), FVector(520.f, 130.f, 140.f), false,
         ETSTSSInspectionStation::Lift, ETSTSSFirstWakeBeat::EngineeringChecked}
    };
    // A single guarded arrival from boarding; no direct scene entry may
    // instantiate progression markers or manufacture the story handoff.
    TArray<ATSTSSMilestoneActor*> Spawned;
    FActorSpawnParameters Spawn;
    Spawn.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    for (const FReviewMarkerPlacement& Item : Placements)
    {
        ATSTSSMilestoneActor* Marker =
            World->SpawnActor<ATSTSSMilestoneActor>(
                Item.Location, FRotator::ZeroRotator, Spawn);
        if (!IsValid(Marker))
        {
            break;
        }
        Marker->SetActorLabel(FString::Printf(
            TEXT("TSTSS_ENGINEROOM_REVIEW_%s"), Item.Name));
        Marker->bIsInspectionStation = Item.bInspection;
        Marker->InspectionStation = Item.Station;
        Marker->Milestone = Item.Milestone;
        UStaticMeshComponent* Shape =
            Cast<UStaticMeshComponent>(Marker->GetRootComponent());
        if (!IsValid(Shape))
        {
            Marker->Destroy();
            break;
        }
        Shape->SetStaticMesh(MarkerMesh);
        Shape->SetWorldScale3D(FVector(0.7f, 0.7f, 1.4f));
        Spawned.Add(Marker);
    }
    if (Spawned.Num() != UE_ARRAY_COUNT(Placements))
    {
        for (ATSTSSMilestoneActor* Marker : Spawned)
        {
            if (IsValid(Marker)) Marker->Destroy();
        }
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_ENGINE_ROOM_REVIEW_HOLD incomplete marker stage"));
        return;
    }
    // Current VS02 PlayerStart intersects the solid BridgeDeck; reposition
    // only the successfully earned PIE arrival to a collision-clear hatch
    // staging spot on the existing MainWalkableDeck. This is NOT a finished
    // physical doorway and must be audited before art acceptance.
    if (!Pawn->SetActorLocation(FVector(-350.f, -90.f, 140.f),
            false, nullptr, ETeleportType::TeleportPhysics))
    {
        for (ATSTSSMilestoneActor* Marker : Spawned)
        {
            if (IsValid(Marker)) Marker->Destroy();
        }
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_ENGINE_ROOM_REVIEW_HOLD player hatch spawn"));
        return;
    }
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_ENGINE_ROOM_REVIEW_STAGED count=4 beat=%d mask=%u save_mutation=0"),
        static_cast<int32>(State->GetCurrentBeat()), State->GetInspectionMask());
}

#endif
}

ATSTSSExplorerCharacter::ATSTSSExplorerCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
#if !UE_BUILD_SHIPPING
    // Lightweight fall rescue only in four explicitly scoped review maps.
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.2f;
#endif
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(GetRootComponent());
    CameraBoom->TargetArmLength = 360.f;
    CameraBoom->bUsePawnControlRotation = true;
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
}

void ATSTSSExplorerCharacter::BeginPlay()
{
    Super::BeginPlay();
    FirstWakeState = NewObject<UTSTSSFirstWakeState>(this);
#if WITH_EDITOR
    ApplyOpticalReviewPlayerExposure(GetWorld(), FollowCamera);
    bTryHilltoniaOpening = ApplyV5HarborReviewLookdev(GetWorld());
    SetupFirstWakeThirdPersonReview(GetWorld());
    StageDockedWakeReview(GetWorld());
    ApplyCoastalRecoveryReviewSignage(GetWorld());
    ApplySeabourneReviewExposure(GetWorld());
    if (UWorld* World = GetWorld())
    {
        if (UGameInstance* GameInstance = World->GetGameInstance())
        {
            if (UTSTSSReviewShoreTravelSubsystem* Travel =
                    GameInstance->GetSubsystem<UTSTSSReviewShoreTravelSubsystem>())
            {
                if (Travel->ConsumeShoreArrival(World, FirstWakeState))
                {
                    UE_LOG(LogTemp, Display,
                        TEXT("TSTSS_FIRSTWAKE_REVIEW_SCENE_ARRIVAL_STORY_RESTORED_NO_RECRUITMENT beat=%d"),
                        static_cast<int32>(FirstWakeState->GetCurrentBeat()));
                    const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
                    // Only a real queued boarding ticket stages E interactions
                    // in the existing VS02 ship room. No harbor-side mechanic
                    // can replace these interactions or grant inspection bits.
                    if (Scene == TEXT("VS02_AureateInteriors"))
                    {
                        StageEarnedEngineRoomReview(World, FirstWakeState, this);
                    }
                    // Only an earned in-memory arrival ticket reveals the
                    // optional optical study; a direct level launch gets none.
                    if (GEngine &&
                        FirstWakeState->GetCurrentBeat() ==
                            ETSTSSFirstWakeBeat::BoardedAureateWake &&
                        Scene == TEXT("VS02_AureateInteriors"))
                    {
                        GEngine->AddOnScreenDebugMessage(-1, 12.f, FColor::Cyan,
                            TEXT("Aureate engine room: inspect LIFT, pressure and reserves [E], then sign off"));
                    }
                    if (FirstWakeState->GetCurrentBeat() ==
                            ETSTSSFirstWakeBeat::EngineeringChecked && GEngine)
                    {
                        if (Scene == TEXT("VS02_AureateInteriors"))
                        {
                            GEngine->AddOnScreenDebugMessage(-1, 10.f, FColor::Cyan,
                                TEXT("Engine room [C] LIFT camera near gauge | [K] launches | [O] dev optical lab"));
                        }
                        else if (Scene == TEXT("M_EnginePresentationReview"))
                        {
                            GEngine->AddOnScreenDebugMessage(-1, 12.f, FColor::Cyan,
                                TEXT("Engine optics: approach LIFT, press [C] for 4s | [K] launches"));
                        }
                    }
                    if (Scene == TEXT("VS03_FirstWakeSky") ||
                        Scene == TEXT("VS04_SplashdownSea"))
                    {
                        // Both scene-review levels have no PlayerStart or walkable
                        // route. Use a temporary observer pawn, not canonical flight.
                        GetCharacterMovement()->SetMovementMode(MOVE_Flying);
                        SetActorLocation(Scene == TEXT("VS03_FirstWakeSky")
                            ? FVector(-1600.f, -2300.f, 1000.f)
                            : FVector(-1800.f, -2800.f, 950.f));
                        if (Controller)
                        {
                            Controller->SetControlRotation(FRotator(-12.f, 55.f, 0.f));
                        }
                    }
                    else if (Scene == TEXT("VS05_DenithFuelShanty") &&
                        FirstWakeState->GetCurrentBeat() ==
                            ETSTSSFirstWakeBeat::FlotationConfirmed)
                    {
                        // The native fuel-shanty map is scenery only. Add one
                        // review interaction at the player's spawn, requiring E
                        // before K may advance to the published shoreline.
                        ATSTSSMilestoneActor* Reserve =
                            World->SpawnActor<ATSTSSMilestoneActor>(
                                FVector(-1430.f, -140.f, 180.f),
                                FRotator::ZeroRotator);
                        UStaticMesh* ReviewCube = LoadObject<UStaticMesh>(
                            nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
                        if (IsValid(Reserve) && IsValid(ReviewCube))
                        {
                            Reserve->SetActorLabel(
                                TEXT("TSTSS_SPLASHDOWN_GREYBOX_EmptyReserveMarker"));
                            Reserve->Milestone = ETSTSSFirstWakeBeat::EmptyReserveInspected;
                            UStaticMeshComponent* Shape =
                                Reserve->FindComponentByClass<UStaticMeshComponent>();
                            if (IsValid(Shape))
                            {
                                Shape->SetStaticMesh(ReviewCube);
                                Shape->SetWorldScale3D(FVector(1.2f));
                            }
                            if (ATextRenderActor* Sign = World->SpawnActor<ATextRenderActor>(
                                    FVector(-1490.f, -230.f, 330.f),
                                    FRotator::ZeroRotator))
                            {
                                Sign->SetActorLabel(TEXT("TSTSS_REVIEW_ReserveCheckNotice"));
                                Sign->GetTextRender()->SetText(
                                    FText::FromString(TEXT("SHIP SYSTEMS  |  Inspect [E]")));
                            }
                        }
                        else if (IsValid(Reserve))
                        {
                            Reserve->Destroy();
                        }
                    }
                }
            }
        }
    }
#endif
#if WITH_EDITOR
    // Bind any scene-authored Aureate Wake preview actor to the SAME story
    // instance restored through review shoreline travel. No new ship spawn,
    // asset promotion or synthetic water-contact event is introduced.
    if (UWorld* ReviewWorld = GetWorld())
    {
        if ((ReviewWorld->WorldType == EWorldType::PIE ||
             ReviewWorld->WorldType == EWorldType::Game) &&
            ReviewWorld->GetNetMode() == NM_Standalone &&
            ReviewWorld->GetOutermost() &&
            ReviewWorld->GetOutermost()->GetName().Contains(TEXT("/TSTSS/Review/")))
        {
            for (TActorIterator<AAureateWakePreviewActor> Ship(ReviewWorld); Ship; ++Ship)
            {
                if (IsValid(*Ship) && Ship->BindReviewStory(FirstWakeState))
                {
                    UE_LOG(LogTemp, Display,
                        TEXT("TSTSS_AUREATE_REVIEW_STORY_BIND form=%d beat=%d"),
                        static_cast<int32>(Ship->GetCurrentForm()),
                        static_cast<int32>(FirstWakeState->GetCurrentBeat()));
                }
            }
        }
    }
#endif
    bPIEReviewQuickSlotOwned = false;
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
    ShowObjectiveReview();
}

#if !UE_BUILD_SHIPPING
bool ATSTSSExplorerCharacter::HasSupportedReviewFooting(
    const UWorld* World, const FVector& PawnLocation) const
{
    if (!World || PawnLocation.ContainsNaN()) return false;
    // A center-only contact can record an unsafe anchor right on the edge.
    // Require support under the center and four capsule-adjacent points.
    constexpr float RadiusCm = 35.f;
    const FVector Offsets[] = {
        FVector::ZeroVector,
        FVector(RadiusCm, 0.f, 0.f),
        FVector(-RadiusCm, 0.f, 0.f),
        FVector(0.f, RadiusCm, 0.f),
        FVector(0.f, -RadiusCm, 0.f)
    };
    const FCollisionObjectQueryParams Objects(ECC_WorldStatic);
    const FCollisionQueryParams Query(SCENE_QUERY_STAT(TSTSSReviewSupportedFloor), false, this);
    for (const FVector& Offset : Offsets)
    {
        FHitResult Hit;
        if (!World->LineTraceSingleByObjectType(
                Hit, PawnLocation + Offset + FVector(0.f, 0.f, 15.f),
                PawnLocation + Offset - FVector(0.f, 0.f, 160.f),
                Objects, Query) ||
            !Hit.bBlockingHit || Hit.ImpactNormal.Z < 0.7f)
        {
            return false;
        }
    }
    return true;
}
#endif

void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
    UWorld* World = GetWorld();
    if (!World || (World->WorldType != EWorldType::PIE &&
                   World->WorldType != EWorldType::Game) ||
        !IsPlayerControlled())
    {
        return;
    }
    // Reject same-named production maps outside the explicit review namespace.
    const bool bReviewNamespace = World->GetOutermost() &&
        World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/"));
    const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
#if WITH_EDITOR
    if (bTryHilltoniaOpening)
    {
        bTryHilltoniaOpening = false;
        StartHilltoniaOpening(World);
    }
    if (bFirstWakeBokehReview)
    {
        UpdateFirstWakeBokehReview(DeltaSeconds);
    }
    if (bHilltoniaFlyerRead && !IsHilltoniaFlyerOpen())
    {
        DeclineHilltoniaFlyer();
    }
    // Only scoped review worlds advertise live interaction. Visual refresh
    // reads the authoritative state; it cannot advance or save a story beat.
    if (bReviewNamespace && World->GetNetMode() == NM_Standalone &&
        (Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview") ||
         Scene == TEXT("VS02_AureateInteriors") ||
         Scene == TEXT("VS05_DenithFuelShanty")))
    {
        for (TActorIterator<ATSTSSMilestoneActor> It(World); It; ++It)
        {
            It->UpdateReviewBeacon(FirstWakeState);
        }
        if (Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview"))
        {
            // Obsolete always-on captions obscure the actual next marker.
            // Keep actor bytes in the saved map and hide only this runtime.
            for (TActorIterator<ATextRenderActor> It(World); It; ++It)
            {
                if (It->GetActorLabel().StartsWith(
                        TEXT("TSTSS_PRELUDE_REVIEW_SIGN_")))
                {
                    It->SetActorHiddenInGame(true);
                }
            }
        }
    }
#endif
    if (!bReviewNamespace || !TSTSSReviewGrounding::IsWalkableReviewMap(Scene)) return;
    UCharacterMovementComponent* Movement = GetCharacterMovement();
    if (!Movement) return;

    const FVector Current = GetActorLocation();
#if WITH_EDITOR
    // Evidence from the real player's movement, never a scripted teleport.
    // Only instrument the exact standalone V5 review map and landward area.
    // Checkpoint entry and two-second heartbeat logs are read-only and do
    // not modify collision, gameplay, save data or story progression.
    if (bReviewNamespace && World->GetNetMode() == NM_Standalone &&
        Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview") &&
        TSTSSHilltoniaRouteTelemetry::IsScopedRouteRegion(Current))
    {
        const TCHAR* RouteWaypoint =
            TSTSSHilltoniaRouteTelemetry::NearestWaypoint(Current);
        const FName CurrentWaypoint = RouteWaypoint ? FName(RouteWaypoint) : NAME_None;
        const float Now = World->GetTimeSeconds();
        const bool bNewWaypoint = CurrentWaypoint != NAME_None &&
            CurrentWaypoint != LastHilltoniaProbeWaypoint;
        const bool bHeartbeat = Now >= NextHilltoniaProbeTimeSeconds;
        if (bNewWaypoint || bHeartbeat)
        {
            const bool bGrounded = Movement->IsMovingOnGround();
            const bool bFivePointFooting = bGrounded &&
                HasSupportedReviewFooting(World, Current);
            if (bNewWaypoint)
            {
                UE_LOG(LogTemp, Display,
                    TEXT("TSTSS_HILLTONIA_ROUTE_WAYPOINT map=V5 name=%s time=%.2f x=%.1f y=%.1f z=%.1f grounded=%d footing=%d"),
                    RouteWaypoint, Now, Current.X, Current.Y, Current.Z,
                    bGrounded ? 1 : 0, bFivePointFooting ? 1 : 0);
            }
            if (bHeartbeat)
            {
                UE_LOG(LogTemp, Display,
                    TEXT("TSTSS_HILLTONIA_ROUTE_SAMPLE map=V5 name=%s time=%.2f x=%.1f y=%.1f z=%.1f grounded=%d footing=%d"),
                    RouteWaypoint ? RouteWaypoint : TEXT("UNMARKED"),
                    Now, Current.X, Current.Y, Current.Z,
                    bGrounded ? 1 : 0, bFivePointFooting ? 1 : 0);
                NextHilltoniaProbeTimeSeconds = Now + 2.f;
            }
        }
        LastHilltoniaProbeWaypoint = CurrentWaypoint;
    }
    else
    {
        LastHilltoniaProbeWaypoint = NAME_None;
    }
#endif
    if (Movement->IsMovingOnGround() &&
        HasSupportedReviewFooting(World, Current))
    {
        LastSupportedReviewLocation = Current;
        bHasSupportedReviewLocation = true;
    }
    if (!TSTSSReviewGrounding::ShouldRecover(
            bReviewNamespace, Scene, bHasSupportedReviewLocation,
            Movement->IsFalling(), Current, LastSupportedReviewLocation))
    {
        return;
    }

    FVector Candidate = LastSupportedReviewLocation + FVector(0.f, 0.f, 15.f);
    if (!World->FindTeleportSpot(this, Candidate, GetActorRotation()) ||
        FVector::Dist(Candidate, LastSupportedReviewLocation) > 80.f ||
        !TeleportTo(Candidate, GetActorRotation(), false, false))
    {
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_REVIEW_FALL_RETURN_REJECT map=%s from=%s"),
            *Scene, *Current.ToCompactString());
        return;
    }

    Movement->StopMovementImmediately();
    Movement->SetMovementMode(MOVE_Walking);
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_REVIEW_FALL_RETURN map=%s from=%s to=%s story_unchanged=1"),
        *Scene, *Current.ToCompactString(), *GetActorLocation().ToCompactString());
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Cyan,
            TEXT("Review: returned to the last supported walkway"));
    }
#endif
}

// Present the discoverable optical action without adding a sixth editor-only
// diagnostic branch to the existing first-wake E interaction path.
static void ShowOptionalEngineFocusHint(const UWorld* World, bool bInspection)
{
#if WITH_EDITOR
    if (World && World->WorldType == EWorldType::PIE
        && bInspection && GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 6.f, FColor::Cyan,
            TEXT("Engine inspection: press C near the LIFT instrument for a 4s focus view"));
    }
#else
    (void)World;
    (void)bInspection;
#endif
}

void ATSTSSExplorerCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
#if WITH_EDITOR
    RestoreEngineFocusPreview();
#endif
    Super::EndPlay(EndPlayReason);
}

#if WITH_EDITOR
void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()
{
    // Explicit review-only camera cut; never an E-interaction consequence.
    // The production explorer and its camera are unchanged unless the player presses C.
    UWorld* World = GetWorld();
    if (!World || World->WorldType != EWorldType::PIE || !IsValid(FirstWakeState))
    {
        return;
    }
    if (EngineFocusPreviewCamera.IsValid())
    {
        RestoreEngineFocusPreview();
        return;
    }

    const auto Warn = [](const TCHAR* Message)
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Yellow, Message);
        }
    };

    APlayerController* PC = Cast<APlayerController>(Controller);
    if (!IsValid(PC) || PC != UGameplayStatics::GetPlayerController(World, 0)
        || PC->GetViewTarget() != this || PC->IsMoveInputIgnored()
        || PC->IsLookInputIgnored())
    {
        // Passive, editor-only diagnostic: do not steal a camera, alter input,
        // or bypass the review-only state guard.
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE denied=controller_or_input_owner"));
        Warn(TEXT("Engine view unavailable: player camera is already owned"));
        return;
    }

    // The actual VS02 gauge is the only acceptable focus target.
    // No runtime duplication of story markers or fabrication of first-wake state.
    AActor* Instrument = nullptr;
    int32 InstrumentCount = 0;
    ATSTSSAtmosphereDirector* Atmosphere = nullptr;
    int32 AtmosphereCount = 0;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        AActor* Actor = *It;
        if (!IsValid(Actor)) continue;
        if (Actor->GetActorLabel() ==
            TEXT("TSTSS_VS_REVIEW_InstrumentCore_LIFT"))
        {
            Instrument = Actor;
            ++InstrumentCount;
        }
        if (ATSTSSAtmosphereDirector* Director =
                Cast<ATSTSSAtmosphereDirector>(Actor))
        {
            Atmosphere = Director;
            ++AtmosphereCount;
        }
    }
    const FVector ReviewPawnLocation = GetActorLocation();
    const FVector ReviewGaugeLocation = IsValid(Instrument)
        ? Instrument->GetActorLocation() : FVector::ZeroVector;
    const float ReviewGaugeDistanceCm = IsValid(Instrument)
        ? FVector::Dist(ReviewPawnLocation, ReviewGaugeLocation) : -1.f;
    // The same real PIE player and existing native gauge used by the guard
    // below. This is a read-only diagnostic before any cinematic mutation.
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE pawn_x=%.1f pawn_y=%.1f pawn_z=%.1f gauge_x=%.1f gauge_y=%.1f gauge_z=%.1f distance_cm=%.1f limit_cm=450.0 gauge_count=%d sky_count=%d"),
        ReviewPawnLocation.X, ReviewPawnLocation.Y, ReviewPawnLocation.Z,
        ReviewGaugeLocation.X, ReviewGaugeLocation.Y, ReviewGaugeLocation.Z,
        ReviewGaugeDistanceCm, InstrumentCount, AtmosphereCount);
    if (InstrumentCount != 1 || AtmosphereCount != 1
        || !IsValid(Instrument) || !IsValid(Atmosphere)
        || FVector::Dist(GetActorLocation(), Instrument->GetActorLocation()) > 450.f)
    {
        // Show actionable, measured distance when the real LIFT exists;
        // never blame navigation if an actual review-map authority is missing.
        if (InstrumentCount == 1 && AtmosphereCount == 1
            && IsValid(Instrument) && IsValid(Atmosphere)
            && FMath::IsFinite(ReviewGaugeDistanceCm)
            && ReviewGaugeDistanceCm > 450.f)
        {
            if (GEngine)
            {
                GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Yellow,
                    FString::Printf(
                        TEXT("LIFT inspection: %.1f m away - move within 4.5 m and press C"),
                        ReviewGaugeDistanceCm / 100.f));
            }
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE denied=too_far distance_cm=%.1f limit_cm=450.0"),
                ReviewGaugeDistanceCm);
        }
        else
        {
            UE_LOG(LogTemp, Display,
                TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE denied=missing_native_lift_or_sky"));
            Warn(TEXT("Engine view unavailable: LIFT or sky authority missing"));
        }
        return;
    }
    UTSTSSPresentationCoordinatorSubsystem* Coordinator =
        World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>();
    if (!IsValid(Coordinator))
    {
        Warn(TEXT("Engine view unavailable: no presentation coordinator"));
        return;
    }
    const bool bWasEnabled = Coordinator->IsReviewEnabled();
    // This PIE-only preview may borrow an enabled-but-neutral coordinator.
    // It must NEVER republish over a valid shot already owned by another
    // cinematic consumer. No lease exists for forcefully taking that intent.
    if (bWasEnabled && Coordinator->GetCurrentIntent().bEligible)
    {
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE denied=cinematic_owner"));
        Warn(TEXT("Engine view held: another cinematic shot already owns presentation"));
        return;
    }
    // Validate lens geometry BEFORE publishing presentation intent.
    // A nonfinite/off-scene anchor must never leave a borrowed coordinator
    // with an eligible cue when no camera can be created.
    const FVector Target = Instrument->GetActorLocation();
    // Provisional optical camera framing from isolated VS02 lookdev; not approved art.
    // Approach the LIFT from its clear rail-facing side.
    const FVector Location = Target + FVector(-380.f, 650.f, 260.f);
    const float FocusCm = FVector::Dist(Location, Target);
    if (!FMath::IsFinite(FocusCm) || FocusCm < 65.f || FocusCm > 12000.f)
    {
        Warn(TEXT("Engine view held: invalid native instrument focus anchor"));
        return;
    }
    if (!bWasEnabled)
    {
        Coordinator->SetReviewEnabled(true);
    }
    const FTSTSSPresentationIntent Intent = Coordinator->TryPublishMoment(
        FirstWakeState, Atmosphere, ETSTSSPresentationMoment::EngineInspection,
        /*bReducedMotion=*/false, /*bGameplayClarityOverride=*/false);
    if (!Intent.bEligible || !Intent.bAllowCinematicFocus
        || !Intent.bAllowFocusRack || Intent.bRequireDeepFocus
        || Intent.ShotId != FName(TEXT("FW03_Engine_Inspection")))
    {
        if (!bWasEnabled) Coordinator->SetReviewEnabled(false);
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE denied=story_weather_access"));
        Warn(TEXT("Engine view held: first-wake story/weather/access gate"));
        return;
    }

    // Technically verified 65 mm f/2.8 lens; native gameplay look still unapproved.
    FActorSpawnParameters Spawn;
    Spawn.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    ACineCameraActor* Camera = World->SpawnActor<ACineCameraActor>(
        Location, (Target - Location).Rotation(), Spawn);
    if (!IsValid(Camera) || !IsValid(Camera->GetCineCameraComponent()))
    {
        if (IsValid(Camera)) Camera->Destroy();
        if (!bWasEnabled)
        {
            Coordinator->SetReviewEnabled(false);
        }
        else
        {
            // Borrowed coordinators must remain enabled, but our accepted
            // engine shot cannot survive a failed native camera spawn.
            // Do not reset a different shot if ownership changed meanwhile.
            const FTSTSSPresentationIntent Current =
                Coordinator->GetCurrentIntent();
            if (Current.bEligible
                && Current.ShotId == FName(TEXT("FW03_Engine_Inspection")))
            {
                Coordinator->ResetReviewIntent();
            }
        }
        Warn(TEXT("Engine view unavailable: no native Cine Camera"));
        return;
    }
    Camera->SetActorLabel(TEXT("TSTSS_GAMEPLAY_ENGINE_FOCUS_PREVIEW_ONLY"));
    UCineCameraComponent* Cine = Camera->GetCineCameraComponent();
    Cine->SetCurrentFocalLength(65.f);
    Cine->SetCurrentAperture(2.8f);
    FCameraFocusSettings Settings = Cine->FocusSettings;
    Settings.FocusMethod = ECameraFocusMethod::Manual;
    Settings.ManualFocusDistance = FocusCm;
    Settings.bSmoothFocusChanges = true;
    Settings.FocusSmoothingInterpSpeed = 2.f;
#if WITH_EDITORONLY_DATA
    Settings.bDrawDebugFocusPlane = false;
#endif
    Cine->SetFocusSettings(Settings);
    // Draft Neontic D3D12 fixed look; the 17h Lit review otherwise clips to white.
    // Weather/time and accessibility acceptance are still NOT established.
    Cine->PostProcessSettings.bOverride_AutoExposureBias = true;
    Cine->PostProcessSettings.AutoExposureBias = -6.f;
    Cine->PostProcessBlendWeight = 1.f;

    // Explicit, reversible 4 s preview. The player pawn stays at its
    // original location, and existing movement/look ignore values are
    // refused above rather than overwritten.
    EngineFocusPreviewCamera = Camera;
    EngineFocusPreviewController = PC;
    bEngineFocusPreviewOwnsCoordinatorEnable = !bWasEnabled;
    bEngineFocusPreviewIgnoredMove = true;
    bEngineFocusPreviewIgnoredLook = true;
    EngineFocusPreviewStartedSeconds = FPlatformTime::Seconds();
    EngineFocusPreviewDeadlineSeconds = EngineFocusPreviewStartedSeconds + 4.0;
    PC->SetIgnoreMoveInput(true);
    PC->SetIgnoreLookInput(true);
    PC->SetViewTargetWithBlend(Camera, 0.35f, VTBlend_EaseInOut, 2.f);
    GetWorldTimerManager().SetTimer(EngineFocusPreviewGuardTimer, this,
        &ATSTSSExplorerCharacter::VerifyEngineFocusPreview, 0.2f, true);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 4.f, FColor::Cyan,
            TEXT("LIFT inspection view - press C to return (auto return 4s)"));
    }
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER focus_cm=%.1f gauge_distance_cm=%.1f preview_limit_s=4.0 move_ignored=%d look_ignored=%d"),
        FocusCm, ReviewGaugeDistanceCm,
        PC->IsMoveInputIgnored() ? 1 : 0,
        PC->IsLookInputIgnored() ? 1 : 0);
}

void ATSTSSExplorerCharacter::VerifyEngineFocusPreview()
{
    const UWorld* World = GetWorld();
    APlayerController* PC = EngineFocusPreviewController.Get();
    ACineCameraActor* Camera = EngineFocusPreviewCamera.Get();
    UTSTSSPresentationCoordinatorSubsystem* Coordinator = World
        ? World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>() : nullptr;
    if (!World || World->WorldType != EWorldType::PIE
        || !IsValid(PC) || !IsValid(Camera)
        // A blend can still report the pawn as view target momentarily.
        // Do not destroy the camera midway through its entry transition.
        || (FPlatformTime::Seconds() - EngineFocusPreviewStartedSeconds > 0.75
            && PC->GetViewTarget() != Camera)
        || FPlatformTime::Seconds() >= EngineFocusPreviewDeadlineSeconds
        || !IsValid(Coordinator)
        || !Coordinator->GetCurrentIntent().bEligible
        || !Coordinator->GetCurrentIntent().bAllowCinematicFocus
        || Coordinator->GetCurrentIntent().ShotId !=
            FName(TEXT("FW03_Engine_Inspection")))
    {
        RestoreEngineFocusPreview();
    }
}

void ATSTSSExplorerCharacter::RestoreEngineFocusPreview()
{
    const bool bHadPreview = EngineFocusPreviewCamera.IsValid()
        || bEngineFocusPreviewIgnoredMove || bEngineFocusPreviewIgnoredLook;
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(EngineFocusPreviewGuardTimer);
    }
    APlayerController* PC = EngineFocusPreviewController.Get();
    ACineCameraActor* Camera = EngineFocusPreviewCamera.Get();
    // If the transition is still entering, UE may report the pawn as
    // CurrentViewTarget even though the review camera is still pending.
    // Reasserting the pawn with a zero-duration blend cancels that pending
    // transition. NEVER steal a view already owned by a third-party actor.
    if (IsValid(PC))
    {
        if (IsValid(Camera) && PC->GetViewTarget() == Camera)
        {
            PC->SetViewTargetWithBlend(this, 0.3f, VTBlend_EaseInOut, 2.f);
        }
        else if (IsValid(Camera) && PC->GetViewTarget() == this)
        {
            PC->SetViewTargetWithBlend(this, 0.f);
        }
        if (bEngineFocusPreviewIgnoredMove) PC->SetIgnoreMoveInput(false);
        if (bEngineFocusPreviewIgnoredLook) PC->SetIgnoreLookInput(false);
    }
    if (IsValid(Camera))
    {
        // Retain the temporary camera until the return blend finishes.
        Camera->SetLifeSpan(0.6f);
    }
    if (bEngineFocusPreviewOwnsCoordinatorEnable)
    {
        if (UWorld* World = GetWorld())
        {
            if (UTSTSSPresentationCoordinatorSubsystem* Coordinator =
                    World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>())
            {
                // Never shut off another presentation source's eligible
                // shot if it superseded our inspection while the preview ran.
                const FTSTSSPresentationIntent Current =
                    Coordinator->GetCurrentIntent();
                if (!Current.bEligible
                    || Current.ShotId == FName(TEXT("FW03_Engine_Inspection")))
                {
                    Coordinator->SetReviewEnabled(false);
                }
            }
        }
    }
    else if (bHadPreview)
    {
        if (UWorld* World = GetWorld())
        {
            if (UTSTSSPresentationCoordinatorSubsystem* Coordinator =
                    World->GetSubsystem<UTSTSSPresentationCoordinatorSubsystem>())
            {
                if (Coordinator->GetCurrentIntent().ShotId ==
                        FName(TEXT("FW03_Engine_Inspection")))
                {
                    // A pre-enabled coordinator remains enabled but the expired
                    // inspection must not leak after the player returns.
                    Coordinator->ResetReviewIntent();
                }
            }
        }
    }
    // Capture the state after releasing only the input locks we owned.
    // A pawn-view target can still be blending back for 0.3s here; this
    // does NOT assert final rendered camera ownership or physical movement.
    if (bHadPreview)
    {
        const double ElapsedSeconds = EngineFocusPreviewStartedSeconds > 0.
            ? FPlatformTime::Seconds() - EngineFocusPreviewStartedSeconds : -1.;
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT elapsed_s=%.3f move_ignored=%d look_ignored=%d immediate_view_pawn=%d controller_valid=%d"),
            ElapsedSeconds,
            IsValid(PC) && PC->IsMoveInputIgnored() ? 1 : 0,
            IsValid(PC) && PC->IsLookInputIgnored() ? 1 : 0,
            IsValid(PC) && PC->GetViewTarget() == this ? 1 : 0,
            IsValid(PC) ? 1 : 0);
    }
    EngineFocusPreviewCamera.Reset();
    EngineFocusPreviewController.Reset();
    bEngineFocusPreviewOwnsCoordinatorEnable = false;
    bEngineFocusPreviewIgnoredMove = false;
    bEngineFocusPreviewIgnoredLook = false;
    EngineFocusPreviewStartedSeconds = 0.;
    EngineFocusPreviewDeadlineSeconds = 0.;
    if (bHadPreview)
    {
        UE_LOG(LogTemp, Display, TEXT("TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE"));
    }
}
#endif // WITH_EDITOR

#if WITH_EDITOR
void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(UWorld* World)
{
    if (!World || !IsValid(FollowCamera) || !IsValid(CameraBoom) ||
        (World->WorldType != EWorldType::PIE && World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone || !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")))
    {
        return;
    }
    const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
    if (Scene != TEXT("FirstWake_PreludeInteraction_V5_VisualReview") &&
        Scene != TEXT("VS02_AureateInteriors"))
    {
        return;
    }

    // Reuse the existing possession, movement, smart boom collision and E ray.
    const bool bInteriors = Scene == TEXT("VS02_AureateInteriors");
    CameraBoom->TargetArmLength = bInteriors ? 340.f : 480.f;
    CameraBoom->TargetOffset = FVector(0.f, 0.f, bInteriors ? 45.f : 35.f);
    CameraBoom->SocketOffset = FVector(0.f, 48.f, 12.f);
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 13.f;
    CameraBoom->CameraLagMaxDistance = 55.f;
    FollowCamera->SetFieldOfView(bInteriors ? 70.f : 68.f);
    bFirstWakeThirdPersonReview = true;

    // A possessed skeletal Ender review candidate takes precedence over the
    // historical static V2 lookdev overlay. A separate Blueprint may already
    // have bound the skeletal body; adding a second opaque static character
    // would hide it and make actual locomotion/rig assessment impossible.
    // This only selects presentation, never art admission or animation proof.
    USkeletalMeshComponent* SkeletalBody = GetMesh();
    if (IsValid(SkeletalBody) && SkeletalBody->IsRegistered() &&
        IsValid(SkeletalBody->GetSkeletalMeshAsset()) &&
        SkeletalBody->GetNumBones() > 0 && SkeletalBody->IsVisible())
    {
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_ENDER_SKELETAL_REVIEW_PRESENT scene=%s bones=%d animation_NOT_VERIFIED art_NOT_APPROVED"),
            *Scene, SkeletalBody->GetNumBones());
        return;
    }

    // Local Ender V2 look-development package. Keep the donor and its materials
    // at their original package paths, outside tracked Content on Neontic.
    constexpr const TCHAR* PackageRoot = TEXT("/Game/ArtLookdev/Characters/EnderFidelityV2/");
    const FString MeshPackage =
        TEXT("/Game/ArtLookdev/Characters/EnderFidelityV2/Ender_ender_fidelity_v2/StaticMeshes/Ender_ender_fidelity_v2");
    const FString MeshPath = MeshPackage + TEXT(".Ender_ender_fidelity_v2");
    const FString LocalPath = FPaths::ConvertRelativePathToFull(
        FPaths::ProjectSavedDir() / TEXT("FirstWakeEnderReview/EnderFidelityV2/"));
    static bool bMountedEnderReview = false;
    if (!bMountedEnderReview && FPaths::DirectoryExists(LocalPath))
    {
        FPackageName::RegisterMountPoint(PackageRoot, LocalPath);
        bMountedEnderReview = true;
    }
    UStaticMesh* Body = FPackageName::DoesPackageExist(MeshPackage)
        ? LoadObject<UStaticMesh>(nullptr, *MeshPath) : nullptr;
    if (!IsValid(Body))
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_ENDER_THIRD_PERSON_HOLD missing local Ender review mesh"));
        return;
    }
    const FBox Bounds = Body->GetBoundingBox();
    const double Height = Bounds.GetSize().Z;
    if (!Bounds.IsValid || !FMath::IsFinite(Height) || Height < 1.f || Height > 1000.f)
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_ENDER_THIRD_PERSON_HOLD invalid body bounds"));
        return;
    }
    const double Scale = 176.0 / Height;
    // This import faces +Y; match the controlled pawn's +X forward.
    const FRotator BodyYaw(0.f, -90.f, 0.f);
    const FVector FootCenter(Bounds.GetCenter().X, Bounds.GetCenter().Y, Bounds.Min.Z);
    auto* Visual = NewObject<UStaticMeshComponent>(this, TEXT("EnderFirstWakeReviewBody"));
    Visual->SetMobility(EComponentMobility::Movable);
    Visual->SetStaticMesh(Body);
    Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Visual->SetGenerateOverlapEvents(false);
    Visual->SetupAttachment(GetRootComponent());
    Visual->SetRelativeRotation(BodyYaw);
    Visual->SetRelativeScale3D(FVector(Scale));
    Visual->SetRelativeLocation(
        FVector(0.f, 0.f, -GetCapsuleComponent()->GetScaledCapsuleHalfHeight()) -
        BodyYaw.RotateVector(FootCenter * Scale));
    AddInstanceComponent(Visual);
    Visual->RegisterComponent();
    UE_LOG(LogTemp, Display, TEXT("TSTSS_ENDER_THIRD_PERSON_READY scene=%s source_height_cm=%.1f review_height_cm=176 static_lookdev=1"),
        *Scene, Height);
}

void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()
{
    if (!bFirstWakeThirdPersonReview || !FollowCamera || IsHilltoniaFlyerOpen() ||
        EngineFocusPreviewCamera.IsValid())
    {
        return;
    }
    bFirstWakeBokehReview = !bFirstWakeBokehReview;
    FPostProcessSettings& Lens = FollowCamera->PostProcessSettings;
    Lens.bOverride_DepthOfFieldEnabled = bFirstWakeBokehReview;
    Lens.DepthOfFieldEnabled = true;
    Lens.bOverride_DepthOfFieldSensorWidth = bFirstWakeBokehReview;
    Lens.DepthOfFieldSensorWidth = 48.f;
    Lens.bOverride_DepthOfFieldFocalDistance = bFirstWakeBokehReview;
    Lens.bOverride_DepthOfFieldFstop = bFirstWakeBokehReview;
    Lens.bOverride_DepthOfFieldBladeCount = bFirstWakeBokehReview;
    Lens.DepthOfFieldBladeCount = 9;
    if (bFirstWakeBokehReview)
    {
        FirstWakeReviewFstop = 9.f;
        UpdateFirstWakeBokehReview(0.f);
    }
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 3.f, FColor::Cyan,
            bFirstWakeBokehReview ? TEXT("Cinematic focus on [B]") : TEXT("Cinematic focus off [B]"));
    }
    UE_LOG(LogTemp, Display, TEXT("TSTSS_FIRST_WAKE_BOKEH enabled=%d"), bFirstWakeBokehReview);
}

void ATSTSSExplorerCharacter::UpdateFirstWakeBokehReview(float DeltaSeconds)
{
    // Keep the character plane sharp at rest. Close down during locomotion and
    // while reading the flyer, so walking and the choice overlay remain clear.
    const bool bExploring = GetVelocity().SizeSquared2D() > FMath::Square(35.f) ||
        IsHilltoniaFlyerOpen();
    const float TargetFstop = bExploring ? 16.f : 2.8f;
    FirstWakeReviewFstop = FMath::FInterpTo(FirstWakeReviewFstop, TargetFstop, DeltaSeconds, 2.8f);
    const FVector FocusPoint = GetActorLocation() + FVector(0.f, 0.f, 28.f);
    const float Depth = FVector::DotProduct(
        FocusPoint - FollowCamera->GetComponentLocation(), FollowCamera->GetForwardVector());
    FPostProcessSettings& Lens = FollowCamera->PostProcessSettings;
    Lens.DepthOfFieldFocalDistance = FMath::Clamp(Depth, 210.f, 900.f);
    Lens.DepthOfFieldFstop = FirstWakeReviewFstop;
}

void ATSTSSExplorerCharacter::StartHilltoniaOpening(UWorld* World)
{
    if (!IsValid(FirstWakeState) || FirstWakeState->HasStarted() || !Controller)
    {
        return;
    }
    ATSTSSMilestoneActor* OldFlyer = nullptr;
    ATSTSSMilestoneActor* Captain = nullptr;
    for (TActorIterator<ATSTSSMilestoneActor> It(World); It; ++It)
    {
        if (It->GetActorLabel() == TEXT("TSTSS_PRELUDE_REVIEW_FlyerDiscovery"))
        {
            if (OldFlyer) return;
            OldFlyer = *It;
        }
        if (It->GetActorLabel() == TEXT("TSTSS_PRELUDE_REVIEW_IoniaHiring"))
        {
            if (Captain) return;
            Captain = *It;
        }
    }
    // Center the capsule over the built west road and face town (+X).
    const FVector Spawn(-14650.f, -150.f,
        GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 8.f);
    if (!IsValid(OldFlyer) || !IsValid(Captain) ||
        !HasSupportedReviewFooting(World, Spawn) || !TeleportTo(Spawn, FRotator::ZeroRotator))
    {
        UE_LOG(LogTemp, Warning, TEXT("TSTSS_HILLTONIA_OPENING_HOLD spawn or marker inventory"));
        return;
    }
    GetCharacterMovement()->StopMovementImmediately();
    Controller->SetControlRotation(FRotator(-8.f, 0.f, 0.f));
    HilltoniaCaptain = Captain;
    bHilltoniaOpeningActive = true;
    OldFlyer->Tags.AddUnique(TEXT("TSTSS_RETIRED_HARBOR_FLYER"));
    OldFlyer->SetActorHiddenInGame(true);
    OldFlyer->SetActorEnableCollision(false);
    UE_LOG(LogTemp, Display, TEXT("TSTSS_HILLTONIA_OPENING_READY location=%s"),
        *GetActorLocation().ToCompactString());
}

bool ATSTSSExplorerCharacter::IsHilltoniaFlyerHit(const FHitResult& Hit) const
{
    const UPrimitiveComponent* Component = Hit.GetComponent();
    return bHilltoniaOpeningActive && IsValid(FirstWakeState) &&
        !FirstWakeState->HasStarted() && IsValid(Component) &&
        Component->ComponentHasTag(TEXT("TSTSS_HILLTONIA_FLYER"));
}

bool ATSTSSExplorerCharacter::IsHilltoniaFlyerOpen() const
{
    return bHilltoniaOpeningActive && bHilltoniaFlyerRead &&
        IsValid(FirstWakeState) && !FirstWakeState->HasStarted() &&
        FirstWakeState->GetRestoreGeneration() == HilltoniaFlyerGeneration &&
        TSTSSInteractionReach::IsInsidePlayerReach(
            GetActorLocation(), HilltoniaFlyerHit, InteractionDistance);
}

void ATSTSSExplorerCharacter::AcceptHilltoniaFlyer()
{
    if (!IsHilltoniaFlyerOpen() || !HilltoniaCaptain.IsValid()) return;
    bHilltoniaFlyerRead = false;
    if (FirstWakeState->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered))
    {
        UE_LOG(LogTemp, Display, TEXT("TSTSS_HILLTONIA_FLYER_ACCEPT"));
        ShowFirstWakeReviewObjective(FirstWakeState);
    }
}

void ATSTSSExplorerCharacter::DeclineHilltoniaFlyer()
{
    bHilltoniaFlyerRead = false;
}

bool ATSTSSExplorerCharacter::GetHilltoniaCaptainWaypoint(FVector& Location) const
{
    if (!bHilltoniaOpeningActive || !HilltoniaCaptain.IsValid() ||
        !IsValid(FirstWakeState) || !FirstWakeState->HasStarted() ||
        FirstWakeState->GetCurrentBeat() != ETSTSSFirstWakeBeat::FlyerDiscovered)
    {
        return false;
    }
    Location = HilltoniaCaptain->GetActorLocation() + FVector(0.f, 0.f, 175.f);
    return !Location.ContainsNaN();
}
#endif

void ATSTSSExplorerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    check(PlayerInputComponent);
    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &ATSTSSExplorerCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &ATSTSSExplorerCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &ATSTSSExplorerCharacter::Turn);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &ATSTSSExplorerCharacter::LookUp);
    PlayerInputComponent->BindAction(TEXT("Interact"), IE_Pressed, this, &ATSTSSExplorerCharacter::Interact);
    // Editor shortcuts may consume or strip modifier state before the game
    // receives the key. Never bind the PIE save action to F5 at all:
    // Shift+F5 must not accidentally trigger a gameplay save.
    // Outside PIE, preserve the existing normal-game F5 action.
    const UWorld* InputWorld = GetWorld();
    if (InputWorld && InputWorld->WorldType == EWorldType::PIE)
    {
        PlayerInputComponent->BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickSave);
    }
    else if (InputWorld && InputWorld->WorldType == EWorldType::Game)
    {
        PlayerInputComponent->BindAction(TEXT("QuickSave"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickSave);
    }
    PlayerInputComponent->BindAction(TEXT("QuickLoad"), IE_Pressed, this, &ATSTSSExplorerCharacter::QuickLoad);
#if WITH_EDITOR
    if (InputWorld && InputWorld->WorldType == EWorldType::PIE)
    {
        PlayerInputComponent->BindAction(TEXT("ReviewContinue"), IE_Pressed, this, &ATSTSSExplorerCharacter::ReviewContinue);
        // Opt-in cinematography is separate from E, J, K, F6, F7 and F9.
        PlayerInputComponent->BindAction(TEXT("EngineFocusPreview"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ToggleEngineFocusPreview);
        // Independent, opt-in route from earned engineering signoff.
        PlayerInputComponent->BindAction(TEXT("ReviewOpticalInspectionTravel"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ReviewOpticalInspectionTravel);
    }
#endif
    PlayerInputComponent->BindAction(TEXT("ReviewObjective"), IE_Pressed, this, &ATSTSSExplorerCharacter::ShowObjectiveReview);
#if WITH_EDITOR
    if (InputWorld && (InputWorld->WorldType == EWorldType::PIE ||
                       InputWorld->WorldType == EWorldType::Game))
    {
        PlayerInputComponent->BindAction(TEXT("ReviewShoreTravel"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ReviewShoreTravel);
        PlayerInputComponent->BindAction(TEXT("AcceptHilltoniaFlyer"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::AcceptHilltoniaFlyer);
        PlayerInputComponent->BindAction(TEXT("DeclineHilltoniaFlyer"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::DeclineHilltoniaFlyer);
        PlayerInputComponent->BindAction(TEXT("FirstWakeBokehReview"), IE_Pressed,
            this, &ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview);
    }
#endif
}

void ATSTSSExplorerCharacter::MoveForward(float Value)
{
#if WITH_EDITOR
    // The flyer is a focused quest decision: do not walk or look away
    // while Accept / Not now is displayed. Only those actions dismiss it.
    if (IsHilltoniaFlyerOpen()) return;
#endif
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Value);
    }
}
void ATSTSSExplorerCharacter::MoveRight(float Value)
{
#if WITH_EDITOR
    // The flyer is a focused quest decision: do not walk or look away
    // while Accept / Not now is displayed. Only those actions dismiss it.
    if (IsHilltoniaFlyerOpen()) return;
#endif
    if (Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
        AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Value);
    }
}
void ATSTSSExplorerCharacter::Turn(float Value)
{
#if WITH_EDITOR
    // The flyer is a focused quest decision: do not walk or look away
    // while Accept / Not now is displayed. Only those actions dismiss it.
    if (IsHilltoniaFlyerOpen()) return;
#endif
    AddControllerYawInput(Value);
}
void ATSTSSExplorerCharacter::LookUp(float Value)
{
#if WITH_EDITOR
    // The flyer is a focused quest decision: do not walk or look away
    // while Accept / Not now is displayed. Only those actions dismiss it.
    if (IsHilltoniaFlyerOpen()) return;
#endif
    AddControllerPitchInput(Value);
}

#if !UE_BUILD_SHIPPING
FString ATSTSSExplorerCharacter::GetReviewAimStatus() const
{
#if WITH_EDITOR
    const UWorld* World = GetWorld();
    if (!World || !IsValid(FirstWakeState) || !IsValid(FollowCamera) ||
        (World->WorldType != EWorldType::PIE && World->WorldType != EWorldType::Game) ||
        World->GetNetMode() != NM_Standalone ||
        !World->GetOutermost() ||
        !World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")))
    {
        return FString();
    }
    const FVector Camera = FollowCamera->GetComponentLocation();
    const FVector Pawn = GetActorLocation();
    const float Distance =
        TSTSSInteractionReach::GetCameraTraceLength(Camera, Pawn, InteractionDistance);
    if (Distance <= 0.f) return FString();
    FHitResult Hit;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(TSTSSReviewAim), false, this);
    if (!World->LineTraceSingleByChannel(Hit, Camera,
        Camera + FollowCamera->GetForwardVector() * Distance,
        ECC_Visibility, Query))
    {
        return FString();
    }
    if (IsHilltoniaFlyerHit(Hit))
    {
        return TSTSSInteractionReach::IsInsidePlayerReach(
            Pawn, Hit.ImpactPoint, InteractionDistance)
            ? TEXT("[E]  READ IONIA'S FLYER") : TEXT("MOVE CLOSER  |  IONIA'S FLYER");
    }
    const ATSTSSMilestoneActor* Marker = Cast<ATSTSSMilestoneActor>(Hit.GetActor());
    if (!IsValid(Marker)) return FString();
    const FString Display = Marker->GetReviewDisplayName();
    if (!Marker->IsReviewActionable(FirstWakeState))
    {
        return TEXT("LOCKED  |  COMPLETE CURRENT OBJECTIVE FIRST");
    }
    if (!TSTSSInteractionReach::IsInsidePlayerReach(
            Pawn, Hit.ImpactPoint, InteractionDistance))
    {
        return FString::Printf(TEXT("MOVE CLOSER  |  %s"), *Display);
    }
    return FString::Printf(TEXT("[E]  %s"), *Display);
#else
    return FString();
#endif
}
#endif

void ATSTSSExplorerCharacter::Interact()
{
#if WITH_EDITOR
    // E opens the flyer once; it cannot interact with another target
    // while the explicit Enter / Backspace decision is pending.
    if (IsHilltoniaFlyerOpen()) return;
#endif
    if (!FirstWakeState || !FollowCamera || !GetWorld()) return;
    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector PawnLocation = GetActorLocation();
    const float CameraTraceLength =
        TSTSSInteractionReach::GetCameraTraceLength(Start, PawnLocation, InteractionDistance);
    if (CameraTraceLength <= 0.f)
    {
        return;
    }

    // Trace across the camera boom before applying the *separate* pawn
    // reach check. At a 360 cm boom and 300 cm interact range the old
    // camera-only 300 cm ray could end behind the player entirely.
    const FVector End = Start + FollowCamera->GetForwardVector() * CameraTraceLength;
    FHitResult Hit;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(TSTSSInteract), false, this);
    const bool bTraceHit = GetWorld()->LineTraceSingleByChannel(
        Hit, Start, End, ECC_Visibility, Query);
#if WITH_EDITOR
    if (GetWorld()->WorldType == EWorldType::PIE && !bTraceHit)
    {
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_E_MISS pawn=%s camera=%s forward=%s trace_cm=%.1f objective=%s"),
            *PawnLocation.ToCompactString(), *Start.ToCompactString(),
            *FollowCamera->GetForwardVector().ToCompactString(), CameraTraceLength,
            *FirstWakeState->GetReviewObjectiveText());
    }
#endif
    if (bTraceHit)
    {
#if WITH_EDITOR
        if (IsHilltoniaFlyerHit(Hit))
        {
            if (TSTSSInteractionReach::IsInsidePlayerReach(
                    PawnLocation, Hit.ImpactPoint, InteractionDistance))
            {
                HilltoniaFlyerHit = Hit.ImpactPoint;
                HilltoniaFlyerGeneration = FirstWakeState->GetRestoreGeneration();
                bHilltoniaFlyerRead = true;
                // Prevent residual WASD velocity carrying Ender out of
                // interaction reach while the flyer modal is on screen.
                if (UCharacterMovementComponent* Movement = GetCharacterMovement())
                {
                    Movement->StopMovementImmediately();
                }
                UE_LOG(LogTemp, Display, TEXT("TSTSS_HILLTONIA_FLYER_READ"));
            }
            return;
        }
#endif
        if (ATSTSSMilestoneActor* Milestone = Cast<ATSTSSMilestoneActor>(Hit.GetActor()))
        {
            // A longer camera ray never increases interaction reach.
            if (TSTSSInteractionReach::IsInsidePlayerReach(
                    PawnLocation, Hit.ImpactPoint, InteractionDistance))
            {
                if (Milestone->TryActivate(FirstWakeState))
                {
#if WITH_EDITOR
                    if (GetWorld()->WorldType == EWorldType::PIE)
                    {
                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_PIE_REVIEW_E_ACCEPT target=%s pawn_hit_cm=%.1f objective_after=%s"),
                            *Milestone->GetActorLabel(),
                            FVector::Dist(PawnLocation, Hit.ImpactPoint),
                            *FirstWakeState->GetReviewObjectiveText());
                    }
#endif
                    ShowFirstWakeReviewObjective(FirstWakeState);
                    ShowOptionalEngineFocusHint(GetWorld(), Milestone->bIsInspectionStation);
#if WITH_EDITOR
                    // An earned click on the docked ship is the boarding action.
                    // Reuse the existing one-use, gated in-memory scene ticket.
                    if (GetWorld()->GetNetMode() == NM_Standalone &&
                        GetWorld()->GetOutermost() &&
                        GetWorld()->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) &&
                        UGameplayStatics::GetCurrentLevelName(GetWorld(), true) ==
                            TEXT("FirstWake_PreludeInteraction_V5_VisualReview") &&
                        Milestone->GetActorLabel() ==
                            TEXT("TSTSS_PRELUDE_REVIEW_AureateBoarding"))
                    {
                        ReviewShoreTravel();
                        return;
                    }
#endif
                }
                else
                {
                    // A valid, in-reach marker rejected the state transition.
                    // This does not grant progression or claim that E hit when
                    // the camera trace missed or the target was out of reach.
#if WITH_EDITOR
                    if (GetWorld()->WorldType == EWorldType::PIE)
                    {
                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_PIE_REVIEW_E_DENIED target=%s pawn_hit_cm=%.1f objective=%s"),
                            *Milestone->GetActorLabel(),
                            FVector::Dist(PawnLocation, Hit.ImpactPoint),
                            *FirstWakeState->GetReviewObjectiveText());
                    }
#endif
                    ShowFirstWakeReviewBlockedInteraction(FirstWakeState);
                }
            }
            else
            {
#if WITH_EDITOR
                if (GetWorld()->WorldType == EWorldType::PIE)
                {
                    UE_LOG(LogTemp, Display,
                        TEXT("TSTSS_PIE_REVIEW_E_OUT_OF_REACH target=%s pawn=%s pawn_hit_cm=%.1f limit_cm=%.1f objective=%s"),
                        *Milestone->GetActorLabel(), *PawnLocation.ToCompactString(),
                        FVector::Dist(PawnLocation, Hit.ImpactPoint),
                        InteractionDistance, *FirstWakeState->GetReviewObjectiveText());
                }
#endif
            }
        }
        else
        {
#if WITH_EDITOR
            if (GetWorld()->WorldType == EWorldType::PIE)
            {
                const AActor* OtherActor = Hit.GetActor();
                UE_LOG(LogTemp, Display,
                    TEXT("TSTSS_PIE_REVIEW_E_OTHER target=%s pawn=%s pawn_hit_cm=%.1f objective=%s"),
                    OtherActor ? *OtherActor->GetActorNameOrLabel() : TEXT("None"),
                    *PawnLocation.ToCompactString(),
                    FVector::Dist(PawnLocation, Hit.ImpactPoint),
                    *FirstWakeState->GetReviewObjectiveText());
            }
#endif
        }
    }
}

void ATSTSSExplorerCharacter::ShowObjectiveReview()
{
    // Read-only recall of the existing short-lived objective cue.
    ShowFirstWakeReviewObjective(FirstWakeState);
#if WITH_EDITOR
    UWorld* World = GetWorld();
    if (World && (World->WorldType == EWorldType::PIE ||
                  World->WorldType == EWorldType::Game) &&
        World->GetNetMode() == NM_Standalone &&
        World->GetOutermost() &&
        World->GetOutermost()->GetName().StartsWith(TEXT("/Game/TSTSS/Review/")) &&
        GEngine)
    {
        // J makes K discoverable, but never opens a level or grants a beat.
        // Keep K locked until the live state passes the existing route gate.
        const FString Scene = UGameplayStatics::GetCurrentLevelName(World, true);
        if (UTSTSSReviewShoreTravelSubsystem::IsEligible(FirstWakeState, Scene))
        {
            const FString Destination =
                UTSTSSReviewShoreTravelSubsystem::NextReviewMap(FirstWakeState, Scene);
            const FString ShortDestination = FPackageName::GetShortName(Destination);
            GEngine->AddOnScreenDebugMessage(-1, 7.f, FColor::Cyan,
                FString::Printf(TEXT("First Wake (review): K = %s (temporary scene review)"),
                    *ShortDestination));
        }
        else if (Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview") ||
                 Scene == TEXT("VS02_AureateInteriors") ||
                 Scene == TEXT("VS03_FirstWakeSky") ||
                 Scene == TEXT("VS04_SplashdownSea") ||
                 Scene == TEXT("VS05_DenithFuelShanty"))
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Yellow,
                TEXT("First Wake (review): K locked until current objective is complete"));
        }
    }
#endif
}

#if WITH_EDITOR
void ATSTSSExplorerCharacter::ReviewShoreTravel()
{
    UWorld* World = GetWorld();
    UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
    UTSTSSReviewShoreTravelSubsystem* Travel = GameInstance
        ? GameInstance->GetSubsystem<UTSTSSReviewShoreTravelSubsystem>() : nullptr;
    if (!Travel || !Travel->QueueShore(World, FirstWakeState))
    {
        if (GEngine)
        {
            const FString Objective = IsValid(FirstWakeState)
                ? FirstWakeState->GetReviewObjectiveText()
                : TEXT("story state unavailable");
            GEngine->AddOnScreenDebugMessage(-1, 6.f, FColor::Yellow,
                FString::Printf(TEXT("First Wake (review): K locked - %s"), *Objective));
        }
        return;
    }
    const FString Destination = Travel->GetPendingMapPackage();
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT destination=%s"),
        *Destination);
    UGameplayStatics::OpenLevel(this, FName(*Destination));
}

void ATSTSSExplorerCharacter::ReviewOpticalInspectionTravel()
{
    UWorld* World = GetWorld();
    UGameInstance* Instance = World ? World->GetGameInstance() : nullptr;
    UTSTSSReviewShoreTravelSubsystem* Travel = Instance
        ? Instance->GetSubsystem<UTSTSSReviewShoreTravelSubsystem>() : nullptr;
    if (!Travel || !Travel->QueueOpticalInspection(World, FirstWakeState))
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Yellow,
                TEXT("Optical review locked: complete engineering signoff in VS02 first"));
        }
        return;
    }
    const FString Destination = Travel->GetPendingMapPackage();
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_FIRSTWAKE_OPTICAL_REVIEW_QUEUED_NO_STORY_ADVANCE destination=%s"),
        *Destination);
    UGameplayStatics::OpenLevel(this, FName(*Destination));
}

#endif

void ATSTSSExplorerCharacter::QuickSave()
{
    // UE's Shift+F5 is Stop Play-In-Editor. The F5 action may also be
    // dispatched to this pawn before PIE shuts down; that must never
    // create a new review SaveGame as a side effect of stopping play.
    // Fail closed for unpossessed PIE pawns as well.
    const UWorld* World = GetWorld();
    const bool bPIE = World && World->WorldType == EWorldType::PIE;
    if (bPIE)
    {
        const APlayerController* PC = Cast<APlayerController>(GetController());
        if (!PC || PC->IsInputKeyDown(EKeys::LeftShift) ||
            PC->IsInputKeyDown(EKeys::RightShift))
        {
            return;
        }
    }
    // PIE testing must not write the normal quicksave slot. Never adopt or
    // overwrite a leftover review save from another Editor session.
    const FString Slot = bPIE ? TEXT("tstss_prelude_pie_quick") : TEXT("first_wake_quick");
    if (bPIE && !bPIEReviewQuickSlotOwned &&
        (UGameplayStatics::DoesSaveGameExist(Slot, 0) ||
         UGameplayStatics::DoesSaveGameExist(
             TEXT("tstss_prelude_pie_manifest_v1"), 0)))
    {
        ShowFirstWakeReviewProtectedSlotWarning(false);
        return;
    }
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
    const bool bSavedStory = SaveFirstWake(Slot);
    bool bSaved = bSavedStory;
#if WITH_EDITOR
    if (bPIE && bSavedStory)
    {
        bSaved = SaveReviewContinueBinding(Slot);
    }
#endif
    if (bPIE && bSaved)
    {
        bPIEReviewQuickSlotOwned = true;
    }
    ShowFirstWakeReviewSaveLoadStatus(false, bSaved);
}

void ATSTSSExplorerCharacter::QuickLoad()
{
#if WITH_EDITOR
    bPendingReviewContinue = false;
#endif
    const UWorld* World = GetWorld();
    const bool bPIE = World && World->WorldType == EWorldType::PIE;
    const FString Slot = bPIE ? TEXT("tstss_prelude_pie_quick") : TEXT("first_wake_quick");
    // No stale PIE save from an earlier test session can change this pawn.
    if (bPIE && !bPIEReviewQuickSlotOwned)
    {
        ShowFirstWakeReviewProtectedSlotWarning(true);
        return;
    }
    const bool bLoaded = LoadFirstWake(Slot);
    if (bLoaded)
    {
        ShowFirstWakeReviewObjective(FirstWakeState);
    }
    ShowFirstWakeReviewSaveLoadStatus(true, bLoaded);
}

bool ATSTSSExplorerCharacter::SaveFirstWake(const FString& Slot)
{
    if (!IsValid(FirstWakeState) || !UTSTSSPersistence::IsValidSlotName(Slot))
    {
        return false;
    }

    // This review actor does not own the combat party. An existing save may
    // contain a valid roster (or be corrupt/future-versioned). Never replace
    // such player data with an empty story-only payload. For a validated,
    // roster-free save, reuse its object to preserve other schema fields.
    UTSTSSSaveGame* Save = nullptr;
    if (UGameplayStatics::DoesSaveGameExist(Slot, 0))
    {
        Save = UTSTSSPersistence::LoadProgress(Slot);
        if (!IsValid(Save) || Save->PartyRoster.Num() != 0)
        {
            return false;
        }
    }
    else
    {
        Save = NewObject<UTSTSSSaveGame>(this);
    }
    if (!IsValid(Save))
    {
        return false;
    }

    Save->bFirstWakeStarted = FirstWakeState->HasStarted();
    Save->FirstWakeBeat = FirstWakeState->GetCurrentBeat();
    Save->InspectionMask = FirstWakeState->GetInspectionMask();
    return UTSTSSPersistence::SaveProgress(Slot, Save);
}

bool ATSTSSExplorerCharacter::LoadFirstWake(const FString& Slot)
{
    if (!IsValid(FirstWakeState)) return false;
    const UTSTSSSaveGame* Save = UTSTSSPersistence::LoadProgress(Slot);
    if (!Save) return false;
    const bool bRestored = FirstWakeState->Restore(
        Save->bFirstWakeStarted, Save->FirstWakeBeat, Save->InspectionMask);
#if WITH_EDITOR
    // Previously accepted review cubes have been made transparent to rays
    // and pawn movement. Restoring an earlier story beat must reactivate
    // only the markers which are now incomplete; keep saved-complete ones
    // transparent. Do not touch non-PIE or production-world actors.
    UWorld* World = GetWorld();
    if (bRestored && World && World->WorldType == EWorldType::PIE)
    {
        int32 ReconciledCount = 0;
        for (TActorIterator<ATSTSSMilestoneActor> It(World); It; ++It)
        {
            if (IsValid(*It))
            {
                It->ReconcileReviewCollisionAfterRestore(FirstWakeState);
                ++ReconciledCount;
            }
        }
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_LOAD_REBOUND beat=%d inspection_mask=%u generation=%llu actors_considered=%d"),
            static_cast<int32>(FirstWakeState->GetCurrentBeat()),
            static_cast<uint32>(FirstWakeState->GetInspectionMask()),
            static_cast<unsigned long long>(FirstWakeState->GetRestoreGeneration()),
            ReconciledCount);
    }
#endif
    return bRestored;
}

#if WITH_EDITOR
bool ATSTSSExplorerCharacter::SaveReviewContinueBinding(const FString& Slot)
{
    const UWorld* World = GetWorld();
    if (Slot != ReviewPrimarySlot || !World ||
        World->WorldType != EWorldType::PIE || !IsValid(FirstWakeState))
    {
        return false;
    }
    FString Digest;
    if (!DigestExactReviewPrimary(Slot, Digest)) return false;

    UTSTSSReviewContinueManifest* Manifest =
        NewObject<UTSTSSReviewContinueManifest>(this);
    if (!IsValid(Manifest)) return false;

    Manifest->PrimarySlot = Slot;
    Manifest->ProjectRoot = BoundReviewProjectRoot();
    Manifest->ReviewMapPackage = BoundReviewMapPackage(World);
    Manifest->PrimaryBlake3_160 = Digest;
    Manifest->PrimarySchemaVersion = UTSTSSSaveGame::CurrentVersion;
    Manifest->bSavedStoryStarted = FirstWakeState->HasStarted();
    Manifest->SavedBeat = FirstWakeState->GetCurrentBeat();
    Manifest->SavedInspectionMask = FirstWakeState->GetInspectionMask();
    Manifest->SavedPawnLocation = GetActorLocation();
    Manifest->SavedPawnRotation = GetActorRotation();
    Manifest->SavedControlRotation = Controller
        ? Controller->GetControlRotation() : GetActorRotation();

    // Existing manifest can only be updated after this PIE session owns the
    // primary slot; QuickSave checks ownership before writing the primary.
    const bool bStored = UGameplayStatics::SaveGameToSlot(
        Manifest, ReviewManifestSlot, 0);
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_REVIEW_CONTINUE_BINDING saved=%d beat=%d slot=%s"),
        bStored ? 1 : 0, static_cast<int32>(Manifest->SavedBeat), *Slot);
    return bStored;
}

void ATSTSSExplorerCharacter::ReviewContinue()
{
    UWorld* World = GetWorld();
    auto Reject = [this](const TCHAR* Reason)
    {
        bPendingReviewContinue = false;
        UE_LOG(LogTemp, Warning,
            TEXT("TSTSS_PIE_REVIEW_CONTINUE_REJECT reason=%s"), Reason);
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(
                -1, 8.f, FColor::Red,
                FString::Printf(TEXT("Review Continue refused: %s"), Reason));
        }
    };

    if (!World || World->WorldType != EWorldType::PIE ||
        !IsValid(FirstWakeState))
    {
        Reject(TEXT("review_PIE_only"));
        return;
    }
    // F9 remains session-scoped. F7 is a separate explicit action and cannot
    // silently adopt any save after a fresh Editor process starts.
    if (bPIEReviewQuickSlotOwned)
    {
        Reject(TEXT("session_already_owns_quicksave_use_F9"));
        return;
    }

    UTSTSSSaveGame* Saved = nullptr;
    UTSTSSReviewContinueManifest* Manifest = nullptr;
    FString Digest;
    if (!LoadBoundReviewContinueCandidate(
            World, ReviewPrimarySlot, Saved, Manifest, Digest))
    {
        Reject(TEXT("missing_corrupt_foreign_or_flight_save"));
        return;
    }

    // A second F7 is effective only for the unchanged state, exact files,
    // project/world, and same current PIE generation within 30 seconds.
    const bool bConfirm = bPendingReviewContinue &&
        World->GetTimeSeconds() <= PendingReviewContinueExpireWorldSeconds &&
        PendingReviewContinueDigest == Digest &&
        FirstWakeState->GetRestoreGeneration() ==
            PendingReviewContinueRestoreGeneration &&
        FirstWakeState->HasStarted() == bPendingReviewContinueStarted &&
        FirstWakeState->GetCurrentBeat() == PendingReviewContinueBeat &&
        FirstWakeState->GetInspectionMask() ==
            PendingReviewContinueInspectionMask;

    if (!bConfirm)
    {
        bPendingReviewContinue = true;
        PendingReviewContinueDigest = Digest;
        PendingReviewContinueExpireWorldSeconds =
            World->GetTimeSeconds() + 30.f;
        PendingReviewContinueRestoreGeneration =
            FirstWakeState->GetRestoreGeneration();
        bPendingReviewContinueStarted = FirstWakeState->HasStarted();
        PendingReviewContinueBeat = FirstWakeState->GetCurrentBeat();
        PendingReviewContinueInspectionMask =
            FirstWakeState->GetInspectionMask();

        const FString BeatName = StaticEnum<ETSTSSFirstWakeBeat>()->
            GetNameStringByValue(static_cast<int64>(Saved->FirstWakeBeat));
        const FString Summary = FString::Printf(
            TEXT("Continue preview: %s, inspections %u, Ender (%.0f,%.0f,%.0f). Press F7 AGAIN within 30s to confirm."),
            *BeatName, static_cast<uint32>(Saved->InspectionMask),
            Manifest->SavedPawnLocation.X, Manifest->SavedPawnLocation.Y,
            Manifest->SavedPawnLocation.Z);
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_PIE_REVIEW_CONTINUE_PREVIEW beat=%d inspections=%u position=%s confirmation_required=1"),
            static_cast<int32>(Saved->FirstWakeBeat),
            static_cast<uint32>(Saved->InspectionMask),
            *Manifest->SavedPawnLocation.ToCompactString());
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(
                -1, 30.f, FColor::Cyan, Summary);
        }
        return;
    }

    bPendingReviewContinue = false;
    // Validate the story restore in an isolated UObject first; no mutations
    // to the current gameplay state or actor collision on rejected saves.
    UTSTSSFirstWakeState* Trial =
        NewObject<UTSTSSFirstWakeState>(this);
    if (!IsValid(Trial) || !Trial->Restore(
            Saved->bFirstWakeStarted, Saved->FirstWakeBeat,
            Saved->InspectionMask))
    {
        Reject(TEXT("invalid_story_state"));
        return;
    }

    FVector TargetLocation = Manifest->SavedPawnLocation;
    const FRotator TargetRotation = Manifest->SavedPawnRotation;
    // Fail closed if the saved pawn would be embedded in collision or moved
    // far from the position that the player explicitly previewed.
    if (!World->FindTeleportSpot(this, TargetLocation, TargetRotation) ||
        FVector::Dist(TargetLocation, Manifest->SavedPawnLocation) > 50.f)
    {
        Reject(TEXT("unsafe_saved_player_location"));
        return;
    }

    const FVector OriginalLocation = GetActorLocation();
    const FRotator OriginalRotation = GetActorRotation();
    if (!TeleportTo(TargetLocation, TargetRotation, false, false))
    {
        Reject(TEXT("player_teleport_not_safe"));
        return;
    }
    // Use the same validated story load and review collision reconciliation
    // as the already tested in-session F9. If it fails, undo the pawn move.
    if (!LoadFirstWake(ReviewPrimarySlot))
    {
        SetActorLocationAndRotation(OriginalLocation, OriginalRotation,
            false, nullptr, ETeleportType::TeleportPhysics);
        Reject(TEXT("story_restore_failed"));
        return;
    }

    if (Controller)
    {
        Controller->SetControlRotation(Manifest->SavedControlRotation);
    }
    bPIEReviewQuickSlotOwned = true;
    UE_LOG(LogTemp, Display,
        TEXT("TSTSS_PIE_REVIEW_CONTINUE_ACCEPT beat=%d mask=%u location=%s generation=%llu"),
        static_cast<int32>(FirstWakeState->GetCurrentBeat()),
        static_cast<uint32>(FirstWakeState->GetInspectionMask()),
        *GetActorLocation().ToCompactString(),
        static_cast<unsigned long long>(
            FirstWakeState->GetRestoreGeneration()));
    ShowFirstWakeReviewObjective(FirstWakeState);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(
            -1, 8.f, FColor::Green,
            TEXT("First Wake review Continue accepted. F9 now uses this session's adopted slot."));
    }
}
#endif
