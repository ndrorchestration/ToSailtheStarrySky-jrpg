"""Independent native proof of the nonshipping VS02 reframed optical copy.

Run only in Unreal Editor 5.8.4 with -ExecutePythonScript. Native map
readback alone does NOT verify actual PIE input, GPU bokeh or visual approval.
"""
from __future__ import annotations
import hashlib
import json
import math
import subprocess
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
MANIFEST = PROJECT / "DataSource/Cinematics/VS02OpticalLookdev.review.json"
OUT = PROJECT / "Saved/OpticalVS02Stage/LookdevV2Readback"
SOURCE_FILE = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
REVIEW_FILE = PROJECT / "Content/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview.umap"

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(ok: bool, why: str):
    if not ok:
        raise RuntimeError("HOLD: " + why)

def verify() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(ROOT.name == "TSTSS_836_835_OpticalGraft_20261114",
            "wrong native isolated review worktree")
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
            "wrong Unreal Editor version")
    require(digest(SOURCE_FILE) == manifest["original_source_sha256"],
            "protected original map checksum differs")
    require(digest(REVIEW_FILE) == manifest["current_review_map_sha256"],
            "review copy checksum differs")
    require(not (OUT / "readback.json").exists(), "existing evidence receipt")
    world = u.EditorLoadingAndSavingUtils.load_map(manifest["current_review_map"])
    require(world is not None, "review map cannot be loaded")
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    require(len(actors) == manifest["actor_count"], "unexpected actor count")
    def single(label):
        found = [actor for actor in actors if str(actor.get_actor_label()) == label]
        require(len(found) == 1, "actor inventory mismatch: " + label)
        return found[0]
    gauge = single(manifest["camera_target_actor"])
    require(gauge.get_class().get_name() == "StaticMeshActor",
            "LIFT is not a native scene mesh")
    require(sum(actor.get_class().get_name() == "TSTSSAtmosphereDirector"
                for actor in actors) == 1, "exact one atmosphere owner required")
    receiver = single("TSTSS_OPTICAL_REVIEW_Receiver_Disabled")
    require(receiver.get_editor_property("explicit_review_opt_in") is False,
            "optical receiver unexpectedly enabled")
    target = gauge.get_actor_location()
    offset = u.Vector(*manifest["camera_offset_cm"])
    pos = target + offset
    distance = math.sqrt(sum(float(v) ** 2 for v in manifest["camera_offset_cm"]))
    rows = []
    for label, disabled in (
        ("TSTSS_OPTICAL_REVIEW_Inspection_ManualDOF", False),
        ("TSTSS_OPTICAL_REVIEW_Inspection_NoDOF_Control", True),
    ):
        actor = single(label)
        xyz = actor.get_actor_location()
        error = math.sqrt((xyz.x - pos.x)**2 +
                          (xyz.y - pos.y)**2 +
                          (xyz.z - pos.z)**2)
        require(error < 0.1, "camera position drift: " + label)
        camera = actor.get_cine_camera_component()
        require(camera is not None, "missing native cine camera component")
        require(abs(float(camera.get_editor_property("current_focal_length")) -
                    manifest["camera_lens_mm"]) < 0.05, "focal length changed")
        require(abs(float(camera.get_editor_property("current_aperture")) -
                    manifest["camera_aperture_f"]) < 0.05, "aperture changed")
        focus = camera.get_editor_property("focus_settings")
        expected = u.CameraFocusMethod.DISABLE if disabled else u.CameraFocusMethod.MANUAL
        require(focus.get_editor_property("focus_method") == expected,
                "focus mode changed: " + label)
        require(abs(float(focus.get_editor_property("manual_focus_distance")) -
                    distance) < 1.0, "focus distance changed")
        pp = camera.get_editor_property("post_process_settings")
        require(bool(pp.get_editor_property("override_auto_exposure_bias")),
                "camera fixed exposure override absent")
        require(abs(float(pp.get_editor_property("auto_exposure_bias")) -
                    manifest["camera_exposure_bias_ev"]) < 0.01, "exposure bias changed")
        require(abs(float(camera.get_editor_property("post_process_blend_weight")) -
                    1.0) < 0.001, "post process blend unexpectedly disabled")
        rows.append({"label": label, "focus_mode": "disabled" if disabled else "manual",
                     "focus_cm": round(distance, 3),
                     "exposure_ev": manifest["camera_exposure_bias_ev"]})
    require(digest(SOURCE_FILE) == manifest["original_source_sha256"] and
            digest(REVIEW_FILE) == manifest["current_review_map_sha256"],
            "map changed during read-only actor inspection")
    receipt = {
        "status": "NATIVE_VS02_OPTICAL_V2_READBACK_PASS_NOT_PIE_OR_VISUAL_APPROVAL",
        "source_sha256": digest(SOURCE_FILE),
        "review_map_sha256": digest(REVIEW_FILE),
        "actor_count": len(actors),
        "camera_readback": rows,
        "source_map_unchanged": True,
        "receiver_enabled": False,
        "physical_keyboard_tested": False,
        "gpu_bokeh_approved": False,
        "creator_approved": False,
        "map_write_performed": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "readback.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
    u.log("TSTSS_VS02_OPTICAL_V2_NATIVE_READBACK_PASS_NOT_PIE")
    return receipt

if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
