"""Original Ender dark-copper layered hair geometry: noncanonical static lookdev.

Meters, glTF +X right, +Y face/front, +Z up. Source local origin is
an approximate skull center, not an author-approved MetaHuman fit.
No paid assets, copyrighted texture scans or character sculpt are used.
Only generates a NEW hair GLB; never writes to the user's production project.
"""
import hashlib
import json
import math
import os
import struct
from pathlib import Path

import numpy as np

OUT = Path(os.getenv("TSTSS_ENDER_HAIR_OUTPUT",
                     "C:/TSTSS_EnderHairNativeV1_20261104/private_generated"))
OUT.mkdir(parents=True, exist_ok=True)
GLB = OUT / "Ender_DarkCopper_LayeredHair_V1_NONCANONICAL.glb"
RECEIPT = OUT / "Ender_DarkCopper_LayeredHair_V1_SOURCE_PROVENANCE.json"
if GLB.exists() or RECEIPT.exists():
    raise RuntimeError("FAIL_CLOSED: refuse to replace hair source/evidence")

RNG = np.random.default_rng(20261104)
TAU = math.tau
# Anatomical dimensions are UNVERIFIED until a native MetaHuman head-bounds probe.
SKULL_RX, SKULL_RY, SKULL_RZ = 0.083, 0.103, 0.103
MATERIALS = [
    ("DeepCopperRoots", [0.125, 0.053, 0.038, 1.0], 0.85),
    ("WarmChestnutBase", [0.24, 0.095, 0.065, 1.0], 0.75),
    ("TousledAuburnBody", [0.32, 0.135, 0.078, 1.0], 0.69),
    ("CopperRimHighlights", [0.47, 0.220, 0.112, 1.0], 0.63),
    ("ShadowBrownStrands", [0.18, 0.073, 0.052, 1.0], 0.77),
]
PARTS = {name: [] for name, *_ in MATERIALS}
CATEGORIES = {}
def add_part(name, verts, faces, category):
    verts = np.asarray(verts, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.uint32)
    if not (len(verts) > 3 and len(faces) > 3 and np.isfinite(verts).all()):
        raise AssertionError("invalid mesh part")
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1)
    if np.min(area) < 1.0e-12:
        raise AssertionError("degenerate faces in " + category)
    PARTS[name].append((verts, faces))
    CATEGORIES[category] = CATEGORIES.get(category, 0) + 1

def head(azimuth, polar, radius_offset=0.0):
    """Ellipsoidal scalp surface and outward radial-normal approximation."""
    normal = np.array([math.sin(polar)*math.cos(azimuth)/SKULL_RX,
                       math.sin(polar)*math.sin(azimuth)/SKULL_RY,
                       math.cos(polar)/SKULL_RZ], dtype=float)
    normal /= np.linalg.norm(normal)
    point = np.array([SKULL_RX*math.sin(polar)*math.cos(azimuth),
                      SKULL_RY*math.sin(polar)*math.sin(azimuth),
                      SKULL_RZ*math.cos(polar)], dtype=float) + normal*radius_offset
    return point, normal

def scalp_cap():
    """Continuous ellipsoidal cap; rear nape naturally extends lower."""
    verts, faces = [], []
    rings, angular = 28, 64
    # Root cap slopes to near-temple, but longer across nape, protecting the forehead.
    for j in range(rings+1):
        u = j / rings
        for k in range(angular):
            a = k*TAU/angular
            front = max(0.0, math.sin(a))
            back = max(0.0, -math.sin(a))
            maxpolar = 1.78 - 0.29*front + 0.25*back
            p, n = head(a, 0.003 + maxpolar*u, 0.0005)
            verts.append(p)
    for j in range(rings):
        for k in range(angular):
            q = (k+1) % angular
            x = j*angular+k
            y = j*angular+q
            z = (j+1)*angular+k
            w = (j+1)*angular+q
            faces.extend([(x,z,y),(y,z,w)])
    # Close underside with a small patch only at the lower rim; surface remains review-only.
    add_part("DeepCopperRoots", verts, faces, "scalp_cap")

def clamp_unit(v):
    n = np.linalg.norm(v)
    if n < 1e-8:
        raise ValueError("zero direction")
    return v / n

def curved_lock(p0, p1, p2, p3, base_width, material, category, segments=10, sides=7):
    """Closed 3D, narrowing curved tuft. This is not a hair groom or real hairstyle fit."""
    vs, fs = [], []
    for j in range(segments+1):
        t = j/segments
        omt = 1-t
        center = (omt**3*p0 + 3*omt**2*t*p1 + 3*omt*t*t*p2 + t**3*p3)
        tangent = 3*omt*omt*(p1-p0) + 6*omt*t*(p2-p1) + 3*t*t*(p3-p2)
        tangent = clamp_unit(tangent)
        across = np.cross(tangent, np.array([0.0, 0.0, 1.0]))
        if np.linalg.norm(across) < .05:
            across = np.cross(tangent, np.array([0, 1, 0], dtype=float))
        across = clamp_unit(across)
        depth = clamp_unit(np.cross(tangent, across))
        width = base_width * (0.92 * (1.0 - t)**0.75 + 0.04)
        thickness = width * 0.38
        for k in range(sides):
            a = TAU*k/sides
            vs.append(center + width*math.cos(a)*across + thickness*math.sin(a)*depth)
    for j in range(segments):
        for k in range(sides):
            nxt = (k+1)%sides
            a=j*sides+k
            b=j*sides+nxt
            c=(j+1)*sides+k
            d=(j+1)*sides+nxt
            fs.extend([(a,b,c),(b,d,c)])
    for k in range(1,sides-1):
        fs.append((0,k+1,k))
        top=segments*sides
        fs.append((top,top+k,top+k+1))
    add_part(material, vs, fs, category)

scalp_cap()
# Individual crown and side clumps, deterministically staggered along the scalp.
# Outward volume and a clockwise crown sweep are intentional; no claim to scalp contact.
for i in range(190):
    theta = 0.13 + 1.59*math.sqrt((i + .5)/190)
    az = ((i*2.399963229728653 + .16) % TAU)
    front = max(0.0, math.sin(az))
    back = max(0.0, -math.sin(az))
    # Avoid burying the frontal eyes or uncontrolled geometry near jaw.
    if front > .60 and theta > 1.33:
        theta = 1.33 - .02*(i%5)
    root, normal = head(az, theta, .0004)
    tangent = clamp_unit(np.array([-math.sin(az), math.cos(az), .12]))
    sign = -1.0  # natural sweep toward the wearer's right
    phi = (i*0.618 + 0.3)
    spread = 0.012 + .015*math.sin(phi)**2
    drop = .008 + .015*theta + .004*(i%3)
    if theta < .63:
        drop -= .018
    if back > .65:
        drop += .009
    p0 = root
    p1 = root + normal*(.009 + spread*.3) + tangent*sign*.005 + [0,0,.004]
    p2 = root + normal*(.014 + spread*.3) + tangent*sign*(spread*.8) + [0,0,-drop*.30]
    p3 = root + normal*(.005 + spread*.38) + tangent*sign*spread + [0,0,-drop]
    width = .0042 + .0035*((i%11)/10)
    material = ["WarmChestnutBase","TousledAuburnBody","TousledAuburnBody",
                "ShadowBrownStrands","CopperRimHighlights"][i%5]
    curved_lock(p0,p1,p2,p3,width,material,"layered_crown_lock")

# Asymmetric swept fringe. Each clump starts above the upper brow and tapers.
for i in range(23):
    angle = 0.79 + (i/22)*1.55
    polar = .98 + .12*math.sin(i*.91)
    root, normal = head(angle, polar, .005)
    xshift = -.009 - .014*((i%5)/4)
    drop = .025 + .022*((i%7)/6)
    # Face forward +Y, fringe ends above eyes, not across the face.
    p0 = root
    p1 = root + np.array([xshift*.30, .010, .002])
    p2 = root + np.array([xshift*.78, .018, -drop*.48])
    p3 = root + np.array([xshift, .012, -drop])
    curved_lock(p0,p1,p2,p3,.0065+.0030*((i%5)/4),
                ["TousledAuburnBody","WarmChestnutBase",
                 "CopperRimHighlights","ShadowBrownStrands"][i%4],
                "asymmetric_fringe")

# Distinct side-flare and nape clusters prevent a featureless hemispherical helmet.
for side in (-1,1):
    for i in range(15):
        az = (.17 if side>0 else math.pi-.17) + (i%3-1)*.16
        theta=1.22 + (i//3)*.085
        root,normal=head(az,theta,.004)
        drop=.016 + .009*(i%4)
        p0=root
        p1=root+normal*.007 + [side*.004,.001,-.002]
        p2=root+normal*.016 + [side*.014,-.002,-drop*.35]
        p3=root+normal*.008 + [side*.019,-.003,-drop]
        curved_lock(p0,p1,p2,p3,.0055,
                    "WarmChestnutBase" if i%3 else "CopperRimHighlights",
                    "side_temples")
for i in range(24):
    az=math.pi+.25+(i/23)*(math.pi-.50)
    theta=1.65 + .13*((i%4)/3)
    root,normal=head(az,theta,.002)
    p0=root
    p1=root+normal*.010+[0,-.006,-.003]
    p2=root+normal*.014+[0,-.009,-.018]
    p3=root+normal*.007+[.004*math.sin(i),-.005,-.032-.007*(i%3)]
    curved_lock(p0,p1,p2,p3,.0061,"ShadowBrownStrands" if i%2 else
                "TousledAuburnBody","layered_nape")

# Export a single static mesh with separate PBR material primitives, with accurate normals.
binary=bytearray()
views,accs,primitives,glbmaterials=[],[],[],[]
mesh_summary={}
def pad4(buf, value=b"\x00"):
    while len(buf)%4:buf.extend(value)
def view(arr, target):
    pad4(binary)
    arr=np.ascontiguousarray(arr)
    offset=len(binary)
    binary.extend(arr.tobytes())
    views.append({"buffer":0,"byteOffset":offset,"byteLength":arr.nbytes,"target":target})
    return len(views)-1
def acc(arr,kind,ctype,target):
    arr=np.asarray(arr)
    ident=view(arr,target)
    a={"bufferView":ident,"componentType":ctype,"count":len(arr),"type":kind}
    if kind=="VEC3" and ctype==5126:
        a["min"]=np.min(arr,axis=0).astype(float).tolist()
        a["max"]=np.max(arr,axis=0).astype(float).tolist()
    accs.append(a)
    return len(accs)-1
allmins=[];allmaxs=[]
for name,color,rough in MATERIALS:
    meshes=PARTS[name]
    verts=[];faces=[];shift=0
    for p,f in meshes:
        verts.append(p)
        faces.append(f + shift)
        shift += len(p)
    if not verts:continue
    pos=np.concatenate(verts).astype(np.float32)
    tri=np.concatenate(faces).astype(np.uint32)
    # Smooth imported mesh shading, no normal-map dependency.
    normal=np.zeros_like(pos)
    v0,v1,v2=pos[tri[:,0]],pos[tri[:,1]],pos[tri[:,2]]
    area_normal=np.cross(v1-v0,v2-v0)
    for m in range(3):np.add.at(normal,tri[:,m],area_normal)
    mag=np.linalg.norm(normal,axis=1)
    assert np.min(mag)>1e-10,(name,float(np.min(mag)))
    normal=(normal/mag[:,None]).astype(np.float32)
    allmins.append(np.min(pos,axis=0))
    allmaxs.append(np.max(pos,axis=0))
    glbmaterials.append({
        "name":name,
        "pbrMetallicRoughness":{
            "baseColorFactor":color,
            "roughnessFactor":rough,
            "metallicFactor":0.0},
        "doubleSided":True})
    mi=len(glbmaterials)-1
    primitives.append({"attributes":{
        "POSITION":acc(pos,"VEC3",5126,34962),
        "NORMAL":acc(normal,"VEC3",5126,34962)},
        "indices":acc(tri.flatten(),"SCALAR",5125,34963),
        "material":mi,"mode":4})
    mesh_summary[name]={"parts":len(meshes),"verts":len(pos),"triangles":len(tri)}
pad4(binary)
bounds_min=np.min(np.stack(allmins),axis=0)
bounds_max=np.max(np.stack(allmaxs),axis=0)
dims=bounds_max-bounds_min
assert 0.15 < dims[0] < 0.30 and 0.15 < dims[1] < 0.35 and 0.12 < dims[2] < 0.29, dims
assert 5 == len(primitives)
assert sum(s["triangles"] for s in mesh_summary.values()) < 100000
doc={"asset":{"version":"2.0","generator":"Original TSTSS Ender Copper Hair V1; noncanonical"},
     "scene":0,"scenes":[{"nodes":[0]}],
     "nodes":[{"mesh":0,"name":"Ender_CopperHair_Review_Static"}],
     "meshes":[{"name":"Ender_CopperHair_Review_Static","primitives":primitives}],
     "accessors":accs,"bufferViews":views,"buffers":[{"byteLength":len(binary)}],
     "materials":glbmaterials,
     "extras":{"review_only":True,"source_authored":True,"creator_approved":False,
               "hair_color_lock":"provisional_dark_copper",
               "actual_head_fit_verified":False,"static_only":True,
               "gameplay_asset":False,"rigged":False,"groom":False,
               "source_reference_pixels_included":False}}
raw=json.dumps(doc,sort_keys=True,separators=(",",":")).encode("utf-8")
raw+=b" "*((-len(raw))%4)
size=12+8+len(raw)+8+len(binary)
with GLB.open("wb") as f:
    f.write(struct.pack("<4sII",b"glTF",2,size))
    f.write(struct.pack("<I4s",len(raw),b"JSON"))
    f.write(raw)
    f.write(struct.pack("<I4s",len(binary),b"BIN\x00"))
    f.write(binary)
report={"status":"ENDER_ORIGINAL_DARK_COPPER_STATIC_HAIR_V1_SOURCE_CREATED_ART_HOLD",
        "glb_path":str(GLB),"sha256":hashlib.sha256(GLB.read_bytes()).hexdigest(),
        "file_bytes":GLB.stat().st_size,"materials":[x[0] for x in MATERIALS],
        "category_counts":CATEGORIES,"triangle_total":sum(s["triangles"] for s in mesh_summary.values()),
        "bounds_min_m":bounds_min.tolist(),"bounds_max_m":bounds_max.tolist(),
        "dimensions_cm":np.round(dims*100,4).tolist(),
        "fit_to_meta_human":False,"native_render":False,"creator_approved":False,
        "fitted_goggles":False,"skeletal_mesh":False,"animation":False,
        "no_existing_assets_overwritten":True}
RECEIPT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
print(json.dumps(report,sort_keys=True,indent=2))
