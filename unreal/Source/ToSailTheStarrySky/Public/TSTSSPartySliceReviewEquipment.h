#pragma once

#include "CoreMinimal.h"
#include "TSTSSReviewEquipment.h"

// Only Ender and Ionia before splashdown; Lyra can join AFTER splashdown.
// This is an opt-in transient review fixture, not a game item-grant service,
// runtime equipment attachment, authoritative inventory or character unlock.
enum class ETSTSSPartySliceReviewStage : uint8
{
    FirstWake,
    AfterSplashdown
};

class TOSAILTHESTARRYSKY_API FTSTSSPartySliceReviewEquipment
{
public:
    static bool IsMemberAvailable(ETSTSSPartySliceReviewStage Stage, FName CharacterId);

    // Pure deterministic fixture builder. Atomic failure preserves caller output.
    // All items must still pass normal owner/slot validity in TSTSSReviewEquipment.
    static bool TryBuildEquippedReviewFixture(
        ETSTSSPartySliceReviewStage Stage, FTSTSSReviewGearState& OutState);
};
