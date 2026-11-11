"""Build a disposable, review-only 3-column gear showroom map in UE5.8.
Requires prior imported /Game/TSTSS/Review/PartyEquipment StaticMeshes.
Will not touch First Wake maps, production actors, GameMode, inventory, or SaveGame.
"""
import json, traceback
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
EXPECTED=Path(r"C:\TSTSS_PartyEquipmentContentQA_20261110")
REPORT=ROOT/"Saved"/"PartyEquipmentReview"/"gallery_report.json"
IMPORT=ROOT/"Saved"/"PartyEquipmentReview"/"native_import_report.json"
MAP="/Game/TSTSS/Review/PartyEquipment/TSTSS_ThreePartyGearGallery_REVIEW"
data={"status":"STARTED","expected_models":14,"placed_models":0,"review_only":True,
      "lyra_available_during_first_wake":False,
      "playable_character_actors":0,"native_gameplay_test":False}
def save():
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
def require(c,m):
 if not c:raise RuntimeError("FAIL_CLOSED: "+m)
save()
try:
 require(ROOT==EXPECTED,"unexpected destination project")
 require(unreal.SystemLibrary.get_engine_version().startswith("5.8."),"wrong engine")
 record=json.loads(IMPORT.read_text())
 require(record["status"]=="NATIVE_STATIC_MESH_IMPORT_PASS_REVIEW_ONLY","import proof missing")
 require(len(record["entries"])==14,"native mesh count")
 require(not unreal.EditorAssetLibrary.does_asset_exist(MAP),"gallery map already exists")
 level=unreal.EditorLevelLibrary
 require(hasattr(level,"new_level"),"EditorLevelLibrary.new_level not found")
 require(level.new_level(MAP),"failed to create isolated gallery level")
 podium=unreal.load_asset("/Engine/BasicShapes/Cylinder.Cylinder")
 require(isinstance(podium,unreal.StaticMesh),"Engine podium mesh unavailable")
 owners={"Ender":-560.,"Ionia":0.,"Lyra":560.}
 rows={"weapon":0.,"armor":310.,"accessory":620.,"utility":930.,"prop":1235.}
 labels={"Ender":[],"Ionia":[],"Lyra":[],"Shared":[]}
 for item in record["entries"]:
  owner=item["owner"]
  mesh=unreal.load_asset(item["mesh_path"])
  require(isinstance(mesh,unreal.StaticMesh),"missing native reviewed asset "+item["id"])
  ident=item["id"].split(".")[-1]
  cat=next((k for k in rows if k.lower() in ident.lower()),None)
  # Geometry does not encode gameplay slot; author-controlled row by item ID.
  key={
    "Ender.ResonanceStaff":"weapon","Ender.EngineersVest":"armor",
    "Ender.SealedAviatorGoggles":"accessory","Ender.HarmonicCalibrationKit":"utility",
    "Ionia.CaptainSaber":"weapon","Ionia.CaptainsCoat":"armor",
    "Ionia.EarthCompass":"accessory","Ionia.ChartCase":"utility",
    "Lyra.WaterFocus":"weapon","Lyra.TravelCoat":"armor",
    "Lyra.WaterPendant":"accessory","Lyra.HealersSatchel":"utility",
    "Shared.RestorativeVial":"prop","Shared.ResonanceCapacitor":"prop"
  }[item["id"]]
  if owner=="Shared":
   x=-280. if "Vial" in item["id"] else 280.
  else:x=owners[owner]
  y=rows[key]
  pedestal=level.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,55))
  require(pedestal is not None,"could not spawn pedestal")
  pedestal.static_mesh_component.set_static_mesh(podium)
  pedestal.set_actor_scale3d(unreal.Vector(2.0,2.0,1.1))
  pedestal.set_actor_label("REVIEW_PEDESTAL_"+owner+"_"+ident)
  actor=level.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,145))
  require(actor is not None,"could not spawn mesh actor")
  actor.static_mesh_component.set_static_mesh(mesh)
  actor.set_actor_label("REVIEW_"+owner+"_"+ident)
  labels[owner].append(ident)
  data["placed_models"]+=1
 # Lighting for later GUI art direction; nullRHI does NOT prove appearance.
 for cls,loc,rot,name in (
  (unreal.DirectionalLight,unreal.Vector(200,300,1100),
      unreal.Rotator(-42,30,0),"REVIEW_KEY_LIGHT"),
  (unreal.PointLight,unreal.Vector(-300,430,450),
      unreal.Rotator(0,0,0),"REVIEW_FILL_LIGHT")
 ):
  actor=level.spawn_actor_from_class(cls,loc,rot)
  require(actor is not None,"failed review light")
  actor.set_actor_label(name)
 require(data["placed_models"]==14,"incomplete gallery")
 require(level.save_current_level(),"could not save gallery map")
 require(unreal.EditorAssetLibrary.does_asset_exist(MAP),"native gallery umap not persisted")
 data.update(status="NATIVE_REVIEW_GALLERY_MAP_PASS_NO_VISUAL_PROOF",
             map_package=MAP,by_owner=labels,gameplay_actors=0)
except Exception:
 data["status"]="NATIVE_REVIEW_GALLERY_FAILED"
 data["error"]=traceback.format_exc()[-4500:]
 unreal.log_error(data["error"])
finally:
 save()
unreal.log("TSTSS_THREE_PARTY_GEAR_GALLERY "+data["status"])
