#!/usr/bin/env python3
"""Independent, read-only native UE world inventory verification.

This is a separate UnrealEditor -ExecutePythonScript process after staging.
Saves only a new JSON readback receipt; does not save/edit level or user state.
A successful result is not D3D rendering, gameplay or visual art approval.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import stage_first_wake_slice_objects as stage

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def verify():
    import unreal
    root=Path(unreal.Paths.project_dir()).resolve()
    if root.name.lower()!="unreal" or root.parent.name!=stage.ROOT_NAME:
        raise RuntimeError("HOLD: wrong isolated source workspace")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: exact UE 5.8.4 required")
    dest=root/stage.NEW_MAP_REL
    source=root/stage.SOURCE_MAP_REL
    receipt=root/stage.DEST_RECEIPT_REL
    readback=root/"Saved/FirstWakeSliceObjectsV1/native_objects_readback.json"
    if not all(p.is_file() for p in (dest,source,receipt)):
        raise RuntimeError("HOLD: not a previously staged native World")
    if readback.exists(): raise RuntimeError("HOLD: prior readback; never overwrite")
    if list((root/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGames")
    before=sha256(dest)
    stage_json=json.loads(receipt.read_text(encoding="utf-8"))
    if (stage_json.get("status")!="NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
            or stage_json.get("new_map_sha256")!=before
            or stage_json.get("source_map_sha256")!=sha256(source)
            or stage_json.get("new_native_actor_count")!=31):
        raise RuntimeError("HOLD: map/receipt divergence")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty map")
    if not unreal.EditorLoadingAndSavingUtils.load_map(stage.NEW_MAP):
        raise RuntimeError("HOLD: UE failed to load saved objects map")
    system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=system.get_all_level_actors()
    labels=[a.get_actor_label() for a in actors]
    expected=set(stage_json["actor_labels"])
    if len(actors)!=115 or len(expected)!=31 or len(set(labels))!=len(labels):
        raise RuntimeError("HOLD: actors missing/duplicate in saved World")
    if sum(isinstance(a,unreal.PlayerStart) for a in actors)!=1:
        raise RuntimeError("HOLD: original PlayerStart lost/duplicated")
    for label in stage.MILESTONES:
        if labels.count("TSTSS_PRELUDE_REVIEW_"+label)!=1:
            raise RuntimeError("HOLD: milestone actor missing "+label)
    new=[a for a in actors if a.get_actor_label().startswith(stage.ACTOR_PREFIX)]
    if len(new)!=31 or {a.get_actor_label() for a in new}!=expected:
        raise RuntimeError("HOLD: visual object placement labels changed")
    referenced=set()
    for a in new:
        if not isinstance(a,unreal.StaticMeshActor):
            raise RuntimeError("HOLD: visual prop not a static-mesh actor")
        c=a.static_mesh_component
        if c.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("HOLD: imported mesh accidentally intercepts interaction/physics")
        m=c.get_editor_property("static_mesh")
        if m is None:
            raise RuntimeError("HOLD: unloaded static mesh "+a.get_actor_label())
        path=m.get_path_name()
        if not path.startswith(stage.IMPORT_DIR+"/"):
            raise RuntimeError("HOLD: unexpected mesh asset folder "+path)
        referenced.add(path)
    if len(referenced)!=22:
        raise RuntimeError("HOLD: not all 22 original assets used")
    if any("Starbourne" in label for label in labels):
        raise RuntimeError("HOLD: restricted Starbourne content in First Wake")
    if sum(isinstance(a,unreal.DirectionalLight) for a in actors)!=1:
        raise RuntimeError("HOLD: wrong lighting inheritance")
    if sha256(dest)!=before or sha256(source)!=stage_json["source_map_sha256"]:
        raise RuntimeError("HOLD: World bytes drifted on readback")
    result={"status":"INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE",
            "source_commit_expected":"stage receipt; check host custody",
            "engine":unreal.SystemLibrary.get_engine_version(),
            "saved_world_sha256":before,
            "actors":len(actors),"new_visual_actors":len(new),
            "distinct_imported_static_meshes":len(referenced),
            "milestones_preserved":list(stage.MILESTONES),
            "player_starts":1,"physics_verified":False,
            "pie_verified":False,"render_verified":False,"art_approved":False}
    readback.parent.mkdir(parents=True,exist_ok=True)
    with readback.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,indent=2,sort_keys=True)
    unreal.log("TSTSS_SLICE_OBJECT_INDEPENDENT_NATIVE_READBACK_PASS_NOT_PIE "+before)
    return result

if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
