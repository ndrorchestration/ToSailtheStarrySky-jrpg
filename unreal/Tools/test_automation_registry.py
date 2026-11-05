#!/usr/bin/env python3
"""Self-tests for source registration preflight; no Unreal installation required."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check_automation_registry.py")


class RegistryPreflightTests(unittest.TestCase):
    def run_fixture(self, names, registrations):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tool_dir = root / "Tools"
            cpp_dir = root / "Source" / "ToSailTheStarrySky" / "Private" / "Tests"
            tool_dir.mkdir(parents=True)
            cpp_dir.mkdir(parents=True)
            checker = tool_dir / CHECKER.name
            checker.write_text(CHECKER.read_text(encoding="utf-8"), encoding="utf-8")
            entries = ",\n".join(f"    '{name}'" for name in names)
            (tool_dir / "Verify-Unreal.ps1").write_text(
                "$RequiredTests = @(\n" + entries + "\n)\n", encoding="utf-8"
            )
            declarations = "\n".join(
                f'IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTest{i}, "{name}", Flags)'
                for i, name in enumerate(registrations)
            )
            (cpp_dir / "Fixture.cpp").write_text(declarations, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(checker)], check=False,
                capture_output=True, text=True
            )

    def test_matching_registration(self):
        result = self.run_fixture(["TSTSS.Combat.One"], ["TSTSS.Combat.One"])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_registration(self):
        result = self.run_fixture(["TSTSS.Combat.One"], ["TSTSS.Combat.Other"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required name not registered", result.stderr)

    def test_unlisted_registration(self):
        result = self.run_fixture(["TSTSS.Combat.One"], ["TSTSS.Combat.One", "TSTSS.Combat.New"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing from required verification list", result.stderr)

    def test_duplicate_registration(self):
        result = self.run_fixture(["TSTSS.Combat.One"], ["TSTSS.Combat.One", "TSTSS.Combat.One"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate native registration", result.stderr)

    def test_duplicate_required_name(self):
        result = self.run_fixture(["TSTSS.Combat.One", "TSTSS.Combat.One"], ["TSTSS.Combat.One"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicates", result.stderr)


if __name__ == "__main__":
    unittest.main()
