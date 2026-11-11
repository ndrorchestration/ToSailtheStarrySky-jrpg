#!/usr/bin/env python3
"""Independent separate-process UE5.8 saved V3 PBR World readback.

A native map+material inventory pass is NOT D3D visual acceptance or PIE.
Does not save World, author assets, change story markers or touch user saves.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import stage_first_wake_pbr_native_v3 as stage
import plan_first_wake_material_lookdev_v3 as plan
import generate_first_wake_pbr_textures_v3 as pbr

RECEIPT="Saved/FirstWakeMaterialLookdevV3/native_independent_readback.json"
STATUS="INDEPENDENT_NATIVE_PBR_V3_READBACK_PASS_NOT_PIE"

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def exact_inventory(labels,expected_new):
    if len(labels)!=115+len(plan.DETAILS)+1 or len(labels)!=len(set(labels)):
        raise RuntimeError("HOLD: wrong total actor inventory in derived World")
    for milestone in plan.MILESTONES:
        for prefix in ("TSTSS_PRELUDE_REVIEW_",stage.SIGN_PREFIX):
            if labels.count(prefix+milestone)!=1:
                raise RuntimeError("HOLD: story/sign actor missing or duplicated "+milestone)
    actual={s for s in labels if s.startswith(stage.DETAIL_PREFIX)}
    if len(actual)!=len(plan.DETAILS)+1 or actual!=set(expected_new):
        raise RuntimeError("HOLD: new V3 material details/camera changed")
    if any("Starbourne" in name for name in labels):
        raise RuntimeError("HOLD: restricted ship config unexpectedly present")
    return True

def verify():
    import unreal
    root=Path(unreal.Paths.project_dir()).resolve()
    if root.name.lower()!="unreal" or root.parent.name!=plan.ROOT_NAME:
        raise RuntimeError("HOLD: wrong native readback worktree")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: exact UE5.8.4 required")
    saved=root/stage.DEST_REL
    original=root/stage.PARENT_REL
    receipt=root/stage.RECEIPT_REL
    out=root/RECEIPT
    if not all(p.is_file() for p in (saved,original,receipt)):
        raise RuntimeError("HOLD: native stage map or receipt absent")
    if out.exists():raise RuntimeError("HOLD: prior readback file cannot be overwritten")
    if list((root/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGames present")
    native=json.loads(receipt.read_text(encoding="utf-8"))
    before=digest(saved)
    if (native.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            native.get("new_map_sha256")!=before or
            native.get("parent_map_sha256")!=plan.BASE_SHA or
            digest(original)!=plan.BASE_SHA or
            native.get("native_texture_assets")!=30 or
            native.get("native_material_assets")!=10 or
            native.get("original_floor_collision_preserved") is not True or
            native.get("original_interaction_markers_preserved") is not True):
        raise RuntimeError("HOLD: original native V3 staging receipt drifted")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty Editor state")
    if not unreal.EditorLoadingAndSavingUtils.load_map(plan.DEST_LEVEL):
        raise RuntimeError("HOLD: cannot load saved V3 PBR World")
    system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=list(system.get_all_level_actors())
    labels=[a.get_actor_label() for a in actors]
    exact_inventory(labels,native["new_actor_labels"])
    if sum(isinstance(a,unreal.PlayerStart) for a in actors)!=1:
        raise RuntimeError("HOLD: original player start lost/duplicated")
    bylabel={a.get_actor_label():a for a in actors}
    floor=bylabel.get(stage.FLOOR)
    if not isinstance(floor,unreal.StaticMeshActor):
        raise RuntimeError("HOLD: traversal floor class changed")
    comp=floor.static_mesh_component
    if comp.get_collision_enabled()!=unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("HOLD: material stage broke traversable collision")
    if (floor.get_actor_location()!=unreal.Vector(-600,0,-100) or
            floor.get_actor_scale3d()!=unreal.Vector(63,14,2)):
        raise RuntimeError("HOLD: original traversal floor geometry moved/rescaled")
    mesh=comp.get_editor_property("static_mesh")
    if mesh is None or mesh.get_path_name()!="/Engine/BasicShapes/Cube.Cube":
        raise RuntimeError("HOLD: original traversal floor collision mesh replaced")
    replaced=set()
    for label,role in stage.REPLACEMENTS.items():
        actor=bylabel.get(label)
        if not isinstance(actor,unreal.StaticMeshActor):
            raise RuntimeError("HOLD: source structure identity changed "+label)
        material=actor.static_mesh_component.get_material(0)
        if material is None or material.get_path_name()!=(plan.MATERIAL_DIR+"/M_FWV3_"+role+
                                                        ".M_FWV3_"+role):
            raise RuntimeError("HOLD: PBR material not bound to correct native structure "+label)
        replaced.add(label)
    details=[]
    for label in native["new_actor_labels"]:
        actor=bylabel[label]
        if label.endswith("PierReviewCamera"):
            if not isinstance(actor,unreal.CameraActor):
                raise RuntimeError("HOLD: derivative review camera not a camera")
            continue
        if not isinstance(actor,unreal.StaticMeshActor):
            raise RuntimeError("HOLD: decorative actor not a static mesh")
        c=actor.static_mesh_component
        if c.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("HOLD: decorative actor unexpectedly collides")
        material=c.get_material(0)
        if material is None or not material.get_path_name().startswith(plan.MATERIAL_DIR+"/"):
            raise RuntimeError("HOLD: derivative detail lacks review material")
        details.append(label)
    if len(details)!=len(plan.DETAILS):
        raise RuntimeError("HOLD: derivative detail count changed")
    signs=[]
    for s in plan.MILESTONES:
        sign=bylabel[stage.SIGN_PREFIX+s]
        if not isinstance(sign,unreal.TextRenderActor):
            raise RuntimeError("HOLD: native developer sign class not preserved")
        signs.append(sign.get_actor_label())
    for role in pbr.ROLES:
        material=unreal.load_asset(plan.MATERIAL_DIR+"/M_FWV3_"+role)
        if not isinstance(material,unreal.Material):
            raise RuntimeError("HOLD: referenced native material package absent "+role)
        for channel in pbr.CHANNELS:
            tex=unreal.load_asset(plan.TEXTURE_DIR+"/TX_FWV3_"+role+"_"+channel)
            if not isinstance(tex,unreal.Texture2D):
                raise RuntimeError("HOLD: source PBR texture absent "+role+channel)
    if digest(saved)!=before or digest(original)!=plan.BASE_SHA:
        raise RuntimeError("HOLD: source/derived map bytes changed during readback")
    report={"status":STATUS,"engine":unreal.SystemLibrary.get_engine_version(),
            "derived_world_sha256":before,"parent_world_sha256":plan.BASE_SHA,
            "actors":len(actors),"new_visual_only_mesh_actors":len(details),
            "original_actors_inherited":115,
            "new_camera_count":1,"materials_replaced_on_inherited_actors":len(replaced),
            "native_texture_assets_reloaded":30,"native_material_assets_reloaded":10,
            "preserved_interactions":list(plan.MILESTONES),
            "preserved_signs":signs,"original_floor_collision_verified":True,
            "original_floor_geometry_verified":True,
            "new_detail_collision_disabled":True,
            "gpu_render_verified":False,"pie_verified":False,
            "art_approved":False,"physics_splashdown_verified":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,sort_keys=True)
    unreal.log("FIRSTWAKE_PBR_V3_INDEPENDENT_READBACK_PASS_NOT_PIE "+before)
    return report

if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
