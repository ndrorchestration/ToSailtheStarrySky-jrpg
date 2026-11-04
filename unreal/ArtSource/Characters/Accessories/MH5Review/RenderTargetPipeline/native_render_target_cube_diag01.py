"""UE 5.8 D3D11 lightweight diagnostic: SceneCapture2D -> RenderTarget -> PNG.

Runs only in pre-existing isolated content-only Cast643 review project. Creates
transient cube/light/capture actors and target. Never saves any map or asset.
No MetaHuman, textures, or online services; do not interpret as character QA.
"""
import builtins, hashlib, json, math, struct, time, traceback, zlib
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
ALLOWED=Path(r"C:\Users\Admin\work\TSTSS-Cast643-UEImport-Sandbox-20261101")
OUT=ROOT/"Saved/CharacterLookdev/RenderTargetDiagnostic01"
PNG=OUT/"scene_capture_cube.png"
RECEIPT=OUT/"capture_diagnostic.json"
SIZE=(320,180)

def require(x,m):
    if not x:raise RuntimeError("FAIL_CLOSED "+m)
def validate_png(path):
    data=path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"),"no PNG signature")
    n=8;images=0;wh=(0,0);done=False
    while n+12<=len(data):
        sz=struct.unpack_from(">I",data,n)[0]
        t=data[n+4:n+8];end=n+sz+12
        require(end<=len(data),"corrupt PNG chunk bounds")
        payload=data[n+8:n+8+sz]
        crc=struct.unpack_from(">I",data,n+8+sz)[0]
        require(zlib.crc32(t+payload)&0xffffffff==crc,"bad PNG CRC")
        if t==b"IHDR":wh=struct.unpack_from(">II",payload,0)
        if t==b"IDAT":images+=1
        n=end
        if t==b"IEND":done=True;break
    require(done and n==len(data) and images>0 and wh==SIZE,"PNG missing/invalid dimensions")
    return {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"width":wh[0],"height":wh[1],"crc_valid":True}

require(ROOT.as_posix().lower()==ALLOWED.as_posix().lower(),"not content-only Cast643 sandbox")
require((ROOT/"Cast643Review.uproject").is_file(),"wrong uproject")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine mismatch")
require(not OUT.exists(),"refuse to overwrite prior evidence")
OUT.mkdir(parents=True)
record={"status":"STARTED","source":"Unreal Engine 5.8.4 native D3D11",
        "method":"SceneCaptureComponent2D + transient TextureRenderTarget2D + RenderingLibrary.export_render_target",
        "engine":unreal.SystemLibrary.get_engine_version(),
        "image_size":[*SIZE],"kind":"LIGHTWEIGHT_CUBE_NOT_METAHUMAN",
        "source_project":str(ROOT),"map_saved":False,"assets_saved":False,
        "character_render_claim":False,"user_game_changed":False,
        "render_target_export_success":False,"file":[]}
def save():RECEIPT.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8")
save()

try:
    world=unreal.EditorLevelLibrary.get_editor_world()
    require(world is not None,"editor world unavailable")
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube_mesh=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    require(isinstance(cube_mesh,unreal.StaticMesh),"engine cube absent")
    cube=es.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,100))
    require(cube is not None,"cube actor")
    cube.set_actor_label("TEMP_RenderTargetProof_Cube")
    cube.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cube_mesh)
    cube.set_actor_rotation(unreal.Rotator(18,24,4),False)
    light=es.spawn_actor_from_class(unreal.PointLight,unreal.Vector(70,20,250))
    require(light is not None,"light actor")
    lc=light.get_component_by_class(unreal.PointLightComponent)
    lc.set_editor_property("intensity",3400.)
    lc.set_editor_property("attenuation_radius",950.)
    cap_actor=es.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(225,0,145))
    require(cap_actor is not None,"SceneCapture2D actor")
    cap_actor.set_actor_label("TEMP_RenderTargetProof_Capture")
    cap_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(
        cap_actor.get_actor_location(),unreal.Vector(0,0,102)),False)
    component=cap_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    require(component is not None,"SceneCapture2D component unavailable")
    component.set_editor_property("capture_every_frame",False)
    component.set_editor_property("capture_on_movement",False)
    component.set_editor_property("fov_angle",52.)
    component.set_editor_property("capture_source",unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    target=unreal.RenderingLibrary.create_render_target2d(
        world_context_object=world,width=SIZE[0],height=SIZE[1],
        format=unreal.TextureRenderTargetFormat.RTF_RGBA8,
        clear_color=unreal.LinearColor(0.015,0.02,0.04,1.0),
        auto_generate_mip_maps=False)
    require(target is not None,"transient render target create failure")
    component.set_editor_property("texture_target",target)
    component.capture_scene()
    record["native_capture_scene_called"]=True
    save()
except Exception:
    record["status"]="SETUP_FAILED"
    record["error"]=traceback.format_exc()[-3500:]
    save()
    raise

class Runner:
    def __init__(self):
        self.t0=time.monotonic();self.count=0;self.handle=None
        self.world=world;self.capture=component;self.target=target
    def finish(self,status,error=None):
        record["status"]=status
        if error:record["error"]=str(error)[-2900:]
        save()
        if self.handle is not None:unreal.unregister_slate_post_tick_callback(self.handle)
        builtins._tstss_rt_diagnostic_runner=None
        unreal.log("TSTSS_RT_DIAGNOSTIC_FINAL "+status+" "+str(RECEIPT))
    def tick(self,dt):
        try:
            self.count+=1
            if time.monotonic()-self.t0>42:
                self.finish("TIMED_OUT_NO_RENDER_TARGET_PNG")
                return
            if self.count==5:
                self.capture.capture_scene()
            if self.count==12:
                unreal.RenderingLibrary.export_render_target(
                    self.world,self.target,str(OUT),PNG.name)
                record["native_export_called"]=True
                save()
                unreal.log("TSTSS_RT_EXPORT_CALLED "+str(PNG))
            if self.count>=14 and PNG.exists():
                try:details=validate_png(PNG)
                except Exception:
                    if self.count<45:return
                    raise
                record["file"]=[details]
                record["render_target_export_success"]=True
                self.finish("NATIVE_RENDER_TARGET_PNG_PASS_LIGHTWEIGHT_CUBE_UNINSPECTED")
        except Exception:
            self.finish("DIAGNOSTIC_FAILED",traceback.format_exc())
            unreal.log_error("TSTSS_RT_DIAGNOSTIC_EXCEPTION "+traceback.format_exc())
runner=Runner()
builtins._tstss_rt_diagnostic_runner=runner
try:runner.handle=unreal.register_slate_post_tick_callback(runner.tick)
except Exception:
    runner.finish("TICK_REGISTRATION_FAILED",traceback.format_exc())
    raise
unreal.log("TSTSS_RT_DIAGNOSTIC_ARMED "+str(RECEIPT))
