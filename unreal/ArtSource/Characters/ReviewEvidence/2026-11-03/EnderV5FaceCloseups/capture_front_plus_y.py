"""Noncanonical V5 MetaHuman transient preview screenshot in isolated MH4 only."""
import builtins,hashlib,json,struct,time,traceback,zlib
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
ASSET=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
ASSET_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
OBJ="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
LEVEL="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
OUT=ROOT/"Saved/CharacterLookdev/V5NativeScreens/ender_v5_green_truefront02"
SIZE=(800,450)
def digest(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def guard(x,msg):
    if not x:raise RuntimeError("FAIL_CLOSED "+msg)
def png_meta(path):
    blob=path.read_bytes()
    guard(blob[:8]==b"\x89PNG\r\n\x1a\n","PNG header")
    i,w,h,count,ended=8,0,0,0,False
    while i+12<=len(blob):
        n=struct.unpack_from(">I",blob,i)[0]
        tag=blob[i+4:i+8]
        j=i+12+n
        guard(j<=len(blob),"PNG chunk bounds")
        payload=blob[i+8:i+8+n]
        crc=struct.unpack_from(">I",blob,i+8+n)[0]
        guard((zlib.crc32(tag+payload)&0xffffffff)==crc,"PNG CRC")
        if tag==b"IHDR":w,h=struct.unpack_from(">II",payload)
        if tag==b"IDAT":count+=1
        i=j
        if tag==b"IEND":ended=True;break
    guard(ended and count>0 and i==len(blob),"PNG incomplete")
    guard((w,h)==SIZE,"PNG resolution mismatch")
    return {"filename":path.name,"width":w,"height":h,"bytes":len(blob),
            "sha256":hashlib.sha256(blob).hexdigest(),"png_crc_valid":True}
guard(ROOT.as_posix().lower()=="c:/mh4/castallsandbox","only MH4 sandbox")
guard(not OUT.exists(),"refuse overwrite")
guard(ASSET.exists() and MAP.exists(),"review source missing")
guard(digest(ASSET)==ASSET_SHA and digest(MAP)==MAP_SHA,"review hashes changed")
guard(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine version")
guard(hasattr(unreal,"register_slate_post_tick_callback"),"ticker missing")
guard(not getattr(builtins,"_v5_screenshot_active",False),"already running")
character=unreal.load_asset(OBJ)
guard(isinstance(character,unreal.MetaHumanCharacter),"asset class")
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
guard(level.load_level(LEVEL) is not False,"review level loading")
editor=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
editor.open_editor_for_assets(assets=[character])
sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
actor=sub.spawn_meta_human_actor(character=character)
guard(actor is not None,"preview actor not created")
cs=actor.get_components_by_class(unreal.ActorComponent)
skeletal=[c.get_name() for c in cs if isinstance(c,unreal.SkeletalMeshComponent)]
guard("Face" in skeletal and "Body" in skeletal,"not a face/body preview")
origin=actor.get_actor_location()
head=unreal.Vector(origin.x,origin.y,origin.z+153.0)
system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cam=system.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(origin.x+0,origin.y+120,origin.z+169))
guard(cam is not None,"camera unavailable")
cam.set_actor_label("Temporary_Ender_V5_3D_Face_Camera")
position=cam.get_actor_location()
cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(position,head),False)
cam.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view",36.0)
for n,(dx,dy,dz,power) in enumerate(((110,130,205,145.0),(-130,115,184,70.0),(0,-180,190,95.0))):
    light=system.spawn_actor_from_class(unreal.PointLight,unreal.Vector(origin.x+dx,origin.y+dy,origin.z+dz))
    guard(light is not None,"light unavailable")
    light.set_actor_label("Temporary_Ender_V5_StudioFill_"+str(n))
    comp=light.get_component_by_class(unreal.PointLightComponent)
    comp.set_editor_property("intensity",power)
    comp.set_editor_property("attenuation_radius",1200.0)
OUT.mkdir(parents=True)
receipt=OUT/"capture_receipt.json"
record={"status":"IN_PROGRESS","kind":"V5_TRANSIENT_FACE_CLOSEUP_REVIEW",
        "engine":unreal.SystemLibrary.get_engine_version(),"source_asset_sha256":ASSET_SHA,
        "source_map_sha256":MAP_SHA,"actor_class":actor.get_class().get_name(),
        "skeletal_components":skeletal,
        "asset_saved":False,"level_saved":False,"rig_for_gameplay_verified":False,
        "camera_contract":"FRONTAL_PLUS_Y_MODEL_AXIS_PROVISIONAL","visual_likeness_approved":False,"production_canon_promoted":False,"captures":[]}
def write():receipt.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf-8")
write()
class Capture:
    def __init__(self):
        self.actor=actor;self.character=character;self.camera=cam
        self.started=time.monotonic();self.frame=0;self.task=None
        self.busy=False;self.wait_frame=None;self.handle=None
    def close(self,status,error=None):
        record["status"]=status
        if error:record["error"]=error[-2500:]
        record["asset_sha256_after"]=digest(ASSET)
        record["map_sha256_after"]=digest(MAP)
        if record["asset_sha256_after"]!=ASSET_SHA or record["map_sha256_after"]!=MAP_SHA:
            record["status"]="FAIL_ASSET_OR_MAP_CHANGED"
        write()
        if self.handle is not None:unreal.unregister_slate_post_tick_callback(self.handle)
        builtins._v5_screenshot_active=False
        builtins._v5_screenshot_runner=None
        unreal.log("TSTSS_V5_NATIVE_SCREENSHOT_STATUS "+record["status"]+" "+str(receipt))
    def tick(self,delta):
        if self.busy:return
        try:
            self.frame+=1
            if time.monotonic()-self.started>120:
                self.close("TIMED_OUT")
                return
            if self.frame<12:return
            target=OUT/"face_truefront_plus_y.png"
            if self.task is None:
                self.busy=True
                try:self.task=unreal.AutomationLibrary.take_high_res_screenshot(
                    SIZE[0],SIZE[1],str(target),camera=self.camera,delay=0.0,force_game_view=True)
                finally:self.busy=False
                guard(self.task is not None and self.task.is_valid_task(),"screenshot task")
                unreal.log("TSTSS_V5_NATIVE_CAPTURE_REQUESTED "+str(target))
                return
            if not self.task.is_task_done():return
            try:info=png_meta(target)
            except (OSError,RuntimeError):
                if self.wait_frame is None:self.wait_frame=self.frame
                if self.frame-self.wait_frame<90:return
                raise
            record["captures"].append(info)
            self.close("NATIVE_PNG_CAPTURED_VISUAL_UNREVIEWED")
        except Exception:
            e=traceback.format_exc()
            unreal.log_error("TSTSS_V5_NATIVE_CAPTURE_FAILED "+e)
            self.close("FAILED",e)
runner=Capture()
builtins._v5_screenshot_active=True
builtins._v5_screenshot_runner=runner
try:runner.handle=unreal.register_slate_post_tick_callback(runner.tick)
except Exception:
    runner.close("FAILED_TO_REGISTER_TICK",traceback.format_exc())
    raise
unreal.log("TSTSS_V5_NATIVE_CAPTURE_ARMED "+str(receipt))
