"""Source-locked, engine-free diagnosis of VS02 bridge spawn obstruction.

Diagnostic geometry assumes UE's BasicShapes/Cube nominal 100 cm extent;
runtime collision and WASD reachability must still be verified in native PIE.
No map changes, no actor teleport, and no story state writes.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import math
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
AUTHORING=PROJECT/"Tools/build_vertical_slice_environment_maps.py"
COPY=PROJECT/"Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"
SOURCE=PROJECT/"Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
EXPECTED_SOURCE="a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69"
EXPECTED_REVIEW="06f006b42d54a990ffefa5903bda0d24e34259a424c1f6bee4a51a29f0766223"
CUBE_CM=100.0
C_RADIUS_CM=450.0
LIFT=(-250.0,-250.0,270.0)

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _entry(source:str,label:str):
    pattern=(r'prop\("'+re.escape(label)+
             r'",\s*"Cube",\s*(\([^)]+\)),\s*(\([^)]+\)),'
             r'\s*"[^"]+",\s*True\)')
    matches=re.findall(pattern,source,re.S)
    if len(matches)!=1:
        raise RuntimeError("HOLD: expected one unchanged solid cube definition: "+label)
    loc=ast.literal_eval(matches[0][0]);scale=ast.literal_eval(matches[0][1])
    if len(loc)!=3 or len(scale)!=3:raise RuntimeError("HOLD: malformed geometry")
    return tuple(float(x) for x in loc),tuple(float(x) for x in scale)

def _player(source:str):
    segment=source.split("    def ship():",1)
    if len(segment)!=2:raise RuntimeError("HOLD: no original ship definition")
    block=segment[1].split("\n    def sky():",1)[0]
    matches=re.findall(r'player\((\([^)]+\))\)',block)
    if len(matches)!=1:raise RuntimeError("HOLD: ambiguous native PlayerStart")
    return tuple(float(x) for x in ast.literal_eval(matches[0]))

def bbox(loc,scale):
    return tuple((loc[i]-CUBE_CM*scale[i]/2.,
                  loc[i]+CUBE_CM*scale[i]/2.) for i in range(3))

def within(pos,bounds):
    return all(lo<=x<=hi for x,(lo,hi) in zip(pos,bounds))

def distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def validate_original_geometry(source:str):
    deck_loc,deck_scale=_entry(source,"BridgeDeck")
    floor_loc,floor_scale=_entry(source,"MainWalkableDeck")
    player=_player(source)
    if deck_loc!=(-780.,0.,65.) or deck_scale!=(7.,9.,1.4):
        raise RuntimeError("HOLD: original BridgeDeck size or location drift")
    if floor_loc!=(0.,0.,-50.) or floor_scale!=(24.,10.,1.):
        raise RuntimeError("HOLD: original MainWalkableDeck drift")
    if player!=(-1080.,0.,120.):
        raise RuntimeError("HOLD: original PlayerStart drift")
    return deck_loc,deck_scale,floor_loc,floor_scale,player

def diagnose():
    # Engine-free source checks also run in GitHub Actions clone directories.
    # Only the actual map-writing native stager is Neontic/worktree-locked.
    if sha(SOURCE)!=EXPECTED_SOURCE or sha(COPY)!=EXPECTED_REVIEW:
        raise RuntimeError("HOLD: baseline map SHA drift")
    authoring=AUTHORING.read_text(encoding="utf-8")
    deck_loc,deck_scale,floor_loc,floor_scale,player=validate_original_geometry(authoring)
    bounds=bbox(deck_loc,deck_scale)
    footprint_inside=within(player,bounds)
    floor_bounds=bbox(floor_loc,floor_scale)
    proposed_loc=(-780.,0.,7.5)
    proposed_scale=(7.,9.,0.15)
    proposed_bounds=bbox(proposed_loc,proposed_scale)
    assert deck_loc==(-780.,0.,65.) and deck_scale==(7.,9.,1.4)
    assert floor_loc==(0.,0.,-50.) and floor_scale==(24.,10.,1.)
    assert player==(-1080.,0.,120.)
    assert bounds==((-1130.,-430.),(-450.,450.),(-5.,135.))
    assert footprint_inside
    assert proposed_bounds==((-1130.,-430.),(-450.,450.),(0.,15.))
    assert not within(player,proposed_bounds)
    assert floor_bounds[2][1]==0.0
    assert proposed_bounds[2][0]==floor_bounds[2][1]
    assert proposed_bounds[2][1]-floor_bounds[2][1]==15.0
    assert distance(player,LIFT)>C_RADIUS_CM
    return {
        "status":"SOURCE_GEOMETRY_INTERSECTION_CONFIRMED_PROPOSED_FIX_NOT_NATIVE_TESTED",
        "source_map_sha256":EXPECTED_SOURCE,"review_map_sha256":EXPECTED_REVIEW,
        "source_authoring_preserved":True,
        "actor_label":"TSTSS_VS_REVIEW_BridgeDeck",
        "nominal_basic_cube_dimension_cm":CUBE_CM,
        "original_bridge_xyz_cm":deck_loc,
        "original_bridge_scale":deck_scale,
        "original_bridge_aabb_cm":bounds,
        "player_start_xyz_cm":player,
        "player_start_inside_solid_bridge":footprint_inside,
        "lift_gauge_xyz_cm":LIFT,
        "spawn_distance_to_lift_cm":round(distance(player,LIFT),3),
        "c_key_required_distance_cm":C_RADIUS_CM,
        "proposal":{
            "scope":"NONSHIPPING_M_ENGINEPRESENTATIONREVIEW_ONLY",
            "same_named_actor":True,"new_bridge_xyz_cm":proposed_loc,
            "new_bridge_scale":proposed_scale,
            "new_bridge_aabb_cm":proposed_bounds,
            "raised_walkable_lip_cm":15.,
            "player_start_intersects_proposed_bridge":within(player,proposed_bounds),
            "canonical_vs02_modified":False,
            "authoring_script_modified":False,
            "native_unreal_asset_saved":False,
            "real_wasd_c_reachability_established":False,
            "creator_approved":False
        },
        "limitations":"AABB checks infer nominal UE BasicShapes/Cube dimensions; real actor transforms, collision, floor angle, capsule reach and C-key activation need independent native Unreal and real PIE testing."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--receipt",action="store_true")
    args=parser.parse_args()
    report=diagnose()
    if args.receipt:
        out=PROJECT/"Saved/OpticalReachGeometry/diagnosis.json"
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x",encoding="utf-8") as f:json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
