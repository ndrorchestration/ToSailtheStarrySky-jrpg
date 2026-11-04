"""Standalone FULL EDITOR NullRHI bridge+quarters common-pivot test.

Provisional test axis/angles only. Create one NEW disposable review map, verify
both child actors rigidly follow pivot, roll back pose, then save at rest.
Never touches existing four maps, production actor or Starbourne story gate.
"""
from pathlib import Path
import hashlib
import json
import math
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
MAP="/Game/TSTSS/Review/Scenes/AureateV4_HabitationCoupledPivot_20261103_PILOT"
OUT=ROOT/"coupled_habitation_native_pilot_receipt_20261103.json"
SOURCE_MAP=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap"
SOURCE_SHA="16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40"
report={"state":"NOT_STARTED","candidate":"UNAPPROVED_COUPLED_HABITATION_REVIEW_ONLY",
        "current_gameplay_modified":False,"existing_review_maps_modified":False,
        "starbourne_player_unlock":False,"native_gpu_rendered":False,
        "physical_clearance_proven":False,"creator_pose_approved":False}
if OUT.exists():raise FileExistsError("Pilot already attempted")
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def v3(v):return (float(v.x),float(v.y),float(v.z))
def distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def near(x,y,absolute=.01):return distance(x,y)<absolute
def req(condition,msg):
    if not condition:raise RuntimeError(msg)
try:
    req(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"Wrong active project")
    meta=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    req("AUREATE_CINEMATIC_V4_REVIEW_ONLY" in meta.get("Description",""),"Not isolated review")
    report["engine"]=unreal.SystemLibrary.get_engine_version()
    req(report["engine"].startswith("5.8."),"Wrong engine")
    req(SOURCE_MAP.is_file() and digest(SOURCE_MAP)==SOURCE_SHA,"Untrusted source scene hash")
    lib=unreal.EditorAssetLibrary
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    req(not lib.does_asset_exist(MAP),"Target pilot map already exists")
    if not levels.new_level(MAP) or not levels.load_level(MAP):
        raise RuntimeError("New isolated pivot-review map unavailable")
    req(not actors.get_all_level_actors(),"Pivot map is not empty")
    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    sphere=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    req(isinstance(cube,unreal.StaticMesh) and isinstance(sphere,unreal.StaticMesh),
        "Engine BasicShapes missing")
    def actor(name,mesh,coords,scale):
        obj=actors.spawn_actor_from_class(unreal.StaticMeshActor,
                            unreal.Vector(*coords),unreal.Rotator(0,0,0))
        req(obj is not None,"Spawn failed "+name)
        comp=obj.get_component_by_class(unreal.StaticMeshComponent)
        req(comp is not None and comp.set_static_mesh(mesh),"Mesh set failed "+name)
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        obj.set_actor_enable_collision(False)
        obj.set_actor_scale3d(unreal.Vector(*scale))
        obj.set_actor_label("V4_NONCANONICAL_"+name)
        return obj
    hull=actor("STATIC_HULL_REFERENCE",sphere,(0,0,0),(7.9,1.15,.55))
    pivot=actor("COUPLED_BRIDGE_AND_QUARTERS_PIVOT",cube,(30,0,70),(.08,.08,.08))
    bridge=actor("BRIDGE_CHILD",sphere,(210,0,122),(1.08,.76,.72))
    quarters=actor("LIVING_QUARTERS_CHILD",cube,(0,0,60),(2.05,1.13,.58))
    mode=unreal.AttachmentRule.KEEP_WORLD
    req(bool(bridge.attach_to_actor(pivot,"",mode,mode,mode,False)),
        "Bridge parent attachment failed")
    req(bool(quarters.attach_to_actor(pivot,"",mode,mode,mode,False)),
        "Quarters parent attachment failed")
    req(bridge.get_attach_parent_actor()==pivot and
        quarters.get_attach_parent_actor()==pivot,
        "Missing same parent for both habitation children")
    b0=v3(bridge.get_actor_location())
    q0=v3(quarters.get_actor_location())
    h0=v3(hull.get_actor_location())
    d0=distance(b0,q0)
    req(bool(pivot.set_actor_rotation(unreal.Rotator(0,17.5,0),False)),
        "Could not rotate central review pivot")
    b1=v3(bridge.get_actor_location());q1=v3(quarters.get_actor_location())
    req(not near(b0,b1) and not near(q0,q1),
        "One or both cabin children did not move under review yaw")
    req(abs(distance(b1,q1)-d0)<.01,
        "Shared pivot failed rigid child-to-child distance")
    req(near(h0,v3(hull.get_actor_location())),"Independent ship hull moved")
    req(bool(pivot.set_actor_rotation(unreal.Rotator(0,0,0),False)),
        "Cannot restore original pivot pose")
    req(near(b0,v3(bridge.get_actor_location())) and
        near(q0,v3(quarters.get_actor_location())),
        "Habitation children did not restore original positions")
    req(bridge.get_attach_parent_actor()==pivot and
        quarters.get_attach_parent_actor()==pivot,
        "Attachment changed after rollback")
    req(levels.save_current_level(),"Pilot map failed to save")
    outfile=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateV4_HabitationCoupledPivot_20261103_PILOT.umap"
    req(outfile.is_file(),"Missing saved pivot-review map")
    req(digest(SOURCE_MAP)==SOURCE_SHA,"Source Skybourne map unexpectedly mutated")
    report.update({"state":"NATIVE_COUPLED_HABITATION_REVIEW_PIVOT_PASS",
                   "saved_map":MAP,"saved_map_sha256":digest(outfile),
                   "actor_count":len(actors.get_all_level_actors()),
                   "shared_parent":pivot.get_actor_label(),
                   "bridge_child":bridge.get_actor_label(),
                   "quarters_child":quarters.get_actor_label(),
                   "temporary_test_yaw_degrees":17.5,
                   "bridge_before_cm":b0,"bridge_during_cm":b1,
                   "quarters_before_cm":q0,"quarters_during_cm":q1,
                   "rigid_distance_before_cm":d0,
                   "rigid_distance_during_cm":distance(b1,q1),
                   "hull_remained_stationary":True,
                   "review_angle_restored":True,
                   "source_map_sha_after":digest(SOURCE_MAP)})
except Exception as e:
    report["state"]="NATIVE_COUPLED_HABITATION_PIVOT_HOLD"
    report["error"]=str(e)
    report["traceback"]=traceback.format_exc()[-4000:]
finally:
    OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    unreal.log("V4_COUPLED_HABITATION_PIVOT "+json.dumps(report,sort_keys=True))
if report["state"]!="NATIVE_COUPLED_HABITATION_REVIEW_PIVOT_PASS":
    raise RuntimeError(report.get("error","Pivot pilot did not complete"))
