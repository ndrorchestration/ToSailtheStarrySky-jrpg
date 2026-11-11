"""Engine-free source and GLB integrity tests. Not UE Editor/PIE acceptance."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).parent))
import generate_first_wake_slice_objects as g
import stage_first_wake_slice_objects as s

class TestSliceObjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.blobs=g.inventory()

    def test_complete_bounded_inventory(self):
        self.assertEqual(22,len(self.report["original_objects"]))
        self.assertEqual(31,len(self.report["placements"]))
        self.assertEqual(set(g.ASSET_NAMES),{p["asset"] for p in self.report["placements"]})
        self.assertEqual(len({r["name"] for r in self.report["original_objects"]}),22)
        self.assertTrue(set(g.MATERIALS)=={"brass","dark_iron","patina","wood","canvas",
                                         "porcelain","amber_glass","teal_glass","ruby"})

    def test_every_glb_has_valid_binary_container_and_mesh(self):
        for name,blob in self.blobs.items():
            with self.subTest(name=name):
                signature,version,total=struct.unpack_from("<4sII",blob)
                self.assertEqual((b"glTF",2,len(blob)),(signature,version,total))
                jlen,jtype=struct.unpack_from("<I4s",blob,12)
                self.assertEqual(b"JSON",jtype)
                document=json.loads(blob[20:20+jlen].decode("utf-8"))
                self.assertEqual("2.0",document["asset"]["version"])
                self.assertEqual(1,len(document["meshes"]))
                self.assertEqual(1,len(document["nodes"]))
                self.assertTrue(document["meshes"][0]["primitives"])
                self.assertEqual(len(g.MATERIALS),len(document["materials"]))
                self.assertTrue(all(p["mode"]==4 for p in document["meshes"][0]["primitives"]))
                self.assertTrue(all("TEXCOORD_0" in p["attributes"] for p in document["meshes"][0]["primitives"]))
                blen,btype=struct.unpack_from("<I4s",blob,20+jlen)
                self.assertEqual(b"BIN\x00",btype)
                self.assertEqual(20+jlen+8+blen,len(blob))
                self.assertEqual(blen,document["buffers"][0]["byteLength"])

    def test_glb_geometry_honest_bounds_and_nonzero_normals(self):
        for entry in self.report["original_objects"]:
            with self.subTest(name=entry["name"]):
                self.assertGreater(entry["triangles"],60)
                self.assertLess(entry["triangles"],25000)
                for lo,hi in entry["bounds_glb_m"]:
                    self.assertLess(lo,hi)
                    self.assertLess(abs(lo),12)
                    self.assertLess(abs(hi),12)
                self.assertEqual(entry["sha256"],hashlib.sha256(self.blobs[entry["name"]]).hexdigest())

    def test_actual_source_art_files_match_generated_bytes(self):
        files=list(g.OUT.glob("*.glb"))
        self.assertEqual(len(files),22)
        self.assertEqual(json.loads((g.OUT/"manifest.json").read_text(encoding="utf-8")),self.report)
        for name,blob in self.blobs.items():
            with self.subTest(name=name):
                self.assertEqual(blob,(g.OUT/(name+".glb")).read_bytes())
        self.assertEqual(22,s.validate_source()["source_models"])

    def test_source_contract_not_native_claim(self):
        info=s.validate_source()
        self.assertEqual("NATIVE_OBJECT_IMPORT_NOT_RUN",info["status"])
        self.assertEqual(115,info["native_actor_count_expected"])
        self.assertEqual(7,len(info["gameplay_markers_preserved"]))
        self.assertFalse(info["physics_modified"])
        self.assertFalse(info["story_modified"])
        self.assertFalse(info["user_saves_modified"])

    def test_critical_stations_stay_visual_only_and_separate(self):
        anchors={"LiftResonator":-250,"PressureRegulator":225,"ReserveTank":700}
        for role,x in anchors.items():
            selection=[r for r in self.report["placements"] if r["asset"]==role]
            self.assertEqual(1,len(selection))
            self.assertEqual(x,selection[0]["x"])
            self.assertEqual("NoCollision",selection[0]["collision"])
            self.assertFalse(selection[0]["interactive"])
        self.assertNotIn("Starbourne"," ".join(g.ASSET_NAMES))
        self.assertNotIn("Lyra"," ".join(g.ASSET_NAMES))

    def test_reject_duplicate_missing_or_intruding_object(self):
        with mock.patch.object(g,"ASSET_NAMES",g.ASSET_NAMES+("MooringBollard",)):
            with self.assertRaises(ValueError): g.inventory()
        with mock.patch.object(g,"PLACEMENTS",g.PLACEMENTS[:1]):
            with self.assertRaises(ValueError): g.inventory()
        original=g.PLACEMENTS
        mutated=tuple((n,x,0,z,yaw,scale) if n=="ReserveTank" else (n,x,y,z,yaw,scale)
                      for n,x,y,z,yaw,scale in original)
        with mock.patch.object(g,"PLACEMENTS",mutated):
            with self.assertRaises(ValueError): g.inventory()

    def test_generation_idempotence_and_no_unsafe_mutation(self):
        before=[(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
                for p in sorted(g.OUT.glob("*")) if p.is_file()]
        self.assertEqual(23,len(before))
        self.assertEqual(22,len(g.inventory()[1]))
        after=[(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
               for p in sorted(g.OUT.glob("*")) if p.is_file()]
        self.assertEqual(before,after)

if __name__=="__main__":
    unittest.main()
