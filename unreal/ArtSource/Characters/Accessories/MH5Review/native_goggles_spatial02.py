"""Ender V5 + goggles: native transform feasibility only, no scene/asset saves.

This test uses actual UE MetaHuman preview and imported StaticMesh bounds.
AABB contacts are broad-phase proximity estimates, NOT mesh collisions or an
artist-accepted fit. No anatomical landmark identities are assumed.
"""
import hashlib,json,math,traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
CHAR_FILE=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP_FILE=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
SOURCE=Path(r"C:\MH2\CastAllSandbox\Saved\CharacterLookdev\EnderV5LandmarkAtlas\native_landmark_index.json")
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\Ender_goggles_noncanonical.glb")
IMP=ROOT/"Saved/CharacterLookdev/GogglesFitV1/native_import01.json"
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV1/native_spatial_review02.json"
CHAR_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GLB_SHA="76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae"
LANDMARK_SHA="9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed"
CHAR="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
MESH="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/GogglesCandidateV1/Ender_goggles_noncanonical/StaticMeshes/Ender_goggles_noncanonical.Ender_goggles_noncanonical"
LEVEL="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(cond,msg):
    if not cond:raise RuntimeError("FAIL_CLOSED "+msg)
def v(x):return [round(float(getattr(x,a)),5) for a in "xyz"]
check(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","sandbox")
check("goggles fitting experiment (MH5)" in (ROOT/"CastAllSandbox.uproject").read_text(encoding="utf-8-sig"),"sandbox descriptor")
check(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine")
check(sha(CHAR_FILE)==CHAR_SHA and sha(MAP_FILE)==MAP_SHA,"character/map source drift")
check(sha(GLB)==GLB_SHA and sha(SOURCE)==LANDMARK_SHA,"geometry evidence source drift")
check(IMP.is_file() and not OUT.exists(),"missing import receipt or occupied spatial receipt")
imp=json.loads(IMP.read_text(encoding="utf-8"))
check(imp.get("status")=="MH5_NATIVE_GOGGLES_IMPORT_PASS_POSITIONING_PENDING","native import gate")
check(imp.get("static_mesh_path")==MESH,"wrong imported asset")
points=json.loads(SOURCE.read_text(encoding="utf-8"))["points"]
check(len(points)==79 and [p["index"] for p in points]==list(range(79)),"native landmark index drift")
char=unreal.load_asset(CHAR)
mesh=unreal.load_asset(MESH)
check(isinstance(char,unreal.MetaHumanCharacter) and isinstance(mesh,unreal.StaticMesh),"asset types")
world=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world.load_level(LEVEL)
edit=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
edit.open_editor_for_assets(assets=[char])
sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
preview=sub.spawn_meta_human_actor(character=char)
check(preview is not None,"transient MetaHuman preview actor")
components=preview.get_components_by_class(unreal.ActorComponent)
face=[c for c in components if isinstance(c,unreal.SkeletalMeshComponent) and c.get_name()=="Face"]
body=[c for c in components if isinstance(c,unreal.SkeletalMeshComponent) and c.get_name()=="Body"]
check(len(face)==1 and len(body)==1,"not a genuine native face/body preview")
origin=preview.get_actor_location()
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
goggles=actor_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
check(goggles is not None,"transient goggles actor")
goggles.set_actor_label("TEMP_EnderV5_Goggles_AlignmentOnly")
sc=goggles.get_component_by_class(unreal.StaticMeshComponent)
check(sc is not None,"missing StaticMesh component")
sc.set_static_mesh(mesh)

# Unreal imported source Y-forward into native Z, and source Z-up into native Y.
# Applying native-searched Pitch+90/Yaw+180/Roll0 restores upright axes
# (mirroring temple X, which is bilateral). This is MODEL orientation only.
rotation=unreal.Rotator(90.0,180.0,0.0)
goggles.set_actor_rotation(rotation,False)

report={
 "status":"SPATIAL_REVIEW_STARTED","source_metahuman_sha256":CHAR_SHA,
 "source_map_sha256":MAP_SHA,"source_goggles_glb_sha256":GLB_SHA,
 "source_79_index_json_sha256":LANDMARK_SHA,
 "engine":unreal.SystemLibrary.get_engine_version(),
 "character":"Ender","kind":"BOUNDED_NATIVE_AABB_FIT_EXPLORATION",
 "native_preview_class":preview.get_class().get_name(),
 "native_skeletal_components":[x.get_name() for x in face+body],
 "meta_preview_origin_cm":v(origin),
 "goggles_mesh":mesh.get_path_name(),
 "candidate_rotation_pitch_yaw_roll_deg":[90.0,180.0,0.0],
 "image_pixel_to_native_indices_verified":False,
 "native_points_anatomically_named":False,
 "actual_mesh_intersection_proven":False,"fit_approved":False,
 "attachment_socket_approved":False,"native_gpu_fitting_screenshot":False,
 "character_asset_saved":False,"level_saved":False,"rigged_game_character":False,
 "production_or_canon_promoted":False,"candidates":[]}
OUT.parent.mkdir(parents=True,exist_ok=True)

def save():OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
save()
try:
    bb=mesh.get_bounding_box()
    report["mesh_local_min_cm"]=v(bb.min)
    report["mesh_local_max_cm"]=v(bb.max)
    report["face_component_class"]=face[0].get_class().get_name()
    report["face_component_bounds"]={}
    for key,component in (("face",face[0]),("body",body[0])):
        try:
            box=component.bounds
            report["face_component_bounds"][key]={"origin_cm":v(box.origin),"extent_cm":v(box.box_extent)}
        except Exception:
            report["face_component_bounds"][key]={"error":"bounds field unavailable"}
    candidate_positions=[
     ("at_eye_height_hypothesis",0.0,11.4,164.5),
     ("above_brow_hypothesis",0.0,9.5,171.5),
    ]
    for name,dx,dy,dz in candidate_positions:
        goggles.set_actor_location(unreal.Vector(origin.x+dx,origin.y+dy,origin.z+dz),False,False)
        center,extents=goggles.get_actor_bounds(False)
        c=v(center);e=v(extents)
        mn=[round(c[i]-e[i],5) for i in range(3)]
        mx=[round(c[i]+e[i],5) for i in range(3)]
        near=[]
        inside=[]
        for p in points:
            xyz=[x+o for x,o in zip(p["xyz_cm"],v(origin))]
            nearest=[min(max(xyz[i],mn[i]),mx[i]) for i in range(3)]
            dist=math.dist(xyz,nearest)
            if dist<1.0:near.append(p["index"])
            if dist<1.0e-6:inside.append(p["index"])
        report["candidates"].append({
          "label":name,"actor_location_cm":[round(origin.x+dx,5),round(origin.y+dy,5),round(origin.z+dz,5)],
          "actor_world_bounds_center_cm":c,"actor_world_bounds_extents_cm":e,
          "world_bounds_min_cm":mn,"world_bounds_max_cm":mx,
          "outer_envelope_width_cm":round(mx[0]-mn[0],5),
          "outer_envelope_forward_depth_cm":round(mx[1]-mn[1],5),
          "outer_envelope_vertical_height_cm":round(mx[2]-mn[2],5),
          "source_landmark_inside_AABB_count":len(inside),
          "source_landmark_within_1cm_of_AABB_count":len(near),
          "source_landmark_inside_AABB_indices":inside,
          "meaning":"PROVISIONAL_BROAD_PHASE_BOUNDS_NOT_FACIAL_FIT",
          "no_collisions_or_head_fit_established":True
        })
    # After rotating the imported mesh, the Y-depth (15.35 cm) and
    # Z-height (6.1 cm) should be restored; otherwise orientation fail.
    sizes=report["candidates"][0]
    check(abs(sizes["outer_envelope_width_cm"]-18.21768)<0.2,"X width")
    check(abs(sizes["outer_envelope_forward_depth_cm"]-15.35)<0.2,"Y depth")
    check(abs(sizes["outer_envelope_vertical_height_cm"]-6.1)<0.2,"Z vertical")
    report["status"]="MH5_NATIVE_GOGGLES_AXES_RESTORED_TWO_BOUNDS_HYPOTHESES_RECORDED"
except Exception:
    report["status"]="SPATIAL_REVIEW_FAILED"
    report["error"]=traceback.format_exc()[-3500:]
    unreal.log_error("TSTSS_MH5_GOGGLES_SPATIAL_FAIL "+report["error"])
finally:
    report["meta_sha256_after"]=sha(CHAR_FILE)
    report["map_sha256_after"]=sha(MAP_FILE)
    if report["meta_sha256_after"]!=CHAR_SHA or report["map_sha256_after"]!=MAP_SHA:
        report["status"]="FAIL_CHARACTER_OR_MAP_MUTATED"
    save()
print("TSTSS_MH5_GOGGLES_SPATIAL",report["status"],str(OUT))
