#include "TSTSSWaterLandingGate.h"

bool UTSTSSWaterLandingGate::Observe(float DeltaSeconds, bool bHullTouchesWater,
    float HullVerticalSpeedCms, UTSTSSFirstWakeState* Story)
{
    if (!IsValid(Story) || !FMath::IsFinite(DeltaSeconds) ||
        !FMath::IsFinite(HullVerticalSpeedCms) || DeltaSeconds <= 0.f ||
        DeltaSeconds > 0.25f)
    {
        Reset(); // Invalid samples cannot preserve stable-contact evidence.
        return false;
    }
    if (Story->GetCurrentBeat() != ETSTSSFirstWakeBeat::Launched &&
        Story->GetCurrentBeat() != ETSTSSFirstWakeBeat::SeaContact)
    {
        Reset();
        return false;
    }
    if (!bHullTouchesWater)
    {
        // A discontinuity invalidates both contact provenance and settling time.
        // On re-entry the story can reacquire SeaContact without replaying it.
        Reset();
        return false;
    }
    // Restore() can return to the same beat as well as an earlier one. Its
    // transient generation invalidates all contact evidence from the old timeline.
    const uint64 RestoreGeneration = Story->GetRestoreGeneration();
    if (!bHasObservedRestoreGeneration ||
        ObservedRestoreGeneration != RestoreGeneration)
    {
        StableContactSeconds = 0.f;
        bContactRecorded = false;
        bHasPreviousStableSample = false;
        ObservedRestoreGeneration = RestoreGeneration;
        bHasObservedRestoreGeneration = true;
    }
    // A restored save may already have recorded SeaContact. Reacquire contact
    // without replaying a milestone; never skip ahead from another story beat.
    if (!bContactRecorded)
    {
        if (Story->HasStarted() &&
            Story->GetCurrentBeat() == ETSTSSFirstWakeBeat::SeaContact)
        {
            bContactRecorded = true;
        }
        else
        {
            if (!Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::SeaContact)) return false;
            bContactRecorded = true;
        }
    }
    if (FMath::Abs(HullVerticalSpeedCms) > 25.f)
    {
        StableContactSeconds = 0.f;
        bHasPreviousStableSample = false;
        return false;
    }
    // The first calm, immersed frame observes the beginning of a stable window.
    // Its DeltaSeconds covers time since an earlier UNQUALIFIED or unobserved
    // frame, so crediting it would overstate directly witnessed stability.
    if (!bHasPreviousStableSample)
    {
        bHasPreviousStableSample = true;
        StableContactSeconds = 0.f;
        return false;
    }
    StableContactSeconds += DeltaSeconds;
    if (StableContactSeconds < 2.f) return false;
    if (Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::FlotationConfirmed))
    {
        return true;
    }
    return false;
}
