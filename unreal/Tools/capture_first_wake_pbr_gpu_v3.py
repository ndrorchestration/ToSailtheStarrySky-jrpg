"""Genuine UE5.8.4 D3D11 PNG capture of independently saved 200-actor PBR World.

Four temporary/unsaved native camera views; hide precisely seven dev
TextRender signs in game view only. No level save, E-interaction or PIE claim.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parent))
import intake_first_wake_pbr_gpu_v3 as source
import first_wake_cinematic_sign_policy_v3 as sign
from capture_first_wake_slice_objects_d3d11 import validate_png,alignment,SIZE

PROJECT=source.DEST/"unreal"
WORLD_MAP="/Game/TSTSS/Review/Scenes/FirstWake_MaterialLookdev_20261111_REVIEW_V3"
WORLD_FILE=source.DEST/source.WORLD_REL
OUTPUT=PROJECT/"Saved/FirstWakeMaterialLookdevV3/D3D11_PBR_V3_20261111"
NATIVE_RECEIPT=OUTPUT/"native_gpu_capture_receipt.json"
STATUS="NATIVE_PBR_V3_D3D11_PNG_TASKS_PASS_VISUAL_QA_PENDING"
CAMERAS=(
    ("Harbor_Establishing",(-2800,-2900,950),(-850,540,190)),
    ("Engineering_OpenQuay",(470,840,420),(250,270,130)),
    ("Aureate_Boarding",(-2100,2500,600),(-850,980,185)),
    ("Quay_Paving_Study",(-1450,-450,330),(-450,200,0)),
)
FRAMES=tuple(OUTPUT/("FirstWakePBRV3_"+n+"_UE584_D3D11_REVIEW.png")
             for n,*_ in CAMERAS)

def native_world():
    import unreal
    if (Path(unreal.Paths.project_dir()).resolve()!=PROJECT.resolve() or
            not unreal.SystemLibrary.get_engine_version().startswith("5.8.4") or
            not WORLD_FILE.is_file() or source.sha(WORLD_FILE)!=source.WORLD_SHA):
        raise RuntimeError("PBR_GPU_HOLD: exact saved World/project/engine not matched")
    receipt=json.loads((source.DEST/source.OUT).read_text(encoding="utf-8"))
    if (receipt.get("status")!="VERIFIED_NATIVE_200_ACTOR_GPU_PRIVATE_CUSTODY_NOT_RENDERED" or
            receipt.get("file_count")!=source.MIN_FILES or
            receipt.get("native_world_sha256")!=source.WORLD_SHA):
        raise RuntimeError("PBR_GPU_HOLD: native 200-actor package custody missing")
    native=json.loads((PROJECT/"Saved/FirstWakeMaterialLookdevV3/native_independent_readback.json")
                      .read_text(encoding="utf-8"))
    host=json.loads((PROJECT/"Saved/FirstWakeMaterialLookdevV3/host_independent_readback.json")
                    .read_text(encoding="utf-8"))
    if (native.get("status")!="INDEPENDENT_NATIVE_PBR_V3_READBACK_PASS_NOT_PIE" or
            native.get("derived_world_sha256")!=source.WORLD_SHA or
            native.get("actors")!=200 or
            native.get("new_visual_only_mesh_actors")!=84 or
            native.get("native_texture_assets_reloaded")!=30 or
            native.get("native_material_assets_reloaded")!=10 or
            native.get("materials_replaced_on_inherited_actors")!=18 or
            native.get("original_floor_collision_verified") is not True or
            native.get("new_detail_collision_disabled") is not True or
            host.get("status")!="INDEPENDENT_NATIVE_PBR_V3_READBACK_VERIFIED_NOT_PIE" or
            host.get("native_exit_code")!=0):
        raise RuntimeError("PBR_GPU_HOLD: independent native stage evidence incomplete")
    if not unreal.EditorLoadingAndSavingUtils.load_map(WORLD_MAP):
        raise RuntimeError("PBR_GPU_HOLD: exact PBR saved World cannot load")
    actors=list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
    labels=[a.get_actor_label() for a in actors]
    if len(actors)!=200 or len(labels)!=len(set(labels)):
        raise RuntimeError("PBR_GPU_HOLD: saved actor inventory changed")
    if sum(isinstance(a,unreal.PlayerStart) for a in actors)!=1:
        raise RuntimeError("PBR_GPU_HOLD: original PlayerStart changed")
    sign.sign_inventory(labels)
    heritage={a.get_actor_label():a for a in actors}
    floor=heritage.get("TSTSS_PRELUDE_REVIEW_Harbor_TraversalFloor")
    if (not isinstance(floor,unreal.StaticMeshActor) or
            floor.static_mesh_component.get_collision_enabled() !=
            unreal.CollisionEnabled.QUERY_AND_PHYSICS):
        raise RuntimeError("PBR_GPU_HOLD: original floor collision changed")
    newactors=[a for a in actors if a.get_actor_label().startswith(
        "TSTSS_MATERIAL_LOOKDEV_V3_")]
    if len(newactors)!=85:
        raise RuntimeError("PBR_GPU_HOLD: not exactly 84 decorative meshes + one camera")
    for actor in newactors:
        if isinstance(actor,unreal.StaticMeshActor):
            if actor.static_mesh_component.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION:
                raise RuntimeError("PBR_GPU_HOLD: decorative review actor collision enabled")
    if any("Starbourne" in s for s in labels):
        raise RuntimeError("PBR_GPU_HOLD: restricted Starbourne actor appeared")
    return unreal,actors

def schedule():
    unreal,actors=native_world()
    if not hasattr(unreal,"AutomationScheduler") or not hasattr(unreal,"AutomationLibrary"):
        raise RuntimeError("PBR_GPU_HOLD: UE Python automation plugin absent")
    if OUTPUT.exists():
        raise RuntimeError("PBR_GPU_HOLD: previous V3 GPU output cannot be overwritten")
    before=source.sha(WORLD_FILE)
    hidden=sign.suppress_transient_only(actors,unreal)
    cameras=[]
    system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for name,eye,focus in CAMERAS:
        origin=unreal.Vector(*eye)
        target=unreal.Vector(*focus)
        cam=system.spawn_actor_from_class(unreal.CameraActor,origin,unreal.Rotator())
        if cam is None:
            raise RuntimeError("PBR_GPU_HOLD: transient camera not spawned "+name)
        cam.set_actor_label("TSTSS_GPU_PBR_TEMP_UNSAVED_"+name)
        if not cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(origin,target),False):
            raise RuntimeError("PBR_GPU_HOLD: camera face rotation not applied")
        vector=unreal.MathLibrary.get_forward_vector(cam.get_actor_rotation())
        alignment(eye,focus,(vector.x,vector.y,vector.z))
        cameras.append(cam)
    OUTPUT.mkdir(parents=True,exist_ok=False)
    report={
        "status":"PBR_V3_D3D11_CAPTURE_TASKS_SCHEDULED_NOT_VERIFIED",
        "engine":unreal.SystemLibrary.get_engine_version(),
        "world_sha256":before,"native_level_actors":200,
        "transient_hidden_developer_text_signs":len(hidden["sign_labels"]),
        "transient_sign_policy_status":hidden["status"],
        "hidden_gameplay_milestones":0,
        "no_source_level_save":True,"source_world_preserved":False,
        "frames_expected":len(FRAMES),
        "shot_plan":[{"name":n,"eye":list(e),"target":list(f)} for n,e,f in CAMERAS],
        "native_d3d11_engine_verified":False,"gpu_visual_approved":False,
        "pie_verified":False,"ocean_splashdown_verified":False,
        "starbourne_unlocked":False}
    with NATIVE_RECEIPT.open("x",encoding="utf-8") as f:
        json.dump(report,f,sort_keys=True,indent=2)
    @unreal.AutomationScheduler.add_latent_command
    def capture():
        try:
            images=[]
            for frame,cam in zip(FRAMES,cameras):
                task=unreal.AutomationLibrary.take_high_res_screenshot(
                    SIZE[0],SIZE[1],str(frame),camera=cam,delay=.45,
                    force_game_view=True,capture_hdr=False)
                if task is None or not task.is_valid_task():
                    raise RuntimeError("PBR_GPU_HOLD: real D3D11 screenshot task not valid")
                tick=0
                while not task.is_task_done():
                    tick+=1
                    if tick>2500:
                        raise RuntimeError("PBR_GPU_HOLD: screenshot task tick budget exceeded")
                    yield
                if not frame.is_file():
                    raise RuntimeError("PBR_GPU_HOLD: screenshot completed without real PNG")
                images.append(validate_png(frame))
                yield
            if source.sha(WORLD_FILE)!=before:
                raise RuntimeError("PBR_GPU_HOLD: saved 200-actor World bytes changed")
            report.update(status=STATUS,images=images,source_world_preserved=True)
        except Exception as e:
            report.update(status="NATIVE_PBR_GPU_CAPTURE_HOLD",error=str(e),
                          traceback=traceback.format_exc()[-2500:])
            unreal.log_error("FIRSTWAKE_PBR_GPU_HOLD "+str(e))
            raise
        finally:
            NATIVE_RECEIPT.write_text(json.dumps(report,sort_keys=True,indent=2),encoding="utf-8")
            unreal.log("FIRSTWAKE_PBR_GPU_NATIVE_RECEIPT "+json.dumps(report,sort_keys=True))
    return report

if __name__=="__main__":
    import unreal
    unreal.log("FIRSTWAKE_PBR_GPU_START "+json.dumps(schedule(),sort_keys=True))
