"""Fail-closed source checks for the optional First Wake graphical review RAM gate.

No Unreal Editor or PowerShell launcher is executed by these tests.
Win32_OperatingSystem.FreePhysicalMemory reports KiB, not bytes or GiB.
"""
import re
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).with_name("Start-FirstWakeReview.ps1")
EXPECTED_MINIMUM_KIB = 13 * 1024 * 1024 // 2  # 6.5 GiB in KiB

GUARD = re.compile(
    r"if\s*\(\s*\$FreeKiB\s+-lt\s+(\d+)\s*\)\s*"
    r"\{\s*throw\s+'Insufficient free RAM for graphical review'\s*\}"
)


def admitted_minimum_kib(source: str) -> int:
    matches = GUARD.findall(source)
    if len(matches) != 1:
        raise ValueError("Exactly one fail-closed KiB graphical review guard is required")
    return int(matches[0])


class FirstWakeGraphicalMemoryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = LAUNCHER.read_text(encoding="utf-8")

    def test_exact_binary_gib_to_kib_conversion(self):
        self.assertEqual(EXPECTED_MINIMUM_KIB, 6815744)
        self.assertEqual(admitted_minimum_kib(self.source), EXPECTED_MINIMUM_KIB)
        self.assertIn("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory", self.source)

    def test_negative_and_positive_boundary_cases(self):
        threshold = admitted_minimum_kib(self.source)
        for free_gib, must_refuse in ((6.20, True), (6.49, True),
                                      (6.50, False), (6.51, False)):
            with self.subTest(free_gib=free_gib):
                free_kib = int(free_gib * 1024 * 1024)
                self.assertEqual(free_kib < threshold, must_refuse)

    def test_decimal_kib_regression_is_rejected(self):
        wrong = self.source.replace("6815744", "6500000")
        self.assertNotEqual(admitted_minimum_kib(wrong), EXPECTED_MINIMUM_KIB)
        with self.assertRaisesRegex(ValueError, "Exactly one"):
            admitted_minimum_kib(self.source.replace("-lt 6815744", "-le 6815744"))

    def test_guard_stays_before_editor_open_and_retains_existing_admission(self):
        self.assertLess(
            self.source.index("Get-CimInstance Win32_OperatingSystem"),
            self.source.index("if (-not $OpenEditor) { return }"),
        )
        self.assertLess(
            self.source.index("if ($FreeKiB -lt 6815744)"),
            self.source.index("Start-Process -FilePath $Editor"),
        )
        for marker in (
            "ExpectedHead mismatch", "Clean source required", "Prelude map changed",
            "Existing saves protected", "Existing Unreal session active",
            "Exact-head native automation evidence missing",
            "Exact-head native map admission missing",
            "DefaultEngine.ini", "DefaultInput.ini",
        ):
            self.assertIn(marker, self.source)


if __name__ == "__main__":
    unittest.main()
