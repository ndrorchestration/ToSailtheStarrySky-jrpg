#include "TSTSSFirstWakeState.h"

// Temporary objective copy for First Wake review UX; no story authority changes.
// Blueprints may read this value without relying on debug-screen rendering.
FString UTSTSSFirstWakeState::GetReviewObjectiveText() const
{
    if (!bStarted)
    {
        return TEXT("Find Ionia's flyer");
    }

    switch (CurrentBeat)
    {
    case ETSTSSFirstWakeBeat::FlyerDiscovered:
        return TEXT("Speak with Captain Ionia");
    case ETSTSSFirstWakeBeat::IoniaHired:
        return TEXT("Board the Aureate Wake");
    case ETSTSSFirstWakeBeat::BoardedAureateWake:
        if ((InspectionMask & 0x01u) == 0) return TEXT("Inspect the levitation lift");
        if ((InspectionMask & 0x02u) == 0) return TEXT("Inspect the pressure systems");
        if ((InspectionMask & 0x04u) == 0) return TEXT("Inspect the reserve systems");
        return TEXT("Complete engineering signoff");
    case ETSTSSFirstWakeBeat::EngineeringChecked:
        return TEXT("Prepare for the First Wake launch");
    case ETSTSSFirstWakeBeat::Launched:
        return TEXT("Navigate the First Wake flight");
    case ETSTSSFirstWakeBeat::SeaContact:
        return TEXT("Stabilize the water landing");
    case ETSTSSFirstWakeBeat::FlotationConfirmed:
        return TEXT("Survey the hull and harmonic systems");
    case ETSTSSFirstWakeBeat::EmptyReserveInspected:
        return TEXT("Continue to the coastal survey");
    case ETSTSSFirstWakeBeat::ReturnedToBerth:
        return TEXT("First Wake review sequence complete");
    default:
        return TEXT("Review objective unavailable");
    }
}

bool UTSTSSFirstWakeState::AdvanceTo(const ETSTSSFirstWakeBeat RequestedBeat)
{
    const uint8 Requested = static_cast<uint8>(RequestedBeat);
    const uint8 Current = static_cast<uint8>(CurrentBeat);
    const uint8 Last = static_cast<uint8>(ETSTSSFirstWakeBeat::ReturnedToBerth);

    if (RequestedBeat == ETSTSSFirstWakeBeat::SeaContact ||
        RequestedBeat == ETSTSSFirstWakeBeat::FlotationConfirmed) return false;
    if (Requested > Last)
    {
        return false;
    }
    if (!bStarted)
    {
        if (RequestedBeat != ETSTSSFirstWakeBeat::FlyerDiscovered)
        {
            return false;
        }
        bStarted = true;
        return true;
    }
    if (Current >= Last || Requested != Current + 1)
    {
        return false;
    }
    if (RequestedBeat == ETSTSSFirstWakeBeat::EngineeringChecked && !AreInspectionsComplete())
    {
        return false;
    }
    CurrentBeat = RequestedBeat;
    return true;
}

bool UTSTSSFirstWakeState::AdvanceWaterBeat(ETSTSSFirstWakeBeat RequestedBeat)
{
    if (!bStarted) return false;
    if (RequestedBeat == ETSTSSFirstWakeBeat::SeaContact &&
        CurrentBeat == ETSTSSFirstWakeBeat::Launched)
    {
        CurrentBeat = RequestedBeat;
        return true;
    }
    if (RequestedBeat == ETSTSSFirstWakeBeat::FlotationConfirmed &&
        CurrentBeat == ETSTSSFirstWakeBeat::SeaContact)
    {
        CurrentBeat = RequestedBeat;
        return true;
    }
    return false;
}

bool UTSTSSFirstWakeState::InspectStation(ETSTSSInspectionStation Station)
{
    if (!bStarted || CurrentBeat != ETSTSSFirstWakeBeat::BoardedAureateWake)
    {
        return false;
    }
    const uint8 Index = static_cast<uint8>(Station);
    if (Index > 2) return false;
    const uint8 Bit = static_cast<uint8>(1u << Index);
    if ((InspectionMask & Bit) != 0) return false;
    InspectionMask |= Bit;
    return true;
}

void UTSTSSFirstWakeState::Reset()
{
    bStarted = false;
    CurrentBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    InspectionMask = 0;
    // A full story restart is also a timeline discontinuity. Invalidate
    // cached hull contact/settling evidence even if the same state and gate
    // instances survive the reset before the next adapter Tick.
    ++RestoreGeneration;
}

bool UTSTSSFirstWakeState::Restore(bool bWasStarted, ETSTSSFirstWakeBeat SavedBeat, uint8 SavedInspectionMask)
{
    if (static_cast<uint8>(SavedBeat) > static_cast<uint8>(ETSTSSFirstWakeBeat::ReturnedToBerth) ||
        (SavedInspectionMask & ~0x07u) != 0 ||
        (!bWasStarted && (SavedBeat != ETSTSSFirstWakeBeat::FlyerDiscovered || SavedInspectionMask != 0)) ||
        (SavedInspectionMask != 0 && static_cast<uint8>(SavedBeat) < static_cast<uint8>(ETSTSSFirstWakeBeat::BoardedAureateWake)) ||
        (static_cast<uint8>(SavedBeat) >= static_cast<uint8>(ETSTSSFirstWakeBeat::EngineeringChecked) && SavedInspectionMask != 0x07))
    {
        return false;
    }
    bStarted = bWasStarted;
    CurrentBeat = SavedBeat;
    InspectionMask = SavedInspectionMask;
    ++RestoreGeneration;
    return true;
}
