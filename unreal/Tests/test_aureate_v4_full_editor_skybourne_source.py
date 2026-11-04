"""Engine-free safety checks for a reviewed Skybourne native full-Editor scene.

These source tests are NOT native actor/render tests and must not be labeled so.
"""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"


class NativeSkybourneContractSourceTests(unittest.TestCase):
    def source(self,name):
        p=TOOLS/name
        self.assertTrue(p.is_file(),name)
        s=p.read_text(encoding="utf-8")
        ast.parse(s,filename=str(p))
        return s

    def test_skybourne_stage_only_in_exact_review_sandbox_and_new_map(self):
        s=self.source("aureate_v4_full_editor_skybourne_stage.py")
        self.assertIn("AureateCinematicV4Sandbox",s)
        self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",s)
        self.assertIn("Skybourne_Hero_20261103_FullEditor",s)
        self.assertIn("if lib.does_asset_exist(MAP)",s)
        self.assertIn("native_import_receipt.json",s)
        self.assertIn("SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS",s)

    def test_exact_four_persistent_wing_ids_not_extra_wings(self):
        s=self.source("aureate_v4_full_editor_skybourne_stage.py")
        for identity in ("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD"):
            self.assertIn(identity,s)
        self.assertIn('if len(set(report["wing_identity_labels"]))!=4',s)
        self.assertIn("SHARED_HULL_CINEMATIC_V4_TRIM",s)
        self.assertIn("FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",s)
        self.assertIn("CENTRAL_LIVING_QUARTERS_PROXY",s)

    def test_native_skybourne_scene_saves_map_and_never_claims_render(self):
        s=self.source("aureate_v4_full_editor_skybourne_stage.py")
        self.assertIn("unreal.StaticMeshActor",s)
        self.assertIn("levels.save_current_level()",s)
        self.assertIn('"real_gpu_frame_generated":False',s)
        self.assertIn("NOT_YET_GPU_RENDERED_OR_ART_APPROVED",s)
        self.assertIn('"starbourne_player_unlocked":False',s)

    def test_staging_runner_is_bounded_and_no_user_editor_process_kill(self):
        s=self.source("run_aureate_v4_full_editor_skybourne_stage.py")
        self.assertIn("-ExecutePythonScript=",s)
        self.assertIn("-NullRHI",s)
        self.assertIn("free_ram()<4.2",s)
        self.assertIn("MAX_SECONDS=160",s)
        self.assertIn("proc.terminate()",s)
        self.assertIn("proc.kill()",s)
        self.assertIn("user_editor_untouched",s)
        self.assertIn("host_full_editor_skybourne_stage_receipt.json",s)
        self.assertNotIn("taskkill /IM",s)

    def test_capture_checks_exact_saved_map_and_all_four_laces(self):
        s=self.source("capture_aureate_v4_skybourne_native_gpu.py")
        self.assertIn("16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",s)
        self.assertIn("V4_NONCANONICAL_CAMERA_THREE_QUARTER",s)
        self.assertIn("V4_NONCANONICAL_",s)
        for identity in ("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD"):
            self.assertIn(identity,s)
        self.assertIn("unreal.AutomationLibrary.take_high_res_screenshot",s)
        self.assertIn("NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING",s)
        self.assertIn('if sha(MAP_FILE)!=MAP_SHA',s)

    def test_gpu_runner_only_calls_d3d11_and_never_conflates_png_with_approval(self):
        s=self.source("run_aureate_v4_skybourne_gpu_capture.py")
        self.assertIn("-ExecutePythonScript=",s)
        self.assertIn("-d3d11",s)
        self.assertNotIn("-NullRHI",s)
        self.assertIn("free_ram()<6.5",s)
        self.assertIn("new_art_approval",s)
        self.assertIn("NATIVE_GPU_CAPTURE_TASK_PASS_PIXEL_QA_PENDING",s)
        self.assertNotIn("Stop-Process",s)

    def test_no_gameplay_or_permanent_art_mutations(self):
        for name in ("aureate_v4_full_editor_skybourne_stage.py",
                     "run_aureate_v4_full_editor_skybourne_stage.py",
                     "capture_aureate_v4_skybourne_native_gpu.py",
                     "run_aureate_v4_skybourne_gpu_capture.py"):
            s=self.source(name)
            for ban in ("RequestForm(", "git push origin main",
                        "unreal.AssetToolsHelpers.get_asset_tools().rename_assets",
                        "SetStoryFlag", "load_player_save", "SetPlayerStarbourneUnlocked"):
                with self.subTest(name=name,ban=ban):
                    self.assertNotIn(ban,s)


if __name__=="__main__":
    unittest.main()
