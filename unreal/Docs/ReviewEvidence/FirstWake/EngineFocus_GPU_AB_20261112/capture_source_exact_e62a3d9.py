"""Read-only GPU focus comparison. Unreal 5.8.4 embedded Python, isolated worktree.
This writes only under unreal/Saved/EngineFocusReviewV1 and NEVER saves the map.
No player camera, PIE, source edits, production map changes, asset promotion.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import traceback
import unreal as u

ROOT = Path(u.Paths.project_dir()).resolve().parent
PROJECT = ROOT / "unreal"
SAVE = PROJECT / "Saved" / "EngineFocusReviewV1"
OUT = SAVE / "GPUCapture_20261112_e62a3d9_V2"
MAP = PROJECT / "Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"
ORIGINAL = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
EXPECTED_HEAD = "e62a3d9b4d711ad95484d609b2e6282f6b4da673"
MAP_SHA = "9338c2abdebd7eeb19e50fb98733a9358d417f0633f8947aa9c6d48259c5e65a"
ORIGINAL_SHA = "a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69"
MAP_ASSET = "/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview"
RESOLUTION = (960, 540)
NAMES = (
 "TSTSS_BOKEH_ENGINE_REVIEW_EngineInspection_Optical",
 "TSTSS_BOKEH_ENGINE_REVIEW_EngineInspection_NoDoF",
)
FILES = ("EngineInspection_Optical_GPU.png", "EngineInspection_NoDOF_GPU.png")
CFG = ("DefaultEngine.ini", "DefaultInput.ini")
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok, reason):
    if not ok:
        raise RuntimeError("HOLD_GPU_REVIEW: " + reason)
def git(*args):
    p=subprocess.run(["git","-C",str(ROOT),*args],text=True,capture_output=True,timeout=15)
    require(p.returncode==0,"git custody failed")
    return p.stdout.strip()
def png_dimensions(path):
    b=path.read_bytes()
    require(len(b)>30000 and b[:8]==b"\x89PNG\r\n\x1a\n" and b[12:16]==b"IHDR",
            "invalid/empty native screenshot PNG: "+str(path))
    width,height=struct.unpack(">II",b[16:24])
    require((width,height)==(810,540), "GPU filmback output not 3:2 / 810x540: "+str((width,height)))
    return width,height

ctx={"started":time.monotonic(),"ticks":0,"phase":"warmup","index":0,"task":None,
     "capture_paths":[],"handle":None,"cameras":[],"last_shot_tick":0,"prev_cfg":None}
def verify_invariants():
    require(ROOT.name=="TSTSS_BokehFocusReview_20261111","worktree not isolated")
    require(git("rev-parse","HEAD")==EXPECTED_HEAD,"source head drift")
    require(git("status","--porcelain")=="","source checkout dirty")
    require(sha(MAP)==MAP_SHA and sha(ORIGINAL)==ORIGINAL_SHA,"source/review map hash drift")
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),"wrong UE version")
    cmd=str(u.SystemLibrary.get_command_line()).lower()
    require("-renderoffscreen" in cmd and "-nullrhi" not in cmd,
            "actual GPU RHI / offscreen launch not established")
    require(os.environ.get("TSTSS_GPU_CAPTURE_OPT_IN")=="1","capture not explicitly opted in")
    require(os.environ.get("TSTSS_GPU_CAPTURE_EXPECTED_HEAD")==EXPECTED_HEAD,
            "capture source-lock env missing")
    require(not OUT.exists(),"prior GPU evidence directory occupied")
    require(hasattr(u.AutomationLibrary,"take_high_res_screenshot"),"Unreal screenshot API absent")
    require(hasattr(u.EditorPythonScripting,"set_keep_python_script_alive"),"keep-alive API absent")
def stop(error=None):
    try:
        if ctx["handle"] is not None:
            u.unregister_slate_post_tick_callback(ctx["handle"])
            ctx["handle"]=None
    except Exception: pass
    if error is not None:
        try:
            OUT.mkdir(parents=True,exist_ok=True)
            (OUT/"capture_failed.json").write_text(json.dumps(
             {"status":"HOLD_GPU_CAPTURE_NOT_PROVEN","reason":str(error),
              "traceback":traceback.format_exc(),"ticks":ctx["ticks"],
              "native_visual_approved":False},indent=2),encoding="utf-8")
        except Exception: pass
        u.log_error("TSTSS_GPU_CAPTURE_HOLD "+str(error))
    try:
        u.EditorPythonScripting.set_keep_python_script_alive(False)
        u.SystemLibrary.quit_editor()
    except Exception as e:
        u.log_error("TSTSS_GPU_CAPTURE_QUIT_FAILED "+str(e))

def callback(delta):
    try:
        ctx["ticks"]+=1
        if time.monotonic()-ctx["started"]>125:
            raise RuntimeError("GPU capture exceeded 125s bounded deadline")
        if ctx["phase"]=="warmup":
            if ctx["ticks"]<45: return
            ctx["phase"]="request"
        if ctx["phase"]=="request":
            if ctx["ticks"]-ctx["last_shot_tick"]<5: return
            idx=ctx["index"]
            if idx>=2:
                raise RuntimeError("invalid camera index")
            path=OUT/FILES[idx]
            require(not path.exists(),"candidate screenshot output occupied")
            cam=ctx["cameras"][idx]
            # Explicit camera arg; do not change gameplay, view target, actor focus, or map.
            ctx["phase"]="launching"
            task=u.AutomationLibrary.take_high_res_screenshot(
                RESOLUTION[0],RESOLUTION[1],str(path),camera=cam,
                delay=0.1,force_game_view=True,capture_hdr=False)
            require(task is not None and task.is_valid_task(),"native screenshot task refused")
            ctx["task"]=task
            ctx["last_shot_tick"]=ctx["ticks"]
            ctx["phase"]="wait"
            u.log("TSTSS_GPU_CAPTURE_REQUESTED "+FILES[idx])
        elif ctx["phase"]=="wait":
            if not ctx["task"].is_task_done():return
            ctx["phase"]="file"
            ctx["file_wait_tick"]=ctx["ticks"]
        elif ctx["phase"]=="file":
            idx=ctx["index"]
            path=OUT/FILES[idx]
            if not path.exists():
                if ctx["ticks"]-ctx["file_wait_tick"]>40:
                    raise RuntimeError("native screenshot task done but output PNG absent: "+str(path))
                return
            dimensions=png_dimensions(path)
            ctx["capture_paths"].append(
                {"file":str(path),"sha256":sha(path),"bytes":path.stat().st_size,
                 "width":dimensions[0],"height":dimensions[1],
                 "camera_label":NAMES[idx]})
            u.log("TSTSS_GPU_CAPTURE_PNG_WRITTEN "+FILES[idx])
            ctx["index"]+=1
            ctx["task"]=None
            ctx["phase"]="request" if ctx["index"]<2 else "done"
        if ctx["phase"]=="done":
            require(len(ctx["capture_paths"])==2,"pair incomplete")
            require(ctx["capture_paths"][0]["sha256"]!=ctx["capture_paths"][1]["sha256"],
                    "identical image bytes: optical difference not supported")
            require(sha(MAP)==MAP_SHA and sha(ORIGINAL)==ORIGINAL_SHA,
                    "source or study map changed during native rendering")
            result={
                "status":"GPU_PNG_PAIR_CAPTURED_AWAITING_PIXEL_AND_CREATOR_QA",
                "engine":"UE 5.8.4", "review_only":True,"native_rhi_requested":True,
                "head":EXPECTED_HEAD,"map_sha256":MAP_SHA,
                "original_map_sha256":ORIGINAL_SHA,
                "camera_pair":list(NAMES), "images":ctx["capture_paths"],
                "ticks":ctx["ticks"], "pie":"NOT_RUN",
                "native_visual_approved":False,
                "render_qa":"NOT_ESTABLISHED",
                "gameplay_modified":False,"assets_promoted":False
            }
            (OUT/"capture_pair.json").write_text(
                json.dumps(result,indent=2),encoding="utf-8")
            u.log("TSTSS_GPU_CAPTURE_PAIR_PNG_RECORDED_PENDING_CREATOR_QA")
            stop()
    except Exception as e:
        stop(e)

try:
    verify_invariants()
    require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(),
            "unsaved editor maps before capture")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
            "unsaved Editor assets before capture")
    world=u.EditorLoadingAndSavingUtils.load_map(MAP_ASSET)
    require(world is not None,"isolated map could not reopen")
    editor=u.get_editor_subsystem(u.EditorActorSubsystem)
    actors=editor.get_all_level_actors()
    cams=[]
    for name in NAMES:
        matches=[x for x in actors if x.get_actor_label()==name]
        require(len(matches)==1 and isinstance(matches[0],u.CineCameraActor),
                "missing/duplicate native CineCamera: "+name)
        cams.append(matches[0])
    require(len(actors)==33,"review actor count drift")
    c0,c1=[cam.get_cine_camera_component() for cam in cams]
    for cam in (c0,c1):
        require(abs(float(cam.get_editor_property("current_focal_length"))-65.0)<0.01,
                "lens drift")
        require(abs(float(cam.get_editor_property("current_aperture"))-2.8)<0.01,
                "aperture drift")
    require(c0.get_editor_property("focus_settings").get_editor_property("focus_method")==
            u.CameraFocusMethod.MANUAL,"DOF-on changed")
    require(c1.get_editor_property("focus_settings").get_editor_property("focus_method")==
            u.CameraFocusMethod.DISABLE,"DOF-off changed")
    require(tuple(cams[0].get_actor_location().to_tuple())==
            tuple(cams[1].get_actor_location().to_tuple()),"A/B camera position drift")
    require(str(cams[0].get_actor_rotation())==str(cams[1].get_actor_rotation()),
            "A/B camera rotation drift")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(),
            "map became dirty after read-only camera lookup")
    ctx["cameras"]=cams
    OUT.mkdir(parents=True,exist_ok=False)
    # Keep Editor ticking while the asynchronous screenshot task is scheduled.
    u.EditorPythonScripting.set_keep_python_script_alive(True)
    ctx["handle"]=u.register_slate_post_tick_callback(callback)
    u.log("TSTSS_GPU_CAPTURE_READY_REAL_RHI_REQUESTED")
except Exception as exc:
    stop(exc)
