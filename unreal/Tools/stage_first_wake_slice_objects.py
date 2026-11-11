#!/usr/bin/env python3
"""Opt-in UE5.8.4 importer + new independent first-wake object-stage map.

Preserves seven real milestone interaction actors, player spawn, harbor and
ship/character review scene. Never edits original V3 or Harbor World.
Source validation does not claim native import, rendering or PIE verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_first_wake_slice_objects as objects

ROOT_NAME = "TSTSS_VSliceObjects_20261110"
SOURCE_MAP = "/Game/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1"
NEW_MAP = "/Game/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1"
SOURCE_MAP_REL = "Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap"
NEW_MAP_REL = "Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap"
SOURCE_RECEIPT_REL = "Saved/FirstWakeEnvironmentV1/native_harbor_stage.json"
DEST_RECEIPT_REL = "Saved/FirstWakeSliceObjectsV1/native_objects_stage.json"
IMPORT_DIR = "/Game/TSTSS/Review/Objects/FirstWakeSliceV1"
ACTOR_PREFIX = "TSTSS_SLICE_OBJ_V1_"
MILESTONES = (
    "FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation",
    "PressureStation","ReserveStation","EngineeringApproval"
)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def validate_source() -> dict:
    report, data=objects.inventory()
    manifest=objects.OUT/"manifest.json"
    if not manifest.is_file() or json.loads(manifest.read_text(encoding="utf-8"))!=report:
        raise RuntimeError("Missing/drifted source-art manifest")
    for name,blob in data.items():
        p=objects.OUT/(name+".glb")
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=hashlib.sha256(blob).hexdigest():
            raise RuntimeError("Missing/drifted source GLB: "+name)
    return {"status":"NATIVE_OBJECT_IMPORT_NOT_RUN","source_models":len(data),
            "planned_instances":len(report["placements"]),"source_map":SOURCE_MAP,
            "new_map":NEW_MAP,"native_actor_count_expected":84+len(report["placements"]),
            "gameplay_markers_preserved":list(MILESTONES),
            "physics_modified":False,"story_modified":False,"user_saves_modified":False}

def native_build() -> dict:
    result=validate_source()
    import unreal
    root=Path(unreal.Paths.project_dir()).resolve()
    if root.name.lower()!="unreal" or root.parent.name!=ROOT_NAME:
        raise RuntimeError("HOLD: refuse non-isolated object worktree")
    if os.environ.get("TSTSS_SLICE_OBJECT_STAGE_EXPLICIT")!="1":
        raise RuntimeError("HOLD: opt-in host launcher required")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: wrong Unreal Editor version")
    source=root/SOURCE_MAP_REL; dest=root/NEW_MAP_REL
    parent_receipt=root/SOURCE_RECEIPT_REL
    receipt=root/DEST_RECEIPT_REL
    if not source.is_file() or not parent_receipt.is_file():
        raise RuntimeError("HOLD: genuine native harbor World and receipt required")
    parent=json.loads(parent_receipt.read_text(encoding="utf-8"))
    if (parent.get("status")!="NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
            or parent.get("map_sha256")!=sha256(source)):
        raise RuntimeError("HOLD: parent saved Harbor World/receipt mismatch")
    if (dest.exists() or receipt.exists() or
            unreal.EditorAssetLibrary.does_asset_exist(NEW_MAP) or
            unreal.EditorAssetLibrary.does_directory_exist(IMPORT_DIR)):
        raise RuntimeError("HOLD: object output already exists; refuse overwrite")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty Editor World")
    if list((root/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing player SaveGames")
    configs=[root/"Config/DefaultEngine.ini",root/"Config/DefaultInput.ini"]
    before={p.name:sha256(p) for p in configs}
    parent_digest=sha256(source)
    # One asset per GLB. The imported source asset is one mesh with multi-material
    # primitives; no authored character, hull, ocean or executable spell is touched.
    library=unreal.EditorAssetLibrary
    if not library.make_directory(IMPORT_DIR):
        raise RuntimeError("HOLD: failed to make review objects folder")
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    tasks=[]
    for name in objects.ASSET_NAMES:
        task=unreal.AssetImportTask()
        task.set_editor_property("filename",str(objects.OUT/(name+".glb")))
        task.set_editor_property("destination_path",IMPORT_DIR)
        task.set_editor_property("destination_name",name)
        task.set_editor_property("automated",True)
        task.set_editor_property("replace_existing",False)
        task.set_editor_property("save",True)
        tasks.append(task)
    tools.import_asset_tasks(tasks)
    meshes={}
    for name,task in zip(objects.ASSET_NAMES,tasks):
        paths=list(task.get_editor_property("imported_object_paths"))
        candidates=[]
        for path in paths:
            asset=unreal.load_asset(path)
            if isinstance(asset,unreal.StaticMesh): candidates.append(asset)
        if len(candidates)!=1:
            raise RuntimeError("HOLD: expected one StaticMesh for "+name+", got "+repr(paths))
        meshes[name]=candidates[0]
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level_from_template(NEW_MAP,SOURCE_MAP):
        raise RuntimeError("HOLD: could not make NEW map from Harbor review World")
    actor_system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    original=actor_system.get_all_level_actors()
    labels=[actor.get_actor_label() for actor in original]
    if len(labels)!=84 or any(label.startswith(ACTOR_PREFIX) for label in labels):
        raise RuntimeError("HOLD: Harbor parent actor inventory changed")
    for marker in MILESTONES:
        if labels.count("TSTSS_PRELUDE_REVIEW_"+marker)!=1:
            raise RuntimeError("HOLD: missing native E-interaction marker "+marker)
    if sum(isinstance(a,unreal.PlayerStart) for a in original)!=1:
        raise RuntimeError("HOLD: expected exactly one preserved PlayerStart")
    if sum(isinstance(a,unreal.DirectionalLight) for a in original)!=1:
        raise RuntimeError("HOLD: original directional sun missing/duplicated")
    instances=[]
    for i, row in enumerate(json.loads((objects.OUT/"manifest.json").read_text())["placements"],1):
        actor=actor_system.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(row["x"],row["y"],row["z"]),
            unreal.Rotator(0,row["yaw"],0))
        if actor is None: raise RuntimeError("HOLD: actor spawn failure "+row["asset"])
        actor.set_actor_label(ACTOR_PREFIX+f"{i:02d}_"+row["asset"])
        component=actor.static_mesh_component
        if not component.set_static_mesh(meshes[row["asset"]]):
            raise RuntimeError("HOLD: native mesh binding failure "+row["asset"])
        actor.set_actor_scale3d(unreal.Vector(row["scale"],row["scale"],row["scale"]))
        actor.set_actor_enable_collision(False)
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        if component.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("HOLD: object collision unexpectedly active")
        instances.append(actor.get_actor_label())
    if not levels.save_current_level():
        raise RuntimeError("HOLD: new slice-object World did not save")
    if not dest.is_file() or sha256(source)!=parent_digest:
        raise RuntimeError("HOLD: target not saved or Harbor template mutated")
    if any(sha256(p)!=before[p.name] for p in configs):
        raise RuntimeError("HOLD: protected Unreal config changed")
    report=dict(result,status="NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                source_map_sha256=parent_digest,new_map_sha256=sha256(dest),
                actor_labels=instances,new_native_actor_count=len(instances),
                native_static_mesh_assets=len(meshes),
                engine_version=unreal.SystemLibrary.get_engine_version(),
                native_render_verified=False,pie_verified=False,
                art_approved=False,water_physics_verified=False)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
    unreal.log("TSTSS_SLICE_OBJECT_NATIVE_STAGE_SAVED_NOT_PIE "+report["new_map_sha256"])
    return report

def main(argv=None):
    # Unreal's -ExecutePythonScript need not expose an ordinary sys.argv.
    # Native authoring is therefore possible only via the opted-in host runner.
    if argv is None and os.environ.get("TSTSS_SLICE_OBJECT_STAGE_EXPLICIT")=="1":
        argv=["--build"]
    args=argparse.ArgumentParser()
    modes=args.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate",action="store_true")
    modes.add_argument("--build",action="store_true")
    x=args.parse_args(argv)
    output=native_build() if x.build else validate_source()
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
