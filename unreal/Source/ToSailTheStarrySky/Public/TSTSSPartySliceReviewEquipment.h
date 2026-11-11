#pragma once

#include "CoreMinimal.h"
#include "TSTSSReviewEquipment.h"
#include "TSTSSPartySliceReviewEquipment.generated.h"

// Review-stage authority is NOT proof of actual story recruitment.
// Splashdown alone does NOT unlock Lyra. A separate verified recruitment
// event is required before the review fixture may include her.
UENUM(BlueprintType)
enum class ETSTSSPartySliceReviewStage : uint8
{
    FirstWake,
    AfterSplashdown,
    LyraRecruited
};

class TOSAILTHESTARRYSKY_API FTSTSSPartySliceReviewEquipment
{
public:
    static bool IsMemberAvailable(ETSTSSPartySliceReviewStage Stage, FName CharacterId);

    // Pure deterministic fixture builder. Atomic failure preserves caller output.
    // No persistent inventory, story-state mutation or skill authority.
    static bool TryBuildEquippedReviewFixture(
        ETSTSSPartySliceReviewStage Stage, FTSTSSReviewGearState& OutState);
};
