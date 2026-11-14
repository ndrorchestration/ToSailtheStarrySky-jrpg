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
using TCHAR = char; // Portable API double for Unreal's platform-wide TCHAR.
struct FString : std::string {
    using std::string::string;
    using std::string::operator=;
    FString() = default;
    FString(const std::string& str) : std::string(str) {}
    bool StartsWith(const char* prefix) const { return rfind(prefix, 0) == 0; }
    bool IsEmpty() const { return empty(); }
};
struct FLinearColor {
    float r, g, b, a;
    FLinearColor(float red, float green, float blue, float alpha)
        : r(red), g(green), b(blue), a(alpha) {}
    static const FLinearColor White;
};
const FLinearColor FLinearColor::White(1.f, 1.f, 1.f, 1.f);
struct UCanvas { float ClipX = 1280.f; float ClipY = 720.f; };
struct FVector {
    float X = 0.f, Y = 0.f, Z = 0.f;
    bool ContainsNaN() const {
        return !std::isfinite(X) || !std::isfinite(Y) || !std::isfinite(Z);
    }
};
namespace EWorldType { enum Type { Game, PIE, Editor }; }
enum ENetMode { NM_Standalone, NM_Client };
// Minimal package API for the actual map-scoped Seabourne review HUD.
// This API double does not create a real World, route or gameplay authority.
struct UPackage {
    FString Name;
    const FString& GetName() const { return Name; }
};
struct UWorld {
    const UPackage* Package = nullptr;
    EWorldType::Type WorldType = EWorldType::Game;
    ENetMode Mode = NM_Standalone;
    ENetMode GetNetMode() const { return Mode; }
    const UPackage* GetOutermost() const { return Package; }
};
struct UTSTSSFirstWakeState {
    FString Objective = "Find Ionia's flyer";
    unsigned Mask = 0;
    bool ChapterOne = false;
    FString GetReviewObjectiveText() const { return Objective; }
    unsigned GetInspectionMask() const { return Mask; }
    bool IsChapterOneActOne() const { return ChapterOne; }
};
struct APawn {
    virtual ~APawn() = default;
    FVector Location;
    FVector GetActorLocation() const { return Location; }
};
struct ATSTSSExplorerCharacter : APawn {
    UTSTSSFirstWakeState* State = nullptr;
    FString Prompt;
    UTSTSSFirstWakeState* GetFirstWakeState() const { return State; }
    FString GetReviewAimStatus() const { return Prompt; }
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
    static bool IsFinite(float value) { return std::isfinite(value); }
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
    UWorld* World = nullptr;
    const UWorld* GetWorld() const { return World; }
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
        expect(hud.rects.size() == 7 && hud.text.size() == 6,
               "valid Prelude draws objective, lamps, controls plus contrast-protected interaction prompt");
        expect(hud.text[5].value.find("FOLLOW THE GOLD MARKER") != FString::npos,
               "readable hint must lead to the current highlighted marker");
        expect(hud.text[0].value.find("PRELUDE REVIEW") != FString::npos,
               "persistent overlay must identify review provenance");
        expect(hud.text[1].value == "Find Ionia's flyer",
               "HUD must read live objective from state");
        expect(hud.text[2].value.find("INSPECTIONS") != FString::npos,
               "review HUD must identify three engineer systems");
        expect(hud.text[3].value.find("E: interact") != FString::npos &&
               hud.text[3].value.find("PIE F6: save") != FString::npos &&
               hud.text[3].value.find("F9: load") != FString::npos &&
               hud.text[3].value.find("F7: Continue preview/confirm") != FString::npos &&
               hud.text[3].value.find("F5/F9") == FString::npos,
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
        expect(hud.text[hud.text.size() - 2].value.find("no launch") != FString::npos &&
               hud.text[hud.text.size() - 5].value == "Board the Aureate Wake",
               "next frame must reflect current state without cached objective");
        expect(hud.rects[8].color.g > 0.8f && hud.rects[9].color.g > 0.8f &&
               hud.rects[10].color.g < 0.4f,
               "inspection lamps must reflect the current, uncached story mask");
        state.Mask = 0x07u;
        hud.DrawHUD();
        expect(hud.rects[15].color.g > 0.8f &&
               hud.rects[16].color.g > 0.8f &&
               hud.rects[17].color.g > 0.8f,
               "all three engineering systems must illuminate after inspection");
        canvas.ClipX = 500.f;
        hud.DrawHUD();
        expect(hud.rects[hud.rects.size()-4].w == 452.f,
               "review panel must adapt to a smaller valid viewport");
        expect(hud.text[hud.text.size()-2].value.find("E interact") != FString::npos &&
               hud.text[hud.text.size()-2].value.find("PIE F6 save F9 load F7 Continue") != FString::npos &&
               hud.text.back().value.find("no sea landing") != FString::npos,
               "compact layout must use shortened controls and review disclaimer");
        // Scope and visibility checks must also exercise the real, active E
        // cue, not merely compile its presentation behind API stand-ins.
        canvas.ClipX = 1280.f;
        explorer.Prompt = "[E]  SPEAK TO IONIA";
        hud.DrawHUD();
        expect(hud.text.back().value == "[E]  SPEAK TO IONIA",
               "real aim cue must announce only the eligible E target");
        expect(hud.rects.back().color.r > 0.95f,
               "eligible reticle must have warm high-contrast emphasis");
        explorer.Prompt = "MOVE CLOSER  |  SPEAK TO IONIA";
        hud.DrawHUD();
        expect(hud.text.back().value.find("MOVE CLOSER") != FString::npos,
               "out-of-reach prompts must never look like an actionable E");
        const auto beforeChapter = hud.text.size();
        state.ChapterOne = true;
        hud.DrawHUD();
        expect(hud.text.size() == beforeChapter,
               "Prelude review HUD must disappear after real Chapter 1 boundary");
        UPackage seabournePackage;
        seabournePackage.Name =
            "/Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview";
        UWorld seabourneWorld;
        seabourneWorld.Package = &seabournePackage;
        hud.World = &seabourneWorld;
        const auto priorText = hud.text.size();
        const auto priorRects = hud.rects.size();
        hud.DrawHUD();
        expect(hud.text.size() == priorText + 3 &&
               hud.rects.size() == priorRects + 1,
               "isolated Seabourne review must render 3 status lines and one panel");
        expect(hud.text[priorText].value.find("SEABOURNE VISUAL REVIEW") !=
                   FString::npos &&
               hud.text[priorText+2].value.find("No ship sailing") !=
                   FString::npos,
               "review-only HUD cannot claim ship traversal or Prelude objectives");
        seabournePackage.Name = "/Game/TSTSS/Review/UnknownTest";
        const auto priorUnknown = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == priorUnknown,
               "unrelated map cannot inherit Seabourne HUD");
        hud.World = nullptr;
        // Distinguish traversable Hilltonia review geography from legitimate
        // E plot interactions; prove it is scoped to V5, standalone and finite.
        UPackage hilltoniaPackage;
        hilltoniaPackage.Name =
            "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview";
        UWorld hilltoniaWorld;
        hilltoniaWorld.Package = &hilltoniaPackage;
        hud.World = &hilltoniaWorld;
        state.ChapterOne = false;
        explorer.Location = {-3650.f, -150.f, 130.f};
        const auto roadText = hud.text.size();
        const auto roadRects = hud.rects.size();
        hud.DrawHUD();
        expect(hud.text.size() == roadText + 9 &&
               hud.rects.size() == roadRects + 8,
               "V5 road must draw normal 6-line HUD plus 3-line route guidance");
        expect(hud.text[roadText+6].value.find("HILLTONIA") != FString::npos &&
               hud.text[roadText+7].value.find("FOLLOW ROAD WEST") != FString::npos &&
               hud.text[roadText+8].value.find("NOT an [E]") != FString::npos,
               "wayfinding must distinguish non-interactive roads from E markers");
        expect(hud.rects.back().x > 800.f && hud.rects.back().w == 386.f,
               "route panel must sit beside rather than over Prelude objective");
        explorer.Location = {-7350.f, -1700.f, 130.f};
        const auto forestText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text[forestText+7].value.find("WOODLAND TRACK") != FString::npos,
               "forest route must use actual pawn location");
        explorer.Location = {-1000.f, -150.f, 130.f};
        const auto outsideText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == outsideText + 6,
               "ordinary harbor markers must not inherit Hilltonia route overlay");
        explorer.Location = {-3650.f, -150.f, 130.f};
        hilltoniaWorld.Mode = NM_Client;
        const auto networkText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == networkText + 6,
               "network worlds must not show local review wayfinding");
        hilltoniaWorld.Mode = NM_Standalone;
        hilltoniaWorld.WorldType = EWorldType::Editor;
        const auto editorText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == editorText + 6,
               "Editor world must not inherit live player route overlay");
        hilltoniaWorld.WorldType = EWorldType::PIE;
        explorer.Location = {NAN, -150.f, 130.f};
        const auto nonfiniteText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == nonfiniteText + 6,
               "nonfinite pawn positions must not generate navigation labels");
        explorer.Location = {-3650.f, -150.f, 130.f};
        canvas.ClipX = 1000.f;
        const auto narrowText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == narrowText + 6,
               "narrow view must not clip an overlapping Hilltonia side panel");
        canvas.ClipX = 1280.f;
        hilltoniaPackage.Name = "/Game/Unrelated/HilltoniaDebug";
        const auto otherText = hud.text.size();
        hud.DrawHUD();
        expect(hud.text.size() == otherText + 6,
               "unrelated world must not receive Hilltonia panel");
        hud.World = nullptr;
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
