"""Fail-closed source boundary checks for Ender's Resonant Pulse PBAoE candidate.

The checks inspect real edited C++/DataSource and include negative mutations;
they are NOT a UE compiler, PIE runtime, geometry/radius measurement or GPU test.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

UE = Path(__file__).resolve().parents[1]
ROOT = UE / "Source/ToSailTheStarrySky"
PATHS = {
    "magic": UE / "DataSource/Magic/EnderResonator.vertical_slice.review.json",
    "header": ROOT / "Public/TSTSSBattleSkillSystem.h",
    "executor": ROOT / "Private/TSTSSBattleSkillSystem.cpp",
    "manager_h": ROOT / "Public/Combat/TSS_CombatTurnManager.h",
    "manager": ROOT / "Private/Combat/TSS_CombatTurnManager.cpp",
    "review": ROOT / "Private/Review/TSTSSResonatorFocusReviewActor.cpp",
    "vfx": ROOT / "Private/TSTSSResonatorVfxActor.cpp",
    "native": ROOT / "Private/Tests/TSTSSResonatorVfxTests.cpp",
    "integration": UE / "DataSource/Integration/FirstWakeMultipath.review.json",
}


def validate(sources: dict) -> list[str]:
    errors = []
    magic = json.loads(sources["magic"])
    integration = json.loads(sources["integration"])
    rows = {r["SkillId"]: r for r in magic}
    pulse = rows.get("Ender_ResonantPulse", {})
    centering = rows.get("Ender_Centering", {})
    if not (
        pulse.get("Target") == "Enemy"
        and pulse.get("TargetShape") == "CasterCenteredSphere"
        and pulse.get("AreaRadiusCm") == 600
        and pulse.get("AffectedFaction") == "OpponentsOnly"
        and pulse.get("CastResolution") == "OneTransactionOneCostOneTurn"
        and pulse.get("ResourceCost") == 3
        and pulse.get("Power") == 6
        and pulse.get("Admission") == "ReviewExecutable"
    ):
        errors.append("Pulse must have one 3-MP 600cm enemy-only spherical source contract")
    if not (
        centering.get("Target") == "Self"
        and centering.get("ResourceCost") == 5
        and centering.get("PhysicalDefenseBuffPercent") == 15
        and centering.get("BuffDurationRounds") == 3
    ):
        errors.append("Centering existing combat balance must be preserved")

    header = sources["header"]
    executor = sources["executor"]
    if not (
        "ResonantPulseRadiusCm = 600.0" in header
        and "TryUseResonantPulseArea(" in header
        and "TryUseValidatedRow(" in header
        and "bool FTSTSSBattleSkillSystem::TryUseResonantPulseArea(" in executor
        and "Combat/TSTSSPulseAreaMath.h" in executor
        and "TSTSSPulseAreaMath::WithinSphere(" in executor
        and "ResonantPulseRadiusCm))" in executor
        and "*Side == OpponentFaction && Unit.Health > 0" in executor
        and "ParticipantWorldPositions.Num() != State.Combat.Roster.Num()" in executor
        and "Affected.IsEmpty()" in executor
        and "Affected.Sort(" in executor
    ):
        errors.append("caster-centered real 3D hostile-target spatial selection missing")

    if not (
        "SkillId == TEXT(\"Ender_ResonantPulse\")" in executor
        and "!bAuthorizedAreaPulse" in executor
        and "Row.Power != 6 || Row.ResourceCost != 3" in executor
        and "FTSTSSBattleSkillSystem::TryUseRow(" in executor
        and "Row, false, OutState, OutCue" in executor
        and "Row.SkillId, Row, true," in executor
        and "UTSTSSCombatRules::TryApplyAction(" in executor
        and "Extra.ResourceCost = 0" in executor
        and "Extra.bHealing = false" in executor
        and "OutAffectedEnemyIds = MoveTemp(Affected)" in executor
    ):
        errors.append("single-target Pulse bypass or per-cast transaction boundary missing")

    manager = sources["manager"]
    if not (
        "SubmitResonantPulseArea(" in sources["manager_h"]
        and "Command.SkillId == TEXT(\"Ender_ResonantPulse\")" in manager
        and "Command.TargetParticipantId != Command.SourceParticipantId" in manager
        and "FTSTSSBattleSkillSystem::TryUseResonantPulseArea(" in manager
        and "CommitAcceptedAction(MoveTemp(Candidate), CandidateCue)" in manager
        and manager.count("OnSkillAccepted.Broadcast(") == 1
    ):
        errors.append("single-event combat manager area-dispatch boundary missing")

    review = sources["review"]
    if not (
        "bool ATSTSSResonatorFocusReviewActor::TryCastResonantPulse()" in review
        and "GetCombatantSnapshot()" in review
        and "Positions.Add(Unit.CharacterId, EnderProxy->GetComponentLocation())" in review
        and "Positions.Add(Unit.CharacterId, FoeProxy->GetComponentLocation())" in review
        and "Command.TargetParticipantId = TEXT(\"Ender\")" in review
        and "SubmitResonantPulseArea(Command, Positions)" in review
    ):
        errors.append("focus PIE encounter must supply true proxy positions and caster anchor")

    vfx = sources["vfx"]
    if not (
        "if (Style == 0)" in vfx
        and "constexpr float GoldenAngle = 2.3999632297286533f" in vfx
        and "for (int32 Index = 0; Index < 72; ++Index)" in vfx
        and "Planar * FMath::Sin(Azimuth), H" in vfx
        and "const FVector Point = Unit * RadiusCm" in vfx
        and "FTSTSSBattleSkillSystem::ResonantPulseRadiusCm" in vfx
        and "return;" in vfx.split("if (Style == 0)", 1)[1].split("for (int32 Ring", 1)[0]
    ):
        errors.append("Pulse renderer must expand as volumetric spherical surface")

    native = sources["native"]
    for token in (
        "legacy single-target Pulse MUST NOT execute",
        "Pulse hits multiple foes from full 3D distance",
        "two enemies within radius hit",
        "Ionia inside radius takes no damage",
        "enemy just beyond 600cm 3D boundary unaffected",
        "missing enemy coordinate refuses entire cast",
        "no in-range enemies must not charge MP or skip a turn",
        "area spell insufficient MP fails atomically",
        "combat manager disallows legacy targeted Pulse",
        "manager routes admitted caster-centered Pulse area",
    ):
        if token not in native:
            errors.append("native mutation/positive regression missing: " + token)

    status = integration["source_ownership_audit_2026_11_13"]["single_owner_lanes"]["resonator"]
    if not (
        status.get("observed_pulse_action_model") == "SOURCE_ATOMIC_AOE_CANDIDATE"
        and status.get("pulse_area_source_candidate") is True
        and status.get("pulse_radius_cm") == 600
        and status.get("pulse_source_head_native_verified") is False
        and status.get("pulse_spatial_positions_verified_in_game") is False
        and status.get("pulse_3d_spherical_vfx_approved") is False
        and status.get("pulse_full_aoe_runtime_verified") is False
        and integration.get("merged_to_main") is False
        and integration.get("release_authorized") is False
    ):
        errors.append("source candidate cannot claim native, creator, or production status")
    return errors


class PulseSpatialSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {name: path.read_text(encoding="utf-8") for name, path in PATHS.items()}

    def fail_mutation(self, name, old, new, needle):
        files = dict(self.files)
        self.assertIn(old, files[name])
        files[name] = files[name].replace(old, new, 1)
        self.assertTrue(any(needle in e for e in validate(files)))

    def test_source_spatial_contract_complete(self):
        self.assertEqual([], validate(self.files))

    def test_radius_mismatch_rejected(self):
        self.fail_mutation("header", "ResonantPulseRadiusCm = 600.0",
                           "ResonantPulseRadiusCm = 1200.0", "spatial")

    def test_spell_ally_target_rejected(self):
        self.fail_mutation("magic", '"AffectedFaction": "OpponentsOnly"',
                           '"AffectedFaction": "Everyone"', "enemy-only")

    def test_single_enemy_bypass_rejected(self):
        self.fail_mutation("executor", "Row, false, OutState, OutCue",
                           "Row, true, OutState, OutCue", "transaction")

    def test_extra_enemy_mp_spend_rejected(self):
        self.fail_mutation("executor", "Extra.ResourceCost = 0",
                           "Extra.ResourceCost = 3", "transaction")

    def test_faction_drift_rejected(self):
        self.fail_mutation("executor", "*Side == OpponentFaction && Unit.Health > 0",
                           "*Side == PartyFaction && Unit.Health > 0", "spatial")

    def test_2d_radius_rejected(self):
        self.fail_mutation("executor", "TSTSSPulseAreaMath::WithinSphere(",
                           "TSTSSPulseAreaMath::WithinCylinder(", "spatial")

    def test_renderer_flattening_rejected(self):
        self.fail_mutation("vfx", "const FVector Point = Unit * RadiusCm",
                           "const FVector Point = FVector(Unit.X,Unit.Y,0) * RadiusCm", "spherical")

    def test_ally_inside_radius_native_test_required(self):
        self.fail_mutation("native", "Ionia inside radius takes no damage",
                           "Ionia receives aura damage", "native mutation")

    def test_managed_cue_single_event_required(self):
        self.fail_mutation("manager", "OnSkillAccepted.Broadcast(",
                           "OnSkillAccepted.Broadcast(\n    OnSkillAccepted.Broadcast(",
                           "manager")

    def test_pie_source_must_use_real_proxy_transform(self):
        self.fail_mutation("review", "EnderProxy->GetComponentLocation()",
                           "FVector::ZeroVector", "proxy")

    def test_source_approval_not_fabricated(self):
        self.fail_mutation("integration", '"pulse_source_head_native_verified": false',
                           '"pulse_source_head_native_verified": true', "candidate")


if __name__ == "__main__":
    unittest.main()
