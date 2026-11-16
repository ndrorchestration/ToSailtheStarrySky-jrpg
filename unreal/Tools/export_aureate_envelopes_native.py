"""Read-only recorder for isolated V4 review maps. Run via guarded host only.

Collects StaticMesh local asset bounds and component world transforms. Does not
create actors, save maps, prove collision, infer transitions, or authorize art.
"""
from pathlib import Path
import hashlib, json, os, re
import unreal as u

SANDBOX=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103/AureateCinematicV4Sandbox").resolve()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def xyz(v): return [float(v.x),float(v.y),float(v.z)]
def main():
    if os.environ.get("TSTSS_ENVELOPE_EXPORT_EXPLICIT")!="1": raise RuntimeError("HOLD explicit opt-in required")
    project=Path(u.Paths.project_dir()).resolve()
    if project!=SANDBOX: raise RuntimeError("HOLD wrong sandbox")
    descriptor=json.loads((project/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf-8"))
    if "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in descriptor.get("Description",""): raise RuntimeError("HOLD not review sandbox")
    if not u.SystemLibrary.get_engine_version().startswith("5.8.4"): raise RuntimeError("HOLD wrong Unreal version")
    package=os.environ["TSTSS_ENVELOPE_MAP"]
    if not re.fullmatch(r"/Game/TSTSS/Review/Scenes/[A-Za-z0-9_]+",package): raise RuntimeError("HOLD map outside review scenes")
    map_file=project/"Content"/Path(package.removeprefix("/Game/")+".umap")
    expected=os.environ["TSTSS_ENVELOPE_MAP_SHA"]
    if not re.fullmatch(r"[0-9a-f]{64}",expected) or not map_file.is_file() or sha(map_file)!=expected: raise RuntimeError("HOLD map hash")
    output=Path(os.environ["TSTSS_ENVELOPE_OUTPUT"]).resolve()
    if output.is_relative_to(project) or output.exists() or not output.parent.is_dir(): raise RuntimeError("HOLD output path")
    frame=os.environ["TSTSS_ENVELOPE_FRAME"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}",frame): raise RuntimeError("HOLD frame")
    levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
    if levels.is_in_play_in_editor() or u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or u.EditorLoadingAndSavingUtils.get_dirty_content_packages(): raise RuntimeError("HOLD dirty or PIE")
    if not levels.load_level(package): raise RuntimeError("HOLD level load")
    rows=[]; seen=set()
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        if not isinstance(actor,u.StaticMeshActor): continue
        label=str(actor.get_actor_label())
        if not label or label in seen: raise RuntimeError("HOLD duplicate/empty actor label")
        seen.add(label)
        components=actor.get_components_by_class(u.StaticMeshComponent)
        if len(components)!=1 or isinstance(components[0],u.InstancedStaticMeshComponent): raise RuntimeError("HOLD unsupported mesh components")
        comp=components[0]; mesh=comp.get_editor_property("static_mesh")
        if not isinstance(mesh,u.StaticMesh): raise RuntimeError("HOLD missing static mesh")
        bounds=mesh.get_bounding_box(); transform=comp.get_world_transform(); q=transform.rotation
        rows.append({"label":label,"mesh":str(mesh.get_path_name()),"bounds_min":xyz(bounds.min),"bounds_max":xyz(bounds.max),
                     "position":xyz(transform.translation),"rotation_xyzw":[float(q.x),float(q.y),float(q.z),float(q.w)],"scale":xyz(transform.scale3d)})
    if not rows: raise RuntimeError("HOLD empty map")
    if sha(map_file)!=expected: raise RuntimeError("HOLD map changed")
    result={"schema":"aureate_envelope_snapshot_v1","units":"cm","frame":frame,"frame_authority":"OPERATOR_ASSERTED_NOT_PROVEN",
            "map_package":package,"map_sha256":expected,"engine":u.SystemLibrary.get_engine_version(),
            "native_collision_verified":False,"creator_approved":False,"actors":rows}
    encoded=json.dumps(result,indent=2,allow_nan=False)
    with output.open("x",encoding="utf-8") as f: f.write(encoded)
    u.log("AUREATE_ENVELOPE_SNAPSHOT_WRITTEN_NOT_COLLISION_PROOF")
if __name__=="__main__": main()
