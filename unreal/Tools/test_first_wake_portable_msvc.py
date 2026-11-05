"""Engine-free regression checks for First Wake's portable Windows C++ test runners.

The real MSVC compile/mutation runs are a separate operation; these guards
ensure the Windows and hosted-compiler routes retain safety properties.
"""
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parent
NAMES = (
    "check_first_wake_pie_save_compiled.py",
    "check_first_wake_save_guard_compiled.py",
)


class FirstWakePortableMSVCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = [((TOOLS / name).read_text(encoding="utf-8")) for name in NAMES]

    def test_native_msvc_compiler_is_explicitly_eligible(self):
        for source in self.sources:
            with self.subTest(which=source[:60]):
                self.assertIn('("g++", "clang++", "c++", "cl")', source)
                self.assertIn('Path(compiler).name.lower() == "cl.exe"', source)
                self.assertIn('"/std:c++17"', source)
                self.assertIn('"/EHsc"', source)
                self.assertIn('"/WX"', source)

    def test_mutation_specific_constant_warning_is_the_only_exception(self):
        for source in self.sources:
            with self.subTest(which=source[:60]):
                self.assertEqual(source.count('"/wd4127"'), 1)
                self.assertIn('"-Werror"', source)
                self.assertIn('"cl.exe" else "', source)

    def test_existing_safety_mutations_remain_required(self):
        self.assertIn('unsafe pre-existing-slot overwrite mutation detected', self.sources[0])
        self.assertIn('if (bPIE && !bPIEReviewQuickSlotOwned &&', self.sources[0])
        self.assertIn('deliberate existing-roster overwrite mutation rejected', self.sources[1])
        self.assertIn('Save->PartyRoster.Num() != 0', self.sources[1])

    def test_test_executables_are_temporary_not_player_save_files(self):
        for source in self.sources:
            with self.subTest(which=source[:60]):
                self.assertIn("tempfile.TemporaryDirectory(", source)
                self.assertIn('"/Fe:"', source)
                self.assertIn('"/Fo:"', source)
                self.assertNotIn("Saved/SaveGames", source)
                self.assertNotIn("shutil.rmtree", source)


if __name__ == "__main__":
    unittest.main()
