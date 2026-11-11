"""Mutation and exact-source tests for First Wake review shot/runtime handoffs.

This is source authority reconciliation, never a real UE/PIE rendering test.
"""
import copy
import unittest
from verify_first_wake_shot_handoffs import load_inputs, validate_bridge


class FirstWakeRuntimeShotHandoffTests(unittest.TestCase):
    def setUp(self):
        self.bridge, self.plan, self.header, self.story, self.water = load_inputs()

    def check(self, bridge=None, plan=None, header=None, story=None, water=None):
        return validate_bridge(
            self.bridge if bridge is None else bridge,
            self.plan if plan is None else plan,
            self.header if header is None else header,
            self.story if story is None else story,
            self.water if water is None else water,
        )

    def assert_holds(self, needle, **changes):
        errors = self.check(**changes)
        self.assertTrue(any(needle in err for err in errors), errors)

    def test_exact_combined_source_handoff(self):
        self.assertEqual(self.check(), [])

    def test_no_unearned_unreal_evidence(self):
        edited = copy.deepcopy(self.bridge)
        edited["native_pie_verified"] = True
        self.assert_holds("unearned", bridge=edited)
        edited = copy.deepcopy(self.bridge)
        edited["mappings"][7]["evidence"] = ["fake_clip.mp4"]
        self.assert_holds("no native render evidence", bridge=edited)

    def test_no_sequencer_mutation_of_story_state(self):
        edited = copy.deepcopy(self.bridge)
        edited["mappings"][3]["auto_advance_story"] = True
        self.assert_holds("cannot authorize progression", bridge=edited)

    def test_no_missing_or_reordered_shot_handoffs(self):
        edited = copy.deepcopy(self.bridge)
        edited["mappings"][7], edited["mappings"][8] = (
            edited["mappings"][8], edited["mappings"][7]
        )
        self.assert_holds("handoff drift", bridge=edited)
        edited = copy.deepcopy(self.bridge)
        edited["mappings"].pop()
        self.assert_holds("ten-shot", bridge=edited)

    def test_no_premature_shoreline_or_late_party(self):
        edited = copy.deepcopy(self.bridge)
        edited["mappings"][9]["earliest_state"] = "Launched"
        self.assert_holds("boundary drift", bridge=edited)
        altered_shots = copy.deepcopy(self.plan)
        altered_shots["shots"][4]["subjects"].append("Lyra")
        self.assert_holds("early Lyra", plan=altered_shots)

    def test_no_false_water_gate_or_window(self):
        edited = copy.deepcopy(self.bridge)
        edited["water_gate"]["min_continuous_pretransition_world_seconds"] = 1.9943
        self.assert_holds("strict two-second", bridge=edited)
        edited = copy.deepcopy(self.bridge)
        edited["mappings"][8]["trigger"] = "scripted_scene_cut"
        self.assert_holds("boundary drift", bridge=edited)
        altered_plan = copy.deepcopy(self.plan)
        altered_plan["shots"][8]["min_continuous_pretransition_world_seconds"] = 1.9943
        self.assert_holds("exactly two witnessed", plan=altered_plan)

    def test_cpp_water_gate_must_be_directly_witnessed(self):
        altered_water = self.water.replace(
            "if (StableContactSeconds < 2.f) return false;",
            "if (StableContactSeconds < 1.5f) return false;", 1,
        )
        self.assert_holds("physical water witness marker", water=altered_water)
        # Guard is present in several places; remove all references to detect drift.
        altered_water = self.water.replace(
            "bHasPreviousStableSample", "hasFakePriorClock"
        )
        self.assert_holds("physical water witness marker", water=altered_water)

    def test_real_story_enum_and_authority_required(self):
        altered_header = self.header.replace(
            "    SeaContact,", "    SeaContactDeleted,", 1
        )
        self.assert_holds("runtime story enum changed", header=altered_header)
        altered_story = self.story.replace(
            "CurrentBeat == ETSTSSFirstWakeBeat::SeaContact",
            "CurrentBeat == ETSTSSFirstWakeBeat::Launched", 1
        )
        self.assert_holds("runtime authority marker", story=altered_story)

    def test_no_starbourne_early_release(self):
        edited = copy.deepcopy(self.bridge)
        edited["story_policy"] = "No stated vessel restrictions."
        self.assert_holds("Starbourne restriction", bridge=edited)

    def test_no_implicit_runtime_capability(self):
        edited = copy.deepcopy(self.bridge)
        edited["runtime_emits_shot_cues"] = True
        self.assert_holds("unearned runtime", bridge=edited)


if __name__ == "__main__":
    unittest.main()
