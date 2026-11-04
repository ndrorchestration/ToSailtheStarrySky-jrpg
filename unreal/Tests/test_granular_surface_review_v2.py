"""Engine-free controls for optional original granular lookdev V2; NOT Unreal GPU proof."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

PATH=Path(__file__).resolve().parents[1]/"Tools/granular_surface_review_v2.py"

class GranularReviewSourceTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location("tstss_granular_v2",PATH)
        self.m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)

    def api(self,occupied=False,dirty=False,missing=False):
        return SimpleNamespace(
            EditorAssetLibrary=SimpleNamespace(
                does_directory_exist=Mock(return_value=occupied)),
            EditorLoadingAndSavingUtils=SimpleNamespace(
                get_dirty_map_packages=Mock(return_value=["map"] if dirty else []),
                get_dirty_content_packages=Mock(return_value=[])),
            load_asset=Mock(return_value=None if missing else object()),
        )

    def test_only_two_original_review_surfaces(self):
        p=self.m.validate()
        self.assertEqual(p["surfaces"],["SilkenDune","WindCrustSnow"])
        self.assertTrue(p["root"].startswith("/Game/TSTSS/Review/"))
        self.assertEqual(p["native_render"],"NOT_RUN")
        self.assertFalse(p["production_terrain_edited"])

    def test_no_copied_proprietary_shader_or_geometry_displacement(self):
        code=self.m.COLOR_HLSL+self.m.NORMAL_HLSL+self.m.HIGHLIGHT_HLSL
        for banned in ("#include","Texture2DSample","WorldPositionOffset",
                       "SceneDepth","Time *"):
            self.assertNotIn(banned,code)
        self.assertIn("return normalize(float3",self.m.NORMAL_HLSL)

    def test_highlight_day_gated_anti_aliased_and_bounded(self):
        h=self.m.HIGHLIGHT_HLSL
        for fragment in ("fwidth(","saturate(SunStrength)","saturate(Glitter)",
                         "saturate(Quality)","min(glow,0.65)","saturate(dot(n,l))"):
            self.assertIn(fragment,h)

    def test_snow_is_not_sand_with_white_albedo_only(self):
        self.assertIn("float windCrust",self.m.COLOR_HLSL)
        self.assertIn("Crust",self.m.NORMAL_HLSL)
        self.assertIn("float snowFactor",self.m.HIGHLIGHT_HLSL)

    def test_review_directory_refuses_overwrite(self):
        a=self.api(occupied=True)
        with self.assertRaisesRegex(RuntimeError,"occupied"):
            self.m.preflight(a)
        a.load_asset.assert_not_called()

    def test_dirty_editor_refuses(self):
        with self.assertRaisesRegex(RuntimeError,"unsaved"):
            self.m.preflight(self.api(dirty=True))

    def test_missing_engine_geometry_refuses(self):
        with self.assertRaisesRegex(RuntimeError,"missing"):
            self.m.preflight(self.api(missing=True))

    def test_clean_preflight_has_only_review_shapes(self):
        self.assertEqual(set(self.m.preflight(self.api())),{"Plane","Sphere"})

    def test_shader_compilation_must_return_explicit_success(self):
        self.m.require_compilation([])
        with self.assertRaisesRegex(RuntimeError,"unverified"):
            self.m.require_compilation(None)
        with self.assertRaisesRegex(RuntimeError,"failed"):
            self.m.require_compilation(["unexpected compile error"])

    def test_mask_connects_with_documented_first_input_semantics(self):
        # Epic UE5.8: empty target-input name chooses the first pin.
        source=PATH.read_text(encoding="utf8")
        self.assertIn('edit.connect_material_expressions(color,"",rgb,"")',source)
        self.assertIn('edit.connect_material_expressions(color,"",rough,"")',source)
        self.assertNotIn('edit.connect_material_expressions(color,"",rgb,"Input")',source)

    def test_no_fake_native_unreal_available_outside_editor(self):
        with self.assertRaisesRegex(RuntimeError,"Unreal Engine Editor"):
            self.m.build()

if __name__=="__main__":
    unittest.main()
