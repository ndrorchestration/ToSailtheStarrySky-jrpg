"""NEW separate Skybourne Unreal review level with four 280cm authored leaf wings.

Never duplicates a World asset, never opens or changes a source map. Ship rig,
four original preview form maps, game SaveGame and Starbourne gate untouched.
Noncanonical V4 preview geometry only; no render or physics approval implied.
"""
from pathlib import Path
import hashlib,json,traceback,math
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
MAP="/Game/TSTSS/Review/Scenes/AureateV4_Skybourne_CoupledHabitation_20261104"
RECEIPT=ROOT/"native_coupled_habitation_stage_20261104.json"
WING_SOURCE_SHA="04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73"
WING_ASSET="/Game/TSTSS/Review/ShipArt/WingCinematicCandidate_20261103/AureateWake_Wing_Lookdev/StaticMeshes/AureateWake_Wing_Lookdev.AureateWake_Wing_Lookdev"
report={"state":"NOT_STARTED","authority":"NONCANONICAL_COUPLED_HABITATION_LOOKDEV_ONLY",
        "gameplay_modified":False,"original_four_maps_changed":False,
        "starbourne_player_unlocked":False,"native_gpu_rendered":False,
        "physical_wing_clearance_verified":False,"artist_approved":False}
if RECEIPT.exists():raise FileExistsError("Wing scene receipt already exists")
def must(cond,msg):
    if not cond:raise RuntimeError(msg)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
try:
    must(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"Not sandbox")
    conf=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    must("AUREATE_CINEMATIC_V4_REVIEW_ONLY" in conf.get("Description",""),
         "Project is not private review")
    report["engine"]=unreal.SystemLibrary.get_engine_version()
    must(report["engine"].startswith("5.8."),"Wrong native engine")
    importproof=json.loads((ROOT/"wing_leaf_native_import_20261103.json").read_text(encoding="utf8"))
    must(importproof["state"]=="ONE_NATIVE_280CM_LEAF_WING_THREE_MATERIAL_SLOTS_PASS" and
         importproof["source_sha256"]==WING_SOURCE_SHA and
         importproof["static_mesh"]==WING_ASSET,
         "Source leaf wing SHA and native intake not bound")
    v4=json.loads((ROOT/"native_import_receipt.json").read_text(encoding="utf8"))
    must(v4["state"]=="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS",
         "Shared detail intake not trusted")
    trimpath=[x["object_path"] for name,x in v4["readback"].items()
              if "SharedExteriorTrim" in name]
    must(len(trimpath)==1,"Missing exactly one V4 trim")
    trim=unreal.load_asset(trimpath[0])
    wing=unreal.load_asset(WING_ASSET)
    must(isinstance(trim,unreal.StaticMesh) and
         len(trim.get_editor_property("static_materials"))==4,
         "Imported shared trim missing or slots drift")
    must(isinstance(wing,unreal.StaticMesh) and
         len(wing.get_editor_property("static_materials"))==3,
         "Authored leaf wing missing or slots drift")
    # Source receipt and native geometry are independently pinned.
    habitation=json.loads((ROOT/"coupled_habitation_native_import_20261104.json").read_text())
    must(habitation["state"]=="TWO_NATIVE_NONCANONICAL_HABITATION_MESHES_IMPORT_PASS",
         "No trusted two-mesh habitation import")
    def checked_mesh(name,sha):
        item=habitation["imported"][name]
        must(item["source_sha256"]==sha and item["material_slots"]==3,
             "Habitation mesh source or slot mismatch: "+name)
        result=unreal.load_asset(item["native_path"])
        must(isinstance(result,unreal.StaticMesh)
             and len(result.get_editor_property("static_materials"))==3,
             "Missing exact native habitation mesh "+name)
        return result
    bridge_mesh=checked_mesh("AureateWake_CoupledBridge_Geodesic_REVIEW.glb",
         "a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506")
    quarters_mesh=checked_mesh("AureateWake_CurvedLivingQuarters_REVIEW.glb",
         "69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0")
    # No existing mode scene or the authored-leaf reference map may change.
    checksums={
      "AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap":
      "16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",
      "AureateCinematicV4_Seabourne_20261103_FullEditor.umap":
      "b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a",
      "AureateCinematicV4_Submersible_20261103_FullEditor.umap":
      "815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35",
      "AureateCinematicV4_Starbourne_20261103_FullEditor.umap":
      "953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00",
      "AureateV4_Skybourne_AuthoredLeaf_FRESH_20261103.umap":
      "93b0940c75bcd0269d0d20dbf55aaf2bfad3c2f903f82d4daf835797be220e95"}
    directory=PROJECT/"Content/TSTSS/Review/Scenes"
    def verify_sources():
        return all((directory/name).is_file()
                   and digest(directory/name)==expected
                   for name,expected in checksums.items())
    must(verify_sources(),"One original saved review map changed")
    lib=unreal.EditorAssetLibrary
    must(not lib.does_asset_exist(MAP),"Review destination already occupied")
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    must(bool(levels.new_level(MAP)) and bool(levels.load_level(MAP)),
         "Fresh review level creation/loading failed")
    must(not actors.get_all_level_actors(),"Unexpected actors in fresh map")
    sphere=unreal.load_asset("/Engine/BasicShapes/Sphere.Sphere")
    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    must(isinstance(sphere,unreal.StaticMesh) and isinstance(cube,unreal.StaticMesh),
         "Missing engine preview primitives")
    labels=[]
    def place(label,mesh,loc,scale=(1,1,1),angles=(0,0,0)):
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,
                    unreal.Vector(*loc),unreal.Rotator(*angles))
        must(a is not None,"Native actor failed: "+label)
        m=a.get_component_by_class(unreal.StaticMeshComponent)
        must(m is not None and m.set_static_mesh(mesh),"Mesh assignment failed: "+label)
        a.set_actor_label("V4_NONCANONICAL_"+label)
        a.set_actor_scale3d(unreal.Vector(*scale))
        a.set_actor_enable_collision(False)
        m.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        labels.append(a.get_actor_label())
        return a
    place("SHARED_PEARL_HULL_PROXY",sphere,(0,0,0),(7.9,1.15,.55))
    place("SHARED_HULL_CINEMATIC_V4_TRIM",trim,(0,0,0))
    quarters=place("CENTRAL_CURVED_QUARTERS_REVIEW",quarters_mesh,(0,0,0))
    bridge=place("FORWARD_GEODESIC_GLASS_DOME_REVIEW",bridge_mesh,(170,0,133))
    pivot=place("COUPLED_HABITATION_PIVOT_REVIEW",cube,(40,0,72),(.018,.018,.018))
    attach=unreal.AttachmentRule.KEEP_WORLD
    must(bool(quarters.attach_to_actor(pivot,"",attach,attach,attach,False))
         and bool(bridge.attach_to_actor(pivot,"",attach,attach,attach,False)),
         "Bridge and quarters cannot share one parent")
    must(quarters.get_attach_parent_actor()==pivot
         and bridge.get_attach_parent_actor()==pivot,
         "Unverified common pivot linkage")
    def coords(actor):
        pt=actor.get_actor_location()
        return (float(pt.x),float(pt.y),float(pt.z))
    def dist(a,b):
        return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
    first_bridge=coords(bridge)
    first_quarters=coords(quarters)
    first_span=dist(first_bridge,first_quarters)
    must(bool(pivot.set_actor_rotation(unreal.Rotator(0,17.5,0),False)),
         "Review pivot could not rotate")
    moved_bridge,moved_quarters=coords(bridge),coords(quarters)
    must(dist(first_bridge,moved_bridge)>0.1
         and dist(first_quarters,moved_quarters)>0.1,
         "At least one habitation child did not rotate")
    must(abs(dist(moved_bridge,moved_quarters)-first_span)<.05,
         "Coupled habitat did not rotate rigidly")
    must(bool(pivot.set_actor_rotation(unreal.Rotator(0,0,0),False)),
         "Review pivot rollback failed")
    must(dist(coords(bridge),first_bridge)<.05
         and dist(coords(quarters),first_quarters)<.05,
         "Habitation children failed zero-pose restore")
    place("FORWARD_OBSERVATION_DECK_PROXY",cube,(320,0,55),(1.65,.68,.07))
    roots=(
      ("FORE_PORT",(145,-99,55),(0,-80,-8)),
      ("FORE_STARBOARD",(145,99,55),(0,80,8)),
      ("AFT_PORT",(-180,-99,53),(0,-102,-8)),
      ("AFT_STARBOARD",(-180,99,53),(0,102,8)),
    )
    for ident,origin,angle in roots:
        place(ident+"_AUTHORED_LEAF_280CM_REVIEW",wing,origin,(1,1,1),angle)
    camviews=(
      ("THREE_QUARTER",(1050,840,560),(0,0,40)),
      ("TOP",(0,0,1250),(0,0,0)),
      ("PROFILE",(80,1175,285),(0,0,25)),
      ("BRIDGE",(515,410,300),(200,0,105)),
    )
    for role,position,target in camviews:
        rotation=unreal.MathLibrary.find_look_at_rotation(
            unreal.Vector(*position),unreal.Vector(*target))
        cam=actors.spawn_actor_from_class(unreal.CameraActor,
                       unreal.Vector(*position),rotation)
        must(cam is not None,"Camera failed "+role)
        cam.set_actor_label("V4_NONCANONICAL_CAMERA_"+role)
        cam.get_component_by_class(unreal.CameraComponent).set_editor_property(
            "field_of_view",42.0)
    key=actors.spawn_actor_from_class(unreal.DirectionalLight,
                           unreal.Vector(0,0,660),unreal.Rotator(-40,40,0))
    must(key is not None,"Key light failed")
    key.set_actor_label("V4_NONCANONICAL_DIRECTIONAL_KEYLIGHT")
    actual=actors.get_all_level_actors()
    must(len(actual)==15,"Unexpected actor total in new review level")
    must(all(label in [a.get_actor_label() for a in actual] for label in labels),
         "Lost one or more actor identities")
    must(verify_sources(),"Source review map changed before save")
    must(bool(levels.save_current_level()),"Cannot save authored wing review map")
    must(verify_sources(),"Source review map changed after save")
    target=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateV4_Skybourne_CoupledHabitation_20261104.umap"
    must(target.is_file(),"Saved authored leaf map missing")
    report.update({"state":"NATIVE_FRESH_COUPLED_HABITATION_REVIEW_STAGE_PASS",
                   "map":MAP,"map_file":str(target),"map_sha256":digest(target),
                   "native_actor_count":15,"leaf_wing_count":4,
                   "camera_count":4,"source_wing_sha256":WING_SOURCE_SHA,
                   "leaf_wing_source_span_cm":280,
                   "leaf_wing_native_material_slots":3,
                   "imported_leaf_asset":WING_ASSET,
                   "habitation_meshes":[habitation["imported"][x]["native_path"]
                        for x in ("AureateWake_CoupledBridge_Geodesic_REVIEW.glb",
                                  "AureateWake_CurvedLivingQuarters_REVIEW.glb")],
                   "shared_pivot_actor":pivot.get_actor_label(),
                   "bridge_actor":bridge.get_actor_label(),
                   "quarters_actor":quarters.get_actor_label(),
                   "coupled_test_yaw_degrees":17.5,
                   "bridge_child_moved_and_restored":True,
                   "quarters_child_moved_and_restored":True,
                   "rigid_child_distance_before_cm":first_span,
                   "rigid_child_distance_during_cm":dist(moved_bridge,moved_quarters),
                   "source_review_map_shas_unchanged":checksums,
                   "pressure_seal_verified":False,
                   "continuous_clearance_verified":False,
                   "native_gpu_render":"NOT_YET_EXECUTED",
                   "creator_art_approved":False,

                   "temporary_angles_not_canon":True})
except Exception as exc:
    report["state"]="NATIVE_FRESH_COUPLED_HABITATION_STAGE_HOLD"
    report["error"]=str(exc)
    report["traceback"]=traceback.format_exc()[-4000:]
finally:
    RECEIPT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    unreal.log("V4_COUPLED_HABITATION_NATIVE_STAGE "+json.dumps(report,sort_keys=True))
if report["state"]!="NATIVE_FRESH_COUPLED_HABITATION_REVIEW_STAGE_PASS":
    raise RuntimeError(report.get("error","Fresh wing review scene was not verified"))
