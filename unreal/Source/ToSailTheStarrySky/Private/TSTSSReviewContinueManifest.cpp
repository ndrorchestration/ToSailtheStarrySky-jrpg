#include "TSTSSReviewContinueManifest.h"
#include "TSTSSSaveGame.h"

bool UTSTSSReviewContinueManifest::IsBoundFor(
    const UTSTSSSaveGame* Primary, const FString& ExpectedSlot,
    const FString& ExpectedProjectRoot, const FString& ExpectedMapPackage,
    const FString& ActualPrimaryBlake3_160) const
{
    if (!IsValid(Primary) || !Primary->IsStructurallyValid() ||
        !Primary->IsSupportedVersion() || Primary->PartyRoster.Num() != 0 ||
        ReviewVersion != CurrentReviewVersion ||
        ReviewProtocol != TEXT("TSTSS_FIRST_WAKE_PIE_CONTINUE_V1") ||
        PrimarySlot != TEXT("tstss_prelude_pie_quick") ||
        PrimarySlot != ExpectedSlot ||
        !ProjectRoot.Equals(ExpectedProjectRoot, ESearchCase::IgnoreCase) ||
        ReviewMapPackage != ExpectedMapPackage ||
        !ReviewMapPackage.StartsWith(TEXT("/Game/TSTSS/Review/FirstWake_")) ||
        PrimaryBlake3_160.Len() != 40 ||
        !PrimaryBlake3_160.Equals(ActualPrimaryBlake3_160, ESearchCase::IgnoreCase) ||
        PrimarySchemaVersion != UTSTSSSaveGame::CurrentVersion ||
        bSavedStoryStarted != Primary->bFirstWakeStarted ||
        SavedBeat != Primary->FirstWakeBeat ||
        SavedInspectionMask != Primary->InspectionMask)
    {
        return false;
    }
    // Review-only Continue deliberately stops at the preflight-to-launch
    // boundary: ship physics, water contact and crew state aren't saved yet.
    if (static_cast<uint8>(SavedBeat) >=
        static_cast<uint8>(ETSTSSFirstWakeBeat::Launched))
    {
        return false;
    }
    const auto IsFiniteLocation = [](const FVector& P) {
        return FMath::IsFinite(P.X) && FMath::IsFinite(P.Y) &&
            FMath::IsFinite(P.Z) && FMath::Abs(P.X) <= 100000.f &&
            FMath::Abs(P.Y) <= 100000.f && FMath::Abs(P.Z) <= 100000.f;
    };
    const auto IsFiniteRotation = [](const FRotator& R) {
        return FMath::IsFinite(R.Pitch) && FMath::IsFinite(R.Yaw) &&
            FMath::IsFinite(R.Roll) && FMath::Abs(R.Pitch) <= 36000.f &&
            FMath::Abs(R.Yaw) <= 36000.f && FMath::Abs(R.Roll) <= 36000.f;
    };
    return IsFiniteLocation(SavedPawnLocation) &&
        IsFiniteRotation(SavedPawnRotation) &&
        IsFiniteRotation(SavedControlRotation);
}
