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

    def test_six_bounded_scene_weather_and_light_references(self):
        self.assertEqual(set(surface.SCENE_LOOKS), set(surface.SCENES))
        self.assertEqual(set(surface.PRACTICAL_LAMPS), set(surface.SCENES))
        atmosphere_src = SRC.with_name("build_first_wake_atmosphere_review.py").read_text(encoding="utf-8")
        lighting_src = SRC.with_name("tstss_lighting_review.py").read_text(encoding="utf-8")
        for scene, (weather, hour, look) in surface.SCENE_LOOKS.items():
            self.assertIn('"' + weather + '"', atmosphere_src)
            self.assertIn('Look("' + look + '"', lighting_src)
            self.assertTrue(0 <= hour < 24)
            self.assertTrue(surface.manifest()["scene_looks"][scene]
                            ["weather_and_time_are_noncanonical_lookdev"])
        self.assertNotIn("Snow", [entry[0] for entry in surface.SCENE_LOOKS.values()])
        self.assertNotIn("Blizzard", [entry[0] for entry in surface.SCENE_LOOKS.values()])

    def test_only_known_sky_actors_will_be_replaced(self):
        self.assertEqual(len(surface.OLD_SKY_LABELS), 4)
        self.assertEqual(len(surface.HARBOR_INHERITED_LIGHTS), 2)
        code = SRC.with_name("stage_first_wake_multipath_shore.py").read_text(encoding="utf-8")
        for name in surface.OLD_SKY_LABELS:
            self.assertIn(name, code)
        self.assertEqual(len(set(surface.OLD_SKY_LABELS +
                                 surface.HARBOR_INHERITED_LIGHTS)), 6)

    def test_weather_enum_resolution_refuses_missing_member(self):
        from types import SimpleNamespace
        u = SimpleNamespace(ETSTSSWeather=SimpleNamespace(
            CLEAR=12, COASTAL_MIST=13, STORM=14, RAIN=15))
        self.assertEqual(surface.weather_enum_value(u, "CoastalMist"), 13)
        self.assertEqual(surface.weather_enum_value(u, "Clear"), 12)
        with self.assertRaisesRegex(RuntimeError, "unsupported native weather"):
            surface.weather_enum_value(u, "AuroralVeil")

    def test_native_staging_refuses_missing_original_lights_before_writes(self):
        class FakeWorld:
            def get_all_level_actors(self): return []
            def destroy_actor(self, _actor):
                raise AssertionError("Must not mutate map")
        with self.assertRaisesRegex(RuntimeError, "inventory drift"):
            surface.stage_scene_atmosphere(None, FakeWorld(),
                                            "VS06_SplashdownShore", None, None)

    def test_native_staging_refuses_unowned_extra_sky(self):
        class FakeClass:
            def __init__(self, name): self.name = name
            def get_name(self): return self.name
        class FakeActor:
            def __init__(self, label, klass): self.label, self.klass = label, klass
            def get_actor_label(self): return self.label
            def get_class(self): return FakeClass(self.klass)
        actors = [FakeActor(n, "DirectionalLight" if n.endswith("SunKey")
                            else "SkyLight" if n.endswith("SkyAmbient")
                            else "ExponentialHeightFog") for n in surface.OLD_SKY_LABELS]
        actors.append(FakeActor("Unowned_Sun", "DirectionalLight"))
        class FakeWorld:
            def get_all_level_actors(self): return actors
            def destroy_actor(self, _actor):
                raise AssertionError("Must not mutate map")
        with self.assertRaisesRegex(RuntimeError, "duplicate illumination"):
            surface.stage_scene_atmosphere(None, FakeWorld(),
                                            "VS06_SplashdownShore", None, None)

    def test_guarded_scene_source_map_receipts_are_present(self):
        proof = surface.PROJECT / "Docs/Evidence/vertical_slice_map_readback_20261110.json"
        self.assertTrue(proof.is_file())
        receipt = json.loads(proof.read_text(encoding="utf-8"))
        self.assertEqual(set(receipt["map_validation"]), set(surface.SCENES))
        for scene in surface.SCENES:
            self.assertEqual(
                hashlib.sha256((surface.PROJECT / "Content/TSTSS/Review/VerticalSlice" /
                                (scene + ".umap")).read_bytes()).hexdigest(),
                receipt["map_validation"][scene]["source_sha256"])

if __name__ == "__main__":
    unittest.main()
