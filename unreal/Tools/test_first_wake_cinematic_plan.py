"""Negative controls for the review-only First Wake cinematic shot plan."""
import copy
import unittest

from verify_first_wake_cinematic_plan import load_plan, validate_plan


class FirstWakeCinematicPlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = load_plan()

    def fails_with(self, phrase):
        self.assertTrue(any(phrase in x for x in validate_plan(self.plan)),
                        msg=validate_plan(self.plan))

    def test_authored_source_contract(self):
        self.assertEqual([], validate_plan(self.plan))

    def test_rejects_premature_lyra(self):
        self.plan["shots"][4]["subjects"].append("Lyra")
        self.fails_with("before Splashdown")

    def test_rejects_early_party_or_talen_playability(self):
        self.plan["shots"][0]["subjects"].append("Aepex")
        self.fails_with("late-party")
        self.plan = load_plan()
        self.plan["shots"][-1]["playable_subjects"].append("Talen")
        self.fails_with("never be playable")

    def test_rejects_reordered_beats(self):
        self.plan["shots"][0], self.plan["shots"][1] = self.plan["shots"][1], self.plan["shots"][0]
        self.fails_with("reordered")

    def test_rejects_false_water_window(self):
        self.plan["shots"][8]["min_continuous_pretransition_world_seconds"] = 1.9943
        self.fails_with("insufficient")

    def test_rejects_unearned_approval(self):
        self.plan["shots"][0]["creator_accepted"] = True
        self.fails_with("unearned")
        self.plan = load_plan()
        self.plan["approval_status"] = "APPROVED"
        self.fails_with("cannot claim")

    def test_rejects_missing_cinematic_spec(self):
        self.plan["shots"][6]["composition"] = ""
        self.fails_with("composition")
        self.plan = load_plan()
        self.plan["shots"][0]["lens_mm"] = 300
        self.fails_with("focal length")

    def test_rejects_mockup_as_native(self):
        self.plan["shots"][0]["requires_native_capture"] = False
        self.fails_with("native capture")


if __name__ == "__main__":
    unittest.main()
