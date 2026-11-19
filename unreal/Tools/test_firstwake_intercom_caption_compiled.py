"""Execute real intercom/objective/caption/HUD C++ with narrow API stand-ins.

Checks every inspection order and stale-caption refusal. This is not a UE
build, native input, rendered text-fit check, audio test or creator approval.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from check_first_wake_review_hud_compiled import API

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
PAWN = (ROOT / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HUD = (ROOT / "Private/TSTSSFirstWakeReviewHUD.cpp").read_text(encoding="utf8")
STATE = (ROOT / "Private/TSTSSFirstWakeState.cpp").read_text(encoding="utf8")


def method(source, signature):
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for end in range(brace, len(source)):
        depth += (source[end] == "{") - (source[end] == "}")
        if depth == 0:
            return source[start:end + 1]
    raise ValueError("Unclosed method: " + signature)


STANDINS = API.replace(
    "bool IsEmpty() const { return empty(); }",
    "bool IsEmpty() const { return empty(); } void Empty() { clear(); }",
).replace(
    "const UPackage* Package = nullptr;",
    'FString Level = "VS02_AureateInteriors"; float Seconds = 1.f;\n'
    "    float GetTimeSeconds() const { return Seconds; }\n"
    "    const UPackage* Package = nullptr;",
)
state_start = STANDINS.index("struct UTSTSSFirstWakeState {")
state_end = STANDINS.index("struct APawn {", state_start)
STANDINS = STANDINS[:state_start] + r"""
using uint8 = unsigned char;
using uint64 = unsigned long long;
#define UE_LOG(...) ((void)0)
enum class ETSTSSFirstWakeBeat : uint8 {
    FlyerDiscovered, IoniaHired, BoardedAureateWake, EngineeringChecked,
    Launched, SeaContact, FlotationConfirmed, EmptyReserveInspected, ReturnedToBerth
};
enum class ETSTSSInspectionStation : uint8 { Lift, Pressure, Reserve };
struct UTSTSSFirstWakeState {
    bool bStarted = true;
    ETSTSSFirstWakeBeat CurrentBeat = ETSTSSFirstWakeBeat::BoardedAureateWake;
    uint8 InspectionMask = 0;
    uint64 Generation = 1;
    uint64 GetRestoreGeneration() const { return Generation; }
    uint8 GetInspectionMask() const { return InspectionMask; }
    ETSTSSFirstWakeBeat GetCurrentBeat() const { return CurrentBeat; }
    bool AreInspectionsComplete() const { return InspectionMask == 7; }
    FString GetReviewObjectiveText() const;
};
struct ATSTSSMilestoneActor {
    FString Label = "TSTSS_ENGINEROOM_REVIEW_Station";
    FString GetActorLabel() const { return Label; }
    bool bIsInspectionStation = true;
    ETSTSSInspectionStation InspectionStation = ETSTSSInspectionStation::Lift;
    ETSTSSFirstWakeBeat Milestone = ETSTSSFirstWakeBeat::EngineeringChecked;
};
struct UGameplayStatics {
    static FString GetCurrentLevelName(const UWorld* world, bool) { return world->Level; }
};
""" + STANDINS[state_end:]
STANDINS = STANDINS.replace(
    "UTSTSSFirstWakeState* State = nullptr;", "UTSTSSFirstWakeState* FirstWakeState = nullptr;",
).replace("return State;", "return FirstWakeState;").replace(
    "FString Prompt;",
    r"""FString Prompt;
    UWorld* World = nullptr;
    const UWorld* GetWorld() const { return World; }
    FString FirstWakeIntercomSubtitle, FirstWakeIntercomNextCheck;
    float FirstWakeIntercomStartedSeconds = 1.f, FirstWakeIntercomExpiresSeconds = 10.f;
    uint64 FirstWakeIntercomGeneration = 1;
    uint8 FirstWakeIntercomMask = 0;
    ETSTSSFirstWakeBeat FirstWakeIntercomBeat = ETSTSSFirstWakeBeat::BoardedAureateWake;
    bool GetEngineeringIntercomCaption(FString&, FString&) const;""",
).replace("void DrawHUD() override;", "void DrawHUD() override {}\n"
          "    void DrawEngineeringIntercom(const ATSTSSExplorerCharacter&);")

TEST = r"""
#include <limits>
int checks = 0;
void expect(bool good, const char* reason) {
    ++checks;
    if (!good) throw std::runtime_error(reason);
}
int main() {
    try {
        UPackage package;
        package.Name = "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors";
        UWorld world;
        world.Package = &package;
        UTSTSSFirstWakeState state;
        ATSTSSMilestoneActor marker;
        FString subtitle, next;
        const int orders[][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
        const char* expected[] = {"", "Inspect the pressure systems",
            "Enter engine room; inspect the levitation LIFT", "Inspect the reserve systems",
            "Enter engine room; inspect the levitation LIFT", "Inspect the pressure systems",
            "Enter engine room; inspect the levitation LIFT", "Complete engineering signoff"};
        for (const auto& order : orders) {
            state.InspectionMask = 0;
            for (const auto station : order) {
                state.InspectionMask |= (1u << station);
                marker.InspectionStation = static_cast<ETSTSSInspectionStation>(station);
                const auto mask = state.InspectionMask;
                ShowEarnedFirstWakeEngineeringIntercom(&world, &marker, &state, subtitle, next);
                expect(!subtitle.IsEmpty(), "accepted inspection must have acknowledgement");
                expect(next == expected[mask], "next check must match missing inspections in every order");
                expect(state.InspectionMask == mask && state.Generation == 1 &&
                    state.CurrentBeat == ETSTSSFirstWakeBeat::BoardedAureateWake,
                    "caption may not mutate state");
            }
        }
        marker.bIsInspectionStation = false;
        state.CurrentBeat = ETSTSSFirstWakeBeat::EngineeringChecked;
        ShowEarnedFirstWakeEngineeringIntercom(&world, &marker, &state, subtitle, next);
        expect(next == "Await Captain Ionia's launch order.", "signoff does not grant launch");
        state.InspectionMask = 4;
        ShowEarnedFirstWakeEngineeringIntercom(&world, &marker, &state, subtitle, next);
        expect(subtitle.IsEmpty() && next.IsEmpty(), "partial checks cannot emit signoff");
        state.CurrentBeat = ETSTSSFirstWakeBeat::BoardedAureateWake;
        marker.bIsInspectionStation = true;
        auto reject = [&]() {
            subtitle = "stale"; next = "stale";
            ShowEarnedFirstWakeEngineeringIntercom(&world, &marker, &state, subtitle, next);
            expect(subtitle.IsEmpty() && next.IsEmpty(), "wrong context must clear outputs");
        };
        world.Level = "VS03_FirstWakeSky"; reject();
        world.Level = "VS02_AureateInteriors";
        package.Name = "/Game/Production/VS02_AureateInteriors"; reject();
        package.Name = "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors";
        world.Mode = NM_Client; reject(); world.Mode = NM_Standalone;
        world.WorldType = EWorldType::Editor; reject(); world.WorldType = EWorldType::PIE;
        marker.Label = "TSTSS_PRELUDE_REVIEW_Reserve"; reject();
        marker.Label = "TSTSS_ENGINEROOM_REVIEW_Station";

        ATSTSSExplorerCharacter explorer;
        explorer.FirstWakeState = &state; explorer.World = &world;
        explorer.FirstWakeIntercomMask = state.InspectionMask;
        explorer.FirstWakeIntercomSubtitle = "Reserve check received.";
        explorer.FirstWakeIntercomNextCheck = expected[4];
        auto visible = [&]() { return explorer.GetEngineeringIntercomCaption(subtitle, next); };
        expect(visible(), "fresh caption visible at start");
        world.Seconds = 9.99f; expect(visible(), "caption lasts nine game seconds");
        world.Seconds = 10.f; expect(!visible() && subtitle.IsEmpty(), "caption expires at deadline");
        world.Seconds = 0.f; expect(!visible(), "clock rewind hides caption");
        world.Seconds = std::numeric_limits<float>::quiet_NaN(); expect(!visible(), "NaN clock hidden");
        world.Seconds = std::numeric_limits<float>::infinity(); expect(!visible(), "infinite clock hidden");
        world.Seconds = 2.f;
        explorer.FirstWakeIntercomExpiresSeconds = std::numeric_limits<float>::quiet_NaN();
        expect(!visible(), "nonfinite deadline hidden");
        explorer.FirstWakeIntercomExpiresSeconds = 10.f;
        ++state.Generation; expect(!visible(), "restore/reset invalidates old captain reply"); --state.Generation;
        ++state.InspectionMask; expect(!visible(), "changed checks invalidate caption"); --state.InspectionMask;
        state.CurrentBeat = ETSTSSFirstWakeBeat::Launched;
        expect(!visible(), "later beat invalidates caption");
        state.CurrentBeat = ETSTSSFirstWakeBeat::BoardedAureateWake;
        world.Level = "VS03_FirstWakeSky"; expect(!visible(), "other map hides caption");
        world.Level = "VS02_AureateInteriors";
        UEngine engine; GEngine = &engine;
        UCanvas canvas; canvas.ClipX = 640; canvas.ClipY = 480;
        ATSTSSFirstWakeReviewHUD hud; hud.Canvas = &canvas;
        hud.DrawEngineeringIntercom(explorer);
        expect(hud.text.size() == 3 && hud.rects.size() == 2, "dedicated HUD draws speaker, reply and next check");
        const auto& panel = hud.rects.front();
        expect(panel.x >= 24 && panel.x + panel.w <= canvas.ClipX - 24 &&
            panel.y > 156 && panel.y + panel.h < canvas.ClipY - 88,
            "caption clears objective and interaction panels at minimum viewport");
        canvas.ClipY = 360; hud.DrawEngineeringIntercom(explorer);
        expect(hud.text.size() == 3, "small viewport must not clip panel");
        canvas.ClipY = 480; ++state.Generation; hud.DrawEngineeringIntercom(explorer);
        expect(hud.text.size() == 3, "stale caption must not render");
        std::cout << "INTERCOM_REAL_SOURCE_PASS " << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        return 2;
    }
}
"""


class IntercomCaptionCompiledTests(unittest.TestCase):
    def run_probe(self, pawn=PAWN):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("No portable C++17 compiler; native UE remains unverified")
        code = STANDINS + "\n" + "\n".join((
            method(STATE, "FString UTSTSSFirstWakeState::GetReviewObjectiveText() const"),
            method(pawn, "void ShowEarnedFirstWakeEngineeringIntercom("),
            method(pawn, "bool ATSTSSExplorerCharacter::GetEngineeringIntercomCaption("),
            method(HUD, "void ATSTSSFirstWakeReviewHUD::DrawEngineeringIntercom("),
        )) + TEST
        with tempfile.TemporaryDirectory(prefix="tstss-intercom-") as directory:
            source = Path(directory) / "intercom.cpp"
            binary = Path(directory) / "intercom"
            source.write_text(code, encoding="utf8")
            built = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                                    str(source), "-o", str(binary)],
                                   capture_output=True, text=True, timeout=45)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            return subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)

    def test_all_orders_timeline_revocation_and_actual_hud_method(self):
        result = self.run_probe()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INTERCOM_REAL_SOURCE_PASS", result.stdout)

    def test_fixed_order_signoff_mutation_fails_behavior(self):
        mutation = PAWN.replace('? State->GetReviewObjectiveText() :',
                                '? TEXT("Complete engineering signoff") :', 1)
        self.assertNotEqual(mutation, PAWN)
        self.assertNotEqual(self.run_probe(mutation).returncode, 0)

    def test_removed_restore_guard_fails_behavior(self):
        mutation = PAWN.replace(
            "FirstWakeState->GetRestoreGeneration() != FirstWakeIntercomGeneration ||", "false ||", 1)
        self.assertNotEqual(mutation, PAWN)
        self.assertNotEqual(self.run_probe(mutation).returncode, 0)

    def test_accepted_interaction_wires_cache_and_hud_without_debug_messages(self):
        helper = method(PAWN, "void ShowEarnedFirstWakeEngineeringIntercom(")
        self.assertNotIn("AddOnScreenDebugMessage", helper)
        interact = method(PAWN, "void ATSTSSExplorerCharacter::Interact()")
        self.assertLess(interact.index("if (Milestone->TryActivate(FirstWakeState))"),
                        interact.index("ShowEarnedFirstWakeEngineeringIntercom("))
        for token in ("FirstWakeIntercomStartedSeconds + 9.f", "FirstWakeIntercomGeneration =",
                      "FirstWakeIntercomBeat =", "FirstWakeIntercomMask ="):
            self.assertIn(token, interact)
        self.assertIn("DrawEngineeringIntercom(*Explorer);", method(
            HUD, "void ATSTSSFirstWakeReviewHUD::DrawHUD()"))


if __name__ == "__main__":
    unittest.main()
