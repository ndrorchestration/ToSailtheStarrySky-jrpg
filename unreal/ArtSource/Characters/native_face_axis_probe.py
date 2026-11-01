"""Read-only UE5.8 face forward-axis probe using actual pupil and shirt polygons."""
import json,statistics
from pathlib import Path
import unreal
m=unreal.load_asset("/Game/ArtLookdev/Characters/Ender/Ender/StaticMeshes/Ender.Ender")
d=m.get_static_mesh_description(0)
materials=[str(x.material_slot_name).lower() for x in m.get_editor_property("static_materials")]
out={"engine":unreal.SystemLibrary.get_engine_version(),"groups":[]}
for suffix in ("211b18","e8d9b8","c99972","354c35"):
 ids=[i for i,k in enumerate(materials) if k.endswith(suffix)]
 if len(ids)!=1:raise RuntimeError("Unexpected material "+suffix)
 points=[]
 for poly in d.get_polygon_group_polygons(unreal.PolygonGroupID(ids[0])):
  for v in d.get_polygon_vertices(poly):
   p=d.get_vertex_position(v);points.append((p.x,p.y,p.z))
 med=[statistics.median(p[i] for p in points) for i in range(3)]
 out["groups"].append({"suffix":suffix,"median_xyz_cm":med,"min_xyz_cm":[min(p[i] for p in points) for i in range(3)],"max_xyz_cm":[max(p[i] for p in points) for i in range(3)]})
dest=Path(unreal.Paths.project_dir())/"Saved"/"CharacterLookdev"/"native_face_axis_20261101.json"
if dest.exists():raise RuntimeError("No overwrite")
dest.write_text(json.dumps(out,indent=2)+"\n")
print("TSTSS_FACE_AXIS_PASS",dest)
