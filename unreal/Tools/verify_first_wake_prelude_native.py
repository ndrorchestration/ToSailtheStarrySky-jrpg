"""Inspect the saved Unreal Prelude map and exercise actual native milestone actors.

Run ONLY on the disposable First Wake Prelude Sandbox, in Unreal Editor Python.
The test creates an unsaved temporary UObject story state; it does NOT change
the map, player saves or game state, run physics observations or grant crew.
"""
from pathlib import Path
import hashlib
import json
import unreal
from build_first_wake_prelude_interaction import (
    REVIEW_MAP, STOPS, AUTHORING_PREFIX, assert_disposable_project,
)

project = assert_disposable_project(unreal.Paths.project_dir())
map_asset = project / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
if not map_asset.is_file():
    raise RuntimeError("Expected actual native .umap missing")
prior = hashlib.sha256(map_asset.read_bytes()).hexdigest()
if not unreal.EditorAssetLibrary.does_asset_exist(REVIEW_MAP):
    raise RuntimeError("Review .umap not registered in Unreal")
loaded = unreal.EditorLoadingAndSavingUtils.load_map(REVIEW_MAP)
if loaded is None:
    raise RuntimeError("Unable to load actual Prelude review .umap")
actor_subsys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = actor_subsys.get_all_level_actors()
by_label = {}
for actor in actors:
    name = actor.get_actor_label()
    if name in by_label and name.startswith(AUTHORING_PREFIX):
        raise RuntimeError("Duplicate review actor label: "+name)
    by_label[name] = actor

for stop in STOPS:
    label = AUTHORING_PREFIX + stop.label
    actor = by_label.get(label)
    if actor is None or not isinstance(actor, unreal.TSTSSMilestoneActor):
        raise RuntimeError("Missing actual compiled milestone actor: " + label)
    part = actor.get_component_by_class(unreal.StaticMeshComponent)
    if part is None or not part.get_editor_property("static_mesh"):
        raise RuntimeError("Missing collidable review interaction mesh: " + label)
    if bool(actor.get_editor_property("is_inspection_station")) != bool(stop.inspection):
        raise RuntimeError("Inspection/milestone type drift: " + label)

start = by_label.get(AUTHORING_PREFIX+"PlayerStart_Ender_REVIEW_PROXY")
if start is None or not isinstance(start, unreal.PlayerStart):
    raise RuntimeError("Review PlayerStart missing")
if by_label.get(AUTHORING_PREFIX+"Harbor_TraversalFloor") is None:
    raise RuntimeError("Traversable floor missing")
ocean = by_label.get(AUTHORING_PREFIX+"Ocean_VISUAL_ONLY_NO_BUOYANCY")
if ocean is None:
    raise RuntimeError("Visual-only ocean marker missing")
sea_collision = ocean.get_component_by_class(unreal.StaticMeshComponent)
if sea_collision is None or sea_collision.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
    raise RuntimeError("Visual-only ocean has physical collision")
if str(sea_collision.get_collision_profile_name()).lower() != "nocollision":
    raise RuntimeError("Decorative ocean collision profile is not persistent NoCollision")
floor_collision = by_label[AUTHORING_PREFIX+"Harbor_TraversalFloor"].get_component_by_class(unreal.StaticMeshComponent)
if floor_collision is None or floor_collision.get_collision_enabled() != unreal.CollisionEnabled.QUERY_AND_PHYSICS:
    raise RuntimeError("Traversal floor does not block the player")
if any(name.startswith(AUTHORING_PREFIX+"SeaContact") or
       name.startswith(AUTHORING_PREFIX+"FlotationConfirmed") for name in by_label):
    raise RuntimeError("Fake sea landing actor forbidden")

state_class = unreal.load_class(None,"/Script/ToSailTheStarrySky.TSTSSFirstWakeState")
if state_class is None:
    raise RuntimeError("Compiled native First Wake story state unavailable")
state = unreal.new_object(state_class)
milestones = {stop.label:by_label[AUTHORING_PREFIX + stop.label] for stop in STOPS}
if milestones["EngineeringApproval"].try_activate(state):
    raise RuntimeError("Premature EngineeringChecked accepted")
if milestones["IoniaHiring"].try_activate(state):
    raise RuntimeError("Premature hiring accepted")
for name in ("FlyerDiscovery","IoniaHiring","AureateBoarding"):
    if not milestones[name].try_activate(state):
        raise RuntimeError("Valid ordered interaction rejected: "+name)
if milestones["EngineeringApproval"].try_activate(state):
    raise RuntimeError("Engineering approval accepted before inspections")
for name in ("LiftStation","PressureStation","ReserveStation"):
    if not milestones[name].try_activate(state):
        raise RuntimeError("Valid inspection rejected: "+name)
    if milestones[name].try_activate(state):
        raise RuntimeError("Duplicate inspection accepted: "+name)
if not milestones["EngineeringApproval"].try_activate(state):
    raise RuntimeError("Completed inspection signoff rejected")
if state.is_chapter_one_act_one():
    raise RuntimeError("Fake Splashdown obtained without physical flotation")
if len([a for a in actors if isinstance(a,unreal.TSTSSMilestoneActor)]) != len(STOPS):
    raise RuntimeError("Unexpected extra milestone actor")

after = hashlib.sha256(map_asset.read_bytes()).hexdigest()
if after != prior:
    raise RuntimeError("Review map was modified by verification")
out_dir = project/"Saved"/"PreludeInteractionV2"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir/"native_actor_verification_pr694.json"
if out_file.exists():
    raise RuntimeError("Native actor receipt exists: refuse overwrite")
receipt = {
    "status":"UNREAL_NATIVE_MILESTONE_ACTORS_PASS_NOT_PLAYTEST_APPROVAL",
    "map":REVIEW_MAP,
    "map_sha256":prior,
    "actual_milestone_actors":len(STOPS),
    "ordered_activation_steps":7,
    "premature_engineering_rejected":True,
    "premature_ionia_rejected":True,
    "duplicate_inspections_rejected":True,
    "chapter_one_act_one":False,
    "ocean_physics":False,
    "ue_version":unreal.SystemLibrary.get_engine_version(),
    "artist_approved":False,
    "player_input_tested":False,
}
out_file.write_text(json.dumps(receipt, indent=2)+"\n",encoding="utf-8")
print("TSTSS_PRELUDE_NATIVE_ACTOR_VERIFICATION_PASS",json.dumps(receipt))
