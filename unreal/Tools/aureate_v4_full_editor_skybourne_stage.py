"""One Skybourne noncanonical assembly in UE 5.8.4 full Editor.

Only writes one NEW dedicated map in the earlier disposable V4 review sandbox.
Imported V4 meshes are reused, never modified. No native screenshot claim.
All component placements are temporary proposal positions, NOT approved forms.
"""
from pathlib import Path
import hashlib
import json
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
EXPECTED_ENGINE="5.8."
MAP="/Game/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor"
RECEIPT=ROOT/"full_editor_skybourne_stage_receipt.json"
IMPORTED=ROOT/"native_import_receipt.json"
report={"state":"NOT_VERIFIED","form":"Skybourne",
        "authority":"NONCANONICAL_ART_STAGING_ONLY",
        "production_actor_modified":False,
        "gameplay_or_save_modified":False,
        "starbourne_player_unlocked":False,
        "real_gpu_frame_generated":False,
        "wing_identity_labels":[],"native_asset_paths":[]}
if RECEIPT.exists():
    raise FileExistsError("Existing hero receipt; refuse repeated attempt")

try:
    assert Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"Not existing disposable V4 sandbox"
    projconf=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    assert "AUREATE_CINEMATIC_V4_REVIEW_ONLY" in projconf.get("Description","")
    assert unreal.SystemLibrary.get_engine_version().startswith(EXPECTED_ENGINE)
    imports=json.loads(IMPORTED.read_text(encoding="utf8"))
    assert imports.get("state")=="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS"
    lib=unreal.EditorAssetLibrary
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if lib.does_asset_exist(MAP):raise FileExistsError("Review map already exists, stop")
    def imported_mesh(fragment):
        matches=[v["object_path"] for name,v in imports["readback"].items() if fragment in name]
        if len(matches)!=1:raise RuntimeError("Wrong imported mesh count for "+fragment)
        m=unreal.load_asset(matches[0])
        if not isinstance(m,unreal.StaticMesh):raise RuntimeError("Native StaticMesh missing "+fragment)
        if len(m.get_editor_property("static_materials"))!=4:
            raise RuntimeError("Unexpected material slot drift "+fragment)
        report["native_asset_paths"].append(matches[0])
        return m
    trim=imported_mesh("SharedExteriorTrim")
    filigree=imported_mesh("SkybourneWingFiligree")
    sphere=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not isinstance(sphere,unreal.StaticMesh) or not isinstance(cube,unreal.StaticMesh):
        raise RuntimeError("Engine basic preview meshes missing")
    if hasattr(levels,"new_level"):
        created=levels.new_level(MAP)
    else:
        created=unreal.EditorLevelLibrary.new_level(MAP)
    if not created or not levels.load_level(MAP):
        raise RuntimeError("Unable to create/reload new isolated hero level")
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None or actors.get_all_level_actors():
        raise RuntimeError("Review map missing world or non-empty")

    labels=[]
    def place(label,mesh,pos,scale=(1,1,1),rot=(0,0,0)):
        x=actors.spawn_actor_from_class(unreal.StaticMeshActor,
             unreal.Vector(*pos),unreal.Rotator(*rot))
        if x is None:raise RuntimeError("Full Editor spawn failed "+label)
        c=x.get_component_by_class(unreal.StaticMeshComponent)
        if c is None or not c.set_static_mesh(mesh):
            raise RuntimeError("Failed to bind actual StaticMesh "+label)
        x.set_actor_label("V4_NONCANONICAL_"+label)
        x.set_actor_scale3d(unreal.Vector(*scale))
        x.set_actor_enable_collision(False)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        labels.append(x.get_actor_label())
        return x

    # Temporary blockout shared across all future forms, not true production hull.
    place("SHARED_PEARL_HULL_PROXY",sphere,(0,0,0),(7.9,1.15,.55))
    place("SHARED_HULL_CINEMATIC_V4_TRIM",trim,(0,0,0))
    place("CENTRAL_LIVING_QUARTERS_PROXY",cube,(0,0,60),(2.05,1.13,.58))
    place("FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",sphere,(210,0,122),(1.08,.76,.72))
    place("FORWARD_OBSERVATION_DECK_PROXY",cube,(320,0,55),(1.65,.68,.07))
    # Exactly FOUR principal wing identities. Paired proxy and lace are co-located
    # rendering layers, not extra main wings. Rotations are unapproved study only.
    wing_roots=(
       ("FORE_PORT",(145,-99,55),(0,-80,-8)),
       ("FORE_STARBOARD",(145,99,55),(0,80,8)),
       ("AFT_PORT",(-180,-99,53),(0,-102,-8)),
       ("AFT_STARBOARD",(-180,99,53),(0,102,8)),
    )
    for wing_id,loc,angle in wing_roots:
        place(wing_id+"_MEMBRANE_PROXY",cube,loc,(2.63,.59,.029),angle)
        place(wing_id+"_V4_GOLD_FILIGREE",filigree,loc,(1,1,1),angle)
        report["wing_identity_labels"].append(wing_id)
    if len(set(report["wing_identity_labels"]))!=4:
        raise RuntimeError("Not four persistent named wings")

    # Same four camera roles for future ordinary-form comparisons.
    camera_views=(
       ("THREE_QUARTER",(1050,840,560),(0,0,40)),
       ("TOP",(0,0,1250),(0,0,0)),
       ("PROFILE",(80,1175,285),(0,0,25)),
       ("BRIDGE",(515,410,300),(200,0,105)),
    )
    cameras=[]
    for name,position,target in camera_views:
        rot=unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*position),
                                                   unreal.Vector(*target))
        cam=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*position),rot)
        if not cam:raise RuntimeError("Failed native camera spawn "+name)
        cam.set_actor_label("V4_NONCANONICAL_CAMERA_"+name)
        cam.get_component_by_class(unreal.CameraComponent).set_editor_property(
            "field_of_view",42.0)
        cameras.append(cam.get_actor_label())
    key=actors.spawn_actor_from_class(unreal.DirectionalLight,
                                       unreal.Vector(0,0,660),
                                       unreal.Rotator(-40,40,0))
    if key is None:raise RuntimeError("Key-light actor missing")
    key.set_actor_label("V4_NONCANONICAL_DIRECTIONAL_KEYLIGHT")
    report["camera_labels"]=cameras
    all_labels=[a.get_actor_label() for a in actors.get_all_level_actors()]
    if not all(x in all_labels for x in labels+cameras):
        raise RuntimeError("Native post-spawn identity readback differs")
    if not levels.save_current_level():
        raise RuntimeError("Could not save full Editor Skybourne hero level")
    dest=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap"
    if not dest.is_file():raise RuntimeError("Saved native level asset missing")
    report.update({"state":"SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS",
                   "engine":unreal.SystemLibrary.get_engine_version(),
                   "map":MAP,"map_file":str(dest),
                   "map_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
                   "actor_count":len(all_labels),
                   "detail_mesh_count":2,
                   "wing_count":4,
                   "camera_count":4,
                   "bridge_and_quarters":"SAME_HULL_STATIC_PROXIES_NOT_ROTATION_VERIFIED",
                   "visual_fidelity":"NOT_YET_GPU_RENDERED_OR_ART_APPROVED",
                   "next":"ACTUAL_GPU_SCREENSHOT_AND_CREATOR_VISUAL_QA"})
except Exception as e:
    report["state"]="SKYBOURNE_NATIVE_STAGE_FAILED_DO_NOT_CLAIM_RENDER"
    report["error"]=str(e)
    report["traceback"]=traceback.format_exc()[-4200:]
finally:
    RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    unreal.log("AUREATE_V4_FULL_EDITOR_SKYBOURNE_STAGE "+json.dumps(report))
if report["state"]!="SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS":
    raise RuntimeError(report.get("error","Stage failed"))
