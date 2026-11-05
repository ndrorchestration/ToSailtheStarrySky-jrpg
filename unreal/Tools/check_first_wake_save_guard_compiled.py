#!/usr/bin/env python3
"""Compile the *actual* SaveFirstWake C++ method against in-memory stand-ins.

Behavioral evidence only: no Unreal engine, filesystem saves, or player's
stored roster. Mutation control must catch disabled roster-protection guard.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
START = "bool ATSTSSExplorerCharacter::SaveFirstWake(const FString& Slot)\n"
END = "bool ATSTSSExplorerCharacter::LoadFirstWake(const FString& Slot)\n"

PREFIX = r"""
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
using FString = std::string;
template <typename T> bool IsValid(const T* p) { return p != nullptr; }
struct UWorld {};
struct FakeRoster {
    std::vector<int> Values;
    int Num() const { return static_cast<int>(Values.size()); }
};
struct UTSTSSSaveGame {
    bool bFirstWakeStarted = false;
    int FirstWakeBeat = 0;
    unsigned char InspectionMask = 0;
    FakeRoster PartyRoster;
    int OpaqueFutureField = 0;
    bool StructurallyValid = true;
};
struct FakeFirstWakeState {
    bool Started = true;
    int Beat = 2;
    unsigned char Mask = 1;
    bool HasStarted() const { return Started; }
    int GetCurrentBeat() const { return Beat; }
    unsigned char GetInspectionMask() const { return Mask; }
};
struct ATSTSSExplorerCharacter {
    FakeFirstWakeState* FirstWakeState = nullptr;
    bool SaveFirstWake(const FString& Slot);
};
template <typename T> T* NewObject(ATSTSSExplorerCharacter*) { return new T(); }
struct UGameplayStatics {
    static std::map<FString, UTSTSSSaveGame> Slots;
    static bool DoesSaveGameExist(const FString& slot, int) {
        return Slots.find(slot) != Slots.end();
    }
};
std::map<FString, UTSTSSSaveGame> UGameplayStatics::Slots;
struct UTSTSSPersistence {
    static bool FailSave;
    static bool FailLoad;
    static int Writes;
    static int Reads;
    static bool IsValidSlotName(const FString& slot) {
        if (slot.empty() || slot.size() > 48) return false;
        for (char c : slot) {
            if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                  (c >= '0' && c <= '9') || c == '_' || c == '-')) return false;
        }
        return true;
    }
    static UTSTSSSaveGame* LoadProgress(const FString& slot) {
        ++Reads;
        if (FailLoad) return nullptr;
        auto it = UGameplayStatics::Slots.find(slot);
        if (it == UGameplayStatics::Slots.end() ||
            !it->second.StructurallyValid) return nullptr;
        // Simulate LoadGameFromSlot returning an isolated in-memory object.
        return new UTSTSSSaveGame(it->second);
    }
    static bool SaveProgress(const FString& slot, UTSTSSSaveGame* saved) {
        ++Writes;
        if (FailSave || !IsValidSlotName(slot) || !saved ||
            !saved->StructurallyValid) return false;
        UGameplayStatics::Slots[slot] = *saved;
        return true;
    }
};
bool UTSTSSPersistence::FailSave = false;
bool UTSTSSPersistence::FailLoad = false;
int UTSTSSPersistence::Writes = 0;
int UTSTSSPersistence::Reads = 0;
"""

SUFFIX = r"""
int cases = 0;
void check(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
    ++cases;
}
void reset() {
    UGameplayStatics::Slots.clear();
    UTSTSSPersistence::FailSave = false;
    UTSTSSPersistence::FailLoad = false;
    UTSTSSPersistence::Writes = 0;
    UTSTSSPersistence::Reads = 0;
}
int main() {
    try {
        reset();
        FakeFirstWakeState story{};
        ATSTSSExplorerCharacter pawn{&story};
        check(!pawn.SaveFirstWake("unsafe name") && UTSTSSPersistence::Writes == 0,
              "Invalid slot must refuse before writing");
        ATSTSSExplorerCharacter missing{nullptr};
        check(!missing.SaveFirstWake("first_wake_quick") &&
              UTSTSSPersistence::Writes == 0,
              "Missing story state was written");
        check(pawn.SaveFirstWake("first_wake_quick") &&
              UGameplayStatics::Slots["first_wake_quick"].bFirstWakeStarted &&
              UGameplayStatics::Slots["first_wake_quick"].FirstWakeBeat == 2 &&
              UGameplayStatics::Slots["first_wake_quick"].InspectionMask == 1 &&
              UGameplayStatics::Slots["first_wake_quick"].PartyRoster.Num() == 0 &&
              UTSTSSPersistence::Reads == 0,
              "New story-only save failed");

        reset();
        UTSTSSSaveGame existing;
        existing.OpaqueFutureField = 1001;
        existing.FirstWakeBeat = 3;
        UGameplayStatics::Slots["first_wake_quick"] = existing;
        check(pawn.SaveFirstWake("first_wake_quick") &&
              UGameplayStatics::Slots["first_wake_quick"].OpaqueFutureField == 1001 &&
              UGameplayStatics::Slots["first_wake_quick"].FirstWakeBeat == story.Beat &&
              UTSTSSPersistence::Reads == 1,
              "Safe roster-free save must preserve other fields");

        reset();
        UTSTSSSaveGame player;
        player.PartyRoster.Values = {1, 2, 3};
        player.OpaqueFutureField = 202;
        player.FirstWakeBeat = 7;
        UGameplayStatics::Slots["first_wake_quick"] = player;
        check(!pawn.SaveFirstWake("first_wake_quick") &&
              UTSTSSPersistence::Writes == 0 &&
              UTSTSSPersistence::Reads == 1 &&
              UGameplayStatics::Slots["first_wake_quick"].PartyRoster.Num() == 3 &&
              UGameplayStatics::Slots["first_wake_quick"].FirstWakeBeat == 7,
              "Existing player party was overwritten by story-only save");

        reset();
        player.PartyRoster.Values = {42};
        UGameplayStatics::Slots["tstss_prelude_pie_quick"] = player;
        check(!pawn.SaveFirstWake("tstss_prelude_pie_quick") &&
              UTSTSSPersistence::Writes == 0 &&
              UGameplayStatics::Slots["tstss_prelude_pie_quick"].PartyRoster.Num() == 1,
              "PIE programmatic save overwrote roster data");

        reset();
        existing.StructurallyValid = false;
        UGameplayStatics::Slots["first_wake_quick"] = existing;
        check(!pawn.SaveFirstWake("first_wake_quick") &&
              UTSTSSPersistence::Writes == 0 &&
              UGameplayStatics::Slots["first_wake_quick"].StructurallyValid == false,
              "Corrupt/unsupported existing save was overwritten");

        reset();
        UGameplayStatics::Slots["first_wake_quick"] = UTSTSSSaveGame{};
        UTSTSSPersistence::FailLoad = true;
        check(!pawn.SaveFirstWake("first_wake_quick") &&
              UTSTSSPersistence::Writes == 0 &&
              UTSTSSPersistence::Reads == 1,
              "Unreadable existing slot was overwritten");

        reset();
        UTSTSSPersistence::FailSave = true;
        check(!pawn.SaveFirstWake("first_wake_quick") &&
              UGameplayStatics::Slots.empty(),
              "Failure in persistence was treated as a successful save");

        reset();
        story.Started = false;
        story.Beat = 0;
        story.Mask = 0;
        check(pawn.SaveFirstWake("first_wake_quick") &&
              !UGameplayStatics::Slots["first_wake_quick"].bFirstWakeStarted &&
              UGameplayStatics::Slots["first_wake_quick"].FirstWakeBeat == 0 &&
              UGameplayStatics::Slots["first_wake_quick"].InspectionMask == 0,
              "Fresh unstarted story snapshot was not preserved");

        std::cout << "PASS: " << cases
                  << " real-body C++ First Wake SaveFirstWake guard cases; no real saves\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "SAVE_GUARD_BEHAVIOR_FAILURE: " << error.what() << "\n";
        return 2;
    }
}
"""


def extract(code: str) -> str:
    for marker in (START, END):
        if code.count(marker) != 1:
            raise ValueError("SaveFirstWake handler boundary changed")
    start, end = code.index(START), code.index(END)
    if not start < end:
        raise ValueError("SaveFirstWake handler moved after load")
    method = code[start:end]
    for token in ("UGameplayStatics::DoesSaveGameExist(Slot, 0)",
                  "UTSTSSPersistence::LoadProgress(Slot)",
                  "Save->PartyRoster.Num() != 0",
                  "UTSTSSPersistence::IsValidSlotName(Slot)",
                  "UTSTSSPersistence::SaveProgress(Slot, Save)"):
        if token not in method:
            raise ValueError("Required guard missing: " + token)
    return method


def build_run(compiler: str, method: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-real-save-guard-") as directory:
        root = Path(directory)
        source = root / "save.cpp"
        binary = root / ("save.exe" if Path(compiler).name.lower() == "cl.exe" else "save")
        source.write_text(PREFIX + method + SUFFIX, encoding="utf-8")
        if Path(compiler).name.lower() == "cl.exe":
            # Mutation tests intentionally compile constant-false conditions;
            # suppress only MSVC C4127 while keeping all other warnings fatal.
            command = [compiler, "/nologo", "/std:c++17", "/EHsc", "/W4",
                       "/WX", "/wd4127", str(source), "/Fo:" + str(root / "save.obj"),
                       "/Fe:" + str(binary)]
        else:
            command = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra",
                       "-Werror", "-pedantic", str(source), "-o", str(binary)]
        built = subprocess.run(
            command, capture_output=True, text=True, timeout=45, check=False)
        if built.returncode:
            raise RuntimeError("C++ portable compile failed: " + (built.stdout + built.stderr)[-5000:])
        return subprocess.run([str(binary)], capture_output=True, text=True,
                              timeout=25, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    compiler = next((exe for name in ("g++", "clang++", "c++", "cl")
                     if (exe := shutil.which(name))), None)
    if compiler is None:
        raise RuntimeError("C++17 compiler required: native Unreal not available")
    method = extract(SOURCE.read_text(encoding="utf-8"))
    actual = build_run(compiler, method)
    if actual.returncode:
        raise RuntimeError(actual.stdout + actual.stderr)
    print(actual.stdout.strip())
    if args.self_test:
        anchor = "Save->PartyRoster.Num() != 0"
        if method.count(anchor) != 1:
            raise RuntimeError("Roster protection mutation anchor missing/duplicated")
        mutated = method.replace(anchor, "false", 1)
        bad = build_run(compiler, mutated)
        if bad.returncode == 0 or "SAVE_GUARD_BEHAVIOR_FAILURE" not in bad.stderr:
            raise RuntimeError("Mutation control did not catch unprotected roster overwrite")
        print("PASS: deliberate existing-roster overwrite mutation rejected")
    print("Only the actual C++ method compiled with API doubles; UE native save/load still untested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
