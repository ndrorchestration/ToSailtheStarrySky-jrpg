"""Source-only negative tests for independent post-stage Unreal map readback."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_first_wake_multipath_shore as stage
import verify_first_wake_multipath_shore as auditor


class FirstWakeMultipathReadbackTests(unittest.TestCase):
    def test_source_plan_does_not_claim_ue_acceptance(self):
        data=auditor.source_plan()
        self.assertEqual("tstss.shore.independent-readback.v1",data["schema"])
        self.assertEqual(26,len(data["expected_labels"]))
        self.assertEqual(26,data["expected_additional_actor_count"])
        self.assertFalse(data["native_scene_loaded"])
        self.assertFalse(data["pie_verified"])
        self.assertFalse(data["visual_approved"])
        self.assertEqual(stage.DEST_MAP,data["destination_map"])

    def test_source_only_inspection_keeps_exact_review_categories(self):
        labels=auditor.expected_labels()
        self.assertEqual(1,sum("CoastalAtmosphere" in x for x in labels))
        self.assertEqual(8,sum("OriginalProp_" in x for x in labels))
        self.assertEqual(3,sum("StaticGear_NotEquipped_" in x for x in labels))
        self.assertEqual(3,sum("EnemyVisual_NoEncounter_" in x for x in labels))
        self.assertEqual(9,sum("NoAuthorizedCast_" in x for x in labels))
        self.assertTrue(all(x.startswith(stage.PREFIX) for x in labels))
        self.assertEqual("TSTSSSliceEnemyActor",
                         labels[stage.PREFIX+"EnemyVisual_NoEncounter_DockSkitter"])

    def test_missing_or_unsafe_head_denied_without_editor(self):
        for head in ("", "c"*39, "not-a-sha", "z"*40):
            with self.subTest(head=head):
                with self.assertRaisesRegex(RuntimeError,"full exact Git head"):
                    auditor.validate_native_receipt(head)

    def test_no_native_receipt_does_not_become_positive_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(auditor,"NATIVE_RECEIPT",Path(d)/"missing.json"), \
                 mock.patch.object(auditor,"DEST_FILE",Path(d)/"missing.umap"), \
                 mock.patch.object(auditor,"READBACK",Path(d)/"result.json"):
                with self.assertRaisesRegex(RuntimeError,"map/stage receipt absent"):
                    auditor.validate_native_receipt("a"*40)

    def test_false_native_stage_or_wrong_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            new_map=root/"scene.umap"
            new_map.write_bytes(b"fixture map never loaded in UE")
            receipt=root/"stage.json"
            head="a"*40
            valid={
                "status":"NATIVE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED",
                "source_head":head, "native_staged":True,
                "PIE_verified":False, "visual_approved":False,
                "new_map_sha256":auditor.sha256(new_map),
                "source_sha256":auditor.sha256(stage.MAP_FILE),
                "new_unique_review_actors":26,
                "removed_duplicate_only_environment_actors":list(stage.LEGACY_ENV_LABELS),
                "saved_actor_count":21-len(stage.LEGACY_ENV_LABELS)+26,
            }
            with mock.patch.object(auditor,"DEST_FILE",new_map), \
                 mock.patch.object(auditor,"NATIVE_RECEIPT",receipt), \
                 mock.patch.object(auditor,"READBACK",root/"result.json"):
                receipt.write_text(json.dumps(valid),encoding="utf-8")
                self.assertEqual(valid,auditor.validate_native_receipt(head))
                for key,bad in (("native_staged",False),
                                ("visual_approved",True),
                                ("source_head","f"*40),
                                ("status","APPROVED"),
                                ("PIE_verified",True)):
                    altered=dict(valid);altered[key]=bad
                    receipt.write_text(json.dumps(altered),encoding="utf-8")
                    with self.subTest(key=key):
                        with self.assertRaisesRegex(RuntimeError,"exact-head review-only"):
                            auditor.validate_native_receipt(head)
                modified=dict(valid);modified["new_map_sha256"]="0"*64
                receipt.write_text(json.dumps(modified),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"digest differs"):
                    auditor.validate_native_receipt(head)
                modified=dict(valid);modified["saved_actor_count"]=26
                receipt.write_text(json.dumps(modified),encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError,"count inconsistent"):
                    auditor.validate_native_receipt(head)

    def test_reviewer_code_is_independent_and_readonly(self):
        source=Path(auditor.__file__).read_text(encoding="utf-8")
        self.assertIn("load_map(stage.DEST_MAP)",source)
        self.assertIn("get_all_level_actors()",source)
        self.assertIn("get_actor_enable_collision()",source)
        self.assertIn("sha256(DEST_FILE)",source)
        self.assertIn("sha256(stage.MAP_FILE)",source)
        self.assertIn('READBACK.open("x"',source)
        self.assertNotIn("save_map(",source)
        self.assertNotIn("spawn_actor_from_class(",source)
        self.assertNotIn("duplicate_asset(",source)
        self.assertNotIn("SaveGameToSlot(",source)


if __name__=="__main__":
    unittest.main()
