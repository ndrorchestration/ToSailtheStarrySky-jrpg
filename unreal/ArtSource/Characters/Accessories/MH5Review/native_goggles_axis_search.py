"""Enumerate Unreal-native goggle StaticMesh axis transforms; no character edits.

Record only properly dimensioned orientation candidates and transformed local
basis vectors. This is geometry/coordinate evidence, not face-fitting proof.
"""
import hashlib,json,math,traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
META=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
META_SHA="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
MESH="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/GogglesCandidateV1/Ender_goggles_noncanonical/StaticMeshes/Ender_goggles_noncanonical.Ender_goggles_noncanonical"
OUT=ROOT/"Saved/CharacterLookdev/GogglesFitV1/native_axis_search01.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(b,msg):
    if not b:raise RuntimeError("FAIL_CLOSED "+msg)
def vec(v):return [round(float(getattr(v,n)),5) for n in "xyz"]
require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox","MH5 only")
require(sha(META)==META_SHA and sha(MAP)==MAP_SHA,"source drift")
require(not OUT.exists(),"refuse overwrite")
require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"engine")
mesh=unreal.load_asset(MESH)
require(isinstance(mesh,unreal.StaticMesh),"imported goggles missing")
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,50))
require(actor is not None,"transient actor unavailable")
comp=actor.get_component_by_class(unreal.StaticMeshComponent)
comp.set_static_mesh(mesh)
report={"status":"AXIS_SEARCH_IN_PROGRESS","engine":unreal.SystemLibrary.get_engine_version(),
"mesh":MESH,"meta_sha256":META_SHA,"map_sha256":MAP_SHA,
"importer_mapped_dimensions_cm":[18.21768,6.1,15.35],
"desired_dimensions_cm":[18.21768,15.35,6.1],
"candidate_rotations":[],"native_screenshot_available":False,
"face_fit_proven":False,"artist_approved":False,"no_assets_saved":True}
OUT.parent.mkdir(parents=True,exist_ok=True)
def save():OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
save()
try:
    for pitch in (0,90,180,270):
      for yaw in (0,90,180,270):
       for roll in (0,90,180,270):
        actor.set_actor_rotation(unreal.Rotator(float(pitch),float(yaw),float(roll)),False)
        center,ex=actor.get_actor_bounds(False)
        dims=[round(2.0*float(getattr(ex,a)),5) for a in "xyz"]
        if not (abs(dims[0]-18.21768)<.2 and abs(dims[1]-15.35)<.2 and abs(dims[2]-6.1)<.2):
            continue
        t=actor.get_actor_transform()
        origin=t.transform_location(unreal.Vector(0,0,0))
        axes=[]
        for p in (unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1)):
            a=t.transform_location(p)
            axes.append([round(float(getattr(a,n)-getattr(origin,n)),5) for n in "xyz"])
        report["candidate_rotations"].append({
        "pitch_yaw_roll_deg":[pitch,yaw,roll],
        "world_aabb_dimensions_cm":dims,
        "local_x_mapped_to_world":axes[0],
        "local_y_mapped_to_world":axes[1],
        "local_z_mapped_to_world":axes[2],
        "art_face_fit":False})
    require(len(report["candidate_rotations"])>=1,"no orientation candidates")
    # Source model Y is forward and original GLB Z is up. UE importer
    # placed source Y into native Z and source Z into native Y.
    # Seek one orientation with local +Z -> +world Y, +Y -> +world Z,
    # local X -> -world X; the X mirror is allowed for symmetric goggles.
    ideal=[r for r in report["candidate_rotations"]
       if r["local_z_mapped_to_world"][1]>.99 and
          r["local_y_mapped_to_world"][2]>.99 and
          r["local_x_mapped_to_world"][0]<-.99]
    report["preferred_orientation_count"]=len(ideal)
    report["preferred_orientations"]=ideal
    report["status"]="NATIVE_AXIS_SEARCH_PASS_PREFERRED_AVAILABLE" if ideal else "NATIVE_AXIS_SEARCH_PASS_BUT_NO_PREFERRED"
except Exception:
    report["status"]="NATIVE_AXIS_SEARCH_FAILED"
    report["error"]=traceback.format_exc()[-2500:]
finally:
    report["meta_sha256_after"]=sha(META)
    report["map_sha256_after"]=sha(MAP)
    if report["meta_sha256_after"]!=META_SHA or report["map_sha256_after"]!=MAP_SHA:
        report["status"]="FAIL_SOURCE_MUTATED"
    save()
print("TSTSS_GOGGLES_AXIS_SEARCH",report["status"],"candidates",len(report["candidate_rotations"]),"ideal",report.get("preferred_orientation_count",0))
