#!/usr/bin/env python3
"""Compile the *actual* Unreal First Wake input-binding method against C++ doubles.

This validates action selection in PIE/Game and negative controls. It does NOT
run Unreal, send keystrokes, modify saves, or prove the Editor's event routing.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
CONFIG = ROOT / "Config/DefaultInput.ini"
START = "void ATSTSSExplorerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)"
END = "\nvoid ATSTSSExplorerCharacter::MoveForward(float Value)"
PREFIX = r"""
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#define TEXT(s) s
#define check(expr) do { if (!(expr)) throw std::runtime_error("Unreal check failed"); } while (false)
enum class EWorldType { PIE, Game, Editor };
struct UWorld { EWorldType WorldType; };
enum EInputEvent { IE_Pressed };
struct ATSTSSExplorerCharacter;
struct UInputComponent {
    std::vector<std::string> axes, actions;
    template <class Method>
    void BindAxis(const char* name, ATSTSSExplorerCharacter*, Method) { axes.emplace_back(name); }
    template <class Method>
    void BindAction(const char* name, EInputEvent event, ATSTSSExplorerCharacter*, Method) {
        if (event != IE_Pressed) throw std::runtime_error("Action should be pressed");
        actions.emplace_back(name);
    }
};
struct TSTSSBaseCharacter {
    void SetupPlayerInputComponent(UInputComponent*) {}
};
struct ATSTSSExplorerCharacter : TSTSSBaseCharacter {
    using Super = TSTSSBaseCharacter;
    const UWorld* world = nullptr;
    const UWorld* GetWorld() const { return world; }
    void SetupPlayerInputComponent(UInputComponent*);
    void MoveForward(float); void MoveRight(float);
    void Turn(float); void LookUp(float);
    void Interact(); void QuickSave(); void QuickLoad(); void ShowObjectiveReview();
};
// The binder receives real member-function pointers; provide no-op implementations
// only so the standalone executable links. None of these methods are executed.
void ATSTSSExplorerCharacter::MoveForward(float) {}
void ATSTSSExplorerCharacter::MoveRight(float) {}
void ATSTSSExplorerCharacter::Turn(float) {}
void ATSTSSExplorerCharacter::LookUp(float) {}
void ATSTSSExplorerCharacter::Interact() {}
void ATSTSSExplorerCharacter::QuickSave() {}
void ATSTSSExplorerCharacter::QuickLoad() {}
void ATSTSSExplorerCharacter::ShowObjectiveReview() {}
"""
SUFFIX = r"""
static unsigned cases = 0;
static void verify(bool passed, const char* what) {
    if (!passed) throw std::runtime_error(what);
    ++cases;
}
static bool hasExactly(const std::vector<std::string>& actions,
                       const std::string& name, int expected) {
    return std::count(actions.begin(), actions.end(), name) == expected;
}
int main() {
    try {
        const std::vector<std::string> expectedAxes = {
            "MoveForward", "MoveRight", "Turn", "LookUp"
        };
        for (EWorldType type : {EWorldType::PIE, EWorldType::Game, EWorldType::Editor}) {
            UWorld world{type};
            ATSTSSExplorerCharacter pawn;
            pawn.world = &world;
            UInputComponent input;
            pawn.SetupPlayerInputComponent(&input);
            verify(input.axes == expectedAxes, "Movement/camera axis bindings drifted");
            verify(hasExactly(input.actions, "Interact", 1), "Interaction unavailable");
            verify(hasExactly(input.actions, "QuickLoad", 1), "QuickLoad unavailable");
            verify(hasExactly(input.actions, "ReviewObjective", 1), "Read-only objective unavailable");
            if (type == EWorldType::PIE) {
                verify(hasExactly(input.actions, "PIEReviewQuickSave", 1),
                       "PIE must bind exactly one F6 action");
                verify(hasExactly(input.actions, "QuickSave", 0),
                       "PIE illegally binds normal F5 QuickSave");
            } else if (type == EWorldType::Game) {
                verify(hasExactly(input.actions, "QuickSave", 1),
                       "Normal Game must bind F5 QuickSave");
                verify(hasExactly(input.actions, "PIEReviewQuickSave", 0),
                       "Normal Game illegally binds PIE F6 review save");
            } else {
                verify(hasExactly(input.actions, "QuickSave", 0),
                       "Editor world must never bind normal Game QuickSave");
                verify(hasExactly(input.actions, "PIEReviewQuickSave", 0),
                       "Editor world must never bind review QuickSave");
            }
            verify(input.actions.size() == 4 || (type == EWorldType::Editor && input.actions.size() == 3),
                   "Unexpected extra or duplicated action bindings");
        }
        ATSTSSExplorerCharacter missingWorld;
        UInputComponent noWorldInput;
        missingWorld.SetupPlayerInputComponent(&noWorldInput);
        verify(hasExactly(noWorldInput.actions, "QuickSave", 0) &&
               hasExactly(noWorldInput.actions, "PIEReviewQuickSave", 0),
               "Null world must fail closed for both save bindings");
        std::cout << "PASS: " << cases
                  << " actual-source input binding C++ cases; PIE F6 separated from Game F5\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FIRST_WAKE_INPUT_BINDING_FAILURE: " << error.what() << "\n";
        return 2;
    }
}
"""


def method_from(source: str) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("Refuse changed/ambiguous SetupPlayerInputComponent boundaries")
    beginning = source.index(START)
    ending = source.index(END, beginning)
    method = source[beginning:ending]
    for token in ("Super::SetupPlayerInputComponent", "EWorldType::PIE",
                  "EWorldType::Game", 'TEXT("PIEReviewQuickSave")',
                  'TEXT("QuickSave")', 'TEXT("QuickLoad")'):
        if token not in method:
            raise ValueError("Source method missing expected selection: " + token)
    return method


def config_guard(config: str) -> None:
    mappings = re.findall(r'^\+ActionMappings=\(ActionName="([^"]+)",Key=([^)]*)\)',
                          config, re.M)
    required = {("PIEReviewQuickSave", "F6"), ("QuickSave", "F5"),
                ("QuickLoad", "F9"), ("Interact", "E"), ("ReviewObjective", "J")}
    if len(mappings) != len(set(mappings)) or not required.issubset(mappings):
        raise ValueError("DefaultInput.ini lacks unique F6 PIE / F5 Game / F9 load")
    if any(name in ("PIEReviewQuickSave", "QuickSave") and (name, key) not in required
           for name, key in mappings):
        raise ValueError("Multiple or unsafe save key declarations")


def compile_and_run(compiler: str, body: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-input-binding-") as folder:
        root = Path(folder)
        source = root / "bindings.cpp"
        is_msvc = Path(compiler).name.lower() == "cl.exe"
        executable = root / ("bindings.exe" if is_msvc else "bindings")
        source.write_text(PREFIX + body + SUFFIX, encoding="utf-8")
        if is_msvc:
            args = [compiler, "/nologo", "/std:c++17", "/EHsc", "/W4", "/WX",
                    str(source), "/Fo:" + str(root / "bindings.obj"),
                    "/Fe:" + str(executable)]
        else:
            args = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-Werror",
                    "-pedantic", str(source), "-o", str(executable)]
        build = subprocess.run(args, check=False, capture_output=True,
                               text=True, timeout=45)
        if build.returncode != 0:
            raise RuntimeError("C++ input method compilation failed: " +
                               (build.stdout + build.stderr)[-4000:])
        return subprocess.run([str(executable)], check=False,
                              capture_output=True, text=True, timeout=20)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    compiler = next((p for name in ("g++", "clang++", "c++", "cl")
                     if (p := shutil.which(name))), None)
    if not compiler:
        raise RuntimeError("No C++17 compiler: refusing compiled behavior PASS")
    config_guard(CONFIG.read_text(encoding="utf-8"))
    original = method_from(CHARACTER.read_text(encoding="utf-8"))
    result = compile_and_run(compiler, original)
    if result.returncode:
        raise RuntimeError("Original Unreal C++ input bindings failed: " +
                           result.stdout + result.stderr)
    print(result.stdout.strip())
    if args.self_test:
        for name, old, new in (
            ("PIE F5 shortcut collision", 'TEXT("PIEReviewQuickSave")', 'TEXT("QuickSave")'),
            ("Game mistakenly uses F6", 'TEXT("QuickSave")', 'TEXT("PIEReviewQuickSave")'),
        ):
            if original.count(old) != 1:
                raise RuntimeError("Mutation anchor missing or ambiguous: " + name)
            mutation = original.replace(old, new, 1)
            rejected = compile_and_run(compiler, mutation)
            if rejected.returncode == 0 or "FIRST_WAKE_INPUT_BINDING_FAILURE" not in rejected.stderr:
                raise RuntimeError("Unsafe mutation not detected: " + name)
            print("PASS: rejected unsafe " + name)
        invalid = CONFIG.read_text(encoding="utf-8").replace(
            'ActionName="PIEReviewQuickSave",Key=F6',
            'ActionName="PIEReviewQuickSave",Key=F5', 1)
        try:
            config_guard(invalid)
        except ValueError:
            print("PASS: rejected F6-to-F5 config mutation")
        else:
            raise RuntimeError("Unsafe F6 mapping mutation accepted")
    print("Source-extracted C++ API-double proof ONLY. Actual Unreal/PIE keyboard and saves untested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
