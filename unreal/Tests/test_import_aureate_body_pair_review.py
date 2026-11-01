"""Fail-closed review intake checks for the Aureate Wake two-GLB pair.

Does not require Unreal; synthetic unreal modules verify refusal before import.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/"Tools"
sys.path.insert(0,str(TOOLS))
import author_aureate_body_pair as body
import import_aureate_body_pair_review as intake


class BodyPairIntake(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.pair,self.manifest=body.make_pair()
        for name,content in self.pair.items():
            (self.folder/name).write_bytes(content)
        self.save_receipt()

    def save_receipt(self):
        (self.folder/body.MANIFEST).write_text(
            json.dumps(self.manifest),encoding="utf-8")

    def test_valid_two_part_preflight_returns_review_only_receipts(self):
        result=intake.preflight(self.folder)
        self.assertEqual(set(result["parts"]),{body.HULL,body.BRIDGE})
        self.assertEqual(result["authority"],"NONCANONICAL_REVIEW_NOT_GAMEPLAY")
        for name in self.pair:
            self.assertEqual(result["parts"][name]["sha256"],
                hashlib.sha256(self.pair[name]).hexdigest())

    def test_missing_dome_rejected_before_any_intake(self):
        (self.folder/body.BRIDGE).unlink()
        with self.assertRaises((intake.BodyPairHold,FileNotFoundError)):
            intake.preflight(self.folder)

    def test_mutated_hull_bytes_fail_exact_receipt(self):
        p=self.folder/body.HULL
        v=bytearray(p.read_bytes())
        v[-4]^=1
        p.write_bytes(v)
        with self.assertRaisesRegex(intake.BodyPairHold,"hash"):
            intake.preflight(self.folder)

    def test_wrong_scale_not_accepted_if_attacker_updates_hash(self):
        # Create a structurally valid GLB with a tampered scale marker.
        p=self.folder/body.BRIDGE
        blob=p.read_bytes()
        needle=b'"sourceToGltfScale":0.01'
        self.assertIn(needle,blob)
        tampered=blob.replace(needle,b'"sourceToGltfScale":0.10')
        self.assertEqual(len(tampered),len(blob))
        p.write_bytes(tampered)
        self.manifest["sha256"][body.BRIDGE]=hashlib.sha256(tampered).hexdigest()
        self.save_receipt()
        with self.assertRaisesRegex(intake.BodyPairHold,"provenance"):
            intake.preflight(self.folder)

    def test_wrong_manifest_destinations_rejected(self):
        self.manifest["destinations"][body.HULL]="/Game/Production"
        self.save_receipt()
        with self.assertRaisesRegex(intake.BodyPairHold,"Manifest"):
            intake.preflight(self.folder)

    def test_occupied_second_destination_blocks_first_import(self):
        calls=[]
        class FakeLibrary:
            @staticmethod
            def does_directory_exist(path):
                calls.append(("exists",path))
                return True
            @staticmethod
            def list_assets(path,recursive=True,include_folder=False):
                calls.append(("list",path))
                return ["already-exists"] if path==body.DESTINATIONS[body.BRIDGE] else []
        def new_task():
            calls.append(("TASK_CREATED",None))
            raise AssertionError("No task may be created if any destination is occupied")
        fake=types.SimpleNamespace(
            EditorAssetLibrary=FakeLibrary,
            AssetImportTask=new_task,
            AssetToolsHelpers=object(),
            StaticMesh=object(),
            load_asset=lambda path:None
        )
        with patch.dict(sys.modules,{"unreal":fake}):
            with self.assertRaisesRegex(intake.BodyPairHold,"occupied"):
                intake.import_review(self.folder,intake.preflight(self.folder))
        self.assertFalse(any(name=="TASK_CREATED" for name,_ in calls))

    def test_invalid_and_empty_glb_rejected(self):
        for blob in (b"",b"glTF",self.pair[body.HULL][:-4]):
            with self.subTest(size=len(blob)):
                with self.assertRaises(intake.BodyPairHold):
                    intake.inspect_glb(blob,body.HULL)

    def test_cli_check_mode_never_writes_assets(self):
        before=sorted((p.name,hashlib.sha256(p.read_bytes()).hexdigest())
                      for p in self.folder.iterdir())
        intake.main(["--source-dir",str(self.folder),"--check"])
        after=sorted((p.name,hashlib.sha256(p.read_bytes()).hexdigest())
                     for p in self.folder.iterdir())
        self.assertEqual(before,after)


if __name__=="__main__":
    unittest.main()
