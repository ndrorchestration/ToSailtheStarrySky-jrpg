"""Capture ONE genuine native UE5.8.4 D3D11 Skybourne candidate frame in isolated sandbox.

Temporary/noncanonical assembled map: no production scene, game route, model
approval, user Editor/PIE action or final-cinematic appearance implied.
"""
from pathlib import Path
import hashlib
import json
import struct
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
MAP="/Game/TSTSS/Review/Scenes/AureateV4_Skybourne_CoupledHabitation_20261104"
MAP_FILE=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateV4_Skybourne_CoupledHabitation_20261104.umap"
MAP_SHA="14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362"
CAMERA="V4_NONCANONICAL_CAMERA_THREE_QUARTER"
DIR=ROOT/"SkybourneV4HabitationGPU_20261104_Automation13"
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
    # All extra environment/light actors are transient to this UN-SAVED
    # private D3D11 session. This does not resolve the production #705 sky.
    artist=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ephemeral=[]
    if hasattr(unreal,"SkyAtmosphere"):
        sky=artist.spawn_actor_from_class(unreal.SkyAtmosphere,
                 unreal.Vector(0,0,0),unreal.Rotator(0,0,0))
        if sky is not None:
            sky.set_actor_label("V4_NONCANONICAL_TEMPORARY_SKYATMOSPHERE")
            ephemeral.append("SkyAtmosphere")
    if hasattr(unreal,"SkyLight"):
        skyfill=artist.spawn_actor_from_class(unreal.SkyLight,
                   unreal.Vector(0,0,650),unreal.Rotator(0,0,0))
        if skyfill is not None:
            skyfill.set_actor_label("V4_NONCANONICAL_TEMPORARY_SKYLIGHT")
            component=skyfill.get_component_by_class(unreal.SkyLightComponent)
            if component is not None:
                component.set_editor_property("intensity",2.0)
            ephemeral.append("SkyLight")
    for label,point,intensity in (
      ("FRONT_KEY",(520,350,430),9000.0),
      ("OPPOSITE_FILL",(-280,-350,310),7500.0),
      ("UPPER_RIM",(0,-100,650),14000.0),
      ("LOWER_ACCENT",(280,350,-230),6000.0),
    ):
        actor=artist.spawn_actor_from_class(unreal.PointLight,
                    unreal.Vector(*point),unreal.Rotator(0,0,0))
        if actor is None:raise RuntimeError("Review-only fill light spawn failed: "+label)
        actor.set_actor_label("V4_NONCANONICAL_TEMPORARY_"+label)
        comp=actor.get_component_by_class(unreal.PointLightComponent)
        if comp is None:raise RuntimeError("Missing PointLightComponent "+label)
        comp.set_editor_property("intensity",intensity)
        ephemeral.append(label)
    info["temporary_lighting_actors_not_saved"]=ephemeral
    info["lighting_state"]="PROVISIONAL_CINEMATIC_FILL_NOT_CREATOR_APPROVED"
    # Lock camera exposure instead of letting a black sky make all white
    # proxy surfaces blow out. All actor changes remain unsaved.
    cam_component=cam.get_component_by_class(unreal.CameraComponent)
    assert cam_component is not None
    settings=cam_component.get_editor_property("post_process_settings")
    settings.set_editor_property("override_auto_exposure_method",True)
    settings.set_editor_property("auto_exposure_method",unreal.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_bias",True)
    settings.set_editor_property("auto_exposure_bias",5.4)
    cam_component.set_editor_property("post_process_settings",settings)
    cam_component.set_editor_property("post_process_blend_weight",1.0)
    info["camera_manual_exposure_bias_review"]=5.4
    info["fill_intensities_lumens_review"]=[9000,7500,14000,6000]
    # The sun flag is required for a SkyAtmosphere actor to draw an
    # atmosphere rather than an unlit black surrounding.
    sun=[a for a in actors if "DIRECTIONAL_KEYLIGHT" in a.get_actor_label()]
    if len(sun)==1:
        comp=sun[0].get_component_by_class(unreal.DirectionalLightComponent)
        if comp is not None:
            try:
                comp.set_editor_property("atmosphere_sun_light",True)
                info["sky_atmosphere_sun_light"]=True
            except Exception as e:
                info["sky_atmosphere_sun_light"]="PROPERTY_NOT_AVAILABLE: "+str(e)
    if hasattr(unreal,"ExponentialHeightFog"):
        fog=artist.spawn_actor_from_class(unreal.ExponentialHeightFog,
                       unreal.Vector(0,0,-450),unreal.Rotator(0,0,0))
        if fog is not None:
            fog.set_actor_label("V4_NONCANONICAL_TEMPORARY_HEIGHT_FOG")
            fog_component=fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if fog_component is not None:
                fog_component.set_editor_property("fog_density",0.002)
            ephemeral.append("ExponentialHeightFog")
    # REPRODUCIBLE DEVELOPER CYCLORAMA — NOT a physically simulated sky,
    # not source art, and not the separately gated #705 environment.
    # New material ONLY inside this disposable project's review-only path.
    matfolder="/Game/TSTSS/Review/Materials"
    matname="M_V4_SolidSkydome_DEV_Automation13_Habitation"
    material_path=matfolder+"/"+matname
    lib=unreal.EditorAssetLibrary
    if lib.does_asset_exist(material_path):
        raise FileExistsError("Cyclorama already exists, refuse art overwrite")
    if not lib.does_directory_exist(matfolder):
        assert lib.make_directory(matfolder),"Cannot create isolated materials folder"
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    material=tools.create_asset(matname,matfolder,unreal.Material,
                                unreal.MaterialFactoryNew())
    assert isinstance(material,unreal.Material),"Could not create review-only material"
    material.set_editor_property("two_sided",True)
    material.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    edit=unreal.MaterialEditingLibrary
    def makecolor(color, x,y):
        node=edit.create_material_expression(material,
                 unreal.MaterialExpressionConstant3Vector,x,y)
        assert node is not None,"Could not create color constant"
        node.set_editor_property("constant",unreal.LinearColor(*color,1.0))
        return node
    solid=makecolor((4.0,8.0,16.0),-320,-100)
    assert edit.connect_material_property(solid,"",
            unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    errors=edit.recompile_material(material)
    if errors:raise RuntimeError("Review material compile errors: "+str(errors))
    if not lib.save_loaded_asset(material):
        raise RuntimeError("Could not save new review material asset")
    background=unreal.load_asset(material_path)
    assert isinstance(background,unreal.MaterialInterface)
    shape=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    assert isinstance(shape,unreal.StaticMesh)
    center=cam.get_actor_location()
    backdrop_rot=unreal.Rotator(0,0,0)
    backdrop=artist.spawn_actor_from_class(unreal.StaticMeshActor,
                                           center,backdrop_rot)
    assert backdrop is not None
    backdrop.set_actor_label("V4_NONCANONICAL_TEMPORARY_SKY_CYCLORAMA")
    backdrop.set_actor_scale3d(unreal.Vector(100,100,100))
    backdrop.set_actor_enable_collision(False)
    bgmesh=backdrop.get_component_by_class(unreal.StaticMeshComponent)
    assert bgmesh is not None and bgmesh.set_static_mesh(shape)
    bgmesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    bgmesh.set_material(0,background)
    ephemeral.append("DEV_SKYDOME")
    info["backdrop_placement"]="CAMERA_CENTERED_TWO_SIDED_SKYDOME_R5000_CM"
    info["backdrop_test"]="TEMPORARY_NONPHYSICAL_DAYLIGHT_BACKDROP_NOT_APPROVED"
    info["backdrop_kind"]="DEV_UNLIT_TWO_SIDED_SKYDOME_NONPHYSICAL"
    info["backdrop_material"]=material_path
    info["backdrop_model_saved"]=False
    info["background_not_creator_approved"]=True
    wanted={"V4_NONCANONICAL_"+slot+"_AUTHORED_LEAF_280CM_REVIEW" for slot in (
        "FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")}
    found={x.get_actor_label() for x in actors if x.get_actor_label().endswith("_AUTHORED_LEAF_280CM_REVIEW")}
    assert found==wanted, "Wrong four V4 wing lace identities"
    assert len([x for x in actors if x.get_actor_label()=="V4_NONCANONICAL_SHARED_HULL_CINEMATIC_V4_TRIM"])==1
    wingpath="/Game/TSTSS/Review/ShipArt/WingCinematicCandidate_20261103/AureateWake_Wing_Lookdev/StaticMeshes/AureateWake_Wing_Lookdev.AureateWake_Wing_Lookdev"
    leaf_actors=[x for x in actors if x.get_actor_label().endswith("_AUTHORED_LEAF_280CM_REVIEW")]
    assert len(leaf_actors)==4,"Not exactly four rooted authored wing actors"
    for leaf in leaf_actors:
        comp=leaf.get_component_by_class(unreal.StaticMeshComponent)
        assert comp is not None and comp.get_editor_property("static_mesh").get_path_name()==wingpath
    info["authored_wing_native_path"]=wingpath
    info["authored_wing_source_sha256"]="04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73"
    info["four_rooted_leaf_meshes_verified"]=True
    # Verify this is the newly saved coupled pivot map, not the old leaf-only map.
    def unique(label):
        matches=[a for a in actors if a.get_actor_label()==label]
        assert len(matches)==1,"Required habitation identity missing: "+label
        return matches[0]
    pivot=unique("V4_NONCANONICAL_COUPLED_HABITATION_PIVOT_REVIEW")
    bridge=unique("V4_NONCANONICAL_FORWARD_GEODESIC_GLASS_DOME_REVIEW")
    quarters=unique("V4_NONCANONICAL_CENTRAL_CURVED_QUARTERS_REVIEW")
    assert bridge.get_attach_parent_actor()==pivot
    assert quarters.get_attach_parent_actor()==pivot
    imported=json.loads((ROOT/"coupled_habitation_native_import_20261104.json").read_text())
    assert imported["state"]=="TWO_NATIVE_NONCANONICAL_HABITATION_MESHES_IMPORT_PASS"
    geometry=(
      (bridge,"AureateWake_CoupledBridge_Geodesic_REVIEW.glb",
       "a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506"),
      (quarters,"AureateWake_CurvedLivingQuarters_REVIEW.glb",
       "69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0"))
    for actor,asset,source_sha in geometry:
        comp=actor.get_component_by_class(unreal.StaticMeshComponent)
        assert comp is not None
        receipt=imported["imported"][asset]
        assert receipt["source_sha256"]==source_sha
        assert comp.get_editor_property("static_mesh").get_path_name()==receipt["native_path"]
    info["habitation_native_meshes_verified"]=True
    info["habitation_shared_parent_verified"]=True
    info["temporary_pivot_rotation_done_on_existing_saved_map"]=False
    info["geodesic_bridge_source_sha256"]=geometry[0][2]
    info["curved_quarters_source_sha256"]=geometry[1][2]
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
