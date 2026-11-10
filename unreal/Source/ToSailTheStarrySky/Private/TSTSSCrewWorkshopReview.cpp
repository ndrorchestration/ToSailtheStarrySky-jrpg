#include "TSTSSCrewWorkshopReview.h"

bool FTSTSSCrewWorkshopReview::TryGetRoleProfile(
    FName CharacterId, FTSTSSCrewRoleProfile& OutProfile)
{
    FTSTSSCrewRoleProfile Candidate;
    Candidate.CharacterId = CharacterId;
    if (CharacterId == TEXT("Ender"))
    {
        Candidate.FiveLightAffinity = TEXT("Spirit");
        Candidate.bHarmonicEngineer = true;
    }
    else if (CharacterId == TEXT("Ionia"))
    {
        Candidate.FiveLightAffinity = TEXT("Earth");
        Candidate.bCaptain = true;
    }
    else if (CharacterId == TEXT("Lyra"))
    {
        Candidate.FiveLightAffinity = TEXT("Water");
        Candidate.bDefaultHealer = true;
    }
    else if (CharacterId == TEXT("Reson"))
    {
        Candidate.FiveLightAffinity = TEXT("Fire");
        Candidate.bArmsmaster = true;
        Candidate.bAcePilot = true;
    }
    else if (CharacterId == TEXT("Aepex"))
    {
        Candidate.FiveLightAffinity = TEXT("Air");
        Candidate.bWorkshopBuilder = true;
    }
    else
    {
        return false;
    }
    // No character's permanent identity is an exclusive job lock.
    Candidate.bCanEquipUnlockedJobs = true;
    OutProfile = Candidate;
    return true;
}

bool FTSTSSCrewWorkshopReview::TryRecordEngineObservation(
    const FTSTSSCrewWorkshopReviewState& Current,
    FName ObservationId,
    bool bDirectlyObserved,
    FTSTSSCrewWorkshopReviewState& OutState)
{
    if (!Current.RecruitedCharacters.Contains(TEXT("Ender"))
        || !bDirectlyObserved
        || ObservationId.IsNone()
        || Current.DirectlyObservedEngineClues.Contains(ObservationId))
    {
        return false;
    }

    FTSTSSCrewWorkshopReviewState Next = Current;
    Next.DirectlyObservedEngineClues.Add(ObservationId);
    OutState = MoveTemp(Next);
    return true;
}

bool FTSTSSCrewWorkshopReview::TryInstallReviewUpgrade(
    const FTSTSSCrewWorkshopReviewState& Current,
    const FTSTSSWorkshopUpgradeReview& Upgrade,
    FTSTSSCrewWorkshopReviewState& OutState)
{
    if (!Current.RecruitedCharacters.Contains(TEXT("Aepex"))
        || !Current.bAtSafeWorkshop
        || !Upgrade.bReviewSelectable
        || Upgrade.UpgradeId.IsNone()
        || Upgrade.TargetId.IsNone()
        || Upgrade.MaterialId.IsNone()
        || Upgrade.MaterialCost <= 0
        || !Current.ExplicitlyUnlockedUpgradeIds.Contains(Upgrade.UpgradeId)
        || Current.InstalledReviewUpgradeIds.Contains(Upgrade.UpgradeId)
        || Current.ReviewMaterials.FindRef(Upgrade.MaterialId) < Upgrade.MaterialCost)
    {
        return false;
    }

    switch (Upgrade.Target)
    {
    case ETSTSSWorkshopTarget::Vessel:
        // Ionia retains ship command even with an ace pilot and an inventor aboard.
        if (Upgrade.TargetId != TEXT("AureateWake")
            || !Current.RecruitedCharacters.Contains(TEXT("Ionia"))
            || !Current.bCaptainAuthorizedVesselWork)
        {
            return false;
        }
        break;
    case ETSTSSWorkshopTarget::Weapon:
    case ETSTSSWorkshopTarget::Equipment:
        break;
    default:
        return false;
    }

    if (Upgrade.bRequiresEnderObservation
        && (Upgrade.RequiredObservationId.IsNone()
            || !Current.RecruitedCharacters.Contains(TEXT("Ender"))
            || !Current.DirectlyObservedEngineClues.Contains(Upgrade.RequiredObservationId)))
    {
        return false;
    }

    FTSTSSCrewWorkshopReviewState Next = Current;
    const int32 Remaining = Next.ReviewMaterials.FindRef(Upgrade.MaterialId) - Upgrade.MaterialCost;
    Next.ReviewMaterials.Add(Upgrade.MaterialId, Remaining);
    Next.InstalledReviewUpgradeIds.Add(Upgrade.UpgradeId);
    OutState = MoveTemp(Next);
    return true;
}
