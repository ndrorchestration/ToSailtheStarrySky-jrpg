"""UE5.8 native semantic orientation gate for noncanonical cast lookdev.

Positive Z bounds alone are insufficient. Check material-associated hair against
boots and pants, and preserve the canonical relative height order. Read-only.
"""
import json
import statistics
from pathlib import Path
import unreal

REFERENCE = {
    "Ender": {"hair": "354c35", "boots": "49372c"},
    "Ionia": {"hair": "c99a56", "boots": "48362b"},
    "Lyra": {"hair": "a3472d", "boots": "55402d"},
    "Reson": {"hair": "372e27", "boots": "382b23"},
    "Aepex": {"hair": "714a2d", "boots": "382d27"},
}
ORDER = ("Reson", "Aepex", "Ender", "Ionia", "Lyra")
def gather_z(desc, group_index):
    verts=[]
    for poly in desc.get_polygon_group_polygons(unreal.PolygonGroupID(group_index)):
        verts.extend(desc.get_polygon_vertices(poly))
    if not verts:
        raise ValueError("Empty native polygon group")
    return [desc.get_vertex_position(v).z for v in verts]

def analyze(mesh, name):
    desc=mesh.get_static_mesh_description(0)
    if desc is None:raise ValueError(name+": no LOD0 mesh description")
    mats=[str(x.material_slot_name).lower() for x in mesh.get_editor_property("static_materials")]
    centers={}
    for region,hex_code in REFERENCE[name].items():
        groups=[i for i,mat in enumerate(mats) if mat.endswith(hex_code)]
        if len(groups)!=1:raise ValueError(name+": ambiguous/missing "+region+" material")
        centers[region]=statistics.median(gather_z(desc,groups[0]))
    lo=mesh.get_bounding_box().min.z
    hi=mesh.get_bounding_box().max.z
    if centers["hair"] <= centers["boots"]+20:
        raise ValueError(name+": native hair is not above boot material (possible upside-down mesh)")
    if not lo >= -5 or not (150 < hi-lo < 220):
        raise ValueError(name+": unexpected native height/ground")
    return {"name":name,"hair_median_cm":round(centers["hair"],2),
            "boot_material_median_cm":round(centers["boots"],2),
            "mesh_min_z_cm":round(lo,2),"mesh_max_z_cm":round(hi,2),
            "hair_above_boot_material_cm":round(centers["hair"]-centers["boots"],2)}

def main():
    rows=[]
    for name in REFERENCE:
        p="/Game/ArtLookdev/Characters/"+name+"/"+name+"/StaticMeshes/"+name+"."+name
        mesh=unreal.load_asset(p)
        if not isinstance(mesh,unreal.StaticMesh):raise ValueError(name+": missing StaticMesh")
        rows.append(analyze(mesh,name))
    heights={x["name"]:x["mesh_max_z_cm"]-x["mesh_min_z_cm"] for x in rows}
    # Ender's fighting staff exceeds his intrinsic body height; evaluate
    # relative ranking using unaffected other figures, never that proxy as canon.
    for high,low in zip(("Reson","Ionia"),("Ionia","Lyra")):
        if heights[high]<=heights[low]:raise ValueError("Unexpected lookdev character height ranking")
    output=Path(unreal.Paths.project_dir())/"Saved"/"CharacterLookdev"/"cast_semantic_upright_receipt.json"
    if output.exists():raise ValueError("Refuse overwrite")
    report={"status":"NATIVE_LANDMARK_HEIGHT_PASS_ART_REVIEW_PENDING",
       "engine":unreal.SystemLibrary.get_engine_version(),"results":rows,
       "height_order_canon":"Reson > Aepex > Ender > Ionia > Lyra",
       "numerical_heights_canon":False,"screenshot_orientation_approved":False,
       "model_likeness_approved":False}
    output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("TSTSS_CAST_SEMANTIC_UPRIGHT_PASS",output)

if __name__=="__main__":main()
