// Independently compiled native C++ test for the *exact* production header.
// Does not require Unreal Engine and cannot certify physics or sea rendering.
#include "TSTSSWaterlineGeometry.h"
#include <array>
#include <iostream>
#include <limits>

struct WaterlineCase
{
    const char* Name;
    bool Overlap;
    double HullCenter;
    double HullHalf;
    double WaterCenter;
    double WaterHalf;
    bool Expected;
};

int main()
{
    using TSTSSWaterlineGeometry::HasMeasuredHullWaterlineIntersection;
    const double Inf = std::numeric_limits<double>::infinity();
    const double Nan = std::numeric_limits<double>::quiet_NaN();
    const double Max = std::numeric_limits<double>::max();
    const std::array<WaterlineCase, 16> Cases = {{
        {"overlap without immersion",true,110.0,10.0,0.0,20.0,false},
        {"valid hull surface penetration",true,24.0,10.0,0.0,20.0,true},
        {"no collider overlap",false,24.0,10.0,0.0,20.0,false},
        {"exact tangent is not penetration",true,30.0,10.0,0.0,20.0,false},
        {"one centimeter immersed",true,29.0,10.0,0.0,20.0,true},
        {"submerged below waterline",true,-100.0,10.0,0.0,20.0,true},
        {"zero hull bounds",true,24.0,0.0,0.0,20.0,false},
        {"negative hull bounds",true,24.0,-1.0,0.0,20.0,false},
        {"zero water bounds",true,24.0,10.0,0.0,0.0,false},
        {"negative water bounds",true,24.0,10.0,0.0,-20.0,false},
        {"infinite hull location",true,Inf,10.0,0.0,20.0,false},
        {"nan hull extent",true,24.0,Nan,0.0,20.0,false},
        {"infinite water location",true,24.0,10.0,-Inf,20.0,false},
        {"nan water extent",true,24.0,10.0,0.0,Nan,false},
        {"water surface overflow",true,24.0,10.0,Max,Max,false},
        {"hull lower bound overflow",true,-Max,Max,0.0,20.0,false},
    }};
    unsigned Count = 0;
    for (const auto& Test : Cases)
    {
        const bool Got = HasMeasuredHullWaterlineIntersection(
            Test.Overlap, Test.HullCenter, Test.HullHalf,
            Test.WaterCenter, Test.WaterHalf);
        if (Got != Test.Expected)
        {
            std::cerr << "FAIL: " << Test.Name << " expected=" << Test.Expected
                      << " received=" << Got << "\n";
            return 1;
        }
        ++Count;
    }
    std::cout << "PASS: " << Count
              << " native compiled C++ waterline numeric cases; UE engine not run\n";
    return 0;
}
