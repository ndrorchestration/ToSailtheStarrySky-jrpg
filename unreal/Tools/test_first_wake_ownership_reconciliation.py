"""Source-only, fail-closed checks for the First Wake four-lane ownership audit.

This does not test a live Unreal build, actual Pulse radius, imported sound,
PIE navigation, or native recruitment. It prevents those statuses being
silently promoted by a documentation/manifest edit.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

UE = Path(__file__).resolve().parents[1]
MANIFEST = UE / "DataSource/Integration/FirstWakeMultipath.review.json"
SPELLS = UE / "DataSource/Magic/EnderResonator.vertical_slice.review.json"
AUDIO = UE / "DataSource/Audio/FirstWakeSceneAudioBindings.review.json"
INPUT = UE / "Config/DefaultInput.ini"
PARTY = UE / "Source/ToSailTheStarrySky/Private/TSTSSPartySliceReviewEquipment.cpp"
COMBAT = UE / "Source/ToSailTheStarrySky/Private/TSTSSBattleSkillSystem.cpp"


def validate(manifest, spells, audio, input_text, party_cpp, combat_cpp):
    errors = []
    owners = manifest.get("source_ownership_audit_2026_11_13")
    if not isinstance(owners, dict):
        return ["four-lane source-ownership audit missing"]
    lanes = owners.get("single_owner_lanes", {})
    if set(lanes) != {
        "interactive_story_travel", "audio", "party_equipment", "resonator"
    }:
        errors.append("four distinct integration owners required")
        return errors
    if owners.get("combined_head_native_test_status") != "NOT_TESTED":
        errors.append("cannot inherit native test evidence from a different head")

    route = lanes["interactive_story_travel"]
    if (route.get("player_interact_action") != "Interact" or
        route.get("debug_scene_travel_action") != "ReviewShoreTravel" or
        route.get("debug_scene_travel_key") != "K" or
        '+ActionMappings=(ActionName="Interact",Key=E)' not in input_text or
        '+ActionMappings=(ActionName="ReviewShoreTravel",Key=K)' not in input_text):
        errors.append("E/K input or route owner drift")
    if (route.get("observed_complete_route") is not False or
        route.get("k_only_travel_is_gameplay_acceptance") is not False):
        errors.append("K map travel cannot authorize player route acceptance")

    audio_owner = lanes["audio"]
    if (audio_owner.get("reviewed_join_pr") != 823 or
        audio_owner.get("source_donor_pr") != 804 or
        audio_owner.get("parallel_convergence_pr") != 813 or
        audio_owner.get("v5_audio_actors_placed") is not False or
        audio_owner.get("v5_audio_audible_in_pie") is not False or
        audio_owner.get("historical_music_cleared") is not False):
        errors.append("audio donor/owner or real playback evidence drift")
    if not audio.get("scenes") or any(
        scene.get("actors_placed") is not False or
        scene.get("native_playback_verified") is not False or
        scene.get("mix_approved") is not False
        for scene in audio["scenes"]
    ):
        errors.append("unplaced source audio scenes must remain unverified")

    party = lanes["party_equipment"]
    if (party.get("first_wake") != ["Ender", "Ionia"] or
        party.get("after_splashdown_before_recruitment") != ["Ender", "Ionia"] or
        party.get("after_explicit_recruitment") != ["Ender", "Ionia", "Lyra"] or
        party.get("unavailable") != ["Reson", "Aepex"] or
        party.get("lyra_runtime_recruitment_verified") is not False):
        errors.append("Lyra stage/party eligibility authority drift")
    if ("Stage == ETSTSSPartySliceReviewStage::LyraRecruited" not in party_cpp or
        "Stage != ETSTSSPartySliceReviewStage::AfterSplashdown" not in party_cpp or
        "Stage != ETSTSSPartySliceReviewStage::FirstWake" not in party_cpp):
        errors.append("three-stage equipment source guard missing")
    if (manifest.get("lyra_equipment_gate", {}).get("runtime_recruitment_verified") is not False):
        errors.append("fixture source cannot establish runtime Lyra recruitment")

    magic = lanes["resonator"]
    indexed = {row.get("SkillId"): row for row in spells}
    pulse, centering = indexed.get("Ender_ResonantPulse", {}), indexed.get("Ender_Centering", {})
    if (pulse.get("Target") != magic.get("observed_pulse_target") or
        magic.get("observed_pulse_target") != "Enemy" or
        "case ETSTSSBattleSkillTarget::Enemy:" not in combat_cpp or
        "case ETSTSSBattleSkillTarget::EnemyArea:" in combat_cpp):
        errors.append("Pulse hostile-faction targeting witness changed; re-audit")
    if (magic.get("creator_pulse_target") !=
            "POINT_BLANK_SPHERICAL_AOE_ENEMIES_ONLY" or
        magic.get("observed_pulse_action_model") != "SOURCE_ATOMIC_AOE_CANDIDATE" or
        magic.get("pulse_area_source_candidate") is not True or
        magic.get("pulse_radius_cm") != 600 or
        magic.get("pulse_source_head_native_verified") is not False or
        magic.get("pulse_spatial_positions_verified_in_game") is not False or
        magic.get("source_compatible_with_creator_pulse") is not False or
        magic.get("pulse_full_aoe_runtime_verified") is not False or
        magic.get("pulse_3d_spherical_vfx_approved") is not False):
        errors.append("Pulse is NOT an implemented or native-verified PBAoE")
    if (magic.get("centering_resource_cost") != 5 or
        magic.get("centering_defense_buff_percent") != 15 or
        magic.get("centering_rounds") != 3 or
        centering.get("ResourceCost") != 5 or
        centering.get("PhysicalDefenseBuffPercent") != 15 or
        centering.get("BuffDurationRounds") != 3):
        errors.append("Centering admitted balance contract drift")
    if magic.get("correspondence_spells_status") != "DESIGN_ONLY_ON_HOLD":
        errors.append("Correspondence is not slice-executable")

    if (manifest.get("merged_to_main") is not False or
        manifest.get("release_authorized") is not False or
        manifest.get("creator_approved") is not False or
        manifest.get("pie_verified") is not False):
        errors.append("bounded review source cannot assert production acceptance")
    return errors


def read_sources():
    return (
        json.loads(MANIFEST.read_text(encoding="utf-8")),
        json.loads(SPELLS.read_text(encoding="utf-8")),
        json.loads(AUDIO.read_text(encoding="utf-8")),
        INPUT.read_text(encoding="utf-8"),
        PARTY.read_text(encoding="utf-8"),
        COMBAT.read_text(encoding="utf-8"),
    )


class FirstWakeOwnerReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read_sources()

    def errors(self, which=None, value=None):
        args = list(copy.deepcopy(self.source))
        if which is not None:
            args[which] = value
        return validate(*args)

    def test_source_receipt_is_still_non_authorizing(self):
        self.assertEqual([], self.errors())

    def test_native_head_cannot_inherit_another_branch_receipt(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["combined_head_native_test_status"] = "PASS"
        self.assertTrue(any("native" in x for x in self.errors(0, doc)))

    def test_k_route_cannot_be_promoted(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "interactive_story_travel"]["k_only_travel_is_gameplay_acceptance"] = True
        self.assertTrue(any("route" in x for x in self.errors(0, doc)))

    def test_k_input_rebind_requires_reconciliation(self):
        ini = self.source[3].replace(
            '+ActionMappings=(ActionName="ReviewShoreTravel",Key=K)',
            '+ActionMappings=(ActionName="ReviewShoreTravel",Key=J)', 1)
        self.assertTrue(any("E/K" in x for x in self.errors(3, ini)))

    def test_unplaced_audio_cannot_be_marked_audible(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "audio"]["v5_audio_audible_in_pie"] = True
        self.assertTrue(any("audio" in x for x in self.errors(0, doc)))

    def test_scene_audio_placement_requires_native_evidence(self):
        scenes = copy.deepcopy(self.source[2])
        scenes["scenes"][0]["actors_placed"] = True
        self.assertTrue(any("audio scenes" in x for x in self.errors(2, scenes)))

    def test_splashdown_does_not_recruit_lyra(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "party_equipment"]["after_splashdown_before_recruitment"].append("Lyra")
        self.assertTrue(any("Lyra" in x for x in self.errors(0, doc)))

    def test_party_source_missing_recruit_gate_is_rejected(self):
        source = self.source[4].replace(
            "Stage == ETSTSSPartySliceReviewStage::LyraRecruited",
            "Stage == ETSTSSPartySliceReviewStage::AfterSplashdown")
        self.assertTrue(any("three-stage" in x for x in self.errors(4, source)))

    def test_pulse_single_target_cannot_be_claimed_area_damage(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "resonator"]["source_compatible_with_creator_pulse"] = True
        self.assertTrue(any("PBAoE" in x for x in self.errors(0, doc)))

    def test_pulse_data_change_requires_new_head_source_audit(self):
        rows = copy.deepcopy(self.source[1])
        next(r for r in rows if r["SkillId"] == "Ender_ResonantPulse")["Target"] = "EnemyArea"
        self.assertTrue(any("hostile-faction" in x for x in self.errors(1, rows)))

    def test_pulse_candidate_cannot_claim_native_radius_witness(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "resonator"]["pulse_source_head_native_verified"] = True
        self.assertTrue(any("PBAoE" in x for x in self.errors(0, doc)))

    def test_pulse_candidate_radius_drift_refused(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "resonator"]["pulse_radius_cm"] = 1200
        self.assertTrue(any("PBAoE" in x for x in self.errors(0, doc)))

    def test_centering_balance_cannot_change_in_status_only(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "resonator"]["centering_rounds"] = 2
        self.assertTrue(any("Centering" in x for x in self.errors(0, doc)))

    def test_correspondence_remains_design_only(self):
        doc = copy.deepcopy(self.source[0])
        doc["source_ownership_audit_2026_11_13"]["single_owner_lanes"][
            "resonator"]["correspondence_spells_status"] = "ReviewExecutable"
        self.assertTrue(any("Correspondence" in x for x in self.errors(0, doc)))


if __name__ == "__main__":
    unittest.main()
