"""Read-only UE 5.8 audit of legacy VS05 for isolated Seabourne review staging."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
if PROJECT.parent.name != "TSTSS_V5ObjectIntegration_20261112":
    raise RuntimeError("HOLD: wrong Unreal project sandbox")
PATH = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty.umap"
SOURCE = "/Game/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty"
if not PATH.is_file():
    raise RuntimeError("HOLD: source native map unavailable")
BEFORE = hashlib.sha256(PATH.read_bytes()).hexdigest()
world = unreal.EditorLoadingAndSavingUtils.load_map(SOURCE)
if world is None:
    raise RuntimeError("HOLD: legacy map did not open")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
entries = []
for actor in actors:
    label = str(actor.get_actor_label())
    if any(t in label for t in ("FuelShop", "FuelPier", "TideShallow", "PlayerStart",
                               "CoastalPlatform", "Shanty", "Aureate", "Wake")):
        pos = actor.get_actor_location()
        entries.append({
            "label": label,
            "class": str(actor.get_class().get_name()),
            "location_cm": [round(pos.x, 2), round(pos.y, 2), round(pos.z, 2)],
        })
labels = {str(a.get_actor_label()) for a in actors}
if "TSTSS_VS_REVIEW_FuelPier" not in labels or "TSTSS_VS_REVIEW_CoastalPlatform" not in labels:
    raise RuntimeError("HOLD: expected pier/platform geometry missing; no staging")
AFTER = hashlib.sha256(PATH.read_bytes()).hexdigest()
if BEFORE != AFTER:
    raise RuntimeError("HOLD: source map bytes changed during audit")
result = {
    "authority": "READ_ONLY_NATIVE_MAP_AUDIT",
    "package": SOURCE,
    "source_sha256_unchanged": BEFORE,
    "actor_count": len(actors),
    "fuelshop_label_present": "TSTSS_VS_REVIEW_FuelShop" in labels,
    "native_preview_ship_count": sum("AureateWakePreviewActor" in str(a.get_class().get_name()) for a in actors),
    "candidate_objects": entries,
}
out = PROJECT / "Saved/SeabourneRecoveryMapAudit_20261113.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
unreal.log("TSTSS_SEABOURNE_MAP_AUDIT_OK " + json.dumps(result))