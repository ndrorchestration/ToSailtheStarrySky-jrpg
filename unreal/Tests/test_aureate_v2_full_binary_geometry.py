"""Negative-case audits over actual generated GLB BIN buffers, not metadata only."""
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_fidelity_v2 as generator
from audit_aureate_v2_glb_geometry import GeometryHold,audit_binary,audit_folder,parse_glb

def binary_offset(payload, doc, accessor_number):
    jlen=struct.unpack_from("<I",payload,12)[0]
    a=doc["accessors"][accessor_number]
    view=doc["bufferViews"][a["bufferView"]]
    return 28+jlen+view.get("byteOffset",0)+a.get("byteOffset",0)

def edit_float(payload, attr, new_values, primitive=0):
    doc,_=parse_glb(payload)
    p=doc["meshes"][0]["primitives"][primitive]
    off=binary_offset(payload,doc,p["attributes"][attr])
    b=bytearray(payload)
    struct.pack_into("<"+"f"*len(new_values),b,off,*new_values)
    return bytes(b)

def edit_index(payload, index_position, value):
    doc,_=parse_glb(payload)
    p=doc["meshes"][0]["primitives"][0]
    off=binary_offset(payload,doc,p["indices"])+index_position*4
    b=bytearray(payload)
    struct.pack_into("<I",b,off,value)
    return bytes(b)

def repack(doc,bin_data):
    js=json.dumps(doc,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    js+=b" "*(-len(js)%4)
    binary=bytes(bin_data)
    return (struct.pack("<4sII",b"glTF",2,28+len(js)+len(binary))+
            struct.pack("<I4s",len(js),b"JSON")+js+
            struct.pack("<I4s",len(binary),b"BIN\0")+binary)

class FullBinaryGeometryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads=generator.deterministic_payloads()
        cls.name=generator.FILES[0]
        cls.body=cls.payloads[cls.name]

    def test_both_real_generated_binary_meshes_pass(self):
        for name,payload in self.payloads.items():
            with self.subTest(name=name):
                result=audit_binary(payload,expected_name=name)
                self.assertTrue(result["complete_binary_vertex_coverage"])
                self.assertGreater(result["triangle_count"],400)
                self.assertEqual(result["native_unreal_import"],"NOT_ESTABLISHED")
                self.assertFalse("approved" in result["native_unreal_import"].lower())

    def test_folder_audit_requires_exact_deterministic_manifest_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generator.write_or_verify(folder,True)
            result=audit_folder(folder)
            self.assertEqual(result["status"],"COMPLETE_GLTF_BUFFER_GEOMETRY_PASS_OFFLINE_ONLY")
            self.assertEqual(len(result["candidate_reports"]),2)
            self.assertFalse(result["orbiter_unlocked"])
            self.assertFalse(result["native_art_approved"])

    def test_forged_accessor_extrema_cannot_mask_actual_vertices(self):
        doc,bin_data=parse_glb(self.body)
        tamper=deepcopy(doc)
        idx=tamper["meshes"][0]["primitives"][0]["attributes"]["POSITION"]
        tamper["accessors"][idx]["max"][0]+=2
        with self.assertRaisesRegex(GeometryHold,"Claimed accessor bounds"):
            audit_binary(repack(tamper,bin_data),expected_name=self.name)

    def test_position_nan_rejected(self):
        mutated=edit_float(self.body,"POSITION",(float("nan"),))
        with self.assertRaisesRegex(GeometryHold,"Nonfinite"):
            audit_binary(mutated,expected_name=self.name)

    def test_normal_nan_rejected(self):
        mutated=edit_float(self.body,"NORMAL",(float("nan"),))
        with self.assertRaisesRegex(GeometryHold,"Nonfinite"):
            audit_binary(mutated,expected_name=self.name)

    def test_uv_nan_rejected(self):
        mutated=edit_float(self.body,"TEXCOORD_0",(float("nan"),))
        with self.assertRaisesRegex(GeometryHold,"Nonfinite"):
            audit_binary(mutated,expected_name=self.name)

    def test_tampered_actual_vertex_escapes_declared_extrema(self):
        mutated=edit_float(self.body,"POSITION",(30.,))
        with self.assertRaisesRegex(GeometryHold,"Claimed accessor bounds"):
            audit_binary(mutated,expected_name=self.name)

    def test_index_out_of_range_rejected(self):
        mutated=edit_index(self.body,0,999999)
        with self.assertRaisesRegex(GeometryHold,"Out-of-range"):
            audit_binary(mutated,expected_name=self.name)

    def test_triangle_duplicate_index_rejected(self):
        doc,_=parse_glb(self.body)
        p=doc["meshes"][0]["primitives"][0]
        offset=binary_offset(self.body,doc,p["indices"])
        first=struct.unpack_from("<I",self.body,offset)[0]
        mutated=edit_index(self.body,1,first)
        with self.assertRaisesRegex(GeometryHold,"repeated triangle index"):
            audit_binary(mutated,expected_name=self.name)

    def test_flipped_triangle_winding_rejected_by_normals(self):
        doc,_=parse_glb(self.body)
        p=doc["meshes"][0]["primitives"][0]
        off=binary_offset(self.body,doc,p["indices"])
        second,third=struct.unpack_from("<II",self.body,off+4)
        mutated=edit_index(edit_index(self.body,1,third),2,second)
        with self.assertRaisesRegex(GeometryHold,"winding/normal mismatch"):
            audit_binary(mutated,expected_name=self.name)

    def test_normal_sign_flip_rejected(self):
        doc,_=parse_glb(self.body)
        pos=doc["meshes"][0]["primitives"][0]["attributes"]["NORMAL"]
        off=binary_offset(self.body,doc,pos)
        n=struct.unpack_from("<3f",self.body,off)
        mutated=edit_float(self.body,"NORMAL",tuple(-v for v in n))
        with self.assertRaisesRegex(GeometryHold,"winding/normal mismatch"):
            audit_binary(mutated,expected_name=self.name)

    def test_non_identity_node_transform_rejected(self):
        doc,bin_data=parse_glb(self.body)
        modified=deepcopy(doc)
        modified["nodes"][0]["scale"]=[.01,.01,.01]
        with self.assertRaisesRegex(GeometryHold,"node transformation"):
            audit_binary(repack(modified,bin_data),expected_name=self.name)

    def test_corrupt_glb_file_length_rejected(self):
        with self.assertRaisesRegex(GeometryHold,"version/length"):
            audit_binary(self.body[:-4],expected_name=self.name)

    def test_wrong_asset_name_rejected(self):
        with self.assertRaisesRegex(GeometryHold,"Unrecognized"):
            audit_binary(self.body,expected_name="SomeOtherShip.glb")

if __name__=="__main__":
    unittest.main()
