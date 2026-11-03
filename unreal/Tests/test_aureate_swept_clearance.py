"""Behavioural tests for the fail-closed swept-clearance verifier.

Review tooling only: these tests prove properties of the verifier, not of the
Aureate Wake. No test here is evidence about native Unreal geometry.
"""
import copy
import importlib.util
import json
import random
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "ArtSource" / "ShipReview"
MODULE = ART / "aureate_swept_clearance.py"
EXAMPLE = ART / "aureate_swept_clearance_example_SYNTHETIC.json"

_spec = importlib.util.spec_from_file_location("aureate_swept_clearance", MODULE)
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

IDQ = [1, 0, 0, 0]


def box(center, half, quat=None):
    part = {"center": list(center), "half_extents": list(half)}
    if quat is not None:
        part["rotation_quat"] = list(quat)
    return part


def pose(position, quat=IDQ, scale=(1, 1, 1)):
    return {"position": list(position), "rotation_quat": list(quat), "scale": list(scale)}


def base_config(clearance=5.0, **sweep):
    """Everything far apart and static: a CLEAR baseline to mutate per test."""
    far = {"hull": 2000, "bridge": 3000, "quarters": 4000, "deck": 5000}
    obstacles = [{"role": r, "parts": [box((0, 0, z), (10, 10, 10))]} for r, z in far.items()]
    spots = {"FORE_PORT": (400, -400, 0), "FORE_STARBOARD": (400, 400, 0),
             "AFT_PORT": (-400, -400, 0), "AFT_STARBOARD": (-400, 400, 0)}
    wings = [{"identity": n, "parts": [box((0, 0, 0), (20, 20, 2))],
              "pose_from": pose(p), "pose_to": pose(p)} for n, p in spots.items()]
    cfg = {"schema_version": 1, "provisional": True, "units": "cm",
           "required_clearance": clearance, "obstacles": obstacles, "wings": wings}
    if sweep:
        cfg["sweep"] = sweep
    return cfg


def set_obstacle(cfg, role, parts):
    for o in cfg["obstacles"]:
        if o["role"] == role:
            o["parts"] = parts
            return
    raise AssertionError(role)


def wing(cfg, name):
    return next(w for w in cfg["wings"] if w["identity"] == name)


def pair(result, a, b):
    return next(p for p in result["pairs"] if p["a"] == a and p["b"] == b)


class ObbTests(unittest.TestCase):
    AX = sc.quat_axes((1.0, 0.0, 0.0, 0.0))

    def hit(self, cb, half_b=(1, 1, 1), qb=(1.0, 0.0, 0.0, 0.0)):
        return sc.obb_intersect((0, 0, 0), self.AX, (1, 1, 1), cb, sc.quat_axes(qb), half_b)

    def test_overlap_separation_and_touching(self):
        self.assertTrue(self.hit((1.5, 0, 0)))
        self.assertFalse(self.hit((2.5, 0, 0)))
        self.assertTrue(self.hit((2.0, 0, 0)), "touching must count as a hit (fail closed)")

    def test_rotated_box_extent(self):
        q45 = sc.quat_from_axis_angle((0, 0, 1), 45)
        self.assertTrue(self.hit((2.3, 0, 0), qb=q45))   # 1 + sqrt(2) = 2.414
        self.assertFalse(self.hit((2.5, 0, 0), qb=q45))

    def test_edge_edge_case_needs_cross_axes(self):
        # Two boxes rotated about different axes separated only by an edge-edge axis.
        qa = sc.quat_from_axis_angle((1, 0, 0), 45)
        qb = sc.quat_from_axis_angle((0, 1, 0), 45)
        a_axes, b_axes = sc.quat_axes(qa), sc.quat_axes(qb)
        far = sc.obb_intersect((0, 0, 0), a_axes, (1, 1, 1), (2.9, 0, 2.9), b_axes, (1, 1, 1))
        near = sc.obb_intersect((0, 0, 0), a_axes, (1, 1, 1), (0.5, 0.5, 0.5), b_axes, (1, 1, 1))
        self.assertFalse(far)
        self.assertTrue(near)


class VerdictTests(unittest.TestCase):
    def test_static_baseline_is_clear(self):
        self.assertEqual(sc.verify(base_config())["verdict"], sc.V_CLEAR)

    def test_endpoint_only_check_would_miss_thin_obstacle_but_sweep_rejects(self):
        cfg = base_config()
        set_obstacle(cfg, "deck", [box((0, 0, 0), (1, 50, 50))])  # thin plate
        w = wing(cfg, "FORE_PORT")
        w["pose_from"] = pose((-200, 0, 0))
        w["pose_to"] = pose((200, 0, 0))
        model = sc.parse_config(cfg)
        wb, plate = model["wings"]["FORE_PORT"], model["obstacles"]["deck"]
        self.assertFalse(sc._bodies_intersect(wb, plate, 0.0, 0.0), "start must be clear")
        self.assertFalse(sc._bodies_intersect(wb, plate, 1.0, 0.0), "end must be clear")
        result = sc.verify(cfg)
        self.assertEqual(result["verdict"], sc.V_REJECT)
        self.assertEqual(pair(result, "FORE_PORT", "deck")["verdict"], sc.V_REJECT)

    def test_rotation_sweep_through_obstacle_with_clear_endpoints(self):
        cfg = base_config()
        set_obstacle(cfg, "deck", [box((0, 100, 0), (10, 10, 10))])
        w = wing(cfg, "FORE_PORT")
        w["parts"] = [box((100, 0, 0), (90, 5, 5))]  # bar along +x from the pivot
        w["pose_from"] = pose((0, 0, 0))
        w["pose_to"] = pose((0, 0, 0), sc.quat_from_axis_angle((0, 0, 1), 170))
        model = sc.parse_config(cfg)
        wb, obs = model["wings"]["FORE_PORT"], model["obstacles"]["deck"]
        self.assertFalse(sc._bodies_intersect(wb, obs, 0.0, 0.0))
        self.assertFalse(sc._bodies_intersect(wb, obs, 1.0, 0.0))
        self.assertEqual(pair(sc.verify(cfg), "FORE_PORT", "deck")["verdict"], sc.V_REJECT)

    def test_rotation_that_stays_clear_is_proven_clear(self):
        cfg = base_config()
        set_obstacle(cfg, "deck", [box((0, 100, 0), (10, 10, 10))])
        w = wing(cfg, "FORE_PORT")
        w["parts"] = [box((100, 0, 0), (90, 5, 5))]
        w["pose_from"] = pose((0, 0, 0))
        w["pose_to"] = pose((0, 0, 0), sc.quat_from_axis_angle((0, 0, 1), 30))
        self.assertEqual(pair(sc.verify(cfg), "FORE_PORT", "deck")["verdict"], sc.V_CLEAR)

    def test_required_clearance_margin_is_enforced(self):
        def build(clearance):
            cfg = base_config(clearance)
            wing(cfg, "FORE_PORT")["parts"] = [box((0, 0, 0), (10, 10, 10))]
            wing(cfg, "FORE_PORT")["pose_from"] = pose((0, 0, 0))
            wing(cfg, "FORE_PORT")["pose_to"] = pose((0, 0, 0))
            set_obstacle(cfg, "deck", [box((30, 0, 0), (10, 10, 10))])  # 10 cm gap
            return cfg
        self.assertEqual(sc.verify(build(5.0))["verdict"], sc.V_CLEAR)
        self.assertEqual(sc.verify(build(15.0))["verdict"], sc.V_REJECT)

    def test_refinement_proves_what_a_coarse_pass_cannot(self):
        def build(max_depth):
            cfg = base_config(0.0, max_depth=max_depth)
            set_obstacle(cfg, "deck", [box((0, 0, 0), (10, 10, 10))])
            w = wing(cfg, "FORE_PORT")
            w["pose_from"] = pose((-200, 100, 0))
            w["pose_to"] = pose((200, 100, 0))  # true gap to the box is 70 cm
            return cfg
        coarse = sc.verify(build(0))
        self.assertEqual(coarse["verdict"], sc.V_UNPROVEN)
        self.assertEqual(sc.verify(build(16))["verdict"], sc.V_CLEAR)

    def test_budget_exhaustion_fails_closed(self):
        cfg = base_config(0.0, max_evals=3)
        set_obstacle(cfg, "deck", [box((0, 0, 0), (10, 10, 10))])
        w = wing(cfg, "FORE_PORT")
        w["pose_from"] = pose((-200, 100, 0))
        w["pose_to"] = pose((200, 100, 0))
        self.assertEqual(pair(sc.verify(cfg), "FORE_PORT", "deck")["verdict"], sc.V_UNPROVEN)
        self.assertNotEqual(sc.verify(cfg)["verdict"], sc.V_CLEAR)

    def test_wings_crossing_each_other_are_rejected(self):
        cfg = base_config()
        a, b = wing(cfg, "FORE_PORT"), wing(cfg, "FORE_STARBOARD")
        a["pose_from"], a["pose_to"] = pose((0, -100, 500)), pose((0, 100, 500))
        b["pose_from"], b["pose_to"] = pose((0, 100, 500)), pose((0, -100, 500))
        result = sc.verify(cfg)
        self.assertEqual(result["verdict"], sc.V_REJECT)
        self.assertEqual(pair(result, "FORE_PORT", "FORE_STARBOARD")["verdict"], sc.V_REJECT)

    def test_scale_change_toward_obstacle_is_covered(self):
        cfg = base_config(0.0)
        set_obstacle(cfg, "deck", [box((100, 0, 0), (5, 5, 5))])
        w = wing(cfg, "FORE_PORT")
        w["parts"] = [box((0, 0, 0), (10, 10, 10))]
        w["pose_from"] = pose((0, 0, 0), scale=(1, 1, 1))
        w["pose_to"] = pose((0, 0, 0), scale=(20, 1, 1))  # grows to 200 cm along x
        self.assertEqual(pair(sc.verify(cfg), "FORE_PORT", "deck")["verdict"], sc.V_REJECT)

    def test_result_is_deterministic(self):
        cfg = base_config()
        wing(cfg, "FORE_PORT")["pose_to"] = pose((10, 20, 30), sc.quat_from_axis_angle((1, 1, 0), 33))
        first = json.dumps(sc.verify(copy.deepcopy(cfg)), sort_keys=True)
        second = json.dumps(sc.verify(copy.deepcopy(cfg)), sort_keys=True)
        self.assertEqual(first, second)

    def test_every_result_lists_what_was_not_checked(self):
        for result in (sc.verify(base_config()), sc.verify(None)):
            joined = " ".join(result["not_checked"])
            for needle in ("true wing mesh", "creator visual", "structural", "rotating bridge"):
                self.assertIn(needle, joined)


class InvalidInputTests(unittest.TestCase):
    def assert_invalid(self, cfg):
        result = sc.verify(cfg)
        self.assertEqual(result["verdict"], sc.V_INVALID, result.get("reason"))
        self.assertTrue(result["reason"])

    def test_non_object_configs(self):
        for bad in (None, [], "x", 3, {}):
            self.assert_invalid(bad)

    def test_missing_required_obstacle_role(self):
        for role in sc.REQUIRED_OBSTACLE_ROLES:
            cfg = base_config()
            cfg["obstacles"] = [o for o in cfg["obstacles"] if o["role"] != role]
            self.assert_invalid(cfg)

    def test_wing_identity_set_must_be_exact(self):
        cfg = base_config()
        cfg["wings"].pop()
        self.assert_invalid(cfg)
        cfg = base_config()
        cfg["wings"][0]["identity"] = "WING_ONE"
        self.assert_invalid(cfg)
        cfg = base_config()
        cfg["wings"][1]["identity"] = cfg["wings"][0]["identity"]
        self.assert_invalid(cfg)

    def test_non_finite_numbers(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            cfg = base_config()
            wing(cfg, "FORE_PORT")["pose_to"]["position"][0] = bad
            self.assert_invalid(cfg)
            cfg = base_config()
            cfg["required_clearance"] = bad
            self.assert_invalid(cfg)

    def test_degenerate_geometry(self):
        cfg = base_config()
        wing(cfg, "AFT_PORT")["parts"][0]["half_extents"][1] = 0
        self.assert_invalid(cfg)
        cfg = base_config()
        wing(cfg, "AFT_PORT")["pose_from"]["scale"][2] = -1
        self.assert_invalid(cfg)
        cfg = base_config()
        wing(cfg, "AFT_PORT")["pose_from"]["rotation_quat"] = [0, 0, 0, 0]
        self.assert_invalid(cfg)
        cfg = base_config()
        cfg["obstacles"][0]["parts"] = []
        self.assert_invalid(cfg)

    def test_header_fields_are_required_and_strict(self):
        for key, value in (("schema_version", 2), ("provisional", None), ("units", "m"),
                           ("required_clearance", -1), ("required_clearance", True)):
            cfg = base_config()
            cfg[key] = value
            self.assert_invalid(cfg)
        cfg = base_config()
        del cfg["provisional"]
        self.assert_invalid(cfg)

    def test_bad_sweep_parameters(self):
        for sweep in ({"max_depth": -1}, {"max_depth": 31}, {"max_depth": 2.5},
                      {"max_evals": 0}, {"max_depth": True}):
            cfg = base_config()
            cfg["sweep"] = sweep
            self.assert_invalid(cfg)

    def test_rotated_parts_not_allowed_on_moving_wings(self):
        cfg = base_config()
        wing(cfg, "FORE_PORT")["parts"][0]["rotation_quat"] = IDQ
        self.assert_invalid(cfg)


class SoundnessPropertyTests(unittest.TestCase):
    """Seeded randomized check: a CLEAR proof must survive dense brute force."""

    SAMPLES = 700

    @staticmethod
    def random_quat(rng):
        axis = [rng.uniform(-1, 1) for _ in range(3)]
        if sum(a * a for a in axis) < 1e-6:
            axis = [0, 0, 1]
        return sc.quat_from_axis_angle(axis, rng.uniform(-180, 180))

    def test_clear_verdict_is_never_contradicted_by_dense_sampling(self):
        rng = random.Random(20261103)
        counts = {"clear": 0, "not_clear": 0}
        for case in range(60):
            clearance = rng.choice([0.0, 5.0])
            cfg = base_config(clearance, max_depth=12)
            half_w = [rng.uniform(5, 60), rng.uniform(5, 60), rng.uniform(1, 20)]
            w = wing(cfg, "FORE_PORT")
            w["parts"] = [box([rng.uniform(-30, 30) for _ in range(3)], half_w)]
            w["pose_from"] = pose([rng.uniform(-150, 150) for _ in range(3)], self.random_quat(rng),
                                  [rng.uniform(.5, 1.5) for _ in range(3)])
            w["pose_to"] = pose([rng.uniform(-150, 150) for _ in range(3)], self.random_quat(rng),
                                [rng.uniform(.5, 1.5) for _ in range(3)])
            obstacle = box([rng.uniform(-100, 100) for _ in range(3)],
                           [rng.uniform(10, 50) for _ in range(3)],
                           self.random_quat(rng))
            set_obstacle(cfg, "deck", [obstacle])
            result = sc.verify(cfg)
            self.assertNotEqual(result["verdict"], sc.V_INVALID, result.get("reason"))
            verdict = pair(result, "FORE_PORT", "deck")["verdict"]
            model = sc.parse_config(cfg)
            wb, obs = model["wings"]["FORE_PORT"], model["obstacles"]["deck"]
            hit = any(sc._bodies_intersect(wb, obs, i / self.SAMPLES, clearance)
                      for i in range(self.SAMPLES + 1))
            if hit:
                counts["not_clear"] += 1
                self.assertNotEqual(verdict, sc.V_CLEAR, f"unsound CLEAR in case {case}")
            else:
                counts["clear"] += 1
            if verdict == sc.V_CLEAR:
                self.assertFalse(hit, f"unsound CLEAR in case {case}")
        self.assertGreater(counts["clear"], 3, counts)
        self.assertGreater(counts["not_clear"], 3, counts)


class ExampleAndCliTests(unittest.TestCase):
    def test_example_is_marked_synthetic_and_verifies_deterministically(self):
        cfg = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertTrue(cfg["provisional"])
        self.assertIn("SYNTHETIC", cfg["note"])
        self.assertIn("NOT exported from Unreal", cfg["note"])
        first, second = sc.verify(cfg), sc.verify(copy.deepcopy(cfg))
        self.assertEqual(first, second)
        self.assertEqual(first["verdict"], sc.V_CLEAR)
        self.assertTrue(first["provisional_inputs"])

    def test_cli_exit_codes_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.json"
            good.write_text(json.dumps(base_config()), encoding="utf-8")
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            reject = base_config()
            wing(reject, "FORE_PORT")["pose_to"] = pose((0, 0, 2000))  # into the hull envelope
            rej = Path(tmp) / "reject.json"
            rej.write_text(json.dumps(reject), encoding="utf-8")
            self.assertEqual(sc.main(["x", str(good)]), 0)
            self.assertEqual(sc.main(["x", str(bad)]), 1)
            self.assertEqual(sc.main(["x", str(rej)]), 1)
            self.assertEqual(sc.main(["x", str(Path(tmp) / "missing.json")]), 1)
        self.assertEqual(sc.main(["x"]), 2)


if __name__ == "__main__":
    unittest.main()
