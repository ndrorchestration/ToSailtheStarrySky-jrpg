#!/usr/bin/env python3
"""Regression and mutation checks for the noncanonical Aureate Wake internals."""
from __future__ import annotations

import copy
import json
import unittest

from validate_aureate_internals_review import (
    HEADER, MANIFEST, SOURCE, InteriorHold, validate,
)

class InteriorTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.cpp = SOURCE.read_text(encoding="utf-8")

    def altered(self):
        return copy.deepcopy(self.data)

    def require_hold(self, data=None, header=None, cpp=None):
        with self.assertRaises(InteriorHold):
            validate(data if data is not None else self.data,
                     header if header is not None else self.header,
                     cpp if cpp is not None else self.cpp)

    def test_baseline_is_a_hold_not_a_habitable_ship(self):
        result = validate(self.data, self.header, self.cpp)
        self.assertEqual(result["systems"], 24)
        self.assertEqual(result["anchors"], 4)
        self.assertEqual(result["interfaces_unverified"], 3)
        self.assertEqual(result["preview_quarters_headroom_cm"], 35.0)
        self.assertEqual(result["status"], "HOLD_UNBUILT_INTERNALS_AND_UNVERIFIED_PASSAGE")
        self.assertFalse(result["native_verified"])
        self.assertFalse(result["starbourne_unlocked"])

    def test_enabled_by_default_is_refused(self):
        d = self.altered()
        d["review_permissions"]["enabled_by_default"] = True
        self.require_hold(data=d)

    def test_crew_walkability_claim_is_refused(self):
        d = self.altered()
        d["review_permissions"]["crew_walkable"] = True
        self.require_hold(data=d)

    def test_starbourne_unlock_claim_is_refused(self):
        d = self.altered()
        d["review_permissions"]["starbourne_unlocked"] = True
        self.require_hold(data=d)

    def test_production_art_claim_is_refused(self):
        d = self.altered()
        d["review_permissions"]["creator_art_approved"] = True
        self.require_hold(data=d)

    def test_native_approval_claim_is_refused(self):
        d = self.altered()
        d["review_permissions"]["native_approval"] = True
        self.require_hold(data=d)

    def test_wrong_display_configuration_is_refused(self):
        d = self.altered()
        d["display_forms"][0] = "Skyborne"
        self.require_hold(data=d)

    def test_serialized_enum_drift_is_refused(self):
        d = self.altered()
        d["serialized_forms"][-1] = "Starbourne"
        self.require_hold(data=d)

    def test_proxy_dimensions_cannot_claim_space(self):
        d = self.altered()
        d["geometry"]["quarters_proxy_extents_cm"][2] = 235
        d["geometry"]["habitation_verdict"] = "HABITABLE"
        self.require_hold(data=d)

    def test_source_quarters_height_change_requires_review(self):
        changed = self.cpp.replace(
            "LivingQuartersEnvelope->SetRelativeScale3D(FVector(2.2, 1.15, .35));",
            "LivingQuartersEnvelope->SetRelativeScale3D(FVector(2.2, 1.15, 2.35));")
        self.assertNotEqual(changed, self.cpp)
        self.require_hold(cpp=changed)

    def test_missing_anchor_refused(self):
        d = self.altered()
        d["anchors"].pop()
        self.require_hold(data=d)

    def test_anchor_reparenting_refused(self):
        changed = self.cpp.replace(
            "QuartersDeckReviewAnchor->SetupAttachment(BridgeHabitationPivot);",
            "QuartersDeckReviewAnchor->SetupAttachment(VesselRoot);")
        self.assertNotEqual(changed, self.cpp)
        self.require_hold(cpp=changed)

    def test_review_helm_rollback_protected(self):
        changed = self.cpp.replace(
            "BridgeHelmReviewAnchor->SetRelativeLocation(FVector(240, 0, 95));",
            "BridgeHelmReviewAnchor->SetRelativeLocation(FVector(0, 0, 95));")
        self.assertNotEqual(changed, self.cpp)
        self.require_hold(cpp=changed)

    def test_unverified_rotating_coupler_cannot_be_passed(self):
        d = self.altered()
        d["interfaces"][1]["status"] = "ACCESS_GRANTED"
        self.require_hold(data=d)

    def test_cannot_skip_rotating_coupler(self):
        d = self.altered()
        d["interfaces"][1]["type"] = "DIRECT_OPEN_HALLWAY"
        self.require_hold(data=d)

    def test_missing_emergency_egress_system_refused(self):
        d = self.altered()
        d["systems"] = [x for x in d["systems"] if x["id"] != "emergency_egress"]
        self.require_hold(data=d)

    def test_duplicate_system_refused(self):
        d = self.altered()
        d["systems"][0]["id"] = d["systems"][1]["id"]
        self.require_hold(data=d)

    def test_invented_functional_life_support_refused(self):
        d = self.altered()
        row = next(x for x in d["systems"] if x["id"] == "air_recirculation")
        row["gameplay_enabled"] = True
        self.require_hold(data=d)

    def test_unknown_dependency_refused(self):
        d = self.altered()
        d["systems"][0]["depends_on"].append("invented_engine")
        self.require_hold(data=d)

    def test_cyclic_dependencies_refused(self):
        d = self.altered()
        system = next(x for x in d["systems"] if x["id"] == "power_bus")
        system["depends_on"] = ["helm_controls"]
        self.require_hold(data=d)

    def test_cpp_starbourne_gate_removal_refused(self):
        changed = self.cpp.replace(
            "RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview",
            "RequestedForm == EAureateWakeForm::Orbiter && false")
        self.assertNotEqual(changed, self.cpp)
        self.require_hold(cpp=changed)

    def test_cpp_nonfinite_guard_removal_refused(self):
        changed = self.cpp.replace(
            "!HasFiniteHabitationReviewRotation(RequestedForm)",
            "false /* unsafe rotation allowed */")
        self.assertNotEqual(changed, self.cpp)
        self.require_hold(cpp=changed)

    def test_native_regression_targets_all_four_anchors(self):
        native = (HEADER.parents[1] /
                  "Private/Tests/AureateBridgeHabitationReviewTests.cpp").read_text(
                      encoding="utf-8")
        for label in ("Bridge/helm review anchor", "Quarters/deck review anchor",
                      "Engineering hull review anchor", "Boarding hull review anchor",
                      "Opt-in helm anchor follows dome center",
                      "Opt-out restores helm anchor with original bridge"):
            self.assertIn(label, native)

if __name__ == "__main__":
    unittest.main()
