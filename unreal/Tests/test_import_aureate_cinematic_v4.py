"""Pure offline contract tests of the guarded Unreal V4 detail import path."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
sys.path.insert(0,str(ROOT/"ArtSource"/"ShipReview"))
import build_aureate_cinematic_v4 as author
import import_aureate_cinematic_v4_review as importer


class CinematicV4ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest=Path(self.tmp.name)
        author.build_or_verify(self.dest,True)

    def test_valid_five_meshes_preflight(self):
        receipt=importer.preflight(self.dest)
        self.assertEqual(receipt["asset_count"],5)
        self.assertEqual(set(receipt["sha256"]),set(author.FILES))
        self.assertTrue(receipt["starbourne_locked"])
        self.assertEqual(receipt["candidate_folder"],author.REVIEW_ROOT)

    def test_reject_tampered_glb(self):
        asset=self.dest/author.STAR
        original=asset.read_bytes()
        asset.write_bytes(original[:-1]+bytes([original[-1]^1]))
        with self.assertRaisesRegex(importer.CinematicV4Hold,"SHA-256"):
            importer.preflight(self.dest)

    def test_reject_fake_starbourne_unlock(self):
        doc=self.dest/author.MANIFEST
        data=json.loads(doc.read_text())
        data["starbourne_gameplay_unlocked"]=True
        doc.write_text(json.dumps(data))
        with self.assertRaisesRegex(importer.CinematicV4Hold,"starbourne_gameplay_unlocked"):
            importer.preflight(self.dest)

    def test_reject_fake_native_proof(self):
        doc=self.dest/author.MANIFEST
        data=json.loads(doc.read_text())
        data["native_unreal_import"]="SUCCESS"
        doc.write_text(json.dumps(data))
        with self.assertRaisesRegex(importer.CinematicV4Hold,"native_unreal_import"):
            importer.preflight(self.dest)

    def test_reject_extra_unexpected_files(self):
        (self.dest/"unknown.uasset").write_bytes(b"keep")
        with self.assertRaisesRegex(importer.CinematicV4Hold,"Unexpected"):
            importer.preflight(self.dest)

    def test_import_gate_confines_unreal_project(self):
        source=(ROOT/"Tools"/"import_aureate_cinematic_v4_review.py").read_text()
        self.assertIn('project_dir.name!="AureateCinematicV4Sandbox"',source)
        self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",source)
        self.assertIn('replace_existing",False',source)
        self.assertIn('"scene_saved":False',source)
        self.assertIn('"actor_changed":False',source)
        self.assertNotIn("request_form(",source)
        self.assertNotIn("save_current_level(",source)


if __name__=="__main__":unittest.main()
