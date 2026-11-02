#!/usr/bin/env python3
"""Unreal Editor ONLY: duplicate the V3 Skyborne review, add sky/ocean lookdev.

Requires TSTSS_AUREATE_SKY_SEA_SOURCE_DIR from offline deterministic generator.
Fail closed if any review destination is occupied; create no gameplay bindings.
Native Unreal asset writes are NOT transactional: failures require manual review
of isolated paths before retrying. Review-only textures are not ocean physics.
"""
from __future__ import annotations
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal

STATUS="NONCANONICAL_ENVIRONMENT_LOOKDEV_NOT_GAMEPLAY"
ROOT="/Game/TSTSS/Review/Environment/SkySeaV1"
MAP="/Game/TSTSS/Review/Scenes/AureateWakeSkyborne_SkySeaReviewV1"
SOURCE="/Game/TSTSS/Review/Scenes/AureateWakeSkyborne_WingUVRepairV3"
FILES={
    "Sky":"AureateWake_SkyReviewV1.png",
    "Ocean":"AureateWake_OceanReviewV1.png",
}
lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assettools=unreal.AssetToolsHelpers.get_asset_tools()
report={"authority":STATUS,"source_map":SOURCE,"destination_map":MAP,
        "textures":{},"native_unreal_asset_stage":True}
receipt_path=os.environ.get("TSTSS_AUREATE_SKY_SEA_RECEIPT")
if not receipt_path:raise RuntimeError("A separate receipt path is required")

def stop(message):
    raise RuntimeError("ENVIRONMENT REVIEW HOLD: "+message)

def empty_assets(path):
    if lib.does_directory_exist(path) and lib.list_assets(path,recursive=True,include_folder=False):
        stop("already populated (no overwrite): "+path)

def import_texture(folder,name):
    target=ROOT+"/Textures"
    task=unreal.AssetImportTask()
    for k,v in (("filename",str(folder/name)),("destination_path",target),
                ("automated",True),("replace_existing",False),("save",True)):
        task.set_editor_property(k,v)
    assettools.import_asset_tasks([task])
    imported=list(task.get_editor_property("imported_object_paths"))
    matches=[unreal.load_asset(p) for p in imported if p.startswith(target+"/")]
    textures=[obj for obj in matches if isinstance(obj,unreal.Texture2D)]
    if len(textures)!=1:stop("texture failed import: "+name)
    report["textures"][name]=imported
    return textures[0]

def make_material(name,tex,sky):
    material=assettools.create_asset(name,ROOT+"/Materials",unreal.Material,
                                    unreal.MaterialFactoryNew())
    if not isinstance(material,unreal.Material):stop("material creation failed: "+name)
    mel=unreal.MaterialEditingLibrary
    node=mel.create_material_expression(material,unreal.MaterialExpressionTextureSample,-300,0)
    node.set_editor_property("texture",tex)
    if sky:
        material.set_editor_property("two_sided",True)
        # The shell is deliberately emissive and receives no scene shadows.
        try:material.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        except Exception:
            # Some UE versions only expose shading_models; emissive still works
            # with default-lit, but record that fallback explicitly.
            report["sky_unlit_fallback"]=True
        if not mel.connect_material_property(node,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR):
            stop("Could not bind sky texture to emissive")
    else:
        if not mel.connect_material_property(node,"RGB",unreal.MaterialProperty.MP_BASE_COLOR):
            stop("Could not bind ocean texture to base color")
        rough=mel.create_material_expression(material,unreal.MaterialExpressionConstant,0,230)
        rough.set_editor_property("r",0.19)
        if not mel.connect_material_property(rough,"",unreal.MaterialProperty.MP_ROUGHNESS):
            stop("Could not set ocean review roughness")
    mel.recompile_material(material)
    if not lib.save_loaded_asset(material):stop("Material save failed: "+name)
    return material

def add_surface(name,mesh,material,position,scale):
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*position))
    if not actor:stop("Actor spawn failed: "+name)
    actor.set_actor_label(name)
    comp=actor.static_mesh_component
    comp.set_static_mesh(mesh)
    comp.set_material(0,material)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property("cast_shadow",False)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    report.setdefault("review_actors",[]).append(name)
    return actor

try:
    folder_str=os.environ.get("TSTSS_AUREATE_SKY_SEA_SOURCE_DIR")
    if not folder_str:stop("missing explicitly specified source folder")
    folder=Path(folder_str).resolve(strict=True)
    manifest=json.loads((folder/"AureateWake_SkySeaReviewV1_Manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status")!=STATUS or manifest.get("orbiter")!="LOCKED" or manifest.get("target_scene")!=MAP or manifest.get("source_scene")!=SOURCE or manifest.get("target_assets")!=ROOT:
        stop("incompatible review manifest or unsafe gate provenance")
    for name in FILES.values():
        blob=(folder/name).read_bytes()
        if hashlib.sha256(blob).hexdigest()!=manifest.get("sha256",{}).get(name):
            stop("asset SHA-256 mismatch: "+name)
        if blob[:8]!=b"\x89PNG\r\n\x1a\n":
            stop("invalid PNG file: "+name)
    if not lib.does_asset_exist(SOURCE):stop("missing original isolated Skyborne map")
    if lib.does_asset_exist(MAP):stop("review scene already exists; no overwrite")
    empty_assets(ROOT)
    sky=import_texture(folder,FILES["Sky"])
    ocean=import_texture(folder,FILES["Ocean"])
    sky_mat=make_material("M_AureateSkyEmissionV1",sky,True)
    sea_mat=make_material("M_AureateOceanReviewV1",ocean,False)
    if not lib.duplicate_asset(SOURCE,MAP):stop("could not duplicate reference map")
    if not levels.load_level(MAP):stop("new environment map failed to load")
    ships=[a for a in actors.get_all_level_actors()
           if isinstance(a,unreal.AureateWakePreviewActor)]
    if len(ships)!=1 or not ships[0].is_authored_body_review_applied():
        stop("expected one intact reviewed authored hull+bridge ship")
    ship=ships[0]
    if (ship.get_wing_count(),ship.get_wing_root_mount_count(),
        ship.get_hydrofoil_count(),ship.get_hydrofoil_strut_count())!=(4,4,2,2):
        stop("ship component counts changed")
    if ship.request_form(unreal.AureateWakeForm.ORBITER):
        stop("Orbiter gate was bypassed")
    sphere=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    plane=unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
    if not isinstance(sphere,unreal.StaticMesh) or not isinstance(plane,unreal.StaticMesh):
        stop("Unreal basic review meshes missing")
    # Sky sphere is large enough to enclose the existing fixed camera.
    add_surface("REVIEW_AuroralSkySphere_NO_GAMEPLAY",sphere,sky_mat,
                (0,0,0),(4000,4000,4000))
    # Broad visual-only ocean well below the airborne hull. No collision.
    add_surface("REVIEW_OceanSurface_NO_BUOYANCY",plane,sea_mat,
                (0,0,-165),(650,650,1))
    report["wing_count"]=ship.get_wing_count()
    report["orbiter_request_rejected"]=True
    report["ocean_height_cm"]=-165
    report["saved"]=bool(levels.save_current_level())
    if not report["saved"]:stop("scene save failed")
    report["success"]=True
except Exception as e:
    report["success"]=False
    report["error"]=str(e)
    report["trace"]=traceback.format_exc()[-3000:]
Path(receipt_path).write_text(json.dumps(report,indent=2,sort_keys=True),encoding="utf-8")
unreal.log("TSTSS_ENV_REVIEW "+json.dumps(report))
if not report["success"]:raise RuntimeError(report["error"])
