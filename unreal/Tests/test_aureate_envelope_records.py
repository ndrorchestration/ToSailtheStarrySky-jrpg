"""Tests for the pure native-snapshot -> verifier-config converter.

Snapshots here are SYNTHETIC. They exercise conversion and fail-closed rules;
they say nothing about the real Aureate Wake or any native map.
"""
import copy
import importlib.util
import itertools
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Tools"))
import aureate_envelope_records as rec  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "aureate_swept_clearance", ROOT / "ArtSource" / "ShipReview" / "aureate_swept_clearance.py")
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

SHA_A = "a" * 64
SHA_B = "b" * 64
IDQ = [1.0, 0.0, 0.0, 0.0]


def world_aabb(loc, quat, scale, origin, extent):
    """Independent engine-style AABB: transform all 8 corners of the local box."""
    axes = sc.quat_axes(tuple(quat))  # world-space images of local x, y, z
    pts = []
    for sx, sy, sz in itertools.product((-1, 1), repeat=3):
        local = [origin[i] + (sx, sy, sz)[i] * extent[i] for i in range(3)]
        local = [local[i] * scale[i] for i in range(3)]
        pts.append([loc[i] + sum(axes[j][i] * local[j] for j in range(3)) for i in range(3)])
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return {"origin": [(l + h) / 2 for l, h in zip(lo, hi)],
            "extent": [(h - l) / 2 for l, h in zip(lo, hi)]}


def actor(label, loc, quat, scale, origin, extent):
    return {"label": label, "location": list(loc), "rotation_quat": list(quat),
            "scale": list(scale),
            "local_bounds": {"origin": list(origin), "extent": list(extent)},
            "world_aabb": world_aabb(loc, quat, scale, origin, extent)}


def snapshot(form, sha, wing_rot_deg, wing_y=112.0):
    q = list(sc.quat_from_axis_angle((1, 0, 0), wing_rot_deg))
    qn = list(sc.quat_from_axis_angle((1, 0, 0), -wing_rot_deg))
    yaw = list(sc.quat_from_axis_angle((0, 0, 1), 20))
    actors = [
        actor("V4_NONCANONICAL_SHARED_PEARL_HULL_PROXY", (0, 0, 0), IDQ, (1, 1, 1), (0, 0, 0), (300, 100, 50)),
        actor("V4_NONCANONICAL_SHARED_HULL_CINEMATIC_V4_TRIM", (0, 0, 0), IDQ, (1, 1, 1), (0, 0, 0), (290, 95, 45)),
        actor("V4_NONCANONICAL_FORWARD_GEODESIC_GLASS_DOME_REVIEW", (170, 0, 133), yaw, (1, 1, 1), (3, 0, 5), (40, 40, 30)),
        actor("V4_NONCANONICAL_CENTRAL_CURVED_QUARTERS_REVIEW", (0, 0, 60), IDQ, (1.5, 1, 1), (10, 0, 0), (80, 50, 20)),
        actor("V4_NONCANONICAL_FORWARD_OBSERVATION_DECK_PROXY", (320, 0, 55), IDQ, (1.65, .68, .07), (0, 0, 0), (100, 100, 100)),
    ]
    for ident, (x, side) in {"FORE_PORT": (155, -1), "FORE_STARBOARD": (155, 1),
                             "AFT_PORT": (-180, -1), "AFT_STARBOARD": (-180, 1)}.items():
        quat = q if side > 0 else qn
        actors.append(actor(f"V4_NONCANONICAL_{ident}_AUTHORED_LEAF_280CM_REVIEW",
                            (x, side * wing_y, 48), quat, (1, 1, 1), (0, side * 60, 0), (30, 60, 1)))
    return {"schema": rec.SNAPSHOT_SCHEMA, "ue_version": "5.8.4", "map_path": "/Game/TEST",
            "map_sha256": sha, "form": form, "units": "cm", "actors": actors}


def pair():
    return snapshot("Skybourne", SHA_A, 0.0), snapshot("Submersible", SHA_B, 80.0)


def label_of(snap, token):
    return next(a for a in snap["actors"] if token in a["label"])


class ConversionTests(unittest.TestCase):
    def test_roundtrip_verifies_clear(self):
        a, b = pair()
        cfg = rec.build_config(a, b, required_clearance=0.0)
        self.assertTrue(cfg["provisional"])
        self.assertEqual(cfg["transition"], {"from": "Skybourne", "to": "Submersible"})
        self.assertEqual(cfg["provenance"]["from_map_sha256"], SHA_A)
        result = sc.verify(json.loads(json.dumps(cfg)))
        self.assertEqual(result["verdict"], sc.V_CLEAR, result)

    def test_converted_config_rejects_wing_driven_through_hull(self):
        a, b = pair()
        for ident in rec.WING_IDENTITIES:
            label_of(b, ident)["location"][1] = 0.0
            lab = label_of(b, ident)
            lab["world_aabb"] = world_aabb(lab["location"], lab["rotation_quat"], lab["scale"],
                                           lab["local_bounds"]["origin"], lab["local_bounds"]["extent"])
        cfg = rec.build_config(a, b, required_clearance=0.0)
        self.assertNotEqual(sc.verify(cfg)["verdict"], sc.V_CLEAR)

    def test_rotated_scaled_obstacle_center_includes_scaled_rotated_offset(self):
        a, b = pair()
        cfg = rec.build_config(a, b, required_clearance=0.0)
        bridge = next(o for o in cfg["obstacles"] if o["role"] == "bridge")["parts"][0]
        q = tuple(bridge["rotation_quat"])
        expect = rec._rotate(q, (3.0, 0.0, 5.0))
        for got, base, off in zip(bridge["center"], (170, 0, 133), expect):
            self.assertAlmostEqual(got, base + off, places=9)
        quarters = next(o for o in cfg["obstacles"] if o["role"] == "quarters")["parts"][0]
        self.assertAlmostEqual(quarters["half_extents"][0], 120.0)
        self.assertAlmostEqual(quarters["center"][0], 15.0)  # origin 10 * scale 1.5

    def test_hull_role_has_two_parts_and_all_roles_present(self):
        a, b = pair()
        cfg = rec.build_config(a, b, required_clearance=0.0)
        roles = {o["role"]: len(o["parts"]) for o in cfg["obstacles"]}
        self.assertEqual(roles, {"hull": 2, "bridge": 1, "quarters": 1, "deck": 1})
        self.assertEqual([w["identity"] for w in cfg["wings"]], list(rec.WING_IDENTITIES))

    def test_wing_parts_stay_local_and_unrotated(self):
        a, b = pair()
        cfg = rec.build_config(a, b, required_clearance=0.0)
        for w in cfg["wings"]:
            self.assertNotIn("rotation_quat", w["parts"][0])
            self.assertEqual(w["parts"][0]["half_extents"], [30.0, 60.0, 1.0])


class FailClosedTests(unittest.TestCase):
    def assertRefused(self, mutate, **kw):
        a, b = pair()
        mutate(a, b)
        with self.assertRaises(rec.EnvelopeError):
            rec.build_config(a, b, required_clearance=kw.pop("clearance", 0.0), **kw)

    def test_wrong_schema(self):
        self.assertRefused(lambda a, b: a.update(schema="nope"))

    def test_units_not_cm(self):
        self.assertRefused(lambda a, b: b.update(units="m"))

    def test_bad_sha(self):
        self.assertRefused(lambda a, b: a.update(map_sha256="XYZ"))
        self.assertRefused(lambda a, b: b.pop("map_sha256"))

    def test_same_form(self):
        self.assertRefused(lambda a, b: b.update(form="Skybourne"))

    def test_missing_wing(self):
        self.assertRefused(lambda a, b: b["actors"].remove(label_of(b, "AFT_PORT")))

    def test_duplicate_label_is_ambiguous(self):
        self.assertRefused(lambda a, b: a["actors"].append(copy.deepcopy(label_of(a, "FORE_PORT"))))

    def test_missing_obstacle_role(self):
        self.assertRefused(lambda a, b: a["actors"].remove(label_of(a, "FORWARD_OBSERVATION_DECK")))

    def test_non_finite_number(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT")["location"].__setitem__(0, float("nan")))
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT")["location"].__setitem__(0, float("inf")))

    def test_bool_is_not_a_number(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT")["location"].__setitem__(0, True))

    def test_non_unit_quaternion(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT").update(rotation_quat=[2.0, 0, 0, 0]))

    def test_mirrored_or_zero_scale(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT").update(scale=[-1, 1, 1]))
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT").update(scale=[0, 1, 1]))

    def test_non_positive_extent(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT")["local_bounds"].update(extent=[0, 1, 1]))

    def test_obstacle_moved_between_forms(self):
        def mutate(a, b):
            act = label_of(b, "SHARED_PEARL_HULL")
            act["location"][0] += 0.5
            act["world_aabb"] = world_aabb(act["location"], act["rotation_quat"], act["scale"],
                                           act["local_bounds"]["origin"], act["local_bounds"]["extent"])
        self.assertRefused(mutate)

    def test_wing_mesh_changed_between_forms(self):
        def mutate(a, b):
            act = label_of(b, "FORE_PORT")
            act["local_bounds"]["extent"][0] += 1.0
            act["world_aabb"] = world_aabb(act["location"], act["rotation_quat"], act["scale"],
                                           act["local_bounds"]["origin"], act["local_bounds"]["extent"])
        self.assertRefused(mutate)

    def test_engine_aabb_disagreement_refused(self):
        self.assertRefused(lambda a, b: label_of(a, "FORE_PORT")["world_aabb"]["origin"].__setitem__(2, 60.0))

    def test_engine_aabb_missing_refused(self):
        self.assertRefused(lambda a, b: label_of(b, "FORE_PORT").pop("world_aabb"))

    def test_wrong_quaternion_convention_is_caught_by_self_check(self):
        # A UE-ordered (x,y,z,w) quaternion fed where [w,x,y,z] is expected must not pass.
        def mutate(a, b):
            w, x, y, z = label_of(b, "FORE_STARBOARD")["rotation_quat"]
            label_of(b, "FORE_STARBOARD")["rotation_quat"] = [x, y, z, w]
        self.assertRefused(mutate)

    def test_negative_or_bad_clearance(self):
        for bad in (-1.0, float("nan"), True, "5"):
            a, b = pair()
            with self.assertRaises(rec.EnvelopeError):
                rec.build_config(a, b, required_clearance=bad)

    def test_role_with_no_tokens(self):
        a, b = pair()
        roles = dict(rec.DEFAULT_ROLE_LABELS, bridge=())
        with self.assertRaises(rec.EnvelopeError):
            rec.build_config(a, b, required_clearance=0.0, role_labels=roles)


if __name__ == "__main__":
    unittest.main()
