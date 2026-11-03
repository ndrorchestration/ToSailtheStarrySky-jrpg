"""UE 5.8 MetaHuman V5: read-only native 79-landmark index census.

NOT semantic label registration, approved face fitting, sculpt, render or rig.
Requires fresh disposable MH2 clone, exact saved V5 base and review-map SHAs.
"""
import hashlib
import json
import math
from pathlib import Path
import unreal

SHA_ASSET="7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd"
SHA_MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
REL_ASSET="Content/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.uasset"
REL_MAP="Content/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review.umap"
OBJECT="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
OUTPUT="Saved/CharacterLookdev/EnderV5LandmarkAtlas/native_landmark_index.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    proj=Path(unreal.Paths.project_dir()).resolve()
    conf=proj/"CastAllSandbox.uproject"
    assert proj.name=="CastAllSandbox"
    assert "MH2" in str(proj), "Refuse non-review clone"
    assert conf.is_file()
    c=json.loads(conf.read_text(encoding="utf-8-sig"))
    assert "Disposable TSTSS Ender V5 Landmark Atlas read-only" in c["Description"]
    assert c["EngineAssociation"]=="5.8"
    assert any(q["Name"]=="MetaHumanCharacter" and q.get("Enabled") is True
               for q in c["Plugins"])
    engine=unreal.SystemLibrary.get_engine_version()
    assert engine.startswith("5.8.")
    asset_file=proj/REL_ASSET
    map_file=proj/REL_MAP
    assert digest(asset_file)==SHA_ASSET, "V5 base asset changed"
    assert digest(map_file)==SHA_MAP, "V2 review map changed"
    outfile=proj/OUTPUT
    if outfile.exists():
        raise FileExistsError("Refuse overwrite of prior native landmark evidence")
    if not hasattr(unreal,"MetaHumanCharacterEditorSubsystem"):
        raise RuntimeError("MetaHuman editor subsystem unavailable")
    asset=unreal.load_asset(OBJECT)
    if asset is None or not isinstance(asset,unreal.MetaHumanCharacter):
        raise RuntimeError("V5 saved MetaHuman asset not loadable")
    assert asset.get_path_name()==OBJECT
    sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    if sub is None:
        raise RuntimeError("Missing registered MetaHuman face editor")
    registered=False
    points=[]
    try:
        registered=bool(sub.try_add_object_to_edit(asset))
        if not registered:
            raise RuntimeError("Could not enter read-only face edit context")
        native=sub.get_face_landmarks(character=asset)
        if native is None or len(native)!=79:
            raise RuntimeError("Native landmark count changed; refuse guessed mapping")
        for index,v in enumerate(native):
            xyz=[round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)]
            if not all(math.isfinite(x) and abs(x)<1000 for x in xyz):
                raise ValueError("Invalid native landmark coordinate")
            points.append({"index":index,"xyz_cm":xyz})
    finally:
        if registered:
            sub.remove_object_to_edit(asset)
    assert [p["index"] for p in points]==list(range(79))
    assert digest(asset_file)==SHA_ASSET and digest(map_file)==SHA_MAP
    bounds={}
    for i,axis in enumerate("xyz"):
        vals=[p["xyz_cm"][i] for p in points]
        bounds[axis]={"min_cm":round(min(vals),5),"max_cm":round(max(vals),5)}
    data={
        "status":"NATIVE_METAHUMAN_79_INDEX_ATLAS_PASS_NO_SCULPT",
        "engine":engine,"source_asset":OBJECT,
        "source_uasset_sha256_before_after":SHA_ASSET,
        "saved_reference_map_sha256_before_after":SHA_MAP,
        "source_asset_changed":False,"face_landmarks_edited":False,
        "semantic_point_names_known":False,
        "source_image_landmark_correspondences_approved":False,
        "likeness_approved":False,"face_assembled":False,
        "skin_editing_available":False,"rigged":False,"render_verified":False,
        "image_space_coordinates_measured":False,
        "coordinate_system":"Unreal native world/model coordinate from MetaHumanCharacterEditorSubsystem, centimetres; index order is API output, NO semantic names",
        "point_count":len(points),"bounds_cm":bounds,"points":points,
    }
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("TSTSS_ENDER_V5_LANDMARK_ATLAS_NATIVE_PASS",len(points),str(outfile))
    print("TSTSS_ENDER_V5_LANDMARK_AXIS_BOUNDS",json.dumps(bounds,sort_keys=True))

if __name__=="__main__":
    run()
