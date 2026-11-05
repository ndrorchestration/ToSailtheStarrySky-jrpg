"""Negative controls for the combined source-only authority/dependency gate."""
from __future__ import annotations
import copy
import json
import unittest

import check_integrated_review_contract as gate

ROOT = gate.ROOT


def inputs():
    def txt(p): return (ROOT / p).read_text(encoding="utf-8")
    def obj(p): return json.loads(txt(p))
    return [
        txt("AGENTS.md"), txt("README.md"),
        obj("data/design/level-one-rank-constraints.json"),
        obj("unreal/Tools/first_wake_dependency_contract.json"),
        obj("unreal/Tools/dependency_baseline.json"),
        obj("unreal/ToSailTheStarrySky.uproject"),
        txt("unreal/Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md"),
        txt("unreal/Docs/FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md"),
        txt("unreal/Tools/Verify-Unreal.ps1"),
    ]


class IntegratedSourceGateTests(unittest.TestCase):
    def setUp(self):
        self.args = copy.deepcopy(inputs())

    def fail_if(self, expected):
        with self.assertRaisesRegex(gate.CompositionHold, expected):
            gate.check_consistency(*self.args)

    def test_composed_source_passes_without_native_claim(self):
        result = gate.verify()
        self.assertEqual(result["result"], "COMPOSED_SOURCE_DECLARATIONS_PASS")
        self.assertEqual(result["native_automation_26"], "NOT_TESTED")
        self.assertEqual(result["pie_cases_13"], "NOT_TESTED")
        self.assertFalse(result["merges_or_releases_authorized"])

    def test_legacy_engine_instruction_cannot_be_repromoted(self):
        self.args[1] = self.args[1].replace("Current forward-engine authority", "Old")
        self.fail_if("Root README")

    def test_wrong_engine_lock_fails(self):
        self.args[0] = self.args[0].replace("Unreal Engine 5.8.4", "Godot 4.7.2")
        self.fail_if("AGENTS.md")

    def test_stat_numeric_permission_cannot_be_added(self):
        self.args[2]["numeric_values_approved"] = True
        self.fail_if("unreviewed numbers")

    def test_stat_hierarchy_cannot_be_inverted(self):
        self.args[2]["strict_rank_rules"][2]["first"] = "ender"
        self.fail_if("relative-stat rules")

    def test_primary_plugin_baseline_mismatch_fails(self):
        self.args[3]["project"]["enabled_plugins"] = []
        self.fail_if("enabled plugin")

    def test_secondary_plugin_baseline_mismatch_fails(self):
        self.args[4]["unreal"]["enabled_project_plugins"] = []
        self.fail_if("enabled plugin")

    def test_secondary_runtime_module_mismatch_fails(self):
        self.args[4]["unreal"]["runtime_module_dependencies"].append("Niagara")
        self.fail_if("runtime modules")

    def test_historical_npm_mismatch_fails(self):
        self.args[4]["legacy_nwjs"]["dev_dependencies"]["playwright"] = "^1.64.0"
        self.fail_if("npm")

    def test_unreviewed_release_flag_fails(self):
        self.args[3]["policy"]["release_authorized"] = True
        self.fail_if("allows install")

    def test_missing_pie_scenario_fails(self):
        self.args[7] = self.args[7].replace("| P13 |", "| PXX |")
        self.fail_if("P13")

    def test_native_test_name_drift_fails(self):
        self.args[8] = self.args[8].replace(
            "TSTSS.FirstWake.ReviewObjectivesAreReadOnly", "TSTSS.FirstWake.MISSING"
        )
        self.fail_if("review-objectives native automation")

    def test_joined_splashdown_native_name_cannot_disappear(self):
        self.args[8] = self.args[8].replace(
            "TSTSS.FirstWake.InteractionToSplashdown", "TSTSS.FirstWake.MISSING"
        )
        self.fail_if("26th interaction-to-Splashdown")

    def test_no_admitted_implicit_merge(self):
        self.args[6] = self.args[6].replace("#711", "#999")
        self.fail_if("ancestry")


if __name__ == "__main__":
    unittest.main()
