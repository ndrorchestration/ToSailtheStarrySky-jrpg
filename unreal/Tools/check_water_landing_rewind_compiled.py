#!/usr/bin/env python3
"""Compile actual First Wake state/gate headers, methods and water test bodies.

Only Unreal includes/reflection annotations are stripped. Narrow stand-ins cover
UObject lifetime, null-only IsValid, FMath and automation assertions; story and
landing behavior comes entirely from production C++. No Unreal, UHT, PIE,
collision simulation or filesystem saves are exercised. --self-test must compile
without the rewind guard and fail the same-object rewind behavioral assertion.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "Source/ToSailTheStarrySky"
STATE_HEADER = MODULE / "Public/TSTSSFirstWakeState.h"
GATE_HEADER = MODULE / "Public/TSTSSWaterLandingGate.h"
STATE_SOURCE = MODULE / "Private/TSTSSFirstWakeState.cpp"
GATE_SOURCE = MODULE / "Private/TSTSSWaterLandingGate.cpp"
TEST_SOURCE = MODULE / "Private/Tests/TSTSSWaterLandingRestoreTests.cpp"
FAILURE = "WATER_LANDING_BEHAVIOR_FAILURE: "
RESTORE_ASSERTION = "Same-beat restore cannot inherit pre-load settling time"
RESTORE_GENERATION_GUARD = re.compile(
    r"    const uint64 RestoreGeneration = Story->GetRestoreGeneration\(\);\s*"
    r"    if \(!bHasObservedRestoreGeneration \|\|\s*"
    r"        ObservedRestoreGeneration != RestoreGeneration\)\s*\{\s*"
    r"        StableContactSeconds = 0\.f;\s*"
    r"        bContactRecorded = false;\s*"
    r"        ObservedRestoreGeneration = RestoreGeneration;\s*"
    r"        bHasObservedRestoreGeneration = true;\s*\}"
)

PREFIX = r"""
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#define TEXT(value) value
#define TOSAILTHESTARRYSKY_API
#define WITH_DEV_AUTOMATION_TESTS 1
using uint8 = std::uint8_t;
using int32 = std::int32_t;
using uint64 = std::uint64_t;
using FString = std::string;
struct UObject { virtual ~UObject() = default; };
template <typename T> bool IsValid(const T* value) { return value != nullptr; }
struct FMath {
    static bool IsFinite(float value) { return std::isfinite(value); }
    static float Abs(float value) { return std::abs(value); }
};
std::vector<std::unique_ptr<UObject>> Objects;
template <typename T> T* NewObject() {
    auto object = std::make_unique<T>();
    T* result = object.get();
    Objects.push_back(std::move(object));
    return result;
}
unsigned Assertions = 0;
void Check(bool result, const std::string& reason) {
    if (!result) throw std::runtime_error(reason);
    ++Assertions;
}
struct FPortableAutomationTest {
    bool TestTrue(const char* label, bool value) {
        Check(value, label);
        return value;
    }
    bool TestFalse(const char* label, bool value) {
        Check(!value, label);
        return !value;
    }
    template <typename T>
    bool TestEqual(const char* label, const T& actual, const T& expected) {
        Check(actual == expected, label);
        return actual == expected;
    }
};
#define IMPLEMENT_SIMPLE_AUTOMATION_TEST(Class, Name, Flags) \
    class Class : public FPortableAutomationTest { \
    public: bool RunTest(const FString& Parameters); };
"""

SUFFIX = r"""
void CheckRestoredSeaContact() {
    UTSTSSFirstWakeState story;
    UTSTSSWaterLandingGate gate;
    Check(story.Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07),
          "Saved SeaContact setup failed");
    for (int sample = 0; sample < 7; ++sample)
        Check(!gate.Observe(0.25f, true, 0.f, &story),
              "Saved SeaContact completed before two stable seconds");
    Check(story.GetCurrentBeat() == ETSTSSFirstWakeBeat::SeaContact,
          "Saved SeaContact changed before two seconds");
    Check(gate.Observe(0.25f, true, 0.f, &story) &&
          story.GetCurrentBeat() == ETSTSSFirstWakeBeat::FlotationConfirmed,
          "Saved SeaContact did not complete at two stable seconds");
}

unsigned CheckInterruptedRewinds() {
    struct Sample {
        const char* name;
        float delta;
        bool wet;
        float speed;
        bool missingStory;
        bool recordsContact;
    };
    const float nan = std::numeric_limits<float>::quiet_NaN();
    const float inf = std::numeric_limits<float>::infinity();
    const Sample samples[] = {
        {"dry", 0.25f, false, 0.f, false, false},
        {"rising fast", 0.25f, true, 90.f, false, true},
        {"falling fast", 0.25f, true, -90.f, false, true},
        {"zero delta", 0.f, true, 0.f, false, false},
        {"negative delta", -0.1f, true, 0.f, false, false},
        {"oversized delta", 0.3f, true, 0.f, false, false},
        {"NaN delta", nan, true, 0.f, false, false},
        {"infinite delta", inf, true, 0.f, false, false},
        {"NaN speed", 0.25f, true, nan, false, false},
        {"infinite speed", 0.25f, true, inf, false, false},
        {"missing story", 0.25f, true, 0.f, true, false},
    };
    unsigned scenarios = 0;
    for (const Sample& sample : samples) {
        const auto require = [&sample](bool result, const char* reason) {
            Check(result, std::string(sample.name) + ": " + reason);
        };
        UTSTSSFirstWakeState story;
        UTSTSSWaterLandingGate gate;
        require(story.Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07),
                "initial restore failed");
        for (int index = 0; index < 6; ++index)
            require(!gate.Observe(0.25f, true, 0.f, &story),
                    "old timeline completed too soon");
        require(story.GetCurrentBeat() == ETSTSSFirstWakeBeat::SeaContact &&
                gate.GetStableContactSeconds() == 1.5f,
                "old timeline did not accumulate contact evidence");
        require(story.Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07),
                "in-place rewind failed");
        require(!gate.Observe(sample.delta, sample.wet, sample.speed,
                              sample.missingStory ? nullptr : &story),
                "interrupted first sample completed flotation");
        require(gate.GetStableContactSeconds() == 0.f,
                "interrupted first sample retained old stability");
        require(story.GetCurrentBeat() == (sample.recordsContact
                    ? ETSTSSFirstWakeBeat::SeaContact : ETSTSSFirstWakeBeat::Launched),
                "interrupted sample recorded the wrong beat");

        // Neither dry/invalid samples nor high-speed contact count as settling.
        for (int index = 0; index < 7; ++index)
            require(!gate.Observe(0.25f, true, 0.f, &story),
                    "insufficient fresh samples completed flotation");
        require(story.GetCurrentBeat() == ETSTSSFirstWakeBeat::SeaContact &&
                gate.GetStableContactSeconds() == 1.75f,
                "recovery did not reacquire contact with fresh duration");
        require(gate.Observe(0.25f, true, 0.f, &story) &&
                story.GetCurrentBeat() == ETSTSSFirstWakeBeat::FlotationConfirmed &&
                gate.GetStableContactSeconds() == 2.f,
                "recovery did not complete at exactly two fresh seconds");
        ++scenarios;
    }
    return scenarios;
}

int main() {
    try {
        // Run the actual repository test bodies, not portable copies of them.
        FTSTSSWaterLandingRestoreTest restore;
        FTSTSSWaterLandingNegativePathsTest negative;
        Check(restore.RunTest(""), "WaterLandingRestore returned false");
        Check(negative.RunTest(""), "WaterLandingNegativePaths returned false");
        CheckRestoredSeaContact();
        const unsigned interrupted = CheckInterruptedRewinds();
        std::cout << "PASS: 2 repository water test bodies, restored SeaContact and "
                  << interrupted << " interrupted-rewind scenarios ("
                  << Assertions << " assertions) using production state/gate C++\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "WATER_LANDING_BEHAVIOR_FAILURE: " << error.what() << "\n";
        return 2;
    }
}
"""


def strip_unreal(code: str, *, header: bool = False) -> str:
    """Remove dependencies/annotations, retaining declarations and method bodies."""
    code = re.sub(r'^\s*#include[^\n]*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^\s*#pragma once[^\n]*\n', '', code, flags=re.MULTILINE)
    if header:
        code = re.sub(
            r'\b(?:UCLASS|UENUM|UFUNCTION|UPROPERTY|GENERATED_BODY)\([^()]*\)',
            '', code,
        )
    return code


def portable_source(gate_source: str) -> str:
    chunks = [PREFIX]
    for path in (STATE_HEADER, GATE_HEADER, STATE_SOURCE):
        chunks.append(strip_unreal(path.read_text(encoding="utf-8"),
                                   header=path.suffix == ".h"))
    chunks.append(strip_unreal(gate_source))
    chunks.append(strip_unreal(TEST_SOURCE.read_text(encoding="utf-8")))
    chunks.append(SUFFIX)
    return "\n".join(chunks)


def compile_and_run(compiler: str, source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-water-landing-rewind-") as directory:
        root = Path(directory)
        cpp = root / "water_landing.cpp"
        binary = root / "water_landing"
        cpp.write_text(source, encoding="utf-8")
        if Path(compiler).name.lower() == "cl.exe":
            binary = root / "water_landing.exe"
            command = [compiler, "/nologo", "/std:c++17", "/EHsc", str(cpp),
                       "/Fo:" + str(root / "water_landing.obj"),
                       "/Fe:" + str(binary)]
        else:
            command = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-Werror",
                       # Unreal's required RunTest signature has an unused Parameters arg.
                       "-Wno-unused-parameter", "-pedantic", str(cpp), "-o", str(binary)]
        compiled = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=45,
        )
        if compiled.returncode:
            raise RuntimeError("Portable water landing compile failed: "
                               + compiled.stdout + compiled.stderr[-5000:])
        return subprocess.run(
            [str(binary)], check=False, capture_output=True, text=True, timeout=20,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="also compile without the restore-generation guard and require a behavioral failure")
    args = parser.parse_args()
    compiler = next((exe for name in ("g++", "clang++", "c++")
                     if (exe := shutil.which(name))), None)
    if compiler is None:
        compiler = shutil.which("cl")
    if compiler is None:
        raise RuntimeError("C++17 compiler required; cannot claim a portable behavioral pass")
    gate = GATE_SOURCE.read_text(encoding="utf-8")
    actual = compile_and_run(compiler, portable_source(gate))
    if actual.returncode:
        raise RuntimeError("Actual production C++ failed behavioral checks: "
                           + actual.stdout + actual.stderr)
    print(actual.stdout.strip())
    if args.self_test:
        mutated, count = RESTORE_GENERATION_GUARD.subn("", gate)
        if count != 1:
            raise RuntimeError("Restore-generation mutation target is missing or duplicated")
        # compile_and_run raises on compilation failure: only a running binary's
        # specific regression assertion can satisfy this negative control.
        negative = compile_and_run(compiler, portable_source(mutated))
        expected = FAILURE + RESTORE_ASSERTION
        if negative.returncode != 2 or negative.stderr.strip() != expected:
            raise RuntimeError("Mutation did not fail the expected same-beat restore assertion: "
                               + negative.stdout + negative.stderr)
        print("PASS: restore-generation guard removal compiled and was rejected by same-beat restore assertion")
        print("  " + negative.stderr.strip())
    print("Source-extracted portable C++ only; no filesystem saves; "
          "Unreal native/UHT/PIE verification remains pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
