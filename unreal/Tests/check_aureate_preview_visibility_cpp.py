"""Compile and execute the actual hull-visibility predicate extracted from UE source.

Engine-free executable contract; NOT a native UE/UHT/renderer pass.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky"
header = (root / "Public" / "AureateWakePreviewActor.h").read_text(encoding="utf-8")
actor = (root / "Private" / "AureateWakePreviewActor.cpp").read_text(encoding="utf-8")
m = re.search(
    r"static\s+bool\s+(ShouldShowPrimitiveHullStudy\s*\([^)]*\))\s*\{([^{}]*)\}",
    header,
)
if m is None:
    raise SystemExit("FAIL CLOSED: cannot extract actual hull-visibility predicate")

start = actor.index("void AAureateWakePreviewActor::UpdateHullSilhouetteVisibility()")
end = actor.index("void AAureateWakePreviewActor::UpdateWingRootMounts()", start)
visibility = actor[start:end]
for exact in (
    "const bool bShowPrimitiveStudy = ShouldShowPrimitiveHullStudy(bUseHullSilhouetteReview, bBodyReviewApplied);",
    "Hull->SetVisibility(!bShowPrimitiveStudy);",
    "ForwardBridge->SetVisibility(!bShowPrimitiveStudy);",
    "Section->SetVisibility(bShowPrimitiveStudy);",
    "Rib->SetVisibility(bShowPrimitiveStudy);",
):
    if exact not in visibility:
        raise SystemExit(f"FAIL CLOSED: active visibility path no longer uses predicate: {exact}")
if "ShouldShowPrimitiveHullStudy(bUseHullSilhouetteReview, bBodyReviewApplied) ? 56.f : 72.f;" not in actor:
    raise SystemExit("FAIL CLOSED: root-anchor selection disagrees with visibility predicate")

compiler = next((shutil.which(name) for name in ("g++", "clang++", "c++") if shutil.which(name)), None)
if compiler is None:
    print("No host C++ compiler; cannot claim executable source verification.", file=sys.stderr)
    raise SystemExit(2)

cpp = """
#include <iostream>
bool """ + m.group(1) + "{" + m.group(2) + """}
int main() {
  int cases = 0;
  for (int requested = 0; requested <= 1; ++requested) {
    for (int applied = 0; applied <= 1; ++applied) {
      const bool observed = ShouldShowPrimitiveHullStudy(requested, applied);
      const bool expected = requested && !applied;
      if (observed != expected) {
        std::cerr << "FAIL: requested=" << requested << ", applied=" << applied << "\\n";
        return 1;
      }
      ++cases;
    }
  }
  std::cout << cases << " preview precedence cases; 0 failures. Source C++ only; NOT Unreal.\\n";
  return 0;
}
"""
with tempfile.TemporaryDirectory(prefix="tstss-visibility-") as directory:
    source = Path(directory) / "visibility.cpp"
    binary = Path(directory) / "visibility"
    source.write_text(cpp, encoding="utf-8")
    try:
        subprocess.run(
            [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
             str(source), "-o", str(binary)], check=True, timeout=30
        )
        result = subprocess.run([str(binary)], check=False, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL CLOSED: C++ source contract failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(result.returncode)
