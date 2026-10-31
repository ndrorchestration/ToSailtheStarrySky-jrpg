#include "Misc/AutomationTest.h"
#include "TSTSSWaterlineGeometry.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSWaterlineGeometryTest,
    "TSTSS.FirstWake.WaterlineGeometry",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSWaterlineGeometryTest::RunTest(const FString& Parameters)
{
    using TSTSSWaterlineGeometry::HasMeasuredHullWaterlineIntersection;
    const double NaN = std::numeric_limits<double>::quiet_NaN();

    TestFalse(TEXT("Overlapping water volume above surface is not SeaContact"),
        HasMeasuredHullWaterlineIntersection(true, 110., 10., 0., 20.));
    TestFalse(TEXT("No overlap is never accepted"),
        HasMeasuredHullWaterlineIntersection(false, 24., 10., 0., 20.));
    TestFalse(TEXT("Exact tangent requires actual penetration"),
        HasMeasuredHullWaterlineIntersection(true, 30., 10., 0., 20.));
    TestTrue(TEXT("Actual hull lower bound crossing can count as provisional contact"),
        HasMeasuredHullWaterlineIntersection(true, 29., 10., 0., 20.));
    TestFalse(TEXT("Invalid water bounds fail closed"),
        HasMeasuredHullWaterlineIntersection(true, 29., 10., 0., 0.));
    TestFalse(TEXT("NaN hull extent fails closed"),
        HasMeasuredHullWaterlineIntersection(true, 29., NaN, 0., 20.));
    // The observer's actual permission, collision, and story gates require
    // independent world-level proof; a numeric predicate alone never advances.
    return true;
}
#endif
