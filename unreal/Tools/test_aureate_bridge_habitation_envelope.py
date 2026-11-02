#!/usr/bin/env python3
"""Fail-closed contract tests for rotating bridge+quarters wing envelope screen."""
import unittest
from pathlib import Path
from audit_aureate_bridge_habitation_envelope import (
    COMPONENT_BOXES_CM, PROVENANCE, TEST_ONLY_YAW_DEGREES, EnvelopeHold,
    conservative_box_triangle_candidates, require_actor_source, to_coupled_local,
)
from audit_aureate_root_support_routes import form_routes

ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/"Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
HEADER=ROOT/"Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h"
NATIVE=ROOT/"Source/ToSailTheStarrySky/Private/Tests/AureateBridgeHabitationReviewTests.cpp"


class HabitationEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp=CPP.read_text(encoding="utf-8")
        cls.header=HEADER.read_text(encoding="utf-8")
        cls.native=NATIVE.read_text(encoding="utf-8")

    def test_exact_actor_source_and_native_test_angles(self):
        require_actor_source(self.cpp,self.header,self.native)

    def test_absent_living_quarters_attachment_holds(self):
        altered=self.cpp.replace(
            "LivingQuartersEnvelope->SetupAttachment(BridgeHabitationPivot);",
            "LivingQuartersEnvelope->SetupAttachment(VesselRoot);")
        with self.assertRaisesRegex(EnvelopeHold,"source drift"):
            require_actor_source(altered,self.header,self.native)

    def test_changed_provisional_pivot_holds(self):
        altered=self.cpp.replace(
            "BridgeHabitationPivot->SetRelativeLocation(FVector(0, 0, 50));",
            "BridgeHabitationPivot->SetRelativeLocation(FVector(200, 0, 50));")
        with self.assertRaisesRegex(EnvelopeHold,"source drift"):
            require_actor_source(altered,self.header,self.native)

    def test_changed_native_demo_angle_holds(self):
        altered=self.native.replace(
            "Ship->SubmersibleHabitationReviewRotation = FRotator(0.f, 75.f, 0.f);",
            "Ship->SubmersibleHabitationReviewRotation = FRotator(0.f, 10.f, 0.f);")
        with self.assertRaisesRegex(EnvelopeHold,"source drift"):
            require_actor_source(self.cpp,self.header,altered)

    def test_126_sample_review_never_admits_orbiter(self):
        rows=form_routes()
        self.assertEqual(len(rows),126)
        self.assertEqual(len({(a,b) for a,b,_,_ in rows}),6)
        self.assertFalse(any(a=="Orbiter" or b=="Orbiter" for a,b,_,_ in rows))
        self.assertEqual(TEST_ONLY_YAW_DEGREES,{"Skyborne":0.,"Seaborne":30.,"Submersible":75.})
        self.assertIn("NOT_MESH_COLLISION_OR_CCD",PROVENANCE)
        self.assertEqual(set(COMPONENT_BOXES_CM),{"ForwardBridge_PROXY","LivingQuarters_PROXY"})

    def test_numpy_conservative_triangle_aabb_near_and_far_if_available(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy is optional in CI; full geometric Windows run required")
        pts=np.asarray([(0.,0.,0.),(2.,0.,0.),(0.,2.,0.),(30.,0.,0.),(32.,0.,0.),(30.,2.,0.)])
        faces=np.asarray([(0,1,2),(3,4,5)])
        near,lower=conservative_box_triangle_candidates(
            pts,faces,(3.,3.,3.),np)
        self.assertEqual(near,1)
        self.assertAlmostEqual(lower,0.)
        shifted=pts+np.asarray([50.,0.,0.])
        far,lower=conservative_box_triangle_candidates(
            shifted,faces,(3.,3.,3.),np)
        self.assertEqual(far,0)
        self.assertGreater(lower,10.)

    def test_numpy_inverse_yaw_couples_both_children_if_available(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy optional in hosted source CI")
        # A yaw of +90 maps local +X to world +Y; inverting returns +X.
        world=np.asarray([(0.,10.,130.),(0.,10.,25.)])
        dome=to_coupled_local(world[:1],90.,(0.,0.,80.),np)
        quarters=to_coupled_local(world[1:],90.,(0.,0.,-25.),np)
        self.assertAlmostEqual(dome[0,0],10.)
        self.assertAlmostEqual(dome[0,1],0.)
        self.assertAlmostEqual(quarters[0,0],10.)
        self.assertAlmostEqual(quarters[0,2],0.)


if __name__=="__main__":
    unittest.main()
