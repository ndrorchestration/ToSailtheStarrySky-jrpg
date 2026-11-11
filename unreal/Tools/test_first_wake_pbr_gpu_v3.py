"""Source-only checks: 200-actor PBR D3D evidence and cinematic sign gate."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parent))
import capture_first_wake_pbr_gpu_v3 as capture
import intake_first_wake_pbr_gpu_v3 as intake
import run_first_wake_pbr_gpu_v3 as host
import first_wake_cinematic_sign_policy_v3 as signs

class TestPBRNativeGPU(unittest.TestCase):
    def test_requires_entire_200_actor_native_custody(self):
        self.assertEqual(367,intake.MIN_FILES)
        self.assertEqual("3e3d65e1e30b7620b6ddc4d47cf7b94e447d930a7f290818068ac50a51641815",
                         intake.WORLD_SHA)
        self.assertEqual("2c22f9ad1c043a97fbbd8cebbf1adae1ab1e3ffd",
                         intake.SOURCE_HEAD)
        self.assertEqual("review/ue58-vslice-lookdev-gpu-20261111",intake.BRANCH)

    def test_four_actual_UE_camera_views_and_immutable_level(self):
        self.assertEqual(4,len(capture.CAMERAS))
        self.assertEqual(4,len(capture.FRAMES))
        self.assertEqual(4,len(set(capture.FRAMES)))
        self.assertEqual((1280,720),capture.SIZE)
        self.assertEqual("Quay_Paving_Study",capture.CAMERAS[3][0])
        self.assertEqual("Engineering_OpenQuay",capture.CAMERAS[1][0])
        self.assertEqual("D3D11_PBR_V3_20261111_R1",capture.OUTPUT.name)
        code=Path(capture.__file__).read_text(encoding="utf-8")
        self.assertNotIn("save_current_level",code)
        self.assertNotIn("destroy_actor",code)
        self.assertNotIn("save_dirty_packages",code)
        self.assertIn("sign.suppress_transient_only(actors,unreal)",code)

    def test_source_map_and_real_native_stage_remain_separate(self):
        self.assertNotEqual(intake.WORLD_REL,
                            "unreal/Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap")
        self.assertTrue(capture.WORLD_FILE.name.endswith("REVIEW_V3.umap"))
        self.assertIn("FIRSTWAKE_PBR_GPU_NATIVE_RECEIPT",
                      Path(capture.__file__).read_text(encoding="utf-8"))

    def test_native_visibility_uses_actor_hidden_property_not_nonexistent_method(self):
        code=Path(signs.__file__).read_text(encoding="utf-8")
        self.assertNotIn(".is_hidden()",code)
        self.assertIn('get_editor_property("hidden")',code)
        self.assertIn('set_actor_hidden_in_game(True)',code)
        self.assertEqual(7,len(signs.MILESTONES))

    def test_retry_receipts_never_overwrite_failed_original(self):
        self.assertTrue(capture.OUTPUT.name.endswith("_R1"))
        self.assertTrue(host.LOG.name.endswith("_R1.log"))
        self.assertTrue(host.HOST.name.endswith("_R1.json"))
        self.assertTrue(host.REPORT.name.endswith("_R1"))
        self.assertNotEqual(capture.OUTPUT.parent/"PBR_V3_GPU_UE584_D3D11_HostReceipt_20261111.json",host.HOST)

    def test_cinematic_sign_gate_only_hides_signs(self):
        self.assertEqual(7,len(signs.MILESTONES))
        names=[signs.SIGN_PREFIX+s for s in signs.MILESTONES]
        names +=[signs.MILESTONE_PREFIX+s for s in signs.MILESTONES]
        self.assertEqual(7,len(signs.sign_inventory(names)))
        with self.assertRaisesRegex(RuntimeError,"HOLD"):
            signs.sign_inventory(names[:-1])

    def test_fake_native_controller_or_claims_not_accepted(self):
        frames=[{"file":p.name,"bytes":6000,"size":[1280,720],"sha256":f"h{i}"}
                for i,p in enumerate(capture.FRAMES)]
        data={"status":capture.STATUS,"world_sha256":intake.WORLD_SHA,
              "source_world_preserved":True,"no_source_level_save":True,
              "native_level_actors":200,
              "transient_hidden_developer_text_signs":7,
              "hidden_gameplay_milestones":0,
              "transient_sign_policy_status":"ONLY_SEVEN_DEV_SIGNS_HIDDEN_TRANSIENT_FOR_CAPTURE",
              "gpu_visual_approved":False,
              "pie_verified":False,"ocean_splashdown_verified":False,
              "starbourne_unlocked":False,
              "frames_expected":4,"images":frames}
        self.assertTrue(host.match_receipt(data,frames))
        for name,bad in (("status","NATIVE_PBR_GPU_CAPTURE_HOLD"),
                         ("native_level_actors",199),
                         ("transient_hidden_developer_text_signs",6),
                         ("hidden_gameplay_milestones",1),
                         ("source_world_preserved",False),
                         ("gpu_visual_approved",True),
                         ("pie_verified",True),
                         ("ocean_splashdown_verified",True),
                         ("starbourne_unlocked",True)):
            with self.subTest(name=name),self.assertRaisesRegex(RuntimeError,"HOLD"):
                host.match_receipt(dict(data,**{name:bad}),frames)
        with self.assertRaisesRegex(RuntimeError,"HOLD"):
            host.match_receipt(data,frames[:-1])

    def test_gpu_host_never_runs_in_hosted_linux(self):
        with mock.patch.object(host.sys,"platform","linux"):
            with self.assertRaisesRegex(RuntimeError,"Windows"):
                host.check()
        self.assertGreaterEqual(host.MIN_RAM_GIB,6.5)
        self.assertGreaterEqual(host.MIN_DISK_GIB,14)
        self.assertLessEqual(host.MAX_SECONDS,360)

    def test_registered_camera_only_new_scope(self):
        project=Path(__file__).resolve().parents[1]
        registry=(project/"Content/Python/test_first_wake_pbr_gpu_v3.py").read_text("utf-8")
        prior=(project/"Content/Python/test_first_wake_slice_object_gpu_review.py").read_text("utf-8")
        self.assertIn("capture_first_wake_pbr_gpu_v3.py",registry)
        self.assertIn('project!=expected',registry)
        self.assertIn("OLD_115_ACTOR_GPU_TEST_OUT_OF_SCOPE",prior)
        self.assertIn("if Path(unreal.Paths.project_dir()).resolve()",prior)

    def test_plugin_only_not_committed_to_canonical_project(self):
        # This is a separate runtime-only uncommitted .uproject change.
        original=Path(__file__).resolve().parents[1]/"ToSailTheStarrySky.uproject"
        data=original.read_text(encoding="utf-8")
        self.assertIn("PythonScriptPlugin",data)
        self.assertNotIn('"Name": "PythonAutomationTest"',data)

    def test_negative_screenshot_assurance_remains_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            try:
                from PIL import Image
            except ImportError:
                self.skipTest("Pillow optional in hosted-source tests")
            pic=Path(d)/"flat.png"
            Image.new("RGB",(1280,720),(0,0,0)).save(pic)
            with self.assertRaisesRegex(RuntimeError,"black or featureless"):
                host.quality(pic)
            positive=Image.new("RGB",(1280,720),(22,45,90))
            from PIL import ImageDraw
            ImageDraw.Draw(positive).rectangle((0,0,600,600),fill=(180,130,90))
            positive.save(pic)
            self.assertEqual("GPU_PIXEL_EVIDENCE_ONLY_NO_CREATOR_ART_APPROVAL",
                             host.quality(pic)["approval"])

if __name__=="__main__":
    unittest.main()
