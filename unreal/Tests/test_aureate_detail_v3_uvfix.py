"""UV tangent regression checks for isolated V3 repair, no Unreal runtime."""
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_detail_v3 as original
import build_aureate_detail_v3_uvfix as fix
from audit_aureate_v2_glb_geometry import parse_glb,accessor_values

ORIGINAL_WINDOWS_SHA={
    "AureateWake_RootFairing_V3_REVIEW.glb":"ce8d17d69b5742eb3ad8d91d259f123a5b5d9935c8f845bdccb3cf846f37cb6a",
    "AureateWake_BridgeInterior_V3_REVIEW.glb":"bfc97e0f32494059aad7e6e8e478f1512099922549cb80a5d8ee25833a0d3d76",
}

class NativeTangentUVFixTests(unittest.TestCase):
    def test_original_v3_glbs_remain_byte_identical(self):
        orig=original.payloads()
        observed={name:hashlib.sha256(blob).hexdigest() for name,blob in orig.items()}
        # The legacy V3 generator uses platform libm trigonometry. Its
        # Windows/Linux GLB bytes can differ even when geometry is equivalent.
        # Preserve the historical Windows receipt, without misusing it as a
        # purported cross-platform golden hash.
        if sys.platform=="win32":
            self.assertEqual(observed,ORIGINAL_WINDOWS_SHA)
        _=fix.payloads()
        self.assertEqual(orig,original.payloads())

    def test_all_source_vertices_normals_and_triangles_unchanged(self):
        for old,new in zip((original.fairing_surfaces(),original.interior_surfaces()),
                           (fix.surfaces()[fix.FILES[0]],fix.surfaces()[fix.FILES[1]])):
            self.assertEqual(len(old),len(new))
            for a,b in zip(old,new):
                self.assertEqual(a.pos,b.pos)
                self.assertEqual(a.normal,b.normal)
                self.assertEqual(a.indices,b.indices)
                self.assertEqual(a.name,b.name)

    def test_every_triangle_uv_basis_nondegenerate_and_consistent(self):
        for groups in fix.surfaces().values():
            for surface in groups:
                self.assertGreater(len(surface.indices),0)
                for i in range(0,len(surface.indices),3):
                    uvs=surface.uv[i:i+3]
                    self.assertEqual(len(uvs),3)
                    self.assertGreater(fix.uv_area(*uvs),1e-6)

    def test_generated_binary_uv_basis_is_non_degenerate(self):
        for name,payload in fix.payloads().items():
            with self.subTest(name=name):
                doc,blob=parse_glb(payload)
                self.assertEqual(len(doc["materials"]),4)
                for prim in doc["meshes"][0]["primitives"]:
                    attrs=prim["attributes"]
                    uv,_=accessor_values(doc,blob,attrs["TEXCOORD_0"],width=2,ctype=5126,target=34962)
                    indices,_=accessor_values(doc,blob,prim["indices"],width=1,ctype=5125,target=34963)
                    for (a,),(b,),(c,) in zip(indices[::3],indices[1::3],indices[2::3]):
                        self.assertGreater(fix.uv_area(uv[a],uv[b],uv[c]),1e-6)

    def test_provenance_and_strict_review_hold(self):
        m=fix.manifest(fix.payloads())
        self.assertEqual(m["origin_unchanged_v3_sha256"],{
            name:hashlib.sha256(blob).hexdigest()
            for name,blob in original.payloads().items()})
        self.assertEqual(m["original_creator_approved_image_sha256"],original.ART_SHA)
        self.assertEqual(m["native_import"],"NOT_VERIFIED")
        self.assertEqual(m["native_tangent_warning_fix"],"NOT_VERIFIED")
        self.assertFalse(m["creator_model_approval"])
        self.assertFalse(m["orbiter_authorized"])
        self.assertFalse(m["gameplay_modified"])

    def test_generation_is_deterministic(self):
        self.assertEqual(fix.payloads(),fix.payloads())
        self.assertNotEqual(*fix.FILES)

    def test_tampering_fails_closed_and_old_output_untouched(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            fix.build_or_verify(folder,True)
            fix.build_or_verify(folder,False)
            f=folder/fix.FILES[0];b=bytearray(f.read_bytes());b[-9]^=1;f.write_bytes(b)
            with self.assertRaisesRegex(fix.UVFixHold,"Refusing"):
                fix.build_or_verify(folder,True)

    def test_no_editor_mutation_and_no_production_binding(self):
        src=(ART/"build_aureate_detail_v3_uvfix.py").read_text(encoding="utf-8")
        for phrase in ("import unreal","save_map(","RequestForm(","spawn_actor_from_class("):
            self.assertNotIn(phrase,src)

if __name__=="__main__":unittest.main()
