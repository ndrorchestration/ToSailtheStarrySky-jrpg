"""Capture ONE genuine native UE5.8.4 D3D11 Skybourne candidate frame in isolated sandbox.

Temporary/noncanonical assembled map: no production scene, game route, model
approval, user Editor/PIE action or final-cinematic appearance implied.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import struct
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
MAP="/Game/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor"
MAP_FILE=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap"
MAP_SHA="16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40"
CAMERA="V4_NONCANONICAL_CAMERA_THREE_QUARTER"
ATTEMPT=os.environ.get("TSTSS_V4_CAPTURE_ATTEMPT","")
if not re.fullmatch(r"[a-z][a-z0-9_]{2,18}",ATTEMPT):
    raise RuntimeError("Capture requires a unique validated attempt label")
DIR=ROOT/("SkybourneV4NativeGPU_20261103_"+ATTEMPT)
PNG=DIR/"Skybourne_V4_UE584_D3D11_ThreeQuarter_REVIEW.png"
RECEIPT=DIR/"native_skybourne_gpu_capture_receipt.json"
info={"state":"NOT_STARTED",
      "art_authority":"NONCANONICAL_PREVIEW_NOT_ART_APPROVED",
      "real_gpu_capture_requested":True,
      "starbourne_player_unlock":False,"production_content_modified":False,
      "scene_save_allowed":False,"source_map_sha_expected":MAP_SHA}
if DIR.exists():raise FileExistsError("Capture output already exists; refuse overwrite")
try:
    assert Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve()
    project_data=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    assert "AUREATE_CINEMATIC_V4_REVIEW_ONLY" in project_data["Description"]
    info["engine"]=unreal.SystemLibrary.get_engine_version()
    assert info["engine"].startswith("5.8.")
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    assert MAP_FILE.is_file() and sha(MAP_FILE)==MAP_SHA,"Source review map changed or absent"
    subsystem=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert subsystem.load_level(MAP),"Could not load isolated Skybourne map"
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    cameras=[x for x in actors if isinstance(x,unreal.CameraActor) and x.get_actor_label()==CAMERA]
    assert len(cameras)==1,"Missing exact Skybourne comparison camera"
    cam=cameras[0]
    wanted={"V4_NONCANONICAL_"+slot+"_V4_GOLD_FILIGREE" for slot in (
        "FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")}
    found={x.get_actor_label() for x in actors if x.get_actor_label().endswith("_V4_GOLD_FILIGREE")}
    assert found==wanted, "Wrong four V4 wing lace identities"
    assert len([x for x in actors if x.get_actor_label()=="V4_NONCANONICAL_SHARED_HULL_CINEMATIC_V4_TRIM"])==1
    assert hasattr(unreal,"AutomationScheduler"),"Native automation scheduler unavailable"
    DIR.mkdir(parents=True,exist_ok=False)
    info["native_actor_count"]=len(actors)
    info["camera_label"]=CAMERA
    info["image_path"]=str(PNG)
    info["requested_dimensions"]=[1280,720]
    info["source_map_sha_before"]=sha(MAP_FILE)
    info["state"]="NATIVE_CAPTURE_REQUESTED_NOT_YET_DONE"
    RECEIPT.write_text(json.dumps(info,indent=2,sort_keys=True)+"\n",encoding="utf8")
except Exception as exc:
    info["state"]="NATIVE_CAPTURE_PRECHECK_FAILED"
    info["error"]=str(exc)
    info["traceback"]=traceback.format_exc()[-4000:]
    if DIR.is_dir():RECEIPT.write_text(json.dumps(info,indent=2,sort_keys=True)+"\n",encoding="utf8")
    unreal.log_error("V4_SKY_CAPTURE_PRECHECK_FAILED "+json.dumps(info))
    raise

@unreal.AutomationScheduler.add_latent_command
def capture_frame():
    try:
        req=unreal.AutomationLibrary.take_high_res_screenshot(
             1280,720,str(PNG),camera=cam,delay=.5,force_game_view=True)
        if not req.is_valid_task():raise RuntimeError("Unreal screenshot task invalid")
        ticks=0
        while not req.is_task_done():
            ticks+=1
            if ticks>1800:raise RuntimeError("Screenshot task exceeded 1800 ticks")
            yield
        if not PNG.is_file():raise RuntimeError("Native screenshot task finished with no file")
        raw=PNG.read_bytes()
        if len(raw)<4096 or raw[:8]!=b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("Native capture artifact absent/invalid/too small")
        width,height=struct.unpack_from(">II",raw,16)
        if (width,height)!=(1280,720):raise RuntimeError("Wrong PNG dimensions")
        if sha(MAP_FILE)!=MAP_SHA:raise RuntimeError("Review source map changed during capture")
        info.update({"state":"NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING",
                     "native_task_complete":True,
                     "task_ticks":ticks,"png_sha256":hashlib.sha256(raw).hexdigest(),
                     "png_bytes":len(raw),"actual_dimensions":[width,height],
                     "source_map_sha_after":sha(MAP_FILE),
                     "image_art_approved":False,
                     "native_assembled_scene":True,
                     "gameplay_transition_tested":False,
                     "continuous_collision_tested":False})
    except Exception as exc:
        info["state"]="NATIVE_GPU_CAPTURE_FAILED_NOT_A_RENDER_PASS"
        info["error"]=str(exc)
        info["traceback"]=traceback.format_exc()[-3500:]
        unreal.log_error("V4_SKY_GPU_CAPTURE_FAILED "+str(exc))
    finally:
        RECEIPT.write_text(json.dumps(info,indent=2,sort_keys=True)+"\n",encoding="utf8")
        unreal.log("V4_SKY_GPU_CAPTURE_RECEIPT "+json.dumps(info,sort_keys=True))
