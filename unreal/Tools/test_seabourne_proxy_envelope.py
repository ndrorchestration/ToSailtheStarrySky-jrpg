"""Engine-free negative fixtures for BasicShapes cube endpoint-yaw AABB only."""
import unittest
from audit_seabourne_proxy_envelope import (
    YAW_SAMPLES, analyze, lock_source, sail, separation
)


class SeabourneProxyEnvelopeTests(unittest.TestCase):
    def test_source_locked_four_station_geometry(self):
        self.assertEqual(lock_source(),(300.,105.,-90.,-285.))

    def test_sampled_endpoint_proxy_boxes_are_clear(self):
        result=analyze(lock_source())
        self.assertEqual(result["tested_wings"],4)
        self.assertEqual(result["evaluated_box_pairs"],1590)
        self.assertEqual(len(result["yaw_samples_degrees"]),15)
        self.assertGreater(result["minimum_proxy_aabb_gap_cm"],0.)
        self.assertEqual(result["status"],
                         "SOURCE_LOCKED_BASIC_CUBE_ENDPOINT_YAW_SAMPLES_AABB_CLEAR")

    def test_no_native_or_physically_verified_clearance_claim(self):
        report=analyze(lock_source())
        for tag in ("actual_mesh_geometry_evaluated",
                    "actual_native_unreal_evaluated",
                    "swept_deployment_or_continuous_yaw_verified",
                    "verified_collision_clearance",
                    "wind_propulsion_verified","creator_approved"):
            self.assertIs(report[tag],False)

    def test_collapsed_stations_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"distinct stations"):
            analyze((300.,105.,105.,-285.))

    def test_obstacle_near_bridge_intersection_rejected(self):
        with self.assertRaisesRegex(ValueError,"proxy box overlap or contact"):
            analyze(lock_source(),bridge_z=270.)

    def test_unapproved_yaw_or_missing_samples_rejected(self):
        for samples in ((),(36.,),(-36.,),(float("nan"),)):
            with self.subTest(samples=samples):
                with self.assertRaisesRegex(ValueError,"sampled bounds"):
                    analyze(lock_source(),samples=samples)

    def test_opposing_trim_rotations_do_not_collapse_adjacent_proxies(self):
        roots=lock_source()
        self.assertGreater(separation(sail(roots[0],35.),sail(roots[1],-35.)),0.)
        self.assertGreater(separation(sail(roots[2],-35.),sail(roots[3],35.)),0.)


if __name__=="__main__":
    unittest.main()
