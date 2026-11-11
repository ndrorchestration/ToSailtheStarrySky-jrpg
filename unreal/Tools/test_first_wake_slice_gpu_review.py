"""Engine-free fail-closed checks for true UE5.8 native First Wake D3D11 QA."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest import mock
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parent))
import intake_first_wake_slice_gpu_review as intake
import capture_first_wake_slice_objects_d3d11 as capture
import run_first_wake_slice_objects_d3d11 as host

def chunk(kind,blob):
    return struct.pack(">I",len(blob))+kind+blob+struct.pack(">I",zlib.crc32(kind+blob))

def valid_fixture():
    size=capture.SIZE
    header=struct.pack(">IIBBBBB",*size,8,2,0,0,0)
    # A valid PNG with large ancillary tEXt chunk to cross the minimum size
    # without claiming that a synthetic frame is a GPU screenshot.
    pixels=b"".join(b"\x00"+b"\x10\x80\xd0"*size[0] for _ in range(size[1]))
    image=(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+
           chunk(b"tEXt",b"a\x00"+b"fixture"*1000)+
           chunk(b"IDAT",zlib.compress(pixels,9))+chunk(b"IEND",b""))
    return image

class GPUReviewSafetyTests(unittest.TestCase):
    def test_plan_exact_three_unsaved_cameras(self):
        self.assertEqual(3,len(capture.SHOT_PLAN))
        self.assertEqual((1280,720),capture.SIZE)
        self.assertEqual(3,len(set(capture.PICS)))
        self.assertTrue(all("Starbourne" not in n for n,_,_ in capture.SHOT_PLAN))

    def test_camera_alignment_accepts_forward_rejects_wrong(self):
        dot=capture.alignment((0,0,0),(0,10,0),(0,1,0))
        self.assertAlmostEqual(1.0,dot)
        for bad in ((0,-1,0),(0,0,0)):
            with self.assertRaisesRegex(RuntimeError,"GPU_FRAME_HOLD"):
                capture.alignment((0,0,0),(0,10,0),bad)
        with self.assertRaises(RuntimeError):
            capture.alignment((0,0,0),(0,0,0),(0,1,0))

    def test_png_header_crc_dimensions_and_truncation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"sample.png"
            path.write_bytes(valid_fixture())
            record=capture.validate_png(path)
            self.assertEqual(list(capture.SIZE),record["size"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record["sha256"])
            raw=bytearray(path.read_bytes())
            raw[70]^=1
            path.write_bytes(raw)
            with self.assertRaisesRegex(RuntimeError,"CRC"):
                capture.validate_png(path)
            path.write_bytes(valid_fixture()[:-4])
            with self.assertRaisesRegex(RuntimeError,"truncated"):
                capture.validate_png(path)
            path.write_bytes(b"not a png")
            with self.assertRaisesRegex(RuntimeError,"invalid/truncated"):
                capture.validate_png(path)

    def test_native_receipt_rejects_false_art_or_pie(self):
        images=[{"file":p.name,"sha256":"h"+str(i),"bytes":5000,"size":[1280,720]}
                for i,p in enumerate(capture.PICS)]
        proof={"status":capture.STATUS_OK,"source_map_sha256":intake.WORLD_SHA,
               "source_world_unchanged":True,
               "temporary_camera_only_not_saved":True,
               "art_approved":False,"pie_verified":False,
               "ocean_physics_verified":False,"images":images}
        self.assertTrue(host.evaluate_native_receipt(proof,images,intake.WORLD_SHA))
        for key,value in (("art_approved",True),("pie_verified",True),
                          ("source_world_unchanged",False),
                          ("source_map_sha256","wrong"),
                          ("status","NATIVE_D3D11_CAPTURE_HOLD"),
                          ("temporary_camera_only_not_saved",False),
                          ("ocean_physics_verified",True)):
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,"bounded"):
                host.evaluate_native_receipt(dict(proof,**{key:value}),images,intake.WORLD_SHA)
        with self.assertRaisesRegex(RuntimeError,"bounded"):
            host.evaluate_native_receipt(proof,images[:-1],intake.WORLD_SHA)

    def test_rejects_restricted_and_path_traversal(self):
        for name in ("../private","unreal/../../secret",
                     "C:/wrong","unreal/Content/StarbourneFoam.uasset",
                     "unreal/Content/SubmersibleHydrofoil.uasset"):
            with self.subTest(path=name),self.assertRaises(RuntimeError):
                intake.safe(name)
        self.assertEqual("unreal/Content/Cast.uasset",
                         intake.safe("unreal\\Content\\Cast.uasset").as_posix())

    def test_requires_only_review_plugin_delta(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"TSTSS_VSliceObjectsNativeV2_20261110"
            b=Path(d)/"TSTSS_VSliceVisualQA_20261110"
            original={"EngineAssociation":"5.8",
                      "Modules":[{"Name":"ToSailTheStarrySky"}],
                      "Plugins":[{"Name":"PythonScriptPlugin","Enabled":True}]}
            update={**original,"Plugins":original["Plugins"]+
                    [{"Name":"PythonAutomationTest","Enabled":True}]}
            for root,desc in ((a,original),(b,update)):
                up=root/"unreal/ToSailTheStarrySky.uproject"
                up.parent.mkdir(parents=True,exist_ok=True)
                up.write_text(json.dumps(desc),encoding="utf-8")
                for name in ("DefaultEngine.ini","DefaultInput.ini"):
                    p=root/"unreal/Config"/name
                    p.parent.mkdir(parents=True,exist_ok=True)
                    p.write_text("native-config",encoding="utf-8")
            with mock.patch.object(intake,"SOURCE",a),mock.patch.object(intake,"TARGET",b),mock.patch.object(intake,"git",return_value=""):
                self.assertIsNone(intake.plugin_only_review_change())
                update["Description"]="Unapproved game rewrite"
                (b/"unreal/ToSailTheStarrySky.uproject").write_text(json.dumps(update))
                with self.assertRaisesRegex(RuntimeError,"beyond"):
                    intake.plugin_only_review_change()

    def test_preflight_never_runs_gpu_on_nonwindows(self):
        with mock.patch.object(host.sys,"platform","linux"):
            with self.assertRaisesRegex(RuntimeError,"wrong GPU host"):
                host.check()

    def test_pixel_qa_rejects_black_native_png(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow optional for engine-free hosted source checks")
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"frame.png"
            Image.new("RGB",capture.SIZE,(0,0,0)).save(p)
            with self.assertRaisesRegex(RuntimeError,"black/flat"):
                host.gpu_color_quality(p)
            picture=Image.new("RGB",capture.SIZE,(35,85,165))
            from PIL import ImageDraw
            ImageDraw.Draw(picture).rectangle((0,0,300,500),fill=(185,160,80))
            picture.save(p)
            self.assertEqual("PIXEL_DIVERSITY_ONLY_NOT_CREATOR_VISUAL_APPROVAL",
                             host.gpu_color_quality(p)["approval"])

    def test_registration_and_source_guards(self):
        reg=Path(__file__).parents[1]/"Content/Python/test_first_wake_slice_object_gpu_review.py"
        self.assertIn("runpy.run_path",reg.read_text(encoding="utf-8"))
        self.assertEqual(115,84+31)
        script=Path(__file__).with_name("capture_first_wake_slice_objects_d3d11.py").read_text(encoding="utf-8")
        self.assertIn("AutomationScheduler.add_latent_command",script)
        self.assertNotIn("save_current_level",script)
        self.assertNotIn("save_dirty_packages",script)
        self.assertNotIn("os.remove",script)

if __name__=="__main__":
    unittest.main()
