"""Cross-check the swept-clearance verifier against the PR #747 AABB audit.

Anchors the verifier to independent code: #747's `calculate` and its in-repo box
fixture (extracted there from SHA-pinned private GLBs). These are conservative
review envelopes, not native Unreal collision proof, and nothing here approves
any rotation angle. Skips cleanly when the #747 audit module is not present.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

_spec = importlib.util.spec_from_file_location(
    "aureate_swept_clearance", ROOT / "ArtSource" / "ShipReview" / "aureate_swept_clearance.py")
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

try:
    import audit_aureate_v4_habitation_envelopes as study
    import test_aureate_v4_habitation_clearance_envelopes as fx
    HAVE_747 = True
except ImportError:  # branch not stacked on #747
    HAVE_747 = False

IDENT = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
BUDGET = (20, 2_000_000)


def _part(box, pivot=(0.0, 0.0, 0.0)):
    lo, hi = box
    return sc.Part(tuple((l + h) / 2 - p for l, h, p in zip(lo, hi, pivot)),
                   tuple((h - l) / 2 for l, h in zip(lo, hi)))


@unittest.skipUnless(HAVE_747, "PR #747 audit module not present on this branch")
class Crosscheck747Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = (("bridge", fx.BRIDGE), ("quarters", fx.QUARTERS))
        cls.theirs = study.calculate(fx.BRIDGE, fx.QUARTERS, fx.WING)
        cls.pivot = tuple(study.PIVOT)
        cls.aabb_wings = {}
        cls.obb_wings = {}
        lo = tuple(min(p[i] for p in fx.WING) for i in range(3))
        hi = tuple(max(p[i] for p in fx.WING) for i in range(3))
        for name, (loc, yaw, roll) in study.FORE_WINGS.items():
            box = study.wing_box(fx.WING, loc, yaw, roll)
            cls.aabb_wings[name] = sc.Body(name, [_part(box)], IDENT, IDENT)
            q = sc._quat_mul(sc.quat_from_axis_angle((0, 0, 1), yaw),
                             sc.quat_from_axis_angle((1, 0, 0), roll))
            pose = (tuple(loc), q, (1.0, 1.0, 1.0))
            cls.obb_wings[name] = sc.Body(name, [_part((lo, hi))], pose, pose)

    def habitat(self, name, corners, yaw_deg):
        rest = study.aabb(study.add(p, study.ORIGINS[name]) for p in corners)
        q = sc.quat_from_axis_angle((0, 0, 1), yaw_deg)
        return sc.Body(name, [_part(rest, self.pivot)],
                       (self.pivot, (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                       (self.pivot, q, (1.0, 1.0, 1.0)))

    def clear(self, name, corners, wing, yaw_deg, clearance=0.0):
        hab = self.habitat(name, corners, yaw_deg)
        return sc.check_pair(hab, wing, clearance, *BUDGET)["verdict"] == sc.V_CLEAR

    def first_contact(self, name, corners, wing, sign):
        if self.clear(name, corners, wing, sign * 17.5):
            return None
        lo, hi = 0.0, 17.5
        for _ in range(40):
            mid = (lo + hi) / 2
            if self.clear(name, corners, wing, sign * mid):
                lo = mid
            else:
                hi = mid
        return hi

    def brute_contact(self, name, corners, wing, sign, step=0.01):
        for i in range(int(17.5 / step) + 1):
            hab = self.habitat(name, corners, sign * i * step)
            end = sc.Body(hab.name, hab.parts, hab.pose_to, hab.pose_to)
            if sc._bodies_intersect(end, wing, 0.0, 0.0):
                return i * step
        return None

    def test_rest_lateral_gaps_match_747_exactly(self):
        for name, corners in self.cases:
            gap = self.theirs["fore_wing_envelope_review"]["0.0"][name]["FORE_PORT"]["axis_separations_cm"][1]
            wing = self.aabb_wings["FORE_PORT"]
            self.assertTrue(self.clear(name, corners, wing, 0.0, gap - 0.01), name)
            self.assertFalse(self.clear(name, corners, wing, 0.0, gap + 0.01), name)

    def test_aabb_wing_contact_is_never_earlier_than_747_and_close(self):
        reported = self.theirs["first_conservative_aabb_overlap_magnitude_deg_not_a_safe_limit"]
        for side, sign in (("FORE_PORT", -1), ("FORE_STARBOARD", 1)):
            for name, corners in self.cases:
                mine = self.first_contact(name, corners, self.aabb_wings[side], sign)
                ours = reported[side][name]
                # #747 boxes the rotated habitat; an exact oriented box can only touch later.
                self.assertGreaterEqual(mine + 1e-9, ours, (side, name))
                self.assertLess(mine - ours, 1.0, (side, name))

    def test_sweep_agrees_with_dense_brute_force_and_errs_conservative(self):
        for side, sign in (("FORE_PORT", -1), ("FORE_STARBOARD", 1)):
            for name, corners in self.cases:
                wing = self.aabb_wings[side]
                swept = self.first_contact(name, corners, wing, sign)
                brute = self.brute_contact(name, corners, wing, sign)
                self.assertIsNotNone(brute)
                self.assertLessEqual(swept, brute + 1e-9, (side, name))
                self.assertLess(brute - swept, 0.02, (side, name))

    def test_oriented_wing_never_contacts_earlier_than_aabb_wing(self):
        for side, sign in (("FORE_PORT", -1), ("FORE_STARBOARD", 1)):
            for name, corners in self.cases:
                loose = self.first_contact(name, corners, self.aabb_wings[side], sign)
                tight = self.first_contact(name, corners, self.obb_wings[side], sign)
                self.assertGreaterEqual(tight + 1e-9, loose, (side, name))

    def test_temporary_17_5_degree_pivot_yaw_is_rejected_under_every_envelope(self):
        for wings in (self.aabb_wings, self.obb_wings):
            for side, sign in (("FORE_PORT", -1), ("FORE_STARBOARD", 1)):
                for name, corners in self.cases:
                    self.assertFalse(self.clear(name, corners, wings[side], sign * 17.5), (side, name))


if __name__ == "__main__":
    unittest.main()
