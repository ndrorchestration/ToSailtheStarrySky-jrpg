"""Engine-free Ender broad-layer V3 art asset regression checks only.

No test here establishes UE-native import, scalp clearance or artistic likeness.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from verify_ender_copper_hair_v3 import ASSET, HERE, inspect, parse, require

SOURCE = HERE / "generate_ender_copper_hair_v3.py"
EXPECTED = "bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e"


class EnderV3SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ASSET.read_bytes()

    def test_real_committed_static_glb_and_sha(self):
        self.assertEqual(hashlib.sha256(self.data).hexdigest(),EXPECTED)
        result=inspect(self.data)
        self.assertEqual(result["status"],"SOURCE_GEOMETRY_PASS_ART_HOLD")
        self.assertEqual(result["triangles"],29280)
        self.assertEqual(result["materials"],4)

    def test_creator_approval_and_native_status_explicitly_false(self):
        doc,_=parse(self.data)
        flags=doc["extras"]
        self.assertFalse(flags["creator_approved"])
        self.assertFalse(flags["head_fit_verified"])
        self.assertFalse(flags["native_render_verified"])
        self.assertFalse(flags["gameplay_asset"])
        self.assertFalse(flags["rigged"])
        self.assertFalse(flags["groom"])
        self.assertNotIn("skins",doc)
        self.assertNotIn("animations",doc)

    def test_no_tube_clump_inventory_and_face_clearance_unclaimed(self):
        # These categories come from the independent source receipt; they
        # describe model topology, not a visually or anatomically accepted groom.
        src=SOURCE.read_text(encoding="utf-8")
        for token in ("range(24)", "range(9)", "range(12)", "sculpted_blade("):
            self.assertIn(token,src)
        self.assertIn("FAIL_CLOSED",src)
        self.assertIn('"head_fit_verified":False',src)

    def test_bad_signature_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"GLB signature"):
            inspect(b"BAD!"+self.data[4:])

    def test_forced_creator_approval_is_rejected(self):
        old=b'"creator_approved":false'
        new=b'"creator_approved":true '
        self.assertEqual(len(old),len(new))
        self.assertIn(old,self.data)
        with self.assertRaisesRegex(ValueError,"false-promotion"):
            inspect(self.data.replace(old,new,1))

    def test_same_host_regeneration_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="tstss_ender_v3_") as d:
            root=Path(d)
            runs=[]
            for name in ("first","second"):
                out=root/name
                out.mkdir()
                p=subprocess.run([sys.executable,str(SOURCE),"--outdir",str(out)],
                    capture_output=True,text=True,check=True)
                report=json.loads(p.stdout)
                data=(out/ASSET.name).read_bytes()
                self.assertEqual(report["sha256"],hashlib.sha256(data).hexdigest())
                self.assertFalse(report["ue_native_import"])
                self.assertFalse(report["creator_approved"])
                self.assertEqual(inspect(data)["triangles"],29280)
                runs.append(data)
            self.assertEqual(runs[0],runs[1],"same-host regeneration drift")
            locked=subprocess.run(
                [sys.executable,str(SOURCE),"--outdir",str(root/"first")],
                capture_output=True,text=True)
            self.assertNotEqual(locked.returncode,0)
            self.assertIn("FAIL_CLOSED",locked.stderr)
            self.assertEqual((root/"first"/ASSET.name).read_bytes(),runs[0])


if __name__=="__main__":
    unittest.main()
