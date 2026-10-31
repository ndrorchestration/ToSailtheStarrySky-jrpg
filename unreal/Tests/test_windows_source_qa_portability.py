"""Cross-platform QA controls: no fake C++ PASS and correct hidden-wing regex."""
from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
REQUEST = HERE / "check_aureate_request_logic.py"
PREVIEW = HERE / "check_aureate_preview_source.py"


class CrossPlatformUnrealSourceChecks(unittest.TestCase):
    def test_explicit_source_only_mode_is_not_compiled_pass(self):
        result = subprocess.run(
            [sys.executable, str(REQUEST), "--source-only"],
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SOURCE SCREEN ONLY", result.stdout)
        self.assertIn("no C++ compiler", result.stdout)

    def test_no_compiler_exits_nonzero_without_false_success(self):
        env = dict(os.environ)
        env["PATH"] = ""
        result = subprocess.run(
            [sys.executable, str(REQUEST)], env=env, text=True,
            capture_output=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("C++ TOOLCHAIN UNAVAILABLE", result.stderr)
        self.assertNotIn("failures. Isolated C++ method", result.stdout)

    def test_source_preview_regex_rejects_actual_hidden_wing(self):
        script = PREVIEW.read_text(encoding="utf-8")
        match = re.search(r"re\.search\(r'([^']+)'\s*,\s*source\)", script)
        self.assertIsNotNone(match)
        with __import__("warnings").catch_warnings():
            __import__("warnings").simplefilter("error", FutureWarning)
            pattern = re.compile(match.group(1))
        self.assertIsNotNone(pattern.search("Wing->SetVisibility(false)"))
        self.assertIsNotNone(pattern.search("Wings[Index]->SetVisibility( false )"))
        self.assertIsNotNone(pattern.search("Wings[WingIndex]->SetVisibility(false)"))
        self.assertIsNone(pattern.search("Support->SetVisibility(false)"))
        self.assertIsNone(pattern.search("Wings[Index]->SetVisibility(true)"))

    def test_preview_source_contract_has_no_regex_warnings(self):
        result = subprocess.run(
            [sys.executable, "-W", "error::FutureWarning", str(PREVIEW)],
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Source contracts passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
