"""Read-only native geometry/orientation diagnostics for original five imported meshes."""
import json
from pathlib import Path
import unreal

names=("Ender","Ionia","Lyra","Reson","Aepex")
rows=[]
for name in names:
    p="/Game/ArtLookdev/Characters/"+name+"/"+name+"/StaticMeshes/"+name+"."+name
    mesh=unreal.load_asset(p)
    if not isinstance(mesh,unreal.StaticMesh):
        raise RuntimeError(name+": missing mesh")
    bounds=mesh.get_bounding_box()
    rows.append({"name":name,"min_cm":[getattr(bounds.min,k) for k in ("x","y","z")],"max_cm":[getattr(bounds.max,k) for k in ("x","y","z")],
                 "mesh_path":p})
world=unreal.EditorLoadingAndSavingUtils.load_map("/Game/ArtLookdev/ReviewMaps/TSTSS_CastLineup_Review")
if not world:raise RuntimeError("missing map")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for row in rows:
    a=next((a for a in actors if a.get_actor_label()=="LOOKDEV_STATIC_"+row["name"]),None)
    if a is None:raise RuntimeError(row["name"]+": actor not found")
    loc=a.get_actor_location();rot=a.get_actor_rotation()
    row["actor_location_cm"]=[loc.x,loc.y,loc.z]
    row["actor_rotation"]={"pitch":rot.pitch,"yaw":rot.yaw,"roll":rot.roll}
out=Path(unreal.Paths.project_dir())/"Saved"/"CharacterLookdev"/"native_asset_orientation_diag.json"
if out.exists():raise RuntimeError("refuse to overwrite diagnostic")
out.write_text(json.dumps({"engine":unreal.SystemLibrary.get_engine_version(),
                           "status":"READ_ONLY_DIAGNOSTIC","mesh_records":rows},indent=2)+"\n")
print("TSTSS_CAST_ASSET_ORIENTATION_DIAG",out)
