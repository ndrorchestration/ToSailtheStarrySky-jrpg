"""Unreal Editor Python entry point: guarded native import of 5 V4 review GLBs.

Invoke only by the resource-gated isolated host runner, inside the named
DISPOSABLE project. Never opens a level, touches production or unlocks modes.
"""
from pathlib import Path
import hashlib, json, sys, traceback
import unreal

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from import_aureate_cinematic_v4_review import preflight, native_import, CinematicV4Hold

SOURCE=Path("C:/tmp/TSTSS_AureateCinematicV4_Output_20261103")
ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
RECEIPT=ROOT/"native_import_receipt.json"
report={"state":"STARTED_NATIVE_V4_IMPORT", "art_authority":"NONCANONICAL_REVIEW",
        "runtime_form_change":False,"gameplay_changed":False,
        "story_starbourne_unlocked":False,"map_saved":False}
if RECEIPT.exists():
    raise FileExistsError("Native V4 import receipt exists: refusing repeat")

try:
    assert Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(), "Refuse other UE project"
    assert unreal.SystemLibrary.get_engine_version().startswith("5.8."), "Expected UE 5.8"
    assert not (PROJECT/"Content"/"TSTSS"/"Review"/"ShipArt"/"CinematicV4").exists(), "Destination occupied"
    report["native_engine"]=unreal.SystemLibrary.get_engine_version()
    report["sandbox"]=str(PROJECT)
    report["project_sha256_before"]=hashlib.sha256((PROJECT/"AureateCinematicV4Sandbox.uproject").read_bytes()).hexdigest()
    source_receipt=preflight(SOURCE)
    report["source_sha256"]=source_receipt["sha256"]
    report["import"]=native_import(SOURCE,source_receipt)
    native_readback={}
    lib=unreal.EditorAssetLibrary
    for source_name,objects in report["import"]["candidate_assets"].items():
        meshes=[unreal.load_asset(object_path) for object_path in objects]
        meshes=[mesh for mesh in meshes if isinstance(mesh,unreal.StaticMesh)]
        if len(meshes)!=1: raise CinematicV4Hold("Post-import readback missing exactly one StaticMesh: "+source_name)
        mesh=meshes[0]
        slots=mesh.get_editor_property("static_materials")
        if len(slots)!=4: raise CinematicV4Hold("Incorrect four-slot StaticMesh in native Unreal: "+source_name)
        native_readback[source_name]={"object_path":mesh.get_path_name(),
                                      "material_slots":len(slots)}
    report["readback"]=native_readback
    report["project_sha256_after"]=hashlib.sha256((PROJECT/"AureateCinematicV4Sandbox.uproject").read_bytes()).hexdigest()
    assert report["project_sha256_before"]==report["project_sha256_after"], "Project file changed unexpectedly"
    report["state"]="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS"
except Exception as exc:
    report["state"]="NATIVE_IMPORT_FAILED_NOT_APPROVED"
    report["error"]=str(exc)
    report["traceback"]=traceback.format_exc()[-4000:]
finally:
    RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    unreal.log("TSTSS_AUREATE_CINEMATIC_V4 "+json.dumps(report,sort_keys=True))
if report["state"]!="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS":
    raise RuntimeError(report.get("error","V4 import did not pass"))
