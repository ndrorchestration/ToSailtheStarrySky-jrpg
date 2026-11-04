#!/usr/bin/env python3
"""Compile and exercise the ACTUAL C++ focused-interaction hint with API doubles.

Source-only: no UE Editor, no player input, no SaveGame, no screenshot.
E and HUD must use the same camera-trace + pawn-centered range helper.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

SRC = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp")
START = "FString ATSTSSExplorerCharacter::GetFocusedReviewInteractionHint() const\n"

API = r"""
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#define TEXT(x) x
#define SCENE_QUERY_STAT(x) 0
constexpr int ECC_Visibility = 1;
struct FString : std::string {
    using std::string::string;
    using std::string::operator=;
    FString() = default;
    FString(const std::string& s) : std::string(s) {}
    bool IsEmpty() const { return empty(); }
};
struct FVector {
    float x = 0.f, y = 0.f, z = 0.f;
    FVector() = default;
    FVector(float a, float b, float c) : x(a), y(b), z(c) {}
    FVector operator+(FVector rhs) const {
        return {x+rhs.x,y+rhs.y,z+rhs.z};
    }
    FVector operator*(float t) const { return {x*t,y*t,z*t}; }
};
float distance_squared(FVector a,FVector b) {
    float dx=a.x-b.x,dy=a.y-b.y,dz=a.z-b.z;
    return dx*dx+dy*dy+dz*dz;
}
struct AActor { virtual ~AActor() = default; };
struct ATSTSSMilestoneActor : AActor {
    bool bIsInspectionStation = false;
};
struct FHitResult {
    AActor* Actor = nullptr;
    FVector ImpactPoint;
    AActor* GetActor() const { return Actor; }
};
struct FCollisionQueryParams {
    FCollisionQueryParams(int, bool, const AActor*) {}
};
struct UWorld {
    bool bHit = true;
    AActor* Target = nullptr;
    FVector ImpactPoint{180.f, 0.f, 130.f};
    mutable int Queries = 0;
    mutable FVector LastEnd;
    bool LineTraceSingleByChannel(
        FHitResult& hit, FVector, FVector end, int, const FCollisionQueryParams&) const {
        ++Queries;
        LastEnd = end;
        if (!bHit) return false;
        hit.Actor = Target;
        hit.ImpactPoint = ImpactPoint;
        return true;
    }
};
struct UCameraComponent {
    FVector Location{-360.f,0.f,130.f};
    FVector Forward{1.f,0.f,0.f};
    FVector GetComponentLocation() const { return Location; }
    FVector GetForwardVector() const { return Forward; }
};
struct UTSTSSFirstWakeState {
    bool ChapterOne = false;
    bool IsChapterOneActOne() const { return ChapterOne; }
};
template<typename T> T* Cast(AActor* a) { return dynamic_cast<T*>(a); }
template<typename T> bool IsValid(const T* ptr) { return ptr != nullptr; }
namespace TSTSSInteractionReach {
float GetCameraTraceLength(FVector cam,FVector pawn,float reach) {
    const float d=std::sqrt(distance_squared(cam,pawn));
    return std::isfinite(d) && std::isfinite(reach) && reach>0.f ? d+reach : 0.f;
}
bool IsInsidePlayerReach(FVector pawn,FVector impact,float reach) {
    return std::isfinite(reach) && reach > 0.f &&
           std::isfinite(distance_squared(pawn,impact)) &&
           distance_squared(pawn,impact) <= reach*reach;
}
}
struct ATSTSSExplorerCharacter : AActor {
    UTSTSSFirstWakeState* FirstWakeState = nullptr;
    UCameraComponent* FollowCamera = nullptr;
    UWorld* World = nullptr;
    float InteractionDistance = 300.f;
    FVector PawnLocation{0.f,0.f,130.f};
    UWorld* GetWorld() const { return World; }
    FVector GetActorLocation() const { return PawnLocation; }
    FString GetFocusedReviewInteractionHint() const;
};
"""

TEST = r"""
int checks=0;
void expect(bool b,const char* why) {
    if(!b) throw std::runtime_error(why);
    ++checks;
}
int main() {
    try {
        UTSTSSFirstWakeState story;
        UCameraComponent camera;
        ATSTSSMilestoneActor milestone;
        UWorld world;
        ATSTSSExplorerCharacter pawn;
        pawn.FirstWakeState=&story;
        pawn.FollowCamera=&camera;
        pawn.World=&world;
        world.Target=&milestone;
        const FString empty="";
#if UE_BUILD_SHIPPING
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "shipping must not expose review hint");
        expect(world.Queries==0,"shipping must perform no focus trace");
#else
        expect(pawn.GetFocusedReviewInteractionHint()=="E: attempt milestone interaction",
               "valid aimed and reachable marker must produce honest tentative cue");
        expect(world.Queries==1 && std::abs(world.LastEnd.x-300.f)<0.01f,
               "camera boom 360cm must extend trace to 660cm while reach stays 300cm");
        milestone.bIsInspectionStation=true;
        expect(pawn.GetFocusedReviewInteractionHint()=="E: attempt engineering inspection",
               "engineering marker should show appropriate review cue");
        world.bHit=false;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "no visibility hit must not show interaction prompt");
        world.bHit=true;
        AActor other;
        world.Target=&other;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "non-review actor must not show prompt");
        world.Target=&milestone;
        world.ImpactPoint={301.f,0.f,130.f};
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "camera hit outside pawn-centered 300cm range must not show prompt");
        world.ImpactPoint={300.f,0.f,130.f};
        expect(pawn.GetFocusedReviewInteractionHint()=="E: attempt engineering inspection",
               "exact 300cm pawn limit should be eligible for attempt");
        story.ChapterOne=true;
        const int before=world.Queries;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "Prelude focus cue must not misrepresent Chapter 1");
        expect(world.Queries==before,"Chapter 1 must short-circuit world trace");
        story.ChapterOne=false;
        pawn.FirstWakeState=nullptr;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "missing story should fail closed");
        pawn.FirstWakeState=&story;
        pawn.FollowCamera=nullptr;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "missing camera should fail closed");
        pawn.FollowCamera=&camera;
        pawn.World=nullptr;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "missing world should fail closed");
        pawn.World=&world;
        pawn.InteractionDistance=0.f;
        expect(pawn.GetFocusedReviewInteractionHint()==empty,
               "zero interaction reach must not show hint");
        pawn.InteractionDistance=300.f;
        world.ImpactPoint={180.f,0.f,130.f};
        milestone.bIsInspectionStation=false;
        expect(pawn.GetFocusedReviewInteractionHint()=="E: attempt milestone interaction",
               "restored valid focus should show cue without caching");
#endif
        std::cout<<"PASS: "<<checks
                 <<" actual C++ focus hint checks (UE/PIE NOT TESTED)\n";
        return 0;
    } catch(const std::exception& e) {
        std::cerr<<"FOCUS_HINT_BEHAVIOR_FAILURE: "<<e.what()<<"\n";
        return 3;
    }
}
"""


def extract(source: str) -> str:
    if source.count(START) != 1:
        raise ValueError("Focus hint method absent or ambiguous")
    offset = source.index(START)
    brace = source.index("{", offset)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                body = source[offset:i + 1]
                required = (
                    "#if !UE_BUILD_SHIPPING",
                    "FirstWakeState->IsChapterOneActOne()",
                    "TSTSSInteractionReach::GetCameraTraceLength(",
                    "LineTraceSingleByChannel(",
                    "Cast<ATSTSSMilestoneActor>(",
                    "TSTSSInteractionReach::IsInsidePlayerReach(",
                    "E: attempt engineering inspection",
                    "E: attempt milestone interaction",
                )
                for word in required:
                    if word not in body:
                        raise ValueError("Focus proof missing: " + word)
                for bad in ("TryActivate(", "AdvanceTo(", "InspectStation(",
                            "SaveFirstWake(", "SaveProgress(", "Reset("):
                    if bad in body:
                        raise ValueError("Focus hint must remain read-only: " + bad)
                return body
    raise ValueError("Focus hint method has unclosed body")


def compile_and_run(compiler: str, method: str, shipping: int) -> str:
    with tempfile.TemporaryDirectory(prefix="tstss-focus-") as directory:
        path = Path(directory)
        cpp, exe = path / "focus.cpp", path / "focus"
        cpp.write_text(API + "\n" + method + "\n" + TEST, encoding="utf-8")
        command = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra",
                   f"-DUE_BUILD_SHIPPING={shipping}", str(cpp), "-o", str(exe)]
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=60, check=False)
        if result.returncode != 0:
            raise RuntimeError("Focus C++ compilation failed: " + result.stderr[-4000:])
        run = subprocess.run([str(exe)], capture_output=True, text=True,
                             timeout=15, check=False)
        if run.returncode:
            raise RuntimeError("Focus C++ checks failed: " + run.stderr + run.stdout)
        return run.stdout.strip()


def main() -> None:
    compiler = next((path for name in ("g++", "clang++", "c++")
                     if (path := shutil.which(name))), None)
    if not compiler:
        raise RuntimeError("Missing portable C++17 compiler; no package install authorized")
    method = extract(SRC.read_text(encoding="utf-8"))
    for shipping in (0, 1):
        print(compile_and_run(compiler, method, shipping))
    print("SOURCE_CPP_FOCUS_HINT_PASS_NOT_UNREAL_EDITOR_OR_PIE")


if __name__ == "__main__":
    main()
