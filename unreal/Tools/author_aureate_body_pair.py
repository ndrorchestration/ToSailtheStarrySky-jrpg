#!/usr/bin/env python3
"""Deterministic, NONCANONICAL Aureate Wake hull+bridge GLBs (pure Python).

The original approved four-form illustration is a visual TARGET, not an
authorization to call these procedural meshes canonical. Source axes are
Unreal +X forward, +Y port/starboard, +Z up in centimeters; GLB uses meters
and glTF +Y up through the already-tested wing serializer.

Two independent meshes intended ONLY for explicitly allowlisted review
folders. No collision, animation, story state, Orbiter unlock or UE import.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

import author_aureate_wing_glb as wing

STATUS = "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"
HULL = "AureateWake_HullCandidateV1.glb"
BRIDGE = "AureateWake_BridgeDomeCandidateV1.glb"
MANIFEST = "AureateWake_BodyPair_Manifest.json"
FILES = (HULL, BRIDGE, MANIFEST)
DESTINATIONS = {
    HULL: "/Game/TSTSS/Review/ShipArt/HullCandidateV1",
    BRIDGE: "/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1",
}


def box(surface, low, high):
    """Closed 12-triangle box with explicit corners; no zero-thickness deck."""
    lx, ly, lz = low
    hx, hy, hz = high
    if not lx < hx or not ly < hy or not lz < hz:
        raise ValueError("Degenerate deck")
    pts = [(lx,ly,lz),(hx,ly,lz),(hx,hy,lz),(lx,hy,lz),
           (lx,ly,hz),(hx,ly,hz),(hx,hy,hz),(lx,hy,hz)]
    offset = len(surface["positions"])
    for p in pts:
        wing.vertex(surface, p)
    for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,1,5,4),
                    (1,2,6,5),(2,3,7,6),(3,0,4,7)):
        surface["faces"].extend(((offset+a,offset+b,offset+c),
                                 (offset+a,offset+c,offset+d)))


def hull_profile(t):
    # Tapered stern and noticeably pointed forward bow.
    taper = max(0.0, math.sin(math.pi * t))
    breadth = 2.8 + 100.0 * taper ** 0.75
    depth = 5.0 + 52.0 * taper ** 0.55
    return breadth, depth


def curved_hull():
    surface = wing.make_surface("pearlescent_continuous_hull_REVIEW")
    rings = 48
    sides = 32
    start, end = -480.0, 560.0
    for i in range(rings + 1):
        t = i / rings
        x = start + (end-start)*t
        breadth, depth = hull_profile(t)
        for j in range(sides):
            theta = math.tau * j / sides
            wing.vertex(surface, (x, breadth*math.cos(theta),
                                  depth*math.sin(theta) - 4.0),
                        (t, j/sides))
    for i in range(rings):
        a, b = i*sides, (i+1)*sides
        for j in range(sides):
            k = (j+1) % sides
            surface["faces"].extend(((a+j, b+j, b+k),(a+j,b+k,a+k)))
    for x, last in ((start, False),(end, True)):
        center = wing.vertex(surface, (x,0.0,-4.0))
        offset = (rings if last else 0)*sides
        for j in range(sides):
            k=(j+1)%sides
            if last:
                surface["faces"].append((center,offset+j,offset+k))
            else:
                surface["faces"].append((center,offset+k,offset+j))
    wing.orient_manifold(surface)
    return surface


def hull_gilding():
    surface = wing.make_surface("brass_keel_and_sheerlines_REVIEW")
    for side in (-1,1):
        rail=[]
        for i in range(65):
            t=.04+.92*i/64
            breadth,depth=hull_profile(t)
            rail.append((-480+1040*t, side*breadth*.90,
                         depth*.31 - 4.0))
        wing.add_vein_path(surface, rail, 1.5, sides=9)
    keel=[]
    for i in range(65):
        t=.025+.95*i/64
        _,depth=hull_profile(t)
        keel.append((-480+1040*t,0.0,-depth-4.0))
    wing.add_vein_path(surface,keel,2.4,sides=9)
    wing.orient_manifold(surface)
    return surface


def open_foredeck():
    surface = wing.make_surface("azure_open_foredeck_REVIEW")
    # Raised, open forward walking deck; the bridge is a separate actor mesh.
    box(surface,(208.0,-48.0,54.0),(479.0,48.0,61.0))
    # Centerline inlaid panel, close to the bridge's forward threshold.
    box(surface,(229.0,-14.0,61.0),(441.0,14.0,63.5))
    wing.orient_manifold(surface)
    return surface


def canopy_glazing():
    surface=wing.make_surface("pale_cyan_panorama_glass_REVIEW")
    radial=32
    layers=13
    rx,ry,rz=113.0,91.0,148.0
    for i in range(layers+1):
        theta=(math.pi/2-.022)*i/layers
        for j in range(radial):
            az=math.tau*j/radial
            wing.vertex(surface,(rx*math.cos(theta)*math.cos(az),
                                 ry*math.cos(theta)*math.sin(az),
                                 rz*math.sin(theta)),
                        (j/radial,i/layers))
    for i in range(layers):
        start=i*radial
        end=(i+1)*radial
        for j in range(radial):
            k=(j+1)%radial
            surface["faces"].extend(((start+j,start+k,end+k),
                                     (start+j,end+k,end+j)))
    tip=wing.vertex(surface,(0.,0.,rz))
    last=layers*radial
    underside=wing.vertex(surface,(0.,0.,0.))
    for j in range(radial):
        k=(j+1)%radial
        surface["faces"].append((last+j,last+k,tip))
        surface["faces"].append((j,underside,k))
    wing.orient_manifold(surface)
    return surface


def canopy_geodesic_ribs():
    surface=wing.make_surface("golden_panorama_geodesic_truss_REVIEW")
    rx,ry,rz=113.0,91.0,148.0
    spokes=16
    for j in range(spokes):
        az=math.tau*j/spokes
        curve=[]
        for k in range(15):
            theta=(math.pi/2)*k/14
            curve.append((rx*math.cos(theta)*math.cos(az),
                          ry*math.cos(theta)*math.sin(az),
                          rz*math.sin(theta)))
        wing.add_vein_path(surface,curve,1.5,sides=7)
        # Diagonals across alternate panels produce recognizable triangulation.
        if j%2==0:
            azi=math.tau*(j+1)/spokes
            for low,high in ((.11,.37),(.38,.66)):
                p=(rx*math.cos(low)*math.cos(az),
                   ry*math.cos(low)*math.sin(az),rz*math.sin(low))
                q=(rx*math.cos(high)*math.cos(azi),
                   ry*math.cos(high)*math.sin(azi),rz*math.sin(high))
                wing.add_vein_path(surface,[p,q],1.0,sides=7)
    for theta in (.05,.38,.70):
        ring=[]
        for j in range(65):
            az=math.tau*j/64
            ring.append((rx*math.cos(theta)*math.cos(az),
                         ry*math.cos(theta)*math.sin(az),
                         rz*math.sin(theta)))
        wing.add_vein_path(surface,ring,1.55,sides=7)
    wing.orient_manifold(surface)
    return surface


def canopy_base():
    surface=wing.make_surface("ivory_canopy_lower_collar_REVIEW")
    box(surface,(-119.,-94.,-7.),(119.,94.,0.))
    wing.orient_manifold(surface)
    return surface


def replace_material_document(raw, document, *, kind, materials, expected_cm):
    if len(materials) != 3 or len(document["meshes"][0]["primitives"]) != 3:
        raise ValueError("Expected exactly three reviewed surface sections")
    document["materials"]=materials
    document["nodes"][0]["name"]="AureateWake_"+kind+"_REVIEW"
    document["meshes"][0]["name"]=kind+"_NONCANONICAL"
    document["asset"]["generator"]="TSTSS offline two-piece ship body candidate"
    document["extras"]={
        "authority":STATUS,
        "sourceUnits":"centimeters","gltfLinearUnits":"meters",
        "sourceToGltfScale":.01,"sourceAxis":"Unreal +X forward +Z up",
        "target":"Isolated UE 5.8.4 reviewer StaticMesh only",
        "noGameplayOrCollision":True,"orbiter":"locked",
        "approximateDimensionsCm":expected_cm,
        "approvedArt":"reference-only; procedural mesh NOT approved",
    }
    old_json_size=struct.unpack_from("<I",raw,12)[0]
    remaining=raw[20+old_json_size:]
    data=json.dumps(document,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    data+=b" "*(-len(data)%4)
    size=12+8+len(data)+len(remaining)
    result=(struct.pack("<4sII",b"glTF",2,size)
            +struct.pack("<I4s",len(data),b"JSON")+data+remaining)
    return result


def make_pair():
    swatch=wing.png_rgba(4,4,bytes([225,213,190,255])*16)
    hull_surfaces=[curved_hull(),hull_gilding(),open_foredeck()]
    bridge_surfaces=[canopy_glazing(),canopy_geodesic_ribs(),canopy_base()]
    hull_raw,hull_doc=wing.make_glb(hull_surfaces,swatch)
    bridge_raw,bridge_doc=wing.make_glb(bridge_surfaces,swatch)
    hull_materials=[
        {"name":"M_WhitePearl_Hull_REVIEW","doubleSided":False,
         "pbrMetallicRoughness":{"baseColorFactor":[.88,.84,.72,1.],
             "metallicFactor":.28,"roughnessFactor":.35}},
        {"name":"M_GoldSheerlines_REVIEW","doubleSided":False,
         "pbrMetallicRoughness":{"baseColorFactor":[.71,.46,.19,1.],
             "metallicFactor":.89,"roughnessFactor":.28}},
        {"name":"M_AzureForedeck_REVIEW","doubleSided":False,
         "pbrMetallicRoughness":{"baseColorFactor":[.16,.37,.51,1.],
             "metallicFactor":.40,"roughnessFactor":.30}},
    ]
    bridge_materials=[
        {"name":"M_CyanPanoramicGlass_REVIEW","doubleSided":True,"alphaMode":"BLEND",
         "pbrMetallicRoughness":{"baseColorFactor":[.30,.73,.84,.34],
             "metallicFactor":.12,"roughnessFactor":.12}},
        {"name":"M_GeodesicBrassFrame_REVIEW","doubleSided":False,
         "pbrMetallicRoughness":{"baseColorFactor":[.71,.49,.20,1.],
             "metallicFactor":.88,"roughnessFactor":.25}},
        {"name":"M_IvoryBridgeCollar_REVIEW","doubleSided":False,
         "pbrMetallicRoughness":{"baseColorFactor":[.85,.80,.71,1.],
             "metallicFactor":.22,"roughnessFactor":.33}},
    ]
    pair={
        HULL:replace_material_document(hull_raw,hull_doc,kind="HullCandidateV1",
                                       materials=hull_materials,expected_cm=[1040,206,120]),
        BRIDGE:replace_material_document(bridge_raw,bridge_doc,kind="BridgeDomeCandidateV1",
                                         materials=bridge_materials,expected_cm=[238,188,155]),
    }
    receipt={
        "status":STATUS,"intent":"Review-only body candidate pair, NOT approved art",
        "source_units":"centimeters","gltf_linear_units":"meters",
        "source_to_gltf_scale":.01,"parts":list(pair),
        "approved_reference_sha256":"03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13",
        "destinations":DESTINATIONS,
        "materials_per_part":3,
        "sha256":{name:hashlib.sha256(data).hexdigest() for name,data in pair.items()},
        "limits":["No native UE import/render","No creator art acceptance",
                  "No pressure hull or glass simulation","No hydrofoil buoyancy",
                  "No authored wing swept collision proof","Orbiter locked"],
    }
    return pair,receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args(argv)
    pair,receipt=make_pair()
    print(json.dumps(receipt,indent=2))
    if args.validate_only:return
    out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        parser.exit(1,"BODY PAIR HOLD: refusing overwrite of populated output folder\n")
    out.mkdir(parents=True,exist_ok=True)
    for name,blob in pair.items():
        (out/name).write_bytes(blob)
    (out/MANIFEST).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
