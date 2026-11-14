"""Independent non-mutating native readback of staged VS02 optic copy."""
from pathlib import Path
import hashlib,json
import unreal as u
ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
HERE=PROJECT/"Saved/OpticalVS02Stage"
MAP="/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview"
DEST=PROJECT/"Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"
SOURCE=PROJECT/"Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
p=json.loads((HERE/"prepare.json").read_text())
c=json.loads((HERE/"compose.json").read_text())
assert ROOT.name=="TSTSS_836_835_OpticalGraft_20261114"
assert u.SystemLibrary.get_engine_version().startswith("5.8.4")
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(SOURCE)==p["source_sha256"]
assert sha(DEST)==c["copy_sha256"]
world=u.EditorLoadingAndSavingUtils.load_map(MAP)
assert world is not None,"native saved map reopening failed"
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
all_rows=[dict(label=str(a.get_actor_label()),cl=str(a.get_class().get_name()),
               xyz=[round(float(v),1) for v in (a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z)])
          for a in actors]
def matching(label):return [a for a in actors if str(a.get_actor_label())==label]
gauges=matching("TSTSS_VS_REVIEW_InstrumentCore_LIFT")
directors=[a for a in actors if str(a.get_class().get_name())=="TSTSSAtmosphereDirector"]
cameras=[a for a in actors if str(a.get_actor_label()).startswith("TSTSS_OPTICAL_REVIEW_Inspection_")]
receivers=matching("TSTSS_OPTICAL_REVIEW_Receiver_Disabled")
assert len(gauges)==len(directors)==len(receivers)==1
assert len(cameras)==2
assert not bool(receivers[0].get_editor_property("explicit_review_opt_in"))
for label in c["source_lights_replaced_in_copy"]:assert len(matching(label))==0,label
camera_rows=[]
for a in cameras:
    comp=a.get_cine_camera_component()
    settings=comp.get_editor_property("focus_settings")
    camera_rows.append(dict(label=str(a.get_actor_label()),lens=float(comp.get_editor_property("current_focal_length")),
        aperture=float(comp.get_editor_property("current_aperture")),
        focus_method=str(settings.get_editor_property("focus_method")),
        focus_cm=float(settings.get_editor_property("manual_focus_distance"))))
assert sha(DEST)==c["copy_sha256"],"readback modified stage map"
out=dict(status="VS02_OPTICAL_SAVED_COPY_NATIVE_READBACK_PASS_NOT_PIE_OR_RENDER",
    source_sha256=p["source_sha256"],review_map_sha256=c["copy_sha256"],
    native_actor_count=len(actors),gauge_count=len(gauges),director_count=len(directors),
    disabled_receiver_count=len(receivers),camera_count=len(cameras),
    camera_readback=camera_rows,actor_inventory=all_rows,
    original_source_unchanged=True,pie_input_tested=False,gpu_captured=False,
    creator_approved=False)
with (HERE/"readback.json").open("x",encoding="utf-8") as f:json.dump(out,f,indent=2)
u.log("TSTSS_VS02_OPTICAL_NATIVE_READBACK_PASS_NOT_PIE director=1 gauge=1 cameras=2")
print(json.dumps({k:v for k,v in out.items() if k!="actor_inventory"},indent=2))
