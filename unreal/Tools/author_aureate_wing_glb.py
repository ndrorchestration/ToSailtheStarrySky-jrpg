#!/usr/bin/env python3
"""Deterministic authored-lookdev Aureate Wake dragonfly wing asset, glTF 2.0 GLB.

Authored source dimensions are centimeters in Unreal +X/+Y/+Z coordinates.
glTF 2.0 encodes positions in meters and +Y up; position export converts cm
to meters while normals remain unit vectors. Inspect imported cm scale in Unreal. No in-game
physics, unlock or creator-art approval is conferred by this review asset.
Pure Python standard library: offline, zero cost, no remote dependencies.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

SPAN = 280.0
WIDTH = 105.0
SEGMENTS = 72
PBR_SIZE = (1024, 512)
OUTPUT_FILES = ("AureateWake_Wing_Lookdev.glb", "AureateWake_Wing_Albedo.png", "AureateWake_Wing_Manifest.json")
STATUS = "NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"


def half_width(t: float) -> float:
    return WIDTH * 0.5 * max(0.025, math.sin(math.pi * t) ** 0.8) * (0.78 + 0.22 * t)


def height(t: float) -> float:
    return 0.8 + 2.8 * math.sin(math.pi * t)


def surface_point(t: float, cross: float, side: int = 1, lift: float = 1.05):
    return (SPAN*t, cross*half_width(t), side*height(t)+side*lift)


def v_add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def v_sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


def v_scale(a, s):
    return (a[0]*s, a[1]*s, a[2]*s)


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def norm(a):
    n = math.sqrt(sum(x*x for x in a))
    if n <= 1e-9:
        raise ValueError("Zero-length vector")
    return v_scale(a, 1/n)


def make_surface(name):
    return {"name": name, "positions": [], "uv": [], "faces": []}


def vertex(s, p, uv=(0., 0.)):
    i = len(s["positions"])
    s["positions"].append(tuple(p))
    s["uv"].append(tuple(uv))
    return i


def mesh_membrane():
    s = make_surface("veined_membrane")
    n = (SEGMENTS + 1) * 2
    for side in (1, -1):
        for i in range(SEGMENTS + 1):
            t = i/SEGMENTS
            for edge in (-1, 1):
                vertex(s, surface_point(t, edge, side=side, lift=-0.0), (t, (edge+1)*.5))
    for i in range(SEGMENTS):
        a, b, c, d = 2*i, 2*i+1, 2*i+2, 2*i+3
        s["faces"].extend(((a, c, d), (a, d, b), (a+n, b+n, d+n), (a+n, d+n, c+n)))
        for edge in (0, 1):
            x, y = 2*i+edge, 2*(i+1)+edge
            if edge == 0:
                s["faces"].extend(((x,x+n,y+n), (x,y+n,y)))
            else:
                s["faces"].extend(((x,y+n,x+n), (x,y,y+n)))
    for a,b in ((0, 1), (2*SEGMENTS, 2*SEGMENTS+1)):
        s["faces"].extend(((a,b,b+n), (a,b+n,a+n)))
    assert all(len(set(f))==3 for f in s["faces"])
    edge_counts = Counter(tuple(sorted(pair)) for f in s["faces"] for pair in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    if not all(v == 2 for v in edge_counts.values()):
        raise ValueError("Membrane failed edge-manifold test")
    orient_manifold(s)
    return s


def orient_manifold(s):
    """Orient every face coherently; correct a real defect in the old shell generator."""
    faces=list(s["faces"])
    edges={}
    for fid,tri in enumerate(faces):
        for a,b in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])):
            key=(min(a,b),max(a,b))
            edges.setdefault(key,[]).append((fid, 1 if a < b else -1))
    if not all(len(items)==2 for items in edges.values()):
        raise ValueError("Cannot orient nonmanifold surface")
    neighbors=[[] for _ in faces]
    for links in edges.values():
        (a,sa),(b,sb)=links
        neighbors[a].append((b,sa,sb));neighbors[b].append((a,sb,sa))
    flip={}
    for initial in range(len(faces)):
        if initial in flip: continue
        flip[initial]=False; queue=[initial]
        while queue:
            f=queue.pop()
            for target,sgn,other in neighbors[f]:
                # Shared edges must run in opposite directions.
                needed = (sgn == other) != flip[f]
                if target in flip:
                    if flip[target]!=needed:raise ValueError("Conflicting face winding")
                else:
                    flip[target]=needed;queue.append(target)
    for f,reverse in flip.items():
        if reverse:
            a,b,c=faces[f];faces[f]=(a,c,b)
    vol=0.
    pp=s["positions"]
    for a,b,c in faces:
        vol+=sum(q*r for q,r in zip(pp[a],cross(pp[b],pp[c])))/6
    if abs(vol)<.001:raise ValueError("Membrane has negligible signed volume")
    if vol<0:faces=[(a,c,b) for a,b,c in faces]
    s["faces"]=faces


def add_vein_path(s, points, thickness=1.0, sides=7):
    """Connected swept cylinder with smooth shared rings and sealed endpoints."""
    if len(points) < 2:
        return
    pts=[]
    for p in points:
        if not pts or math.sqrt(sum(t*t for t in v_sub(p, pts[-1]))) > .002:
            pts.append(p)
    if len(pts) < 2:
        return
    offset = len(s["positions"])
    for i,p in enumerate(pts):
        tangent = v_sub(pts[min(len(pts)-1, i+1)], pts[max(0,i-1)])
        axis = norm(tangent)
        reference = (0.,0.,1.) if abs(axis[2]) < .92 else (0.,1.,0.)
        basis1=norm(cross(axis,reference))
        basis2=norm(cross(axis,basis1))
        radius=thickness*(.80+.20*math.sin(math.pi*i/max(1,len(pts)-1)))
        for j in range(sides):
            theta=math.tau*j/sides
            dir3 = v_add(v_scale(basis1,math.cos(theta)),v_scale(basis2,math.sin(theta)))
            vertex(s,v_add(p,v_scale(dir3,radius)),(i/max(1,len(pts)-1),j/sides))
    for i in range(len(pts)-1):
        a=offset+i*sides; b=a+sides
        for j in range(sides):
            k=(j+1)%sides
            s["faces"].extend(((a+j,b+j,b+k),(a+j,b+k,a+k)))
    # Close endpoint rims rather than leaving thousands of open tubes.
    initial=vertex(s,pts[0]); final=vertex(s,pts[-1])
    end=offset+(len(pts)-1)*sides
    for j in range(sides):
        k=(j+1)%sides
        s["faces"].append((initial,offset+k,offset+j))
        s["faces"].append((final,end+j,end+k))


def mesh_venation():
    s=make_surface("golden_ribs")
    # A main supporting vein, two scalloped edge spars and layered branching veins.
    for side in (1,-1):
        add_vein_path(s,[surface_point(i/80, 0., side, 1.30) for i in range(81)],1.35 if side==1 else .80)
        for edge in (-0.968,0.968):
            add_vein_path(s,[surface_point(i/80,edge,side,1.22) for i in range(81)],.78 if side==1 else .51)
        for i in range(2,36):
            t=i/39
            for direction in (-1,1):
                u_end=min(.985,t+.085+.035*math.sin(i*.71))
                path=[]
                for k in range(9):
                    q=k/8
                    u=t+(u_end-t)*q
                    # Branch starts close to the costa and lands exactly on the physical rim.
                    v=direction * (0.045+0.92*(q**.83))
                    path.append(surface_point(u,v,side,1.35+.2*math.sin(math.pi*q)))
                add_vein_path(s,path,.52 if side==1 else .39)
                if i%2==0:
                    ladder=[]
                    for k in range(5):
                        q=k/4
                        u=t+.020*q
                        v=direction*(.48+.38*q)
                        ladder.append(surface_point(u,v,side,1.28))
                    add_vein_path(s,ladder,.28)
    orient_manifold(s)
    return s


def mesh_hinge():
    s=make_surface("brass_root_hinge")
    # Ringed cylindrical joining hardware: oriented along local +X root axis.
    for x0,x1,r in ((-16,0,7.4),(0,13,9.1),(13,28,6.1)):
        ring_count=12
        offset=len(s["positions"])
        for x in (x0,x1):
            for j in range(ring_count):
                t=math.tau*j/ring_count
                vertex(s,(x,r*math.cos(t),r*math.sin(t)),(j/ring_count,0. if x==x0 else 1.))
        for j in range(ring_count):
            k=(j+1)%ring_count
            a,b,c,d=offset+j,offset+k,offset+ring_count+j,offset+ring_count+k
            s["faces"].extend(((a,b,d),(a,d,c)))
        cap_a=vertex(s,(x0,0.,0.)); cap_b=vertex(s,(x1,0.,0.))
        for j in range(ring_count):
            k=(j+1)%ring_count
            s["faces"].extend(((cap_a,offset+k,offset+j),
                               (cap_b,offset+ring_count+j,offset+ring_count+k)))
    return s


def normals(s):
    ns=[[0.,0.,0.] for _ in s["positions"]]
    for i,j,k in s["faces"]:
        v1,v2,v3=s["positions"][i],s["positions"][j],s["positions"][k]
        nn=cross(v_sub(v2,v1),v_sub(v3,v1))
        for idx in (i,j,k):
            for a in range(3):
                ns[idx][a]+=nn[a]
    return [norm(n) if sum(k*k for k in n)>1e-16 else (0.,0.,1.) for n in ns]


def texture_rgba(width=PBR_SIZE[0],height=PBR_SIZE[1]):
    pixels=bytearray()
    for y in range(height):
        v=y/(height-1)
        for x in range(width):
            u=x/(width-1)
            cell=(math.sin(23*math.pi*u+6.1*v)*math.sin(14*math.pi*v-2*u)+1)/2
            grain=(math.sin(301*u+19*v)*math.sin(188*v-5*u)+1)/2
            soft=max(0.0,math.sin(math.pi*u))**.6
            r=int(43+17*cell+12*grain+19*u)
            g=int(118+24*cell+22*soft+7*grain)
            b=int(143+27*cell+16*soft+8*grain)
            alpha=int(160+73*(1-abs(2*v-1))**.55)
            pixels.extend((min(255,r),min(255,g),min(255,b),min(255,alpha)))
    return bytes(pixels)


def png_rgba(width,height,pixels):
    if len(pixels)!=width*height*4:
        raise ValueError("PNG pixel buffer length mismatch")
    def chunk(kind,data):
        return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    rows=b"".join(b"\0"+pixels[y*width*4:(y+1)*width*4] for y in range(height))
    return (b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0))+
            chunk(b"IDAT",zlib.compress(rows,9))+chunk(b"IEND",b""))


def gltf_axis(p):
    # The glTF +Y-up handedness transform for an authored Unreal +Z-up vertex.
    return (p[0],p[2],-p[1])


def gltf_position(p):
    # glTF 2.0 linear positions are METERS. The authored mesh dimensions are cm.
    return tuple(x * 0.01 for x in gltf_axis(p))


def make_glb(surfaces,embedded_png):
    buffer=bytearray()
    views=[]
    accessors=[]
    primitives=[]
    def append(data,target=None):
        while len(buffer)%4: buffer.append(0)
        offset=len(buffer);buffer.extend(data)
        item={"buffer":0,"byteOffset":offset,"byteLength":len(data)}
        if target: item["target"]=target
        views.append(item)
        return len(views)-1
    def accessor(values,type_,fmt,component_type,target,with_bounds=False):
        flat=[v for item in values for v in (item if isinstance(item,tuple) else (item,))]
        raw=struct.pack("<"+str(len(flat))+fmt,*flat)
        index=append(raw,target)
        a={"bufferView":index,"componentType":component_type,"count":len(values),"type":type_}
        if with_bounds:
            a["min"]=[min(v[i] for v in values) for i in range(len(values[0]))]
            a["max"]=[max(v[i] for v in values) for i in range(len(values[0]))]
        accessors.append(a)
        return len(accessors)-1
    for material,s in enumerate(surfaces):
        pp=[gltf_position(v) for v in s["positions"]]
        nn=[gltf_axis(v) for v in normals(s)]
        pa=accessor(pp,"VEC3","f",5126,34962,True)
        na=accessor(nn,"VEC3","f",5126,34962)
        tex=accessor(s["uv"],"VEC2","f",5126,34962)
        ids=accessor([v for f in s["faces"] for v in f],"SCALAR","I",5125,34963)
        primitives.append({"attributes":{"POSITION":pa,"NORMAL":na,"TEXCOORD_0":tex},"indices":ids,"material":material,"mode":4})
    image_view=append(embedded_png)
    materials=[
      {"name":"MI_Wing_IridescentMembrane_REVIEW","doubleSided":True,"alphaMode":"BLEND",
       "pbrMetallicRoughness":{"baseColorTexture":{"index":0},"metallicFactor":.16,"roughnessFactor":.38}},
      {"name":"MI_Wing_BrassVenation_REVIEW","doubleSided":True,
       "pbrMetallicRoughness":{"baseColorFactor":[.7,.43,.13,1.],"metallicFactor":.75,"roughnessFactor":.3}},
      {"name":"MI_Wing_RootFerrules_REVIEW","doubleSided":True,
       "pbrMetallicRoughness":{"baseColorFactor":[.45,.30,.10,1.],"metallicFactor":.85,"roughnessFactor":.36}},
    ]
    doc={"asset":{"version":"2.0","generator":"TSTSS 2026 wing authoring candidate"},
         "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0,"name":"AureateWake_ArtReviewWing"}],
         "meshes":[{"name":"DragonflyArtReview_OneWing","primitives":primitives}],"bufferViews":views,
         "accessors":accessors,"buffers":[{"byteLength":len(buffer)}],
         "materials":materials,"textures":[{"sampler":0,"source":0}],
         "samplers":[{"magFilter":9729,"minFilter":9729,"wrapS":10497,"wrapT":10497}],
         "images":[{"name":"Wing_CyanGoldAlbedo","bufferView":image_view,"mimeType":"image/png"}],
         "extras":{"authority":STATUS,"sourceUnits":"centimeters","gltfLinearUnits":"meters","sourceToGltfScale":0.01,"reveal_gates":"Not part of this asset; four-form ship preview remains gated"}}
    j=json.dumps(doc,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    j+=b" "*((-len(j))%4)
    while len(buffer)%4:buffer.append(0)
    bchunk=bytes(buffer)
    total=12+8+len(j)+8+len(bchunk)
    return (struct.pack("<4sII",b"glTF",2,total)+struct.pack("<I4s",len(j),b"JSON")+j+
            struct.pack("<I4s",len(bchunk),b"BIN\x00")+bchunk),doc


def build():
    pieces=[mesh_membrane(),mesh_venation(),mesh_hinge()]
    img=png_rgba(*PBR_SIZE,texture_rgba())
    glb,gltf=make_glb(pieces,img)
    summary={"status":STATUS,"source":"deterministic procedural 3D wing study",
             "source_units":"centimeters","gltf_linear_units":"meters","source_to_gltf_scale":0.01,"root_axis":"Unreal +X", "span_cm":SPAN,"full_width_cm":WIDTH,
             "topology":[{"name":p["name"],"vertices":len(p["positions"]),"triangles":len(p["faces"])} for p in pieces],
             "texture_resolution":list(PBR_SIZE),
             "integration":"Review imported static mesh in Unreal 5.8; do not automatically replace approved ship assets",
             "limits":["No creator visual approval","No native Unreal render","No collision or articulated hinge clearance test",
                       "No actual optical photovoltaic or physical metamaterial behavior","No gameplay/story/Orbiter unlock authority"],
             "sha256":{"AureateWake_Wing_Lookdev.glb":hashlib.sha256(glb).hexdigest(),
                       "AureateWake_Wing_Albedo.png":hashlib.sha256(img).hexdigest()}}
    return glb,img,summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--validate-only",action="store_true")
    args=ap.parse_args()
    glb,img,info=build()
    print(json.dumps(info,indent=2))
    if args.validate_only:return
    d=args.output_dir.resolve()
    if d.exists() and any(d.iterdir()):
        raise SystemExit("REVIEW HOLD: output folder exists with contents; no overwrite")
    d.mkdir(parents=True,exist_ok=True)
    for name,blob in ((OUTPUT_FILES[0],glb),(OUTPUT_FILES[1],img),
                      (OUTPUT_FILES[2],(json.dumps(info,indent=2)+"\n").encode())):
        (d/name).write_bytes(blob)
    print("WROTE "+str(d))

if __name__=="__main__":main()