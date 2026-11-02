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
    "const FVector HullAnchor(0.f, Side * 60.f, -30.f);",
    "FVector(0, Side * 80.f, bDeployed ? -140.f : -45.f)",
    "T * T * (3.f - 2.f * T)",
    "Hydrofoils[Index]->SetVisibility(true);",
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

# Only the three ordinary-form *proxy* foil-center Z values, not an
# imported mesh, physics simulation, render or continuous-collision proof.
ORDINARY_FOIL_Z = {"Skyborne": -45.0, "Seaborne": -140.0, "Submersible": -45.0}

def ordinary_route(start, end, side, fraction):
    if start == end or start not in ORDINARY_FOIL_Z or end not in ORDINARY_FOIL_Z:
        raise ValueError("route must select two distinct ordinary forms")
    if type(side) is not int or side not in (-1, 1):
        raise ValueError("port/starboard must be explicit")
    if not isinstance(fraction, (float, int)) or isinstance(fraction, bool) or not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be finite within [0, 1]")
    smooth = fraction * fraction * (3.0 - 2.0 * fraction)
    foil_z = (1.0 - smooth) * ORDINARY_FOIL_Z[start] + smooth * ORDINARY_FOIL_Z[end]
    anchor = (0.0, side * 60.0, -30.0)
    foil = (0.0, side * 80.0, foil_z)
    length = distance(anchor, foil)
    center = tuple((u + v) * .5 for u, v in zip(anchor, foil))
    direction = tuple((v - u) / length for u, v in zip(anchor, foil))
    inboard = tuple(center[i] - length * .5 * direction[i] for i in range(3))
    outboard = tuple(center[i] + length * .5 * direction[i] for i in range(3))
    return anchor, foil, inboard, outboard, length

def hull_exit_parameter(anchor, foil):
    # Provisional 100cm Unreal BasicShapes cube, hull scale (8, 1.5, .65),
    # with root-local y±75 cm, z±32.5 cm. Support begins INSIDE the
    # review hull at z=-30: that overlap is an intentional proxy anchor.
    # This only calculates where its centerline *leaves* an axis-aligned
    # box, not whether a strut mesh collides with any authored geometry.
    if abs(anchor[1]) >= 75.0 or abs(anchor[2]) >= 32.5:
        raise ValueError("expected proxy hull anchor within hull y/z bounds")
    dz = foil[2] - anchor[2]
    if dz >= 0 or foil[2] >= -32.5:
        raise ValueError("foil must extend below proxy hull for this review")
    vertical_exit = (-32.5 - anchor[2]) / dz
    dy = abs(foil[1] - anchor[1])
    lateral_exit = (75.0 - abs(anchor[1])) / dy if dy else math.inf
    return min(vertical_exit, lateral_exit)

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

    def test_actor_foil_and_hull_literal_mutations_fail_closed(self):
        changes = (
            ("const FVector HullAnchor(0.f, Side * 60.f, -30.f);",
             "const FVector HullAnchor(0.f, Side * 65.f, -30.f);"),
            ("FVector(0, Side * 80.f, bDeployed ? -140.f : -45.f)",
             "FVector(0, Side * 80.f, bDeployed ? -120.f : -45.f)"),
            ("T * T * (3.f - 2.f * T)", "T * T * T"),
        )
        for original, replacement in changes:
            self.assertIn(original, self.actor_source)
            altered = self.actor_source.replace(original, replacement, 1)
            self.assertTrue(source_contract(self.test_source, altered),
                            f"changed proxy contract unexpectedly accepted: {original}")

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

    def test_six_ordinary_routes_126_samples_two_supports_each(self):
        forms = tuple(ORDINARY_FOIL_Z)
        count = 0
        for start in forms:
            for end in forms:
                if start == end:
                    continue
                previous = {side: None for side in (-1, 1)}
                for step in range(21):
                    fraction = step / 20.0
                    per_side = {}
                    for side in (-1, 1):
                        anchor, foil, inboard, outboard, length = ordinary_route(
                            start, end, side, fraction)
                        self.assertLess(distance(anchor, inboard), 1e-8)
                        self.assertLess(distance(foil, outboard), 1e-8)
                        self.assertGreater(length, 24.9)
                        self.assertTrue(0.0 < hull_exit_parameter(anchor, foil) < 0.2)
                        self.assertAlmostEqual(foil[1], side * 80.0)
                        if previous[side] is not None:
                            delta = ORDINARY_FOIL_Z[end] - ORDINARY_FOIL_Z[start]
                            last = previous[side]
                            if delta < 0:
                                self.assertGreaterEqual(last + 1e-8, foil[2])
                            elif delta > 0:
                                self.assertLessEqual(last - 1e-8, foil[2])
                            else:
                                self.assertAlmostEqual(last, foil[2])
                        previous[side] = foil[2]
                        per_side[side] = (anchor, foil, length)
                        count += 1
                    left, right = per_side[-1], per_side[1]
                    self.assertAlmostEqual(left[2], right[2])
                    self.assertAlmostEqual(left[1][1], -right[1][1])
                    self.assertAlmostEqual(left[1][2], right[1][2])
        self.assertEqual(count, 252)  # 6 form routes x 21 phases x 2 supports

    def test_route_mutations_are_rejected(self):
        for bad in (("Skyborne", "Skyborne", 1, .5),
                    ("Skyborne", "Orbiter", 1, .5),
                    ("Skyborne", "Seaborne", 0, .5),
                    ("Skyborne", "Seaborne", -1, float("nan")),
                    ("Skyborne", "Seaborne", 1, 1.01)):
            with self.assertRaises(ValueError):
                ordinary_route(*bad)
        with self.assertRaises(ValueError):
            hull_exit_parameter((0.0, 60.0, -30.0), (0.0, 80.0, -10.0))

    def test_old_wrong_constant_length_fails_endpoint_alignment(self):
        anchor, foil, inward, outward, length = endpoints(-1, 1.0)
        self.assertAlmostEqual(length, math.sqrt(20**2+110**2), places=8)
        # A stale 100cm cube has its local tip short of actual foil center.
        self.assertGreater(abs(length-100.0), 11)
        self.assertLess(distance(anchor, inward), 1e-8)
        self.assertLess(distance(foil, outward), 1e-8)

if __name__ == "__main__":
    unittest.main(verbosity=2)
