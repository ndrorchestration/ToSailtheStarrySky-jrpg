"""Native UE5.8.4 Ender V5 + original copper hair V1 + sealed goggles V2.

Temporary 3D review ONLY; source MetaHuman, review map, equipment and game
remain unchanged. Actual PNG pixels determine success, NOT code execution.
"""
import builtins
import hashlib
import json
import struct
import time
import traceback
import zlib
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
HAIR_GLB=Path(r"C:\TSTSS_EnderHairNativeV1_20261104\unreal\ArtSource\Characters\HairReview\Candidates\Ender_DarkCopper_LayeredHair_V1_NONCANONICAL.glb")
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GLB_SHA="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
HAIR_SHA="01bb9f400454d633c5e887cd47a12fd1af34e5bbf6b7c05ab6a5929b0a6db562"
CHAR="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
MESH=json.loads((ROOT/"Saved/CharacterLookdev/GogglesFitV2/native_import01.json").read_text(encoding="utf-8"))["native_mesh"]
HAIR_MESH=json.loads((ROOT/"Saved/CharacterLookdev/EnderHairReviewV1/native_import01.json").read_text(encoding="utf-8"))["imported_mesh"]
LEVEL="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
OUT=ROOT/"Saved/CharacterLookdev/EnderHairReviewV1/NativeHairAndV2Goggles01"
IMG=OUT/"ender_v5_copper_hair_v1_plus_sealed_goggles_v2_front.png"
RECEIPT=OUT/"capture_receipt.json"
SIZE=(480,320)

def require(cond,msg):
    if not cond:raise RuntimeError("FAIL_CLOSED "+msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def png_core_info(path):
    data=path.read_bytes()
    require(data[:8]==b"\x89PNG\r\n\x1a\n","PNG header")
    pos=8;seen_idat=False;dims=None;ended=False
    while pos+12 <= len(data):
        count=struct.unpack_from(">I",data,pos)[0]
        name=data[pos+4:pos+8]
        require(count<20_000_000 and pos+count+12<=len(data),"PNG chunk bounds")
        payload=data[pos+8:pos+8+count]
        expected=struct.unpack_from(">I",data,pos+8+count)[0]
        require((zlib.crc32(name+payload)&0xffffffff)==expected,"PNG CRC")
        if name==b"IHDR":dims=struct.unpack_from(">II",payload)
        if name==b"IDAT":seen_idat=True
        pos+=count+12
        if name==b"IEND":
            ended=True
            break
    require(ended and seen_idat and dims==SIZE,"PNG core incomplete or wrong dimensions")
    return {"png_core_sha256":hashlib.sha256(data[:pos]).hexdigest(),
            "png_raw_sha256":hashlib.sha256(data).hexdigest(),
            "original_raw_bytes":len(data),"valid_png_core_bytes":pos,
            "trailing_bytes":len(data)-pos,"png_crc_pass":True,
            "size":[*SIZE]}

require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","only disposable MH5")
require("goggles fitting experiment (MH5)" in (ROOT/"CastAllSandbox.uproject").read_text(encoding="utf-8-sig"),"clone marker")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine")
require(not OUT.exists(),"no evidence overwrite")
require(all((p.is_file() for p in (META,MAP,GLB,HAIR_GLB))),"missing source")
require(all((sha(p)==expected for p,expected in
             ((META,META_SHA),(MAP,MAP_SHA),(GLB,GLB_SHA),(HAIR_GLB,HAIR_SHA)))),
        "source asset hash changed")
require(not getattr(builtins,"_tstss_ender_hair_v1_native_running",False),"duplicate runner")
OUT.mkdir(parents=True)
report={"status":"IN_PROGRESS",
        "kind":"TRANSIENT_UNAPPROVED_MH5_AND_HAIR_V1_AND_SEALED_GOGGLES_V2",
        "source_meta_sha256":META_SHA,"source_map_sha256":MAP_SHA,
        "source_goggles_v2_glb_sha256":GLB_SHA,"source_hair_glb_sha256":HAIR_SHA,
        "engine":unreal.SystemLibrary.get_engine_version(),
        "native_3d_render":False,"actual_scalp_intersection_verified":False,
        "goggles_wearable_fit":False,"approved_face_likeness":False,
        "hair_visual_approval":False,"hair_color_lock_approved":False,
        "rigging_verified":False,"hair_is_static_mesh":True,
        "source_assets_saved":False,"map_saved":False,
        "production_game_changed":False,"canonical":False,"captures":[]}
def save():RECEIPT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
save()
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(sub.load_level(LEVEL) is not False,"review map")
    world=unreal.EditorLevelLibrary.get_editor_world()
    require(world is not None,"Editor world")
    char=unreal.load_asset(CHAR)
    goggles_mesh=unreal.load_asset(MESH)
    hair_mesh=unreal.load_asset(HAIR_MESH)
    require(isinstance(char,unreal.MetaHumanCharacter),"real MetaHuman")
    require(isinstance(goggles_mesh,unreal.StaticMesh) and isinstance(hair_mesh,unreal.StaticMesh),
            "real imported native static meshes")
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets(assets=[char])
    authoring=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    face_actor=authoring.spawn_meta_human_actor(character=char)
    require(face_actor is not None,"transient MH face")
    names=[c.get_name() for c in face_actor.get_components_by_class(unreal.SkeletalMeshComponent)]
    require("Face" in names and "Body" in names,"real face/body skeletal preview")
    origin=face_actor.get_actor_location()
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def create_static(name,mesh,delta):
        obj=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
        require(obj is not None,name+" actor")
        obj.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
        obj.set_actor_label(name)
        obj.set_actor_rotation(unreal.Rotator(90,180,0),False)
        obj.set_actor_location(unreal.Vector(origin.x+delta[0],origin.y+delta[1],
                                            origin.z+delta[2]),False,False)
        return obj
    goggles=create_static("TEMP_Review_SealedGogglesV2",goggles_mesh,(0,9.5,168.5))
    hair=create_static("TEMP_Review_CopperLayeredHairV1",hair_mesh,(0,0,172.0))
    gp,ge=goggles.get_actor_bounds(False)
    hp,he=hair.get_actor_bounds(False)
    goggles_size=[round(2*float(getattr(ge,key)),4) for key in "xyz"]
    hair_size=[round(2*float(getattr(he,key)),4) for key in "xyz"]
    require(all((abs(a-b)<.3 for a,b in zip(goggles_size,(19.2,19.171,8.02)))),
            "V2 goggles size/axis")
    require(all((abs(a-b)<.6 for a,b in zip(hair_size,(23.0297,24.3367,18.7177)))),
            "hair native size/axis")
    report["hair_mesh"]=hair_mesh.get_path_name()
    report["goggles_mesh"]=goggles_mesh.get_path_name()
    report["hair_world_extent_xyz_cm"]=hair_size
    report["goggles_world_extent_xyz_cm"]=goggles_size
    report["goggles_trial_relative_xyz_cm"]=[0,9.5,168.5]
    report["hair_trial_relative_xyz_cm"]=[0,0,172]
    for i,(x,y,z,power) in enumerate(((52,74,205,110.0),(-45,68,179,65.0),(0,-75,191,52.0))):
        light=actors.spawn_actor_from_class(unreal.PointLight,
              unreal.Vector(origin.x+x,origin.y+y,origin.z+z))
        require(light is not None,"temporary studio light")
        light.set_actor_label("TEMP_EnderHairV1_Light"+str(i))
        comp=light.get_component_by_class(unreal.PointLightComponent)
        comp.set_editor_property("intensity",power*0.1)
        comp.set_editor_property("attenuation_radius",700.0)
    cam=actors.spawn_actor_from_class(unreal.SceneCapture2D,
         unreal.Vector(origin.x,origin.y+82,origin.z+170))
    require(cam is not None,"camera")
    cam.set_actor_label("TEMP_EnderV5_CopperHairV1_Camera")
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(
        cam.get_actor_location(),
        unreal.Vector(origin.x,origin.y+4.0,origin.z+164.0)),False)
    capture=cam.get_component_by_class(unreal.SceneCaptureComponent2D)
    require(capture is not None,"SceneCapture component")
    capture.set_editor_property("fov_angle",31.0)
    capture.set_editor_property("capture_every_frame",False)
    capture.set_editor_property("capture_on_movement",False)
    capture.set_editor_property("capture_source",unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    target=unreal.RenderingLibrary.create_render_target2d(
        world_context_object=world,width=SIZE[0],height=SIZE[1],
        format=unreal.TextureRenderTargetFormat.RTF_RGBA8,
        clear_color=unreal.LinearColor(0.018,0.022,0.033,1),
        auto_generate_mip_maps=False)
    require(target is not None,"render target")
    capture.set_editor_property("texture_target",target)
    capture.capture_scene()
    report["temporary_capture_queued"]=True
    save()
except Exception:
    report["status"]="SETUP_FAILED"
    report["error"]=traceback.format_exc()[-3800:]
    report["source_meta_sha256_after"]=sha(META)
    report["source_map_sha256_after"]=sha(MAP)
    report["source_goggles_sha256_after"]=sha(GLB)
    report["source_hair_sha256_after"]=sha(HAIR_GLB)
    save()
    raise

class Runner:
    def __init__(self):
        self.start=time.monotonic()
        self.frame=0
        self.handle=None
        self.resources=(world,face_actor,goggles,hair,cam,capture,target)
    def finish(self,status,error=None):
        report["status"]=status
        if error:report["error"]=str(error)[-2400:]
        for key,path in (("meta",META),("map",MAP),("goggles",GLB),("hair",HAIR_GLB)):
            report["source_"+key+"_sha256_after"]=sha(path)
        if (report["source_meta_sha256_after"]!=META_SHA or
            report["source_map_sha256_after"]!=MAP_SHA or
            report["source_goggles_sha256_after"]!=GLB_SHA or
            report["source_hair_sha256_after"]!=HAIR_SHA):
            report["status"]="FAIL_SOURCE_HASH_DRIFT"
        save()
        if self.handle is not None:
            unreal.unregister_slate_post_tick_callback(self.handle)
        builtins._tstss_ender_hair_v1_native_running=False
        builtins._tstss_ender_hair_v1_native_runner=None
        unreal.log("TSTSS_ENDER_HAIR_NATIVE_FINAL "+report["status"]+" "+str(RECEIPT))
    def tick(self,dt):
        try:
            self.frame+=1
            if time.monotonic()-self.start>80:
                self.finish("TIMED_OUT_NO_IMAGE")
                return
            if self.frame==7:capture.capture_scene()
            if self.frame==19:
                unreal.RenderingLibrary.export_render_target(world,target,str(OUT),IMG.name)
                report["native_rt_export_called"]=True
                save()
            if self.frame>=22 and IMG.exists():
                try:info=png_core_info(IMG)
                except Exception:
                    if self.frame<65:return
                    raise
                report["captures"].append(info)
                report["native_3d_render"]=True
                self.finish("NATIVE_ENDER_COPPER_HAIR_V1_AND_GOGGLES_V2_GPU_PASS_ART_HOLD")
        except Exception:
            self.finish("RUNTIME_FAILED",traceback.format_exc())
            unreal.log_error("TSTSS_ENDER_HAIR_NATIVE "+traceback.format_exc())
runner=Runner()
builtins._tstss_ender_hair_v1_native_running=True
builtins._tstss_ender_hair_v1_native_runner=runner
try:runner.handle=unreal.register_slate_post_tick_callback(runner.tick)
except Exception:
    runner.finish("TICK_SETUP_FAILED",traceback.format_exc())
    raise
unreal.log("TSTSS_ENDER_HAIR_NATIVE_ARMED "+str(RECEIPT))
