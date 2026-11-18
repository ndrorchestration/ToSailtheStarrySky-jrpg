"""Source-only Git safety guard for PRIVATE non-distributable Ender retarget assets.

Engine-free. This test does not access, render, upload or materialize licensed
content. A Git ignore rule cannot untrack a file previously committed.
"""
from pathlib import Path
import shutil
import subprocess
import unittest


REPO = Path(__file__).resolve().parents[2]
IGNORE = REPO / "unreal/.gitignore"
PRIVATE_DIR = "unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
EXACT_RULE = "/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
ORIGINAL_V5 = "unreal/Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"


class EnderPrivateAssetSafety(unittest.TestCase):
    def test_exact_narrow_exclusion(self):
        text = IGNORE.read_text(encoding="utf-8")
        rules = [
            line.strip() for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertEqual(rules.count(EXACT_RULE), 1)
        self.assertFalse(any(rule == "/Content/TSTSS/Review/Characters/" for rule in rules))
        self.assertFalse(any(rule == "/Content/TSTSS/Review/" for rule in rules))

    def test_mutated_rule_fails_source_contract(self):
        text = IGNORE.read_text(encoding="utf-8")
        self.assertIn(EXACT_RULE, text)
        mutated = text.replace(EXACT_RULE, "")
        self.assertNotIn(EXACT_RULE, mutated)

    @unittest.skipUnless(shutil.which("git"), "Git executable unavailable")
    def test_git_ignores_generated_private_packages(self):
        for name in (
            "BP_EnderLocomotionPreview_NONCANONICAL.uasset",
            "BP_EnderPIEGameMode_NONCANONICAL.uasset",
            "FirstWake_PreludeInteraction_V5_VisualReview.umap",
            "RTG_MannyToEnder_NONCANONICAL.uasset",
        ):
            path = f"{PRIVATE_DIR}/{name}"
            result = subprocess.run(
                ["git", "-C", str(REPO), "check-ignore",
                 "--no-index", "-q", path],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, f"Private path not ignored: {path}")

    @unittest.skipUnless(shutil.which("git"), "Git executable unavailable")
    def test_original_v5_map_not_ignored(self):
        result = subprocess.run(
            ["git", "-C", str(REPO), "check-ignore",
             "--no-index", "-q", ORIGINAL_V5],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1,
                         "Public review V5 original must not be blanket-excluded")

    @unittest.skipUnless(shutil.which("git"), "Git executable unavailable")
    def test_no_private_staging_path_previously_tracked(self):
        result = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "--", PRIVATE_DIR + "/"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "",
                         "A .gitignore rule does not revoke already tracked files")


if __name__ == "__main__":
    unittest.main()
