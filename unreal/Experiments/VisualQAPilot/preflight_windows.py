#!/usr/bin/env python3
"""Read-only Win64 Unreal screenshot readiness preflight.

This tool does NOT launch UE, check the renderer, produce a screenshot,
inspect hydrofoil geometry or claim visual acceptance. No environment dump.
Writes only when --report names a NEW private output file.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PINNED_PR656_HEAD = "77ee249f8a0d734eab165dcafcd16870f12f07a7"

def get_git(checkout, *args):
    try:
        proc = subprocess.run(["git", "-C", str(checkout), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=12, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None

def check(checkout, engine_root, map_file, expected_head=PINNED_PR656_HEAD):
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head or ""):
        raise ValueError("expected-head must be a 40-character lowercase Git SHA")
    checkout = Path(checkout).resolve()
    engine = Path(engine_root).resolve()
    review_map = Path(map_file).resolve()
    head = get_git(checkout, "rev-parse", "HEAD")
    status = get_git(checkout, "status", "--porcelain", "--untracked-files=no")
    project = checkout / "unreal" / "ToSailTheStarrySky.uproject"
    build_version = engine / "Engine" / "Build" / "Build.version"
    editor = engine / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
    editor_cmd = engine / "Engine" / "Binaries" / "Win64" / "UnrealEditor-Cmd.exe"
    version_ok = False
    if build_version.is_file():
        try:
            info = json.loads(build_version.read_text(encoding="utf-8"))
            version_ok = tuple(info.get(k) for k in
                               ("MajorVersion", "MinorVersion", "PatchVersion")) == (5, 8, 4)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    checks = {
        "source_sha_matches_pinned_pr656": head == expected_head,
        "tracked_source_clean": status == "",
        "uproject_exists": project.is_file(),
        "ue_5_8_4_build_version": version_ok,
        "editor_exe_present": editor.is_file(),
        "editor_cmd_exe_present": editor_cmd.is_file(),
        "explicit_review_map_exists": review_map.is_file()
                                    and review_map.suffix.lower() == ".umap",
    }
    return {
        "purpose": "POST_STRUT_SEABORNE_WINDOWS_READ_ONLY_PREFLIGHT",
        "source_target": expected_head,
        "observed_head": head if head and re.fullmatch("[0-9a-f]{40}", head) else None,
        "checks": checks,
        "ready_for_bounded_operator_review": all(checks.values()),
        "native_d3d12_capture_status": "NOT_VERIFIED",
        "real_gpu_renderer_available": "UNKNOWN",
        "two_struts_visually_present": "UNKNOWN",
        "orbiter_gate": "UNCHANGED_FAIL_CLOSED",
        "limits": "No UE launch, build, screenshot, GPU test, source attestation or art approval.",
    }

def self_test():
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    with TemporaryDirectory() as td:
        base = Path(td)
        checkout, engine = base / "src", base / "UE_5_8_4"
        (checkout / "unreal").mkdir(parents=True)
        (checkout / "unreal" / "ToSailTheStarrySky.uproject").write_text("{}", encoding="utf-8")
        version = engine / "Engine" / "Build" / "Build.version"
        version.parent.mkdir(parents=True)
        version.write_text('{"MajorVersion": 5, "MinorVersion": 8, "PatchVersion": 4}',
                           encoding="utf-8")
        editor = engine / "Engine" / "Binaries" / "Win64"
        editor.mkdir(parents=True)
        for name in ("UnrealEditor.exe", "UnrealEditor-Cmd.exe"):
            (editor / name).write_bytes(b"synthetic stub; not executable")
        map_path = base / "Review_Seaborne.umap"
        map_path.write_bytes(b"synthetic stub; not a real map")
        with patch(__name__ + ".get_git", side_effect=[PINNED_PR656_HEAD, ""]):
            ready = check(checkout, engine, map_path)
        assert ready["ready_for_bounded_operator_review"]
        assert ready["native_d3d12_capture_status"] == "NOT_VERIFIED"
        with patch(__name__ + ".get_git", side_effect=["f"*40, ""]):
            wrong_head = check(checkout, engine, map_path)
        assert not wrong_head["ready_for_bounded_operator_review"]
        with patch(__name__ + ".get_git", side_effect=[PINNED_PR656_HEAD, " M unreal/Source/a.cpp"]):
            dirty = check(checkout, engine, map_path)
        assert not dirty["ready_for_bounded_operator_review"]
        map_path.unlink()
        with patch(__name__ + ".get_git", side_effect=[PINNED_PR656_HEAD, ""]):
            missing_map = check(checkout, engine, map_path)
        assert not missing_map["ready_for_bounded_operator_review"]
        version.write_text('{"MajorVersion": 5, "MinorVersion": 8, "PatchVersion": 3}',
                           encoding="utf-8")
        with patch(__name__ + ".get_git", side_effect=[PINNED_PR656_HEAD, ""]):
            wrong_version = check(checkout, engine, map_path)
        assert not wrong_version["ready_for_bounded_operator_review"]
        try:
            check(checkout, engine, map_path, "not-a-real-sha")
        except ValueError:
            pass
        else:
            raise AssertionError("unbound expected source SHA accepted")
    print("PASS: synthetic ready state and 5 fail-closed boundary cases, no Unreal launch")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkout")
    p.add_argument("--engine-root")
    p.add_argument("--review-map-file")
    p.add_argument("--expected-head", default=PINNED_PR656_HEAD)
    p.add_argument("--report", help="NEW private JSON receipt path; never overwrite")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.checkout or not args.engine_root or not args.review_map_file:
        p.error("--checkout, --engine-root and --review-map-file are required")
    receipt = check(args.checkout, args.engine_root, args.review_map_file, args.expected_head)
    report_text = json.dumps(receipt, indent=2) + "\n"
    if args.report:
        out = Path(args.report)
        with out.open("x", encoding="utf-8") as stream:
            stream.write(report_text)
    else:
        print(report_text, end="")
    if not receipt["ready_for_bounded_operator_review"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
