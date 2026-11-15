"""Fail-closed source policy for Ender review focus HUD and actual ability routing.

The scene contains only one training foe; a live multi-enemy/PIE visual test
is separately required. These checks are not a native Unreal build.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "Source/ToSailTheStarrySky/Private/Review/TSTSSResonatorFocusReviewActor.cpp"
SKILLS = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSBattleSkillSystem.h"


def check_contract(source: str, skills: str) -> None:
    controls = source.split("void ATSTSSResonatorFocusReviewActor::RefreshHUD()", 1)[-1]
    required = (
        "1  CENTERING: 5 MP, +15% PARTY PHYSICAL DEF, 3 ROUNDS",
        "2  RESONANT PULSE: 3 MP, 600 CM ENEMY-ONLY 3D AOE",
        "ONE REVIEW FOE",
        "THREE REVIEW FOES: TWO INSIDE (ONE ELEVATED), ONE OUTSIDE",
    )
    for token in required:
        if token not in controls:
            raise ValueError("Focus HUD contract drift: " + token)
    if "FoeMode+TEXT(" not in controls:
        raise ValueError("Focus HUD lost dynamic opt-in foe count")
    for misleading in ("SINGLE ENEMY", "SINGLE TARGET", "ALL TARGETS"):
        if misleading in controls:
            raise ValueError("Focus HUD misrepresents area targeting: " + misleading)
    pulse = source.split(
        "bool ATSTSSResonatorFocusReviewActor::TryCastResonantPulse()", 1
    )[-1].split("void ATSTSSResonatorFocusReviewActor::CastCenteringKey()", 1)[0]
    for token in (
        "GetComponentLocation()",
        "SubmitResonantPulseArea(Command, Positions)",
        "Command.TargetParticipantId = TEXT(\"Ender\")",
        "CombatManager->GetActiveParticipantId() != TEXT(\"Ender\")",
    ):
        if token not in pulse:
            raise ValueError("Focus Pulse input/caster contract drift: " + token)
    if "ResonantPulseRadiusCm = 600.0" not in skills:
        raise ValueError("Focus area radius changed from provisional 600 cm")


class FocusHUDContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ACTOR.read_text(encoding="utf8")
        cls.skills = SKILLS.read_text(encoding="utf8")

    def test_hud_matches_actual_3d_enemy_only_pulse(self):
        check_contract(self.source, self.skills)

    def test_mislabeled_single_enemy_mutation_fails(self):
        corrupted = self.source.replace(
            "600 CM ENEMY-ONLY 3D AOE", "SINGLE ENEMY"
        )
        with self.assertRaisesRegex(ValueError, "Focus HUD contract drift"):
            check_contract(corrupted, self.skills)

    def test_tampered_radius_fails(self):
        with self.assertRaisesRegex(ValueError, "Focus area radius changed"):
            check_contract(
                self.source,
                self.skills.replace("ResonantPulseRadiusCm = 600.0",
                                    "ResonantPulseRadiusCm = 275.0"),
            )


if __name__ == "__main__":
    unittest.main()
