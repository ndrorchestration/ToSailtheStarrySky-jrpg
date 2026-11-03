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
    // Quickload restores the same Story object in place. If it rewinds to
    // Launched, discard contact/settling evidence from the previous timeline
    // before using this new physical sample to reacquire SeaContact.
    if (bContactRecorded && Story->GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched)
    {
        Reset();
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
