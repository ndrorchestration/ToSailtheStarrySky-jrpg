"""Native GPU capture of detachable goggles alone in dedicated UE5.8.4 sandbox."""
import builtins,hashlib,json,struct,time,traceback,zlib
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
EXPECTED=Path(r"C:\Users\Admin\work\TSTSS-Cast643-UEImport-Sandbox-20261101")
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\Ender_goggles_noncanonical.glb")
SOURCE_SHA="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
MESH_PATH="/Game/ArtLookdev/Characters/Ender/Accessories/GogglesCandidateV1/Ender_goggles_noncanonical/StaticMeshes/Ender_goggles_noncanonical.Ender_goggles_noncanonical"
OUT=ROOT/"Saved/CharacterLookdev/GogglesCandidateV1/native_visual_review01"
SIZE=(800,450)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(ok,msg):
    if not ok:raise RuntimeError("FAIL_CLOSED "+msg)
def validate_png(path):
    raw=path.read_bytes()
    guard(raw[:8]==b"\x89PNG\r\n\x1a\n","PNG header")
    off=8;count=0;done=False;wh=(None,None)
    while off+12<=len(raw):
        n=struct.unpack_from(">I",raw,off)[0];kind=raw[off+4:off+8];end=off+12+n
        guard(end<=len(raw),"chunk bounds")
        payload=raw[off+8:off+8+n]
        guard(zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from(">I",raw,off+8+n)[0],"CRC")
        if kind==b"IHDR":wh=struct.unpack_from(">II",payload)
        if kind==b"IDAT":count+=1
        off=end
        if kind==b"IEND":done=True;break
    guard(done and off==len(raw) and count>0 and wh==SIZE,"bad/incomplete PNG")
    return {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"width":wh[0],"height":wh[1],"png_crc_valid":True}
guard(ROOT.as_posix().lower()==EXPECTED.as_posix().lower(),"project")
guard((ROOT/"Cast643Review.uproject").is_file(),"uproject")
guard(not OUT.exists(),"evidence folder reuse")
guard(digest(GLB)==SOURCE_SHA,"goggles source mutated")
guard(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine")
mesh=unreal.load_asset(MESH_PATH)
guard(isinstance(mesh,unreal.StaticMesh),"mesh missing")
sys=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=sys.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,50))
guard(actor is not None,"actor missing")
actor.set_actor_label("TEMP_Ender_3D_Goggles_ReviewOnly")
comp=actor.get_component_by_class(unreal.StaticMeshComponent)
guard(comp is not None,"StaticMesh component missing")
comp.set_static_mesh(mesh)
actor.set_actor_rotation(unreal.Rotator(0,0,90),False)
bounds, extents=actor.get_actor_bounds(False)
cam_location=unreal.Vector(bounds.x+26,bounds.y+44,bounds.z+13)
camera=sys.spawn_actor_from_class(unreal.CameraActor,cam_location)
guard(camera is not None,"camera missing")
camera.set_actor_label("TEMP_Goggles_3D_StudioCamera")
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam_location,bounds),False)
camera.get_component_by_class(unreal.CameraComponent).set_editor_property("field_of_view",46.)
for i,(dx,dy,dz,power) in enumerate(((0,18,40,750),(-20,-5,50,450),(22,-17,20,300))):
    lamp=sys.spawn_actor_from_class(unreal.PointLight,unreal.Vector(bounds.x+dx,bounds.y+dy,bounds.z+dz))
    lamp.set_actor_label("TEMP_Goggles_StudioLight_"+str(i))
    c=lamp.get_component_by_class(unreal.PointLightComponent)
    c.set_editor_property("intensity",power)
    c.set_editor_property("attenuation_radius",500.)
OUT.mkdir(parents=True,exist_ok=False)
RECEIPT=OUT/"capture_receipt.json"
record={"status":"IN_PROGRESS","engine":unreal.SystemLibrary.get_engine_version(),
    "kind":"DETACHED_GOGGLES_STATICMESH_NOT_METAHUMAN_FITTED",
    "original_glb_sha256":SOURCE_SHA,"mesh_asset":MESH_PATH,
    "mesh_actor_roll_deg":90,"model_space_orientation_needs_visual_check":True,
    "source_asset_not_modified":True,"level_not_saved":True,
    "creator_approved":False,"rigged":False,"canon":False,"capture":[]}
def save():RECEIPT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n",encoding="utf8")
save()
class Runner:
    def __init__(self):
        self.start=time.monotonic();self.frames=0;self.task=None;self.busy=False;self.handle=None;self.wait_frame=None
        self.actor=actor;self.camera=camera
    def close(self,status,reason=None):
        record["status"]=status
        if reason:record["error"]=str(reason)[-1800:]
        record["glb_sha256_after"]=digest(GLB)
        if record["glb_sha256_after"]!=SOURCE_SHA:record["status"]="SOURCE_HASH_DRIFT"
        save()
        if self.handle is not None:unreal.unregister_slate_post_tick_callback(self.handle)
        builtins._tstss_goggles_review_runner=None
        unreal.log("TSTSS_GOGGLES_NATIVE_VISUAL "+record["status"]+" "+str(RECEIPT))
    def tick(self,delta):
        if self.busy:return
        try:
            self.frames+=1
            if time.monotonic()-self.start>85:self.close("TIMED_OUT");return
            if self.frames<15:return
            path=OUT/"goggles_standalone_threequarter.png"
            if self.task is None:
                self.busy=True
                try:self.task=unreal.AutomationLibrary.take_high_res_screenshot(SIZE[0],SIZE[1],str(path),camera=self.camera,delay=0.,force_game_view=True)
                finally:self.busy=False
                guard(self.task is not None and self.task.is_valid_task(),"capture task")
                unreal.log("TSTSS_GOGGLES_SCREENSHOT_REQUESTED "+str(path))
                return
            if not self.task.is_task_done():return
            try:info=validate_png(path)
            except (FileNotFoundError,ValueError,RuntimeError):
                if self.wait_frame is None:self.wait_frame=self.frames
                if self.frames-self.wait_frame<120:return
                raise
            record["capture"].append(info)
            self.close("NATIVE_GOGGLES_PNG_CAPTURED_VISUAL_UNREVIEWED")
        except Exception:
            e=traceback.format_exc();unreal.log_error("TSTSS_GOGGLES_VISUAL_ERROR "+e);self.close("FAILED",e)
runner=Runner()
builtins._tstss_goggles_review_runner=runner
try:runner.handle=unreal.register_slate_post_tick_callback(runner.tick)
except Exception:
    runner.close("FAILED_TO_REGISTER",traceback.format_exc());raise
unreal.log("TSTSS_GOGGLES_VISUAL_ARMED "+str(RECEIPT))
