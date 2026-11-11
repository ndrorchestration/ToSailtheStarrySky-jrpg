"""Engine-free verification of content-addressed native shore review assets."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_first_wake_multipath_asset_snapshot as snapshot


class ShoreNativeAssetSnapshotTests(unittest.TestCase):
    def test_delivered_map_and_assets_are_immutable_review_only(self):
        result = snapshot.check()
        self.assertEqual(result["status"], "SOURCE_ASSET_HASHES_PASS_NOT_NATIVE_REVALIDATION")
        self.assertEqual(result["files"], 222)
        self.assertEqual(result["map_sha256"], snapshot.EXPECTED_MAP_HASH)
        data = json.loads(snapshot.MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["source_provenance_head"], snapshot.ORIGIN_HEAD)
        self.assertTrue(data["assets_are_review_only"])
        for field in ("pie_verified", "player_controls_verified", "gpu_render_verified",
                      "creator_visual_approved", "canon_authorized", "main_merge_authorized"):
            self.assertIs(data[field], False)

    def test_fake_art_approval_or_asset_digest_cannot_pass(self):
        original = json.loads(snapshot.MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp:
            forged = Path(temp) / "snapshot.json"
            for changes in (
                {"creator_visual_approved": True},
                {"pie_verified": True},
                {"native_files": 221},
                {"map_sha256": "0" * 64},
                {"content_tree_sha256": "0" * 64},
                {"delivered_candidate_head": snapshot.ORIGIN_HEAD},
            ):
                modified = dict(original)
                modified.update(changes)
                forged.write_text(json.dumps(modified), encoding="utf-8")
                with mock.patch.object(snapshot, "MANIFEST", forged):
                    with self.assertRaisesRegex(RuntimeError, "snapshot source/evidence/authority drift"):
                        snapshot.check()

    def test_modified_map_or_original_shore_is_rejected(self):
        native_checksum = snapshot.checksum

        def changed_map(path):
            if Path(path) in (snapshot.MAP, snapshot.ORIGINAL):
                return "0" * 64
            return native_checksum(path)

        with mock.patch.object(snapshot, "checksum", side_effect=changed_map):
            with self.assertRaisesRegex(RuntimeError, "map or canonical source-map hash mismatch"):
                snapshot.check()

    def test_snapshot_requires_new_path_and_no_overwrite(self):
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            snapshot.snapshot()


if __name__ == "__main__":
    unittest.main()
