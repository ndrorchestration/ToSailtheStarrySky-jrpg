#!/usr/bin/env python3
"""Evidence-scoped candidate height check from pinned PR #643 manifest.

This inspects LOOKDEV metadata, not actual UE imported bounds or approved heights.
Uses Git's blob object hash of exact raw bytes: sha1("blob N\0" + payload).
No network or mutations.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

PINNED_SOURCE_SHA = "d629faae0838fb1116c629bb8cec480899dfc9d9"
PINNED_BLOB_SHA = "b4e67081c711ef6350b6df612d21756b89b884ea"
MANIFEST_PATH = "unreal/ArtSource/Characters/Candidates/manifest.json"
EXPECTED_ORDER = ("Reson", "Aepex", "Ender", "Ionia", "Lyra")
EVIDENCE_URL = (
    "https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/"
    + PINNED_SOURCE_SHA + "/" + MANIFEST_PATH
)

def git_blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\0" + data).hexdigest()

def extract(data, expected_blob_sha=PINNED_BLOB_SHA):
    if git_blob_hash(data) != expected_blob_sha:
        raise ValueError("manifest bytes do not match pinned Git blob")
    obj = json.loads(data)
    if obj.get("status") != "UNRIGGED_LOOKDEV_CANDIDATE":
        raise ValueError("expected UNRIGGED_LOOKDEV_CANDIDATE")
    chars = obj.get("characters")
    if not isinstance(chars, list) or len(chars) != 5:
        raise ValueError("exactly five candidate records required")
    heights = {}
    for row in chars:
        if not isinstance(row, dict):
            raise ValueError("malformed candidate record")
        name = row.get("name")
        if name not in EXPECTED_ORDER or name in heights:
            raise ValueError("missing, duplicate or unexpected identity")
        height = row.get("height_m")
        if type(height) not in (int, float) or not math.isfinite(height) or height <= 0:
            raise ValueError("invalid candidate lookdev height")
        if row.get("file") != name + ".glb":
            raise ValueError("candidate mesh identity/file mismatch")
        sha = row.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("candidate mesh hash absent or malformed")
        heights[name] = height
    if set(heights) != set(EXPECTED_ORDER) or len(set(heights.values())) != 5:
        raise ValueError("identities incomplete or ties prevent strict order")
    ordered = sorted(heights, key=lambda k: heights[k], reverse=True)
    return {"schema_version": 1, "source_kind": "candidate_manifest",
            "source_sha": PINNED_SOURCE_SHA,
            "manifest_blob_sha": expected_blob_sha,
            "evidence_location": EVIDENCE_URL,
            "observations": {"height_order": ordered}}

def self_test():
    obj = {"status": "UNRIGGED_LOOKDEV_CANDIDATE",
           "characters": [{"name": n, "height_m": 2.0 - i * .1,
                           "file": n+".glb", "sha256": "a"*64}
                          for i,n in enumerate(EXPECTED_ORDER)]}
    data = json.dumps(obj).encode()
    good = extract(data, git_blob_hash(data))
    assert good["observations"]["height_order"] == list(EXPECTED_ORDER)
    for change in ("upside_down_order", "duplicate", "bad_status", "missing",
                   "nonfinite", "wrong_file", "bad_sha"):
        mutated = json.loads(data)
        entries = mutated["characters"]
        if change == "upside_down_order":
            entries[0]["height_m"] = 0.1
        elif change == "duplicate":
            entries[0]["name"] = "Lyra"
        elif change == "bad_status":
            mutated["status"] = "PRODUCTION_APPROVED"
        elif change == "missing":
            entries.pop()
        elif change == "nonfinite":
            entries[0]["height_m"] = float("nan")
        elif change == "wrong_file":
            entries[0]["file"] = "Other.glb"
        elif change == "bad_sha":
            entries[0]["sha256"] = "not-a-sha"
        payload = json.dumps(mutated).encode()
        try:
            if change == "upside_down_order":
                order = extract(payload, git_blob_hash(payload))
                assert order["observations"]["height_order"] != list(EXPECTED_ORDER)
            else:
                extract(payload, git_blob_hash(payload))
        except ValueError:
            if change != "upside_down_order":
                continue
            raise
        if change != "upside_down_order":
            raise AssertionError("invalid candidate accepted: " + change)
    try:
        extract(data, "a"*40)
    except ValueError:
        pass
    else:
        raise AssertionError("tampered pinned-source blob accepted")
    print("PASS: synthetic candidate ordering and 8 negative controls; no native art verification")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("manifest", nargs="?")
    p.add_argument("--self-test", action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.manifest:
        p.error("manifest file extracted from exactly pinned PR #643 required")
    receipt=extract(Path(args.manifest).read_bytes())
    print(json.dumps(receipt,indent=2))
    print("NOTE: only candidate lookdev metadata is source-checked; NOT canonical numerical height or native Unreal proof.")

if __name__ == "__main__":
    main()
