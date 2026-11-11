#!/usr/bin/env python3
"""Opt-in native UE5.8.4 First Wake PBR lookdev derived World stage.

Exactly 115 original actors, all 7 milestone interactions and original collision
geometry are retained. This NEVER saves over the 115-actor source map.
Uses review-only textured materials and collision-disabled decorative geometry.
Source validation cannot establish native import, gameplay, visual approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import generate_first_wake_pbr_textures_v3 as pbr
import plan_first_wake_material_lookdev_v3 as plan

EXPECTED_HEAD="b7b741e0259c1fe0fefe3d078b7b6e7b2dfbc423"
OPT_IN="TSTSS_FIRST_WAKE_PBR_V3_EXPLICIT"
DETAIL_PREFIX=plan.PREFIX
PARENT_REL=plan.BASE_PATH
DEST_REL=plan.DEST_PATH
RECEIPT_REL=plan.RECEIPT
MATERIAL_DIR=plan.MATERIAL_DIR
TEXTURE_DIR=plan.TEXTURE_DIR
BASE=plan.BASE_LEVEL
DEST=plan.DEST_LEVEL
FLOOR=plan.FLOOR_LABEL
FLOOR_ROLE="quay_stone"
REPLACEMENTS={
    "TSTSS_PRELUDE_REVIEW_Harbor_TraversalFloor":"quay_stone",
    "TSTSS_PRELUDE_REVIEW_QuaysideWall":"quay_stone",
    "TSTSS_PRELUDE_REVIEW_HarborStorehouseBlockout":"harbor_plaster",
    "TSTSS_PRELUDE_REVIEW_GangwayVisualMarker":"dock_timber",
    "TSTSS_ENV_HARBOR_V1_QuaySouthWall":"quay_stone",
    "TSTSS_ENV_HARBOR_V1_OuterStonePier":"quay_stone",
    "TSTSS_ENV_HARBOR_V1_BoardingGangplankVisual":"dock_timber",
    "TSTSS_ENV_HARBOR_V1_HarborCustomsHouse":"harbor_plaster",
    "TSTSS_ENV_HARBOR_V1_CustomsRoof":"warm_roof",
    "TSTSS_ENV_HARBOR_V1_IoniaOfficeFacade":"harbor_plaster",
    "TSTSS_ENV_HARBOR_V1_IoniaOfficeRoof":"warm_roof",
    "TSTSS_ENV_HARBOR_V1_HarmonicEngineeringShop":"harbor_plaster",
    "TSTSS_ENV_HARBOR_V1_EngineeringShopRoof":"warm_roof",
    "TSTSS_ENV_HARBOR_V1_DrydockServiceShed":"harbor_plaster",
    "TSTSS_ENV_HARBOR_V1_DrydockRoof":"warm_roof",
    "TSTSS_ENV_HARBOR_V1_WorkshopSmokestack":"patina_metal",
    "TSTSS_ENV_HARBOR_V1_CanvasMarketAwning":"ochre_canvas",
    "TSTSS_ENV_HARBOR_V1_CopperSignalTower":"dark_copper",
}
SIGN_PREFIX="TSTSS_PRELUDE_REVIEW_SIGN_"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def validate_source():
    previous=plan.validate_plan()
    if previous["expected_original_actors"]!=115 or previous["from_sha"]!=plan.BASE_SHA:
        raise RuntimeError("HOLD: new lookdev plan no longer extends approved 115-actor World")
    if set(REPLACEMENTS.values())-set(plan.MATERIALS):
        raise RuntimeError("HOLD: unregistered material replacement role")
    if set(plan.MATERIALS)!=set(pbr.ROLES):
        raise RuntimeError("HOLD: PBR texture roles and native material palette diverged")
    report=pbr.verify()
    if report["texture_count"]!=30:
        raise RuntimeError("HOLD: source PBR textures incomplete")
    if FLOOR not in REPLACEMENTS or REPLACEMENTS[FLOOR]!="quay_stone":
        raise RuntimeError("HOLD: traversal floor must retain geometry with one PBR replacement")
    return {"status":"PBR_V3_SOURCE_PLAN_VALID_NOT_NATIVE",
            "source_native_world_sha256":plan.BASE_SHA,
            "new_world":DEST,"original_actors_preserved":115,
            "review_details":len(plan.DETAILS),
            "expected_new_actor_count":len(plan.DETAILS)+1,
            "textures":30,"material_roles":len(pbr.ROLES),
            "floor_collision_touched":False,
            "story_interaction_touched":False,
            "developer_signs_deleted":False,
            "native_materials_imported":False,"pie_verified":False,
            "gpu_visual_reviewed":False,"art_approved":False}

def spawn_native():
    summary=validate_source()
    import unreal
    project=Path(unreal.Paths.project_dir()).resolve()
    if project.name.lower()!="unreal" or project.parent.name!=plan.ROOT_NAME:
        raise RuntimeError("HOLD: wrong isolated lookdev worktree")
    if os.environ.get(OPT_IN)!="1":
        raise RuntimeError("HOLD: explicit guarded host opt-in absent")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: UE 5.8.4 required")
    parent=project/PARENT_REL
    original=project/plan.ORIGINAL_PATH
    dest=project/DEST_REL
    receipt=project/RECEIPT_REL
    parent_native=project/"Saved/FirstWakeSliceObjectsV1/native_objects_readback.json"
    if not all(x.is_file() for x in (parent,original,parent_native)):
        raise RuntimeError("HOLD: previous saved World/receipt absent")
    native=json.loads(parent_native.read_text(encoding="utf-8"))
    if (sha(parent)!=plan.BASE_SHA or sha(original)!=plan.ORIGINAL_SHA or
            native.get("status")!="INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE" or
            native.get("saved_world_sha256")!=plan.BASE_SHA or
            native.get("actors")!=115 or native.get("new_visual_actors")!=31 or
            native.get("distinct_imported_static_meshes")!=22):
        raise RuntimeError("HOLD: original genuinely native-readback scene diverged")
    if (dest.exists() or receipt.exists() or
            unreal.EditorAssetLibrary.does_asset_exist(DEST) or
            unreal.EditorAssetLibrary.does_directory_exist(MATERIAL_DIR)):
        raise RuntimeError("HOLD: derived map/material receipt already exists")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: user Editor has dirty map")
    if list((project/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGames present")
    configs=[project/"Config/DefaultEngine.ini",project/"Config/DefaultInput.ini"]
    config_sha={p.name:sha(p) for p in configs}
    parent_sha=sha(parent);original_sha=sha(original)
    library=unreal.EditorAssetLibrary
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    if not library.make_directory(MATERIAL_DIR):
        raise RuntimeError("HOLD: cannot create isolated PBR materials directory")
    if not library.make_directory(TEXTURE_DIR):
        raise RuntimeError("HOLD: cannot create private PBR texture directory")
    manifest=json.loads((pbr.OUT/"manifest.json").read_text(encoding="utf-8"))
    tasks=[]
    for item in manifest["textures"]:
        name=item["name"]
        task=unreal.AssetImportTask()
        task.set_editor_property("filename",str(pbr.OUT/name))
        task.set_editor_property("destination_path",TEXTURE_DIR)
        task.set_editor_property("destination_name",Path(name).stem)
        task.set_editor_property("automated",True)
        task.set_editor_property("replace_existing",False)
        task.set_editor_property("save",True)
        tasks.append(task)
    tools.import_asset_tasks(tasks)
    textures={}
    for item,task in zip(manifest["textures"],tasks):
        name=Path(item["name"]).stem
        paths=list(task.get_editor_property("imported_object_paths"))
        hits=[unreal.load_asset(x) for x in paths]
        hits=[x for x in hits if isinstance(x,unreal.Texture2D)]
        if len(hits)!=1:
            raise RuntimeError("HOLD: expected one native Texture2D for "+name)
        texture=hits[0]
        if item["channel"] in ("Normal","Roughness"):
            texture.set_editor_property("srgb",False)
            if not library.save_loaded_asset(texture):
                raise RuntimeError("HOLD: cannot save linear data texture "+name)
        textures[(item["material"],item["channel"])]=texture
    if len(textures)!=30:
        raise RuntimeError("HOLD: imported native PBR textures incomplete")
    materials={}
    edit=unreal.MaterialEditingLibrary
    for role in sorted(pbr.ROLES):
        mat=tools.create_asset("M_FWV3_"+role,MATERIAL_DIR,unreal.Material,unreal.MaterialFactoryNew())
        if not isinstance(mat,unreal.Material):
            raise RuntimeError("HOLD: failed to create native Material "+role)
        tiling=8.0 if role=="quay_stone" else 3.0
        if role in ("blue_green_glass","sea_foam"):tiling=1.0
        coord=edit.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-600,130)
        coord.set_editor_property("u_tiling",tiling)
        coord.set_editor_property("v_tiling",tiling)
        for channel,prop,output,y in (
            ("BaseColor",unreal.MaterialProperty.MP_BASE_COLOR,"RGB",-300),
            ("Normal",unreal.MaterialProperty.MP_NORMAL,"RGB",0),
            ("Roughness",unreal.MaterialProperty.MP_ROUGHNESS,"R",300)):
            sample=edit.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-300,y)
            sample.set_editor_property("texture",textures[(role,channel)])
            if not edit.connect_material_expressions(coord,"",sample,"Coordinates"):
                raise RuntimeError("HOLD: cannot bind native PBR UV "+role+channel)
            if not edit.connect_material_property(sample,output,prop):
                raise RuntimeError("HOLD: cannot bind native PBR channel "+role+channel)
        metal=pbr.ROLES[role][2]/255.0
        scalar=edit.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,540)
        scalar.set_editor_property("r",metal)
        if not edit.connect_material_property(scalar,"",unreal.MaterialProperty.MP_METALLIC):
            raise RuntimeError("HOLD: metallic graph disconnected "+role)
        errors=edit.recompile_material(mat)
        if errors:
            raise RuntimeError("HOLD: material compile error: "+role+": "+str(errors))
        if not library.save_loaded_asset(mat):
            raise RuntimeError("HOLD: native PBR material not saved "+role)
        materials[role]=mat
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level_from_template(DEST,BASE):
        raise RuntimeError("HOLD: derived V3 World creation failed")
    system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=list(system.get_all_level_actors())
    labels=[a.get_actor_label() for a in actors]
    if len(actors)!=115 or len(set(labels))!=115:
        raise RuntimeError("HOLD: native 115-actor source level not preserved")
    for milestone in plan.MILESTONES:
        if labels.count("TSTSS_PRELUDE_REVIEW_"+milestone)!=1:
            raise RuntimeError("HOLD: authoritatively interactive milestone missing "+milestone)
        if labels.count(SIGN_PREFIX+milestone)!=1:
            raise RuntimeError("HOLD: developer review sign was removed unexpectedly")
    if sum(isinstance(a,unreal.PlayerStart) for a in actors)!=1:
        raise RuntimeError("HOLD: native PlayerStart changed")
    targets={}
    for a in actors:
        label=a.get_actor_label()
        if label in REPLACEMENTS:
            if not isinstance(a,unreal.StaticMeshActor):
                raise RuntimeError("HOLD: target structure is not a static mesh "+label)
            targets[label]=a
    if set(targets)!=set(REPLACEMENTS):
        raise RuntimeError("HOLD: expected original world materials target set changed "+
                           str(set(REPLACEMENTS)-set(targets)))
    floor=targets[FLOOR]
    floor_comp=floor.static_mesh_component
    old_floor_mesh=floor_comp.get_editor_property("static_mesh")
    old_floor_collision=floor_comp.get_collision_enabled()
    if old_floor_collision!=unreal.CollisionEnabled.QUERY_AND_PHYSICS:
        raise RuntimeError("HOLD: original collision floor not physically solid")
    original_positions={label:(a.get_actor_location(),a.get_actor_scale3d())
                        for label,a in targets.items()}
    for label,actor in targets.items():
        actor.static_mesh_component.set_material(0,materials[REPLACEMENTS[label]])
    newlabels=[]
    meshes={n:unreal.load_asset("/Engine/BasicShapes/"+n+"."+n)
            for n in ("Cube","Cylinder")}
    if not all(isinstance(m,unreal.StaticMesh) for m in meshes.values()):
        raise RuntimeError("HOLD: basic native detail meshes not available")
    for item in plan.DETAILS:
        a=system.spawn_actor_from_class(unreal.StaticMeshActor,
                                        unreal.Vector(*item.xyz),unreal.Rotator())
        if a is None:raise RuntimeError("HOLD: decorative native asset spawn failed "+item.name)
        a.set_actor_label(DETAIL_PREFIX+item.name)
        component=a.static_mesh_component
        if not component.set_static_mesh(meshes[item.mesh]):
            raise RuntimeError("HOLD: decorative base mesh not assigned")
        component.set_material(0,materials[item.role])
        a.set_actor_scale3d(unreal.Vector(*item.scale))
        a.set_actor_enable_collision(False)
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        if component.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("HOLD: decorative asset unexpectedly collides")
        newlabels.append(a.get_actor_label())
    eye=unreal.Vector(*plan.PIER_LOCATION)
    focus=unreal.Vector(*plan.PIER_TARGET)
    camera=system.spawn_actor_from_class(unreal.CameraActor,eye,
                                          unreal.MathLibrary.find_look_at_rotation(eye,focus))
    if camera is None:raise RuntimeError("HOLD: optional V3 review camera absent")
    camera.set_actor_label(DETAIL_PREFIX+"PierReviewCamera")
    newlabels.append(camera.get_actor_label())
    # Crucial: text and interaction actor inventory preserved; capture-only label
    # suppression must be done transiently in the review camera script.
    after=system.get_all_level_actors()
    final_labels=[a.get_actor_label() for a in after]
    if len(after)!=115+len(newlabels) or len(set(final_labels))!=len(after):
        raise RuntimeError("HOLD: derived level actor count or unique IDs failed")
    for label,actor in targets.items():
        loc,scale=original_positions[label]
        if (actor.get_actor_location()!=loc or actor.get_actor_scale3d()!=scale):
            raise RuntimeError("HOLD: inherited structure geometry changed "+label)
    if (floor_comp.get_editor_property("static_mesh")!=old_floor_mesh or
            floor_comp.get_collision_enabled()!=old_floor_collision):
        raise RuntimeError("HOLD: traversal floor collision/geometry mutated")
    if not levels.save_current_level():
        raise RuntimeError("HOLD: derived V3 world failed native save")
    if (not dest.is_file() or sha(parent)!=parent_sha or
            sha(original)!=original_sha or
            any(sha(p)!=config_sha[p.name] for p in configs)):
        raise RuntimeError("HOLD: original maps/config mutated by review stage")
    result=dict(summary,status="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                new_map_sha256=sha(dest),
                parent_map_sha256=parent_sha,
                original_map_sha256=original_sha,
                new_actor_labels=newlabels,new_actors=len(newlabels),
                saved_actor_count=len(after),
                native_texture_assets=len(textures),
                native_material_assets=len(materials),
                original_floor_collision_preserved=True,
                original_floor_mesh_preserved=True,
                original_interaction_markers_preserved=True,
                debug_sign_actors_retained=True,
                native_gpu_render_verified=False,
                pie_verified=False,art_approved=False,
                engine_version=unreal.SystemLibrary.get_engine_version())
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2)
    unreal.log("FIRSTWAKE_PBR_V3_NATIVE_SAVED_NOT_PIE "+result["new_map_sha256"])
    return result

def main():
    if os.environ.get(OPT_IN)=="1":
        print(json.dumps(spawn_native(),sort_keys=True,indent=2))
        return
    p=argparse.ArgumentParser()
    p.add_argument("--validate",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(validate_source(),sort_keys=True,indent=2))
if __name__=="__main__":
    main()
