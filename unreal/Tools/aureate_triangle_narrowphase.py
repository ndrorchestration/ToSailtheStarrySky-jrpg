"""Exact triangle-surface distances for Aureate Wake review-only geometry.

Standard library, centimeters. No mesh simplification, no physics or CCD claim.
"""
from __future__ import annotations

import math


def sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


def add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def scale(a, s):
    return (a[0]*s, a[1]*s, a[2]*s)


def dot(a, b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def point_segment_sq(p, a, b):
    d = sub(b,a)
    size = dot(d,d)
    if size < 1e-18:
        return dot(sub(p,a),sub(p,a))
    t = max(0.,min(1.,dot(sub(p,a),d)/size))
    v = sub(p, add(a,scale(d,t)))
    return dot(v,v)


def point_triangle_sq(p, tri):
    a,b,c=tri
    e0=sub(b,a);e1=sub(c,a)
    n=cross(e0,e1);n2=dot(n,n)
    if n2 > 1e-14:
        signed=dot(sub(p,a),n)/n2
        pp=sub(p,scale(n,signed))
        v2=sub(pp,a)
        aa=dot(e0,e0);bb=dot(e0,e1);cc=dot(e1,e1)
        den=aa*cc-bb*bb
        if den > 1e-14:
            u=(cc*dot(v2,e0)-bb*dot(v2,e1))/den
            v=(aa*dot(v2,e1)-bb*dot(v2,e0))/den
            if u >= -1e-10 and v >= -1e-10 and u+v <= 1.+1e-10:
                return max(0.,signed*signed*n2)
    return min(point_segment_sq(p,a,b),point_segment_sq(p,b,c),
               point_segment_sq(p,c,a))


def segment_segment_sq(p0,p1,q0,q1):
    # Closest points between two *finite* segments; handles parallel and
    # point-degenerate endpoints without relying on unbounded lines.
    u=sub(p1,p0);v=sub(q1,q0);w=sub(p0,q0)
    a=dot(u,u);b=dot(u,v);c=dot(v,v);d=dot(u,w);e=dot(v,w)
    if a < 1e-18: return point_segment_sq(p0,q0,q1)
    if c < 1e-18: return point_segment_sq(q0,p0,p1)
    den=a*c-b*b
    sd=den;td=den
    if den < 1e-14:
        sn=0.;sd=1.;tn=e;td=c
    else:
        sn=b*e-c*d;tn=a*e-b*d
        if sn<0.: sn=0.;tn=e;td=c
        elif sn>sd: sn=sd;tn=e+b;td=c
    if tn<0.:
        tn=0.
        if -d<0.: sn=0.
        elif -d>a: sn=sd
        else: sn=-d;sd=a
    elif tn>td:
        tn=td
        if -d+b<0.: sn=0.
        elif -d+b>a: sn=sd
        else: sn=-d+b;sd=a
    sc=0. if abs(sn)<1e-14 else sn/sd
    tc=0. if abs(tn)<1e-14 else tn/td
    delta=sub(add(w,scale(u,sc)),scale(v,tc))
    return max(0.,dot(delta,delta))


def segment_hits_triangle(p0,p1,tri):
    # Moller-Trumbore segment/triangle test. Coplanar cases are handled
    # by vertex-face and segment-segment distances below.
    a,b,c=tri
    d=sub(p1,p0);e1=sub(b,a);e2=sub(c,a)
    p=cross(d,e2);det=dot(e1,p)
    if abs(det)<1e-12: return False
    inv=1./det
    t=sub(p0,a);u=dot(t,p)*inv
    if u < -1e-10 or u > 1.+1e-10: return False
    q=cross(t,e1);v=dot(d,q)*inv
    if v < -1e-10 or u+v > 1.+1e-10: return False
    dist=dot(e2,q)*inv
    return -1e-10 <= dist <= 1.+1e-10


def triangle_triangle_sq(first,second):
    e1=((first[0],first[1]),(first[1],first[2]),(first[2],first[0]))
    e2=((second[0],second[1]),(second[1],second[2]),(second[2],second[0]))
    if any(segment_hits_triangle(a,b,second) for a,b in e1):
        return 0.
    if any(segment_hits_triangle(a,b,first) for a,b in e2):
        return 0.
    return min(
        *(point_triangle_sq(p,second) for p in first),
        *(point_triangle_sq(p,first) for p in second),
        *(segment_segment_sq(a,b,c,d) for a,b in e1 for c,d in e2),
    )


def bounds(tri):
    return ((min(p[0] for p in tri),min(p[1] for p in tri),min(p[2] for p in tri)),
            (max(p[0] for p in tri),max(p[1] for p in tri),max(p[2] for p in tri)))


def squared_box_distance(a,b):
    return sum(max(a[0][i]-b[1][i], b[0][i]-a[1][i], 0.)**2 for i in range(3))


def nearest_surface(wing_positions,wing_indices,body_positions,body_indices,
                    threshold_cm=10., exclude_pair=None):
    """Fully indexed, conservative triangle AABB broad phase + exact narrow phase.

    Only pairs whose bounding boxes could be within threshold are tested.
    If none are near, reports min_surface_cm=None (not a global minimum).
    A zero distance is a surface intersection or intentional attachment contact,
    NOT necessarily a problematic collision.
    """
    if threshold_cm <= 0: raise ValueError("Invalid threshold")
    body_tri=[tuple(body_positions[i] for i in tri) for tri in body_indices]
    body_aabb=[bounds(tri) for tri in body_tri]
    low=tuple(min(v[i] for v in body_positions)-threshold_cm for i in range(3))
    high=tuple(max(v[i] for v in body_positions)+threshold_cm for i in range(3))
    threshold_sq=threshold_cm**2
    candidates=0
    closest=(float("inf"),None,None)
    near_triangles=0
    excluded_pairs=0
    for wi,idx in enumerate(wing_indices):
        tri=tuple(wing_positions[i] for i in idx)
        a=bounds(tri)
        if any(a[1][i]<low[i] or a[0][i]>high[i] for i in range(3)):
            continue
        near_triangles+=1
        for bi,box in enumerate(body_aabb):
            if squared_box_distance(a,box)>threshold_sq:
                continue
            if exclude_pair is not None and exclude_pair(wi,bi):
                excluded_pairs+=1
                continue
            candidates+=1
            d2=triangle_triangle_sq(tri,body_tri[bi])
            if d2<closest[0]:
                closest=(d2,wi,bi)
    min_cm=None if closest[1] is None else math.sqrt(closest[0])
    return {"near_wing_triangles":near_triangles,
            "excluded_candidate_triangle_pairs":excluded_pairs,
            "triangle_pairs_narrow_phase_checked":candidates,
            "min_surface_cm_within_threshold":min_cm,
            "wing_triangle_index":closest[1],
            "body_triangle_index":closest[2],
            "below_threshold":min_cm is not None and min_cm<threshold_cm}
