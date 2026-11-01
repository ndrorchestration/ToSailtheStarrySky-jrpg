#!/usr/bin/env python3
"""Aureate Wake V2 procedural material/silhouette study based on approved art.

NOT approved 3D art. Does NOT replace ship actor assets or unlock Orbiter.
Uses the unchanged V1 mesh basis with extra naval/engine shapes and explicitly
authored ivory, gold, navy and blue-glass material slots. Unreal must validate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_aureate_body_review import (
    Surface, encode_glb, hull, bridge_dome, STATUS, SCALE,
)

APPROVED_IMAGE_SHA256 = "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13"
FILES = (
    "AureateWake_WhiteGoldHull_V2_REVIEW.glb",
    "AureateWake_BlueGlassBridge_V2_REVIEW.glb",
)
MANIFEST_NAME = "AureateWake_FidelityV2_Manifest.json"
DISPOSITION = "NONCANONICAL_PALETTE_AND_SILHOUETTE_STUDY_PENDING_NATIVE_AND_CREATOR_REVIEW"

# Material colors are *starting recipes*, not a claim of matching approved
# reference pixels under actual Unreal tone mapping/lighting.
HULL_MATERIALS = [
    {"name": "IvoryPearlEnamel_APPROVAL_STUDY",
     "pbrMetallicRoughness": {
         "baseColorFactor": [.90, .865, .755, 1.0],
         "metallicFactor": .23, "roughnessFactor": .30},
     "doubleSided": True},
    {"name": "WarmBrassFiligree_APPROVAL_STUDY",
     "pbrMetallicRoughness": {
         "baseColorFactor": [.84, .50, .20, 1.0],
         "metallicFactor": .87, "roughnessFactor": .24},
     "doubleSided": True},
    {"name": "NavyResonanceEngineering_APPROVAL_STUDY",
     "pbrMetallicRoughness": {
         "baseColorFactor": [.025, .085, .17, 1.0],
         "metallicFactor": .51, "roughnessFactor": .32},
     "emissiveFactor": [.0, .02, .075],
     "doubleSided": True},
]
BRIDGE_MATERIALS = [
    {"name": "BlueClearGeodesicGlass_APPROVAL_STUDY",
     "alphaMode": "BLEND", "doubleSided": True,
     "pbrMetallicRoughness": {
         "baseColorFactor": [.14, .49, .94, .28],
         "metallicFactor": .10, "roughnessFactor": .13}},
    {"name": "WarmBrassGlassRibs_APPROVAL_STUDY",
     "pbrMetallicRoughness": {
         "baseColorFactor": [.82, .52, .19, 1.0],
         "metallicFactor": .86, "roughnessFactor": .23},
     "doubleSided": True},
    {"name": "NavyPressureCollar_APPROVAL_STUDY",
     "pbrMetallicRoughness": {
         "baseColorFactor": [.028, .11, .19, 1.0],
         "metallicFactor": .54, "roughnessFactor": .33},
     "doubleSided": True},
]


def hull_v2() -> list[Surface]:
    ivory, gold, navy = hull()
    # Keep the previously measured wing-joint pivots, body length and the
    # approximately 8m review envelope. Details are purely visual.
    # Two deep blue engineering pods hug the aft flanks (not extra wings).
    for side in (-1, 1):
        lo, hi = sorted((side*43, side*66))
        navy.block(-285, -97, lo, hi, -15, 16)
        navy.block(-305, -281, lo+3, hi-3, -11, 12)
        # Gold spine and a subordinate line on each nacelle.
        gold.tube((-281,side*59,17),(-108,side*59,17),1.4,8)
        gold.tube((-281,side*58,-11),(-108,side*58,-11),.95,6)
        # Upper fairing contours from the aft engineering bay to the foredeck.
        gold.tube((-250,side*48,34),(-112,side*58,34),1.0,6)
        gold.tube((-112,side*58,34),(124,side*53,34),1.1,6)
        # An understated hull-underbelly side light rail, nonfunctional.
        navy.tube((-200,side*64,-20),(205,side*63,-19),3.2,8)
        # Additional longitudinal blue inset panel only, no collision.
        navy.quad((32,side*56,30),(165,side*53,29),
                  (165,side*38,31),(32,side*38,31))
    # Integrated small dark/navy bow intakes and brass detailing.
    navy.block(258,310,-26,-15,-11,6)
    navy.block(258,310,15,26,-11,6)
    for side in (-1,1):
        gold.tube((258,side*27,8),(322,side*22,5),1.15,6)
    # Existing small observation deck remains unmodified and non-walkable.
    return [ivory, gold, navy]


def dome_v2() -> list[Surface]:
    glass, gold, navy = bridge_dome()
    # Extra native-lookdev ribs and forward framing; do not imply seal integrity.
    for side in (-1,1):
        gold.tube((-70,side*39,-55),(-36,side*40,33),1.3,8)
        gold.tube((-36,side*40,33),(36,side*39,34),1.1,8)
        gold.tube((36,side*39,34),(72,side*28,-52),1.3,8)
    gold.tube((91,0,-60),(91,0,-47),1.4,8)
    return [glass,gold,navy]


def deterministic_payloads() -> dict[str, bytes]:
    return {
        FILES[0]: encode_glb("Hull", hull_v2(), HULL_MATERIALS),
        FILES[1]: encode_glb("BridgeDome", dome_v2(), BRIDGE_MATERIALS),
    }


def manifest(payloads: dict[str, bytes]) -> dict:
    return {
        "status": STATUS,
        "design_review_stage": DISPOSITION,
        "original_creator_approved_reference_sha256": APPROVED_IMAGE_SHA256,
        "source_units": "centimeters",
        "gltf_linear_units": "meters",
        "source_to_gltf_scale": SCALE,
        "axis_remap": "UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP",
        "sha256": {name: hashlib.sha256(data).hexdigest() for name,data in payloads.items()},
        "native_unreal_import": "NOT_VERIFIED",
        "material_appearance": "NOT_VERIFIED",
        "creator_3d_art_approval": "NOT_GRANTED",
        "collision_and_crew_scale": "NOT_VERIFIED",
        "orbiter_authorized": False,
        "gameplay_modified": False,
    }


def expected_files() -> dict[str, bytes]:
    payloads=deterministic_payloads()
    receipt=(json.dumps(manifest(payloads),indent=2,sort_keys=True)+"\n").encode("utf-8")
    return {**payloads, MANIFEST_NAME:receipt}


def write_or_verify(folder:Path, build:bool) -> dict:
    folder=folder.resolve()
    if build: folder.mkdir(parents=True,exist_ok=True)
    if not folder.is_dir():raise ValueError("Candidate folder does not exist")
    files=expected_files()
    for name,data in files.items():
        path=folder/name
        if path.exists():
            if not path.is_file() or path.is_symlink() or path.read_bytes()!=data:
                raise ValueError("Refuse modified or unexpected candidate: "+name)
        elif build:
            path.write_bytes(data)
        else:
            raise ValueError("Missing candidate: "+name)
    return manifest(deterministic_payloads())


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build",action="store_true")
    mode.add_argument("--verify",action="store_true")
    args=p.parse_args(argv)
    result=write_or_verify(args.output_dir, args.build)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
