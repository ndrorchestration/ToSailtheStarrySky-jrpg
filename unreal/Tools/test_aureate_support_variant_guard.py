"""Fail-closed provenance and isolation tests for noncanonical V2 support study."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_aureate_v2_crosslane_envelope import V2ReviewHold
import compare_aureate_v2_support_variant as comparison
import prepare_aureate_v2_support_variant as variant


class RootSupportVariantGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.base=root/"baseline";self.base.mkdir()
        self.cand=root/"experimental_support";self.cand.mkdir()
        self.report=root/"candidate_recipe_receipt.json"
        self.data={
            "authority":"NONCANONICAL_ROOT_SUPPORT_DIAGNOSTIC_DO_NOT_IMPORT_AS_ART",
            "base_v2_source_head":comparison.EXPECTED_V2_SOURCE_HEAD,
            "base_source_shas":copy.deepcopy(variant.BASE_SOURCE_SHA),
            "original_support_recipe":variant.BASE_SUPPORT_RECIPE,
            "experiment_support_recipe":variant.EXPERIMENTAL_SUPPORT_RECIPE,
            "approval":"NOT_GRANTED",
            "orbiter_authorized":False,
            "structural_mount_integrity":"UNVERIFIED",
            "original_mesh_sha256":{
                "hull":variant.BASELINE_HULL_SHA,
                "bridge":variant.BASELINE_BRIDGE_SHA},
            "candidate_mesh_sha256":{
                "hull":comparison.FROZEN_CANDIDATE_HULL_SHA,
                "bridge":variant.BASELINE_BRIDGE_SHA},
        }
        self.persist()

    def tearDown(self):
        self.tmp.cleanup()

    def persist(self):
        self.report.write_text(json.dumps(self.data),encoding="utf-8")

    def inspect(self):
        def digest_stub(path):
            return (
                comparison.FROZEN_CANDIDATE_HULL_SHA
                if path.parent == self.cand and path.name == variant.HULL_FILE
                else variant.BASELINE_HULL_SHA
                if path.name == variant.HULL_FILE
                else variant.BASELINE_BRIDGE_SHA
            )
        with patch.object(comparison, "sha",side_effect=digest_stub):
            return comparison.verify_candidate(self.report,self.cand,self.base)

    def test_exact_frozen_receipt_admitted_for_comparison_only(self):
        self.assertEqual(self.inspect()["approval"],"NOT_GRANTED")

    def test_creator_approval_claim_holds(self):
        self.data["approval"]="GRANTED"
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold,"approval/provenance"):
            self.inspect()

    def test_variant_cannot_authorize_orbiter(self):
        self.data["orbiter_authorized"]=True
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold,"approval/provenance"):
            self.inspect()

    def test_variant_does_not_accept_different_brass_recipe(self):
        self.data["experiment_support_recipe"]="trim.tube((0,0,0),(1,1,1),10)"
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold,"approval/provenance"):
            self.inspect()

    def test_candidate_sha_changed_and_manifest_rewritten_holds(self):
        self.data["candidate_mesh_sha256"]["hull"]="f"*64
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold,"model SHA"):
            self.inspect()

    def test_variant_rejects_changed_source_digest(self):
        self.data["base_source_shas"]["build_aureate_body_review.py"]="a"*64
        self.persist()
        with self.assertRaisesRegex(V2ReviewHold,"approval/provenance"):
            self.inspect()

    def test_power_shell_utf16le_receipt_with_bom_is_decoded(self):
        receipt=Path(self.tmp.name)/"powershell.json"
        receipt.write_bytes(("\ufeff"+json.dumps({"status":"HOLD"})).encode("utf-16-le"))
        self.assertEqual(comparison.read_verified_json_receipt(receipt)["status"],"HOLD")

    def test_utf8_receipt_is_decoded(self):
        self.assertEqual(comparison.read_verified_json_receipt(self.report)["approval"],
                         "NOT_GRANTED")

    def test_nonobject_baseline_json_is_refused(self):
        receipt=Path(self.tmp.name)/"not_object.json"
        receipt.write_text("[]",encoding="utf-8")
        with self.assertRaisesRegex(V2ReviewHold,"Expected JSON object"):
            comparison.read_verified_json_receipt(receipt)

    def test_variant_preparation_never_overwrites_output(self):
        with self.assertRaisesRegex(ValueError,"already exists"):
            variant.prepare(Path(self.tmp.name),Path(self.tmp.name))


if __name__=="__main__":
    unittest.main()
