"""Source-regression guard for native ActiveLoops TObjectPtr map lookup.

Source-only assertions: does not replace a UHT/C++ Editor build.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
HEADER = ROOT / "Public/TSTSSAudioSubsystem.h"
CPP = ROOT / "Private/TSTSSAudioSubsystem.cpp"


def check_lookup(header: str, source: str):
    if "TMap<FName, TObjectPtr<UAudioComponent>> ActiveLoops;" not in header:
        raise ValueError("ActiveLoops map declaration changed")
    if not re.search(
        r"const\s+TObjectPtr<UAudioComponent>\s*\*\s*Existing\s*=\s*"
        r"ActiveLoops\.Find\(EventId\)\s*;", source
    ):
        raise ValueError("ActiveLoops.Find pointer type incompatible with TObjectPtr value")
    if "Existing && IsValid(Existing->Get()) && Existing->Get()->IsPlaying()" not in source:
        raise ValueError("loop-component lookup must guard nullable TObjectPtr")
    if "ActiveLoops.Remove(EventId);" not in source:
        raise ValueError("stale loop state removal missing")


class NativeAudioLookupSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.source = CPP.read_text(encoding="utf-8")

    def test_declared_and_lookup_pointer_types_agree(self):
        check_lookup(self.header, self.source)

    def test_raw_pointer_to_pointer_regression_fails_closed(self):
        broken = self.source.replace(
            "const TObjectPtr<UAudioComponent>* Existing = ActiveLoops.Find(EventId);",
            "UAudioComponent* const* Existing = ActiveLoops.Find(EventId);"
        )
        self.assertNotEqual(broken, self.source)
        with self.assertRaisesRegex(ValueError, "pointer type incompatible"):
            check_lookup(self.header, broken)

    def test_unguarded_loop_component_regression_fails_closed(self):
        broken = self.source.replace(
            "Existing && IsValid(Existing->Get()) && Existing->Get()->IsPlaying()",
            "Existing && Existing->Get()->IsPlaying()"
        )
        self.assertNotEqual(broken, self.source)
        with self.assertRaisesRegex(ValueError, "guard nullable"):
            check_lookup(self.header, broken)


if __name__ == "__main__":
    unittest.main()
