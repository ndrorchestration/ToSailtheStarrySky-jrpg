"""Native Unreal 5.8.4 V2 sealed aviator goggles + V5 transient MetaHuman.
Non-saving broad-phase orientation and AABB proximity only. NOT facial fit.
"""
import hashlib,json,math,traceback
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
GLB=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
LAND=Path(r"C:\MH2\CastAllSandbox\Saved\CharacterLookdev\EnderV5LandmarkAtlas\native_landmark_index.json")
IMP=ROOT/"Saved/CharacterLookdev/GogglesFitV2/native_import01.json"
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV2/native_spatial_review01.json"
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GLB_SHA="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
LAND_SHA="9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed"
CHAR="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
LEVEL="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(x,m):
    if not x:raise RuntimeError("FAIL_CLOSED "+m)
def vec(v):return [round(float(getattr(v,n)),5) for n in "xyz"]
guard(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","not MH5 sandbox")
guard(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine drift")
guard(not OUT.exists(),"refuse overwrite")
guard(sha(META)==META_SHA and sha(MAP)==MAP_SHA and sha(GLB)==GLB_SHA and sha(LAND)==LAND_SHA,"hash drift")
imp=json.loads(IMP.read_text(encoding="utf-8"))
guard(imp["status"]=="NATIVE_V2_SEALED_GOGGLES_STATICMESH_IMPORT_PASS_FIT_PENDING","import not passed")
guard(imp["material_slots"]==11,"material slots drift")
native_mesh=imp["native_mesh"]
pts=json.loads(LAND.read_text(encoding="utf-8"))["points"]
guard(len(pts)==79 and [p["index"] for p in pts]==list(range(79)),"landmark index drift")
char=unreal.load_asset(CHAR);mesh=unreal.load_asset(native_mesh)
guard(isinstance(char,unreal.MetaHumanCharacter) and isinstance(mesh,unreal.StaticMesh),"wrong asset types")
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets(assets=[char])
preview=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem).spawn_meta_human_actor(character=char)
guard(preview is not None,"preview creation failed")
names=[c.get_name() for c in preview.get_components_by_class(unreal.ActorComponent) if isinstance(c,unreal.SkeletalMeshComponent)]
guard("Face" in names and "Body" in names,"real 3D MetaHuman face/body missing")
origin=preview.get_actor_location()
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
goggles=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
guard(goggles is not None,"goggles actor missing")
goggles.set_actor_label("TEMP_Ender_Sealed_Goggles_V2_AABBReview")
goggles.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(mesh)
goggles.set_actor_rotation(unreal.Rotator(90.0,180.0,0.0),False)
report={"status":"V2_SPATIAL_REVIEW_STARTED","native_mesh":native_mesh,
    "mesh_source_sha256":GLB_SHA,"meta_sha256":META_SHA,"map_sha256":MAP_SHA,"landmark_sha256":LAND_SHA,
    "candidate_rotation_pitch_yaw_roll":[90,180,0],
    "native_preview_class":preview.get_class().get_name(),"skeletal_preview_component_names":names,
    "source_index_points_have_approved_semantic_labels":False,
    "actual_goggle_vs_skin_triangle_collision_verified":False,
    "head_fitted":False,"strap_or_lens_materials_approved":False,
    "artist_approved":False,"skin_and_hair_approved":False,"rig_attached":False,
    "level_saved":False,"source_assets_modified":False,
    "production_game_modified":False,"canon_promoted":False,"trials":[]}
OUT.parent.mkdir(parents=True,exist_ok=True)
def save():OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
save()
try:
    for label,dx,dy,dz in [
        ("eye_height_hypothesis",0,11.4,164.5),
        ("above_brow_hypothesis",0,9.5,171.5),
        ("lower_forehead_hypothesis",0,9.5,168.5)
    ]:
        position=unreal.Vector(origin.x+dx,origin.y+dy,origin.z+dz)
        goggles.set_actor_location(position,False,False)
        center,ext=goggles.get_actor_bounds(False)
        sz=[round(2*float(getattr(ext,a)),4) for a in "xyz"]
        guard(all(abs(a-b)<.25 for a,b in zip(sz,[19.2,19.171,8.02])),"wrong native V2 orientation "+str(sz))
        cen=vec(center);exts=vec(ext)
        low=[cen[i]-exts[i] for i in range(3)]
        high=[cen[i]+exts[i] for i in range(3)]
        inside=[];near=[]
        for p in pts:
            pos=[float(p["xyz_cm"][i])+float(getattr(origin,"xyz"[i])) for i in range(3)]
            clamped=[max(low[i],min(high[i],pos[i])) for i in range(3)]
            dist=math.dist(pos,clamped)
            if dist<1.0:near.append(p["index"])
            if dist<1e-6:inside.append(p["index"])
        report["trials"].append({"label":label,"relative_position_cm":[dx,dy,dz],
            "native_outer_aabb_cm":sz,"absolute_actor_position_cm":vec(position),
            "aabb_min_cm":[round(x,3) for x in low],"aabb_max_cm":[round(x,3) for x in high],
            "indexed_face_points_inside_outer_aabb":len(inside),
            "indexed_face_points_within_1cm_of_outer_aabb":len(near),
            "indices_inside":inside,"outer_AABB_is_NOT_wearable_fit":True})
    report["status"]="NATIVE_V2_UPRIGHT_AXES_AND_THREE_AABB_TRIALS_PASS_VISUAL_FIT_PENDING"
except Exception:
    report["status"]="V2_SPATIAL_REVIEW_FAILED"
    report["error"]=traceback.format_exc()[-3500:]
finally:
    report["meta_sha256_after"]=sha(META)
    report["map_sha256_after"]=sha(MAP)
    report["goggles_source_sha256_after"]=sha(GLB)
    if report["meta_sha256_after"]!=META_SHA or report["map_sha256_after"]!=MAP_SHA or report["goggles_source_sha256_after"]!=GLB_SHA:
        report["status"]="FAIL_SOURCE_MUTATED"
    save()
print("TSTSS_V2_GOGGLES_SPATIAL",report["status"],len(report["trials"]),str(OUT))
