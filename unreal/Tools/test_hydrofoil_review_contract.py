#!/usr/bin/env python3
"""Source-only regression contract for PR #695's native C++ test.

This does NOT compile C++ or execute Unreal. It verifies that critical test
assertions remain in the native-test source; math is a bounded independent
proxy calculation with deliberate negative controls.
"""
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
TEST = ROOT / "Source/ToSailTheStarrySky/Private/Tests/AureateWakeHydrofoilStrutNativeTests.cpp"
REQUIRED_TEST_FRAGMENTS = (
    "TSTSS.Ship.HydrofoilStrutNativeReview",
    "GetComponents<UStaticMeshComponent>(Meshes)",
    "ReviewHydrofoilStrut_1", "ReviewHydrofoilStrut_2",
    "Hydrofoil_1", "Hydrofoil_2",
    "ECollisionEnabled::NoCollision",
    "Skyborne hydrofoil", "Skyborne support",
    "Foil %d advances halfway to Seaborne",
    "Support %d follows the actual moving foil",
    "Support %d visible mid-transition",
    "Seaborne support %d",
    "inboard tip reaches hull proxy",
    "outboard tip reaches hydrofoil center",
    "Support %d remains visible during fold",
    "Submersible support", "Submersible foil",
    "Submersible to Seaborne starts",
    "Return support", "Return hydrofoil",
    "Seaborne to Skyborne starts",
    "Restored Skyborne support", "Restored Skyborne hydrofoil",
    "Orbiter request still refused",
    "World->DestroyWorld(false)",
)
REQUIRED_ACTOR_FRAGMENTS = (
    "void AAureateWakePreviewActor::UpdateHydrofoilStruts()",
    "SetRelativeRotation(Span.ToOrientationQuat())",
    "SetRelativeScale3D(FVector(Length / 100.f, .12f, .12f))",
    "SetRelativeLocation((HullAnchor + FoilPosition) * .5f)",
    "Hydrofoils[Index]->SetVisibility(Form == EAureateWakeForm::Seaborne)",
    "UpdateHydrofoilStruts();",
    "RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview",
)

def source_contract(test_source, actor_source):
    failures = []
    for label, text, required in (
        ("test", test_source, REQUIRED_TEST_FRAGMENTS),
        ("actor", actor_source, REQUIRED_ACTOR_FRAGMENTS),
    ):
        for marker in required:
            if marker not in text:
                failures.append(f"{label} missing expected assertion/guard: {marker}")
    declared = re.findall(
        r'IMPLEMENT_SIMPLE_AUTOMATION_TEST\s*\(\s*\w+\s*,\s*"([^"]+)"',
        test_source,
        re.S,
    )
    if declared != ["TSTSS.Ship.HydrofoilStrutNativeReview"]:
        failures.append("unexpected native test registration")
    return failures

def endpoints(side, blend):
    """The cube's local-X endpoints derived from the documented foil poses."""
    if side not in (-1, 1) or not 0 <= blend <= 1:
        raise ValueError("invalid side or interpolation")
    anchor = (0.0, side * 60.0, -30.0)
    # Standard cubic easing in the actual native actor.
    alpha = blend * blend * (3.0 - 2.0 * blend)
    foil = (0.0, side * (80.0 * (1.0 - alpha) + 80.0 * alpha),
            -45.0 + (-140.0 + 45.0) * alpha)
    span = tuple(v - u for u, v in zip(anchor, foil))
    length = math.sqrt(sum(x*x for x in span))
    center = tuple((x+y)*.5 for x,y in zip(anchor, foil))
    direction = tuple(x / length for x in span)
    calculated_inboard = tuple(center[k] - 50.0*(length/100.0)*direction[k] for k in range(3))
    calculated_outboard = tuple(center[k] + 50.0*(length/100.0)*direction[k] for k in range(3))
    return anchor, foil, calculated_inboard, calculated_outboard, length

def distance(a, b):
    return math.dist(a, b)

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_source = TEST.read_text(encoding="utf-8")
        cls.actor_source = ACTOR.read_text(encoding="utf-8")

    def test_native_assertions_and_actor_guards_are_present(self):
        self.assertEqual(source_contract(self.test_source, self.actor_source), [])

    def test_mutated_test_assertion_fails_static_contract(self):
        bad = self.test_source.replace("inboard tip reaches hull proxy",
                                       "inboard tip not checked", 1)
        self.assertIn("test missing expected assertion/guard",
                      "; ".join(source_contract(bad, self.actor_source)))

    def test_mutated_actor_guard_fails_static_contract(self):
        bad = self.actor_source.replace(
            "RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview",
            "RequestedForm == EAureateWakeForm::Orbiter && bAllowOrbiterPreview",
            1)
        self.assertTrue(source_contract(self.test_source, bad))

    def test_proxy_cube_endpoints_are_symmetric_at_three_phases(self):
        for phase in (0.0, 0.5, 1.0):
            observed = []
            for side in (-1, 1):
                anchor, foil, inboard, outboard, length = endpoints(side, phase)
                self.assertLess(distance(anchor, inboard), 1e-8)
                self.assertLess(distance(foil, outboard), 1e-8)
                self.assertGreater(length, 0)
                observed.append(length)
            self.assertAlmostEqual(observed[0], observed[1], places=7)

    def test_old_wrong_constant_length_fails_endpoint_alignment(self):
        anchor, foil, inward, outward, length = endpoints(-1, 1.0)
        self.assertAlmostEqual(length, math.sqrt(20**2+110**2), places=8)
        # A stale 100cm cube has its local tip short of actual foil center.
        self.assertGreater(abs(length-100.0), 11)
        self.assertLess(distance(anchor, inward), 1e-8)
        self.assertLess(distance(foil, outward), 1e-8)

if __name__ == "__main__":
    unittest.main(verbosity=2)
