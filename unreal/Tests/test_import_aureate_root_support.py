"""Review-only support GLB intake: checksums, dimensions, non-destructive import."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import author_aureate_root_support as author
import import_aureate_root_support_review as intake


class RootSupportReviewIntake(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="tstss-support-import-")
        self.dir=Path(self.temp.name)
        self.data,self.receipt=author.build()
        self.asset=self.dir/intake.FILENAME
        self.manifest=self.dir/"AureateWake_RootSupport_Manifest.json"
        self.asset.write_bytes(self.data)
        self.manifest.write_text(json.dumps(self.receipt),encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_review_candidate_is_not_authority(self):
        r=intake.preflight(self.asset,self.manifest)
        self.assertEqual(r["authority"],"REVIEW_ONLY_NOT_GAMEPLAY")
        self.assertEqual(r["strut_length_cm"],100.)
        self.assertEqual(r["material_sections"],3)
        self.assertIn("/Review/",r["destination"])

    def test_mutated_bytes_fail_sha256(self):
        b=bytearray(self.data)
        b[-1]^=1
        self.asset.write_bytes(b)
        with self.assertRaisesRegex(intake.SupportReviewHold,"SHA-256"):
            intake.preflight(self.asset,self.manifest)

    def test_legacy_centimeter_coordinates_are_rejected(self):
        self.receipt["source_to_gltf_scale"]=1.0
        self.manifest.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(intake.SupportReviewHold,"unit scale"):
            intake.preflight(self.asset,self.manifest)

    def test_unapproved_identity_is_rejected(self):
        self.receipt["status"]="CREATOR_APPROVED"
        self.manifest.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(intake.SupportReviewHold,"provenance"):
            intake.preflight(self.asset,self.manifest)

    def test_wrong_name_and_corrupt_header_rejected(self):
        other=self.dir/"WingSupport_Altered.glb"
        other.write_bytes(self.data)
        with self.assertRaisesRegex(intake.SupportReviewHold,"Expected one named"):
            intake.preflight(other,self.manifest)
        self.asset.write_bytes(b"not a GLB")
        self.receipt["sha256"][intake.FILENAME]=__import__("hashlib").sha256(b"not a GLB").hexdigest()
        self.manifest.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(intake.SupportReviewHold,"header"):
            intake.preflight(self.asset,self.manifest)

    def test_missing_emission_rejected_even_if_rehashed(self):
        jlen=struct.unpack_from("<I",self.data,12)[0]
        doc=json.loads(self.data[20:20+jlen])
        del doc["materials"][2]["emissiveFactor"]
        enc=json.dumps(doc,sort_keys=True,separators=(",",":")).encode()
        enc+=b" "*((-len(enc))%4)
        rest=self.data[20+jlen:]
        edited=(struct.pack("<4sII",b"glTF",2,12+8+len(enc)+len(rest))
                +struct.pack("<I4s",len(enc),b"JSON")+enc+rest)
        self.asset.write_bytes(edited)
        self.receipt["sha256"][intake.FILENAME]=__import__("hashlib").sha256(edited).hexdigest()
        self.manifest.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(intake.SupportReviewHold,"luminous"):
            intake.preflight(self.asset,self.manifest)

    def test_occupied_destination_does_not_invoke_asset_tools(self):
        called={"task":0}
        class Library:
            @staticmethod
            def does_directory_exist(p):return True
            @staticmethod
            def list_assets(*args,**kwargs):return [intake.REVIEW_FOLDER+"/ExistingCreatorMesh"]
        class Task:
            def __init__(self): called["task"]+=1
        fake=types.SimpleNamespace(EditorAssetLibrary=Library,AssetImportTask=Task,
                                   AssetToolsHelpers=object(),StaticMesh=object(),load_asset=lambda p:None)
        with patch.dict(sys.modules,{"unreal":fake}):
            with self.assertRaisesRegex(intake.SupportReviewHold,"overwrite"):
                intake.import_review(self.asset,intake.preflight(self.asset,self.manifest))
        self.assertEqual(called["task"],0)

    def test_not_unreal_does_not_import_or_edit_level(self):
        with patch.dict(sys.modules,{"unreal":None}):
            with self.assertRaisesRegex(intake.SupportReviewHold,"Unreal Editor Python"):
                intake.import_review(self.asset,intake.preflight(self.asset,self.manifest))
        source=(ROOT/"Tools/import_aureate_root_support_review.py").read_text()
        for forbidden in ("RequestForm(","SaveGame(","SeaContact(","spawn_actor_from_class","MoonBridgeUnlock"):
            self.assertNotIn(forbidden,source)

if __name__=="__main__":
    unittest.main()
