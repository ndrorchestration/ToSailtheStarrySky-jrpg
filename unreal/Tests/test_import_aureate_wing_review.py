"""Checks corrected wing import readiness; no UE runtime or game writes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / 'Tools' / 'author_aureate_wing_glb.py'
IMPORTER = ROOT / 'Tools' / 'import_aureate_wing_review.py'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

wing = load('wing_generator_import_test', GENERATOR)
review = load('wing_import_review_test', IMPORTER)

class WingImportReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glb, cls.png, cls.manifest = wing.build()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.glb_file = self.dir / review.FILENAME
        self.manifest_file = self.dir / 'AureateWake_Wing_Manifest.json'
        self.glb_file.write_bytes(self.glb)
        self.manifest_file.write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_corrected_file_is_accepted_for_review_only(self):
        info=review.preflight(self.glb_file,self.manifest_file)
        self.assertEqual(info['membrane_span_cm'],280)
        self.assertEqual(info['material_sections'],3)
        self.assertEqual(info['authority'],'REVIEW_ONLY_NOT_GAMEPLAY')

    def test_legacy_scale_claim_is_rejected(self):
        manifest=json.loads(self.manifest_file.read_text())
        manifest['source_to_gltf_scale']=1.0
        self.manifest_file.write_text(json.dumps(manifest))
        with self.assertRaises(review.WingReviewHold):
            review.preflight(self.glb_file,self.manifest_file)

    def test_glb_is_bound_to_exact_sha256(self):
        data=self.glb_file.read_bytes()
        self.glb_file.write_bytes(data[:-1]+b'X')
        with self.assertRaises(review.WingReviewHold):
            review.preflight(self.glb_file,self.manifest_file)

    def test_mismatched_material_metadata_is_rejected(self):
        manifest=json.loads(self.manifest_file.read_text())
        manifest['status']='CREATOR_APPROVED'
        self.manifest_file.write_text(json.dumps(manifest))
        with self.assertRaises(review.WingReviewHold):
            review.preflight(self.glb_file,self.manifest_file)

    def test_existing_ue_assets_prevent_import(self):
        info=review.preflight(self.glb_file,self.manifest_file)
        class FakeLibrary:
            @staticmethod
            def does_directory_exist(path):return True
            @staticmethod
            def list_assets(path,recursive=True,include_folder=False):return ['/Game/existing']
        class FakeAssetTools:
            @staticmethod
            def get_asset_tools():raise AssertionError('should never reach asset tools')
        old=sys.modules.get('unreal')
        sys.modules['unreal']=types.SimpleNamespace(EditorAssetLibrary=FakeLibrary, AssetToolsHelpers=FakeAssetTools)
        try:
            with self.assertRaises(review.WingReviewHold):review.import_review(self.glb_file,info)
        finally:
            if old is None:sys.modules.pop('unreal',None)
            else:sys.modules['unreal']=old

    def test_native_import_cannot_run_offline(self):
        if 'unreal' in sys.modules:self.skipTest('Real Unreal module present')
        info=review.preflight(self.glb_file,self.manifest_file)
        with self.assertRaises(review.WingReviewHold):review.import_review(self.glb_file,info)

    def test_import_script_never_recruits_or_unlocks(self):
        source=IMPORTER.read_text(encoding='utf-8')
        for prohibited in ('SeaContact(', 'FlotationConfirmed(', 'RequestForm(', 'bAllowOrbiterPreview = True'):
            self.assertNotIn(prohibited,source)

if __name__=='__main__':unittest.main()