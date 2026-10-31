#pragma once

// Engine-free numeric boundary shared by the native Aureate Wake observer and
// its independently compiled C++ test executable. Units are Unreal cm.
// This is only an AABB waterline screen, never wave/surface or buoyancy physics.
#include <cmath>

namespace TSTSSWaterlineGeometry
{
    inline bool HasMeasuredHullWaterlineIntersection(
        const bool bOverlappingWaterComponent,
        const double HullCenterZ,
        const double HullHalfHeight,
        const double WaterCenterZ,
        const double WaterHalfHeight)
    {
        if (!bOverlappingWaterComponent ||
            !std::isfinite(HullCenterZ) || !std::isfinite(HullHalfHeight) ||
            !std::isfinite(WaterCenterZ) || !std::isfinite(WaterHalfHeight) ||
            HullHalfHeight <= 0.0 || WaterHalfHeight <= 0.0)
        {
            return false;
        }
        const double HullBottomZ = HullCenterZ - HullHalfHeight;
        const double WaterSurfaceZ = WaterCenterZ + WaterHalfHeight;
        return std::isfinite(HullBottomZ) && std::isfinite(WaterSurfaceZ) &&
            HullBottomZ < WaterSurfaceZ;
    }
}
