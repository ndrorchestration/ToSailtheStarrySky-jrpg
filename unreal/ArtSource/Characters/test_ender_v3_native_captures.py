"""Fail-closed, engine-free V3 native-render provenance negative controls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify_ender_v3_native_captures as subject

def specimen():
    return {
      "status":"V3_NATIVE_SCREENSHOT_TASKS_COMPLETE_PIXEL_QA_PENDING",
      "engine":"5.8.4-58902052+++UE5+Release-5.8",
      "map":subject.MAP,"saved_map_sha256_before":subject.MAP_SHA,
      "saved_map_sha256_after":subject.MAP_SHA,
      "asset":"/Game/ArtLookdev/Characters/EnderLandmarksV3/Mesh.Mesh",
      "source_sha256":subject.SHA,
      "views":list(subject.VIEWS),
      "capture_tasks":[{"name":n,"requested":"C:/preview/"+n+".png","ticks":10}
                       for n in subject.VIEWS],
      "unrigged":True,"creator_likeness_approved":False,
      "source_modified":False,"production_map_modified":False
    }

class NativeCaptureReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.receipt=self.folder/"receipt.json"

    def call(self,content,hashes=("a","b","c")):
        self.receipt.write_text(json.dumps(content),encoding="utf-8")
        with patch.object(subject,"resolve_capture",
                          side_effect=lambda folder,name: self.folder/(name+".png")), \
             patch.object(subject,"inspect_png",
                          side_effect=[{"sha256":s} for s in hashes]), \
             patch.object(subject,"visible_head",
                          return_value={"central_foreground_fraction":.12}):
            return subject.verify(self.folder,self.receipt)

    def test_valid_receipt_does_not_imply_art_approval(self):
        r=self.call(specimen())
        self.assertEqual(r["status"],"V3_NATIVE_SCREENSHOT_INTEGRITY_PASS_ART_HOLD")
        self.assertFalse(r["creator_approved"])

    def test_duplicate_or_untrusted_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicated"):
            self.call(specimen(),("same","same","other"))
        invalid=[
            ("status","PENDING"),("engine","5.7.2"),
            ("source_sha256","0"*64),
            ("asset","/Game/Production/Characters/Ender.Ender"),
            ("creator_likeness_approved",True),
            ("unrigged",False),
            ("production_map_modified",True),
            ("saved_map_sha256_after","b"*64),
            ("views",["v3_head_front"]),
            ("capture_tasks",[]),
        ]
        for k,v in invalid:
            data=specimen()
            data[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):
                self.call(data)

    def test_native_safety_script_does_not_mutate_production(self):
        root=Path(__file__).resolve().parent
        imp=(root/"intake_ender_fidelity_v3.py").read_text(encoding="utf-8")
        cap=(root/"capture_ender_fidelity_v3_native.py").read_text(encoding="utf-8")
        self.assertIn('project.name!="CastAllSandbox"',imp)
        self.assertIn('PROJECT.name!="CastAllSandbox"',cap)
        self.assertIn('"replace_existing",False',imp)
        self.assertNotIn('save_current_level(',cap)
        self.assertNotIn('Game/Characters/',cap)
        self.assertIn('"creator_likeness_approved":False',cap)

if __name__=="__main__":
    unittest.main()
