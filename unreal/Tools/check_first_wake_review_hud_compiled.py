#!/usr/bin/env python3
"""Compile the ACTUAL Unreal review-HUD DrawHUD method with tiny API doubles.

Runs without UE, no Editor, no player saves and no screenshots. Compiles both
non-shipping and shipping variants of the production function, then checks
that the HUD derives text from the story state and never renders in shipping.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

SRC = (Path(__file__).resolve().parents[1]
       / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp")
METHOD = "void ATSTSSFirstWakeReviewHUD::DrawHUD()\n"

API = r"""
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#define TEXT(x) x
using FString = std::string;
struct FLinearColor {
    float r, g, b, a;
    FLinearColor(float red, float green, float blue, float alpha)
        : r(red), g(green), b(blue), a(alpha) {}
    static const FLinearColor White;
};
const FLinearColor FLinearColor::White(1.f, 1.f, 1.f, 1.f);
struct UCanvas { float ClipX = 1280.f; float ClipY = 720.f; };
struct UTSTSSFirstWakeState {
    FString Objective = "Find Ionia's flyer";
    unsigned Mask = 0;
    bool ChapterOne = false;
    FString GetReviewObjectiveText() const { return Objective; }
    unsigned GetInspectionMask() const { return Mask; }
    bool IsChapterOneActOne() const { return ChapterOne; }
};
struct APawn { virtual ~APawn() = default; };
struct ATSTSSExplorerCharacter : APawn {
    UTSTSSFirstWakeState* State = nullptr;
    UTSTSSFirstWakeState* GetFirstWakeState() const { return State; }
};
struct APlayerController {
    APawn* Pawn = nullptr;
    APawn* GetPawn() const { return Pawn; }
};
struct UEngine {
    static void* GetSmallFont() { return reinterpret_cast<void*>(1); }
    static void* GetMediumFont() { return reinterpret_cast<void*>(2); }
};
UEngine* GEngine = nullptr;
template<class T> T* Cast(APawn* p) { return dynamic_cast<T*>(p); }
template<class T> bool IsValid(const T* p) { return p != nullptr; }
struct FMath {
    static float Max(float a, float b) { return std::max(a, b); }
    static float Min(float a, float b) { return std::min(a, b); }
};
struct TextDraw {
    FString value;
    float x, y;
};
struct RectDraw {
    FLinearColor color;
    float x, y, w, h;
};
struct AHUD {
    UCanvas* Canvas = nullptr;
    APlayerController* PlayerOwner = nullptr;
    std::vector<TextDraw> text;
    std::vector<RectDraw> rects;
    virtual ~AHUD() = default;
    virtual void DrawHUD() {}
    void DrawRect(FLinearColor color, float x, float y, float w, float h) {
        rects.push_back({color, x, y, w, h});
    }
    void DrawText(const FString& t, FLinearColor, float x, float y,
                  void*, float) {
        text.push_back({t, x, y});
    }
};
struct ATSTSSFirstWakeReviewHUD : AHUD {
    using Super = AHUD;
    void DrawHUD() override;
};
"""

TEST = r"""
int checks = 0;
void expect(bool condition, const char* why) {
    if (!condition) throw std::runtime_error(why);
    ++checks;
}
int main() {
    try {
        UEngine engine;
        UCanvas canvas;
        APlayerController controller;
        UTSTSSFirstWakeState state;
        ATSTSSExplorerCharacter explorer;
        explorer.State = &state;
        controller.Pawn = &explorer;
        ATSTSSFirstWakeReviewHUD hud;
        hud.Canvas = &canvas;
        hud.PlayerOwner = &controller;
#if UE_BUILD_SHIPPING
        GEngine = &engine;
        hud.DrawHUD();
        expect(hud.text.empty() && hud.rects.empty(),
               "shipping build must never show debug review overlay");
#else
        hud.Canvas = nullptr;
        GEngine = &engine;
        hud.DrawHUD();
        expect(hud.text.empty(), "missing canvas must not draw");
        hud.Canvas = &canvas;
        GEngine = nullptr;
        hud.DrawHUD();
        expect(hud.text.empty(), "missing engine must not draw");
        GEngine = &engine;
        hud.PlayerOwner = nullptr;
        hud.DrawHUD();
        expect(hud.text.empty(), "missing player controller must not draw");
        hud.PlayerOwner = &controller;
        APawn other;
        controller.Pawn = &other;
        hud.DrawHUD();
        expect(hud.text.empty(), "wrong pawn must not draw");
        controller.Pawn = &explorer;
        explorer.State = nullptr;
        hud.DrawHUD();
        expect(hud.text.empty(), "missing story state must not draw");
        explorer.State = &state;

        canvas.ClipX = 380.f;
        hud.DrawHUD();
        expect(hud.text.empty(), "narrow view should hide rather than clip");
        canvas.ClipX = 1280.f;
        canvas.ClipY = 120.f;
        hud.DrawHUD();
        expect(hud.text.empty(), "short view should hide rather than clip");
        canvas.ClipY = 720.f;
        hud.DrawHUD();
        expect(hud.rects.size() == 4 && hud.text.size() == 5,
               "valid Prelude must draw one panel, three inspection lamps and five cues");
        expect(hud.text[0].value.find("PRELUDE REVIEW") != FString::npos,
               "persistent overlay must identify review provenance");
        expect(hud.text[1].value == "Find Ionia's flyer",
               "HUD must read live objective from state");
        expect(hud.text[2].value.find("INSPECTIONS") != FString::npos,
               "review HUD must identify three engineer systems");
        expect(hud.text[3].value.find("E: interact") != FString::npos &&
               hud.text[3].value.find("F5/F9") != FString::npos,
               "review controls must remain discoverable");
        expect(hud.text[4].value.find("no launch") != FString::npos,
               "HUD must not imply launch, sea landing or chapter approval");
        expect(hud.rects[1].color.g < 0.4f && hud.rects[2].color.g < 0.4f &&
               hud.rects[3].color.g < 0.4f,
               "uninspected engineering stations must be visibly incomplete");
        expect(hud.rects[0].x == 24.f && hud.rects[0].w <= 780.f,
               "HUD must stay within maximum authored width");
        state.Objective = "Board the Aureate Wake";
        state.Mask = 0x03u;
        hud.DrawHUD();
        expect(hud.text.back().value.find("no launch") != FString::npos &&
               hud.text[hud.text.size() - 4].value == "Board the Aureate Wake",
               "next frame must reflect current state without cached objective");
        expect(hud.rects[5].color.g > 0.8f && hud.rects[6].color.g > 0.8f &&
               hud.rects[7].color.g < 0.4f,
               "inspection lamps must reflect the current, uncached story mask");
        state.Mask = 0x07u;
        hud.DrawHUD();
        expect(hud.rects[9].color.g > 0.8f &&
               hud.rects[10].color.g > 0.8f &&
               hud.rects[11].color.g > 0.8f,
               "all three engineering systems must illuminate after inspection");
        canvas.ClipX = 500.f;
        hud.DrawHUD();
        expect(hud.rects[hud.rects.size()-4].w == 452.f,
               "review panel must adapt to a smaller valid viewport");
        expect(hud.text[hud.text.size()-2].value.find("E interact") != FString::npos &&
               hud.text.back().value.find("no sea landing") != FString::npos,
               "compact layout must use shortened controls and review disclaimer");
        const auto beforeChapter = hud.text.size();
        state.ChapterOne = true;
        hud.DrawHUD();
        expect(hud.text.size() == beforeChapter,
               "Prelude review HUD must disappear after real Chapter 1 boundary");
#endif
        std::cout << "PASS: " << checks <<
            " portable C++ real DrawHUD behavior checks (UE/PIE NOT TESTED)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "HUD_BEHAVIOR_FAILURE: " << error.what() << "\n";
        return 3;
    }
}
"""


def extract(source: str) -> str:
    if source.count(METHOD) != 1:
        raise ValueError("Cannot unambiguously find actual HUD DrawHUD body")
    start = source.index(METHOD)
    brace = source.index("{", start)
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if not depth:
                body = source[start:i + 1]
                for token in (
                    "Super::DrawHUD()",
                    "#if !UE_BUILD_SHIPPING",
                    "GetFirstWakeState()",
                    "State->GetReviewObjectiveText()",
                    "DrawRect(",
                    "DrawText(",
                    "PanelWidth < 440.f",
                    "Canvas->ClipY < 170.f",
                    "State->IsChapterOneActOne()",
                    "State->GetInspectionMask()",
                    "bCompact",
                    "InspectionMask & 0x01u",
                    "InspectionMask & 0x02u",
                    "InspectionMask & 0x04u",
                ):
                    if token not in body:
                        raise ValueError("Actual HUD lost safety feature: " + token)
                return body
    raise ValueError("Unclosed HUD DrawHUD method")


def compile_and_run(compiler: str, method: str, shipping: int) -> str:
    with tempfile.TemporaryDirectory(prefix="tstss-hud-standins-") as directory:
        root = Path(directory)
        src, exe = root / "hud.cpp", root / "hud_test"
        src.write_text(API + "\n" + method + "\n" + TEST, encoding="utf-8")
        if Path(compiler).name.lower() == "cl.exe":
            exe = root / "hud_test.exe"
            cmd = [compiler, "/nologo", "/std:c++17", "/EHsc",
                   f"/DUE_BUILD_SHIPPING={shipping}", str(src),
                   "/Fo:" + str(root / "hud_test.obj"),
                   "/Fe:" + str(exe)]
        else:
            cmd = [compiler, "-std=c++17", "-O0", "-Wall", "-Wextra", "-pedantic",
                   f"-DUE_BUILD_SHIPPING={shipping}", str(src), "-o", str(exe)]
        build = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
        if build.returncode:
            raise RuntimeError("Portable HUD compile failed: " + (build.stdout + build.stderr)[-4000:])
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
        if run.returncode:
            raise RuntimeError(run.stderr + run.stdout)
        return run.stdout.strip()


def main() -> None:
    compiler = next((found for name in ("g++", "clang++", "c++")
                     if (found := shutil.which(name))), None)
    if not compiler:
        compiler = shutil.which("cl")
    if not compiler:
        raise RuntimeError("No C++17 compiler installed for source-side test")
    method = extract(SRC.read_text(encoding="utf-8"))
    print(compile_and_run(compiler, method, shipping=0))
    print(compile_and_run(compiler, method, shipping=1))
    print("Only DrawHUD is compiled against API stand-ins; native UE HUD rendering awaits separate Editor/PIE checks.")


if __name__ == "__main__":
    main()
