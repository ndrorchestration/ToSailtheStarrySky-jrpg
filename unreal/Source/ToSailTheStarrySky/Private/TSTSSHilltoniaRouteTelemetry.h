#pragma once
#include "CoreMinimal.h"

// Observability only: review-route waypoint classification in local cm.
// No controller commands, teleport, quest authority, saves or map changes.
#if !UE_BUILD_SHIPPING
namespace TSTSSHilltoniaRouteTelemetry
{
struct FReviewWaypoint
{
    const TCHAR* Name;
    float X;
    float Y;
    float RadiusCm;
};

inline const TCHAR* NearestWaypoint(const FVector& Position)
{
    if (Position.ContainsNaN() ||
        !FMath::IsFinite(Position.X) ||
        !FMath::IsFinite(Position.Y) ||
        !FMath::IsFinite(Position.Z))
    {
        return nullptr;
    }

    // Ordered geographic checkpoints, not gameplay objectives.
    // Repeat these in reverse on a real harbor-return walk.
    static constexpr FReviewWaypoint Waypoints[] = {
        {TEXT("DOCK_TOWN_SEAM"), -3650.f, -150.f, 240.f},
        {TEXT("TOWN_MAIN_STREET"), -5350.f, -150.f, 270.f},
        {TEXT("VILLAGE_SQUARE"), -7350.f, -150.f, 280.f},
        {TEXT("WOODLAND_APPROACH"), -7350.f, -1450.f, 260.f},
        {TEXT("FOREST_EDGE"), -7350.f, -3120.f, 260.f}
    };
    for (const FReviewWaypoint& Checkpoint : Waypoints)
    {
        const float DX = Position.X - Checkpoint.X;
        const float DY = Position.Y - Checkpoint.Y;
        if (DX * DX + DY * DY <= Checkpoint.RadiusCm * Checkpoint.RadiusCm)
        {
            return Checkpoint.Name;
        }
    }
    return nullptr;
}

inline bool IsScopedRouteRegion(const FVector& Position)
{
    return !Position.ContainsNaN() &&
        FMath::IsFinite(Position.X) &&
        FMath::IsFinite(Position.Y) &&
        FMath::IsFinite(Position.Z) &&
        Position.X <= -3400.f && Position.X >= -9650.f &&
        Position.Y >= -3650.f && Position.Y <= 1200.f;
}
}
#endif
