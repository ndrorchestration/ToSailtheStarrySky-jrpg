#pragma once

#include "CoreMinimal.h"

// Public-safe, non-persistent review model. Five Lights are narrative identity;
// they do not equip spells, force jobs, or authorize ship travel modes.
struct FTSTSSCrewRoleProfile
{
    FName CharacterId = NAME_None;
    FName FiveLightAffinity = NAME_None;
    bool bCanEquipUnlockedJobs = false;
    bool bCaptain = false;
    bool bHarmonicEngineer = false;
    bool bDefaultHealer = false;
    bool bArmsmaster = false;
    bool bAcePilot = false;
    bool bWorkshopBuilder = false;
};

enum class ETSTSSWorkshopTarget : uint8
{
    Vessel,
    Weapon,
    Equipment
};

// Fixture admission only. This does not create actual equipment, ship actors,
// player inventory, SaveGame entries or callable combat abilities.
struct FTSTSSWorkshopUpgradeReview
{
    FName UpgradeId = NAME_None;
    ETSTSSWorkshopTarget Target = ETSTSSWorkshopTarget::Vessel;
    FName TargetId = NAME_None;
    FName MaterialId = NAME_None;
    int32 MaterialCost = 0;
    bool bReviewSelectable = false;
    bool bRequiresEnderObservation = false;
    FName RequiredObservationId = NAME_None;
};

struct FTSTSSCrewWorkshopReviewState
{
    TSet<FName> RecruitedCharacters;
    TSet<FName> DirectlyObservedEngineClues;
    TSet<FName> ExplicitlyUnlockedUpgradeIds;
    TSet<FName> InstalledReviewUpgradeIds;
    TMap<FName, int32> ReviewMaterials;
    bool bAtSafeWorkshop = false;
    bool bCaptainAuthorizedVesselWork = false;
};

class TOSAILTHESTARRYSKY_API FTSTSSCrewWorkshopReview
{
public:
    // Profiles describe stable identities, not exclusive combat jobs.
    // Unknown character IDs reject without changing the caller's output.
    static bool TryGetRoleProfile(FName CharacterId, FTSTSSCrewRoleProfile& OutProfile);

    // Records the fact of a directly observed clue. Never proves its explanation
    // or automatically grants upgrades, mastery, story access or ship modes.
    static bool TryRecordEngineObservation(
        const FTSTSSCrewWorkshopReviewState& Current,
        FName ObservationId,
        bool bDirectlyObserved,
        FTSTSSCrewWorkshopReviewState& OutState);

    // Transactional shadow inventory transaction. Real crafting/UI/save/gear and
    // stat changes must later be authorized by their respective runtime owners.
    static bool TryInstallReviewUpgrade(
        const FTSTSSCrewWorkshopReviewState& Current,
        const FTSTSSWorkshopUpgradeReview& Upgrade,
        FTSTSSCrewWorkshopReviewState& OutState);
};
