"""Targeted one-shot edit: clear line of sight to draft Seabourne ship."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
if project.parent.name!="TSTSS_V5ObjectIntegration_20261112":
    raise RuntimeError("HOLD: wrong project")
src=project/"Content/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty.umap"
dst=project/"Content/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview.umap"
target="/Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview"
sha=lambda b:hashlib.sha256(b).hexdigest()
src_sha="5c83e7125eb97aa42d951e89ff1b530600bcc1738287b441f681d44bfaf963bd"
before_sha="a460e90c7154a6bbf592fc2040f85e89a53aa0ee6c88683e4d902d6577037512"
if sha(src.read_bytes())!=src_sha or sha(dst.read_bytes())!=before_sha:
    raise RuntimeError("HOLD: map has drifted")
world=unreal.EditorLoadingAndSavingUtils.load_map(target)
if world is None:
    raise RuntimeError("HOLD: cannot reopen independent review")
by_label={str(a.get_actor_label()):a for a in
          unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
def authored(label):
    a=by_label.get("TSTSS_SEABOURNE_REVIEW_"+label)
    if a is None:raise RuntimeError("HOLD: required actor missing: "+label)
    return a
ship=authored("AureateWakeVisualProxy")
if ship.get_current_form()!=unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: ship form not Seabourne")
ship.set_actor_location(unreal.Vector(580,1100,-35),False,False)
for ix in (-1,1):
    rail=authored("PierRail"+str(ix))
    rail.set_actor_scale3d(unreal.Vector(.12,39,.45))
    rail.set_actor_location(unreal.Vector(ix*280,-150,35),False,False)
if not unreal.EditorLoadingAndSavingUtils.save_map(world,target):
    raise RuntimeError("HOLD: review map save failed")
if sha(src.read_bytes())!=src_sha:
    raise RuntimeError("HOLD: source map changed")
new_sha=sha(dst.read_bytes())
if new_sha==before_sha:
    raise RuntimeError("HOLD: unchanged map after clearance refit")
receipt={
 "status":"REVIEW_DOCK_SIGHTLINE_REFIT_PASS",
 "target":target,
 "prior_map_sha256":before_sha,
 "new_review_map_sha256":new_sha,
 "source_vs05_sha256_unchanged":src_sha,
 "ship_location_cm":[580,1100,-35],
 "rail_height_cm":45,
 "gpu_reviewed":False,
 "approved":False,
}
(project/"Saved/SeabourneSightlineReceipt_20261113.json").write_text(
    json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_SIGHTLINE_STAGE_PASS "+json.dumps(receipt))