"""UE Editor only: build/import/save a NEW isolated editable Seabourne rig.

Run with TSTSS_SHIP_EXPECTED_HEAD set to the clean source commit. No game map,
SaveGame, C++ ship authority or Starbourne setting is changed. Individual
SailAzimuth actors may be rotated in Details. Pitch belongs to their children.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
repo=project.parent
sys.path.insert(0,str(project/'ArtSource/ShipReview'))
from build_aureate_shared_hull_rig import build, FILES, STATIONS, ROOT_Z, DECK_Z, PITCH

DEST='/Game/TSTSS/Review/SharedHullRigV2'
MAP=DEST+'/L_AureateWake_Seabourne_EditableReview'
out=project/'Saved/SharedHullRigV2'
generated=out/'Generated'


def hold(message): raise RuntimeError('SHARED_HULL_RIG_HOLD '+message)


def git(*args):
    return subprocess.run(['git','-C',str(repo),*args],capture_output=True,
                          text=True,check=True).stdout.strip()


head=git('rev-parse','HEAD')
if not os.environ.get('TSTSS_SHIP_EXPECTED_HEAD') or head!=os.environ['TSTSS_SHIP_EXPECTED_HEAD']:
    hold('exact source head required')
if git('status','--porcelain'): hold('tracked/untracked source changes before authoring')
if out.exists() or unreal.EditorAssetLibrary.does_directory_exist(DEST):
    hold('review outputs already exist; refuse overwrite')
generated.mkdir(parents=True)
parts,manifest=build()
for name,data in parts.items(): (generated/name).write_bytes(data)
assets={}
for key,name in FILES.items():
    dest=DEST+'/Meshes/'+key
    task=unreal.AssetImportTask()
    for prop,value in {'filename':str(generated/name),'destination_path':dest,
                       'automated':True,'replace_existing':False,'save':True}.items():
        task.set_editor_property(prop,value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes=[]
    for p in unreal.EditorAssetLibrary.list_assets(dest,recursive=True,include_folder=False):
        obj=unreal.load_asset(p)
        if isinstance(obj,unreal.StaticMesh): meshes.append(obj)
    if len(meshes)!=1: hold('expected one static mesh: '+key)
    assets[key]=meshes[0]
    bounds=meshes[0].get_bounds()
    dims=[float(v)*2 for v in (bounds.box_extent.x,bounds.box_extent.y,bounds.box_extent.z)]
    # Catch stale 100x exports and incorrect up/forward import orientation.
    bands={'hull':((790,810),(140,230),(60,100)),
           'bridge':((180,210),(100,130),(115,140)),
           'wing':((290,310),(90,115),(10,25)),
           'mast':((23,25),(23,25),(81,83)),
           'foil':((70,74),(160,165),(110,120))}
    if not all(lo<=v<=hi for v,(lo,hi) in zip(dims,bands[key])):
        hold('native axis/centimetre bounds mismatch '+key+' '+str(dims))
    unreal.log('SHARED_HULL_IMPORT_BOUNDS '+key+' '+json.dumps(dims))

world=unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not world or not sub: hold('no isolated Editor world')


def spawn(key,label,pos=(0,0,0),rot=(0,0,0),parent=None):
    actor=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),
                 unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
    if not actor: hold('failed spawn '+label)
    actor.set_actor_label(label)
    component=actor.get_component_by_class(unreal.StaticMeshComponent)
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    component.set_static_mesh(assets[key])
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if parent:
        rule=unreal.AttachmentRule.KEEP_WORLD
        actor.attach_to_actor(parent,'',rule,rule,rule,False)
    actor.set_folder_path('AureateWake_SharedHull_REVIEW')
    return actor


root=spawn('hull','AureateWake_SHARED_HULL_REVIEW')
bridge=spawn('bridge','ForwardBridge_FIXED',(240,0,95),parent=root)
masts=[];wings=[];foils=[]
for i,x in enumerate(STATIONS,1):
    mast=spawn('mast','SailAzimuth_'+str(i),(x,0,ROOT_Z),parent=root)
    wing=spawn('wing','DragonflyWing_'+str(i),(x,0,ROOT_Z),(PITCH,0,0),parent=mast)
    masts.append(mast);wings.append(wing)
for side,yaw in ((1,0),(-1,180)):
    foils.append(spawn('foil','Hydrofoil_'+('Starboard' if side==1 else 'Port'),
                        (0,side*72,5),(0,yaw,0),root))


def vec(v): return [round(float(x),5) for x in (v.x,v.y,v.z)]


def snapshot():
    return {a.get_actor_label():{'location_cm':vec(a.get_actor_location()),
             'rotation_pyr':[round(float(x),5) for x in (a.get_actor_rotation().pitch,
                             a.get_actor_rotation().yaw,a.get_actor_rotation().roll)]}
            for a in [root,bridge]+masts+wings+foils}


before=snapshot()
for wing in wings:
    axis=wing.get_actor_forward_vector()
    if axis.z < .98 or not (-.15 < axis.x < -.12):
        hold('wing is not upright and aft-raked '+str(vec(axis)))
for foil_actor in foils:
    if foil_actor.get_actor_up_vector().z < .999:
        hold('foil assembly is inverted')
trim_tests=[]
for index,mast in enumerate(masts):
    # Native attachment propagation, each direction, each persistent wing.
    for angle in (-35.,35.):
        mast.set_actor_rotation(unreal.Rotator(pitch=0,yaw=angle,roll=0),False)
        rotation=mast.get_actor_rotation()
        if abs(rotation.yaw-angle)>.001 or abs(rotation.pitch)>.001 or abs(rotation.roll)>.001:
            hold('trim must change azimuth yaw only')
        now=snapshot()
        changed=[name for name in before if before[name]!=now[name]]
        expected={mast.get_actor_label(),wings[index].get_actor_label()}
        if set(changed)!=expected: hold('independent trim changed wrong actors '+str(changed))
        if vec(wings[index].get_actor_location())!=vec(mast.get_actor_location()):
            hold('wing pivot lost attachment')
        trim_tests.append({'sail':index+1,'yaw':angle,'changed':changed})
    mast.set_actor_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0),False)
if snapshot()!=before: hold('neutral rig failed exact restoration')

# Fixed geometry/contact datums; these are not a swept physical clearance test.
for mast in masts:
    if abs(mast.get_actor_location().z-82.-DECK_Z)>.001: hold('mast foot datum')
if len(wings)!=4 or len(foils)!=2: hold('persistent wing/foil identity count')

# Reproducible native light rig; no ocean image concealing attachment fit.
sun=sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1500),unreal.Rotator(pitch=-40,yaw=-35,roll=0))
sun.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property('intensity',5.)
for name,pos,intensity in [('Key',(350,-600,900),45000.),('Rim',(-400,600,650),35000.)]:
    light=sub.spawn_actor_from_class(unreal.PointLight,unreal.Vector(*pos),unreal.Rotator())
    light.set_actor_label('ReviewLight_'+name)
    c=light.get_component_by_class(unreal.PointLightComponent)
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity',intensity)
    c.set_editor_property('attenuation_radius',5000.)
    c.set_editor_property('cast_shadows',False)
camera=sub.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(1100,-1400,720),unreal.Rotator())
camera.set_actor_label('ReviewCamera_Hero')
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(0,0,120)),False)
camera.get_component_by_class(unreal.CameraComponent).set_editor_property('field_of_view',48.)

if not unreal.EditorLoadingAndSavingUtils.save_map(world,MAP): hold('review map save failed')

# Reload the saved level and verify the editable hierarchy survived disk.
unreal.EditorLoadingAndSavingUtils.load_map(MAP)
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
by_label={a.get_actor_label():a for a in sub.get_all_level_actors()}
for i in range(1,5):
    w=by_label['DragonflyWing_'+str(i)]
    if w.get_attach_parent_actor()!=by_label['SailAzimuth_'+str(i)]: hold('saved wing pivot lost')
    if by_label['SailAzimuth_'+str(i)].get_attach_parent_actor()!=by_label['AureateWake_SHARED_HULL_REVIEW']:
        hold('saved shared hull parent lost')

world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
capture=sub.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(),unreal.Rotator())
cc=capture.get_editor_property('capture_component2d')
cc.set_editor_property('capture_every_frame',False)
cc.set_editor_property('capture_on_movement',False)
cc.set_editor_property('fov_angle',48.)
cc.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
pp=cc.get_editor_property('post_process_settings')
for key,value in {'override_auto_exposure_bias':True,'auto_exposure_bias':-4.,
                  'override_bloom_intensity':True,'bloom_intensity':0.}.items():
    pp.set_editor_property(key,value)
cc.set_editor_property('post_process_settings',pp)
views=[]
for name,pos in [('hero',(1100,-1400,720)),('side',(0,-1700,420)),('front',(1400,-360,400))]:
    camera_pos=unreal.Vector(*pos)
    capture.set_actor_location(camera_pos,False,False)
    capture.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera_pos,unreal.Vector(0,0,125)),False)
    rt=unreal.RenderingLibrary.create_render_target2d(world,1600,1000,
          unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.015,.025,.045,1))
    cc.set_editor_property('texture_target',rt)
    cc.capture_scene()
    filename='AureateWake_Seabourne_'+name+'.png'
    unreal.RenderingLibrary.export_render_target(world,rt,str(out),filename)
    image=out/filename
    if not image.exists() or image.stat().st_size<5000: hold('missing capture '+name)
    views.append({'view':name,'camera_cm':list(pos),'look_at_cm':[0,0,125],
                  'fov_degrees':48,'path':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
record={'status':'NATIVE_EDITABLE_REVIEW_RIG_SAVED_AND_RELOADED', 'source_head':head,
        'engine':unreal.SystemLibrary.get_engine_version(),'map':MAP,'views':views,
        'native_trim_tests':trim_tests,'saved_reload_hierarchy_pass':True,
        'initial_native_poses':before,'assets':{k:v.get_path_name() for k,v in assets.items()},
        'geometry_source_manifest':manifest,'creator_art_approved':False,
        'continuous_clearance_proven':False,'playable_sailing':False,
        'gameplay_modified':False,'starbourne_unlocked':False}
(out/'NativeRigReceipt.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
unreal.log('SHARED_HULL_RIG_NATIVE_COMPLETE '+str(out/'NativeRigReceipt.json'))
