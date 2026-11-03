#!/usr/bin/env python3
"""Geometry-only contract for one coupled bridge and living-quarters pivot.

Neither pose angles nor attachment geometry here are creator-approved. No UE
runtime, component, SaveGame, art asset or story authorization is modified.
"""
from __future__ import annotations
import json
import math
from typing import Sequence

STATES=("Skybourne","Seabourne","Submersible")
REVIEW_LABEL="COUPLED_HABITATION_GEOMETRY_REVIEW_ONLY"

def xyz(values:Sequence[float], label:str)->tuple[float,float,float]:
    if len(values)!=3:raise ValueError(label+" must have exactly three coordinates")
    vals=tuple(float(x) for x in values)
    if not all(math.isfinite(x) for x in vals):
        raise ValueError(label+" has nonfinite geometry")
    if any(abs(x)>1e6 for x in vals):
        raise ValueError(label+" outside bounded temporary centimeter study")
    return vals

def rotate_axis(point:Sequence[float],pivot:Sequence[float],
                axis:Sequence[float],degrees:float):
    a=xyz(point,"point"); c=xyz(pivot,"pivot"); n=xyz(axis,"axis")
    t=float(degrees)
    if not math.isfinite(t):raise ValueError("nonfinite review rotation")
    if abs(t)>360.0:raise ValueError("review angle exceeds one turn")
    length=math.sqrt(sum(v*v for v in n))
    if length<1e-8:raise ValueError("zero review pivot axis")
    n=tuple(v/length for v in n)
    t=math.radians(t)
    v=tuple(a[i]-c[i] for i in range(3))
    dot=sum(n[i]*v[i] for i in range(3))
    cross=(n[1]*v[2]-n[2]*v[1],
           n[2]*v[0]-n[0]*v[2],
           n[0]*v[1]-n[1]*v[0])
    return tuple(c[i]+v[i]*math.cos(t)+cross[i]*math.sin(t)+
                 n[i]*dot*(1-math.cos(t)) for i in range(3))

def norm(v):
    return math.sqrt(sum(x*x for x in v))

def delta(a,b):
    return tuple(a[i]-b[i] for i in range(3))

def review_pose(form:str,pivot:Sequence[float],bridge:Sequence[float],
                quarters:Sequence[float],axis:Sequence[float],degrees:float):
    if form not in STATES:
        raise ValueError("no orbital/player Starbourne pose in review-only geometry")
    pivot=xyz(pivot,"pivot")
    bridge=xyz(bridge,"bridge")
    quarters=xyz(quarters,"quarters")
    axis=xyz(axis,"rotation axis")
    b=rotate_axis(bridge,pivot,axis,degrees)
    q=rotate_axis(quarters,pivot,axis,degrees)
    original=norm(delta(bridge,quarters))
    after=norm(delta(b,q))
    if not math.isclose(original,after,abs_tol=1e-6,rel_tol=1e-10):
        raise ValueError("bridge/quarters no longer one rigid coupled assembly")
    return {
      "authority":REVIEW_LABEL,"form":form,
      "pivot_xyz_cm":list(pivot),
      "bridge_before_xyz_cm":list(bridge),"quarters_before_xyz_cm":list(quarters),
      "bridge_after_xyz_cm":list(b),"quarters_after_xyz_cm":list(q),
      "bridge_quarters_rigid_distance_cm":original,
      "relative_distance_preserved":True,
      "source_pose_creator_approved":False,
      "continuous_swept_collision_verified":False,
      "pressure_envelope_verified":False,
      "runtime_component_attached":False,
      "starbourne_player_unlocked":False
    }

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--form",choices=STATES,required=True)
    p.add_argument("--pivot",nargs=3,type=float,required=True)
    p.add_argument("--bridge",nargs=3,type=float,required=True)
    p.add_argument("--quarters",nargs=3,type=float,required=True)
    p.add_argument("--axis",nargs=3,type=float,required=True)
    p.add_argument("--degrees",type=float,required=True)
    args=p.parse_args()
    print(json.dumps(review_pose(args.form,args.pivot,args.bridge,
          args.quarters,args.axis,args.degrees),sort_keys=True,indent=2))

if __name__=="__main__":main()
