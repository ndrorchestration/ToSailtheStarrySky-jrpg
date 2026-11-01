#!/usr/bin/env python3
"""Deterministic, dependency-free GLB lookdev for Aureate Wake hull + glass bridge.

Review-only. This builds new meshes; it does NOT import into UE, change the
AureateWakePreviewActor, alter gameplay, approve art, or unlock Orbiter.

Coordinates are authored in Unreal centimetres, X forward, Z up, transformed
into glTF 2.0 metre Y-up via (X, Z, -Y). Import orientation MUST be confirmed
by a native Unreal bounds-and-up-axis inspection before actor binding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

STATUS = "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"
SCALE = .01
NAMES = ("AureateWake_Hull_Lookdev.glb", "AureateWake_BridgeDome_Lookdev.glb")
MANIFEST = "AureateWake_Body_Manifest.json"


def v_add(a, b): return tuple(a[i]+b[i] for i in range(3))
def v_sub(a, b): return tuple(a[i]-b[i] for i in range(3))
def v_mul(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(a[i]*b[i] for i in range(3))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    d = math.sqrt(dot(a, a))
    if d < 1e-10: raise ValueError("Degenerate vector")
    return v_mul(a, 1/d)


class Surface:
    def __init__(self, name):
        self.name = name
        self.pos = []
        self.normal = []
        self.uv = []
        self.indices = []

    def tri(self, a, b, c):
        # glTF is right-handed: this orthogonal axis remap preserves winding.
        points = [(v[0]*SCALE, v[2]*SCALE, -v[1]*SCALE) for v in (a, b, c)]
        n = cross(v_sub(points[1], points[0]), v_sub(points[2], points[0]))
        if dot(n, n) < 1e-15: return
        n = norm(n)
        idx = len(self.pos)
        self.pos.extend(points)
        self.normal.extend([n]*3)
        self.uv.extend([(p[0]*.18, p[2]*.18) for p in points])
        self.indices.extend([idx, idx+1, idx+2])

    def quad(self, a, b, c, d):
        self.tri(a,b,c); self.tri(a,c,d)

    def tube(self, start, end, radius, sides=8, cap=True):
        axis = v_sub(end,start)
        if dot(axis,axis)<1e-6: return
        up = norm(axis)
        ref = (0,0,1) if abs(up[2])<.90 else (0,1,0)
        tangent = norm(cross(up,ref))
        bitangent = norm(cross(up,tangent))
        ring=[]
        for center in (start,end):
            ring.append([v_add(center,v_add(v_mul(tangent,radius*math.cos(2*math.pi*i/sides)),
                                           v_mul(bitangent,radius*math.sin(2*math.pi*i/sides))))
                         for i in range(sides)])
        for i in range(sides):
            j=(i+1)%sides
            self.quad(ring[0][i], ring[0][j],ring[1][j],ring[1][i])
            if cap:
                self.tri(start,ring[0][j],ring[0][i]);self.tri(end,ring[1][i],ring[1][j])

    def block(self, x0,x1,y0,y1,z0,z1):
        a=(x0,y0,z0);b=(x1,y0,z0);c=(x1,y1,z0);d=(x0,y1,z0)
        e=(x0,y0,z1);f=(x1,y0,z1);g=(x1,y1,z1);h=(x0,y1,z1)
        for q in ((d,c,b,a),(e,f,g,h),(a,b,f,e),(b,c,g,f),(c,d,h,g),(d,a,e,h)):
            self.quad(*q)


def hull():
    shell, trim, deck = Surface("GraphiteCeramicHull"),Surface("WarmBrassAccents"),Surface("AureateDeck")
    # Bounds preserve legacy preview hull envelope and existing 4 wing pivots.
    stations = [(-398,10,25),(-370,37,29),(-310,58,33),(-195,72,36),
                (-40,76,37),(155,76,36),(260,66,33),(345,37,28),(397,10,23)]
    cross_section=[(0,1),(.66,.94),(1,.56),(1,-.36),(.73,-.82),
                   (0,-1),(-.73,-.82),(-1,-.36),(-1,.56),(-.66,.94)]
    rings=[]
    for x,w,h in stations:
        rings.append([(x,w*y,-4+h*z) for y,z in cross_section])
    for one,two in zip(rings,rings[1:]):
        for i in range(len(one)):
            j=(i+1)%len(one)
            shell.quad(one[i],two[i],two[j],one[j])
    center_fwd=(399,0,-4);center_aft=(-399,0,-4)
    for i in range(len(rings[0])):
        j=(i+1)%len(rings[0])
        shell.tri(center_aft,rings[0][j],rings[0][i])
        shell.tri(center_fwd,rings[-1][i],rings[-1][j])
    # Shoulder fairings taper to the four existing support + wing-root sites.
    for x in (155,-180):
        for side in (-1,1):
            shell.block(x-33,x+33,min(side*67,side*91),max(side*67,side*91),-4,22)
            trim.tube((x,side*72,23),(x,side*107,35),2.2)
    # Elegant chine and deck highlight follow actual station widths, not a rectangle.
    for side in (-1,1):
        for i in range(len(stations)-1):
            x0,w0,h0=stations[i];x1,w1,h1=stations[i+1]
            trim.tube((x0,side*w0*.96,-4+h0*.60),(x1,side*w1*.96,-4+h1*.60),1.35)
            trim.tube((x0,side*w0*.64,-4+h0*.95),(x1,side*w1*.64,-4+h1*.95),.9)
    # Bow open deck: separate tan panel with visible brass outer rim, no invisible gameplay collision.
    deck.quad((236,-24,30),(369,-12,24),(369,12,24),(236,24,30))
    for a,b in (((236,-24,30),(369,-12,24)),((369,-12,24),(369,12,24)),
                ((369,12,24),(236,24,30)),((236,24,30),(236,-24,30))):
        trim.tube(a,b,1.6)
    # A small upper dorsal engineering spine, low enough to keep deck legibility.
    shell.block(-300,-95,-17,17,22,32)
    trim.tube((-288,0,34),(-105,0,34),1.5)
    return [shell,trim,deck]


def icosphere(subdivisions=2):
    t=(1+math.sqrt(5))/2
    vertices=[(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),
              (0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]
    vertices=[norm(v) for v in vertices]
    faces=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),
           (5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),
           (3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),
           (8,6,7),(9,8,1)]
    for _ in range(subdivisions):
        cache={}; nxt=[]
        def middle(i,j):
            key=tuple(sorted((i,j)))
            if key not in cache:
                cache[key]=len(vertices)
                vertices.append(norm(v_mul(v_add(vertices[i],vertices[j]),.5)))
            return cache[key]
        for a,b,c in faces:
            ab,bc,ca=middle(a,b),middle(b,c),middle(c,a)
            nxt.extend(((a,ab,ca),(b,bc,ab),(c,ca,bc),(ab,bc,ca)))
        faces=nxt
    return vertices,faces


def clip_upper(face):
    # Polygon cut on unit-sphere z=0; resulting panels remain triangles.
    result=[]
    for i,a in enumerate(face):
        b=face[(i+1)%len(face)];inside_a=a[2]>=-1e-10;inside_b=b[2]>=-1e-10
        if inside_a: result.append(a)
        if inside_a!=inside_b:
            u=a[2]/(a[2]-b[2]);result.append(tuple(a[k]+u*(b[k]-a[k]) for k in range(3)))
    cleaned=[]
    for p in result:
        if not cleaned or dot(v_sub(p,cleaned[-1]),v_sub(p,cleaned[-1]))>1e-12: cleaned.append(p)
    return cleaned


def bridge_dome():
    glass, struts, base=Surface("TintedGlassPanels"),Surface("BrassGeodesicFrame"),Surface("DeckAndPressureCollar")
    verts,faces=icosphere(2)
    edges={}
    def project(p):return (p[0]*94,p[1]*55,-59+p[2]*112)
    for face in faces:
        clipped=clip_upper([verts[i] for i in face])
        if len(clipped)<3: continue
        for i in range(1,len(clipped)-1):
            points=[project(p) for p in (clipped[0],clipped[i],clipped[i+1])]
            glass.tri(*points)
            for j in range(3):
                a,b=points[j],points[(j+1)%3]
                key=tuple(sorted((tuple(round(x,4) for x in a), tuple(round(x,4) for x in b))))
                if dot(v_sub(a,b),v_sub(a,b))>16: edges[key]=(a,b)
    for p,q in sorted(edges.values(),key=lambda ab:repr(ab)):
        struts.tube(p,q,1.05,6,False)
    points=[(94*math.cos(i*math.tau/48),55*math.sin(i*math.tau/48),-59) for i in range(48)]
    for i,a in enumerate(points):
        struts.tube(a,points[(i+1)%len(points)],2.4,8)
    # Visible collar, base and inward cantilever at existing bridge component origin.
    base.block(-96,96,-54,54,-72,-61)
    struts.tube((-88,-52,-59),(88,-52,-59),2.0)
    struts.tube((-88,52,-59),(88,52,-59),2.0)
    return [glass,struts,base]


MATERIALS = {
    "Hull": [
        {"name":"GraphiteCeramicHull_REVIEW","pbrMetallicRoughness":{"baseColorFactor":[.035,.11,.16,1],"metallicFactor":.48,"roughnessFactor":.36},"doubleSided":True},
        {"name":"WarmBrassAccents_REVIEW","pbrMetallicRoughness":{"baseColorFactor":[.8,.48,.16,1],"metallicFactor":.85,"roughnessFactor":.28},"doubleSided":True},
        {"name":"AureateDeck_REVIEW","pbrMetallicRoughness":{"baseColorFactor":[.56,.62,.58,1],"metallicFactor":.18,"roughnessFactor":.55},"doubleSided":True},
    ],
    "BridgeDome": [
        {"name":"TintedGlassPanels_REVIEW","alphaMode":"BLEND","doubleSided":True,"pbrMetallicRoughness":{"baseColorFactor":[.13,.62,.72,.32],"metallicFactor":.28,"roughnessFactor":.16}},
        {"name":"BrassGeodesicFrame_REVIEW","doubleSided":True,"pbrMetallicRoughness":{"baseColorFactor":[.82,.52,.22,1],"metallicFactor":.8,"roughnessFactor":.23}},
        {"name":"DeckAndPressureCollar_REVIEW","doubleSided":True,"pbrMetallicRoughness":{"baseColorFactor":[.075,.16,.20,1],"metallicFactor":.4,"roughnessFactor":.44}},
    ],
}


def encode_glb(name, surfaces, materials=None):
    blob=bytearray(); views=[]; accessors=[]; primitives=[]
    def buffer(data,target):
        while len(blob)%4:blob.append(0)
        start=len(blob);blob.extend(data)
        views.append({"buffer":0,"byteOffset":start,"byteLength":len(data),"target":target})
        return len(views)-1
    def floats(vals,width,minmax=False):
        flat=[v for group in vals for v in group]
        view=buffer(struct.pack("<"+"f"*len(flat),*flat),34962)
        accessor={"bufferView":view,"componentType":5126,"count":len(vals),"type":{2:"VEC2",3:"VEC3"}[width]}
        if minmax:
            accessor["min"]=[min(row[i] for row in vals) for i in range(width)]
            accessor["max"]=[max(row[i] for row in vals) for i in range(width)]
        accessors.append(accessor);return len(accessors)-1
    for idx,s in enumerate(surfaces):
        if not s.indices:raise RuntimeError("Missing geometry section "+s.name)
        pos=floats(s.pos,3,True);norms=floats(s.normal,3);uv=floats(s.uv,2)
        iview=buffer(struct.pack("<"+"I"*len(s.indices),*s.indices),34963)
        accessors.append({"bufferView":iview,"componentType":5125,"count":len(s.indices),"type":"SCALAR","min":[0],"max":[max(s.indices)]})
        primitives.append({"attributes":{"POSITION":pos,"NORMAL":norms,"TEXCOORD_0":uv},
                           "indices":len(accessors)-1,"material":idx,"mode":4})
    while len(blob)%4:blob.append(0)
    data={"asset":{"version":"2.0","generator":"TSTSS deterministic Python review GLB"},
          "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"name":name,"mesh":0}],
          "meshes":[{"name":name,"primitives":primitives}],"materials":MATERIALS[name] if materials is None else materials,
          "accessors":accessors,"bufferViews":views,"buffers":[{"byteLength":len(blob)}],
          "extras":{"authority":STATUS,"source_units":"centimeters","gltf_linear_units":"meters",
                    "sourceToGltfScale":SCALE,"axisRemap":"UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP"}}
    js=json.dumps(data,separators=(',',':'),sort_keys=True,allow_nan=False).encode('utf-8')
    js+=b' ' * (-len(js)%4)
    packed=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(blob))
    return packed+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(blob),b'BIN\0')+blob


def build_payloads():
    return {NAMES[0]:encode_glb("Hull",hull()),NAMES[1]:encode_glb("BridgeDome",bridge_dome())}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--build',action='store_true')
    p.add_argument('--verify',action='store_true')
    args=p.parse_args(argv)
    if args.build==args.verify:p.error("select exactly one of --build and --verify")
    output=args.output_dir.resolve()
    if args.verify and not output.is_dir():p.error("Missing output directory")
    payloads=build_payloads()
    digest={n:hashlib.sha256(d).hexdigest() for n,d in payloads.items()}
    receipt={"status":STATUS,"source_units":"centimeters","gltf_linear_units":"meters",
             "source_to_gltf_scale":SCALE,"axis_remap":"UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP",
             "sha256":digest,"binding":"UNAUTHORIZED_PENDING_NATIVE_IMPORT_AND_CREATOR_REVIEW",
             "orbiter_authorized":False,"gameplay_modified":False}
    manifest=(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode('utf-8')
    files={**payloads,MANIFEST:manifest}
    if args.build:
        output.mkdir(parents=True,exist_ok=True)
        for n,blob in files.items():
            if (output/n).exists() and (output/n).read_bytes()!=blob:
                raise RuntimeError("Existing generated file differs; refusing overwrite: "+n)
        for n,blob in files.items():
            if not (output/n).exists(): (output/n).write_bytes(blob)
    else:
        for n,blob in files.items():
            if not (output/n).is_file() or (output/n).read_bytes()!=blob:
                raise RuntimeError("Generated input changed: "+n)
    print(json.dumps({"status":"DETERMINISTIC_REVIEW_GLBS_PASS_NOT_NATIVE_IMPORT",**receipt},indent=2))


if __name__=='__main__':main()
