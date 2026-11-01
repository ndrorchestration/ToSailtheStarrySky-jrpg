"""Source-only integrity/adversarial tests for V3 optional visual details."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_detail_v3 as v3
import build_aureate_fidelity_v2 as v2
from audit_aureate_v2_glb_geometry import parse_glb,accessor_values,span_and_minmax_match,GeometryHold


class DetailV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads=v3.payloads()

    def test_two_distinct_deterministic_meshes(self):
        self.assertEqual(set(self.payloads),set(v3.FILES))
        self.assertEqual(self.payloads,v3.payloads())
        for payload in self.payloads.values():
            self.assertGreater(len(payload),30000)

    def test_four_material_sections_and_source_authority(self):
        for name,payload in self.payloads.items():
            with self.subTest(name=name):
                doc,bin_=parse_glb(payload)
                self.assertEqual(len(doc["materials"]),4)
                self.assertEqual(len(doc["meshes"][0]["primitives"]),4)
                self.assertEqual(doc["extras"]["authority"],
                                 "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED")
                self.assertEqual(doc["extras"]["sourceToGltfScale"],.01)
                self.assertEqual(doc["extras"]["axisRemap"],
                                 "UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP")
                self.assertTrue(all(m["name"].endswith("_REVIEW")
                                    for m in doc["materials"]))

    def test_actual_buffer_positions_and_triangle_geometry(self):
        for name,payload in self.payloads.items():
            doc,bin_=parse_glb(payload)
            total=0
            extrema=[[],[],[]]
            for n,prim in enumerate(doc["meshes"][0]["primitives"]):
                self.assertEqual(prim["material"],n)
                attrs=prim["attributes"]
                pos,meta=accessor_values(doc,bin_,attrs["POSITION"],width=3,ctype=5126,target=34962)
                normals,_=accessor_values(doc,bin_,attrs["NORMAL"],width=3,ctype=5126,target=34962)
                uv,_=accessor_values(doc,bin_,attrs["TEXCOORD_0"],width=2,ctype=5126,target=34962)
                idx,_=accessor_values(doc,bin_,prim["indices"],width=1,ctype=5125,target=34963)
                span_and_minmax_match(pos,meta)
                self.assertEqual(len(pos),len(normals))
                self.assertEqual(len(pos),len(uv))
                self.assertEqual(len(idx)%3,0)
                for (a,),(b,),(c,) in zip(idx[::3],idx[1::3],idx[2::3]):
                    self.assertLess(max(a,b,c),len(pos))
                    self.assertEqual(len({a,b,c}),3)
                    delta1=tuple(pos[b][i]-pos[a][i] for i in range(3))
                    delta2=tuple(pos[c][i]-pos[a][i] for i in range(3))
                    cross=(delta1[1]*delta2[2]-delta1[2]*delta2[1],
                           delta1[2]*delta2[0]-delta1[0]*delta2[2],
                           delta1[0]*delta2[1]-delta1[1]*delta2[0])
                    self.assertGreater(sum(t*t for t in cross),1e-16)
                    for vertex in (a,b,c):
                        self.assertAlmostEqual(math.sqrt(sum(t*t for t in normals[vertex])),1,places=3)
                    total+=1
                for axis in range(3):
                    extrema[axis].extend(row[axis] for row in pos)
            self.assertGreater(total,180)
            # Fairing +X is approximately 0.54m; cockpit spans ~1.7m.
            span=[max(c)-min(c) for c in extrema]
            if name==v3.FAIRING:
                self.assertTrue(.53<span[0]<.56)
                self.assertTrue(.40<span[1]<.52)
                self.assertTrue(.39<span[2]<.52)
            else:
                self.assertTrue(1.5<span[0]<1.8)
                self.assertTrue(.60<span[1]<1.1)
                self.assertTrue(.8<span[2]<1.1)

    def test_approved_reference_not_claimed_as_approved_model(self):
        r=v3.receipt(self.payloads)
        self.assertEqual(r["original_approved_image_sha256"],v3.ART_SHA)
        self.assertFalse(r["creator_model_approval"])
        self.assertTrue(r["requires_native_review"])
        self.assertFalse(r["orbiter_authorized"])
        self.assertFalse(r["gameplay_modified"])

    def test_old_v2_outputs_unchanged(self):
        before=v2.deterministic_payloads()
        _=v3.payloads()
        self.assertEqual(before,v2.deterministic_payloads())

    def test_build_verify_tamper_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)
            v3.build_or_verify(path,True)
            v3.build_or_verify(path,False)
            p=path/v3.FAIRING
            data=p.read_bytes();p.write_bytes(data[:-1]+bytes([data[-1]^1]))
            with self.assertRaisesRegex(ValueError,"replace changed"):
                v3.build_or_verify(path,True)

    def test_unknown_file_refused_even_on_build(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            (folder/"unrelated.txt").write_text("unknown")
            with self.assertRaisesRegex(ValueError,"Unexpected"):
                v3.build_or_verify(folder,True)

    def test_no_mutating_editor_or_mode_imports(self):
        src=(ART/"build_aureate_detail_v3.py").read_text(encoding="utf-8")
        for forbidden in ("import unreal","RequestForm(","save_map(","spawn_actor_from_class("):
            self.assertNotIn(forbidden,src)

if __name__=="__main__":unittest.main()
