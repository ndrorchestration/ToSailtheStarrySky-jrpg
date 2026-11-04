"""TSTSS Ender V5 and detached goggles, transient UE 5.8 RenderTarget review.

Uses render-target export instead of the previously failing HighResShot task.
Only on disposable MH5. No map/MetaHuman/game asset is ever saved.
A native exported PNG is only technical capture evidence; human artist approval,
rigging, skin/head contact, and canonical promotion remain false.
"""
import builtins, hashlib, json, struct, time, traceback, zlib
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\Ender_goggles_noncanonical.glb")
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GLB_SHA="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
CHAR="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
MESH="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/GogglesCandidateV1/Ender_goggles_noncanonical/StaticMeshes/Ender_goggles_noncanonical.Ender_goggles_noncanonical"
LEVEL="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV1/RenderTargetCombined06_LightTenth"
IMG=OUT/"ender_v5_goggles_rt_front.png"
RECEIPT=OUT/"capture_receipt.json"
SIZE=(480,320)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(cond,msg):
    if not cond:raise RuntimeError("FAIL_CLOSED "+msg)
def png_core_info(p):
    data=p.read_bytes()
    require(data[:8]==b"\x89PNG\r\n\x1a\n","PNG header")
    pos=8;found=False;wh=None;image_chunks=0
    while pos+12<=len(data):
        n=struct.unpack_from(">I",data,pos)[0];tag=data[pos+4:pos+8]
        nxt=pos+12+n
        require(nxt<=len(data),"PNG bad chunk")
        payload=data[pos+8:pos+8+n]
        require((zlib.crc32(tag+payload)&0xffffffff)==struct.unpack_from(">I",data,pos+8+n)[0],"CRC")
        if tag==b"IHDR":wh=struct.unpack_from(">II",payload)
        if tag==b"IDAT":image_chunks+=1
        pos=nxt
        if tag==b"IEND":found=True;break
    require(found and image_chunks>0 and wh==SIZE,"PNG dimensions or core incomplete")
    return {"sha256_raw":hashlib.sha256(data).hexdigest(),"sha256_png_core":hashlib.sha256(data[:pos]).hexdigest(),
            "raw_bytes":len(data),"png_core_bytes":pos,"trailing_bytes_after_iend":len(data)-pos,
            "image_size":[*SIZE],"crc_pass":True}

require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","only MH5")
require("goggles fitting experiment (MH5)" in (ROOT/"CastAllSandbox.uproject").read_text(encoding="utf-8-sig"),"wrong clone")
require(not OUT.exists(),"prior output already exists")
require(sha(META)==META_SHA and sha(MAP)==MAP_SHA and sha(GLB)==GLB_SHA,"source hashes changed")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"wrong UE")
require(not getattr(builtins,"_tstss_v5_rt_combined_active",False),"duplicate request")
OUT.mkdir(parents=True)
record={"status":"IN_PROGRESS","kind":"NONCANONICAL_TRANSIENT_V5_AND_GOGGLES_RENDER_TARGET",
        "engine":unreal.SystemLibrary.get_engine_version(),
        "source_meta_sha256":META_SHA,"source_map_sha256":MAP_SHA,"source_goggles_sha256":GLB_SHA,
        "method":"SceneCapture2D -> RenderingLibrary.export_render_target",
        "original_art":False,"no_face_sculpt":True,"source_assets_saved":False,
        "review_map_saved":False,"production_game_modified":False,
        "real_head_collision_verified":False,"goggles_fit_approved":False,
        "materials_artist_approved":False,"face_likeness_approved":False,
        "rigging_verified":False,"canonical":False,"captures":[]}
def save():RECEIPT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
save()

try:
    le=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(le.load_level(LEVEL) is not False,"review level")
    world=unreal.EditorLevelLibrary.get_editor_world()
    require(world is not None,"editor world")
    char=unreal.load_asset(CHAR);mesh=unreal.load_asset(MESH)
    require(isinstance(char,unreal.MetaHumanCharacter),"MetaHuman missing")
    require(isinstance(mesh,unreal.StaticMesh),"imported goggles missing")
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets(assets=[char])
    pipeline=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    face_actor=pipeline.spawn_meta_human_actor(character=char)
    require(face_actor is not None,"MetaHuman preview actor missing")
    comps=face_actor.get_components_by_class(unreal.ActorComponent)
    names=[c.get_name() for c in comps if isinstance(c,unreal.SkeletalMeshComponent)]
    require("Face" in names and "Body" in names,"real preview face/body unavailable")
    origin=face_actor.get_actor_location()
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    goggles=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    require(goggles is not None,"goggles actor")
    goggles.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
    goggles.set_actor_label("TEMP_Review_Original_Ender_V5_Goggles")
    goggles.set_actor_rotation(unreal.Rotator(90,180,0),False)
    goggles.set_actor_location(unreal.Vector(origin.x,origin.y+9.5,origin.z+171.5),False,False)
    pos,ext=goggles.get_actor_bounds(False)
    bounds=[round(2*float(getattr(ext,key)),5) for key in "xyz"]
    require(all(abs(a-b)<.2 for a,b in zip(bounds,[18.21768,15.35,6.1])),"goggles dimensions/axes drift")
    record["goggles_world_xyz_extent_cm"]=bounds
    record["goggles_position_relative_to_v5_cm"]=[0,9.5,171.5]
    record["goggles_rotation_pitch_yaw_roll_deg"]=[90,180,0]
    record["metahuman_skeletal_preview_components"]=names
    record["native_preview_class"]=face_actor.get_class().get_name()
    # Bounded lights; native skin shaders may remain incomplete without Core Data.
    for idx,(dx,dy,dz,power) in enumerate(((52,74,205,110.0),(-45,68,179,65.0),(0,-75,191,52.0))):
        light=actors.spawn_actor_from_class(unreal.PointLight,
            unreal.Vector(origin.x+dx,origin.y+dy,origin.z+dz))
        require(light is not None,"studio light")
        light.set_actor_label("TEMP_V5_GogglesRT_Light_"+str(idx))
        comp=light.get_component_by_class(unreal.PointLightComponent)
        comp.set_editor_property("intensity",power*0.1)
        comp.set_editor_property("attenuation_radius",700.0)
    cam_actor=actors.spawn_actor_from_class(unreal.SceneCapture2D,
                 unreal.Vector(origin.x,origin.y+82,origin.z+170))
    require(cam_actor is not None,"SceneCapture2D actor")
    cam_actor.set_actor_label("TEMP_ReviewRT_V5_GogglesFront")
    cam_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(
        cam_actor.get_actor_location(),unreal.Vector(origin.x,origin.y+4.0,origin.z+164.0)),False)
    cap=cam_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    require(cap is not None,"SceneCapture2D component")
    cap.set_editor_property("fov_angle",31.0)
    cap.set_editor_property("capture_every_frame",False)
    cap.set_editor_property("capture_on_movement",False)
    cap.set_editor_property("capture_source",unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    target=unreal.RenderingLibrary.create_render_target2d(
        world_context_object=world,width=SIZE[0],height=SIZE[1],
        format=unreal.TextureRenderTargetFormat.RTF_RGBA8,
        clear_color=unreal.LinearColor(0.018,0.022,0.033,1.0),
        auto_generate_mip_maps=False)
    require(target is not None,"transient target")
    cap.set_editor_property("texture_target",target)
    cap.capture_scene()
    record["native_rt_initial_capture_queued"]=True
    save()
except Exception:
    record["status"]="SETUP_FAILED"
    record["error"]=traceback.format_exc()[-4500:]
    record["meta_sha256_after"]=sha(META);record["map_sha256_after"]=sha(MAP)
    record["goggles_sha256_after"]=sha(GLB)
    save()
    raise

class Runner:
    def __init__(self):
        self.t0=time.monotonic();self.frame=0;self.handle=None
        self.world=world;self.cap=cap;self.target=target
        self.face_actor=face_actor;self.goggles=goggles;self.scene=cam_actor
    def end(self,status,error=None):
        record["status"]=status
        if error:record["error"]=str(error)[-3500:]
        record["meta_sha256_after"]=sha(META);record["map_sha256_after"]=sha(MAP)
        record["goggles_sha256_after"]=sha(GLB)
        if any((record["meta_sha256_after"]!=META_SHA,record["map_sha256_after"]!=MAP_SHA,
                record["goggles_sha256_after"]!=GLB_SHA)):
            record["status"]="FAIL_SOURCE_MUTATED"
        save()
        if self.handle is not None:unreal.unregister_slate_post_tick_callback(self.handle)
        builtins._tstss_v5_rt_combined_active=False
        builtins._tstss_v5_rt_combined_runner=None
        unreal.log("TSTSS_V5_GOGGLES_RT_FINAL "+record["status"]+" "+str(RECEIPT))
    def tick(self,dt):
        try:
            self.frame+=1
            if time.monotonic()-self.t0>75:
                self.end("TIMED_OUT_NO_VALIDATED_RENDER_TARGET")
                return
            if self.frame==7:self.cap.capture_scene()
            if self.frame==19:
                unreal.RenderingLibrary.export_render_target(
                    self.world,self.target,str(OUT),IMG.name)
                record["native_rt_export_called"]=True;save()
                unreal.log("TSTSS_V5_GOGGLES_RT_EXPORT_CALLED "+str(IMG))
            if self.frame>=22 and IMG.exists():
                try:core=png_core_info(IMG)
                except Exception:
                    if self.frame<65:return
                    raise
                record["captures"].append(core)
                self.end("NATIVE_V5_GOGGLES_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED")
        except Exception:
            self.end("RUNTIME_FAILED",traceback.format_exc())
            unreal.log_error("TSTSS_V5_GOGGLES_RT_FAILED "+traceback.format_exc())
runner=Runner()
builtins._tstss_v5_rt_combined_active=True
builtins._tstss_v5_rt_combined_runner=runner
try:runner.handle=unreal.register_slate_post_tick_callback(runner.tick)
except Exception:
    runner.end("TICK_REGISTRATION_FAILED",traceback.format_exc())
    raise
unreal.log("TSTSS_V5_GOGGLES_RT_ARMED "+str(RECEIPT))
