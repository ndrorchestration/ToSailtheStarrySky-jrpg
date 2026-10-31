#!/usr/bin/env python3
"""Offline authored-lookdev hull-to-wing telescoping support, one 100-cm +X strut.

Unreal actor duplicates this one StaticMesh into four independently scaled visual
hull-to-root links. Review-only, not a load-bearing or seaworthy hinge simulation.
Zero third-party dependencies. Uses the same GLB coordinate conversion as the
corrected Aureate Wake wing generator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

import author_aureate_wing_glb as wing

STATUS = "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"
NOMINAL_LENGTH_CM = 100.0
FILES = ("AureateWake_RootSupport_Lookdev.glb", "AureateWake_RootSupport_Manifest.json")


def add_tube(surface, x0, x1, radius, *, y=0.0, z=0.0, sides=16):
    """One capped, closed, constant-radius machined support segment."""
    if not (0 <= x0 < x1 <= NOMINAL_LENGTH_CM and radius > 0 and sides >= 8):
        raise ValueError("Invalid support tube")
    offset = len(surface["positions"])
    for x in (x0, x1):
        for j in range(sides):
            t = 2 * wing.math.pi * j / sides
            wing.vertex(surface, (x, y + radius * wing.math.cos(t),
                                  z + radius * wing.math.sin(t)), (x/NOMINAL_LENGTH_CM,j/sides))
    for j in range(sides):
        k = (j+1) % sides
        a,b,c,d = offset+j,offset+k,offset+sides+j,offset+sides+k
        surface["faces"].extend(((a,b,d),(a,d,c)))
    start = wing.vertex(surface, (x0,y,z))
    end = wing.vertex(surface, (x1,y,z))
    for j in range(sides):
        k=(j+1)%sides
        surface["faces"].extend(((start,offset+k,offset+j),
                                  (end,offset+sides+j,offset+sides+k)))


def build_surfaces():
    body = wing.make_surface("structural_alloy_sleeve")
    add_tube(body, 0, 100, 4.75, sides=24)
    # Nested machined collar sleeves; entire length is local +X from hull.
    collars = wing.make_surface("four_gilded_couplers")
    for a,b,r in ((0,11,8.0),(12,16,5.75),(45,50,6.25),(88,100,7.8)):
        add_tube(collars,a,b,r,sides=24)
    light = wing.make_surface("four_lumen_filaments")
    for y,z in ((5.0,0.0),(-5.0,0.0),(0.0,5.0),(0.0,-5.0)):
        add_tube(light,17,87,.48,y=y,z=z,sides=10)
    for piece in (body,collars,light):
        wing.orient_manifold(piece)
    return [body,collars,light]


def serialize_glb(document, original):
    # Keep the generator's validated binary buffer and replace only the JSON
    # metadata/material descriptors. Deterministic JSON encoding and 4B padding.
    json_length = struct.unpack_from("<I",original,12)[0]
    binary_chunk = original[20+json_length:]
    encoded = json.dumps(document,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    encoded += b" " * (-len(encoded)%4)
    size = 12+8+len(encoded)+len(binary_chunk)
    return (struct.pack("<4sII",b"glTF",2,size)+
            struct.pack("<I4s",len(encoded),b"JSON")+encoded+binary_chunk)


def build():
    pieces = build_surfaces()
    # Embedded swatch is unused; no external texture dependency.
    swatch = wing.png_rgba(4,4,bytes([150,184,195,255])*16)
    original,doc = wing.make_glb(pieces,swatch)
    doc["nodes"][0]["name"] = "AureateWake_RootSupport_OneStrut_REVIEW"
    doc["meshes"][0]["name"] = "HullToWing_TelescopingStrut_REVIEW"
    doc["materials"] = [
      {"name":"M_Root_Strut_BlueSteel_REVIEW","doubleSided":False,
       "pbrMetallicRoughness":{"baseColorFactor":[.22,.29,.37,1.0],
                              "metallicFactor":.83,"roughnessFactor":.28}},
      {"name":"M_Root_Coupler_Brass_REVIEW","doubleSided":False,
       "pbrMetallicRoughness":{"baseColorFactor":[.70,.47,.19,1.0],
                              "metallicFactor":.88,"roughnessFactor":.24}},
      {"name":"M_Root_Trace_Lumen_REVIEW","doubleSided":False,
       "emissiveFactor":[.08,.48,.67],
       "pbrMetallicRoughness":{"baseColorFactor":[.09,.64,.79,1.0],
                              "metallicFactor":.12,"roughnessFactor":.21}}
    ]
    doc["extras"] = {
        "authority": STATUS, "sourceUnits":"centimeters",
        "gltfLinearUnits":"meters","sourceToGltfScale":.01,
        "strutLengthCm":NOMINAL_LENGTH_CM,
        "rootAxis":"Unreal +X", "integration":"four support components, not wings",
        "physics":"none","orbiter":"not unlocked"
    }
    result=serialize_glb(doc,original)
    report={
        "status":STATUS,"source_units":"centimeters",
        "gltf_linear_units":"meters","source_to_gltf_scale":.01,
        "nominal_length_cm":NOMINAL_LENGTH_CM,
        "purpose":"four review-only hull-to-wing-root visual struts",
        "topology":[{"name":p["name"],"vertices":len(p["positions"]),
                     "triangles":len(p["faces"])} for p in pieces],
        "limits":["No structural simulation, dynamic stress or vessel watertightness",
                  "No native Unreal import/render/visual acceptance",
                  "No independently approved materials or hull design",
                  "Never introduce a fifth wing or unlock the Moon Bridge"],
        "sha256":{FILES[0]:hashlib.sha256(result).hexdigest()}}
    return result,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args()
    glb,receipt=build()
    print(json.dumps(receipt,indent=2))
    if args.validate_only: return
    target=args.output_dir.resolve()
    if target.exists() and any(target.iterdir()):
        parser.exit(1,"ROOT SUPPORT HOLD: refusing overwrite of populated output directory\n")
    target.mkdir(parents=True,exist_ok=True)
    (target/FILES[0]).write_bytes(glb)
    (target/FILES[1]).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
