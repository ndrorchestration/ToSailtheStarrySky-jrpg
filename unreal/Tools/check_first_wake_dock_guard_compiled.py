"""Compile the actual review fall decision header with narrow C++ API doubles.

This does not run Unreal, inspect collision, teleport actors or establish PIE safety.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

HEADER = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Public/TSTSSReviewGrounding.h")
API = r"""
#pragma once
#include <cmath>
#include <string>
using FString = std::string;
#define TEXT(value) value
struct FVector {
    float X, Y, Z;
    FVector(float x, float y, float z): X(x), Y(y), Z(z) {}
    bool ContainsNaN() const {
        return !std::isfinite(X) || !std::isfinite(Y) || !std::isfinite(Z);
    }
};
"""
PROBE = r"""
#include <limits>
#include <iostream>
#include "TSTSSReviewGrounding.h"
int main() {
    using namespace TSTSSReviewGrounding;
    int failures = 0;
    int cases = 0;
    auto expect = [&](bool actual, bool expected, const char* label) {
        ++cases;
        if (actual != expected) {
            ++failures;
            std::cerr << "FAILED: " << label << "\n";
        }
    };
    const FVector anchor(0.f, 0.f, 160.f);
    const FVector down(0.f, 0.f, -241.f);
    expect(ShouldRecover(true, "VS01_DenithHarbor", true, true, down, anchor), true, "harbor");
    expect(ShouldRecover(true, "FirstWake_PreludeInteraction_V2", true, true, down, anchor), true, "prelude");
    expect(ShouldRecover(true, "FirstWake_PreludeInteraction_V5_VisualReview", true, true, down, anchor), true, "v5 prelude");
    expect(ShouldRecover(true, "FirstWake_PreludeInteraction_V3_VisualReview", true, true, down, anchor), false, "unapproved v3");
    expect(ShouldRecover(true, "FirstWake_PreludeInteraction_V4_VisualReview", true, true, down, anchor), false, "unapproved v4");
    expect(ShouldRecover(true, "VS06_SplashdownShore", true, true, down, anchor), true, "shore");
    expect(ShouldRecover(true, "L_VS06_ShoreMagicEnemyGear_Review", true, true, down, anchor), true, "shore gear");
    expect(ShouldRecover(true, "VS04_SplashdownSea", true, true, down, anchor), false, "no sea travel");
    expect(ShouldRecover(true, "VS03_FirstWakeSky", true, true, down, anchor), false, "no sky travel");
    expect(ShouldRecover(true, "Production", true, true, down, anchor), false, "no production");
    expect(ShouldRecover(false, "VS01_DenithHarbor", true, true, down, anchor), false, "runtime gate");
    expect(ShouldRecover(true, "VS01_DenithHarbor", false, true, down, anchor), false, "anchor gate");
    expect(ShouldRecover(true, "VS01_DenithHarbor", true, false, down, anchor), false, "falling gate");
    expect(ShouldRecover(true, "VS01_DenithHarbor", true, true, FVector(0,0,-240), anchor), false, "threshold exact");
    expect(ShouldRecover(true, "VS01_DenithHarbor", true, true, FVector(0,0,-239), anchor), false, "threshold above");
    expect(ShouldRecover(true, "VS01_DenithHarbor", true, true,
        FVector(0,0,std::numeric_limits<float>::quiet_NaN()), anchor), false, "nan");
    std::cout << "review fall actual-header C++ cases=" << cases
              << " failures=" << failures << "\n";
    return failures ? 1 : 0;
}
"""


def compile_and_run(compiler, root, name, header):
    target = root / name
    target.mkdir()
    (target / "CoreMinimal.h").write_text(API, encoding="utf-8")
    (target / "TSTSSReviewGrounding.h").write_text(header, encoding="utf-8")
    source = target / "probe.cpp"
    source.write_text(PROBE, encoding="utf-8")
    exe = target / "probe.exe"
    if Path(compiler).name.lower() in ("cl.exe", "cl"):
        cmd = [compiler, "/nologo", "/EHsc", "/std:c++17", str(source),
               "/I" + str(target), "/Fe:" + str(exe)]
    else:
        cmd = [compiler, "-std=c++17", str(source), "-I", str(target), "-o", str(exe)]
    result = subprocess.run(cmd, cwd=target, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("Compilation failed: " + result.stdout + result.stderr)
    result = subprocess.run([str(exe)], cwd=target, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main():
    compiler = shutil.which("cl") or shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        raise RuntimeError("No C++17 compiler; no compiled review-fall proof")
    original = HEADER.read_text(encoding="utf-8")
    assert "constexpr float RecoveryDropCm = 400.f;" in original
    with tempfile.TemporaryDirectory(prefix="tstss_dock_guard_") as temp:
        root = Path(temp)
        rc, report = compile_and_run(compiler, root, "real", original)
        if rc:
            raise RuntimeError("Actual header failed: " + report)
        mutated = original.replace("RecoveryDropCm = 400.f", "RecoveryDropCm = -400.f")
        negative_rc, _ = compile_and_run(compiler, root, "mutated", mutated)
        if negative_rc == 0:
            raise RuntimeError("Negative-control mutation escaped the compiled probe")
        print("PASS: " + report.strip())
        print("PASS: mutated threshold rejected by compiled negative control")
        print("Portable C++ header proof only; native Unreal and PIE remain untested.")


if __name__ == "__main__":
    main()
