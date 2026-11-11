"""UE5.8 static import into review-only assets. Must NOT modify canonical maps or grant gear.
Run UnrealEditor-Cmd.exe "PATH_TO_UPROJECT" -unattended -nop4 -nosplash -nullrhi
    -ExecutePythonScript="PATH_TO_THIS_FILE" -log
Only a successful exact-head report proves the native import was completed.
"""
import hashlib, json, math, traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
SRC=ROOT/"ArtSource"/"PartyEquipment"
MANIFEST=SRC/"party_equipment_manifest.review.json"
REPORT=ROOT/"Saved"/"PartyEquipmentReview"/"native_import_report.json"
DEST="/Game/TSTSS/Review/PartyEquipment"
EXPECTED_ROOT=Path(r"C:\TSTSS_PartyEquipment_20261110\unreal")
report={"status":"STARTED","native_import":False,"review_only":True,
    "characters":["Ender","Ionia","Lyra"],"automatic_gear_grants":False,
    "skeleton_binding":False,"gameplay_abilities_granted":False,
    "combat_runtime_verified":False,"approved_canonical_art":False,"entries":[]}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(cond,message):
    if not cond:raise RuntimeError("FAIL_CLOSED: "+message)
def save():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")

save()
try:
    require(ROOT==EXPECTED_ROOT,"wrong isolated review project: "+str(ROOT))
    require(unreal.SystemLibrary.get_engine_version().startswith("5.8."),"wrong engine")
    require(MANIFEST.is_file(),"manifest not found")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["available_party"]==["Ender","Ionia"],"opening party drift")
    require(manifest["joins_post_splashdown"]==["Lyra"],"Lyra gate drift")
    require(manifest["excluded_party"]==["Reson","Aepex"],"excluded party drift")
    require(len(manifest["entries"])==14,"unexpected item list size")
    names=set()
    library=unreal.EditorAssetLibrary
    tasks=[]
    for row in manifest["entries"]:
        owner=row["owner"]
        require(owner in ("Ender","Ionia","Lyra","Shared"),"unknown owner")
        require(not row["creator_approved"] and not row["runtime_equippable"],"unreviewed asset marked ready")
        require(row["id"] not in names,"duplicate item")
        names.add(row["id"])
        source=SRC/row["relative_path"]
        require(source.is_file() and sha(source)==row["sha256"],"GLB source hash "+row["id"])
        dest=DEST+"/"+owner
        require(not library.does_asset_exist(dest+"/"+source.stem),"target already occupied "+row["id"])
        t=unreal.AssetImportTask()
        for key,val in (("filename",str(source)),("destination_path",dest),
                        ("automated",True),("replace_existing",False),("save",True)):
            t.set_editor_property(key,val)
        tasks.append((row,t))
    # All source and destination checks above finish before any asset writes.
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t for _,t in tasks])
    for row,t in tasks:
        objs=list(t.get_objects())
        meshes=[o for o in objs if isinstance(o,unreal.StaticMesh)]
        require(len(meshes)==1,"expected one native UE StaticMesh for "+row["id"]+
                ", got "+str([o.get_class().get_name() for o in objs]))
        mesh=meshes[0]
        materials=len(mesh.get_editor_property("static_materials"))
        require(materials>=1,"material slots absent "+row["id"])
        bounds=mesh.get_bounding_box()
        extents=[round(float(getattr(bounds.max,k)-getattr(bounds.min,k)),2) for k in "xyz"]
        require(all(math.isfinite(x) and .2<x<260 for x in extents),
                "bad real-world bounds "+row["id"]+" "+str(extents))
        if row["id"]=="Ender.ResonanceStaff":
            require(168<extents[2]<175,"reviewed centered staff import axis/scale wrong "+str(extents))
        elif row["slot"]=="armor":
            require(50<extents[2]<135,"torso/outfit preview axis/scale wrong "+str(extents))
        require(library.does_asset_exist(mesh.get_path_name()),"mesh not persisted "+row["id"])
        report["entries"].append({"id":row["id"],"owner":row["owner"],
          "stage":row["stage"],"source_sha256":row["sha256"],
          "mesh_path":mesh.get_path_name(),"material_slots":materials,
          "bounds_xyz_cm":extents,"native_static_mesh":True,
          "rigged":False,"worn_by_character":False,"combat_equippable":False})
        unreal.log("TSTSS_PARTY_EQUIPMENT_IMPORTED "+row["id"]+" "+mesh.get_path_name())
    require(len(report["entries"])==14,"incomplete import")
    report["status"]="NATIVE_STATIC_MESH_IMPORT_PASS_REVIEW_ONLY"
    report["native_import"]=True
except Exception:
    report["status"]="NATIVE_IMPORT_FAILED"
    report["error"]=traceback.format_exc()[-6000:]
    unreal.log_error(report["error"])
finally:
    try:save()
    except Exception as exc:unreal.log_error("REPORT_SAVE_FAILED "+str(exc))
unreal.log("TSTSS_PARTY_EQUIPMENT_RESULT "+report["status"]+" "+str(REPORT))
