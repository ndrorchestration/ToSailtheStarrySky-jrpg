#!/usr/bin/env python3
"""Fail-closed source checks for independently verified UE 5.8 API corrections.
These inspect source, they neither compile Unreal nor prove Editor automation.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Source" / "ToSailTheStarrySky" / "Private"


class NativeCompatibilitySourceTests(unittest.TestCase):
    def test_unreal58_target_build_defaults(self):
        for name in ("ToSailTheStarrySky.Target.cs", "ToSailTheStarrySkyEditor.Target.cs"):
            with self.subTest(name=name):
                content = (ROOT / "Source" / name).read_text(encoding="utf-8")
                self.assertIn("DefaultBuildSettings = BuildSettingsVersion.V7;", content)
                self.assertIn("IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;", content)
                self.assertNotIn("BuildSettingsVersion.V5", content)

    def test_water_contact_uses_current_world_bounds(self):
        content = (SRC / "TSTSSWaterContactAdapter.cpp").read_text(encoding="utf-8")
        self.assertIn("const FBoxSphereBounds HullBounds = Hull->GetBounds();", content)
        self.assertIn("const FVector HullOrigin = HullBounds.Origin;", content)
        self.assertIn("const FVector HullExtent = HullBounds.BoxExtent;", content)
        self.assertNotIn("GetComponentBounds(", content)
        self.assertIn("HullExtent.Z <= 0.f", content)

    def test_save_fixture_never_self_aliases_array_add(self):
        content = (SRC / "Tests" / "TSTSSRulesTests.cpp").read_text(encoding="utf-8")
        self.assertNotIn("Save->PartyRoster.Add(Save->PartyRoster[0])", content)
        self.assertIn("const FTSTSSCombatant ExtraMember = Save->PartyRoster[0];", content)
        self.assertIn("Save->PartyRoster.Add(ExtraMember);", content)


if __name__ == "__main__":
    unittest.main()
