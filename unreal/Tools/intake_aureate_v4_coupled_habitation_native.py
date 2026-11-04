"""One isolated Unreal 5.8.4 NullRHI intake: bridge and quarters GLBs.

Creates new review assets only; never a production actor, map or player gate.
The generated source geometry has centimeter scale and independent provenance.
"""
from pathlib import Path
import json,hashlib,traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
SOURCE=ROOT/"CoupledHabitationLookdev_20261104"
DEST="/Game/TSTSS/Review/ShipArt/CoupledHabitation_20261104"
MANIFEST=SOURCE/"CoupledHabitationLookdevManifest.json"
RECEIPT=ROOT/"coupled_habitation_native_import_20261104.json"
FILES=("AureateWake_CoupledBridge_Geodesic_REVIEW.glb",
       "AureateWake_CurvedLivingQuarters_REVIEW.glb")
EXPECTED={
 FILES[0]:"a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506",
 FILES[1]:"69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0"}
report={"state":"NOT_STARTED","authority":"NONCANONICAL_REVIEW_ONLY",
        "existing_maps_changed":False,"production_content_modified":False,
        "starbourne_player_unlocked":False,"creator_art_approved":False}
if RECEIPT.exists():raise FileExistsError("Habitation intake previously attempted")
def req(ok,message):
    if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    req(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"Wrong active Unreal project")
    meta=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text())
    req(meta.get("EngineAssociation")=="5.8" and
        "AUREATE_CINEMATIC_V4_REVIEW_ONLY" in meta.get("Description",""),"Not disposable V4 sandbox")
    report["engine"]=unreal.SystemLibrary.get_engine_version()
    req(report["engine"].startswith("5.8."),"Wrong Unreal engine")
    manifest=json.loads(MANIFEST.read_text())
    req(manifest.get("authority")=="AUREATE_V4_NONCANONICAL_COUPLED_HABITATION_20261104",
        "Wrong geometry authority")
    req(manifest.get("content_sha256")==EXPECTED and
        manifest.get("starbourne_player_unlocked") is False and
        manifest.get("creator_art_approved") is False,"Manifest provenance mismatch")
    for name in FILES:
        path=SOURCE/name
        req(path.is_file() and sha(path)==EXPECTED[name],
            "Asset source checksum drift: "+name)
        req(path.stat().st_size<25000000,"Unexpected giant review GLB")
    lib=unreal.EditorAssetLibrary
    req(not lib.does_directory_exist(DEST) or not
        lib.list_assets(DEST,recursive=True,include_folder=False),
        "Native destination occupied: refuse overwrite")
    imported={}
    for name in FILES:
        job=unreal.AssetImportTask()
        job.set_editor_property("filename",str((SOURCE/name).resolve()))
        job.set_editor_property("destination_path",DEST)
        job.set_editor_property("automated",True)
        job.set_editor_property("replace_existing",False)
        job.set_editor_property("save",True)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([job])
        paths=list(job.get_editor_property("imported_object_paths"))
        meshes=[unreal.load_asset(p) for p in paths]
        meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)]
        req(len(meshes)==1,"Expected one native StaticMesh per source: "+name)
        mesh=meshes[0]
        slots=mesh.get_editor_property("static_materials")
        req(len(slots)==3,"Review mesh material section mismatch: "+name)
        bounds=mesh.get_bounds()
        imported[name]={"native_path":mesh.get_path_name(),
                        "material_slots":len(slots),
                        "imported_asset_paths":paths,
                        "source_sha256":EXPECTED[name],
                        "native_bounds_box_extent_cm":[float(bounds.box_extent.x),
                                                        float(bounds.box_extent.y),
                                                        float(bounds.box_extent.z)]}
    report.update({"state":"TWO_NATIVE_NONCANONICAL_HABITATION_MESHES_IMPORT_PASS",
                   "imported":imported,
                   "original_maps_opened":False,
                   "shared_pivot_in_map":"NOT_YET_TESTED",
                   "native_gpu_screenshot":"NOT_YET_TESTED",
                   "pressure_seal":"NOT_VERIFIED","physical_clearance":"NOT_VERIFIED"})
except Exception as exc:
    report["state"]="HABITATION_NATIVE_INTAKE_HOLD"
    report["error"]=str(exc)
    report["traceback"]=traceback.format_exc()[-4000:]
finally:
    RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    unreal.log("COUPLED_HABITATION_V4_NATIVE_INTAKE "+json.dumps(report,sort_keys=True))
if report["state"]!="TWO_NATIVE_NONCANONICAL_HABITATION_MESHES_IMPORT_PASS":
    raise RuntimeError(report.get("error","Bridge/quarters intake not verified"))
