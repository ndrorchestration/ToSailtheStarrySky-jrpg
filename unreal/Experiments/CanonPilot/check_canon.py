#!/usr/bin/env python3
"""Advisory canon contract checker; no game engine, no network and no writes."""
import argparse
import json
import re
from pathlib import Path

KINDS = {"synthetic", "native_receipt", "not_observed", "candidate_manifest"}

def evaluate(contract, receipt):
    if contract.get("schema_version") != 1 or receipt.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    expected = contract.get("assertions")
    observed = receipt.get("observations")
    kind = receipt.get("source_kind")
    if kind not in KINDS or not isinstance(expected, dict) or not isinstance(observed, dict):
        raise ValueError("invalid contract or observation envelope")
    if set(observed) - set(expected):
        raise ValueError("unknown observation keys refused")
    if kind == "not_observed" and observed:
        raise ValueError("not_observed cannot contain observations")
    if kind in ("native_receipt", "candidate_manifest"):
        if kind == "candidate_manifest":
            if not re.fullmatch("[0-9a-f]{40}", receipt.get("manifest_blob_sha", "")):
                raise ValueError("candidate_manifest requires git manifest_blob_sha")
            if not receipt.get("evidence_location"):
                raise ValueError("candidate_manifest requires evidence_location")
    if kind == "native_receipt":
        if not re.fullmatch("[0-9a-f]{40}", receipt.get("source_sha", "")):
            raise ValueError("native_receipt requires source_sha")
        if not receipt.get("evidence_location"):
            raise ValueError("native_receipt requires evidence_location")
    results = {}
    for name, want in expected.items():
        if name not in observed:
            results[name] = "UNKNOWN"
        elif type(observed[name]) is not type(want) or observed[name] != want:
            results[name] = "FAIL_MISMATCH"
        elif kind == "synthetic":
            results[name] = "PASS_SYNTHETIC_ONLY"
        elif kind == "candidate_manifest":
            results[name] = "MATCHES_PINNED_LOOKDEV_MANIFEST_NOT_NATIVE_OR_CANON"
        elif kind == "native_receipt":
            results[name] = "MATCHES_REPORTED_NATIVE_RECEIPT_NOT_INDEPENDENTLY_VERIFIED"
        else:
            results[name] = "UNKNOWN"
    return results

def self_test(contract):
    expect = contract["assertions"]
    good = {"schema_version": 1, "source_kind": "synthetic", "observations": expect}
    result = evaluate(contract, good)
    assert set(result.values()) == {"PASS_SYNTHETIC_ONLY"}
    negative = [
        {**expect, "height_order": list(reversed(expect["height_order"]))},
        {**expect, "starting_mp_top_two": ["Lyra", "Ender"]},
        {**expect, "starting_hp_bottom_two": ["Ender", "Lyra"]},
        {**expect, "skyborne_wings": 3},
        {**expect, "orbiter_request_permitted": True},
    ]
    for bad in negative:
        result = evaluate(contract, {**good, "observations": bad})
        assert "FAIL_MISMATCH" in result.values()
    missing = evaluate(contract, {"schema_version": 1,
                                  "source_kind": "not_observed", "observations": {}})
    assert set(missing.values()) == {"UNKNOWN"}
    for obs in ({**expect, "invented": True},):
        try:
            evaluate(contract, {**good, "observations": obs})
        except ValueError:
            pass
        else:
            raise AssertionError("unknown field accepted")
    candidate = {**good, "source_kind": "candidate_manifest",
                 "manifest_blob_sha": "a"*40, "evidence_location": "git-show pinned fixture"}
    assert set(evaluate(contract, candidate).values()) == {
        "MATCHES_PINNED_LOOKDEV_MANIFEST_NOT_NATIVE_OR_CANON"}
    print("PASS: synthetic-positive, five negative controls, missing-evidence, unknown-field, candidate-source separation")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("observations", nargs="?")
    p.add_argument("--contract", default=str(Path(__file__).with_name("contract.json")))
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    contract = json.loads(Path(a.contract).read_text(encoding="utf-8"))
    if a.self_test:
        self_test(contract)
        return
    if not a.observations:
        p.error("observations file required")
    receipt = json.loads(Path(a.observations).read_text(encoding="utf-8"))
    result = evaluate(contract, receipt)
    print(json.dumps({"classification": "ADVISORY_ONLY", "results": result,
                      "source_kind": receipt["source_kind"]}, indent=2))
    if "FAIL_MISMATCH" in result.values():
        raise SystemExit(1)

if __name__ == "__main__":
    main()
