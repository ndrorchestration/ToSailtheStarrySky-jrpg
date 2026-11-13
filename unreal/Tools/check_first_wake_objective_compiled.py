#!/usr/bin/env python3
"""Portable C++ behavioral probe of the actual read-only First Wake objective method.

Compiles the exact implementation body taken from TSTSSFirstWakeState.cpp
against narrow stdlib-only stand-ins. Does NOT execute Unreal, UHT, Blueprint,
keyboard controls, save/load, renderer or PIE.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp"
METHOD = "FString UTSTSSFirstWakeState::GetReviewObjectiveText() const"
NEXT_METHOD = "\nbool UTSTSSFirstWakeState::AdvanceTo"

PREFIX = r"""
#include <cstdint>
#include <iostream>
#include <string>
#define TEXT(s) s
using FString = std::string;
enum class ETSTSSFirstWakeBeat : std::uint8_t {
    FlyerDiscovered, IoniaHired, BoardedAureateWake,
    EngineeringChecked, Launched, SeaContact, FlotationConfirmed,
    EmptyReserveInspected, ReturnedToBerth
};
class UTSTSSFirstWakeState {
public:
    bool bStarted = false;
    ETSTSSFirstWakeBeat CurrentBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    std::uint8_t InspectionMask = 0;
    FString GetReviewObjectiveText() const;
};
"""

SUFFIX = r"""
struct Case {
    bool started;
    ETSTSSFirstWakeBeat beat;
    std::uint8_t mask;
    const char* expected;
};
int main() {
    const Case cases[] = {
        {false, ETSTSSFirstWakeBeat::FlyerDiscovered, 0, "Find Ionia's flyer"},
        {true, ETSTSSFirstWakeBeat::FlyerDiscovered, 0, "Speak with Captain Ionia"},
        {true, ETSTSSFirstWakeBeat::IoniaHired, 0, "Board the Aureate Wake"},
        {true, ETSTSSFirstWakeBeat::BoardedAureateWake, 0, "Inspect the levitation lift"},
        {true, ETSTSSFirstWakeBeat::BoardedAureateWake, 1, "Inspect the pressure systems"},
        {true, ETSTSSFirstWakeBeat::BoardedAureateWake, 3, "Inspect the reserve systems"},
        {true, ETSTSSFirstWakeBeat::BoardedAureateWake, 5, "Inspect the pressure systems"},
        {true, ETSTSSFirstWakeBeat::BoardedAureateWake, 7, "Complete engineering signoff"},
        {true, ETSTSSFirstWakeBeat::EngineeringChecked, 7, "Prepare for the First Wake launch"},
        {true, ETSTSSFirstWakeBeat::Launched, 7, "Navigate the First Wake flight"},
        {true, ETSTSSFirstWakeBeat::SeaContact, 7, "Stabilize the water landing"},
        {true, ETSTSSFirstWakeBeat::FlotationConfirmed, 7, "Survey the hull and harmonic systems"},
        {true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 7, "Continue to the coastal survey"},
        {true, ETSTSSFirstWakeBeat::ReturnedToBerth, 7, "First Wake review sequence complete"},
        {true, static_cast<ETSTSSFirstWakeBeat>(255), 7, "Review objective unavailable"},
        {false, ETSTSSFirstWakeBeat::ReturnedToBerth, 7, "Find Ionia's flyer"}
    };
    unsigned passed = 0;
    for (const Case& c : cases) {
        UTSTSSFirstWakeState state;
        state.bStarted = c.started;
        state.CurrentBeat = c.beat;
        state.InspectionMask = c.mask;
        const FString objective = state.GetReviewObjectiveText();
        const FString repeat = state.GetReviewObjectiveText();
        if (objective != c.expected || repeat != objective ||
            state.bStarted != c.started || state.CurrentBeat != c.beat ||
            state.InspectionMask != c.mask) {
            std::cerr << "Mismatch at case " << passed
                      << ": got [" << objective << "], expected ["
                      << c.expected << "] or state mutated\n";
            return 2;
        }
        ++passed;
    }
    std::cout << "PASS: " << passed
              << " real-source portable C++ objective cases; no state mutations\n";
    return 0;
}
"""


def extract_method(source: str) -> str:
    if source.count(METHOD) != 1 or source.count(NEXT_METHOD) != 1:
        raise ValueError("Unrecognized First Wake objective method boundaries")
    start = source.index(METHOD)
    end = source.index(NEXT_METHOD, start)
    body = source[start:end]
    if "switch (CurrentBeat)" not in body or "if (!bStarted)" not in body:
        raise ValueError("Missing core read-only objective branches")
    return body


def compile_and_run(compiler: str, method: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-objective-compiled-") as td:
        root = Path(td)
        src = root / "objective_probe.cpp"
        executable = root / "objective_probe"
        src.write_text(PREFIX + method + SUFFIX, encoding="utf-8")
        is_msvc = Path(compiler).name.lower() == "cl.exe"
        if is_msvc:
            executable = root / "objective_probe.exe"
            args = [compiler, "/nologo", "/std:c++17", "/EHsc",
                    "/W4", "/WX", str(src),
                    "/Fo:" + str(root / "objective_probe.obj"),
                    "/Fe:" + str(executable)]
        else:
            args = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-Werror",
                    "-pedantic", str(src), "-o", str(executable)]
        compiled = subprocess.run(
            args, check=False, capture_output=True, text=True, timeout=45,
        )
        if compiled.returncode != 0:
            raise RuntimeError("Portable C++ objective compile failed: " + compiled.stderr[-4000:])
        return subprocess.run(
            [str(executable)], check=False, capture_output=True, text=True, timeout=20,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true",
                        help="also ensure an injected wrong objective fails the probe")
    args = parser.parse_args()
    compiler = next((p for name in ("g++", "clang++", "c++")
                     if (p := shutil.which(name))), None)
    if compiler is None:
        compiler = shutil.which("cl")
    if compiler is None:
        raise RuntimeError("No C++17 compiler; cannot claim compiled behavioral pass")
    method = extract_method(SOURCE.read_text(encoding="utf-8"))
    actual = compile_and_run(compiler, method)
    if actual.returncode != 0:
        raise RuntimeError("Actual C++ method failed behavioral checks: "
                           + actual.stdout + actual.stderr)
    print(actual.stdout.strip())
    if args.self_test:
        expected = 'return TEXT("Inspect the levitation lift");'
        if method.count(expected) != 1:
            raise RuntimeError("Negative control target is missing or duplicated")
        altered = method.replace(expected, 'return TEXT("WRONG_INJECTED_OBJECTIVE");', 1)
        negative = compile_and_run(compiler, altered)
        if negative.returncode == 0:
            raise RuntimeError("Behavioral probe failed to detect mutated objective")
        if "Mismatch at case" not in negative.stderr:
            raise RuntimeError("Negative control did not fail for expected reason")
        print("PASS: semantic mutation control rejected wrong objective")
        # Protect the creator-revised post-splashdown objective separately.
        coastal = 'return TEXT("Continue to the coastal survey");'
        if method.count(coastal) != 1:
            raise RuntimeError("Negative coastal survey control target missing")
        mutated_coastal = method.replace(
            coastal, 'return TEXT("WRONG_COASTAL_RECOVERY_OBJECTIVE");', 1)
        coastal_failure = compile_and_run(compiler, mutated_coastal)
        if (coastal_failure.returncode == 0 or
                "Mismatch at case 12" not in coastal_failure.stderr):
            raise RuntimeError("Coastal-survey objective mutation was not caught")
        print("PASS: creator-revised coastal objective mutation rejected")

    print("Source-extracted portable C++ only; Unreal native/editor verification remains pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
