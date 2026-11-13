"""Independent native readback of the saved Seabourne review map; no writes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
if project.parent.name!="TSTSS_V5ObjectIntegration_20261112":
    raise RuntimeError("HOLD: incorrect sandbox")
receipt_path=project/"Saved/SeabourneFreshStagingReceipt_20261113.json"
receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
target=receipt["target"]
dest=project/"Content/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview.umap"
source=project/"Content/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty.umap"
sha=lambda b:hashlib.sha256(b).hexdigest()
if sha(dest.read_bytes())!=receipt["target_sha256"]:
    raise RuntimeError("HOLD: saved review map drifted")
if sha(source.read_bytes())!=receipt["source_vs05_sha256_unchanged"]:
    raise RuntimeError("HOLD: VS05 original map hash drifted")
world=unreal.EditorLoadingAndSavingUtils.load_map(target)
if world is None:
    raise RuntimeError("HOLD: saved review world failed reopen")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
ships=[a for a in actors if a.get_class().get_name()=="AureateWakePreviewActor"]
if len(ships)!=1:
    raise RuntimeError("HOLD: exactly one ship required, got "+str(len(ships)))
ship=ships[0]
if ship.get_current_form()!=unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: persisted actor not in Seabourne pose")
if ship.get_wing_count()!=4 or ship.get_hydrofoil_count()!=2:
    raise RuntimeError("HOLD: ship geometry component count mismatch")
if ship.has_review_story():
    raise RuntimeError("HOLD: editor review map unexpectedly bound runtime story")
labels={str(a.get_actor_label()) for a in actors}
required={
    "TSTSS_SEABOURNE_REVIEW_AureateWakeVisualProxy",
    "TSTSS_SEABOURNE_REVIEW_CoastalGround",
    "TSTSS_SEABOURNE_REVIEW_WalkablePier",
    "TSTSS_SEABOURNE_REVIEW_OceanNoCollision",
    "TSTSS_SEABOURNE_REVIEW_ReviewPlayerStart",
    "TSTSS_SEABOURNE_REVIEW_Notice",
}
if not required.issubset(labels):
    raise RuntimeError("HOLD: review scene actor missing: "+str(required-labels))
response={
    "status":"NATIVE_REOPEN_PASS_NO_PIE",
    "source_unchanged_sha256":sha(source.read_bytes()),
    "review_map_sha256":sha(dest.read_bytes()),
    "ship_count":len(ships),
    "current_form":"Seabourne",
    "wings":ship.get_wing_count(),
    "hydrofoils":ship.get_hydrofoil_count(),
    "actor_count":len(actors),
    "player_start_present":True,
    "approved_art":False,
    "runtime_sailing_tested":False,
}
(project/"Saved/SeabourneFreshReadback_20261113.json").write_text(
    json.dumps(response,indent=2)+"\n",encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_REOPEN_PASS "+json.dumps(response))