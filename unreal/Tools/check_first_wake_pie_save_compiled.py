#!/usr/bin/env python3
"""Compile and execute the *actual* First Wake F5/F9 handler bodies with API doubles.

Portable behavioral smoke for the existing PIE isolation patch. Does not
compile Unreal, run PIE, touch disk saves or verify actual engine semantics.
Fail closed if the source method boundaries drift or C++17 is unavailable.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
SAVE_START = "void ATSTSSExplorerCharacter::QuickSave()\n"
LOAD_START = "void ATSTSSExplorerCharacter::QuickLoad()\n"
METHOD_END = "bool ATSTSSExplorerCharacter::SaveFirstWake("

PREFIX = r"""
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#define TEXT(s) s
using FString = std::string;
enum class EWorldType { PIE, Game };
struct UWorld { EWorldType WorldType; };
struct UGameplayStatics {
    static std::unordered_map<FString, int> Slots;
    static bool DoesSaveGameExist(const FString& slot, int) {
        return Slots.find(slot) != Slots.end();
    }
};
std::unordered_map<FString, int> UGameplayStatics::Slots;
static int protectedSaveWarnings = 0;
static int protectedLoadWarnings = 0;
static int lastStatus = -1;
static int objectivesDisplayed = 0;
void ShowFirstWakeReviewProtectedSlotWarning(bool isLoad) {
    if (isLoad) ++protectedLoadWarnings;
    else ++protectedSaveWarnings;
}
void ShowFirstWakeReviewSaveLoadStatus(bool isLoad, bool succeeded) {
    lastStatus = (isLoad ? 2 : 0) + (succeeded ? 1 : 0);
}
struct UTSTSSFirstWakeState {};
namespace EKeys { static constexpr int LeftShift = 1; static constexpr int RightShift = 2; }
struct APlayerController {
    bool leftShift = false;
    bool rightShift = false;
    bool IsInputKeyDown(int key) const {
        return key == EKeys::LeftShift ? leftShift : (key == EKeys::RightShift && rightShift);
    }
};
template <typename T> T* Cast(APlayerController* p) { return static_cast<T*>(p); }
void ShowFirstWakeReviewObjective(UTSTSSFirstWakeState*) {
    ++objectivesDisplayed;
}
struct ATSTSSExplorerCharacter {
    UWorld* world = nullptr;
    APlayerController controller;
    bool bHasController = true;
    APlayerController* GetController() { return bHasController ? &controller : nullptr; }
    bool bPIEReviewQuickSlotOwned = false;
    bool bSaveSuccess = true;
    bool bLoadSuccess = true;
    int saves = 0;
    int loads = 0;
    int writes = 0;
    FString lastSaveSlot;
    FString lastLoadSlot;
    UTSTSSFirstWakeState state;
    UTSTSSFirstWakeState* FirstWakeState = &state;
    UWorld* GetWorld() const { return world; }
    bool SaveFirstWake(const FString& slot) {
        ++saves;
        lastSaveSlot = slot;
        if (!bSaveSuccess) return false;
        UGameplayStatics::Slots[slot] = ++writes;
        return true;
    }
    bool LoadFirstWake(const FString& slot) {
        ++loads;
        lastLoadSlot = slot;
        return bLoadSuccess && UGameplayStatics::DoesSaveGameExist(slot, 0);
    }
    void QuickSave();
    void QuickLoad();
};
"""

SUFFIX = r"""
static int cases = 0;
static void check(bool condition, const char* description) {
    if (!condition) throw std::runtime_error(description);
    ++cases;
}
int main() {
    try {
        UWorld pie{EWorldType::PIE};
        UWorld game{EWorldType::Game};
        const FString reviewSlot = "tstss_prelude_pie_quick";
        const FString playerSlot = "first_wake_quick";

        ATSTSSExplorerCharacter noSave;
        noSave.world = &pie;
        noSave.QuickLoad();
        check(noSave.loads == 0 && protectedLoadWarnings == 1,
              "Unowned PIE quickload was not refused");

        ATSTSSExplorerCharacter shiftStopLeft;
        shiftStopLeft.world = &pie;
        shiftStopLeft.controller.leftShift = true;
        shiftStopLeft.QuickSave();
        check(shiftStopLeft.saves == 0 && !shiftStopLeft.bPIEReviewQuickSlotOwned &&
                  !UGameplayStatics::DoesSaveGameExist(reviewSlot, 0),
              "Shift+F5 Stop PIE unexpectedly created a quicksave");

        ATSTSSExplorerCharacter shiftStopRight;
        shiftStopRight.world = &pie;
        shiftStopRight.controller.rightShift = true;
        shiftStopRight.QuickSave();
        check(shiftStopRight.saves == 0 &&
                  !UGameplayStatics::DoesSaveGameExist(reviewSlot, 0),
              "RightShift+F5 unexpectedly created a quicksave");

        ATSTSSExplorerCharacter unpossessed;
        unpossessed.world = &pie;
        unpossessed.bHasController = false;
        unpossessed.QuickSave();
        check(unpossessed.saves == 0 &&
                  !UGameplayStatics::DoesSaveGameExist(reviewSlot, 0),
              "Unpossessed PIE character unexpectedly saved");

        UGameplayStatics::Slots[reviewSlot] = 777;
        ATSTSSExplorerCharacter oldSession;
        oldSession.world = &pie;
        oldSession.QuickSave();
        check(oldSession.saves == 0 && !oldSession.bPIEReviewQuickSlotOwned &&
                  UGameplayStatics::Slots[reviewSlot] == 777 &&
                  protectedSaveWarnings == 1,
              "PIE overwrote an existing review save");
        oldSession.QuickLoad();
        check(oldSession.loads == 0 && protectedLoadWarnings == 2 &&
                  UGameplayStatics::Slots[reviewSlot] == 777,
              "PIE adopted old review save for load");

        UGameplayStatics::Slots.clear();
        ATSTSSExplorerCharacter failedSave;
        failedSave.world = &pie;
        failedSave.bSaveSuccess = false;
        failedSave.QuickSave();
        check(failedSave.saves == 1 && !failedSave.bPIEReviewQuickSlotOwned &&
                  !UGameplayStatics::DoesSaveGameExist(reviewSlot, 0) &&
                  lastStatus == 0, "Failed PIE save was misreported/owned");

        ATSTSSExplorerCharacter owned;
        owned.world = &pie;
        owned.QuickSave();
        check(owned.saves == 1 && owned.bPIEReviewQuickSlotOwned &&
                  owned.lastSaveSlot == reviewSlot &&
                  UGameplayStatics::Slots[reviewSlot] == 1 &&
                  !UGameplayStatics::DoesSaveGameExist(playerSlot, 0) &&
                  lastStatus == 1, "New PIE save failed to use isolated slot");
        owned.QuickSave();
        check(owned.saves == 2 && UGameplayStatics::Slots[reviewSlot] == 2,
              "Same-session PIE save update incorrectly refused");
        owned.QuickLoad();
        check(owned.loads == 1 && owned.lastLoadSlot == reviewSlot &&
                  objectivesDisplayed == 1 && lastStatus == 3,
              "Owned PIE reload failed or did not refresh objective");
        owned.bLoadSuccess = false;
        owned.QuickLoad();
        check(owned.loads == 2 && objectivesDisplayed == 1 && lastStatus == 2,
              "Failed PIE reload misreported success");

        ATSTSSExplorerCharacter secondSession;
        secondSession.world = &pie;
        secondSession.QuickSave();
        secondSession.QuickLoad();
        check(secondSession.saves == 0 && secondSession.loads == 0 &&
                  UGameplayStatics::Slots[reviewSlot] == 2,
              "Second PIE session read or replaced first session's slot");

        UGameplayStatics::Slots.clear();
        ATSTSSExplorerCharacter runtime;
        runtime.world = &game;
        runtime.QuickSave();
        check(runtime.saves == 1 && runtime.lastSaveSlot == playerSlot &&
                  UGameplayStatics::DoesSaveGameExist(playerSlot, 0) &&
                  !runtime.bPIEReviewQuickSlotOwned,
              "Non-PIE save was redirected to test slot");
        runtime.QuickLoad();
        check(runtime.loads == 1 && runtime.lastLoadSlot == playerSlot &&
                  lastStatus == 3, "Non-PIE load broke existing player slot");
        ATSTSSExplorerCharacter failingRuntime;
        failingRuntime.world = &game;
        failingRuntime.bSaveSuccess = false;
        failingRuntime.QuickSave();
        check(failingRuntime.saves == 1 && lastStatus == 0 &&
                  UGameplayStatics::Slots[playerSlot] == 1,
              "Failed normal save overwrote or claimed success");
        std::cout << "PASS: " << cases
                  << " actual-handler portable C++ F5/F9 cases; no real disk save\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "HANDLER_BEHAVIOR_FAILURE: " << e.what() << "\n";
        return 2;
    }
}
"""


def extract_methods(code: str) -> str:
    for marker in (SAVE_START, LOAD_START, METHOD_END):
        if code.count(marker) != 1:
            raise ValueError("F5/F9 handler boundaries changed: " + marker)
    start = code.index(SAVE_START)
    load = code.index(LOAD_START, start)
    end = code.index(METHOD_END, load)
    method_code = code[start:end]
    if not (start < load < end):
        raise ValueError("F5/F9 handler order changed")
    for token in ("EWorldType::PIE", "tstss_prelude_pie_quick",
                  "bPIEReviewQuickSlotOwned", "GetController()",
                  "PC->IsInputKeyDown(EKeys::LeftShift)",
                  "PC->IsInputKeyDown(EKeys::RightShift)",
                  "UGameplayStatics::DoesSaveGameExist"):
        if token not in method_code:
            raise ValueError("PIE safety logic missing: " + token)
    return method_code


def compiled_run(compiler: str, methods: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-f5f9-portable-") as tmp:
        src = Path(tmp) / "f5f9.cpp"
        executable = Path(tmp) / "f5f9"
        src.write_text(PREFIX + methods + SUFFIX, encoding="utf-8")
        build = subprocess.run(
            [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-Werror",
             "-pedantic", str(src), "-o", str(executable)],
            check=False, capture_output=True, text=True, timeout=45,
        )
        if build.returncode:
            raise RuntimeError("Portable handler compile failed:\n" + build.stderr[-5000:])
        return subprocess.run([str(executable)], check=False, capture_output=True,
                              text=True, timeout=25)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    compiler = next((binary for name in ("g++", "clang++", "c++")
                     if (binary := shutil.which(name))), None)
    if compiler is None:
        raise RuntimeError("C++17 compiler required for behavioral evidence")
    methods = extract_methods(CHARACTER.read_text(encoding="utf-8"))
    actual = compiled_run(compiler, methods)
    if actual.returncode:
        raise RuntimeError("Actual handler failed: " + actual.stdout + actual.stderr)
    print(actual.stdout.strip())
    if args.self_test:
        anchor = "if (bPIE && !bPIEReviewQuickSlotOwned &&"
        if methods.count(anchor) != 1:
            raise RuntimeError("PIE mutation control anchor missing/duplicated")
        mutation = methods.replace(anchor, "if (false && !bPIEReviewQuickSlotOwned &&", 1)
        rejected = compiled_run(compiler, mutation)
        if rejected.returncode == 0 or "HANDLER_BEHAVIOR_FAILURE" not in rejected.stderr:
            raise RuntimeError("Probe failed to reject intentionally unsafe PIE overwrite")
        print("PASS: unsafe pre-existing-slot overwrite mutation detected")
        for pressed_modifier in ("EKeys::LeftShift", "EKeys::RightShift"):
            anchor = f"PC->IsInputKeyDown({pressed_modifier})"
            if methods.count(anchor) != 1:
                raise RuntimeError("PIE Stop shortcut mutation anchor missing: " + anchor)
            changed = methods.replace(anchor, "false", 1)
            unsafe = compiled_run(compiler, changed)
            if unsafe.returncode == 0 or "HANDLER_BEHAVIOR_FAILURE" not in unsafe.stderr:
                raise RuntimeError("Shift+F5 safety mutation was not caught: " + anchor)
            print(f"PASS: Shift+F5 save guard mutation rejected ({pressed_modifier})")
    print("Only exact C++ method bodies tested with stand-ins; Unreal Editor and PIE unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
