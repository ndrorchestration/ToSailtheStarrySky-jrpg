"""Source-bound UE 5.8.4 full Editor staging of 3 other noncanonical forms.

Skybourne hero map is an immutable SHA-pinned dependency. This tool builds
NEW Seabourne, Submersible and PRIVATE STATIC Starbourne lookdev maps using
the same hull and wing identities. No D3D11 image, physics, save, gameplay
form request, transformation trajectory, art approval or player reveal.
"""
from pathlib import Path
import hashlib
import json
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
NATIVE_IMPORT=ROOT/"native_import_receipt.json"
SKY_RECEIPT=ROOT/"full_editor_skybourne_stage_receipt.json"
RECEIPT=ROOT/"full_editor_three_form_stage_receipt.json"
MAP_FOLDER="/Game/TSTSS/Review/Scenes"
SKY_SHA="16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40"
FORMS=("Seabourne","Submersible","Starbourne")
WINGS=("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")
VIEWS=(
 ("THREE_QUARTER",(1050,840,560),(0,0,40)),
 ("TOP",(0,0,1250),(0,0,0)),
 ("PROFILE",(80,1175,285),(0,0,25)),
 ("BRIDGE",(515,410,300),(200,0,105)),
)
receipt={"state":"NOT_STARTED",
         "scope":"NONCANONICAL_UNREAL_EDITOR_REVIEW_ONLY",
         "completed_maps":[],
         "starbourne_player_form_available":False,
         "runtime_transition_or_save_changed":False,
         "user_playable_game_modified":False,
         "gpu_screenshot_generated":False,
         "canonical_model_accepted":False}
if RECEIPT.exists():raise FileExistsError("Refuse repeat native three-form staging")
try:
    assert Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(), "Wrong Unreal project"
    conf=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    assert conf["EngineAssociation"]=="5.8"
    assert "AUREATE_CINEMATIC_V4_REVIEW_ONLY" in conf["Description"]
    receipt["engine"]=unreal.SystemLibrary.get_engine_version()
    assert receipt["engine"].startswith("5.8.")
    sky=json.loads(SKY_RECEIPT.read_text(encoding="utf8"))
    assert sky["state"]=="SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS"
    skypath=Path(sky["map_file"])
    assert skypath.is_file() and hashlib.sha256(skypath.read_bytes()).hexdigest()==SKY_SHA
    imports=json.loads(NATIVE_IMPORT.read_text(encoding="utf8"))
    assert imports["state"]=="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS"
    lib=unreal.EditorAssetLibrary
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def mesh(part):
        values=[v["object_path"] for k,v in imports["readback"].items() if part in k]
        if len(values)!=1:raise RuntimeError("Nonunique V4 mesh: "+part)
        x=unreal.load_asset(values[0])
        if not isinstance(x,unreal.StaticMesh) or len(x.get_editor_property("static_materials"))!=4:
            raise RuntimeError("Missing native four-slot StaticMesh "+part)
        return x
    shared=mesh("SharedExteriorTrim")
    marine=mesh("SeabourneHydrofoilDetail")
    underwater=mesh("SubmersibleLightRail")
    star=mesh("StarbourneSailMotif")
    sphere=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not isinstance(sphere,unreal.StaticMesh) or not isinstance(cube,unreal.StaticMesh):
        raise RuntimeError("Engine BasicShapes absent")
    expected_maps={f:MAP_FOLDER+"/AureateCinematicV4_"+f+"_20261103_FullEditor"
                   for f in FORMS}
    for name,dest in expected_maps.items():
        if lib.does_asset_exist(dest):
            raise FileExistsError("Unexpected occupied three-form review target "+name)
    def spawn(label,shape,at,scale=(1,1,1),rotate=(0,0,0)):
        a=actor.spawn_actor_from_class(unreal.StaticMeshActor,
                                      unreal.Vector(*at),unreal.Rotator(*rotate))
        if a is None:raise RuntimeError("No native full-Editor actor "+label)
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c is None or not c.set_static_mesh(shape):
            raise RuntimeError("No mesh assignment "+label)
        a.set_actor_label("V4_NONCANONICAL_"+label)
        a.set_actor_scale3d(unreal.Vector(*scale))
        a.set_actor_enable_collision(False)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        return a
    def core():
        spawn("SHARED_PEARL_HULL_PROXY",sphere,(0,0,0),(7.9,1.15,.55))
        spawn("SHARED_HULL_CINEMATIC_V4_TRIM",shared,(0,0,0))
        spawn("CENTRAL_LIVING_QUARTERS_PROXY",cube,(0,0,60),(2.05,1.13,.58))
        spawn("FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",sphere,(210,0,122),(1.08,.76,.72))
        spawn("FORWARD_OBSERVATION_DECK_PROXY",cube,(320,0,55),(1.65,.68,.07))
    def cameras_and_light(form):
        for name,position,target in VIEWS:
            rotation=unreal.MathLibrary.find_look_at_rotation(
                unreal.Vector(*position),unreal.Vector(*target))
            cam=actor.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(*position),rotation)
            if cam is None:raise RuntimeError("Failed camera "+name)
            cam.set_actor_label("V4_NONCANONICAL_"+form+"_CAMERA_"+name)
            cam.get_component_by_class(unreal.CameraComponent).set_editor_property(
                "field_of_view",42.0)
        light=actor.spawn_actor_from_class(unreal.DirectionalLight,
                                          unreal.Vector(0,0,660),
                                          unreal.Rotator(-40,40,0))
        if light is None:raise RuntimeError("Failed review key light")
        light.set_actor_label("V4_NONCANONICAL_"+form+"_DIRECTIONAL_KEYLIGHT")
    def ordinary_wings(form):
        roots=(
          ("FORE_PORT",(145,-99,55)),
          ("FORE_STARBOARD",(145,99,55)),
          ("AFT_PORT",(-180,-99,53)),
          ("AFT_STARBOARD",(-180,99,53)),
        )
        for wing_id,(x,y,z) in roots:
            side=-1 if "PORT" in wing_id else 1
            if form=="Seabourne":
                yaw=side*(80 if x>0 else 100)
                rot=(35,yaw,side*48)
                scale=(2.35,.45,.035)
                location=(x,y,z+25)
            else:
                yaw=side*(22 if x>0 else 158)
                rot=(0,yaw,side*72)
                scale=(2.05,.36,.035)
                location=(x,side*92,z-25)
            spawn("WING_ID_"+wing_id+"_MEMBRANE_PROXY",cube,location,scale,rot)

    for form,dest in expected_maps.items():
        if hasattr(lvl,"new_level"):created=lvl.new_level(dest)
        else:created=unreal.EditorLevelLibrary.new_level(dest)
        if not created or not lvl.load_level(dest):
            raise RuntimeError("Could not create/load fresh review level "+form)
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        if world is None or actor.get_all_level_actors():
            raise RuntimeError("New review level has no usable empty editor world")
        core()
        if form=="Seabourne":
            ordinary_wings(form)
            for side,label in ((-1,"PORT"),(1,"STARBOARD")):
                center=(0,side*80,-140)
                spawn("HYDROFOIL_"+label+"_PROXY",cube,center,(2.1,.74,.1))
                spawn("HYDROFOIL_"+label+"_V4_DETAIL",marine,(0,side*80,-131))
                spawn("HYDROFOIL_"+label+"_BRASS_STRUT_PROXY",cube,(0,side*73,-70),(.14,.11,1.3))
        elif form=="Submersible":
            ordinary_wings(form)
            spawn("SUBMERSIBLE_V4_LIGHT_RAIL",underwater,(0,0,0))
        elif form=="Starbourne":
            # ONE identical sail mesh and size in each of four equal radial positions.
            radial=(("UP",(0,0,240),(0,0,0)),
                    ("RIGHT",(0,240,0),(0,0,90)),
                    ("DOWN",(0,0,-240),(0,0,180)),
                    ("LEFT",(0,-240,0),(0,0,270)))
            for wing_id,(direction,center,rotation) in zip(WINGS,radial):
                spawn("PRIVATE_STATIC_STARB_SAIL_ID_"+wing_id+"_"+direction,
                      star,center,(1,1,1),rotation)
        cameras_and_light(form)
        active=actor.get_all_level_actors()
        labels=[x.get_actor_label() for x in active]
        for wing_id in WINGS:
            if not any(wing_id in s for s in labels):
                raise RuntimeError("Lost four-wing identity "+wing_id+" in "+form)
        if not lvl.save_current_level():
            raise RuntimeError("Failed to save native review level "+form)
        file=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/("AureateCinematicV4_"+form+"_20261103_FullEditor.umap")
        if not file.is_file():raise RuntimeError("Saved map file missing "+form)
        entry={"form":form,"review_map":dest,
               "native_actor_count":len(labels),
               "wing_identity_count":4,
               "camera_count":4,
               "map_file":str(file),
               "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
               "production_model":False,
               "player_starbourne_unlocked":False}
        if form=="Starbourne":
            entry["radial_static_sails"]=4
            entry["development"]="PRIVATE_ONLY"
            entry["player_story_access"]="LOCKED"
        if form=="Seabourne":entry["hydrofoil_count"]=2
        if form=="Submersible":entry["tucked_wings_still_visible"]=True
        receipt["completed_maps"].append(entry)
        RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    assert len(receipt["completed_maps"])==3
    receipt["state"]="THREE_NATIVE_FULL_EDITOR_REVIEW_MAPS_STAGED_PASS"
except Exception as exc:
    receipt["state"]="PARTIAL_OR_FAILED_THREE_FORM_STAGE_NOT_ADMITTED"
    receipt["error"]=str(exc)
    receipt["traceback"]=traceback.format_exc()[-5000:]
finally:
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    unreal.log("TSTSS_V4_REMAINING_FORMS_STAGE "+json.dumps(receipt,sort_keys=True))
if receipt["state"]!="THREE_NATIVE_FULL_EDITOR_REVIEW_MAPS_STAGED_PASS":
    raise RuntimeError(receipt.get("error","Incomplete review-stage"))
