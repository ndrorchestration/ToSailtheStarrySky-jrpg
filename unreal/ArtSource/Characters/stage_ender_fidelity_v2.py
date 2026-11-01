"""One-character disposable native UE 5.8 preview map; immutable cast source remains."""
import json
from pathlib import Path
import unreal
PROJECT=Path(unreal.Paths.project_dir()).resolve()
if "CastAllSandbox" not in PROJECT.name:raise RuntimeError("Disposable only")
intake=PROJECT/"Saved"/"CharacterLookdev"/"ender_fidelity_v2_native_intake.json"
receipt=json.loads(intake.read_text(encoding="utf-8"))
if receipt["status"]!="NATIVE_IMPORT_PASS_ART_UNAPPROVED":raise RuntimeError("No native import")
mesh=unreal.load_asset(receipt["asset"])
if not isinstance(mesh,unreal.StaticMesh):raise RuntimeError("Wrong asset type")
level="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
if unreal.EditorAssetLibrary.does_asset_exist(level):raise RuntimeError("Refuse to overwrite map")
if not unreal.EditorLevelLibrary.new_level(level):raise RuntimeError("Level creation failed")
actor=unreal.EditorLevelLibrary.spawn_actor_from_object(mesh,unreal.Vector(0,0,0),unreal.Rotator(pitch=0.0,yaw=0.0,roll=0.0))
if actor is None:raise RuntimeError("No actor")
actor.set_actor_label("NONCANON_ENDER_FIDELITY_V2")
if not unreal.EditorLevelLibrary.save_current_level():raise RuntimeError("Map save failed")
out=PROJECT/"Saved"/"CharacterLookdev"/"ender_fidelity_v2_map.json"
if out.exists():raise RuntimeError("Receipt exists")
out.write_text(json.dumps({"status":"STAGED_NONCANON_REVIEW_MAP",
 "engine":unreal.SystemLibrary.get_engine_version(),"map":level,
 "actor":actor.get_actor_label(),"mesh":mesh.get_path_name(),
 "skin_or_rigged":False,"art_approved":False},indent=2)+"\n")
print("TSTSS_ENDER_FIDELITY_MAP_STAGED",out)
