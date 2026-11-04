"""Source-only safety/geometry tests for noncanonical V4 horizon stage, NOT UE QA."""
import ast
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"
PLAN=TOOLS/"plan_aureate_v4_horizon_review.py"
STAGE=TOOLS/"stage_aureate_v4_horizon_atmosphere_review.py"

spec=importlib.util.spec_from_file_location("v4_horizon_plan",PLAN)
v4=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)


class V4HorizonCameraSourceTests(unittest.TestCase):
    def test_existing_comparison_camera_looks_entirely_below_local_horizon(self):
        g=v4.frame_geometry(v4.OLD_CAMERA,v4.OLD_TARGET)
        self.assertLess(g["top_ray_elevation_degrees"],-8)
        self.assertFalse(g["local_horizon_intersects_frame"])
        self.assertEqual(g["approx_visible_sky_fraction"],0)

    def test_new_hero_camera_has_meaningful_sky_and_ocean(self):
        g=v4.frame_geometry(v4.HERO_CAMERA,v4.HERO_TARGET)
        self.assertGreater(g["top_ray_elevation_degrees"],7)
        self.assertLess(g["bottom_ray_elevation_degrees"],-16)
        self.assertTrue(g["local_horizon_intersects_frame"])
        self.assertGreaterEqual(g["approx_visible_sky_fraction"],0.25)
        self.assertLessEqual(g["approx_visible_sky_fraction"],0.4)

    def test_aspect_ratio_physical_camera_math(self):
        result=v4.frame_geometry(v4.HERO_CAMERA,v4.HERO_TARGET)
        self.assertAlmostEqual(result["horizontal_fov_degrees"],42)
        self.assertAlmostEqual(result["vertical_fov_degrees"],24.37,places=1)

    def test_horizon_math_rejects_nan_inf_and_vertical_singularity(self):
        for p,t in [((math.inf,0,1),(0,0,0)),((math.nan,0,1),(0,0,0)),
                    ((0,0,1),(0,0,0))]:
            with self.subTest(p=p):
                with self.assertRaises(ValueError):
                    v4.frame_geometry(p,t)

    def test_invalid_fov_dimensions_rejected(self):
        for f,wh in [(0,(1280,720)),(180,(1280,720)),(42,(0,720)),(42,(1280,0))]:
            with self.subTest(f=f,wh=wh):
                with self.assertRaises(ValueError):
                    v4.frame_geometry(v4.HERO_CAMERA,v4.HERO_TARGET,f,wh)

    def test_plan_protects_existing_review_and_all_starbourne_gameplay(self):
        p=v4.plan()
        self.assertEqual(p["scene_base"],v4.BASE_MAP)
        self.assertNotEqual(p["new_scene"],p["scene_base"])
        self.assertEqual(p["scene_source_sha256"],v4.SOURCE_MAP_SHA)
        self.assertTrue(p["original_camera"]["must_remain_unchanged"])
        self.assertFalse(p["approvals"]["starbourne_player_unlock"])
        self.assertFalse(p["approvals"]["production_art"])
        self.assertFalse(p["approvals"]["release"])
        self.assertIn("NOT_VERIFIED",p["gates"][0])
        self.assertFalse(p["environment_proposal"]["no_weather_or_physical_wave_simulation"] is False)

    def test_exact_offline_receipt_immutable(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"manifest.json"
            subprocess.run([sys.executable,str(PLAN),"--output",str(dest)],check=True,
                           capture_output=True,text=True)
            before=dest.read_bytes()
            subprocess.run([sys.executable,str(PLAN),"--output",str(dest),"--check"],
                           check=True,capture_output=True,text=True)
            self.assertEqual(before,dest.read_bytes())
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run([sys.executable,str(PLAN),"--output",str(dest)],check=True,
                               capture_output=True,text=True)
            dest.write_text('{"spoofed": true}',encoding="utf8")
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run([sys.executable,str(PLAN),"--check","--output",str(dest)],
                               check=True,capture_output=True,text=True)

    def test_stage_source_parses_without_engine_and_safeguards_new_paths(self):
        s=STAGE.read_text(encoding="utf8")
        ast.parse(s,filename=str(STAGE))
        for required in [
            "NONCANONICAL_HORIZON_VISUAL_REVIEW_ONLY",
            "AUREATE_CINEMATIC_V4_REVIEW_ONLY",
            "16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",
            "lib.duplicate_asset(SOURCE,TARGET)",
            "lib.does_asset_exist(TARGET)",
            "lib.does_directory_exist(MATERIAL_FOLDER)",
            'len(original)!=18',
            'cc.set_editor_property("field_of_view",42.0)',
            "SkyAtmosphere", "SkyLight", "ExponentialHeightFog",
            'sunlight.set_editor_property("atmosphere_sun_light",True)',
            'sunlight.set_editor_property("atmosphere_sun_light_index",0)',
            'fc.set_editor_property("fog_density",0.004)',
            "M_V4_HorizonOcean_Diagnostic",
            "MP_BASE_COLOR", "MP_ROUGHNESS",
            "NO_COLLISION",
            "V4_REVIEW_ANONYMOUS_CREW_SCALE_PROXY",
            "levels.save_current_level()",
            'hashfile(SOURCE_FILE)',
            '"gpu_screenshot_generated":False',
            '"creator_art_approved":False',
            '"starbourne_player_unlocked":False',
        ]:
            with self.subTest(term=required):
                self.assertIn(required,s)

    def test_stage_never_modifies_player_maps_or_claims_art(self):
        s=STAGE.read_text(encoding="utf8")
        for forbidden in ["RequestForm(", "SetStoryFlag", "SetPlayerStarbourneUnlocked",
                          "git push origin main", "load_player_save", "GameplayStatics.save_game_to_slot",
                          "lib.delete_asset(", "lib.rename_asset(", "pip install",
                          "producer_art_approved"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,s)
        self.assertIn('if not lib.duplicate_asset(SOURCE,TARGET)',s)
        self.assertIn('status["source_map_sha_after"]=hashfile(SOURCE_FILE)',s)

    def test_stage_camera_values_match_geometry_proposal(self):
        s=STAGE.read_text(encoding="utf8")
        self.assertIn('cp=unreal.Vector(900.0,1100.0,190.0)',s)
        self.assertIn('at=unreal.Vector(0.0,0.0,80.0)',s)
        self.assertIn(v4.HERO_LABEL,s)
        self.assertIn(v4.REVIEW_MAP,s)
        self.assertNotIn("NO_ART_APPROVAL_BYPASS",s)

    def test_windows_runner_guards_editor_ram_disk_and_all_original_maps(self):
        runner=(TOOLS/"run_aureate_v4_horizon_stage.py").read_text(encoding="utf8")
        ast.parse(runner)
        for term in (
            'free_ram','ram_gib()<4.2','ram_gib()<0.95',
            '14*1024**3','MAX_SECONDS=180',
            'UnrealEditor.exe','UnrealEditor-Cmd.exe',
            '-ExecutePythonScript=','-NullRHI',
            'four_maps_unchanged()','SOURCE_SHA',
        ):
            # SOURCE_SHA is in stage source; runner stores all four explicit digests.
            if term=='free_ram': continue
            if term=='SOURCE_SHA': continue
            with self.subTest(term=term):
                self.assertIn(term,runner)
        for sha in ('16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40',
                    'b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a',
                    '815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35',
                    '953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00'):
            self.assertIn(sha,runner)
        self.assertIn('OWN_CHILD_STOPPED_LOW_MEMORY',runner)
        self.assertNotIn('taskkill /IM',runner)
        self.assertNotIn('git push origin main',runner)
        self.assertIn('"real_gpu_rendered":False',runner)

    def test_src_only_not_native_unreal(self):
        self.assertFalse(v4.plan()["approvals"]["playable"])
        self.assertFalse(v4.plan()["approvals"]["release"])
        self.assertNotIn("import unreal",PLAN.read_text(encoding="utf8"))


if __name__=="__main__":
    unittest.main()
