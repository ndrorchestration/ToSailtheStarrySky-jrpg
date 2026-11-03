"""Ender V5: attempt *transient* MetaHuman preview actor, never save art or level.

Only MH4 is allowed. A preview actor is not an assembled skeletal game character.
"""
import hashlib, json, traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
EXPECTED_ROOT="c:/mh4/castallsandbox"
ASSET=ROOT/"Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
MAP=ROOT/"Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
SHA_ASSET="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
OBJECT="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
OUT=ROOT/"Saved/CharacterLookdev/V5PreviewFeasibility/preview_actor_probe02.json"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

if ROOT.as_posix().lower()!=EXPECTED_ROOT or OUT.exists():
    raise RuntimeError("FAIL_CLOSED wrong/disallowed sandbox or existing receipt")
if sha(ASSET)!=SHA_ASSET or sha(MAP)!=SHA_MAP:
    raise RuntimeError("FAIL_CLOSED source assets changed")
if not unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"):
    raise RuntimeError("FAIL_CLOSED wrong engine")
OUT.parent.mkdir(parents=True,exist_ok=True)
report={"status":"PREVIEW_NOT_ATTEMPTED","engine":unreal.SystemLibrary.get_engine_version(),
  "source_uasset_sha256":SHA_ASSET,"source_map_sha256":SHA_MAP,
  "spawned_actor":False,"skeletal_meshes":[],"static_meshes":[],
  "native_gpu_rendered":False,"cloud_rigged":False,"face_authority_approved":False,
  "no_asset_save":True,"no_level_save":True,"original_project_untouched":True}
def save():OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
save()
character=unreal.load_asset(OBJECT)
if not isinstance(character,unreal.MetaHumanCharacter):
    raise RuntimeError("FAIL_CLOSED wrong asset class")
sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
if sub is None:raise RuntimeError("FAIL_CLOSED MetaHuman editor missing")
registered=False
actor=None
try:
    # Based on Epic example_spawn_metahuman_actor.py. Asset editor owns the
    # transient actor; no scene or character asset is saved by this script.
    editor=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    editor.open_editor_for_assets(assets=[character])
    report["asset_editor_open_requested"]=True
    registered=sub.is_object_added_for_editing(character)
    report["editing_registered"]=bool(registered)
    actor=sub.spawn_meta_human_actor(character=character)
    if actor is None:
        report["status"]="PREVIEW_SPAWN_NO_ACTOR"
    else:
        report["spawned_actor"]=True
        report["actor_class"]=actor.get_class().get_name()
        report["actor_name"]=actor.get_name()
        all_components=actor.get_components_by_class(unreal.ActorComponent)
        report["component_class_names"]=[c.get_class().get_name() for c in all_components]
        skel=[c for c in all_components if isinstance(c, unreal.SkeletalMeshComponent)]
        static=[c for c in all_components if isinstance(c, unreal.StaticMeshComponent)]
        report["skeletal_meshes"]=[c.get_name() for c in skel]
        report["static_meshes"]=[c.get_name() for c in static]
        report["status"]="TRANSIENT_PREVIEW_ACTOR_CREATED_NOT_RENDERED"
except Exception:
    report["status"]="PREVIEW_SPAWN_FAILED"
    report["error"]=traceback.format_exc()[-2900:]
    unreal.log_error("TSTSS_V5_PREVIEW_SPAWN_FAILED "+report["error"])
finally:
    # Subsystem/editor handles transient teardown; do not save level.
    report["asset_after_sha256"]=sha(ASSET)
    report["map_after_sha256"]=sha(MAP)
    if report["asset_after_sha256"]!=SHA_ASSET or report["map_after_sha256"]!=SHA_MAP:
        report["status"]="FAIL_SOURCE_MUTATED"
    save()
print("TSTSS_V5_PREVIEW_STATUS",report["status"],str(OUT))
