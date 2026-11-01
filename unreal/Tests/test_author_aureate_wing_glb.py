"""Source and generated asset tests, no Unreal runtime required."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "Tools" / "author_aureate_wing_glb.py"
spec = importlib.util.spec_from_file_location("author_aureate_wing_glb", SOURCE)
wing = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wing
spec.loader.exec_module(wing)


def consistent_manifold(surface):
    edges={}
    for face in surface["faces"]:
        for a,b in ((face[0],face[1]),(face[1],face[2]),(face[2],face[0])):
            key=tuple(sorted((a,b)))
            edges.setdefault(key,[]).append((a,b))
    return (len(edges)>0 and all(len(v)==2 and v[0]==v[1][::-1] for v in edges.values()))


class WingArtPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glb,cls.png,cls.manifest=wing.build()

    def test_taper_and_scale_are_positive(self):
        self.assertEqual(wing.SPAN,280)
        self.assertEqual(wing.WIDTH,105)
        self.assertGreater(wing.half_width(.5),40)
        self.assertGreater(wing.half_width(.5),wing.half_width(0))

    def test_all_procedural_submeshes_have_consistent_closed_normals(self):
        for section in (wing.mesh_membrane(),wing.mesh_venation(),wing.mesh_hinge()):
            with self.subTest(section=section["name"]):
                self.assertTrue(consistent_manifold(section))
                self.assertGreater(len(section["faces"]),0)

    def test_glb_spec_and_buffer_lengths(self):
        data=self.glb
        magic,version,total=struct.unpack_from("<4sII",data)
        self.assertEqual((magic,version,total),(b"glTF",2,len(data)))
        json_len,json_kind=struct.unpack_from("<I4s",data,12)
        self.assertEqual(json_kind,b"JSON")
        doc=json.loads(data[20:20+json_len])
        binlen,kind=struct.unpack_from("<I4s",data,20+json_len)
        self.assertEqual(kind,b"BIN\0")
        self.assertLessEqual(doc["buffers"][0]["byteLength"],binlen)
        self.assertLessEqual(binlen-doc["buffers"][0]["byteLength"],3)
        self.assertEqual(20+json_len+8+binlen,len(data))
        self.assertEqual(len(doc["meshes"][0]["primitives"]),3)
        self.assertEqual(doc["scene"],0)
        for view in doc["bufferViews"]:
            self.assertEqual(view["byteOffset"]%4,0)
            self.assertLessEqual(view["byteOffset"]+view["byteLength"],binlen)

    def test_gltf_is_meter_scaled_while_normals_remain_unit_vectors(self):
        # glTF 2.0 specifies meters. Imported UE bounds should be 280cm,
        # not 280m, and surface normals must not be scaled with positions.
        data=self.glb
        jlen=struct.unpack_from("<I",data,12)[0]
        doc=json.loads(data[20:20+jlen])
        self.assertEqual(doc["extras"]["sourceToGltfScale"], .01)
        self.assertEqual(doc["extras"]["gltfLinearUnits"], "meters")
        pos_id=doc["meshes"][0]["primitives"][0]["attributes"]["POSITION"]
        bounds=doc["accessors"][pos_id]
        self.assertAlmostEqual(bounds["max"][0], 2.80, places=5)
        self.assertAlmostEqual(bounds["min"][0], 0, places=5)
        self.assertEqual(self.manifest["source_to_gltf_scale"], .01)
        normal_id=doc["meshes"][0]["primitives"][0]["attributes"]["NORMAL"]
        normal_accessor=doc["accessors"][normal_id]
        view=doc["bufferViews"][normal_accessor["bufferView"]]
        blob=data[20+jlen+8:]
        for i in (0, 1, 42, normal_accessor["count"]-1):
            xyz=struct.unpack_from("<fff",blob,view.get("byteOffset",0)+12*i)
            self.assertAlmostEqual(sum(v*v for v in xyz),1.0,places=4)
        self.assertGreater(len(self.glb), 10000)

    def test_material_and_embedded_image_contract(self):
        dlen=struct.unpack_from("<I",self.glb,12)[0]
        doc=json.loads(self.glb[20:20+dlen])
        self.assertEqual(len(doc["materials"]),3)
        self.assertEqual(doc["images"][0]["mimeType"],"image/png")
        self.assertEqual(doc["materials"][0]["alphaMode"],"BLEND")
        self.assertTrue(doc["materials"][0]["doubleSided"])
        self.assertIn("REVIEW",doc["materials"][0]["name"])
        self.assertEqual(doc["extras"]["authority"],wing.STATUS)

    def test_png_structure_dimensions_and_crc(self):
        img=self.png
        self.assertTrue(img.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(struct.unpack_from(">II",img,16),wing.PBR_SIZE)
        pos=8; types=[]
        while pos<len(img):
            size=struct.unpack_from(">I",img,pos)[0]
            kind=img[pos+4:pos+8]
            body=img[pos+8:pos+8+size]
            crc=struct.unpack_from(">I",img,pos+8+size)[0]
            import zlib
            self.assertEqual(crc,zlib.crc32(kind+body)&0xffffffff)
            types.append(kind)
            pos+=12+size
        self.assertEqual(types,[b"IHDR",b"IDAT",b"IEND"])
        self.assertEqual(pos,len(img))

    def test_manifest_binds_bytes_without_false_approval(self):
        self.assertEqual(self.manifest["sha256"][wing.OUTPUT_FILES[0]],hashlib.sha256(self.glb).hexdigest())
        self.assertEqual(self.manifest["sha256"][wing.OUTPUT_FILES[1]],hashlib.sha256(self.png).hexdigest())
        self.assertEqual(self.manifest["status"],"NONCANONICAL_REVIEW_NOT_ART_ACCEPTED")
        self.assertTrue(any("No native Unreal render" in x for x in self.manifest["limits"]))

    def test_repeatable_identical_asset_bytes(self):
        g,p,m=wing.build()
        self.assertEqual(self.glb,g)
        self.assertEqual(self.png,p)
        self.assertEqual(self.manifest,m)

    def test_non_destructive_export_and_no_early_story_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)/"review"
            d.mkdir()
            (d/"existing.txt").write_text("important",encoding="utf-8")
            import subprocess
            result=subprocess.run([sys.executable,str(SOURCE),"--output-dir",str(d)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual((d/"existing.txt").read_text(),"important")
        source=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("RequestForm(",source)
        self.assertNotIn("SeaContact",source)
        self.assertNotIn("FlotationConfirmed",source)
        self.assertNotIn("bAllowOrbiterPreview = true",source)

if __name__=="__main__":unittest.main()