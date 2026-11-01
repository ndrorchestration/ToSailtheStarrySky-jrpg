"""Regression cases for exact triangle surface distances and fail-closed root screen."""
from __future__ import annotations
import math
import unittest
from aureate_triangle_narrowphase import (
    triangle_triangle_sq,nearest_surface,segment_segment_sq,point_triangle_sq,
    squared_box_distance,
)

TRI=((0.,0.,0.),(4.,0.,0.),(0.,4.,0.))

class TriangleNarrowphaseTests(unittest.TestCase):
    def test_parallel_triangles(self):
        other=tuple((x,y,5.) for x,y,_ in TRI)
        self.assertAlmostEqual(math.sqrt(triangle_triangle_sq(TRI,other)),5.)

    def test_edge_piercing_interior(self):
        other=((1.,1.,-2.),(1.,1.,2.),(2.,2.,1.))
        self.assertAlmostEqual(triangle_triangle_sq(TRI,other),0.)

    def test_coplanar_overlap(self):
        other=((1.,1.,0.),(1.5,1.,0.),(1.,1.5,0.))
        self.assertAlmostEqual(triangle_triangle_sq(TRI,other),0.)

    def test_coplanar_disjoint(self):
        other=((10.,10.,0.),(14.,10.,0.),(10.,14.,0.))
        self.assertGreater(triangle_triangle_sq(TRI,other),1.)

    def test_touching_vertex(self):
        other=((0.,0.,0.),(4.,0.,5.),(0.,4.,5.))
        self.assertAlmostEqual(triangle_triangle_sq(TRI,other),0.)

    def test_degenerate_triangles_safe(self):
        deg=((1.,1.,5.),(1.,1.,5.),(1.,1.,5.))
        self.assertAlmostEqual(triangle_triangle_sq(TRI,deg),25.)

    def test_segments_cross(self):
        self.assertAlmostEqual(segment_segment_sq((-1.,0.,0.),(1.,0.,0.),
                                                  (0.,-1.,0.),(0.,1.,0.)),0.)

    def test_point_inside_triangle_plane_projection(self):
        self.assertAlmostEqual(point_triangle_sq((1.,1.,3.),TRI),9.)

    def test_axis_box_separation(self):
        a=((0.,0.,0.),(1.,1.,1.))
        b=((4.,0.,0.),(5.,1.,1.))
        self.assertAlmostEqual(squared_box_distance(a,b),9.)

    def test_nearest_surface_review_overlap(self):
        body=[(0.,0.,0.),(4.,0.,0.),(0.,4.,0.)]
        wing=[(1.,1.,3.),(2.,1.,3.),(1.,2.,3.)]
        result=nearest_surface(wing,[(0,1,2)],body,[(0,1,2)])
        self.assertAlmostEqual(result["min_surface_cm_among_aabb_candidates"],3.)
        self.assertTrue(result["below_threshold"])
        self.assertEqual(result["triangle_pairs_narrow_phase_checked"],1)

    def test_hypothesized_joint_pair_exclusion_keeps_primary_hold(self):
        body=[(0.,0.,0.),(4.,0.,0.),(0.,4.,0.)]
        wing=[(1.,1.,3.),(2.,1.,3.),(1.,2.,3.)]
        all_triangles=nearest_surface(wing,[(0,1,2)],body,[(0,1,2)])
        other_triangles=nearest_surface(
            wing,[(0,1,2)],body,[(0,1,2)],
            exclude_pair=lambda wi,bi: wi==0 and bi==0)
        self.assertTrue(all_triangles["below_threshold"])
        self.assertFalse(other_triangles["below_threshold"])
        self.assertIsNone(other_triangles["min_surface_cm_among_aabb_candidates"])
        self.assertEqual(other_triangles["excluded_candidate_triangle_pairs"],1)

    def test_far_is_screen_only_not_exact_global_distance(self):
        body=[(0.,0.,0.),(4.,0.,0.),(0.,4.,0.)]
        wing=[(101.,1.,3.),(102.,1.,3.),(101.,2.,3.)]
        result=nearest_surface(wing,[(0,1,2)],body,[(0,1,2)])
        self.assertIsNone(result["min_surface_cm_among_aabb_candidates"])
        self.assertFalse(result["below_threshold"])

    def test_broad_phase_vs_bruteforce_deterministic_triangles(self):
        # AABB pruning may omit distant pairs but must not miss a pair that
        # genuinely lies within the 10 cm surface exclusion distance.
        import random
        rand=random.Random(34021)
        for case in range(15):
            p=[tuple(rand.uniform(-25,25) for _ in range(3)) for _ in range(24)]
            q=[tuple(rand.uniform(-25,25) for _ in range(3)) for _ in range(24)]
            faces=[(i,i+1,i+2) for i in range(0,24,3)]
            actual=nearest_surface(p,faces,q,faces)
            exhaustive=min(triangle_triangle_sq(tuple(p[i] for i in a),
                                                tuple(q[j] for j in b))
                           for a in faces for b in faces)
            if exhaustive < 100.:
                self.assertIsNotNone(actual["min_surface_cm_among_aabb_candidates"])
                self.assertAlmostEqual(
                    actual["min_surface_cm_among_aabb_candidates"]**2,
                    exhaustive,places=6)
            else:
                self.assertFalse(actual["below_threshold"])

    def test_invalid_clearance_threshold(self):
        with self.assertRaises(ValueError):
            nearest_surface([],[],[],[],threshold_cm=0.)

if __name__=="__main__":
    unittest.main()
