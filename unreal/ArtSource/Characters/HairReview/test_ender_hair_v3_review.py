"""Source-only regression of offline V2/V3 diagnostic and future native intake.

Tests bind an actual source-mesh PNG to immutable GLBs; they NEVER assert
Unreal runtime, character fit, hairstyle quality or creator approval.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import unittest
import zlib

HERE=Path(__file__).resolve().parent
CAPTURE=HERE/"ReviewCaptures/2026-11-15/EnderHair_V2_vs_V3_OFFLINE_SOURCE_MESH_SHEET.png"
EXPECTED_PNG="422dacd7c26741865588aa72d71a0db775be9650542a2868779b54851889c387"
CAPTURE_SCRIPT=HERE/"render_ender_hair_v2_v3_offline_20261115.py"
IMPORT_SCRIPT=HERE/"native_import_ender_hair_v3_20261115.py"


def audit_png(data):
    if data[:8]!=b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG signature invalid")
    pos=8
    chunks=[]
    width=height=0
    idat=0
    while pos<len(data):
        if pos+12>len(data):
            raise ValueError("incomplete PNG chunk")
        n=int.from_bytes(data[pos:pos+4],"big")
        name=data[pos+4:pos+8]
        end=pos+12+n
        if n>len(data) or end>len(data):
            raise ValueError("PNG bounds")
        payload=data[pos+8:pos+8+n]
        crc=int.from_bytes(data[pos+8+n:end],"big")
        if zlib.crc32(name+payload)&0xffffffff != crc:
            raise ValueError("PNG CRC mismatch")
        chunks.append(name)
        if name==b"IHDR":
            width,height=struct.unpack_from(">II",payload)
        if name==b"IDAT":
            idat+=len(payload)
        pos=end
        if name==b"IEND":
            break
    if pos!=len(data) or chunks[0]!=b"IHDR" or chunks[-1]!=b"IEND":
        raise ValueError("PNG framing")
    if width!=1920 or height!=1064 or idat<4096:
        raise ValueError("Expected nonempty eight-panel screenshot contract")
    return width,height


class EnderV3OfflineImageAndImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.png=CAPTURE.read_bytes()

    def test_real_eight_panel_cpu_png_integrity(self):
        self.assertEqual(hashlib.sha256(self.png).hexdigest(),EXPECTED_PNG)
        self.assertEqual(audit_png(self.png),(1920,1064))

    def test_png_tampering_fails(self):
        mutated=bytearray(self.png)
        mutated[len(mutated)//2]^=1
        with self.assertRaisesRegex(ValueError,"CRC"):
            audit_png(mutated)

    def test_preview_labels_are_explicitly_not_native_or_approved(self):
        s=CAPTURE_SCRIPT.read_text(encoding="utf-8")
        for line in ("NOT UNREAL", "NOT AN ART APPROVAL",
                     "source_meshes_modified", "source_v2_sha256", "source_v3_sha256",
                     "V2 TUBULAR REJECTED", "V3 BROAD-LAYER STUDY"):
            self.assertIn(line,s)
        self.assertIn("OFFLINE_SOURCE_3D_PREVIEW_ONLY_NOT_UNREAL",s)
        self.assertIn("painter",s.lower())

    def test_native_import_requires_disposable_project_and_immutable_assets(self):
        s=IMPORT_SCRIPT.read_text(encoding="utf-8")
        for part in (
            "c:/mh5/castallsandbox",
            "5.8.4-",
            "C:\\TSTSS_EnderHairNativeV1_20261104",
            "bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e",
            "2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d",
            "025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a",
            "replace_existing", "False",
            "not RECEIPT.exists()",
            "len(meshes)==1",
            "len(mesh.get_editor_property(\"static_materials\"))==4",
            "native_render_verified",
            "orientation_verified=False",
            "V3_STATIC_IMPORT_PASS_ART_AND_ORIENTATION_HOLD",
        ):
            self.assertIn(part,s)

    def test_native_script_does_not_automatically_mark_art_approved(self):
        s=IMPORT_SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn('"creator_approved":True',s)
        self.assertNotIn('"gameplay_ready":True',s)
        self.assertIn('"original_approved_hair":False',s)
        self.assertIn('"genuine_native_screenshot":False',s)


if __name__=="__main__":
    unittest.main()
