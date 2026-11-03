"""Engine-free verification of the five noncanonical Aureate Wake V4 detail GLBs."""
from __future__ import annotations
import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "ArtSource" / "ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_cinematic_v4 as v4
from audit_aureate_v2_glb_geometry import parse_glb, accessor_values


class AureateCinematicV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=v4.payloads()

    def test_five_distinct_deterministic_reusable_glbs(self):
        self.assertEqual(set(self.outputs),set(v4.FILES))
        self.assertEqual(self.outputs,v4.payloads())
        self.assertEqual(len({hashlib.sha256(b).digest() for b in self.outputs.values()}),5)
        self.assertTrue(all(len(p)>10000 for p in self.outputs.values()))

    def test_canonical_names_and_one_vessel_with_four_existing_wings(self):
        r=v4.receipt(self.outputs)
        self.assertEqual(r["canonical_form_names"],
                         ["Skybourne","Seabourne","Submersible","Starbourne"])
        p=r["attachment_plan_review_only"]
        self.assertEqual(p[v4.CORE]["instances"],1)
        self.assertEqual(p[v4.SKY]["instances"],4)
        self.assertEqual(p[v4.SEA]["instances"],2)
        self.assertEqual(p[v4.SUB]["instances"],1)
        self.assertEqual(p[v4.STAR]["instances"],4)
        self.assertEqual(p[v4.STAR]["kind"],"static_developer_study_only")
        self.assertEqual(p[v4.CORE]["states"],list(v4.FORM_NAMES))
        self.assertFalse(r["starbourne_gameplay_unlocked"])
        self.assertFalse(r["form_enum_or_save_schema_changed"])

    def test_complete_glb_positions_normals_uv_triangles_and_section_count(self):
        counts={}
        for name,blob in self.outputs.items():
            with self.subTest(asset=name):
                gltf,raw=parse_glb(blob)
                self.assertEqual(gltf["asset"]["version"],"2.0")
                self.assertEqual(gltf["extras"]["authority"],"NONCANONICAL_REVIEW_NOT_ART_ACCEPTED")
                self.assertEqual(gltf["extras"]["sourceToGltfScale"],.01)
                self.assertEqual(gltf["extras"]["axisRemap"],"UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP")
                self.assertEqual(len(gltf["materials"]),4)
                prims=gltf["meshes"][0]["primitives"]
                self.assertEqual(len(prims),4)
                all_triangles=0
                for ix,prim in enumerate(prims):
                    self.assertEqual(prim["material"],ix)
                    attrs=prim["attributes"]
                    pos,_=accessor_values(gltf,raw,attrs["POSITION"],width=3,ctype=5126,target=34962)
                    norms,_=accessor_values(gltf,raw,attrs["NORMAL"],width=3,ctype=5126,target=34962)
                    uv,_=accessor_values(gltf,raw,attrs["TEXCOORD_0"],width=2,ctype=5126,target=34962)
                    indices,_=accessor_values(gltf,raw,prim["indices"],width=1,ctype=5125,target=34963)
                    self.assertEqual(len(pos),len(norms))
                    self.assertEqual(len(pos),len(uv))
                    self.assertEqual(len(indices)%3,0)
                    self.assertGreater(len(indices),0)
                    for (a,),(b,),(c,) in zip(indices[::3],indices[1::3],indices[2::3]):
                        self.assertLess(max(a,b,c),len(pos))
                        self.assertEqual(len({a,b,c}),3)
                        p,q,r=pos[a],pos[b],pos[c]
                        u,v,w=uv[a],uv[b],uv[c]
                        vec1=tuple(q[k]-p[k] for k in range(3))
                        vec2=tuple(r[k]-p[k] for k in range(3))
                        cross=(vec1[1]*vec2[2]-vec1[2]*vec2[1],
                               vec1[2]*vec2[0]-vec1[0]*vec2[2],
                               vec1[0]*vec2[1]-vec1[1]*vec2[0])
                        self.assertGreater(sum(k*k for k in cross),1e-16)
                        self.assertGreater(abs((v[0]-u[0])*(w[1]-u[1])-
                                               (v[1]-u[1])*(w[0]-u[0])),1e-11)
                        for k in (a,b,c):
                            self.assertTrue(all(math.isfinite(x) for x in pos[k]+norms[k]+uv[k]))
                    all_triangles+=len(indices)//3
                counts[name]=all_triangles
        self.assertTrue(all(n>100 for n in counts.values()),counts)

    def test_no_promoted_materials_or_artwork(self):
        for blob in self.outputs.values():
            doc,_=parse_glb(blob)
            for mat in doc["materials"]:
                self.assertIn("NONCANONICAL_REVIEW",mat["name"])
                self.assertTrue(mat["doubleSided"])
        r=v4.receipt(self.outputs)
        self.assertEqual(r["original_approved_image_sha256"],v4.APPROVED_ART_SHA)
        self.assertFalse(r["creator_model_approved"])
        self.assertFalse(r["production_content_changed"])
        self.assertEqual(r["native_unreal_import"],"NOT_VERIFIED")
        self.assertEqual(r["native_unreal_render"],"NOT_VERIFIED")

    def test_build_verify_and_reject_changed_file(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            built=v4.build_or_verify(folder,True)
            self.assertEqual(v4.build_or_verify(folder,False),built)
            obj=folder/v4.SKY
            original=obj.read_bytes()
            obj.write_bytes(original[:-1]+bytes([original[-1]^1]))
            with self.assertRaisesRegex(ValueError,"Refusing to overwrite"):
                v4.build_or_verify(folder,True)

    def test_refuse_unrelated_files(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            (folder/"important.txt").write_text("do not overwrite")
            with self.assertRaisesRegex(ValueError,"Refusing occupied folder"):
                v4.build_or_verify(folder,True)
            self.assertEqual((folder/"important.txt").read_text(),"do not overwrite")

    def test_no_unreal_or_ship_runtime_invocations(self):
        source=(ART/"build_aureate_cinematic_v4.py").read_text(encoding="utf-8")
        for forbidden in ("import unreal", "request_form(", "RequestForm(",
                          "unreal.Editor", "load_level(", "save_current_level("):
            self.assertNotIn(forbidden,source)

    def test_starbourne_single_motif_reused_in_four_equal_sail_slots(self):
        slots=v4.receipt(self.outputs)["attachment_plan_review_only"][v4.STAR]
        self.assertEqual(slots["instances"],4)
        self.assertTrue(slots["requires_story_unlock"])
        self.assertEqual(slots["states"],["Starbourne"])
        self.assertEqual(slots["kind"],"static_developer_study_only")


if __name__=="__main__":
    unittest.main()
