#!/usr/bin/env python3
"""Source tests for 126-sample targeted Aureate wing-root route admission."""
from __future__ import annotations

import math
import unittest

from audit_aureate_root_support_routes import (
    form_routes, source_sections, transform_vertices_np, screen_category,
    WING_MEMBRANE_END, WING_VENATION_END, WING_HINGE_END,
    HULL_SUPPORT_START, HULL_SUPPORT_END, THRESHOLD_CM
)
from audit_aureate_v2_crosslane_envelope import V2ReviewHold
from audit_aureate_wing_clearance import qrot,blend,pose


class RouteSupportScreenTests(unittest.TestCase):
    def test_six_directed_routes_exactly_126_samples(self):
        rows=form_routes()
        self.assertEqual(len(rows),126)
        unique=list(dict.fromkeys((a,b) for a,b,_,_ in rows))
        self.assertEqual(len(unique),6)
        for a,b in unique:
            times=[t for x,y,_,t in rows if (x,y)==(a,b)]
            self.assertEqual(len(times),21)
            self.assertEqual(times[0],0.)
            self.assertEqual(times[-1],1.)
            self.assertEqual(len(set(times)),21)
            self.assertNotEqual(a,b)
            self.assertNotIn("Orbiter",(a,b))

    def test_invalid_interval_budgets_fail_closed(self):
        for count in (19,-1,101,True,1.5):
            with self.subTest(count=count):
                with self.assertRaises(V2ReviewHold):
                    form_routes(count)

    def test_no_duplicate_symmetric_form_loss(self):
        routes={(a,b) for a,b,_,_ in form_routes()}
        for a,b in routes:
            self.assertIn((b,a),routes)

    def test_source_face_sections_are_pinned(self):
        w=list(range(WING_HINGE_END))
        h=list(range(1950))
        portions=source_sections(w,h)
        self.assertEqual(len(portions["venation"]),28700)
        self.assertEqual(len(portions["hinge"]),144)
        self.assertEqual(len(portions["tubes"]),4)
        self.assertEqual(portions["venation"][0],WING_MEMBRANE_END)
        self.assertEqual(portions["hinge"][0],WING_VENATION_END)
        self.assertEqual([p[0] for p in portions["tubes"]],[240,272,304,336])
        self.assertEqual(portions["tubes"][-1][-1],HULL_SUPPORT_END-1)

    def test_changed_topology_fails_closed(self):
        with self.assertRaises(V2ReviewHold):
            source_sections(list(range(WING_HINGE_END-1)),list(range(1950)))
        with self.assertRaises(V2ReviewHold):
            source_sections(list(range(WING_HINGE_END)),list(range(1949)))

    def test_contact_threshold_is_not_silently_relaxed(self):
        self.assertEqual(THRESHOLD_CM,10.)

    def test_numpy_pose_matches_review_quaternion_if_installed(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("Optional Windows route dependency numpy not available in CI")
        pts=np.asarray([(0.,0.,0.),(10.,4.,3.),(280.,30.,5.),(-8.,-2.,0.)])
        for a,b,_,t in (form_routes()[0],form_routes()[34],form_routes()[-1]):
            for idx in (0,2,3):
                tr=blend(pose(a,idx),pose(b,idx),t)
                got=transform_vertices_np(pts,tr,np)
                xyz,q,sc=tr
                for k,p in enumerate(pts):
                    r=qrot(q,tuple(p[i]*sc[i] for i in range(3)))
                    for j in range(3):
                        self.assertAlmostEqual(got[k,j],r[j]+xyz[j],places=8)

    def test_numpy_broadphase_rejects_real_triangle_proximity_if_installed(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not installed in CI; Windows execution required")
        tri=np.asarray([(0.,0.,0.),(4.,0.,0.),(0.,4.,0.)])
        tube=tri.reshape((1,3,3))
        w0=np.asarray([(1.,1.,3.),(2.,1.,3.),(1.,2.,3.)])
        q=screen_category(w0,[(0,1,2)],[tube],np)
        self.assertTrue(q["under_threshold"])
        self.assertAlmostEqual(q["first_witness_distance_cm"],3.)
        farther=w0+np.asarray([0.,0.,12.])
        x=screen_category(farther,[(0,1,2)],[tube],np)
        self.assertFalse(x["under_threshold"])
        self.assertIsNone(x["first_witness_distance_cm"])

    def test_numpy_early_witness_is_not_claimed_global_minimum_if_installed(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("Optional numpy not available")
        support=np.asarray([[(0.,0.,0.),(4.,0.,0.),(0.,4.,0.)]])
        wings=np.asarray([(0.,0.,8.),(3.,0.,8.),(0.,3.,8.),
                          (0.,0.,1.),(3.,0.,1.),(0.,3.,1.)])
        outcome=screen_category(wings,[(0,1,2),(3,4,5)],[support],np)
        self.assertTrue(outcome["under_threshold"])
        self.assertEqual(outcome["distance_interpretation"],"FIRST_WITNESS_NOT_GLOBAL_MINIMUM")
        self.assertGreaterEqual(outcome["first_witness_distance_cm"],1.)

if __name__=="__main__":
    unittest.main()
