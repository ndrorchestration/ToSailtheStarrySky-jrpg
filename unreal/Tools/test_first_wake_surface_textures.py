"""Offline first-wake 3D scene texture contract tests; no Unreal import required."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SRC = Path(__file__).with_name("first_wake_surface_textures.py")
SPEC = importlib.util.spec_from_file_location("surfacepass", SRC)
surface = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(surface)

class SurfacePassQA(unittest.TestCase):
    def test_six_original_and_six_unique_review_maps(self):
        m = surface.manifest()
        self.assertEqual(len(m["source_maps"]), 6)
        self.assertEqual(len(set(m["review_maps"])), 6)
        self.assertTrue(all(a.startswith("/Game/TSTSS/Review/VerticalSlice/")
                            for a in m["source_maps"]))
        self.assertTrue(all(a.startswith("/Game/TSTSS/Review/SurfacePassV1/")
                            for a in m["review_maps"]))
        self.assertTrue(set(m["source_maps"]).isdisjoint(m["review_maps"]))

    def test_all_original_pbr_surface_families_covered(self):
        path = SRC.with_name("build_vertical_slice_environment_maps.py")
        text = path.read_text(encoding="utf-8")
        import ast
        tree = ast.parse(text)
        palette = next(ast.literal_eval(n.value) for n in tree.body
                       if isinstance(n, ast.Assign) and any(
                           isinstance(t, ast.Name) and t.id == "PALETTE" for t in n.targets))
        self.assertEqual(set(palette), set(surface.SURFACES))

    def test_physical_input_channels_explicit(self):
        for spec in surface.manifest()["textures"].values():
            self.assertEqual(spec["channels"], ["BaseColor", "Normal", "ORM"])
            self.assertGreaterEqual(spec["uv_tiling"], 1)
            self.assertLessEqual(spec["uv_tiling"], 8)

    def test_color_values_and_pbr_ranges(self):
        for rgb, roughness, metalness, _pattern, scale in surface.SURFACES.values():
            self.assertEqual(len(rgb), 3)
            self.assertTrue(all(type(c) is int and 0 <= c <= 255 for c in rgb))
            self.assertTrue(.07 <= roughness <= .98)
            self.assertTrue(0 <= metalness <= 1)
            self.assertTrue(1 <= scale <= 8)

    def test_noise_values_bounded_repeatably(self):
        for name in surface.SURFACES:
            for x, y in [(0,0), (37,91), (255,511), (511,511)]:
                a = surface.height(name, x, y)
                self.assertEqual(a, surface.height(name, x, y))
                self.assertTrue(0 <= a <= 1)

    def test_png_header_and_rgb_format(self):
        sample = surface.png_rgb([bytes([100, 200, 50])], 1, 1)
        self.assertTrue(sample.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(sample[12:16], b"IHDR")
        self.assertEqual(sample[25], 2)

    def test_review_authority_explicit(self):
        m = surface.manifest()
        self.assertFalse(m["production_maps_changed"])
        self.assertFalse(m["PIE_verified"])
        self.assertFalse(m["visual_approval"])
        self.assertIn("REVIEW_ONLY", m["authority"])

    def test_manifest_file_hashes_match_if_generated(self):
        path = surface.SOURCE / "surface_manifest.review.json"
        if not path.is_file():
            self.skipTest("source textures not generated yet")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["sha256"]), len(surface.SURFACES) * 3)
        for filename, sha in manifest["sha256"].items():
            self.assertRegex(filename, r"^T_FW_[a-z_]+_(BaseColor|Normal|ORM)\.png$")
            self.assertEqual(hashlib.sha256((surface.SOURCE / filename).read_bytes()).hexdigest(), sha)

    def test_staging_requires_explicit_native_opt_in(self):
        env = __import__("os").environ.copy()
        env.pop("TSTSS_SURFACE_STAGE", None)
        p = subprocess.run([sys.executable, str(SRC), "--stage-native"],
                           text=True, capture_output=True, env=env, timeout=10)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("explicit opt-in", p.stderr)

if __name__ == "__main__":
    unittest.main()
