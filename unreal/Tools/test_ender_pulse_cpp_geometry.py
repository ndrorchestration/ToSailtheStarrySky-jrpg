"""Compile and RUN the same 3D Pulse sphere predicate used by Unreal.

This is genuine portable C++ execution, not a Python reimplementation.
It proves finite-coordinate, radius-boundary and XYZ geometry only; it is
NOT a UE UHT/UBT, C++ combat-engine, real PIE, spatial actor or GPU test.
No permanent executable or data is written to the repository.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER_DIR = ROOT / "Source/ToSailTheStarrySky/Public"

CPP = r"""
#include "Combat/TSTSSPulseAreaMath.h"
#include <cmath>
#include <iostream>
#include <limits>
using TSTSSPulseAreaMath::WithinSphere;
using TSTSSPulseAreaMath::IsValidWorldPosition;
int main()
{
    int cases = 0;
    auto check = [&](bool ok, const char* name) {
        if (!ok) { std::cerr << "FAIL " << name << "\n"; return false; }
        ++cases;
        return true;
    };
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();
    bool good = true;
    good &= check(WithinSphere(0,0,0, 600,0,0, 600), "positive X inclusive");
    good &= check(WithinSphere(0,0,0, -600,0,0, 600), "negative X inclusive");
    good &= check(WithinSphere(0,0,0, 0,600,0, 600), "positive Y inclusive");
    good &= check(WithinSphere(0,0,0, 0,0,600, 600), "positive Z inclusive");
    good &= check(WithinSphere(0,0,0, 0,0,-600, 600), "negative Z inclusive");
    good &= check(WithinSphere(0,0,0, 360,480,0, 600), "3-4-5 XY boundary");
    good &= check(WithinSphere(0,0,0, 0,360,480, 600), "3-4-5 YZ boundary");
    good &= check(WithinSphere(0,0,0, 200,400,400, 600), "3D XYZ boundary");
    good &= check(!WithinSphere(0,0,0, 0,0,600.01, 600), "high Z outside");
    good &= check(!WithinSphere(0,0,0, 601,0,0, 600), "far X outside");
    good &= check(!WithinSphere(0,0,0, 360,480,1, 600), "XYZ Pythagorean exclusion");
    good &= check(WithinSphere(130,240,350, 130,240,350, 600), "caster center");
    good &= check(WithinSphere(100,200,300, 100,200,900, 600), "translated center");
    good &= check(!WithinSphere(100,200,300, 100,200,900.01, 600), "translated beyond");
    good &= check(!WithinSphere(0,0,0, 0,0,0, 0), "no zero radius");
    good &= check(!WithinSphere(0,0,0, 0,0,0, -600), "no negative radius");
    good &= check(!WithinSphere(0,0,0, 0,0,0, Inf), "no infinite radius");
    good &= check(!WithinSphere(0,0,0, 0,0,0, NaN), "no NaN radius");
    good &= check(!WithinSphere(NaN,0,0, 0,0,0, 600), "no NaN caster");
    good &= check(!WithinSphere(Inf,0,0, 0,0,0, 600), "no Inf caster");
    good &= check(!WithinSphere(0,0,0, NaN,0,0, 600), "no NaN target");
    good &= check(!WithinSphere(0,0,0, 0,0,-Inf, 600), "no Inf target");
    good &= check(!WithinSphere(0,0,0, 100000001,0,0, 600), "out-of-world target");
    good &= check(!WithinSphere(100000001,0,0, 0,0,0, 600), "out-of-world caster");
    good &= check(!IsValidWorldPosition(NaN,0,0), "coordinate predicate NaN");
    good &= check(IsValidWorldPosition(100000000,0,0), "coordinate max inclusive");
    good &= check(!WithinSphere(0,0,0, 0,0,0, 100000001), "out-of-world radius");
    good &= check(WithinSphere(0,0,0, 10,0,0, 600) ==
                  WithinSphere(10,0,0, 0,0,0, 600), "symmetry");
    if (!good) return 2;
    std::cout << "PULSE_CPP_GEOMETRY_PASS " << cases << "\n";
    return 0;
}
"""


class PulsePortableCppGeometryTests(unittest.TestCase):
    def test_compile_and_execute_actual_shared_cpp_geometry(self):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if compiler is None:
            self.skipTest("No C++17 g++/clang++ compiler: portable geometry not executed")
        self.assertTrue((HEADER_DIR / "Combat/TSTSSPulseAreaMath.h").is_file())
        with tempfile.TemporaryDirectory(prefix="tstss_pulse_cpp_") as temp:
            source = Path(temp) / "pulse_geometry.cpp"
            binary = Path(temp) / ("pulse_geometry.exe" if os.name == "nt" else "pulse_geometry")
            source.write_text(CPP, encoding="utf-8")
            built = subprocess.run(
                [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                 "-O0", "-I", str(HEADER_DIR), str(source), "-o", str(binary)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            executed = subprocess.run(
                [str(binary)], capture_output=True, text=True,
                timeout=15, check=False,
            )
            self.assertEqual(executed.returncode, 0, executed.stdout + executed.stderr)
            self.assertIn("PULSE_CPP_GEOMETRY_PASS 28", executed.stdout)


if __name__ == "__main__":
    unittest.main()
