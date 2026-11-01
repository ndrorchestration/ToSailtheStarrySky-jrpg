"""Reversible offline checks of 3-form wing envelope and source parity."""
from __future__ import annotations
import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[1]
TOOLS=HERE/'Tools'
sys.path.insert(0,str(TOOLS))
import audit_aureate_wing_clearance as check

CPP_FIXTURE = '''const float RootY = Side * 112.f;
const float RootX = bForward ? 155.f : -180.f;
Scale = FVector(.94f, .82f, 1.f);
Scale = FVector(.78f, .38f, .95f);
bUseRootPivotedWingPose && AuthoredWingMesh
RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter'''
HEADER_FIXTURE='bUseRootPivotedWingPose = false;\nbAllowOrbiterPreview = false;'
# This fixture is used for isolated algebra tests; the CLI reads the real UE C++ source.


class OfflineEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(tempfile.mkdtemp(prefix='tstss-clearance-'))
        # Make the exact corrected generator output. No external packages needed.
        spec=importlib.util.spec_from_file_location('candidate_wing',TOOLS/'author_aureate_wing_glb.py')
        if spec is None or spec.loader is None:
            raise RuntimeError('Missing wing generator on checked-out branch')
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls.glb,cls.img,cls.manifest=mod.build()
        cls.path=cls.root/'AureateWake_Wing_Lookdev.glb'
        cls.path.write_bytes(cls.glb)
        cls.vertices,cls.counts=check.read_vertices(cls.path,per_primitive=900)

    @classmethod
    def tearDownClass(cls):
        for item in cls.root.iterdir():item.unlink()
        cls.root.rmdir()

    def test_actual_mesh_vertex_counts_and_meter_scale(self):
        self.assertEqual(self.counts, [292,14770,78])
        self.assertGreater(len(self.vertices), 1200)
        self.assertLess(len(self.vertices), 1500)
        self.assertAlmostEqual(max(p[0] for p in self.vertices), 280,delta=.5)
        self.assertAlmostEqual(min(p[0] for p in self.vertices), -16,delta=.5)
        self.assertTrue(all(math.isfinite(v) for pt in self.vertices for v in pt))

    def test_all_six_ordinary_directed_transitions_are_sampled_clear(self):
        report=check.audit(self.vertices,steps=12)
        self.assertEqual(report['checked_directed_transitions'],6)
        self.assertEqual(report['checked_poses'],78)
        self.assertGreater(report['minimum_proxy_aabb_clearance_cm'],10)
        self.assertGreater(report['minimum_interwing_aabb_clearance_cm'],10)
        self.assertIn('SAMPLED_',report['authority'])
        self.assertIn('root',report['unresolved_visual_gates'][0])

    def test_unreal_rotation_convention(self):
        self.assertAlmostEqual(check.qrot(check.quaternion(0,90,0),(1,0,0))[1],1,places=5)
        self.assertAlmostEqual(check.qrot(check.quaternion(90,0,0),(1,0,0))[2],1,places=5)
        self.assertAlmostEqual(check.qrot(check.quaternion(0,0,90),(0,1,0))[2],1,places=5)
        self.assertAlmostEqual(math.sqrt(sum(q*q for q in check.qslerp(check.quaternion(20,35,45),check.quaternion(-15,120,-30),.6))),1,places=6)

    def test_direct_orbiter_interpolation_fails_clearance(self):
        # This is intentionally NOT included in the normal audit, because the
        # existing authored-wing Orbiter straight-line transition clips the hull.
        hit=False
        for k in (0.3,0.4,0.5,0.6,0.7):
            for wing in range(4):
                a=check.pose('Submersible',wing)
                b=check.pose('Orbiter',wing)
                bounds=check.sampled_bounds(self.vertices,check.blend(a,b,k))
                if min(check.clearance_against_boxes(bounds)) < check.MIN_CLEARANCE_CM:
                    hit=True
        self.assertTrue(hit,'Physics/review guard should remain fail-closed for Orbiter path')

    def test_pose_source_contract_detects_missing_secret_mode_guard(self):
        check.assert_source_contract(CPP_FIXTURE,HEADER_FIXTURE)
        with self.assertRaises(check.GeometryHold):
            check.assert_source_contract(CPP_FIXTURE.replace('CurrentForm == EAureateWakeForm::Orbiter','CurrentForm == EAureateWakeForm::Skyborne'),HEADER_FIXTURE)
        with self.assertRaises(check.GeometryHold):
            check.assert_source_contract(CPP_FIXTURE.replace('112.f','90.f'),HEADER_FIXTURE)

    def test_intentionally_colliding_local_pose_is_rejected(self):
        original=check.pose
        def broken(form,wing):
            p,r,s=original(form,wing)
            return ((p[0],(-1 if wing%2==0 else 1)*72.,p[2]),r,s)
        try:
            check.pose=broken
            with self.assertRaises(check.GeometryHold):
                check.audit(self.vertices,steps=12)
        finally:
            check.pose=original

    def test_degenerate_or_truncated_glb_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.glb'
            path.write_bytes(self.glb[:40])
            with self.assertRaises((check.GeometryHold,ValueError,IndexError)):
                check.read_vertices(path)
            path.write_bytes(b'not a GLB')
            with self.assertRaises(check.GeometryHold):
                check.read_vertices(path)

    def test_actor_source_and_header_still_guarded(self):
        cpp=(HERE/'Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp').read_text()
        header=(HERE/'Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h').read_text()
        check.assert_source_contract(cpp,header)
        self.assertIn('OriginalCubeWingMesh',cpp)
        self.assertIn('OriginalCubeWingMesh',header)


if __name__=='__main__':unittest.main()