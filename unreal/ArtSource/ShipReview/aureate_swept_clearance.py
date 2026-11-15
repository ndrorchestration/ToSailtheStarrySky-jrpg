#!/usr/bin/env python3
"""Fail-closed swept-clearance verifier for Aureate Wake wing transitions.

REVIEW TOOLING ONLY. This is a conservative, deterministic, dependency-free
reference model. It does not read Unreal assets, does not prove anything about
final art, and a CLEAR verdict means only: "under the supplied oriented-box
envelopes and the stated interpolation model, no wing envelope comes within the
required clearance of any obstacle envelope or of another wing envelope at any
time during the transition". It grants no canon, art, physics, or release
approval.

Interpolation model (mirrors AAureateWakePreviewActor::Interpolate in the
native source): location = Lerp, rotation = Slerp (normalized), scale = Lerp,
all in the ship frame. The native smoothstep time easing is a monotone
reparameterization of [0, 1] and does not change the swept set, so it is not
modelled.

Method (sound, i.e. never reports CLEAR for a violating input, within float
rounding): adaptive interval refinement over t in [0, 1]. For a segment
[t0, t1] every point of a moving body stays within a computed bound B of its
t0 pose (translation + rotation arc + scale change). If the t0 pose is
separated from the other body by clearance + B_a + B_b (obstacles are inflated
per axis, a superset of the Minkowski sum with a ball), the whole segment is
proven clear. Otherwise the segment is bisected. Anything unresolved at the
depth/evaluation budget is FAIL_CLOSED_UNPROVEN, never CLEAR.

Fail-closed rules: any missing/invalid input, missing obstacle role, wrong wing
identity set, non-finite number, non-positive extent or scale, or exhausted
budget yields a non-CLEAR verdict and a non-zero CLI exit status.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

SCHEMA_VERSION = 1
WING_IDENTITIES = ("FORE_PORT", "FORE_STARBOARD", "AFT_PORT", "AFT_STARBOARD")
REQUIRED_OBSTACLE_ROLES = ("hull", "bridge", "quarters", "deck")

V_CLEAR = "CLEAR_UNDER_ENVELOPES"
V_REJECT = "REJECT_CLEARANCE_VIOLATION"
V_UNPROVEN = "FAIL_CLOSED_UNPROVEN"
V_INVALID = "FAIL_CLOSED_INVALID_INPUT"

DEFAULT_MAX_DEPTH = 16
DEFAULT_MAX_EVALS = 400_000
_EPS = 1e-9

NOT_CHECKED = (
    "true wing mesh geometry (oriented-box envelopes only)",
    "membrane deformation or flex during the transition",
    "equivalence of supplied envelopes to the native Unreal meshes",
    "hydrofoils, struts and root-support actors",
    "rotating bridge/quarters assembly",
    "water contact, buoyancy and pressure sealing",
    "structural load path",
    "creator visual or transformation approval",
)


class InvalidInput(ValueError):
    """Raised for any input that cannot be verified; always fails closed."""


# --------------------------------------------------------------------------
# small vector / quaternion helpers (stdlib only)
# --------------------------------------------------------------------------
def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _vec3(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3 or not all(_finite(v) for v in value):
        raise InvalidInput(f"{name} must be three finite numbers")
    return (float(value[0]), float(value[1]), float(value[2]))


def _quat(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 4 or not all(_finite(v) for v in value):
        raise InvalidInput(f"{name} must be four finite numbers [w, x, y, z]")
    norm = math.sqrt(sum(float(v) * float(v) for v in value))
    if norm < 1e-12:
        raise InvalidInput(f"{name} must be a non-zero quaternion")
    return tuple(float(v) / norm for v in value)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    return math.sqrt(_dot(a, a))


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale_vec(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _hadamard(a, b):
    return (a[0] * b[0], a[1] * b[1], a[2] * b[2])


def _lerp3(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def quat_axes(q):
    """Return the three rotation-matrix column vectors (local axes in world)."""
    w, x, y, z = q
    return (
        (1 - 2 * (y * y + z * z), 2 * (x * y + w * z), 2 * (x * z - w * y)),
        (2 * (x * y - w * z), 1 - 2 * (x * x + z * z), 2 * (y * z + w * x)),
        (2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)),
    )


def _rotate(q, v):
    ax = quat_axes(q)
    return (
        ax[0][0] * v[0] + ax[1][0] * v[1] + ax[2][0] * v[2],
        ax[0][1] * v[0] + ax[1][1] * v[1] + ax[2][1] * v[2],
        ax[0][2] * v[0] + ax[1][2] * v[1] + ax[2][2] * v[2],
    )


def _quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def _quat_angle(a, b):
    d = abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3])
    return 2.0 * math.acos(min(1.0, d))


def quat_slerp(a, b, t):
    d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]
    if d < 0.0:  # shortest path, matches normalized FQuat::Slerp behaviour
        b = (-b[0], -b[1], -b[2], -b[3])
        d = -d
    if d > 0.9995:
        out = tuple(a[i] + (b[i] - a[i]) * t for i in range(4))
    else:
        theta = math.acos(max(-1.0, min(1.0, d)))
        s = math.sin(theta)
        wa = math.sin((1 - t) * theta) / s
        wb = math.sin(t * theta) / s
        out = tuple(a[i] * wa + b[i] * wb for i in range(4))
    n = math.sqrt(sum(c * c for c in out))
    return tuple(c / n for c in out)


def quat_from_axis_angle(axis, degrees):
    """Helper for fixtures/tests: right-handed axis-angle -> [w, x, y, z]."""
    n = _norm(axis)
    if n < 1e-12:
        raise InvalidInput("axis must be non-zero")
    h = math.radians(degrees) / 2.0
    s = math.sin(h) / n
    return (math.cos(h), axis[0] * s, axis[1] * s, axis[2] * s)


# --------------------------------------------------------------------------
# oriented-box intersection (separating axis theorem, touching counts as hit)
# --------------------------------------------------------------------------
def obb_intersect(ca, axa, ha, cb, axb, hb):
    R = [[_dot(axa[i], axb[j]) for j in range(3)] for i in range(3)]
    tw = _sub(cb, ca)
    t = [_dot(tw, axa[i]) for i in range(3)]
    A = [[abs(R[i][j]) + _EPS for j in range(3)] for i in range(3)]
    for i in range(3):
        ra = ha[i]
        rb = hb[0] * A[i][0] + hb[1] * A[i][1] + hb[2] * A[i][2]
        if abs(t[i]) > ra + rb:
            return False
    for j in range(3):
        ra = ha[0] * A[0][j] + ha[1] * A[1][j] + ha[2] * A[2][j]
        rb = hb[j]
        if abs(t[0] * R[0][j] + t[1] * R[1][j] + t[2] * R[2][j]) > ra + rb:
            return False
    for i in range(3):
        i1, i2 = (i + 1) % 3, (i + 2) % 3
        for j in range(3):
            j1, j2 = (j + 1) % 3, (j + 2) % 3
            ra = ha[i1] * A[i2][j] + ha[i2] * A[i1][j]
            rb = hb[j1] * A[i][j2] + hb[j2] * A[i][j1]
            if abs(t[i2] * R[i1][j] - t[i1] * R[i2][j]) > ra + rb:
                return False
    return True


# --------------------------------------------------------------------------
# bodies
# --------------------------------------------------------------------------
class Part:
    """Oriented box in its body's local frame."""

    __slots__ = ("center", "half", "quat")

    def __init__(self, center, half, quat=(1.0, 0.0, 0.0, 0.0)):
        self.center = center
        self.half = half
        self.quat = quat


class Body:
    """Rigid body with Lerp/Slerp/Lerp motion between two poses.

    pose = (position, quaternion, scale) in the ship frame. A static body has
    identical poses. Scale is applied in the body's local frame before
    rotation, so parts of a body with non-uniform scale must be axis-aligned
    in that frame (enforced at parse time).
    """

    def __init__(self, name, parts, pose_from, pose_to):
        self.name = name
        self.parts = parts
        self.pose_from = pose_from
        self.pose_to = pose_to
        self.static = pose_from == pose_to
        hx = [0.0, 0.0, 0.0]
        for part in parts:
            for k in range(3):
                hx[k] = max(hx[k], abs(part.center[k]) + part.half[k])
        self._hx = tuple(hx)

    def pose(self, t):
        if self.static:
            return self.pose_from
        p0, q0, s0 = self.pose_from
        p1, q1, s1 = self.pose_to
        return (_lerp3(p0, p1, t), quat_slerp(q0, q1, t), _lerp3(s0, s1, t))

    def world_parts(self, t, inflate=0.0):
        p, q, s = self.pose(t)
        axes_body = quat_axes(q)
        out = []
        for part in self.parts:
            local = _hadamard(s, part.center)
            center = _add(p, _rotate(q, local))
            if part.quat == (1.0, 0.0, 0.0, 0.0):
                axes = axes_body
            else:
                axes = quat_axes(_quat_mul(q, part.quat))
            half = tuple(abs(s[k]) * part.half[k] + inflate for k in range(3))
            out.append((center, axes, half))
        return out

    def motion_bound(self, t0, t1):
        """Upper bound on how far any point moves between poses at t0 and t1."""
        if self.static:
            return 0.0
        p0, q0, s0 = self.pose(t0)
        p1, q1, s1 = self.pose(t1)
        d_pos = _norm(_sub(p1, p0))
        d_ang = _quat_angle(q0, q1)
        radius0 = _norm(_hadamard(s0, self._hx))
        d_scale = _norm(_hadamard(_sub(s1, s0), self._hx))
        return d_pos + d_ang * radius0 + d_scale


def _bodies_intersect(a, b, t, inflate):
    wa = a.world_parts(t)
    wb = b.world_parts(t, inflate)
    for ca, axa, ha in wa:
        for cb, axb, hb in wb:
            if obb_intersect(ca, axa, ha, cb, axb, hb):
                return True
    return False


def check_pair(a, b, clearance, max_depth, max_evals):
    """Verify bodies a and b stay `clearance` apart for all t in [0, 1]."""
    evals = 0
    deepest = 0
    unproven = False

    def probe(t, margin):
        nonlocal evals
        evals += 1
        return _bodies_intersect(a, b, t, margin)

    if probe(1.0, clearance):
        return {"verdict": V_REJECT, "t": 1.0, "evals": evals, "depth": 0}

    stack = [(0.0, 1.0, 0)]
    while stack:
        if evals > max_evals:
            return {"verdict": V_UNPROVEN, "reason": "evaluation budget exhausted",
                    "evals": evals, "depth": deepest}
        t0, t1, depth = stack.pop()
        deepest = max(deepest, depth)
        bound = a.motion_bound(t0, t1) + b.motion_bound(t0, t1)
        if not probe(t0, clearance + bound):
            continue  # whole segment proven clear
        if probe(t0, clearance):
            return {"verdict": V_REJECT, "t": t0, "evals": evals, "depth": depth}
        if depth >= max_depth:
            unproven = True
            continue
        mid = 0.5 * (t0 + t1)
        stack.append((mid, t1, depth + 1))
        stack.append((t0, mid, depth + 1))

    if unproven:
        return {"verdict": V_UNPROVEN, "reason": "depth budget reached with unresolved segment",
                "evals": evals, "depth": deepest}
    return {"verdict": V_CLEAR, "evals": evals, "depth": deepest}


# --------------------------------------------------------------------------
# config parsing and top-level verification
# --------------------------------------------------------------------------
def _parse_pose(value, name):
    if not isinstance(value, dict):
        raise InvalidInput(f"{name} must be an object")
    position = _vec3(value.get("position"), f"{name}.position")
    quat = _quat(value.get("rotation_quat"), f"{name}.rotation_quat")
    scale = _vec3(value.get("scale", [1, 1, 1]), f"{name}.scale")
    if any(s <= 0 for s in scale):
        raise InvalidInput(f"{name}.scale components must be > 0")
    return (position, quat, scale)


def _parse_parts(value, name, allow_rotation):
    if not isinstance(value, list) or not value:
        raise InvalidInput(f"{name} must be a non-empty list of parts")
    parts = []
    for index, raw in enumerate(value):
        label = f"{name}[{index}]"
        if not isinstance(raw, dict):
            raise InvalidInput(f"{label} must be an object")
        center = _vec3(raw.get("center"), f"{label}.center")
        half = _vec3(raw.get("half_extents"), f"{label}.half_extents")
        if any(h <= 0 for h in half):
            raise InvalidInput(f"{label}.half_extents must all be > 0")
        if "rotation_quat" in raw:
            if not allow_rotation:
                raise InvalidInput(f"{label}.rotation_quat is not allowed on moving wing parts")
            quat = _quat(raw["rotation_quat"], f"{label}.rotation_quat")
        else:
            quat = (1.0, 0.0, 0.0, 0.0)
        parts.append(Part(center, half, quat))
    return parts


def parse_config(cfg):
    if not isinstance(cfg, dict):
        raise InvalidInput("config must be an object")
    if cfg.get("schema_version") != SCHEMA_VERSION:
        raise InvalidInput(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(cfg.get("provisional"), bool):
        raise InvalidInput("provisional must be explicitly true or false")
    if cfg.get("units") != "cm":
        raise InvalidInput("units must be 'cm'")
    clearance = cfg.get("required_clearance")
    if not _finite(clearance) or clearance < 0:
        raise InvalidInput("required_clearance must be a finite number >= 0")
    sweep = cfg.get("sweep", {})
    if not isinstance(sweep, dict):
        raise InvalidInput("sweep must be an object")
    max_depth = sweep.get("max_depth", DEFAULT_MAX_DEPTH)
    max_evals = sweep.get("max_evals", DEFAULT_MAX_EVALS)
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or not 0 <= max_depth <= 30:
        raise InvalidInput("sweep.max_depth must be an integer in [0, 30]")
    if not isinstance(max_evals, int) or isinstance(max_evals, bool) or max_evals < 1:
        raise InvalidInput("sweep.max_evals must be a positive integer")

    obstacles_raw = cfg.get("obstacles")
    if not isinstance(obstacles_raw, list):
        raise InvalidInput("obstacles must be a list")
    obstacles = {}
    for raw in obstacles_raw:
        if not isinstance(raw, dict) or not isinstance(raw.get("role"), str):
            raise InvalidInput("each obstacle needs a string role")
        role = raw["role"]
        if role in obstacles:
            raise InvalidInput(f"duplicate obstacle role {role!r}")
        parts = _parse_parts(raw.get("parts"), f"obstacle {role}", allow_rotation=True)
        identity = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
        obstacles[role] = Body(role, parts, identity, identity)
    missing = [r for r in REQUIRED_OBSTACLE_ROLES if r not in obstacles]
    if missing:
        raise InvalidInput(f"missing required obstacle envelope(s): {', '.join(missing)}")

    wings_raw = cfg.get("wings")
    if not isinstance(wings_raw, list):
        raise InvalidInput("wings must be a list")
    identities = [w.get("identity") if isinstance(w, dict) else None for w in wings_raw]
    if sorted(map(str, identities)) != sorted(WING_IDENTITIES) or len(wings_raw) != 4:
        raise InvalidInput("wings must be exactly " + ", ".join(WING_IDENTITIES))
    wings = {}
    for raw in wings_raw:
        name = raw["identity"]
        parts = _parse_parts(raw.get("parts"), f"wing {name}", allow_rotation=False)
        pose_from = _parse_pose(raw.get("pose_from"), f"wing {name}.pose_from")
        pose_to = _parse_pose(raw.get("pose_to"), f"wing {name}.pose_to")
        wings[name] = Body(name, parts, pose_from, pose_to)
    return {
        "clearance": float(clearance),
        "max_depth": max_depth,
        "max_evals": max_evals,
        "obstacles": obstacles,
        "wings": wings,
        "provisional": cfg["provisional"],
        "transition": cfg.get("transition"),
    }


def _invalid_result(message):
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": V_INVALID,
        "reason": message,
        "pairs": [],
        "not_checked": list(NOT_CHECKED),
    }


def verify(cfg):
    """Return a deterministic result dict. Never raises for bad input."""
    try:
        model = parse_config(cfg)
    except InvalidInput as exc:
        return _invalid_result(str(exc))
    except (TypeError, KeyError, AttributeError) as exc:  # malformed shapes
        return _invalid_result(f"malformed config: {exc.__class__.__name__}")

    pairs = []
    wings = [model["wings"][n] for n in WING_IDENTITIES]
    obstacle_roles = sorted(model["obstacles"])
    for wing in wings:
        for role in obstacle_roles:
            result = check_pair(wing, model["obstacles"][role], model["clearance"],
                                model["max_depth"], model["max_evals"])
            result.update({"a": wing.name, "b": role})
            pairs.append(result)
    for i in range(len(wings)):
        for j in range(i + 1, len(wings)):
            result = check_pair(wings[i], wings[j], model["clearance"],
                                model["max_depth"], model["max_evals"])
            result.update({"a": wings[i].name, "b": wings[j].name})
            pairs.append(result)

    verdicts = {p["verdict"] for p in pairs}
    if V_REJECT in verdicts:
        overall = V_REJECT
    elif V_UNPROVEN in verdicts:
        overall = V_UNPROVEN
    else:
        overall = V_CLEAR
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": overall,
        "provisional_inputs": model["provisional"],
        "transition": model["transition"],
        "required_clearance_cm": model["clearance"],
        "interpolation": "location Lerp, rotation Slerp, scale Lerp (ship frame)",
        "pairs": pairs,
        "not_checked": list(NOT_CHECKED),
    }


def main(argv):
    if len(argv) != 2:
        print("usage: aureate_swept_clearance.py CONFIG.json", file=sys.stderr)
        return 2
    try:
        cfg = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result = _invalid_result(f"cannot read config: {exc.__class__.__name__}")
    else:
        result = verify(cfg)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == V_CLEAR else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
