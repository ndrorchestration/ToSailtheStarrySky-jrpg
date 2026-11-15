"""Engine-free negative/positive tests for the native Pulse readback parser.

Synthetic fixture logs prove parser behavior, never native Unreal gameplay.
"""
import unittest
from pathlib import Path
from verify_focus_multifoe_pie_log import verify_log

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "Source/ToSailTheStarrySky/Private/Review/TSTSSResonatorFocusReviewActor.cpp"
GOOD = "\n".join([
    "LogTemp: Display: TSTSS_FOCUS_COMBAT_ADMITTED: two spells; foes=3 multi_probe=1",
    "LogTemp: Display: TSTSS_FOCUS_INPUT_AND_HUD_BOUND: keys 1 and 2",
    "LogTemp: Display: TSTSS_FOCUS_ACTION_ACCEPTED actor=Ender skill=Ender_ResonantPulse target=Ender",
    "LogTemp: Display: TSTSS_FOCUS_MULTIFOE_READBACK mp_spent=3 primary_hp_delta=12 elevated_hp_delta=9 outside_hp_delta=0 ionia_hp_delta=0",
])


class MultiFoePieReadbackTests(unittest.TestCase):
    def test_first_pulse_log_accepts_exact_faction_and_mp_deltas(self):
        self.assertEqual(verify_log(GOOD), {
            "mp_spent": 3, "primary_hp_delta": 12,
            "elevated_hp_delta": 9, "outside_hp_delta": 0,
            "ionia_hp_delta": 0,
        })

    def test_wrong_mp_denied(self):
        with self.assertRaisesRegex(ValueError, "3 MP"):
            verify_log(GOOD.replace("mp_spent=3", "mp_spent=6"))

    def test_outside_foe_damage_denied(self):
        with self.assertRaisesRegex(ValueError, "was damaged"):
            verify_log(GOOD.replace("outside_hp_delta=0", "outside_hp_delta=8"))

    def test_ionia_damage_denied(self):
        with self.assertRaisesRegex(ValueError, "was damaged"):
            verify_log(GOOD.replace("ionia_hp_delta=0", "ionia_hp_delta=4"))

    def test_elevated_foe_missed_denied(self):
        with self.assertRaisesRegex(ValueError, "positive HP"):
            verify_log(GOOD.replace("elevated_hp_delta=9", "elevated_hp_delta=0"))

    def test_primary_foe_missed_denied(self):
        with self.assertRaisesRegex(ValueError, "positive HP"):
            verify_log(GOOD.replace("primary_hp_delta=12", "primary_hp_delta=0"))

    def test_duplicate_pulse_denied(self):
        with self.assertRaisesRegex(ValueError, "exactly one Ender"):
            verify_log(GOOD + "\n" + (
                "LogTemp: Display: TSTSS_FOCUS_ACTION_ACCEPTED "
                "actor=Ender skill=Ender_ResonantPulse target=Ender"
            ))

    def test_missing_optin_denied(self):
        with self.assertRaisesRegex(ValueError, "three-foe"):
            verify_log(GOOD.replace("multi_probe=1", "multi_probe=0"))

    def test_missing_input_binding_denied(self):
        with self.assertRaisesRegex(ValueError, "input/HUD"):
            verify_log(GOOD.replace("INPUT_AND_HUD_BOUND", "INPUT_NOT_BOUND"))

    def test_unaccepted_or_early_readback_denied(self):
        lines = GOOD.splitlines()
        with self.assertRaisesRegex(ValueError, "preceded"):
            verify_log("\n".join([lines[0], lines[1], lines[3], lines[2]]))

    def test_denied_action_even_with_fake_readback(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            verify_log(GOOD + "\nTSTSS_FOCUS_MULTIFOE_READBACK_DENIED")

    def test_instrumentation_is_after_actual_atomic_manager_call(self):
        source = ACTOR.read_text(encoding="utf-8")
        pulse = source.split(
            "bool ATSTSSResonatorFocusReviewActor::TryCastResonantPulse()", 1
        )[-1].split("void ATSTSSResonatorFocusReviewActor::CastCenteringKey()", 1)[0]
        for required in (
            "const bool bProof = bMultiEnemyPulseProofReview;",
            "const TArray<FTSTSSCombatant> Before = bProof",
            "const bool bAccepted = CombatManager->SubmitResonantPulseArea(Command, Positions);",
            "if (bProof)",
            "const TArray<FTSTSSCombatant> After =",
            "BE->Resource-AE->Resource",
            "BP->Health-AP->Health",
            "BH->Health-AH->Health",
            "BO->Health-AO->Health",
            "BI->Health-AI->Health",
            "TSTSS_FOCUS_MULTIFOE_READBACK mp_spent=",
        ):
            self.assertIn(required, pulse)
        self.assertLess(pulse.index("SubmitResonantPulseArea(Command, Positions)"),
                        pulse.index("TSTSS_FOCUS_MULTIFOE_READBACK mp_spent="))


if __name__ == "__main__":
    unittest.main()
