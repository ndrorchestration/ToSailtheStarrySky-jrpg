#pragma once

// Engine-free exact spatial predicate shared by the Unreal Pulse executor
// and the portable C++ geometry tests. This file does NOT authorize a cast,
// select factions, spend MP, or grant a learned skill.
#include <cmath>

namespace TSTSSPulseAreaMath
{
    constexpr double MaxWorldCoordinateCm = 100000000.0;

    inline bool IsValidWorldPosition(double X, double Y, double Z)
    {
        return std::isfinite(X) && std::isfinite(Y) && std::isfinite(Z) &&
            std::fabs(X) <= MaxWorldCoordinateCm &&
            std::fabs(Y) <= MaxWorldCoordinateCm &&
            std::fabs(Z) <= MaxWorldCoordinateCm;
    }

    // Fully three-dimensional Euclidean sphere, inclusive boundary. Keeping
    // radius as an argument prevents this pure comparator from introducing a
    // second gameplay-radius authority.
    inline bool WithinSphere(
        double CenterX, double CenterY, double CenterZ,
        double TargetX, double TargetY, double TargetZ,
        double RadiusCm)
    {
        if (!IsValidWorldPosition(CenterX, CenterY, CenterZ) ||
            !IsValidWorldPosition(TargetX, TargetY, TargetZ) ||
            !std::isfinite(RadiusCm) ||
            RadiusCm <= 0.0 || RadiusCm > MaxWorldCoordinateCm)
            return false;

        const double DX = TargetX - CenterX;
        const double DY = TargetY - CenterY;
        const double DZ = TargetZ - CenterZ;
        return DX * DX + DY * DY + DZ * DZ <= RadiusCm * RadiusCm;
    }
}
