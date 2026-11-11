"""Registered UE5.8.4 Python automation screenshot — actual GPU artifacts only.

Three UNSAVED transient cameras; source map and originals never modified.
Task completion alone is insufficient: real PNG, dimensions, CRC, world
SHA, native Automation controller and host pixel QA must all pass.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import traceback
import zlib
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))

from intake_first_wake_slice_gpu_review import WORLD_SHA

PROJECT=Path("C:/TSTSS_VSliceVisualRuntime_20261110/unreal")
MAP="/Game/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1"
WORLD_FILE=PROJECT/"Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap"
RESULT_DIR=PROJECT/"Saved/FirstWakeSliceVisualQA/D3D11_FirstWakeObjects_20261110"
RECEIPT=RESULT_DIR/"native_capture_receipt.json"
SIZE=(1280,720)
SHOT_PLAN=(
    ("Harbor_Establishing",(-2800,-2900,950),(-850,540,190)),
    ("Engineering_Close",(-350,-1550,640),(500,-70,260)),
    ("Aureate_Boarding",(-2100,2500,600),(-850,980,185)),
)
PICS=tuple(RESULT_DIR/("FirstWakeObjects_"+name+"_UE584_D3D11_REVIEW.png")
           for name,*_ in SHOT_PLAN)
STATUS_OK="NATIVE_D3D11_PNG_CAPTURE_TASKS_PASS_VISUAL_QA_PENDING"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as inp:
        for chunk in iter(lambda:inp.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def validate_png(path):
    raw=path.read_bytes()
    if len(raw)<4096 or not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("GPU_FRAME_HOLD: invalid/truncated real PNG "+str(path))
    i=8; dimensions=None;idat=False;ended=False
    while i<len(raw):
        if i+12>len(raw):raise RuntimeError("GPU_FRAME_HOLD: truncated PNG chunk")
        n=struct.unpack_from(">I",raw,i)[0]
        kind=raw[i+4:i+8]
        end=i+12+n
        if end>len(raw):raise RuntimeError("GPU_FRAME_HOLD: truncated PNG pixels")
        payload=raw[i+8:i+8+n]
        crc=struct.unpack_from(">I",raw,i+8+n)[0]
        if zlib.crc32(kind+payload)!=crc:
            raise RuntimeError("GPU_FRAME_HOLD: bad CRC in real PNG")
        if dimensions is None:
            if kind!=b"IHDR" or n!=13:
                raise RuntimeError("GPU_FRAME_HOLD: missing PNG dimensions")
            dimensions=struct.unpack_from(">II",payload)
            if dimensions!=SIZE:
                raise RuntimeError("GPU_FRAME_HOLD: wrong screenshot dimensions")
        if kind==b"IDAT":idat=True
        if kind==b"IEND":
            if n!=0 or end!=len(raw) or not idat:
                raise RuntimeError("GPU_FRAME_HOLD: invalid PNG end/pixels")
            ended=True
        i=end
    if not ended or not idat:
        raise RuntimeError("GPU_FRAME_HOLD: PNG lacks real pixel data")
    return {"file":path.name,"sha256":hashlib.sha256(raw).hexdigest(),
            "bytes":len(raw),"size":list(dimensions)}

def alignment(eye,target,actual_forward):
    v=[b-a for a,b in zip(eye,target)]
    n=math.sqrt(sum(x*x for x in v))
    d=math.sqrt(sum(x*x for x in actual_forward))
    if n<=0 or d<=0 or not all(math.isfinite(x) for x in (*eye,*target,*actual_forward)):
        raise RuntimeError("GPU_FRAME_HOLD: impossible camera forward vector")
    ratio=sum(a*b for a,b in zip(v,actual_forward))/(n*d)
    if ratio<0.995:
        raise RuntimeError("GPU_FRAME_HOLD: camera looking away from composed scene")
    return ratio

def validated_native_scene():
    import unreal
    if (Path(unreal.Paths.project_dir()).resolve()!=PROJECT.resolve() or
            not unreal.SystemLibrary.get_engine_version().startswith("5.8.4") or
            not WORLD_FILE.is_file() or sha(WORLD_FILE)!=WORLD_SHA):
        raise RuntimeError("GPU_FRAME_HOLD: wrong project/engine/World SHA")
    stage=json.loads((PROJECT/"Saved/FirstWakeSliceObjectsV1/native_objects_stage.json")
                     .read_text(encoding="utf-8"))
    readback=json.loads((PROJECT/"Saved/FirstWakeSliceObjectsV1/native_objects_readback.json")
                        .read_text(encoding="utf-8"))
    if (stage.get("new_map_sha256")!=WORLD_SHA or
            readback.get("saved_world_sha256")!=WORLD_SHA or
            readback.get("actors")!=115 or readback.get("new_visual_actors")!=31 or
            readback.get("distinct_imported_static_meshes")!=22 or
            readback.get("status")!="INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE"):
        raise RuntimeError("GPU_FRAME_HOLD: saved native provenance not established")
    if not unreal.EditorLoadingAndSavingUtils.load_map(MAP):
        raise RuntimeError("GPU_FRAME_HOLD: exact source review map failed to load")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    labels=[a.get_actor_label() for a in actors]
    if len(actors)!=115 or len(set(labels))!=115:
        raise RuntimeError("GPU_FRAME_HOLD: source scene actor count changed")
    if sum(isinstance(a,unreal.PlayerStart) for a in actors)!=1:
        raise RuntimeError("GPU_FRAME_HOLD: source PlayerStart count changed")
    stops=("FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation",
           "PressureStation","ReserveStation","EngineeringApproval")
    for stop in stops:
        if labels.count("TSTSS_PRELUDE_REVIEW_"+stop)!=1:
            raise RuntimeError("GPU_FRAME_HOLD: story route milestone missing "+stop)
    props=[a for a in actors if a.get_actor_label().startswith("TSTSS_SLICE_OBJ_V1_")]
    if len(props)!=31:
        raise RuntimeError("GPU_FRAME_HOLD: object stage labels changed")
    distinct=set()
    for actor in props:
        if not isinstance(actor,unreal.StaticMeshActor):
            raise RuntimeError("GPU_FRAME_HOLD: prop no longer native mesh actor")
        comp=actor.static_mesh_component
        if comp.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
            raise RuntimeError("GPU_FRAME_HOLD: visual prop has gameplay collision")
        mesh=comp.get_editor_property("static_mesh")
        if not mesh:raise RuntimeError("GPU_FRAME_HOLD: missing native visual mesh")
        distinct.add(mesh.get_path_name())
    if len(distinct)!=22:
        raise RuntimeError("GPU_FRAME_HOLD: expected all 22 native object meshes")
    if any("Starbourne" in s for s in labels):
        raise RuntimeError("GPU_FRAME_HOLD: locked ship configuration appeared")
    return unreal

def schedule():
    unreal=validated_native_scene()
    if not hasattr(unreal,"AutomationScheduler") or not hasattr(unreal,"AutomationLibrary"):
        raise RuntimeError("GPU_FRAME_HOLD: registered PythonAutomationTest API not installed")
    if RESULT_DIR.exists():
        raise RuntimeError("GPU_FRAME_HOLD: no screenshot/receipt overwrite permitted")
    old_hash=sha(WORLD_FILE)
    actor_system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cameras=[]
    for name,eye,point in SHOT_PLAN:
        origin=unreal.Vector(*eye);target=unreal.Vector(*point)
        camera=actor_system.spawn_actor_from_class(unreal.CameraActor,origin,unreal.Rotator(0,0,0))
        if camera is None:
            raise RuntimeError("GPU_FRAME_HOLD: transient review camera not created")
        camera.set_actor_label("TSTSS_TEMP_GPUQA_UNSAVED_"+name)
        if not camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(origin,target),False):
            raise RuntimeError("GPU_FRAME_HOLD: unable to point transient review camera")
        facing=unreal.MathLibrary.get_forward_vector(camera.get_actor_rotation())
        alignment(eye,point,(facing.x,facing.y,facing.z))
        cameras.append(camera)
    RESULT_DIR.mkdir(parents=True,exist_ok=False)
    receipt={"status":"NATIVE_D3D11_SCREENSHOT_TASKS_SCHEDULED_NOT_VERIFIED",
             "engine":unreal.SystemLibrary.get_engine_version(),
             "source_map_sha256":old_hash,"expected_native_actors":115,
             "temporary_camera_only_not_saved":True,
             "capture_engine":"D3D11_requested_not_yet_proven",
             "shot_plan":[{"name":n,"eye":list(e),"target":list(t)}
                          for n,e,t in SHOT_PLAN],
             "art_approved":False,"pie_verified":False,
             "ocean_physics_verified":False,"user_saves_modified":False,
             "starbourne_unlocked":False}
    with RECEIPT.open("x",encoding="utf-8") as out:
        json.dump(receipt,out,sort_keys=True,indent=2)
    @unreal.AutomationScheduler.add_latent_command
    def capture_frames():
        try:
            images=[]
            for pic,cam in zip(PICS,cameras):
                task=unreal.AutomationLibrary.take_high_res_screenshot(
                    SIZE[0],SIZE[1],str(pic),camera=cam,delay=.45,
                    force_game_view=True,capture_hdr=False)
                if task is None or not task.is_valid_task():
                    raise RuntimeError("GPU_FRAME_HOLD: native screenshot task rejected")
                ticks=0
                while not task.is_task_done():
                    ticks+=1
                    if ticks>2200:
                        raise RuntimeError("GPU_FRAME_HOLD: screenshot exceeded tick budget")
                    yield
                if not pic.is_file():
                    raise RuntimeError("GPU_FRAME_HOLD: screenshot task returned without a file")
                images.append(validate_png(pic))
                yield
            if sha(WORLD_FILE)!=old_hash:
                raise RuntimeError("GPU_FRAME_HOLD: source World changed during screenshot")
            receipt.update(status=STATUS_OK,images=images,
                           capture_engine="NATIVE_SCREENSHOT_TASKS_COMPLETED_D3D11_HOST_MUST_VERIFY",
                           source_world_unchanged=True)
        except Exception as exc:
            receipt.update(status="NATIVE_D3D11_CAPTURE_HOLD",error=str(exc),
                           traceback=traceback.format_exc()[-2500:])
            unreal.log_error("FIRST_WAKE_OBJECT_GPU_HOLD "+str(exc))
            # This is a deliberately failing assertion in registered automation:
            raise
        finally:
            RECEIPT.write_text(json.dumps(receipt,sort_keys=True,indent=2),encoding="utf-8")
            unreal.log("FIRST_WAKE_OBJECT_GPU_RECEIPT "+json.dumps(receipt,sort_keys=True))
    return receipt

if __name__=="__main__":
    import unreal
    unreal.log("FIRST_WAKE_OBJECT_GPU_START "+json.dumps(schedule(),sort_keys=True))
