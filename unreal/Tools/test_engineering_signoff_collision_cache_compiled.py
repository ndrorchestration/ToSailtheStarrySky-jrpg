"""Execute the real beacon collision prefix across a stale cosmetic cache.

API stand-ins isolate collision/cache ordering, not native ray/physics or UI.
The prefix ends before cosmetic drawing; no production logic is reimplemented.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp").read_text(encoding="utf8")
START = "void ATSTSSMilestoneActor::UpdateReviewBeacon("
END = "    // Consumed review markers cannot visually occlude later objectives."

API = r'''
#include <iostream>
#include <stdexcept>
#include <string>
#define TEXT(x) x
struct FString : std::string {
    using std::string::string;
    bool Contains(const char* x) const { return find(x) != npos; }
};
struct FTags { bool Retired = false; bool Contains(const char*) const { return Retired; } };
enum ECollisionChannel { ECC_Visibility };
enum ECollisionResponse { ECR_Ignore, ECR_Block };
enum class ETSTSSFirstWakeBeat { BoardedAureateWake, EngineeringChecked };
struct UWorld { FString Scene = "VS02_AureateInteriors"; bool Authorized = true; };
struct UTSTSSFirstWakeState {};
struct UMesh {
    ECollisionResponse Response = ECR_Ignore;
    void SetCollisionResponseToChannel(ECollisionChannel, ECollisionResponse response) { Response = response; }
};
template<class T> bool IsValid(const T* p) { return p != nullptr; }
bool IsRetiredV5HarborEngineeringMarker(const UWorld*, const FString&, bool, ETSTSSFirstWakeBeat) { return false; }
bool IsAuthorizedReviewMilestoneWorld(const UWorld* world, const FString&) { return world && world->Authorized; }
struct UGameplayStatics { static FString GetCurrentLevelName(const UWorld* world, bool) { return world->Scene; } };
struct ATSTSSMilestoneActor {
    UWorld* World = nullptr;
    int Beacon = 1;
    int* ReviewBeacon = &Beacon;
    UMesh Mesh;
    UMesh* InteractionMesh = &Mesh;
    FTags Tags;
    FString Label = "TSTSS_ENGINEROOM_REVIEW_EngineeringApproval";
    bool bIsInspectionStation = false;
    ETSTSSFirstWakeBeat Milestone = ETSTSSFirstWakeBeat::EngineeringChecked;
    bool bReviewBeaconInitialized = true, bReviewBeaconAvailable = true;
    bool Actionable = true;
    const UWorld* GetWorld() const { return World; }
    FString GetActorLabel() const { return Label; }
    bool IsReviewActionable(const UTSTSSFirstWakeState*) const { return Actionable; }
    void EnsureV5ReviewObjectProxy() {}
    void UpdateReviewBeacon(const UTSTSSFirstWakeState*);
};
'''

TEST = r'''
int main() {
    try {
        UWorld world;
        UTSTSSFirstWakeState state;
        ATSTSSMilestoneActor marker;
        marker.World = &world;
        auto require = [](bool ok) { if (!ok) throw std::runtime_error("collision/cache drift"); };
        // Reload can reset collision while the beacon cache still says ready.
        marker.UpdateReviewBeacon(&state);
        require(marker.Mesh.Response == ECR_Block);
        // The inverse drift must hide an unavailable target, even when cached.
        marker.Actionable = false; marker.bReviewBeaconAvailable = false;
        marker.Mesh.Response = ECR_Block;
        marker.UpdateReviewBeacon(&state);
        require(marker.Mesh.Response == ECR_Ignore);
        // Repeated replays must converge despite independent collision resets.
        for (int n = 0; n < 12; ++n) {
            marker.Actionable = true; marker.bReviewBeaconAvailable = true;
            marker.Mesh.Response = ECR_Ignore;
            marker.UpdateReviewBeacon(&state);
            require(marker.Mesh.Response == ECR_Block);
        }
        // Neither ordinary inspections nor unauthorized worlds inherit this policy.
        marker.bIsInspectionStation = true; marker.Mesh.Response = ECR_Ignore;
        marker.UpdateReviewBeacon(&state); require(marker.Mesh.Response == ECR_Ignore);
        marker.bIsInspectionStation = false; world.Authorized = false;
        marker.UpdateReviewBeacon(&state); require(marker.Mesh.Response == ECR_Ignore);
        std::cout << "SIGNOFF_CACHE_PREFIX_PASS 16\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what(); return 2; }
}
'''


class SignoffCollisionCacheTests(unittest.TestCase):
    def run_probe(self, source):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("Portable C++ compiler unavailable")
        start = source.index(START)
        prefix = source[start:source.index(END, start)] + "}\n"
        with tempfile.TemporaryDirectory(prefix="tstss-signoff-cache-") as directory:
            cpp, binary = Path(directory) / "cache.cpp", Path(directory) / "cache"
            cpp.write_text(API + prefix + TEST, encoding="utf8")
            build = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                                    str(cpp), "-o", str(binary)],
                                   capture_output=True, text=True, timeout=45)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            return subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)

    def test_cached_visual_state_cannot_skip_signoff_collision(self):
        run = self.run_probe(SOURCE)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SIGNOFF_CACHE_PREFIX_PASS 16", run.stdout)

    def test_original_early_return_mutation_fails_behavior(self):
        cache_start = SOURCE.index("    if (bReviewBeaconInitialized && bReviewBeaconAvailable == bAvailable)")
        cache_end = SOURCE.index(END, cache_start)
        cache = SOURCE[cache_start:cache_end]
        mutation = SOURCE[:cache_start] + SOURCE[cache_end:]
        insert = mutation.index("    // In the real shipboard route the *final* E marker")
        mutation = mutation[:insert] + cache + mutation[insert:]
        self.assertNotEqual(self.run_probe(mutation).returncode, 0)


if __name__ == "__main__":
    unittest.main()
