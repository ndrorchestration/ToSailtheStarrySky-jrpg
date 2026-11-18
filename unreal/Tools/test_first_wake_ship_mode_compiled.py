#!/usr/bin/env python3
"""Compile and execute the ACTUAL inline First Wake ship-mode gate with C++ stand-ins.

Source-only engine-free verification. This does NOT run Unreal, validate actual
ship geometry, authorize cinematic transitions or establish PIE gameplay.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HEADER = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Public/TSTSSFirstWakeState.h")
METHODS = (
    "bool IsChapterOneActOne() const",
    "bool IsSeabourneRecoveryLocked() const",
    "FName GetReviewShipMode() const",
    "bool IsReviewShipModeAuthorized(FName RequestedMode) const",
)
MODEL = r"""
#include <cstdint>
#include <iostream>
#include <string>
#define TEXT(x) x
using uint8 = std::uint8_t;
struct FName {
    std::string Value;
    FName() = default;
    explicit FName(const char* v) : Value(v) {}
    bool IsNone() const { return Value.empty(); }
    bool operator==(const FName& other) const { return Value == other.Value; }
};
static const FName NAME_None;
enum class ETSTSSFirstWakeBeat : uint8 {
    FlyerDiscovered, IoniaHired, BoardedAureateWake, EngineeringChecked,
    Launched, SeaContact, FlotationConfirmed, EmptyReserveInspected,
    ReturnedToBerth
};
class UTSTSSFirstWakeState {
public:
    bool bStarted = false;
    ETSTSSFirstWakeBeat CurrentBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
__ACTUAL_METHODS__
};
int main() {
    using Beat = ETSTSSFirstWakeBeat;
    UTSTSSFirstWakeState story;
    auto check = [&story](bool started, Beat beat, const FName& expected) {
        story.bStarted = started;
        story.CurrentBeat = beat;
        if (!(story.GetReviewShipMode() == expected)) return false;
        if (story.IsReviewShipModeAuthorized(FName(TEXT("Starbourne")))) return false;
        if (story.IsReviewShipModeAuthorized(FName(TEXT("Submersible")))) return false;
        const bool sea = expected == FName(TEXT("Seabourne"));
        const bool sky = expected == FName(TEXT("Skybourne"));
        if (story.IsReviewShipModeAuthorized(FName(TEXT("Seabourne"))) != sea ||
            story.IsReviewShipModeAuthorized(FName(TEXT("Skybourne"))) != sky) return false;
        return true;
    };
    const Beat beats[] = {
        Beat::FlyerDiscovered, Beat::IoniaHired, Beat::BoardedAureateWake,
        Beat::EngineeringChecked, Beat::Launched, Beat::SeaContact,
        Beat::FlotationConfirmed, Beat::EmptyReserveInspected,
        Beat::ReturnedToBerth
    };
    const FName expected[] = {
        FName(TEXT("Seabourne")), FName(TEXT("Seabourne")),
        FName(TEXT("Seabourne")), FName(TEXT("Seabourne")),
        FName(TEXT("Skybourne")), FName(TEXT("Skybourne")),
        FName(TEXT("Seabourne")), FName(TEXT("Seabourne")),
        FName(TEXT("Seabourne"))
    };
    for (unsigned i = 0; i < 9; ++i) {
        if (!check(false, beats[i], NAME_None)) {
            std::cerr << "Unstarted mode leak at " << i << "\\n"; return 1;
        }
        if (!check(true, beats[i], expected[i])) {
            std::cerr << "Incorrect ship-mode authorization at " << i << "\\n"; return 2;
        }
    }
    std::cout << "PASS: 18 actual-source beat checks; unknown forms denied\\n";
    return 0;
}
"""

def extract_method(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0 or source.find(signature, start + 1) >= 0:
        raise ValueError("missing or duplicate method: " + signature)
    open_brace = source.find("{", start + len(signature))
    if open_brace < 0:
        raise ValueError("missing body: " + signature)
    level = 0
    for pos in range(open_brace, len(source)):
        if source[pos] == "{":
            level += 1
        elif source[pos] == "}":
            level -= 1
            if level == 0:
                return source[start:pos + 1]
    raise ValueError("unclosed method: " + signature)

def compile_and_run(source: str, compiler: str) -> tuple[int, str]:
    implementations = "\n".join(extract_method(source, sig) for sig in METHODS)
    code = MODEL.replace("__ACTUAL_METHODS__", implementations)
    with tempfile.TemporaryDirectory(prefix="tstss-shipmode-") as temp:
        source_file = Path(temp) / "probe.cpp"
        executable = Path(temp) / "probe"
        source_file.write_text(code, encoding="utf8")
        build = subprocess.run([compiler, "-std=c++17", "-O0", "-Wall",
                                "-Wextra", "-Werror", str(source_file),
                                "-o", str(executable)], capture_output=True,
                               text=True, timeout=40)
        if build.returncode:
            raise AssertionError("Portable C++ compile failed: " + build.stderr[-4000:])
        run = subprocess.run([str(executable)], capture_output=True,
                             text=True, timeout=10)
        return run.returncode, run.stdout + run.stderr

class ActualSourceShipMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HEADER.read_text(encoding="utf8")
        cls.compiler = shutil.which("g++") or shutil.which("clang++")
        if not cls.compiler:
            raise unittest.SkipTest("No portable C++ compiler on this host")

    def test_actual_inline_policy_accepts_only_expected_beats(self):
        code, report = compile_and_run(self.source, self.compiler)
        self.assertEqual(code, 0, report)
        self.assertIn("PASS: 18 actual-source beat checks", report)

    def test_mutation_prelaunch_skybourne_is_rejected(self):
        before = "static_cast<uint8>(ETSTSSFirstWakeBeat::Launched)"
        after = "static_cast<uint8>(ETSTSSFirstWakeBeat::EngineeringChecked)"
        self.assertEqual(self.source.count(before), 1)
        code, report = compile_and_run(self.source.replace(before, after, 1),
                                       self.compiler)
        self.assertNotEqual(code, 0, report)

    def test_mutation_premature_recovery_lock_is_rejected(self):
        before = "static_cast<uint8>(ETSTSSFirstWakeBeat::FlotationConfirmed)"
        after = "static_cast<uint8>(ETSTSSFirstWakeBeat::SeaContact)"
        self.assertEqual(self.source.count(before), 1)
        code, report = compile_and_run(self.source.replace(before, after, 1),
                                       self.compiler)
        self.assertNotEqual(code, 0, report)

if __name__ == "__main__":
    unittest.main()
