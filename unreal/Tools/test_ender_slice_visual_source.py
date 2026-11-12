"""Negative and positive tests for the source-only Ender PIE visual contract."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import validate_ender_slice_visual as gate


class EnderSliceVisualSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(gate.MANIFEST.read_text(encoding="utf-8"))
        cls.header = gate.HEADER.read_text(encoding="utf-8")
        cls.source = gate.SOURCE.read_text(encoding="utf-8")

    def altered(self, key: str, subkey: str, value) -> dict:
        row = deepcopy(self.manifest)
        row[key][subkey] = value
        return row

    def test_current_manifest_and_pawn_source(self):
        gate.validate_contract(self.manifest)
        gate.validate_cpp_guards(self.header, self.source)

    def test_rejects_wrong_reference_image_hash(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "appearance_reference", "source_sha256", "0" * 64))

    def test_rejects_false_reference_image_attachment(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "appearance_reference", "source_binary_committed", True))

    def test_rejects_old_buzz_cut_reintroduction(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "authority", "hair", "Very short auburn buzz cut, old approved look"))

    def test_rejects_incorrect_enders_portrait_panel(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "appearance_reference", "source",
                "First panel from left, Ionia"))

    def test_rejects_conflated_image_and_mesh_approval(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "appearance_reference", "avatar_model_approved", True))

    def test_rejects_gameplay_canon_overwritten_by_visual_image(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered(
                "appearance_reference", "game_stats_and_job_redefined", True))

    def test_rejects_unapproved_default_mesh(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("visual_binding", "default_candidate_mesh",
                                                "/Game/TSTSS/Approved/Ender"))

    def test_rejects_early_lyra(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("authority", "playable_pre_splashdown",
                                                ["Ender", "Ionia", "Lyra"]))

    def test_rejects_future_party(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("authority", "unavailable_in_slice", []))

    def test_rejects_starbourne_unlock(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("authority", "starbourne", "UNLOCKED"))

    def test_rejects_unproven_animation_as_done(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("native_acceptance", "animation_deformation",
                                                "PASS"))

    def test_rejects_fake_creator_approval(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("native_acceptance", "creator_signoff", True))

    def test_rejects_hair_visible_by_default(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("visual_binding", "default_hair_visible", True))

    def test_rejects_hair_enabled_in_native_default(self):
        broken = self.header.replace("bShowEnderReviewHair = false", "bShowEnderReviewHair = true")
        with self.assertRaises(gate.ContractError):
            gate.validate_cpp_guards(broken, self.source)

    def test_rejects_absent_hair_attachment(self):
        broken = self.source.replace(
            "PreviewAttachment(EnderReviewHairComponent, EnderSliceReviewHair", "/* missing hair */")
        with self.assertRaises(gate.ContractError):
            gate.validate_cpp_guards(self.header, broken)

    def test_rejects_accessory_visibility_default(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("visual_binding",
                                                "default_staff_visible", True))

    def test_rejects_prod_world(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_contract(self.altered("visual_binding", "world_type",
                                                "PIE_AND_SHIPPING"))

    def test_rejects_pawn_world_guard_removed(self):
        with self.assertRaises(gate.ContractError):
            gate.validate_cpp_guards(self.header,
                                     self.source.replace(
                                         "World->WorldType != EWorldType::PIE",
                                         "World->WorldType == EWorldType::PIE"))

    def test_rejects_gameplay_side_effect_in_review_method(self):
        broken = self.source.replace(
            "Body->SetSkeletalMeshAsset(Candidate);",
            'Body->SetSkeletalMeshAsset(Candidate);\n    SaveFirstWake(TEXT("forbidden"));')
        with self.assertRaises(gate.ContractError):
            gate.validate_cpp_guards(self.header, broken)

    def test_rejects_missing_goggle_clearance_guard(self):
        broken = self.source.replace(
            "!Body->DoesSocketExist(Bone)", "false")
        with self.assertRaises(gate.ContractError):
            gate.validate_cpp_guards(self.header, broken)


if __name__ == "__main__":
    unittest.main()
