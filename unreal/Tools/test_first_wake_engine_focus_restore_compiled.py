"""Engine-free extracted C++ camera-restore behavior in the full source suite."""
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import check_engine_focus_restore_compiled as review


class FirstWakeEngineFocusRestoreCompiledTests(unittest.TestCase):
    def test_actual_restore_body_and_mutation_controls(self):
        compiler = next((shutil.which(name) for name in
                         ("g++","clang++","c++","cl") if shutil.which(name)), None)
        if compiler is None:
            self.skipTest("C++17 compiler not in PATH; native PIE remains pending")
        actual = review.extract_restore(review.SOURCE.read_text(encoding="utf-8"))
        self.assertIn("PC->GetViewTarget() == Camera", actual)
        self.assertIn("PC->GetViewTarget() == this", actual)
        self.assertIn("else if (bHadPreview)", actual)
        result = subprocess.run(
            [sys.executable, str(Path(review.__file__)), "--self-test"],
            capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("source-extracted C++ restore assertions", result.stdout)
        self.assertIn("rejected unsafe pending-cancel", result.stdout)
        self.assertIn("rejected unsafe external-view-steal", result.stdout)
        self.assertIn("rejected unsafe unopened-intent-revoke", result.stdout)
        self.assertIn("native UE5.8 Editor and PIE remain unverified", result.stdout)


if __name__ == "__main__":
    unittest.main()
