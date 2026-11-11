#!/usr/bin/env python3
"""Content-addressed handoff for the NONCANONICAL 3D First Wake shore review.

This file is not an Unreal native build, PIE, gameplay or art acceptance gate.
--snapshot: create one immutable (non-overwriting) provenance manifest after
           exact historical-head native Editor stage and independent readback.
--check:    engine-free verification of committed native asset bytes and scope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
MANIFEST = PROJECT / "Docs/Evidence/firstwake_multipath_native_scene_snapshot_20261111.json"
STAGE = PROJECT / "Saved/MultipathV1/shore_stage_receipt.json"
READBACK = PROJECT / "Saved/MultipathV1/shore_independent_readback.json"
NATIVE = PROJECT / "Saved/MigrationEvidence/a7244775e642-20261111T144831776Z-0dd10928/verified-native.json"
NATIVE_REPORT = NATIVE.parent / "AutomationReport/index.json"
MAP = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
ORIGINAL = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS06_SplashdownShore.umap"
MAGIC = PROJECT / "Content/TSTSS/Magic"
REVIEW = PROJECT / "Content/TSTSS/Review/MultipathV1"
ORIGIN_HEAD = "a7244775e64208be21f04320cc7fe20703704979"
EXPECTED_MAP_HASH = "fec410d08244ec5ac71965af2df98434411591aa8a280dfefe8ea038ae50357f"
EXPECTED_SOURCE_HASH = "316299925275785494d1ec7b082f20007fa0f889f50ce59ea1c7e977ef942726"
EXPECTED_ASSET_COUNT = 222

def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def assets() -> list[dict]:
    paths = sorted([x for folder in (MAGIC, REVIEW)
                    for x in folder.rglob("*") if x.is_file()],
                   key=lambda x: x.relative_to(ROOT).as_posix())
    if len(paths) != EXPECTED_ASSET_COUNT:
        raise RuntimeError(f"HOLD: expected {EXPECTED_ASSET_COUNT} native review files, got {len(paths)}")
    if sum(p.suffix == ".umap" for p in paths) != 1 or sum(p.suffix == ".uasset" for p in paths) != 221:
        raise RuntimeError("HOLD: nonreview/unknown asset extension or map count")
    if not all(p.suffix in (".uasset", ".umap") for p in paths):
        raise RuntimeError("HOLD: unexpected generated review file")
    if MAP not in paths or MAGIC / "M_ResonatorGlow.uasset" not in paths:
        raise RuntimeError("HOLD: expected map or dedicated Ender material missing")
    if checksum(MAP) != EXPECTED_MAP_HASH or checksum(ORIGINAL) != EXPECTED_SOURCE_HASH:
        raise RuntimeError("HOLD: native map or canonical source-map hash mismatch")
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "sha256": checksum(p)} for p in paths]

def tree_digest(entries: list[dict]) -> str:
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def verify_historical_native_receipts() -> dict:
    for p in (STAGE, READBACK, NATIVE, NATIVE_REPORT):
        if not p.is_file():
            raise RuntimeError("HOLD: historical native exact-head receipt missing")
    stage = json.loads(STAGE.read_text(encoding="utf-8"))
    readback = json.loads(READBACK.read_text(encoding="utf-8"))
    native = json.loads(NATIVE.read_text(encoding="utf-8-sig"))
    if (stage.get("status") != "NATIVE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED"
            or stage.get("source_head") != ORIGIN_HEAD
            or stage.get("new_map_sha256") != EXPECTED_MAP_HASH
            or stage.get("source_sha256") != EXPECTED_SOURCE_HASH
            or stage.get("new_unique_review_actors") != 26
            or stage.get("saved_actor_count") != 43
            or stage.get("PIE_verified") is not False
            or stage.get("visual_approved") is not False):
        raise RuntimeError("HOLD: historical native stage receipt changed")
    if (readback.get("status") != "NATIVE_EDITOR_MAP_REOPENED_SOURCE_LOCKED_NOT_PIE"
            or readback.get("head") != ORIGIN_HEAD
            or readback.get("map_sha256") != EXPECTED_MAP_HASH
            or readback.get("native_actor_count") != 43
            or readback.get("review_actor_count") != 26
            or readback.get("original_shore_map_sha256") != EXPECTED_SOURCE_HASH
            or any(readback.get(k) is not False for k in
                   ("pie_verified", "gpu_render_verified", "creator_approved"))):
        raise RuntimeError("HOLD: independent native readback changed")
    if (native.get("status") != "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE"
            or native.get("source_sha") != ORIGIN_HEAD
            or native.get("required_native_tests") != 35
            or native.get("report_sha256") != checksum(NATIVE_REPORT)):
        raise RuntimeError("HOLD: historical exact-head 35-test native acceptance missing")
    report = json.loads(NATIVE_REPORT.read_text(encoding="utf-8-sig"))
    if (report.get("succeeded") != 35 or report.get("failed") != 0 or report.get("notRun") != 0
            or len(report.get("tests", [])) != 35
            or any(x.get("state") != "Success" for x in report["tests"])):
        raise RuntimeError("HOLD: actual historical native test report not complete")
    return {"native_test_report_sha256": native["report_sha256"],
            "readback_status": readback["status"],
            "prepared_actor_count": 43,
            "review_actor_count": 26}

def snapshot() -> dict:
    if MANIFEST.exists():
        raise RuntimeError("HOLD: content-addressed scene manifest already exists; do not overwrite")
    entries = assets()
    evidence = verify_historical_native_receipts()
    out = {
        "schema": "tstss.firstwake.shore-review-native-snapshot.v1",
        "source_provenance_head": ORIGIN_HEAD,
        "delivered_candidate_head": "NOT_YET_VERIFIED_AFTER_ASSET_COMMIT",
        "engine": "Unreal Engine 5.8.4",
        "status": "SAVED_NATIVE_REVIEW_ARTIFACTS_UNMERGED_UNAPPROVED",
        "assets_are_review_only": True,
        "native_files": len(entries),
        "total_bytes": sum(x["bytes"] for x in entries),
        "content_tree_sha256": tree_digest(entries),
        "map_sha256": EXPECTED_MAP_HASH,
        "original_map_sha256": EXPECTED_SOURCE_HASH,
        **evidence,
        "pie_verified": False,
        "player_controls_verified": False,
        "gpu_render_verified": False,
        "creator_visual_approved": False,
        "canon_authorized": False,
        "main_merge_authorized": False,
        "files": entries,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("x", encoding="utf-8") as stream:
        json.dump(out, stream, indent=2)
        stream.write("\n")
    return out

def check() -> dict:
    if not MANIFEST.is_file():
        raise RuntimeError("HOLD: native artifact handoff manifest not included")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = assets()
    if (data.get("schema") != "tstss.firstwake.shore-review-native-snapshot.v1"
            or data.get("source_provenance_head") != ORIGIN_HEAD
            or data.get("delivered_candidate_head") != "NOT_YET_VERIFIED_AFTER_ASSET_COMMIT"
            or data.get("status") != "SAVED_NATIVE_REVIEW_ARTIFACTS_UNMERGED_UNAPPROVED"
            or data.get("native_files") != len(expected)
            or data.get("total_bytes") != sum(x["bytes"] for x in expected)
            or data.get("files") != expected
            or data.get("content_tree_sha256") != tree_digest(expected)
            or data.get("map_sha256") != EXPECTED_MAP_HASH
            or data.get("original_map_sha256") != EXPECTED_SOURCE_HASH
            or data.get("prepared_actor_count") != 43 or data.get("review_actor_count") != 26
            or any(data.get(k) is not False for k in (
                "pie_verified", "player_controls_verified", "gpu_render_verified",
                "creator_visual_approved", "canon_authorized", "main_merge_authorized"))
            or data.get("assets_are_review_only") is not True):
        raise RuntimeError("HOLD: asset snapshot source/evidence/authority drift")
    return {"status": "SOURCE_ASSET_HASHES_PASS_NOT_NATIVE_REVALIDATION",
            "files": len(expected),
            "map_sha256": checksum(MAP), "tree_sha256": tree_digest(expected),
            "origin_head": ORIGIN_HEAD}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--snapshot", action="store_true")
    choice.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    result = snapshot() if arguments.snapshot else check()
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))
