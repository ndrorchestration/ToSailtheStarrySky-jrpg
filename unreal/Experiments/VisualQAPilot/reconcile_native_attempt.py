#!/usr/bin/env python3
"""Bounded cross-check of UE text logs against a local native attempt receipt.

Read only. Text log matching is NOT cryptographic engine attestation and does
not prove an actual screenshot or art acceptance. No process interactions.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

PINNED_PR656 = "77ee249f8a0d734eab165dcafcd16870f12f07a7"
BUILD_TARGET = "ToSailTheStarrySkyEditor Win64 Development"
BUILD_SUCCESS = re.compile(r"(?m)^Result: Succeeded\s*$")
D3D12_INIT = "LogD3D12RHI: Display: Creating D3D12 RHI"
SCREENSHOT_EVENT = "High resolution screenshot saved as"
MAX_LOG = 24 * 1024 * 1024

def read_log(path):
    raw = Path(path).read_bytes()
    if not raw or len(raw) > MAX_LOG:
        raise ValueError("empty or oversized Unreal log")
    return raw.decode("utf-8", errors="replace"), hashlib.sha256(raw).hexdigest()

def analyze(build_log, render_log, receipt, expected_source=PINNED_PR656,
            external_operator_stop=False):
    if not isinstance(receipt, dict) or receipt.get("source_sha") != expected_source:
        raise ValueError("source receipt not bound to required exact PR head")
    if receipt.get("review_only") is not True:
        raise ValueError("source receipt not marked review-only")
    if type(receipt.get("child_pid")) is not int or receipt["child_pid"] <= 0:
        raise ValueError("positive capture child PID required")
    native_build = BUILD_TARGET in build_log and bool(BUILD_SUCCESS.search(build_log))
    native_d3d12 = D3D12_INIT in render_log
    shot_logged = SCREENSHOT_EVENT in render_log
    statements = {
        "build_log_result_succeeded": native_build,
        "d3d12_rhi_in_native_log": native_d3d12,
        "native_screenshot_log_event": shot_logged,
    }
    conflicts = [key for key, value in statements.items()
                 if receipt.get(key) is not value]
    if shot_logged:
        # A textual "saved" message alone does not bind the bytes or timing.
        screenshot = "SCREENSHOT_LOG_EVENT_ONLY__ACTUAL_PNG_AND_VISUAL_REVIEW_REQUIRED"
    else:
        screenshot = "NOT_CAPTURED__NO_NATIVE_SCREENSHOT_EVENT"
        if receipt.get("screenshot_path") is not None or receipt.get("screenshot_sha256") is not None:
            conflicts.append("screenshot_path_or_digest_without_log_event")
    stop_status = "NOT_ESTABLISHED_FROM_LOCAL_RECEIPT"
    if external_operator_stop:
        stop_status = "EXTERNAL_OPERATOR_STOP_RECORDED"
        if receipt.get("isolated_child_force_stopped") is False:
            conflicts.append("operator_stopped_child_but_original_receipt_says_false")
    return {
        "source_head": expected_source,
        "native_build": "LOG_REPORTS_SUCCESS__NOT_INDEPENDENTLY_ATTESTED" if native_build
                        else "NO_SUCCESS_LOG_PROOF",
        "d3d12_initialization": "LOG_REPORTS_D3D12_INIT" if native_d3d12 else "NOT_PROVEN",
        "post_strut_screenshot": screenshot,
        "two_struts_visually_verified": False,
        "stop_provenance": stop_status,
        "receipt_contradictions": conflicts,
        "independent_art_approval": "NOT_ESTABLISHED",
        "orbiter_gate": "UNCHANGED_FAIL_CLOSED",
        "evidence_class": "READ_ONLY_LOCAL_LOG_CROSS_CHECK_NOT_RUNTIME_ATTESTATION",
    }

def self_test():
    build = "Running UnrealBuildTool: " + BUILD_TARGET + "\n[5/6] Link UnrealEditor-ToSailTheStarrySky.dll\nResult: Succeeded\n"
    render = "[00] " + D3D12_INIT + " with Max Feature Level SM5\n"
    receipt = {
        "source_sha": PINNED_PR656, "review_only": True, "child_pid": 24556,
        "build_log_result_succeeded": True, "d3d12_rhi_in_native_log": True,
        "native_screenshot_log_event": False, "screenshot_path": None,
        "screenshot_sha256": None, "isolated_child_force_stopped": False,
    }
    positive = analyze(build, render, receipt, external_operator_stop=True)
    assert positive["native_build"].startswith("LOG_REPORTS_SUCCESS")
    assert positive["post_strut_screenshot"].startswith("NOT_CAPTURED")
    assert positive["receipt_contradictions"] == [
        "operator_stopped_child_but_original_receipt_says_false"]
    no_build = analyze(build.replace("Succeeded", "Failed"), render, receipt)
    assert no_build["native_build"] == "NO_SUCCESS_LOG_PROOF"
    assert "build_log_result_succeeded" in no_build["receipt_contradictions"]
    no_renderer = analyze(build, "", receipt)
    assert no_renderer["d3d12_initialization"] == "NOT_PROVEN"
    assert "d3d12_rhi_in_native_log" in no_renderer["receipt_contradictions"]
    shot = analyze(build, render + SCREENSHOT_EVENT, receipt)
    assert shot["post_strut_screenshot"].startswith("SCREENSHOT_LOG_EVENT_ONLY")
    assert "native_screenshot_log_event" in shot["receipt_contradictions"]
    altered = dict(receipt, source_sha="f"*40)
    try:
        analyze(build, render, altered)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong head accepted")
    altered = dict(receipt, screenshot_path="C:/untrusted-filename.png")
    assert "screenshot_path_or_digest_without_log_event" in analyze(
        build, render, altered)["receipt_contradictions"]
    print("PASS: 6 synthetic native-log/receipt reconciliation controls; no actual render")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--build-log")
    p.add_argument("--render-log")
    p.add_argument("--attempt-receipt")
    p.add_argument("--expected-source", default=PINNED_PR656)
    p.add_argument("--external-operator-stop", action="store_true",
                   help="Operator provides separate stop evidence; never infer from receipt")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    if not (a.build_log and a.render_log and a.attempt_receipt):
        p.error("--build-log, --render-log and --attempt-receipt required")
    b, bhash = read_log(a.build_log)
    r, rhash = read_log(a.render_log)
    receipt = json.loads(Path(a.attempt_receipt).read_text(encoding="utf-8-sig"))
    result = analyze(b, r, receipt, a.expected_source, a.external_operator_stop)
    result["build_log_sha256"] = bhash
    result["d3d12_log_sha256"] = rhash
    print(json.dumps(result, indent=2))
    if result["receipt_contradictions"] or "NOT_CAPTURED" in result["post_strut_screenshot"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
