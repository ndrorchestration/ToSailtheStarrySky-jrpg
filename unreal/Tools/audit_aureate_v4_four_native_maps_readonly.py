"""Read-only native Unreal 5.8.4 audit of all four V4 preview maps.

Does not spawn, attach, move, rotate, save, import, render or promote content.
Refuses checksum drift. Starbourne is a private static preview only.
"""
from pathlib import Path
import hashlib
import json
import traceback
import unreal

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"
OUT=ROOT/"four_map_native_readonly_audit_v2_20261103.json"
FORMS=("Skybourne","Seabourne","Submersible","Starbourne")
WINGS=("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")
CAMERAS=("THREE_QUARTER","TOP","PROFILE","BRIDGE")
MAP_SHA={
 "Skybourne":"16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",
 "Seabourne":"b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a",
 "Submersible":"815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35",
 "Starbourne":"953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00",
}
EXPECTED_COUNT=dict(Skybourne=18,Seabourne=20,Submersible=15,Starbourne=14)
report={"state":"STARTED","engine":None,"mutated_scene":False,
        "story_starbourne_unlocked":False,"gpu_capture":False,
        "forms":[],"errors":[]}
if OUT.exists():raise FileExistsError("Previous audit exists: refuse overwrite")
def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def validate(cond,msg):
    if not cond:raise RuntimeError(msg)
def xyz(vector):
    return [round(float(getattr(vector,axis)),4) for axis in ("x","y","z")]
try:
    validate(Path(unreal.Paths.project_dir()).resolve()==PROJECT.resolve(),"Not disposable review project")
    conf=json.loads((PROJECT/"AureateCinematicV4Sandbox.uproject").read_text(encoding="utf8"))
    validate("AUREATE_CINEMATIC_V4_REVIEW_ONLY" in conf.get("Description",""),"Non-review project")
    report["engine"]=unreal.SystemLibrary.get_engine_version()
    validate(report["engine"].startswith("5.8."),"Incorrect engine")
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for form in FORMS:
        basename=("AureateCinematicV4_Skybourne_Hero_20261103_FullEditor" if form=="Skybourne"
                  else "AureateCinematicV4_"+form+"_20261103_FullEditor")
        file=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/(basename+".umap")
        location="/Game/TSTSS/Review/Scenes/"+basename
        validate(file.is_file() and checksum(file)==MAP_SHA[form],"Map missing or checksum drift: "+form)
        validate(bool(levels.load_level(location)),"Unreal cannot load map: "+form)
        active=actors.get_all_level_actors()
        labels=[a.get_actor_label() for a in active]
        validate(len(active)==EXPECTED_COUNT[form],
                 "Actor count drift: "+form+" "+str(len(active)))
        validate(len(set(labels))==len(labels),"Duplicate actor labels: "+form)
        for core in ("SHARED_PEARL_HULL_PROXY","SHARED_HULL_CINEMATIC_V4_TRIM",
                     "CENTRAL_LIVING_QUARTERS_PROXY",
                     "FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",
                     "FORWARD_OBSERVATION_DECK_PROXY"):
            validate("V4_NONCANONICAL_"+core in labels,"Shared core absent: "+form+" "+core)
        wing_tags=[]
        for wing in WINGS:
            found=[x for x in labels if wing in x and
                   (("_MEMBRANE_PROXY" in x) if form!="Starbourne"
                    else ("PRIVATE_STATIC_STARB_SAIL_ID_" in x))]
            validate(len(found)==1,"Missing/repeated wing identity "+wing+" in "+form)
            wing_tags.append(found[0])
        cams=[a for a in active if isinstance(a,unreal.CameraActor)]
        validate(len(cams)==4,"Camera count drift: "+form)
        for view in CAMERAS:
            name=("V4_NONCANONICAL_CAMERA_"+view if form=="Skybourne"
                  else "V4_NONCANONICAL_"+form+"_CAMERA_"+view)
            validate(sum(a.get_actor_label()==name for a in cams)==1,
                     "Camera role absent: "+form+" "+view)
        hull=next(a for a in active if a.get_actor_label()=="V4_NONCANONICAL_SHARED_PEARL_HULL_PROXY")
        dome=next(a for a in active if a.get_actor_label()=="V4_NONCANONICAL_FORWARD_GLASS_GEODESIC_BRIDGE_PROXY")
        quarters=next(a for a in active if a.get_actor_label()=="V4_NONCANONICAL_CENTRAL_LIVING_QUARTERS_PROXY")
        if form=="Seabourne":
            for side in ("PORT","STARBOARD"):
                validate("V4_NONCANONICAL_HYDROFOIL_"+side+"_PROXY" in labels,
                         "Missing foil "+side)
                validate("V4_NONCANONICAL_HYDROFOIL_"+side+"_V4_DETAIL" in labels,
                         "Missing imported foil detail "+side)
            validate(sum(x in ("V4_NONCANONICAL_HYDROFOIL_PORT_PROXY",
                              "V4_NONCANONICAL_HYDROFOIL_STARBOARD_PROXY")
                             for x in labels)==2,"Foil count drift")
        elif form=="Submersible":
            validate("V4_NONCANONICAL_SUBMERSIBLE_V4_LIGHT_RAIL" in labels,
                     "Missing underwater rail")
        elif form=="Starbourne":
            sails=[x for x in labels if "PRIVATE_STATIC_STARB_SAIL_ID_" in x]
            validate(len(sails)==4,"Not four static radial sail actors")
            for direction in ("UP","RIGHT","DOWN","LEFT"):
                validate(sum(x.endswith("_"+direction) for x in sails)==1,
                         "Missing cardinal sail "+direction)
        v={
            "form":form,"map":location,"map_sha_before":MAP_SHA[form],
            "actor_count":len(active),"wing_identity_labels":wing_tags,
            "camera_labels":[a.get_actor_label() for a in cams],
            "hull_xyz_cm":xyz(hull.get_actor_location()),
            "bridge_xyz_cm":xyz(dome.get_actor_location()),
            "quarters_xyz_cm":xyz(quarters.get_actor_location()),
            "bridge_quarters_rotation_proven":False,
            "gpu_verified":False,
            "starbourne_player_unlocked":False,
        }
        report["forms"].append(v)
    shared=[(a["hull_xyz_cm"],a["bridge_xyz_cm"],a["quarters_xyz_cm"])
            for a in report["forms"]]
    validate(all(item==shared[0] for item in shared),"Core transform drift across form maps")
    for form in FORMS:
        basename=("AureateCinematicV4_Skybourne_Hero_20261103_FullEditor" if form=="Skybourne"
                  else "AureateCinematicV4_"+form+"_20261103_FullEditor")
        file=PROJECT/"Content"/"TSTSS"/"Review"/"Scenes"/(basename+".umap")
        validate(checksum(file)==MAP_SHA[form],"Read-only map digest changed: "+form)
    report["shared_core_matches_across_forms"]=True
    report["native_four_map_actor_readback_pass"]=True
    report["state"]="FOUR_MAP_READONLY_NATIVE_AUDIT_PASS"
except Exception as err:
    report["state"]="FOUR_MAP_READONLY_NATIVE_AUDIT_HOLD"
    report["errors"].append(str(err))
    report["traceback"]=traceback.format_exc()[-3500:]
finally:
    OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    unreal.log("TSTSS_FOUR_MAP_NATIVE_AUDIT "+json.dumps(report,sort_keys=True))
if report["state"]!="FOUR_MAP_READONLY_NATIVE_AUDIT_PASS":
    raise RuntimeError(report["errors"][0])
