"""Fail-closed no-Editor source guards for #769 native admission tooling.

Checks that only approved disposable worktrees are allowed, 29 native names
are still required, correct map/source/save guards remain, and the GUI RAM
threshold matches the documented 6.5 GiB requirement. Never runs Unreal.
"""
import re
import unittest
from pathlib import Path

UNREAL = Path(__file__).resolve().parents[1]
REVIEW = UNREAL / "Tools/Start-FirstWakeReview.ps1"
MAP = UNREAL / "Tools/Invoke-NativePreludeMapQA.ps1"
BUILD = UNREAL / "Tools/Verify-Unreal.ps1"
REQUIRED_ROOT = "TSTSS_P0CombinedF6Objectives_20261104"
MAP_SHA = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"


def verify(review: str, map_launcher: str, builder: str) -> list[str]:
    errors = []
    expected_roots = (
        ("review", review, ["TSTSS_GameAssembly_20261104", REQUIRED_ROOT]),
        ("map QA", map_launcher, [
            "TSTSS_PR713_NativeMapQA_20261102",
            "TSTSS_PR735_NativeMapQA_20261103",
            "TSTSS_GameAssembly_20261104",
            REQUIRED_ROOT,
        ]),
    )
    for label, src, allowed in expected_roots:
        match = re.search(r"\$AllowedReviewRoots\s*=\s*@\(([^)]*)\)", src)
        names = re.findall(r"'([^']+)'", match.group(1)) if match else []
        if names != allowed or "-notin $AllowedReviewRoots" not in src:
            errors.append(f"{label}: non-exact or missing allowed review root check")
        if "Get-Process" not in src or "UnrealEditor" not in src or "LiveCodingConsole" not in src:
            errors.append(f"{label}: existing Editor process hold missing")
        if "Saved/SaveGames" not in src or "ExpectedHead" not in src:
            errors.append(f"{label}: SaveGame/source custody guard missing")
        if "Stop-Process" in src or "taskkill" in src:
            errors.append(f"{label}: arbitrary editor termination is forbidden")
    if MAP_SHA not in review or MAP_SHA not in map_launcher:
        errors.append("V2 original .umap SHA256 custody missing")
    if ("if ($FreeKiB -lt 6815744)" not in review or
            "require at least 6.5 GiB" not in review):
        errors.append("GUI admission must require 6.5 actual GiB")
    if "if (-not $NativeAccepted)" not in review or "if (-not $MapAccepted)" not in review:
        errors.append("GUI launcher must require exact-head native + map receipts")
    if "if ($PreflightOnly)" not in map_launcher or (
            map_launcher.index("if ($PreflightOnly)") >
            map_launcher.index("New-Item -Path $LauncherRoot")):
        errors.append("Map preflight creates receipts before checking the hold")
    names = re.findall(r"^\s*'(TSTSS\.[^']+)'", builder, re.M)
    if len(names) != 29 or len(set(names)) != 29:
        errors.append("Exact combined-head native registry not 29 unique named tests")
    if "Source HEAD differs from the explicitly requested review commit" not in builder:
        errors.append("Native build lacks commit-custody check")
    return errors


class CombinedNativeAdmissionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = REVIEW.read_text(encoding="utf-8")
        cls.map = MAP.read_text(encoding="utf-8")
        cls.builder = BUILD.read_text(encoding="utf-8")

    def check(self, **overrides):
        data = dict(review=self.review, map_launcher=self.map, builder=self.builder)
        data.update(overrides)
        return verify(**data)

    def test_current_exact_head_source_guards(self):
        self.assertEqual(self.check(), [])

    def test_unapproved_review_path_rejected(self):
        self.assertTrue(self.check(review=self.review.replace(
            "'" + REQUIRED_ROOT + "'", "'C:/Anywhere'", 1)))

    def test_unapproved_native_map_path_rejected(self):
        self.assertTrue(self.check(map_launcher=self.map.replace(
            "'" + REQUIRED_ROOT + "'", "'C:/Anywhere'", 1)))

    def test_missing_editor_process_hold_rejected(self):
        self.assertTrue(self.check(map_launcher=self.map.replace(
            "LiveCodingConsole", "OtherProcess", 1)))

    def test_weakened_ram_limit_rejected(self):
        self.assertTrue(self.check(review=self.review.replace(
            "if ($FreeKiB -lt 6815744)", "if ($FreeKiB -lt 1)", 1)))

    def test_missing_native_report_required_rejected(self):
        self.assertTrue(self.check(review=self.review.replace(
            "if (-not $NativeAccepted)", "if ($false)", 1)))

    def test_wrong_29_name_requirement_rejected(self):
        self.assertTrue(self.check(builder=self.builder.replace(
            "'TSTSS.FirstWake.InteractionToSplashdown',",
            "", 1)))

    def test_original_map_sha_mutation_rejected(self):
        self.assertTrue(self.check(map_launcher=self.map.replace(MAP_SHA, "0" * 64, 1)))


if __name__ == "__main__":
    unittest.main()
