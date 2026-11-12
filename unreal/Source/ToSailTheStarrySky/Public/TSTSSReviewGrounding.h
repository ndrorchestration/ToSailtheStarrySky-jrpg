#pragma once
#include "CoreMinimal.h"

// A fail-safe only for explicitly identified, non-shipping First Wake review maps.
// This is not water gameplay, a world boundary system, or a canonical save point.
namespace TSTSSReviewGrounding
{
    constexpr float RecoveryDropCm = 400.f;

    inline bool IsWalkableReviewMap(const FString& ShortName)
    {
        return ShortName == TEXT("FirstWake_PreludeInteraction_V2") ||
               ShortName == TEXT("FirstWake_PreludeInteraction_V5_VisualReview") ||
               ShortName == TEXT("VS01_DenithHarbor") ||
               ShortName == TEXT("VS06_SplashdownShore") ||
               ShortName == TEXT("L_VS06_ShoreMagicEnemyGear_Review");
    }

    inline bool ShouldRecover(const bool bReviewRuntime, const FString& ShortName,
                              const bool bHasSupportedAnchor, const bool bFalling,
                              const FVector& Current, const FVector& Anchor)
    {
        return bReviewRuntime && IsWalkableReviewMap(ShortName) &&
               bHasSupportedAnchor && bFalling &&
               !Current.ContainsNaN() && !Anchor.ContainsNaN() &&
               Current.Z < Anchor.Z - RecoveryDropCm;
    }
}
