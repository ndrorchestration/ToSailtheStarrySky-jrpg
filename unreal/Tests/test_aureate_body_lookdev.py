"""Source-only regression tests for strict two-part ship body lookdev intake.

These tests do not establish Unreal import or visual approval.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]/'ArtSource'/'ShipReview'
sys.path.insert(0,str(ROOT))
import build_aureate_body_review as build
import import_aureate_body_review as intake


class BodyGeometryTests(unittest.TestCase):
    def test_deterministic_regeneration(self):
        first=build.build_payloads();second=build.build_payloads()
        self.assertEqual(first,second)
        self.assertEqual(set(first),set(build.NAMES))
        self.assertTrue(all(20000<len(blob)<1_000_000 for blob in first.values()))

    def test_two_separate_named_objects_and_three_materials(self):
        for name,blob in build.build_payloads().items():
            import struct
            jlen=struct.unpack_from('<I',blob,12)[0]
            doc=json.loads(blob[20:20+jlen])
            self.assertEqual(doc['extras']['authority'],build.STATUS)
            self.assertEqual(doc['extras']['sourceToGltfScale'],.01)
            self.assertEqual(doc['extras']['axisRemap'],'UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP')
            self.assertEqual(len(doc['meshes']),1)
            self.assertEqual(len(doc['meshes'][0]['primitives']),3)
            self.assertEqual(len(doc['materials']),3)
            for p in doc['meshes'][0]['primitives']:
                self.assertGreater(doc['accessors'][p['indices']]['count'],0)
            if 'Bridge' in name:self.assertEqual(doc['materials'][0]['alphaMode'],'BLEND')

    def test_hull_stays_within_wing_root_envelope(self):
        s=build.hull()
        # Model was authored in cm, ship-forward +X, and four struts opt in separately.
        coords=[p for surf in s for p in surf.pos]
        self.assertLess(min(p[0] for p in coords),-3.95)
        self.assertGreater(max(p[0] for p in coords),3.95)
        self.assertLess(max(p[2] for p in coords),1.11)
        self.assertGreater(min(p[2] for p in coords),-1.11)
        self.assertGreater(len(s[0].indices)//3,100)

    def test_hemisphere_has_glass_panels_and_geodesic_frame(self):
        s=build.bridge_dome()
        self.assertGreater(len(s[0].indices)//3,140)
        self.assertGreater(len(s[1].indices)//3,1000)
        self.assertTrue(all(len(p)==3 for surf in s for p in surf.pos))

    def test_manifest_matches_two_generated_files(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            build.main(['--build','--output-dir',d])
            receipt=intake.preflight(folder)
            self.assertEqual(len(receipt['verified']),2)
            self.assertEqual(receipt['native_import'],'NOT_ESTABLISHED')
            self.assertFalse(receipt['orbiter_authorized'])
            build.main(['--verify','--output-dir',d])
            build.main(['--build','--output-dir',d]) # does not overwrite identical assets

    def test_mutated_glb_rejected_by_hash(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);build.main(['--build','--output-dir',d])
            path=folder/build.NAMES[0]
            blob=bytearray(path.read_bytes());blob[-5] ^= 1;path.write_bytes(blob)
            with self.assertRaisesRegex(intake.BodyReviewHold,'SHA mismatch'):intake.preflight(folder)
            with self.assertRaisesRegex(RuntimeError,'refusing overwrite'):build.main(['--build','--output-dir',d])

    def test_authority_or_up_axis_tamper_rejected(self):
        for edit in ('status','axis_remap','binding','orbiter_authorized','sha256'):
            with self.subTest(edit=edit),tempfile.TemporaryDirectory() as d:
                folder=Path(d);build.main(['--build','--output-dir',d]);path=folder/build.MANIFEST
                original=json.loads(path.read_text())
                original[edit]=({'unexpected':'unknown'} if edit=='sha256' else True)
                path.write_text(json.dumps(original))
                with self.assertRaises(intake.BodyReviewHold):intake.preflight(folder)

    def test_empty_or_outside_native_editor_import_rejected(self):
        with patch.dict(sys.modules,{'unreal':None}):
            with self.assertRaisesRegex(intake.BodyReviewHold,'Native Unreal Editor Python required'):
                intake.import_review(Path('.'),{})

    def test_no_automatic_binding_and_gameplay_authority(self):
        source=(ROOT/'import_aureate_body_review.py').read_text()
        self.assertNotIn('RequestForm(',source)
        self.assertNotIn('save_map(',source)
        self.assertNotIn('spawn_actor(',source)
        self.assertIn("'replace_existing',False",source)
        self.assertIn('refusing overwrite',source)
        for dest in intake.DESTINATIONS:
            self.assertTrue(dest.startswith('/Game/TSTSS/Review/'))


if __name__=='__main__':unittest.main()
