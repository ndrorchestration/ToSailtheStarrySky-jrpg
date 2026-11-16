"""Convert native Unreal actor snapshots into a swept-clearance verifier config.

Pure stdlib, no `unreal` import: the Unreal-side script only dumps raw records
(`export_aureate_envelopes_native.py`); every judgement lives here so it can be
unit-tested on any machine. Fail-closed: anything missing, ambiguous, non-finite
or inconsistent raises EnvelopeError and no config is produced.

Output is a SOURCE-SIDE SCREEN INPUT. It is not a native collision receipt, does
not approve any transition, and is marked provisional.

Snapshot schema (`aureate_envelope_snapshot_v1`, units cm, quaternion [w,x,y,z]):
  {schema, ue_version, map_path, map_sha256, form, actors:[
     {label, location[3], rotation_quat[4], scale[3],
      local_bounds:{origin[3], extent[3]},     # mesh-local box, unscaled
      world_aabb:{origin[3], extent[3]}}]}      # engine-reported, for self-check
"""
import math
import re

SNAPSHOT_SCHEMA = "aureate_envelope_snapshot_v1"
WING_IDENTITIES = ("FORE_PORT", "FORE_STARBOARD", "AFT_PORT", "AFT_STARBOARD")

# Labels from the #732 15-actor coupled-habitation stage (substring match, each
# must resolve to exactly one actor). OPEN: confirm on the native map.
DEFAULT_ROLE_LABELS = {
    "hull": ("SHARED_PEARL_HULL_PROXY", "SHARED_HULL_CINEMATIC_V4_TRIM"),
    "bridge": ("FORWARD_GEODESIC_GLASS_DOME_REVIEW",),
    "quarters": ("CENTRAL_CURVED_QUARTERS_REVIEW",),
    "deck": ("FORWARD_OBSERVATION_DECK_PROXY",),
}
OBSTACLE_TOL_CM = 1e-3
WING_BOUNDS_TOL_CM = 1e-3
AABB_SELF_CHECK_TOL_CM = 0.05
QUAT_NORM_TOL = 1e-4
_SHA = re.compile(r"^[0-9a-f]{64}$")


class EnvelopeError(ValueError):
    """Raised for any input that cannot be turned into a trustworthy config."""


def _nums(value, n, name):
    if not isinstance(value, (list, tuple)) or len(value) != n:
        raise EnvelopeError(f"{name} must be a list of {n} numbers")
    out = []
    for x in value:
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
            raise EnvelopeError(f"{name} must contain only finite numbers")
        out.append(float(x))
    return tuple(out)


def _qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def _rotate(q, v):
    qv = (0.0, v[0], v[1], v[2])
    conj = (q[0], -q[1], -q[2], -q[3])
    r = _qmul(_qmul(q, qv), conj)
    return (r[1], r[2], r[3])


def _unit_quat(value, name):
    q = _nums(value, 4, name)
    norm = math.sqrt(sum(c * c for c in q))
    if abs(norm - 1.0) > QUAT_NORM_TOL:
        raise EnvelopeError(f"{name} is not a unit quaternion (norm {norm:.6f})")
    return tuple(c / norm for c in q)


def _check_snapshot(snap, name):
    if not isinstance(snap, dict) or snap.get("schema") != SNAPSHOT_SCHEMA:
        raise EnvelopeError(f"{name}: wrong or missing schema (want {SNAPSHOT_SCHEMA})")
    if snap.get("units") != "cm":
        raise EnvelopeError(f"{name}: units must be 'cm'")
    sha = snap.get("map_sha256")
    if not isinstance(sha, str) or not _SHA.match(sha):
        raise EnvelopeError(f"{name}: map_sha256 must be 64 lowercase hex chars")
    if not isinstance(snap.get("form"), str) or not snap["form"]:
        raise EnvelopeError(f"{name}: form is required")
    actors = snap.get("actors")
    if not isinstance(actors, list) or not actors:
        raise EnvelopeError(f"{name}: actors must be a non-empty list")
    return actors


def _find(actors, token, name):
    hits = [a for a in actors if isinstance(a, dict) and isinstance(a.get("label"), str)
            and token in a["label"]]
    if len(hits) != 1:
        raise EnvelopeError(f"{name}: label token {token!r} matched {len(hits)} actors, need exactly 1")
    return hits[0]


def _record(actor, where):
    loc = _nums(actor.get("location"), 3, f"{where}.location")
    quat = _unit_quat(actor.get("rotation_quat"), f"{where}.rotation_quat")
    scale = _nums(actor.get("scale"), 3, f"{where}.scale")
    if any(s <= 0 for s in scale):
        raise EnvelopeError(f"{where}.scale must be > 0 (mirrored or zero scale refused)")
    lb = actor.get("local_bounds")
    if not isinstance(lb, dict):
        raise EnvelopeError(f"{where}.local_bounds missing")
    origin = _nums(lb.get("origin"), 3, f"{where}.local_bounds.origin")
    extent = _nums(lb.get("extent"), 3, f"{where}.local_bounds.extent")
    if any(e <= 0 for e in extent):
        raise EnvelopeError(f"{where}.local_bounds.extent must all be > 0")
    return loc, quat, scale, origin, extent


def _world_box(loc, quat, scale, origin, extent):
    off = _rotate(quat, tuple(o * s for o, s in zip(origin, scale)))
    center = tuple(l + o for l, o in zip(loc, off))
    half = tuple(e * s for e, s in zip(extent, scale))
    return center, half


def _aabb_of_obb(center, half, quat):
    axes = [_rotate(quat, v) for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
    reach = tuple(sum(abs(axes[j][i]) * half[j] for j in range(3)) for i in range(3))
    return center, reach


def _self_check(actor, where, center, half, quat, tol):
    aabb = actor.get("world_aabb")
    if not isinstance(aabb, dict):
        raise EnvelopeError(f"{where}.world_aabb missing (engine self-check is mandatory)")
    wc = _nums(aabb.get("origin"), 3, f"{where}.world_aabb.origin")
    we = _nums(aabb.get("extent"), 3, f"{where}.world_aabb.extent")
    mc, me = _aabb_of_obb(center, half, quat)
    worst = max(max(abs(a - b) for a, b in zip(wc, mc)), max(abs(a - b) for a, b in zip(we, me)))
    if worst > tol:
        raise EnvelopeError(
            f"{where}: derived box disagrees with engine bounds by {worst:.4f} cm (> {tol}); "
            "quaternion convention or transform composition is wrong")


def _close(a, b, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def build_config(snap_from, snap_to, *, required_clearance, role_labels=None,
                 aabb_tol=AABB_SELF_CHECK_TOL_CM, max_depth=16, max_evals=400_000):
    """Return a verifier config from two native snapshots (from-form, to-form)."""
    if isinstance(required_clearance, bool) or not isinstance(required_clearance, (int, float)) \
            or not math.isfinite(required_clearance) or required_clearance < 0:
        raise EnvelopeError("required_clearance must be a finite number >= 0")
    roles = dict(DEFAULT_ROLE_LABELS if role_labels is None else role_labels)
    for needed in DEFAULT_ROLE_LABELS:
        if not roles.get(needed):
            raise EnvelopeError(f"role {needed!r} has no label tokens")
    actors_a = _check_snapshot(snap_from, "from")
    actors_b = _check_snapshot(snap_to, "to")
    if snap_from["form"] == snap_to["form"]:
        raise EnvelopeError("from and to snapshots describe the same form")

    obstacles = []
    for role in DEFAULT_ROLE_LABELS:
        parts = []
        for token in roles[role]:
            where = f"{role}:{token}"
            aa, ab = _find(actors_a, token, "from"), _find(actors_b, token, "to")
            ra, rb = _record(aa, "from." + where), _record(ab, "to." + where)
            ca, ha = _world_box(*ra)
            cb, hb = _world_box(*rb)
            same_quat = _close(ra[1], rb[1], 1e-6) or _close(ra[1], tuple(-c for c in rb[1]), 1e-6)
            if not (same_quat and _close(ca, cb, OBSTACLE_TOL_CM) and _close(ha, hb, OBSTACLE_TOL_CM)):
                raise EnvelopeError(
                    f"obstacle {where} differs between the two forms; the verifier models "
                    "obstacles as static, so this transition cannot be screened")
            _self_check(aa, "from." + where, ca, ha, ra[1], aabb_tol)
            _self_check(ab, "to." + where, cb, hb, rb[1], aabb_tol)
            parts.append({"center": list(ca), "half_extents": list(ha),
                          "rotation_quat": list(ra[1])})
        obstacles.append({"role": role, "parts": parts})

    wings = []
    for ident in WING_IDENTITIES:
        aa, ab = _find(actors_a, ident, "from"), _find(actors_b, ident, "to")
        ra, rb = _record(aa, f"from.{ident}"), _record(ab, f"to.{ident}")
        if not (_close(ra[3], rb[3], WING_BOUNDS_TOL_CM) and _close(ra[4], rb[4], WING_BOUNDS_TOL_CM)):
            raise EnvelopeError(f"wing {ident} local bounds differ between forms (different mesh?)")
        for tag, act, rec in (("from", aa, ra), ("to", ab, rb)):
            c, h = _world_box(*rec)
            _self_check(act, f"{tag}.{ident}", c, h, rec[1], aabb_tol)
        wings.append({
            "identity": ident,
            "parts": [{"center": list(ra[3]), "half_extents": list(ra[4])}],
            "pose_from": {"position": list(ra[0]), "rotation_quat": list(ra[1]), "scale": list(ra[2])},
            "pose_to": {"position": list(rb[0]), "rotation_quat": list(rb[1]), "scale": list(rb[2])},
        })

    return {
        "schema_version": 1,
        "note": ("Exported from native Unreal actor bounds; SOURCE-SIDE SCREEN INPUT only. "
                 "Not a native collision receipt; approves no transition."),
        "provisional": True,
        "units": "cm",
        "transition": {"from": snap_from["form"], "to": snap_to["form"]},
        "required_clearance": float(required_clearance),
        "sweep": {"max_depth": int(max_depth), "max_evals": int(max_evals)},
        "provenance": {"from_map_sha256": snap_from["map_sha256"],
                       "to_map_sha256": snap_to["map_sha256"],
                       "from_ue_version": snap_from.get("ue_version"),
                       "to_ue_version": snap_to.get("ue_version")},
        "obstacles": obstacles,
        "wings": wings,
    }
