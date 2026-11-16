"""Guarded one-asset, review-only UE 5.8.4 optical BridgeDeck reachability edit.

Requires separate native Editor process with explicit opt-in and no other Editor.
DO NOT run while PR #838 Whiteout PIE session is active. Source-only until then.
Preserves original VS02, gameplay/story/party/input, all non-review maps.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import unreal as u
from verify_optical_bridge_reach_geometry import (
    PROJECT, ROOT, COPY, SOURCE, EXPECTED_SOURCE, EXPECTED_REVIEW,
    diagnose, bbox, within, sha,
)
from optical_bridge_checkout_guard import INTEGRATION_BASE, validate_checkout

MAP="/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview"
DIR=PROJECT/"Saved/OpticalReachGeometry/NativeStage"
BACKUP=DIR/"unchanged_review_copy_before_walkability_fix.umap"
RECEIPT=DIR/"stage.json"
OLD_BRANCH_HEAD=os.environ.get("TSTSS_BRIDGE_REACH_EXPECT_HEAD","")

def hold(ok:bool,message:str):
    if not ok:
        raise RuntimeError("HOLD: "+message)

def single(actors,label):
    xs=[actor for actor in actors if str(actor.get_actor_label())==label]
    hold(len(xs)==1,"expected exactly one "+label)
    return xs[0]

def xyz(v):
    return (float(v.x),float(v.y),float(v.z))

def near(a,b,tol=0.05):
    return all(abs(float(x)-float(y))<=tol for x,y in zip(a,b))

def git(*args):
    r=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,
                     text=True,timeout=20)
    hold(r.returncode==0,"git "+str(args)+" failed")
    return r.stdout.strip()

def stage():
    hold(os.environ.get("TSTSS_BRIDGE_REACH_STAGE_EXPLICIT")=="1",
         "stage requires opt-in")
    ancestry=subprocess.run(["git","-C",str(ROOT),"merge-base","--is-ancestor",
                             INTEGRATION_BASE,"HEAD"],capture_output=True,timeout=20)
    validate_checkout(ROOT.name,git("branch","--show-current"),
                      git("rev-parse","HEAD"),OLD_BRANCH_HEAD,
                      ancestry.returncode==0)
    hold(not git("status","--porcelain=v1","--untracked-files=all"),
         "uncommitted source changes")
    hold(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
         "wrong native Unreal version")
    hold(sha(SOURCE)==EXPECTED_SOURCE and sha(COPY)==EXPECTED_REVIEW,
         "source or optical copy checksum not baseline")
    hold(not RECEIPT.exists() and not BACKUP.exists(),
         "staging receipt or backup already present")
    hold(not u.get_editor_subsystem(u.LevelEditorSubsystem).is_in_play_in_editor(),
         "PIE still running in staging Editor")
    hold(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(),
         "dirty map packages before source lock")
    hold(not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
         "dirty content packages before source lock")
    report=diagnose()
    hold(report["player_start_inside_solid_bridge"],
         "baseline geometry no longer reproduces spawn overlap")
    world=u.EditorLoadingAndSavingUtils.load_map(MAP)
    hold(world is not None,"optical map native load failed")
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    hold(len(actors)==28,"unexpected review map actor inventory")
    bridge=single(actors,"TSTSS_VS_REVIEW_BridgeDeck")
    deck=single(actors,"TSTSS_VS_REVIEW_MainWalkableDeck")
    lift=single(actors,"TSTSS_VS_REVIEW_InstrumentCore_LIFT")
    spawn=single(actors,"TSTSS_VS_REVIEW_PlayerStart_Review")
    receiver=single(actors,"TSTSS_OPTICAL_REVIEW_Receiver_Disabled")
    hold(sum(a.get_class().get_name()=="TSTSSAtmosphereDirector"
             for a in actors)==1,"atmosphere authority drift")
    hold(receiver.get_editor_property("explicit_review_opt_in") is False,
         "receiver unexpectedly enabled")
    hold(near(xyz(bridge.get_actor_location()),(-780.,0.,65.)),
         "bridge location differs")
    hold(near(xyz(bridge.get_actor_scale3d()),(7.,9.,1.4)),
         "bridge scale differs")
    hold(near(xyz(deck.get_actor_location()),(0.,0.,-50.)),
         "floor location differs")
    hold(near(xyz(spawn.get_actor_location()),(-1080.,0.,120.)),
         "spawn differs")
    hold(near(xyz(lift.get_actor_location()),(-250.,-250.,270.)),
         "LIFT differs")
    mesh=bridge.get_component_by_class(u.StaticMeshComponent)
    hold(mesh is not None and mesh.get_editor_property("static_mesh") is not None,
         "missing bridge geometry")
    hold(mesh.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS,
         "bridge not currently a solid collision object")
    hold(mesh.get_material(0) is not None,
         "bridge material absent")
    new_xyz=(-780.,0.,7.5)
    new_scale=(7.,9.,0.15)
    bounds=bbox(new_xyz,new_scale)
    hold(not within((-1080.,0.,120.),bounds),
         "proposed bridge still contains original pawn starting point")
    hold(bounds[2]==(0.,15.),
         "proposed slab does not sit flush on original MainWalkableDeck")
    cfg_paths=[PROJECT/"Config/DefaultInput.ini",
               PROJECT/"Config/DefaultEngine.ini"]
    cfg_sha={str(p):sha(p) for p in cfg_paths}
    DIR.mkdir(parents=True,exist_ok=True)
    shutil.copy2(COPY,BACKUP)
    hold(sha(BACKUP)==EXPECTED_REVIEW,
         "review copy backup mismatch")
    # Smallest possible isolated scene edit: one existing greybox actor.
    bridge.set_actor_location(u.Vector(*new_xyz),sweep=False,teleport=True)
    bridge.set_actor_scale3d(u.Vector(*new_scale))
    hold(near(xyz(bridge.get_actor_location()),new_xyz),
         "new bridge location rejected")
    hold(near(xyz(bridge.get_actor_scale3d()),new_scale),
         "new bridge scale rejected")
    hold(mesh.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS,
         "walkable bridge collision lost")
    hold(u.EditorLoadingAndSavingUtils.save_map(world,MAP),
         "native save of isolated review copy failed")
    hold(sha(SOURCE)==EXPECTED_SOURCE,"original VS02 mutated")
    hold(all(sha(Path(p))==v for p,v in cfg_sha.items()),
         "input or rendering config drift")
    hold(sha(COPY)!=EXPECTED_REVIEW,"review copy unchanged")
    result={
        "status":"NATIVE_NONSHIPPING_WALKABILITY_MAP_STAGE_NOT_PIE",
        "head_at_stage":OLD_BRANCH_HEAD,
        "saved_review_map":MAP,
        "original_vs02_sha256":EXPECTED_SOURCE,
        "old_review_copy_sha256":EXPECTED_REVIEW,
        "new_review_copy_sha256":sha(COPY),
        "old_copy_backup":str(BACKUP),
        "actor_count":len(actors),
        "changed_actor":"TSTSS_VS_REVIEW_BridgeDeck",
        "new_transform":{"xyz_cm":new_xyz,"scale":new_scale,
                         "upper_walkable_z_cm":15.},
        "player_start_unchanged":True,
        "target_LIFT_unchanged":True,
        "receiver_enabled":False,
        "independent_native_readback_complete":False,
        "real_pie_wasd_c_confirmed":False,
        "creator_approved":False,
    }
    with RECEIPT.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
    u.log("TSTSS_BRIDGE_REACH_NONSHIPPING_NATIVE_STAGE_ONLY "+result["new_review_copy_sha256"])
    return result

if __name__=="__main__":
    print(json.dumps(stage(),indent=2))
