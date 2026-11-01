#!/usr/bin/env python3
"""Source-only guard for known Unreal 5.8.4 build compatibility.

This checks that the EXACT changes native-verified in PR #650 are retained
in the newer combat composition. It is NOT UHT, compilation or Editor proof.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"Source"


class UnrealNativeCompatibilitySourceTests(unittest.TestCase):
    def test_editor_and_game_targets_use_verified_ue58_defaults(self):
        for target in ("ToSailTheStarrySkyEditor.Target.cs",
                       "ToSailTheStarrySky.Target.cs"):
            with self.subTest(target=target):
                text=(SOURCE/target).read_text(encoding="utf-8")
                self.assertIn("DefaultBuildSettings = BuildSettingsVersion.V7;",text)
                self.assertIn("IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;",text)
                self.assertNotIn("BuildSettingsVersion.V5",text)

    def test_hull_bound_getter_uses_ue58_api(self):
        text=(SOURCE/"ToSailTheStarrySky"/"Private"/"TSTSSWaterContactAdapter.cpp").read_text(encoding="utf-8")
        self.assertIn("const FBoxSphereBounds HullBounds = Hull->GetBounds();",text)
        self.assertIn("const FVector HullOrigin = HullBounds.Origin;",text)
        self.assertIn("const FVector HullExtent = HullBounds.BoxExtent;",text)
        self.assertNotIn("GetComponentBounds(",text)
        self.assertIn("HullExtent.Z <= 0.f",text)

if __name__=="__main__":
    unittest.main()
