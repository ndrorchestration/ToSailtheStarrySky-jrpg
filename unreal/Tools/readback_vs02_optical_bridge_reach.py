"""Independent fresh-Editor readback for future nonshipping optical bridge repair.

Run only after stage_vs02_optical_bridge_reach.py produced its own native
receipt. Checks one review asset and its unchanged original, NOT PIE gameplay.
No save_map, actor mutation, teleport or production asset writes.
"""
from __future__ import annotations
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import unreal as u
from verify_optical_bridge_reach_geometry import (
    ROOT, PROJECT, COPY, SOURCE, EXPECTED_SOURCE, EXPECTED_REVIEW,
    sha, bbox, within,
)
from optical_bridge_checkout_guard import INTEGRATION_BASE, validate_checkout

MAP="/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview"
DIR=PROJECT/"Saved/OpticalReachGeometry/NativeStage"
STAGE=DIR/"stage.json"
BACKUP=DIR/"unchanged_review_copy_before_walkability_fix.umap"
RECEIPT=DIR/"independent_readback.json"

def require(value,why):
    if not value:
        raise RuntimeError("HOLD: "+why)

def xyz(v):
    return (float(v.x),float(v.y),float(v.z))

def close(a,b,tol=.05):
    return all(abs(x-y)<=tol for x,y in zip(a,b))

def only(actors,label):
    matches=[a for a in actors if str(a.get_actor_label())==label]
    require(len(matches)==1,"actor inventory changed: "+label)
    return matches[0]

def inspect():
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
            "unexpected UE version")
    require(STAGE.exists() and BACKUP.exists() and not RECEIPT.exists(),
            "missing stage/backup or duplicate independent receipt")
    stage=json.loads(STAGE.read_text(encoding="utf-8"))
    def git(*args):
        result=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,
                              text=True,timeout=20)
        require(result.returncode==0,"git readback identity check failed")
        return result.stdout.strip()
    ancestry=subprocess.run(["git","-C",str(ROOT),"merge-base","--is-ancestor",
                             INTEGRATION_BASE,"HEAD"],capture_output=True,timeout=20)
    validate_checkout(ROOT.name,git("branch","--show-current"),git("rev-parse","HEAD"),
                      stage.get("head_at_stage"),ancestry.returncode==0)
    require(stage["status"]=="NATIVE_NONSHIPPING_WALKABILITY_MAP_STAGE_NOT_PIE",
            "stage native result was not an accepted save")
    require(stage["saved_review_map"]==MAP,"unexpected saved package")
    require(stage["old_review_copy_sha256"]==EXPECTED_REVIEW,
            "historical map SHA provenance differs")
    require(stage["original_vs02_sha256"]==EXPECTED_SOURCE,
            "source map provenance differs")
    require(sha(SOURCE)==EXPECTED_SOURCE,
            "canonical original VS02 changed")
    require(sha(BACKUP)==EXPECTED_REVIEW,
            "backup is not the expected original review copy")
    require(sha(COPY)==stage["new_review_copy_sha256"],
            "saved review map modified after staging")
    require(sha(COPY)!=EXPECTED_REVIEW,
            "no review-only binary change")
    world=u.EditorLoadingAndSavingUtils.load_map(MAP)
    require(world is not None,"native review copy load failed")
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    require(len(actors)==28,"expected original 28 actors")
    bridge=only(actors,"TSTSS_VS_REVIEW_BridgeDeck")
    deck=only(actors,"TSTSS_VS_REVIEW_MainWalkableDeck")
    gauge=only(actors,"TSTSS_VS_REVIEW_InstrumentCore_LIFT")
    spawn=only(actors,"TSTSS_VS_REVIEW_PlayerStart_Review")
    receiver=only(actors,"TSTSS_OPTICAL_REVIEW_Receiver_Disabled")
    require(close(xyz(bridge.get_actor_location()),(-780.,0.,7.5)),
            "bridge location did not persist")
    require(close(xyz(bridge.get_actor_scale3d()),(7.,9.,0.15)),
            "bridge scale did not persist")
    require(close(xyz(deck.get_actor_location()),(0.,0.,-50.)),
            "main deck was modified")
    require(close(xyz(spawn.get_actor_location()),(-1080.,0.,120.)),
            "player start was modified")
    require(close(xyz(gauge.get_actor_location()),(-250.,-250.,270.)),
            "LIFT location was modified")
    require(not within(xyz(spawn.get_actor_location()),
                       bbox(xyz(bridge.get_actor_location()),
                            xyz(bridge.get_actor_scale3d()))),
            "player still starts inside bridge")
    mesh=bridge.get_component_by_class(u.StaticMeshComponent)
    require(mesh is not None and mesh.get_editor_property("static_mesh") is not None,
            "bridge lost its native collision mesh")
    require(mesh.get_collision_enabled()==u.CollisionEnabled.QUERY_AND_PHYSICS,
            "bridge lost walkable physical collision")
    require(mesh.get_material(0) is not None,
            "bridge material missing")
    require(receiver.get_editor_property("explicit_review_opt_in") is False,
            "review receiver enabled unexpectedly")
    require(sum(a.get_class().get_name()=="TSTSSAtmosphereDirector"
                for a in actors)==1,"atmosphere owner changed")
    cams=(
        ("TSTSS_OPTICAL_REVIEW_Inspection_ManualDOF",False),
        ("TSTSS_OPTICAL_REVIEW_Inspection_NoDOF_Control",True),
    )
    for label,disabled in cams:
        actor=only(actors,label)
        cine=actor.get_cine_camera_component()
        require(cine is not None,"missing CineCameraComponent")
        require(abs(float(cine.get_editor_property("current_focal_length"))-65.)<.05,
                "lens drift")
        require(abs(float(cine.get_editor_property("current_aperture"))-2.8)<.05,
                "f-stop drift")
        focus=cine.get_editor_property("focus_settings")
        expected=(u.CameraFocusMethod.DISABLE if disabled
                  else u.CameraFocusMethod.MANUAL)
        require(focus.get_editor_property("focus_method")==expected,
                "focus mode drift")
        pp=cine.get_editor_property("post_process_settings")
        require(bool(pp.get_editor_property("override_auto_exposure_bias")),
                "camera exposure not overridden")
        require(abs(float(pp.get_editor_property("auto_exposure_bias"))+6.)<.01,
                "camera exposure bias drift")
    require(sha(SOURCE)==EXPECTED_SOURCE and
            sha(COPY)==stage["new_review_copy_sha256"],
            "unexpected map write during readback")
    receipt={
        "status":"NONSHIPPING_OPTICAL_BRIDGE_FRESH_NATIVE_READBACK_PASS_NOT_PIE",
        "review_map_sha256":sha(COPY),
        "original_map_sha256":sha(SOURCE),
        "old_review_map_backup_sha256":sha(BACKUP),
        "actor_count":len(actors),"camera_count":2,
        "one_atmosphere_owner":True,"receiver_disabled":True,
        "player_spawn_inside_bridge":False,"bridge_collision_enabled":True,
        "real_wasd_navigation_confirmed":False,
        "c_key_preview_or_restore_confirmed":False,
        "gpu_composition_approved":False,
        "creator_approved":False,
        "map_write_performed":False,
    }
    with RECEIPT.open("x",encoding="utf-8") as out:
        json.dump(receipt,out,indent=2)
    u.log("TSTSS_OPTICAL_BRIDGE_INDEPENDENT_NATIVE_READBACK_NOT_PIE "+
          receipt["review_map_sha256"])
    return receipt

if __name__=="__main__":
    print(json.dumps(inspect(),indent=2))
