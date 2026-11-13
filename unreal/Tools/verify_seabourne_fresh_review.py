"""Native source-locked review map readback using the tracked evidence manifest.

Requires UE 5.8 Editor Python; never edits maps.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unreal

project=Path(unreal.Paths.project_dir()).resolve()
manifest_file=project.parent/"docs/evidence/SEABOURNE_REVIEW_MAP_2026-11-13.json"
if not manifest_file.is_file():
    raise RuntimeError("HOLD: tracked manifest missing")
manifest=json.loads(manifest_file.read_text(encoding="utf-8"))
target=manifest["review_map_package"]
original=manifest["protected_source_map_package"]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=project/("Content"+target.removeprefix("/Game")+".umap")
source=project/("Content"+original.removeprefix("/Game")+".umap")
if not dest.is_file() or sha(dest)!=manifest["review_map_sha256"]:
    raise RuntimeError("HOLD: isolated map bytes do not match evidence")
if not source.is_file() or sha(source)!=manifest["protected_source_map_sha256"]:
    raise RuntimeError("HOLD: legacy source changed")
world=unreal.EditorLoadingAndSavingUtils.load_map(target)
if world is None:
    raise RuntimeError("HOLD: native map reopen failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
labels={str(a.get_actor_label()) for a in actors}
required=set(manifest["requires_actor_labels"])
if not required.issubset(labels):
    raise RuntimeError("HOLD: expected scene actors missing: "+str(required-labels))
ships=[a for a in actors if a.get_class().get_name()==manifest["ship_class"]]
if len(ships)!=1:
    raise RuntimeError("HOLD: expected one preview actor")
ship=ships[0]
if ship.get_current_form()!=unreal.AureateWakeForm.SEABORNE:
    raise RuntimeError("HOLD: wrong saved ship pose")
if ship.get_wing_count()!=manifest["wing_count"] or ship.get_hydrofoil_count()!=manifest["hydrofoil_count"]:
    raise RuntimeError("HOLD: wrong ship component counts")
if ship.has_review_story():
    raise RuntimeError("HOLD: preview editor world unexpectedly has gameplay story authority")
if len(actors)!=manifest["actor_count"]:
    raise RuntimeError("HOLD: actor count drift")
xyz=ship.get_actor_location()
actual=(xyz.x, xyz.y, xyz.z)
if any(abs(a-b)>1.0 for a,b in zip(actual,manifest["ship_location_cm"])):
    raise RuntimeError("HOLD: reviewed ship placement drifted")
result={
  "status":"PORTABLE_NATIVE_MAP_REOPEN_PASS",
  "review_map_sha256":sha(dest),
  "protected_source_sha256":sha(source),
  "ship_count":len(ships),
  "form":"Seabourne",
  "wings":ship.get_wing_count(),
  "hydrofoils":ship.get_hydrofoil_count(),
  "actor_count":len(actors),
  "gpu_visual_approval":False,
}
(project/"Saved/SeabournePortableReadback_20261113.json").write_text(
    json.dumps(result,indent=2)+"\n",encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_PORTABLE_READBACK_PASS "+json.dumps(result))