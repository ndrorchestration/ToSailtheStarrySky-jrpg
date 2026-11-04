"""Native UE 5.8.4 *staging only* for isolated Skybourne horizon/atmosphere review.

Creates a NEW private level by duplicating a hash-pinned V4 preview map.
Never save/edit original maps or production actors. Not a beauty-render claim.
Native import/staging is NOT transactional: occupied paths must be investigated,
not automatically cleaned/retried. Run only through resource-gated host runner.
"""
from pathlib import Path
import hashlib
import json
import os
import traceback
import unreal

ROOT = Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT = ROOT / "AureateCinematicV4Sandbox"
SOURCE = "/Game/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor"
TARGET = "/Game/TSTSS/Review/Scenes/AureateV4_Skybourne_HorizonAtmosphere_ReviewV1"
SOURCE_FILE = PROJECT/"Content/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap"
SOURCE_SHA = "16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40"
MATERIAL_FOLDER = "/Game/TSTSS/Review/Environment/V4HorizonReviewV1"
CAMERA_NAME = "V4_NONCANONICAL_CAMERA_HORIZON_HERO_REVIEWV1"
RECEIPT = os.environ.get("TSTSS_V4_HORIZON_RECEIPT", "")
status = {"state":"NOT_STAGED", "authority":"NONCANONICAL_HORIZON_VISUAL_REVIEW_ONLY",
          "source_map_sha_expected":SOURCE_SHA, "source_map_modified":False,
          "gpu_screenshot_generated":False, "creator_art_approved":False,
          "gameplay_or_saves_changed":False, "starbourne_player_unlocked":False,
          "attempted_native_editor_stage":True}

if not RECEIPT:
    raise RuntimeError("Unique host receipt path required before Unreal stage")
receipt_path = Path(RECEIPT)
if receipt_path.exists() or ROOT not in receipt_path.parents:
    raise RuntimeError("Receipt must be a new path inside isolated V4 root")

def hashfile(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def one(actors, label):
    matches = [x for x in actors if x.get_actor_label() == label]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one native review actor "+label)
    return matches[0]

def spawn(actors, cls, name, position=(0,0,0)):
    actor = actors.spawn_actor_from_class(cls,unreal.Vector(*position))
    if actor is None:
        raise RuntimeError("Native actor spawn failed "+name)
    actor.set_actor_label(name)
    return actor

try:
    if Path(unreal.Paths.project_dir()).resolve() != PROJECT.resolve():
        raise RuntimeError("Not the existing isolated V4 Unreal sandbox")
    config = json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf-8"))
    if (config.get("EngineAssociation")!="5.8" or
       "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in config.get("Description","")):
        raise RuntimeError("Not the expected disposable review project")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8."):
        raise RuntimeError("Engine 5.8 mismatch; no rendering permitted")
    if not SOURCE_FILE.is_file() or hashfile(SOURCE_FILE)!=SOURCE_SHA:
        raise RuntimeError("Original review map SHA mismatch")
    lib = unreal.EditorAssetLibrary
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lib.does_asset_exist(SOURCE) or lib.does_asset_exist(TARGET):
        raise RuntimeError("Source map missing or new review target already occupied")
    if lib.does_directory_exist(MATERIAL_FOLDER):
        raise RuntimeError("Existing V4 horizon material folder: refuse overwrite/reuse")
    if not lib.duplicate_asset(SOURCE,TARGET):
        raise RuntimeError("Native level copy failed")
    if not levels.load_level(TARGET):
        raise RuntimeError("New review level could not be loaded")
    original = actors.get_all_level_actors()
    status["original_actor_labels"]=[a.get_actor_label() for a in original]
    if len(original)!=18:
        raise RuntimeError("Unexpected source Skybourne actor count")
    one(original,"V4_NONCANONICAL_CAMERA_THREE_QUARTER")
    one(original,"V4_NONCANONICAL_SHARED_HULL_CINEMATIC_V4_TRIM")
    for identity in ("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD"):
        one(original,"V4_NONCANONICAL_"+identity+"_V4_GOLD_FILIGREE")

    # Preserve the old comparison camera as-is. This new role is angled near
    # the local horizon, not down toward a view consisting entirely of ocean.
    cp=unreal.Vector(900.0,1100.0,190.0)
    at=unreal.Vector(0.0,0.0,80.0)
    orientation=unreal.MathLibrary.find_look_at_rotation(cp,at)
    camera=actors.spawn_actor_from_class(unreal.CameraActor,cp,orientation)
    if camera is None:raise RuntimeError("Horizon camera creation failed")
    camera.set_actor_label(CAMERA_NAME)
    cc=camera.get_component_by_class(unreal.CameraComponent)
    if cc is None:raise RuntimeError("New camera component missing")
    cc.set_editor_property("field_of_view",42.0)

    # Physically based procedural atmosphere, not the black-sky textured sphere
    # from #705 or the failed developer-only cyclorama from earlier V4 trials.
    if not hasattr(unreal,"SkyAtmosphere"):
        raise RuntimeError("SkyAtmosphere unavailable in this native editor")
    sky=spawn(actors,unreal.SkyAtmosphere,"V4_REVIEW_SKY_ATMOSPHERE_NONCANONICAL")
    sun=one(original,"V4_NONCANONICAL_DIRECTIONAL_KEYLIGHT")
    sunlight=sun.get_component_by_class(unreal.DirectionalLightComponent)
    if sunlight is None:
        raise RuntimeError("Original directional sun light component missing")
    sunlight.set_editor_property("atmosphere_sun_light",True)
    sunlight.set_editor_property("atmosphere_sun_light_index",0)
    skylight=spawn(actors,unreal.SkyLight,"V4_REVIEW_SKYLIGHT_NONCANONICAL",
                   (0.0,0.0,400.0))
    if not hasattr(unreal,"ExponentialHeightFog"):
        raise RuntimeError("Height fog actor unavailable in this native editor")
    fog=spawn(actors,unreal.ExponentialHeightFog,
              "V4_REVIEW_HEIGHT_FOG_LOW_DENSITY_NONCANONICAL")
    fc=fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    if fc is None:raise RuntimeError("Review fog component missing")
    fc.set_editor_property("fog_density",0.004)

    # New private PBR ocean study. Not the earlier failed two-sided sky shader
    # or a simulation. It makes the lower hemisphere visually grounded.
    if not lib.make_directory(MATERIAL_FOLDER):
        raise RuntimeError("Could not create isolated material directory")
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_V4_HorizonOcean_Diagnostic",MATERIAL_FOLDER,unreal.Material,
        unreal.MaterialFactoryNew())
    if not isinstance(mat,unreal.Material):
        raise RuntimeError("Could not create ocean study material")
    edit=unreal.MaterialEditingLibrary
    rgb=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-340,0)
    rgb.set_editor_property("constant",unreal.LinearColor(0.025,0.13,0.20,1.0))
    rough=edit.create_material_expression(mat,unreal.MaterialExpressionConstant,-340,240)
    rough.set_editor_property("r",0.28)
    if (not edit.connect_material_property(rgb,"",unreal.MaterialProperty.MP_BASE_COLOR)
        or not edit.connect_material_property(rough,"",unreal.MaterialProperty.MP_ROUGHNESS)):
        raise RuntimeError("PBR ocean inputs did not bind")
    errors=edit.recompile_material(mat)
    if errors:raise RuntimeError("PBR material compile error: "+str(errors))
    if not lib.save_loaded_asset(mat):
        raise RuntimeError("Failed to save new, unique review material")
    plane=unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
    cylinder=unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
    if not isinstance(plane,unreal.StaticMesh) or not isinstance(cylinder,unreal.StaticMesh):
        raise RuntimeError("Missing engine-only review meshes")
    sea=spawn(actors,unreal.StaticMeshActor,"V4_REVIEW_OCEAN_NO_PHYSICS",
              (0.0,0.0,-165.0))
    sea.set_actor_scale3d(unreal.Vector(650,650,1))
    sea.set_actor_enable_collision(False)
    sm=sea.get_component_by_class(unreal.StaticMeshComponent)
    if sm is None or not sm.set_static_mesh(plane):
        raise RuntimeError("Native ocean display mesh failed")
    sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    sm.set_material(0,mat)
    # Noncanonical anonymous 170 cm *proposal*. Actual mesh bbox must be
    # read back before any physical human-scale conclusions are drawn.
    crew=spawn(actors,unreal.StaticMeshActor,"V4_REVIEW_ANONYMOUS_CREW_SCALE_PROXY",
               (255.0,0.0,140.0))
    crew.set_actor_scale3d(unreal.Vector(0.30,0.30,1.70))
    crew.set_actor_enable_collision(False)
    cm=crew.get_component_by_class(unreal.StaticMeshComponent)
    if cm is None or not cm.set_static_mesh(cylinder):
        raise RuntimeError("Crew visual scale mesh failed")
    cm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    status["review_added_labels"]=[x.get_actor_label() for x in
                                  (camera,sky,skylight,fog,sea,crew)]
    if len(set(status["review_added_labels"]))!=6:
        raise RuntimeError("Duplicate new review actor identity")
    if not levels.save_current_level():
        raise RuntimeError("Could not save new disposable horizon review map")
    status["source_map_sha_after"]=hashfile(SOURCE_FILE)
    if status["source_map_sha_after"]!=SOURCE_SHA:
        raise RuntimeError("Original native map changed: reject stage")
    new_file=PROJECT/"Content/TSTSS/Review/Scenes/AureateV4_Skybourne_HorizonAtmosphere_ReviewV1.umap"
    if not new_file.is_file():
        raise RuntimeError("New Unreal review map was not saved")
    status.update({"state":"NATIVE_HORIZON_STAGE_REVIEW_MAP_ONLY_PASS",
        "engine":unreal.SystemLibrary.get_engine_version(),
        "new_map_path":TARGET,"new_map_sha256":hashfile(new_file),
        "new_map_actor_count":len(actors.get_all_level_actors()),
        "camera":CAMERA_NAME,"ocean_height_cm_provisional":-165.0,
        "sky_render_verified":False,"ocean_render_verified":False,
        "human_scale_real_dimensions_verified":False,
        "original_four_form_maps_changed":False})
except Exception as exc:
    status["state"]="NATIVE_HORIZON_STAGE_FAILED_NOT_RENDERED"
    status["error"]=str(exc)
    status["traceback"]=traceback.format_exc()[-3500:]
finally:
    receipt_path.write_text(json.dumps(status,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    unreal.log("AUREATE_V4_HORIZON_NATIVE_STAGE "+json.dumps(status,sort_keys=True))
if status["state"]!="NATIVE_HORIZON_STAGE_REVIEW_MAP_ONLY_PASS":
    raise RuntimeError(status.get("error","Native review stage not proven"))
