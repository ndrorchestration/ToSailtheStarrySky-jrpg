"""Exact-source-locked two-process disposable VS02 optical map composition.
PREPARE saves a copy via Save Map As. COMPOSE requires a fresh Unreal process.
Never writes original VS02, GameMode, save data, protected config or source.
"""
from pathlib import Path
import hashlib, json, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
HERE=PROJECT/"Saved/OpticalVS02Stage"
SOURCE="/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors"
DEST="/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview"
DEST_ROOT="/Game/TSTSS/Review/EngineFocus_V1"
SOURCE_FILE=PROJECT/"Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
DEST_FILE=PROJECT/"Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"
PREPARE=HERE/"prepare.json"; COMPOSE=HERE/"compose.json"
HEAD="e7686bcb2f262ca9de0e6f9ceba96c812b93731f"
GAUGE="TSTSS_VS_REVIEW_InstrumentCore_LIFT"
ENGINE="TSTSS_VS_REVIEW_MainHarmonicLevitationEngine_Proxy"
ATMOS="TSTSS_OPTICAL_REVIEW_SingleAtmosphereDirector"
RECEIVER="TSTSS_OPTICAL_REVIEW_Receiver_Disabled"
LIGHTS=("TSTSS_VS_REVIEW_SunKey","TSTSS_VS_REVIEW_SkyAmbient",
        "TSTSS_VS_REVIEW_Atmosphere","TSTSS_VS_REVIEW_AerialFog")
def require(x,msg):
    if not x:raise RuntimeError("HOLD: "+msg)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):
    result=subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,text=True,timeout=20)
    require(result.returncode==0,"git failure")
    return result.stdout.strip()
def custody():
    phase=os.environ.get("TSTSS_VS02_OPTICAL_PHASE","")
    require(phase in ("prepare","compose"),"bad phase")
    require(os.environ.get("TSTSS_VS02_OPTICAL_STAGE_EXPLICIT")=="1","no explicit opt in")
    require(os.environ.get("TSTSS_VS02_OPTICAL_EXPECTED_HEAD","").lower()==HEAD,"head flag")
    require(sys.platform=="win32" and ROOT.name=="TSTSS_836_835_OpticalGraft_20261114","wrong worktree")
    require(git("rev-parse","HEAD")==HEAD,"source HEAD drift")
    require(SOURCE_FILE.is_file(),"source absent")
    require(not list((PROJECT/"Saved/SaveGames").glob("*.sav")),"player save files present")
    changes=git("status","--porcelain=v1","--untracked-files=all").splitlines()
    if phase=="prepare":
        require(not changes and not DEST_FILE.parent.exists() and not PREPARE.exists(),
                "prepare must begin pristine, empty destination")
    else:
        require(PREPARE.is_file() and DEST_FILE.is_file() and not COMPOSE.exists(),
                "compose files missing or destination already used")
        require(all(x.startswith("?? unreal/Content/TSTSS/Review/EngineFocus_V1/") for x in changes),
                "foreign/unreviewed source changes")
    return phase,dict(head=HEAD,source_sha256=hashfile(SOURCE_FILE),
        config_sha256={n:hashfile(PROJECT/"Config"/n) for n in ("DefaultEngine.ini","DefaultInput.ini")})
def unchanged(c):
    require(hashfile(SOURCE_FILE)==c["source_sha256"],"original map modified")
    for name,expected in c["config_sha256"].items():
        require(hashfile(PROJECT/"Config"/name)==expected,"protected config drift "+name)
def one(editor,label):
    items=[x for x in editor.get_all_level_actors() if str(x.get_actor_label())==label]
    require(len(items)==1,"expected exactly one "+label+" got "+str(len(items)))
    return items[0]
def cam(u,editor,label,gauge,disabled):
    target=gauge.get_actor_location()
    eye=target+u.Vector(-350,-610,265)
    actor=editor.spawn_actor_from_class(u.CineCameraActor,eye,u.MathLibrary.find_look_at_rotation(eye,target))
    require(actor is not None,"CineCamera spawn failed "+label)
    actor.set_actor_label(label)
    actor.set_actor_enable_collision(False)
    component=actor.get_cine_camera_component()
    require(component is not None,"missing CineCamera component")
    component.set_editor_property("current_focal_length",65.0)
    component.set_editor_property("current_aperture",2.8)
    focus=component.get_editor_property("focus_settings")
    focus.set_editor_property("focus_method",u.CameraFocusMethod.DISABLE if disabled else u.CameraFocusMethod.MANUAL)
    dist=((float(eye.x-target.x))**2+(float(eye.y-target.y))**2+(float(eye.z-target.z))**2)**0.5
    focus.set_editor_property("manual_focus_distance",dist)
    focus.set_editor_property("smooth_focus_changes",False)
    focus.set_editor_property("draw_debug_focus_plane",False)
    component.set_editor_property("focus_settings",focus)
    return dict(label=label,manual_focus_cm=round(dist,1),focal_mm=65.0,f_stop=2.8,
                dof="Disabled" if disabled else "Manual")
def run():
    phase,c=custody()
    import unreal as u
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),"wrong Unreal version")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(),"dirty existing map")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),"dirty existing content")
    editor=u.get_editor_subsystem(u.EditorActorSubsystem)
    require(editor is not None,"actor editor unavailable")
    if phase=="prepare":
        require(not u.EditorAssetLibrary.does_directory_exist(DEST_ROOT),"native destination occupied")
        world=u.EditorLoadingAndSavingUtils.load_map(SOURCE)
        require(world is not None,"VS02 source load failed")
        actors=editor.get_all_level_actors()
        for name in (GAUGE,ENGINE,*LIGHTS):one(editor,name)
        require(not any(str(a.get_actor_label()).startswith("TSTSS_OPTICAL_REVIEW_") for a in actors),
                "already composed source")
        require(u.EditorAssetLibrary.make_directory(DEST_ROOT),"review directory failed")
        require(u.EditorLoadingAndSavingUtils.save_map(world,DEST),"Save Map As rejected")
        require(DEST_FILE.is_file(),"no copied package")
        unchanged(c)
        result={**c,"status":"VS02_OPTICAL_COPY_NATIVE_SAVED_NOT_PIE",
                "actor_count":len(actors),"copy_base_sha256":hashfile(DEST_FILE)}
        with PREPARE.open("x",encoding="utf-8") as f:json.dump(result,f,indent=2)
        u.log("TSTSS_VS02_OPTICAL_PREPARE_OK_NOT_PIE")
        return result
    prepared=json.loads(PREPARE.read_text(encoding="utf-8"))
    require(prepared["status"]=="VS02_OPTICAL_COPY_NATIVE_SAVED_NOT_PIE"
            and prepared["head"]==HEAD
            and prepared["source_sha256"]==c["source_sha256"]
            and prepared["copy_base_sha256"]==hashfile(DEST_FILE),"preparation receipt drift")
    world=u.EditorLoadingAndSavingUtils.load_map(DEST)
    require(world is not None,"copy load failed")
    require(len(editor.get_all_level_actors())==prepared["actor_count"],"actor count drift")
    gauge=one(editor,GAUGE);one(editor,ENGINE)
    for name in LIGHTS:one(editor,name)
    director_class=u.load_class(None,"/Script/ToSailTheStarrySky.TSTSSAtmosphereDirector")
    require(director_class is not None,"C++ atmosphere class absent")
    director=editor.spawn_actor_from_class(director_class,u.Vector(0,0,0),u.Rotator(0,0,0))
    require(director is not None and str(director.get_class().get_name())=="TSTSSAtmosphereDirector",
            "native director not spawned")
    director.set_actor_label(ATMOS)
    director.set_editor_property("autoplay_review_cycle",False)
    # Only the disposable copy loses its legacy independent light owners.
    for name in LIGHTS:
        require(editor.destroy_actor(one(editor,name)),"failed to replace copied light: "+name)
    studies=[
        cam(u,editor,"TSTSS_OPTICAL_REVIEW_Inspection_ManualDOF",gauge,False),
        cam(u,editor,"TSTSS_OPTICAL_REVIEW_Inspection_NoDOF_Control",gauge,True)]
    receiver_class=u.load_class(None,"/Script/ToSailTheStarrySky.TSTSSReviewFocusReceiver")
    require(receiver_class is not None,"C++ review receiver absent")
    receiver=editor.spawn_actor_from_class(receiver_class,u.Vector(0,0,0),u.Rotator(0,0,0))
    require(receiver is not None,"receiver spawn failed")
    receiver.set_actor_label(RECEIVER)
    receiver.set_editor_property("explicit_review_opt_in",False)
    require(receiver.get_editor_property("explicit_review_opt_in") is False,"receiver enabled accidentally")
    require(sum(a.get_class().get_name()=="TSTSSAtmosphereDirector" for a in editor.get_all_level_actors())==1,
            "director not unique")
    require(u.EditorLoadingAndSavingUtils.save_map(world,DEST),"composed copy save failed")
    unchanged(c)
    result={**prepared,"status":"VS02_OPTICAL_COMPOSED_NATIVE_NOT_PIE_OR_VISUAL",
            "new_actor_count":len(editor.get_all_level_actors()),
            "copy_sha256":hashfile(DEST_FILE),"director":ATMOS,
            "source_lights_replaced_in_copy":list(LIGHTS),"studies":studies,
            "receiver_enabled":False,"player_C_key_tested":False,"gpu_captured":False}
    with COMPOSE.open("x",encoding="utf-8") as f:json.dump(result,f,indent=2)
    u.log("TSTSS_VS02_OPTICAL_COMPOSE_OK_NOT_PIE "+result["copy_sha256"])
    return result
if __name__=="__main__": print(json.dumps(run(),indent=2))
