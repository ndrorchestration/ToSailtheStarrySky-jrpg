"""Bounded source checks for the six Unreal vertical-slice environments."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import os
import unittest
from unittest.mock import patch

FILE = Path(__file__).with_name("build_vertical_slice_environment_maps.py")
spec = importlib.util.spec_from_file_location("vs_maps", FILE)
maps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maps)


class VerticalSliceEnvironmentContracts(unittest.TestCase):
    def test_six_unique_map_packages_and_complete_links(self):
        p = maps.review_plan()
        levels = p["levels"]
        self.assertEqual(len(levels), 6)
        self.assertEqual(len(p["links"]), 5)
        self.assertEqual(len({r["package"] for r in levels}), 6)
        self.assertEqual([r["name"] for r in levels], [r[0] for r in maps.ORDER])
        self.assertEqual([r["from"] for r in p["links"]],
                         [r["name"] for r in levels[:-1]])
        self.assertEqual([r["to"] for r in p["links"]],
                         [r["name"] for r in levels[1:]])

    def test_preserves_story_and_native_authority(self):
        p = maps.review_plan()
        self.assertTrue(p["preserve_first_wake_v2"])
        self.assertTrue(p["native_water_adaptor_isolated"])
        self.assertTrue(p["starbourne_locked"])
        self.assertTrue(p["no_automatic_lyra_recruitment"])
        self.assertFalse(p["PIE_verified"])
        self.assertFalse(p["visual_approval"])
        self.assertFalse(p["world_globe_not_implemented"] is False)
        self.assertTrue(all(not link["runtime_transition_implemented"]
                            for link in p["links"]))

    def test_post_contact_map_order(self):
        level_gates = [row["gate"] for row in maps.review_plan()["levels"]]
        self.assertEqual(level_gates,
                         ["prelaunch", "prelaunch", "launch", "sea",
                          "post_contact", "post_contact"])

    def test_rejects_build_outside_disposable_worktree(self):
        with self.assertRaisesRegex(RuntimeError, "isolated"):
            maps.assert_sandbox(Path("C:/arbitrary/unreal"))

    def test_rejects_missing_exact_head_before_git(self):
        with patch.dict(os.environ, {"TSTSS_VSLICE_EXPECTED_HEAD": ""}):
            with self.assertRaisesRegex(RuntimeError, "40-hex"):
                maps.assert_sandbox(Path("C:/") / maps.SANDBOX / "unreal")

    def test_authoring_source_does_not_write_protected_configs(self):
        source = FILE.read_text(encoding="utf-8")
        self.assertNotIn("DefaultEngine.ini", source)
        self.assertNotIn("DefaultInput.ini", source)
        self.assertNotIn("set_simulate_physics(True)", source)
        self.assertIn('comp.set_simulate_physics(False)', source)
        self.assertIn('if hashlib.sha256((project / PARENT).read_bytes()).hexdigest()', source)
        self.assertIn('if git("status", "--porcelain")', source)
        self.assertIn("save_map(world, package)", source)

    def test_reference_assets_are_review_only(self):
        self.assertIn("/Review/VerticalSlice", maps.DEST)
        self.assertIn("Review/FirstWake_PreludeInteraction_V2.umap", maps.PARENT)
        self.assertTrue(all(name.startswith("VS0") for name, _, _ in maps.ORDER))
        self.assertFalse(any("Orbiter" in name for name, _, _ in maps.ORDER))


if __name__ == "__main__":
    unittest.main()
