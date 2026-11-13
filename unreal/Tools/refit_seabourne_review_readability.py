"""One-shot native visual-review layout refit; only isolated Seabourne scene."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
if project.parent.name!="TSTSS_V5ObjectIntegration_20261112":
    raise RuntimeError("HOLD: unexpected TSTSS sandbox")
source=project/"Content/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty.umap"
target=project/"Content/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview.umap"
package="/Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview"
sha=lambda b:hashlib.sha256(b).hexdigest()
src_before="5c83e7125eb97aa42d951e89ff1b530600bcc1738287b441f681d44bfaf963bd"
target_before="52a63dc730fb42c7571255a6ea1b0fd5eafb1b41afe5ec59e90ca071d380115e"
if not source.is_file() or sha(source.read_bytes())!=src_before:
    raise RuntimeError("HOLD: original VS05 map changed")
if not target.is_file() or sha(target.read_bytes())!=target_before:
    raise RuntimeError("HOLD: review scene unexpectedly modified")
world=unreal.EditorLoadingAndSavingUtils.load_map(package)
if world is None:
    raise RuntimeError("HOLD: cannot reopen review scene")
system=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=system.get_all_level_actors()
by_label={str(a.get_actor_label()):a for a in actors}
prefix="TSTSS_SEABOURNE_REVIEW_"
def owned(name):
    actor=by_label.get(prefix+name)
    if actor is None:
        raise RuntimeError("HOLD: missing authored actor "+name)
    return actor

ship=owned("AureateWakeVisualProxy")
player=owned("ReviewPlayerStart")
if ship.get_class().get_name()!="AureateWakePreviewActor" or ship.get_current_form()!=unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: wrong ship class or form")
ship.set_actor_location(unreal.Vector(650, 1900, -45), False, False)
player.set_actor_location(unreal.Vector(0, -350, 140), False, False)
# Player now stands on the pier facing near-side ship; review signs behind.
sun=owned("ReviewSun")
sun_comp=sun.get_component_by_class(unreal.DirectionalLightComponent)
sky=owned("ReviewSkyAmbient")
sky_comp=sky.get_component_by_class(unreal.SkyLightComponent)
if sun_comp is None or sky_comp is None:
    raise RuntimeError("HOLD: required lighting components absent")
sun_comp.set_mobility(unreal.ComponentMobility.MOVABLE)
sun_comp.set_editor_property("intensity", 1500.0)
sun_comp.set_atmosphere_sun_light(True)
sky_comp.set_mobility(unreal.ComponentMobility.MOVABLE)
sky_comp.set_editor_property("intensity", 0.45)
sky_comp.set_real_time_capture(True)

def spawn(cls, label):
    actor=system.spawn_actor_from_class(cls, unreal.Vector(0,0,0))
    if actor is None:
        raise RuntimeError("HOLD: spawn failed: "+label)
    actor.set_actor_label(prefix+label)
    return actor

spawn(unreal.SkyAtmosphere, "ReviewSkyAtmosphere")
fog=spawn(unreal.ExponentialHeightFog, "ReviewDistanceFog")
fog_comp=fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
if fog_comp is None:
    raise RuntimeError("HOLD: missing fog component")
fog_comp.set_editor_property("fog_density", 0.001)
fog_comp.set_editor_property("fog_height_falloff", 0.28)
if not unreal.EditorLoadingAndSavingUtils.save_map(world,package):
    raise RuntimeError("HOLD: saving isolated review map failed")
if sha(source.read_bytes())!=src_before:
    raise RuntimeError("HOLD: protected VS05 changed")
new_sha=sha(target.read_bytes())
if new_sha==target_before:
    raise RuntimeError("HOLD: refit changes not persisted")
receipt={
    "status":"SOURCE_LOCKED_VISUAL_REFIT_STAGE",
    "original_vs05_sha256_unchanged":src_before,
    "pre_refit_map_sha256":target_before,
    "new_review_map_sha256":new_sha,
    "review_map_package":package,
    "ship_position_cm":[650,1900,-45],
    "player_start_cm":[0,-350,140],
    "atmosphere":True,
    "fog":True,
    "narrative_mode":"review_only",
    "approved_art":False,
    "gpu_acceptance":False,
}
(project/"Saved/SeabourneVisualRefitReceipt_20261113.json").write_text(
    json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_VISUAL_REFIT_STAGE_PASS "+json.dumps(receipt))