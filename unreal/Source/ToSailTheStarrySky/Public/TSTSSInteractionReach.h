#pragma once
#include "CoreMinimal.h"

// The third-person camera boom starts behind the pawn. A trace of just the
// player reach, measured from the camera, can terminate before reaching the
// player's position. Compute the ray length from camera->pawn plus reach,
// then independently enforce the original pawn->target range.
namespace TSTSSInteractionReach
{
    FORCEINLINE float GetCameraTraceLength(
        const FVector& CameraLocation,
        const FVector& PawnLocation,
        const float PlayerReach)
    {
        if (!FMath::IsFinite(PlayerReach) || PlayerReach <= 0.f
            || CameraLocation.ContainsNaN() || PawnLocation.ContainsNaN())
        {
            return 0.f;
        }

        const float CameraOffset = FVector::Dist(CameraLocation, PawnLocation);
        const float TraceLength = CameraOffset + PlayerReach;
        return FMath::IsFinite(TraceLength) ? TraceLength : 0.f;
    }

    FORCEINLINE bool IsInsidePlayerReach(
        const FVector& PawnLocation,
        const FVector& ImpactPoint,
        const float PlayerReach)
    {
        return FMath::IsFinite(PlayerReach) && PlayerReach > 0.f
            && !PawnLocation.ContainsNaN() && !ImpactPoint.ContainsNaN()
            && FVector::DistSquared(PawnLocation, ImpactPoint)
                <= FMath::Square(PlayerReach);
    }
}
