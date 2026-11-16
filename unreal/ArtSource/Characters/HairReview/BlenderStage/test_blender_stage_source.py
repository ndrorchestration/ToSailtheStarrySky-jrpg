"""Source-contract tests only. They do not run Blender or certify graphics."""
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
PY=HERE/"build_ender_v3_review_scene.py"
PS=HERE/"Start-TSTSSCharacterHairReview.ps1"


class BlenderStageSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script=PY.read_text(encoding="utf-8")
        cls.launcher=PS.read_text(encoding="utf-8")

    def test_only_original_source_locked_asset(self):
        self.assertIn("bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e",self.script)
        self.assertIn("Ender_BroadLayerHair_V3_NONCANONICAL.glb",self.script)
        self.assertIn("bpy.ops.import_scene.gltf",self.script)
        self.assertIn("len(subjects)!=1",self.script)
        self.assertIn("head_fit",self.script.lower())  # False status is mandatory below.
        for forbidden in ("Genesis9_BaseShirtShorts", "dForce Pixie Hair", "open('C:/MH5",
                          "C:\\Users\\Public\\Documents\\My DAZ", "bpy.ops.export_scene"):
            self.assertNotIn(forbidden,self.script)

    def test_four_cameras_and_no_art_promotion(self):
        for name in ("01_FRONT_plus_Y", "02_THREE_QUARTER_plus_XY",
                     "03_RIGHT_plus_X", "04_REAR_minus_Y"):
            self.assertIn(name,self.script)
        for required in (
            "TSTSS_ART_APPROVED", "TSTSS_HEAD_FIT_VERIFIED", "TSTSS_RIGGED_GROOM",
            "TSTSS_NATIVE_UNREAL", "creator_approved", "native_unreal",
            "daz_data_used", "gpu_render_executed"):
            self.assertIn(required,self.script)
        self.assertIn("hair[\"TSTSS_ART_APPROVED\"]=False",self.script)
        self.assertIn('"creator_approved":False',self.script)
        self.assertIn('"gpu_render_executed":False',self.script)

    def test_import_restores_authored_up_axis_before_computing_cameras(self):
        self.assertIn('hair.rotation_mode="XYZ"',self.script)
        self.assertIn('hair.rotation_euler=(-math.pi/2,0,0)',self.script)
        self.assertIn('bpy.context.view_layer.update()',self.script)
        self.assertLess(self.script.index('bpy.context.view_layer.update()'),
                        self.script.index('geometry_bbox='))
        self.assertIn('source_up_axis_corrected',self.script)

    def test_strict_executable_and_no_overwrite(self):
        for required in ("bpy.app.version[:3]", "(5,2,4)",
                         "existing project/evidence; never overwrite",
                         "output directory must already exist",
                         "source missing or changed"):
            self.assertIn(required,self.script)
        self.assertNotIn("bpy.ops.render.render(",self.script)

    def test_launcher_explicit_opt_in_and_foreign_session_guard(self):
        for required in (
            "param([switch]$Launch)", "Get-CimInstance Win32_Process",
            "UnrealEditor.exe", "LiveCodingConsole.exe", "UnrealBuildTool.exe",
            "blender.exe", "if(!$Launch)", "CHECK_ONLY_NO_BLENDER_LAUNCHED",
            "$ram -lt 6.5", "$disk -lt 14.0",
            "$PSScriptRoot", "Start-Process"
        ):
            if required=="Start-Process":
                self.assertNotIn(required,self.launcher)
            else:
                self.assertIn(required,self.launcher)
        for forbidden in ("Stop-Process","Remove-Item","Clear-Content",
                          "Set-ExecutionPolicy","git reset","-Force"):
            self.assertNotIn(forbidden,self.launcher)


if __name__=="__main__":
    unittest.main()
