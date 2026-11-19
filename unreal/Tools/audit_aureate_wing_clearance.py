#!/usr/bin/env python3
"""Auditable offline four-wing geometric *screen*, not Unreal/physics certification.

Samples the actual corrected one-wing GLB geometry under the review actor's
hard-coded root-pivot poses and eased quaternion transitions. It conservatively
rejects AABB overlaps between different wings and the temporary hull/bridge
bounds. A discrete sampled screen cannot prove continuous collision freedom.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
from pathlib import Path
import struct

from import_aureate_wing_review import preflight, WingReviewHold

FORMS = ("Skyborne", "Seaborne", "Submersible")
CUBE_HULL = ((-400., -75., -32.5), (400., 75., 32.5))
CUBE_BRIDGE = ((135., -55., 40.), (345., 55., 150.))
MIN_CLEARANCE_CM = 10.0
STATUS = "SAMPLED_GEOMETRY_SCREEN_ONLY_NOT_ENGINE_OR_COLLISION_APPROVED"


class GeometryHold(ValueError):
    pass


def read_vertices(glb: Path, per_primitive=3000):
    """GLB 2.0 float32 positions, meters/+Y up -> Unreal cm/+Z up."""
    if per_primitive < 100 or per_primitive > 50000:
        raise GeometryHold("Use 100..50000 sample points per primitive")
    blob = glb.read_bytes()
    if len(blob) < 28 or blob[:4] != b"glTF":
        raise GeometryHold("Not a GLB")
    version, total = struct.unpack_from("<II", blob, 4)
    jlen, jtype = struct.unpack_from("<I4s", blob, 12)
    if version != 2 or total != len(blob) or jtype != b"JSON":
        raise GeometryHold("Malformed GLB header")
    doc = json.loads(blob[20:20 + jlen])
    if doc.get("extras", {}).get("sourceToGltfScale") != 0.01:
        raise GeometryHold("Retired/oversized GLB, require cm-to-meter correction")
    bin_pos = 20 + jlen + 8
    blen, btype = struct.unpack_from("<I4s", blob, bin_pos - 8)
    if btype != b"BIN\0" or bin_pos + blen != len(blob):
        raise GeometryHold("Missing GLB binary chunk")
    primitives = doc["meshes"][0]["primitives"]
    if len(primitives) != 3:
        raise GeometryHold("Requires membrane, venation and root primitives")
    vertices = []
    sizes = []
    for piece in primitives:
        acc = doc["accessors"][piece["attributes"]["POSITION"]]
        if acc["type"] != "VEC3" or acc["componentType"] != 5126:
            raise GeometryHold("Unexpected position accessor format")
        view = doc["bufferViews"][acc["bufferView"]]
        count = acc["count"]
        sizes.append(count)
        stride = max(1, math.ceil(count / per_primitive))
        indices = sorted({0, count - 1, *range(0, count, stride)})
        for i in indices:
            start = bin_pos + view.get("byteOffset", 0) + acc.get("byteOffset", 0) + i * view.get("byteStride", 12)
            if start + 12 > bin_pos + blen:
                raise GeometryHold("GLB vertex access out of bounds")
            x, y, z = struct.unpack_from("<fff", blob, start)
            if not all(math.isfinite(v) for v in (x,y,z)):
                raise GeometryHold("Nonfinite GLB geometry")
            # glTF xyz was built as Unreal (x,z,-y); invert and convert m -> cm.
            vertices.append((x * 100., -z * 100., y * 100.))
    return vertices, sizes


def pose(form, wing):
    if form not in (*FORMS, "Orbiter") or wing not in range(4):
        raise GeometryHold("Invalid form or wing index")
    front = wing < 2
    side = -1 if wing % 2 == 0 else 1
    xyz = (155. if front else -180., side * 112., 48.)
    angles = (0., 0., 0.)
    scale = (1., 1., 1.)
    if form == "Skyborne":
        angles = (0., side * (80. if front else 100.), side * 7.)
    elif form == "Seaborne":
        xyz = (xyz[0], xyz[1], 82.)
        angles = (32., side * (75. if front else 105.), side * 50.)
        scale = (.94, .82, 1.)
    elif form == "Submersible":
        xyz = (xyz[0], xyz[1], 16.)
        angles = (0., side * (23. if front else 157.), side * 72.)
        scale = (.78, .38, .95)
    else:
        xyz = [(0., 0., 130.), (0., 0., -130.), (0., -130., 0.), (0., 130., 0.)][wing]
        angles = [(90., 0., 0.), (-90., 0., 0.), (0., -90., 0.), (0., 90., 0.)][wing]
    return xyz, angles, scale


def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw*bw-ax*bx-ay*by-az*bz, aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw)


def quaternion(pitch, yaw, roll):
    # Unreal FRotator yaw about +Z, pitch about -Y, roll about +X.
    p, y, r = (math.radians(v) / 2 for v in (pitch, yaw, roll))
    return qmul((math.cos(y), 0., 0., math.sin(y)),
                qmul((math.cos(p), 0., -math.sin(p), 0.),
                     (math.cos(r), math.sin(r), 0., 0.)))


def qnormalize(q):
    length = math.sqrt(sum(v*v for v in q))
    return tuple(v/length for v in q)


def qslerp(a, b, t):
    dot = sum(x*y for x, y in zip(a,b))
    if dot < 0:
        b = tuple(-v for v in b)
        dot = -dot
    if dot > .9995:
        return qnormalize(tuple(x*(1-t)+y*t for x,y in zip(a,b)))
    theta = math.acos(max(-1., min(1., dot)))
    sn = math.sin(theta)
    left = math.sin((1-t)*theta)/sn
    right = math.sin(t*theta)/sn
    return qnormalize(tuple(left*x+right*y for x,y in zip(a,b)))


def qrot(q, p):
    w,x,y,z = q
    vx,vy,vz=p
    cx=y*vz-z*vy;cy=z*vx-x*vz;cz=x*vy-y*vx
    dx=y*cz-z*cy;dy=z*cx-x*cz;dz=x*cy-y*cx
    return (vx+2*(w*cx+dx),vy+2*(w*cy+dy),vz+2*(w*cz+dz))


def blend(a, b, t):
    axyz, ar, asc = a
    bxyz, br, bsc = b
    smooth = t*t*(3-2*t)
    xyz = tuple(x+(y-x)*smooth for x,y in zip(axyz,bxyz))
    sc = tuple(x+(y-x)*smooth for x,y in zip(asc,bsc))
    q = qslerp(quaternion(*ar), quaternion(*br), smooth)
    return xyz, q, sc


def sampled_bounds(vertices, transform):
    translation, q, sc = transform
    lo = [float("inf")]*3
    hi = [-float("inf")]*3
    for point in vertices:
        p = qrot(q,tuple(x*s for x,s in zip(point,sc)))
        for axis in range(3):
            x = p[axis] + translation[axis]
            if x < lo[axis]: lo[axis]=x
            if x > hi[axis]: hi[axis]=x
    return tuple(lo), tuple(hi)


def gap_axis(a, b, axis):
    return max(a[0][axis]-b[1][axis],b[0][axis]-a[1][axis],0.)


def clearance_against_boxes(bounds):
    # All *sampled* vertices bound the sampled triangle hull at this frame.
    # Positive separation on any axis means the corresponding sampled facets
    # cannot intersect the temporary cuboid proxy at this sample time.
    return [max(gap_axis(bounds, b, ax) for ax in range(3)) for b in (CUBE_HULL,CUBE_BRIDGE)]


def assert_source_contract(cpp_text, header_text):
    for marker in ('const float RootY = Side * 112.f;',
                   'const float RootX = bForward ? 155.f : -180.f;',
                   'Scale = FVector(.94f, .82f, 1.f);',
                   'Scale = FVector(.78f, .38f, .95f);',
                   'bUseRootPivotedWingPose && AuthoredWingMesh'):
        if marker not in cpp_text:
            raise GeometryHold("C++ pose source has diverged from offline audit: " + marker)
    for marker in ('bUseRootPivotedWingPose = false;', 'bAllowOrbiterPreview = false;'):
        if marker not in header_text:
            raise GeometryHold("Preview opt-in default changed: " + marker)
    if 'RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter' not in cpp_text:
        raise GeometryHold("Risky authored Orbiter transitions must be blocked until a clearance path exists")


def audit(vertices, steps=20):
    if steps < 10:
        raise GeometryHold("At least ten time intervals required")
    worst_static = float('inf')
    worst_pair = float('inf')
    frames = 0
    for frm,to in itertools.permutations(FORMS,2):
        for i in range(steps+1):
            t=i/steps
            bounds = [sampled_bounds(vertices,blend(pose(frm,wing),pose(to,wing),t)) for wing in range(4)]
            for b in bounds:
                box_gaps = clearance_against_boxes(b)
                worst_static=min(worst_static,*box_gaps)
                if min(box_gaps) < MIN_CLEARANCE_CM:
                    raise GeometryHold(f"Wing/proxy clearance below {MIN_CLEARANCE_CM} cm on {frm}->{to} t={t:.3f}: {box_gaps}")
            for a,b in itertools.combinations(bounds,2):
                gap = max(gap_axis(a,b,ax) for ax in range(3))
                worst_pair=min(worst_pair,gap)
                if gap < MIN_CLEARANCE_CM:
                    raise GeometryHold(f"Wing/wing sampled AABB clearance below {MIN_CLEARANCE_CM} cm on {frm}->{to} t={t:.3f}")
            frames+=1
    return {"authority":STATUS,"checked_directed_transitions":6,"time_samples_per_transition":steps+1,
            "wing_instances":4,"checked_poses":frames,"mesh_sample_points":len(vertices),
            "minimum_proxy_aabb_clearance_cm":round(worst_static,2),
            "minimum_interwing_aabb_clearance_cm":round(worst_pair,2),
            "unresolved_visual_gates":["approximate 28 cm wing-root to hull-side gap has no authored support spar",
               "discrete sampled bounds are not continuous swept-volume clearance",
               "native Unreal import/render/collision and creator approval are not established",
               "authored wing Orbiter interpolation disabled pending a safe authored path"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--glb',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--cpp',type=Path,required=True)
    parser.add_argument('--header',type=Path,required=True)
    parser.add_argument('--samples-per-primitive',type=int,default=3000)
    parser.add_argument('--steps',type=int,default=20)
    args=parser.parse_args()
    try:
        preflight(args.glb, args.manifest)
        assert_source_contract(args.cpp.read_text(encoding='utf-8'),args.header.read_text(encoding='utf-8'))
        vertices,sizes=read_vertices(args.glb,args.samples_per_primitive)
        result=audit(vertices,args.steps)
        result['source_primitive_vertex_counts']=sizes
        print(json.dumps(result,indent=2))
    except (GeometryHold,WingReviewHold,OSError,KeyError,IndexError,ValueError,struct.error) as exc:
        parser.exit(1, 'WING CLEARANCE HOLD: '+str(exc)+'\n')

if __name__=='__main__':
    main()