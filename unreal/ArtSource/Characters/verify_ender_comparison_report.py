"""Independently verify native Unreal D3D11 V1/V2 comparison screenshot files.

Never infer screenshot success from AutomationScheduler's queued-task receipt.
This script must read actual Incoming.png files from the Editor report.
"""
import argparse
import json
from pathlib import Path

from ender_comparison_contract import CAMERAS, EXPECTED, MAP
from verify_render_pngs import resolve_capture, inspect_png


def verify(report_folder, task_receipt):
    folder = Path(report_folder)
    receipt = json.loads(Path(task_receipt).read_text(encoding="utf-8"))
    if receipt.get("status") != "UNREAL_SCREENSHOT_TASKS_COMPLETE_NATIVE_PNG_QA_PENDING":
        raise ValueError("Native comparison task completion receipt missing")
    if receipt.get("map") != MAP:
        raise ValueError("Review map mismatch")
    if receipt.get("source_sha256") != {key: obj["sha256"] for key, obj in EXPECTED.items()}:
        raise ValueError("Comparison asset provenance mismatch")
    if receipt.get("reference_likeness_approved") is not False:
        raise ValueError("Creator art acceptance not established")
    if receipt.get("source_files_modified") is not False or receipt.get("saved_unreal_map_modified") is not False:
        raise ValueError("Source/map mutation detected")
    names = [row[0] for row in CAMERAS]
    tasks = receipt.get("capture_tasks", [])
    if [task.get("name") for task in tasks] != names:
        raise ValueError("Missing, reordered or duplicate camera tasks")
    result = {}
    for name in names:
        actual_png = resolve_capture(folder, name)
        metrics = inspect_png(actual_png, (1280, 720))
        result[name] = {**metrics, "actual_png": str(actual_png)}
    if len({value["sha256"] for value in result.values()}) != len(result):
        raise ValueError("Distinct camera views contain duplicated native images")
    return {
        "status": "NATIVE_COMPARISON_IMAGE_INTEGRITY_PASS_NOT_ART_ACCEPTANCE",
        "engine_rendered_and_art_reviewed": False,
        "owner_approved": False,
        "images": result,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("automation_report_folder", type=Path)
    parser.add_argument("native_task_receipt", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.automation_report_folder, args.native_task_receipt), indent=2))
