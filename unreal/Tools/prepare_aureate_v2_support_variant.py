#!/usr/bin/env python3
"""Prepare an isolated, NONCANONICAL Aureate V2 wing-root support variant.

Never modifies the checked out V2 generator, canonical assets, Unreal Editor
project or approved image. Fails unless the two source files match precisely.
This is a small art/geometry hypothesis, NOT a proposed final attachment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

BASE_SOURCE_SHA = {
    "build_aureate_body_review.py": "44aaaa1bfcd87b16be283c3af100bb4b67b715a87dbe6c26b13de09ecdf22e90",
    "build_aureate_fidelity_v2.py": "65e9d374ebffc08cea99ae6b00f75c7dd4ffd314db2965fb8853f61d483f75a4",
}
BASELINE_HULL_SHA = "efed53b0b1847646d675bb2efe30dbb9af1aaeafb3cbf2e2ef314bb697cb2388"
BASELINE_BRIDGE_SHA = "b9a5e43ad6759f4f06e1d3634c80c74616307d267de5f3330b04382cf9e822d1"
BASE_V2_SOURCE_HEAD = "cc58d518ca397158df27be366e4dc506a84497c9"
BASE_SUPPORT_RECIPE = "trim.tube((x,side*72,23),(x,side*107,35),2.2)"
EXPERIMENTAL_SUPPORT_RECIPE = "trim.tube((x,side*72,21),(x,side*101,31),1.6)"
HULL_FILE = "AureateWake_WhiteGoldHull_V2_REVIEW.glb"
BRIDGE_FILE = "AureateWake_BlueGlassBridge_V2_REVIEW.glb"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare(source_dir: Path, output_dir: Path):
    if output_dir.exists():
        raise ValueError("Review output already exists; refusing overwrite")
    source_dir = source_dir.resolve()
    originals = {}
    for name, expected in BASE_SOURCE_SHA.items():
        path = source_dir / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or symbolic link V2 generator: " + name)
        blob=path.read_bytes()
        if digest(blob) != expected:
            raise ValueError("V2 generator differs from reviewed exact source: " + name)
        originals[name]=blob
    text=originals["build_aureate_body_review.py"].decode("utf-8")
    if text.count(BASE_SUPPORT_RECIPE) != 1:
        raise ValueError("Expected single exact V2 support recipe")
    output_dir.mkdir(parents=True)
    candidate_source=output_dir / "generator_copy"
    candidate_source.mkdir()
    modified=text.replace(BASE_SUPPORT_RECIPE, EXPERIMENTAL_SUPPORT_RECIPE)
    (candidate_source/"build_aureate_body_review.py").write_text(modified,encoding="utf-8")
    (candidate_source/"build_aureate_fidelity_v2.py").write_bytes(
        originals["build_aureate_fidelity_v2.py"])
    original_dir=output_dir/"baseline"
    candidate_dir=output_dir/"experimental_support"
    env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"}
    generator=source_dir/"build_aureate_fidelity_v2.py"
    subprocess.run([sys.executable,"-B",str(generator),"--build",
                    "--output-dir",str(original_dir)],check=True,env=env,
                   capture_output=True,text=True)
    for name, expected in ((HULL_FILE,BASELINE_HULL_SHA),
                           (BRIDGE_FILE,BASELINE_BRIDGE_SHA)):
        if digest((original_dir/name).read_bytes())!=expected:
            raise ValueError("Regenerated V2 original artifact SHA mismatch: "+name)
    subprocess.run([sys.executable,"-B",str(candidate_source/
                    "build_aureate_fidelity_v2.py"),"--build",
                    "--output-dir",str(candidate_dir)],check=True,env=env,
                   capture_output=True,text=True)
    if (candidate_dir/BRIDGE_FILE).read_bytes() != (original_dir/BRIDGE_FILE).read_bytes():
        raise ValueError("Candidate accidentally changed geodesic bridge")
    if (candidate_dir/HULL_FILE).read_bytes() == (original_dir/HULL_FILE).read_bytes():
        raise ValueError("Candidate hull geometry unexpectedly unchanged")
    receipt={
        "authority":"NONCANONICAL_ROOT_SUPPORT_DIAGNOSTIC_DO_NOT_IMPORT_AS_ART",
        "base_v2_source_head":BASE_V2_SOURCE_HEAD,
        "base_source_shas":BASE_SOURCE_SHA,
        "original_support_recipe":BASE_SUPPORT_RECIPE,
        "experiment_support_recipe":EXPERIMENTAL_SUPPORT_RECIPE,
        "original_mesh_sha256":{
            "hull":BASELINE_HULL_SHA,"bridge":BASELINE_BRIDGE_SHA},
        "candidate_mesh_sha256":{
            "hull":digest((candidate_dir/HULL_FILE).read_bytes()),
            "bridge":digest((candidate_dir/BRIDGE_FILE).read_bytes())},
        "mutations":"ONLY support-tube endpoint/path/radius in isolated generator copy",
        "approval":"NOT_GRANTED",
        "orbiter_authorized":False,
        "structural_mount_integrity":"UNVERIFIED",
        "swept_clearance":"UNVERIFIED",
        "rule":"An apparently improved clearance does NOT certify attachment strength or final art",
    }
    (output_dir/"candidate_recipe_receipt.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(args.source_dir,args.output_dir),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
