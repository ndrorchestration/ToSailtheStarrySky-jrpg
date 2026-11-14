#!/usr/bin/env python3
"""Compile and exercise the REAL editor-only camera restore method with C++ doubles.

Covers pending entry cancellation, active preview return, outside camera
ownership, borrowed/owned presentation intent and idempotence.
This is NOT native Unreal, a PIE test, or proof of final cinematic quality.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
START = "void ATSTSSExplorerCharacter::RestoreEngineFocusPreview()\n{"
END = "\n#endif // WITH_EDITOR"

PREFIX = r"""
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#define TEXT(value) value
#define UE_LOG(...) do {} while (false)
enum EViewTargetBlendFunction { VTBlend_EaseInOut };
struct FName {
    std::string name;
    explicit FName(const char* value) : name(value) {}
    friend bool operator==(const FName& a, const FName& b) {
        return a.name == b.name;
    }
};
struct FTSTSSPresentationIntent { bool bEligible = false; FName ShotId{""}; };
struct UTSTSSPresentationCoordinatorSubsystem {
    FTSTSSPresentationIntent current;
    int disableCalls = 0;
    int resetCalls = 0;
    FTSTSSPresentationIntent GetCurrentIntent() { return current; }
    void SetReviewEnabled(bool enabled) { if (!enabled) ++disableCalls; }
    void ResetReviewIntent() { ++resetCalls; }
};
struct FTimerHandle { int value = 42; };
struct FTimerManager {
    int cleared = 0;
    void ClearTimer(FTimerHandle&) { ++cleared; }
};
struct UWorld {
    FTimerManager manager;
    UTSTSSPresentationCoordinatorSubsystem* coordinator = nullptr;
    FTimerManager& GetTimerManager() { return manager; }
    template<class T> T* GetSubsystem() { return coordinator; }
};
struct AActor { virtual ~AActor() = default; };
struct ACineCameraActor : AActor {
    int lifespanCalls = 0;
    float lifespan = -1.f;
    void SetLifeSpan(float seconds) { ++lifespanCalls; lifespan = seconds; }
};
struct APlayerController {
    AActor* view = nullptr;
    int viewChanges = 0;
    int moveIgnoreCount = 0;
    int lookIgnoreCount = 0;
    float lastBlend = -1.f;
    AActor* GetViewTarget() { return view; }
    void SetViewTargetWithBlend(AActor* target, float duration,
            EViewTargetBlendFunction = VTBlend_EaseInOut, float = 0.f) {
        view = target; ++viewChanges; lastBlend = duration;
    }
    void SetIgnoreMoveInput(bool ignored) {
        moveIgnoreCount = std::max(0, moveIgnoreCount + (ignored ? 1 : -1));
    }
    void SetIgnoreLookInput(bool ignored) {
        lookIgnoreCount = std::max(0, lookIgnoreCount + (ignored ? 1 : -1));
    }
};
template <typename T> bool IsValid(const T* ptr) { return ptr != nullptr; }
template <typename T> struct TWeakObjectPtr {
    T* ptr = nullptr;
    T* Get() const { return ptr; }
    bool IsValid() const { return ptr != nullptr; }
    void Reset() { ptr = nullptr; }
};
struct ATSTSSExplorerCharacter : AActor {
    UWorld* world = nullptr;
    TWeakObjectPtr<ACineCameraActor> EngineFocusPreviewCamera;
    TWeakObjectPtr<APlayerController> EngineFocusPreviewController;
    FTimerHandle EngineFocusPreviewGuardTimer;
    bool bEngineFocusPreviewOwnsCoordinatorEnable = false;
    bool bEngineFocusPreviewIgnoredMove = false;
    bool bEngineFocusPreviewIgnoredLook = false;
    double EngineFocusPreviewStartedSeconds = 0.;
    double EngineFocusPreviewDeadlineSeconds = 0.;
    UWorld* GetWorld() { return world; }
    void RestoreEngineFocusPreview();
};
"""

SUFFIX = r"""
static int cases = 0;
static void check(bool good, const char* reason) {
    if (!good) throw std::runtime_error(reason);
    ++cases;
}
static void setup(ATSTSSExplorerCharacter& pawn, UWorld& world,
                  APlayerController& pc, ACineCameraActor& cam,
                  UTSTSSPresentationCoordinatorSubsystem& coordinator,
                  bool owned = true) {
    pawn.world = &world;
    world.coordinator = &coordinator;
    pawn.EngineFocusPreviewController.ptr = &pc;
    pawn.EngineFocusPreviewCamera.ptr = &cam;
    pawn.bEngineFocusPreviewOwnsCoordinatorEnable = owned;
    pawn.bEngineFocusPreviewIgnoredMove = true;
    pawn.bEngineFocusPreviewIgnoredLook = true;
    pawn.EngineFocusPreviewStartedSeconds = 12.;
    pawn.EngineFocusPreviewDeadlineSeconds = 16.;
    pc.moveIgnoreCount = 1;
    pc.lookIgnoreCount = 1;
    coordinator.current = FTSTSSPresentationIntent{
        true, FName("FW03_Engine_Inspection")};
}
static void checkCleanup(const ATSTSSExplorerCharacter& pawn, APlayerController& pc,
                         ACineCameraActor& camera, UWorld& world) {
    check(pc.moveIgnoreCount == 0, "INPUT_MOVE_RESTORE_FAILED");
    check(pc.lookIgnoreCount == 0, "INPUT_LOOK_RESTORE_FAILED");
    check(world.manager.cleared == 1, "PREVIEW_TIMER_NOT_CLEARED");
    check(camera.lifespanCalls == 1
        && std::abs(camera.lifespan-0.6f)<0.001f,
        "TEMPORARY_CAMERA_NOT_DESTROYED");
    check(!pawn.EngineFocusPreviewCamera.IsValid()
          && !pawn.EngineFocusPreviewController.IsValid()
          && !pawn.bEngineFocusPreviewIgnoredMove
          && !pawn.bEngineFocusPreviewIgnoredLook
          && !pawn.bEngineFocusPreviewOwnsCoordinatorEnable
          && pawn.EngineFocusPreviewStartedSeconds == 0.
          && pawn.EngineFocusPreviewDeadlineSeconds == 0.,
          "PREVIEW_FLAGS_NOT_RESTORED");
}
int main() {
    try {
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            UTSTSSPresentationCoordinatorSubsystem owner; ATSTSSExplorerCharacter pawn;
            setup(pawn, world, pc, cam, owner); pc.view = &cam;
            pawn.RestoreEngineFocusPreview();
            checkCleanup(pawn, pc, cam, world);
            check(pc.view == &pawn && pc.viewChanges == 1 &&
                  std::abs(pc.lastBlend-0.3f)<0.001f,
                  "ACTIVE_VIEW_BLEND_RETURN_FAILED");
            check(owner.disableCalls == 1 && owner.resetCalls == 0,
                  "OWNED_REVIEW_COORDINATOR_NOT_RELEASED");
            pawn.RestoreEngineFocusPreview();
            check(pc.viewChanges == 1 && owner.disableCalls == 1,
                  "IDEMPOTENT_RESTORE_CHANGED_VIEW_OR_OWNER");
        }
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            UTSTSSPresentationCoordinatorSubsystem owner; ATSTSSExplorerCharacter pawn;
            setup(pawn, world, pc, cam, owner); pc.view = &pawn;
            pawn.RestoreEngineFocusPreview();
            checkCleanup(pawn, pc, cam, world);
            check(pc.view == &pawn && pc.viewChanges == 1
                  && pc.lastBlend == 0.f, "PENDING_BLEND_CANCEL_FAILED");
        }
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            AActor thirdParty; UTSTSSPresentationCoordinatorSubsystem owner;
            ATSTSSExplorerCharacter pawn;
            setup(pawn, world, pc, cam, owner); pc.view = &thirdParty;
            owner.current.ShotId = FName("EXTERNAL_AUTHORIZED_SHOT");
            pawn.RestoreEngineFocusPreview();
            checkCleanup(pawn, pc, cam, world);
            check(pc.view == &thirdParty && pc.viewChanges == 0,
                  "EXTERNAL_CAMERA_OWNERSHIP_STOLEN");
            check(owner.disableCalls == 0 && owner.resetCalls == 0,
                  "EXTERNAL_COORDINATOR_OWNERSHIP_STOLEN");
        }
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            UTSTSSPresentationCoordinatorSubsystem owner; ATSTSSExplorerCharacter pawn;
            setup(pawn, world, pc, cam, owner, false); pc.view = &cam;
            pawn.RestoreEngineFocusPreview();
            checkCleanup(pawn, pc, cam, world);
            check(owner.disableCalls == 0 && owner.resetCalls == 1,
                  "BORROWED_REVIEW_INTENT_NOT_RELEASED");
        }
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            UTSTSSPresentationCoordinatorSubsystem owner; ATSTSSExplorerCharacter pawn;
            setup(pawn, world, pc, cam, owner, false); pc.view = &cam;
            owner.current.ShotId = FName("DIFFERENT_SHOT");
            pawn.RestoreEngineFocusPreview();
            checkCleanup(pawn, pc, cam, world);
            check(owner.disableCalls == 0 && owner.resetCalls == 0,
                  "BORROWED_EXTERNAL_SHOT_REVOKED");
        }
        {
            UWorld world; APlayerController pc; ACineCameraActor cam;
            UTSTSSPresentationCoordinatorSubsystem owner; ATSTSSExplorerCharacter pawn;
            pawn.world = &world; world.coordinator = &owner;
            owner.current.ShotId = FName("FW03_Engine_Inspection");
            pawn.RestoreEngineFocusPreview();
            check(owner.disableCalls == 0 && owner.resetCalls == 0,
                  "UNOPENED_PREVIEW_MODIFIED_OWNER");
            check(pc.viewChanges == 0, "UNOPENED_PREVIEW_MODIFIED_CAMERA");
        }
        std::cout << "PASS: " << cases
                  << " source-extracted C++ restore assertions over 6 ownership/cancel scenarios\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "ENGINE_FOCUS_RESTORE_FAILURE: " << e.what() << "\n";
        return 2;
    }
}
"""


def extract_restore(source: str) -> str:
    if source.count(START) != 1:
        raise ValueError("missing or duplicate camera restore method")
    start = source.index(START)
    end = source.find(END, start)
    if end < start:
        raise ValueError("restore method editor boundary absent")
    method = source[start:end]
    for token in (
        "EngineFocusPreviewCamera.Reset()", "EngineFocusPreviewController.Reset()",
        "SetViewTargetWithBlend(this, 0.f)", "SetIgnoreMoveInput(false)",
        "SetIgnoreLookInput(false)", "GetCurrentIntent()",
    ):
        if token not in method:
            raise ValueError("restoration contract missing: " + token)
    return method


def compile_and_run(compiler: str, body: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-engine-focus-restore-") as folder:
        root = Path(folder)
        cpp = root / "restore.cpp"
        exe = root / ("restore.exe" if Path(compiler).name.lower() == "cl.exe" else "restore")
        cpp.write_text(PREFIX + "\n" + body + "\n" + SUFFIX, encoding="utf-8")
        if Path(compiler).name.lower() == "cl.exe":
            command = [compiler, "/nologo", "/std:c++17", "/EHsc", "/W4", "/WX",
                       str(cpp), "/Fo:" + str(root / "restore.obj"),
                       "/Fe:" + str(exe)]
        else:
            command = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-Werror",
                       "-pedantic", str(cpp), "-o", str(exe)]
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False, timeout=45)
        if result.returncode:
            raise RuntimeError("camera restore C++ portable compilation failed: "
                               + result.stdout + result.stderr[-5000:])
        return subprocess.run([str(exe)], capture_output=True, text=True,
                              check=False, timeout=20)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    compiler = next((exe for name in ("g++","clang++","c++","cl")
                     if (exe := shutil.which(name))), None)
    if not compiler:
        raise RuntimeError("C++17 compiler required; portable restore test not run")
    body = extract_restore(SOURCE.read_text(encoding="utf-8"))
    original = compile_and_run(compiler, body)
    if original.returncode != 0:
        raise RuntimeError("actual restore C++ behavior failed: "
                           + original.stdout + original.stderr)
    print(original.stdout.strip())
    if args.self_test:
        mutations = (
            ("pending-cancel", "PC->SetViewTargetWithBlend(this, 0.f);",
             "/* deliberately omitted pending cancel */",
             "ENGINE_FOCUS_RESTORE_FAILURE: PENDING_BLEND_CANCEL_FAILED"),
            ("external-view-steal",
             "else if (IsValid(Camera) && PC->GetViewTarget() == this)",
             "else if (IsValid(Camera))",
             "ENGINE_FOCUS_RESTORE_FAILURE: EXTERNAL_CAMERA_OWNERSHIP_STOLEN"),
            ("unopened-intent-revoke", "else if (bHadPreview)", "else",
             "ENGINE_FOCUS_RESTORE_FAILURE: UNOPENED_PREVIEW_MODIFIED_OWNER"),
        )
        for name, old, new, expected in mutations:
            if body.count(old) != 1:
                raise RuntimeError("unexpected mutation anchor for " + name)
            mutated = compile_and_run(compiler, body.replace(old, new, 1))
            if mutated.returncode != 2 or mutated.stderr.strip() != expected:
                raise RuntimeError("negative mutation survived: " + name + " "
                                   + mutated.stdout + mutated.stderr)
            print("PASS: rejected unsafe " + name)
    print("C++ API-double behavior only; native UE5.8 Editor and PIE remain unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
