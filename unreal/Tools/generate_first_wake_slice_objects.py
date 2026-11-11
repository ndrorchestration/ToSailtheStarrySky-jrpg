#!/usr/bin/env python3
"""Original modular First Wake vertical-slice prop geometry. Engine-free GLB generator.

All model dimensions are in UE centimeters and are rotated to glTF Y-up meters.
One source GLB per static-mesh prefab, with physically based material slots.
This generates no actor interactions, Starbourne content, maps or SaveGames.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "unreal/ArtSource/VerticalSliceObjectsV1"
MODEL_VERSION = "FIRST_WAKE_SLICE_OBJECTS_V1"
MATERIALS = {
    "brass": ([0.56, 0.34, 0.14, 1], 0.76, 0.31),
    "dark_iron": ([0.12, 0.17, 0.20, 1], 0.74, 0.46),
    "patina": ([0.10, 0.31, 0.30, 1], 0.63, 0.56),
    "wood": ([0.30, 0.16, 0.095, 1], 0.05, 0.72),
    "canvas": ([0.77, 0.65, 0.43, 1], 0.0, 0.89),
    "porcelain": ([0.77, 0.79, 0.73, 1], 0.0, 0.33),
    "amber_glass": ([0.96, 0.55, 0.12, 1], 0.06, 0.23),
    "teal_glass": ([0.045, 0.46, 0.46, 1], 0.06, 0.22),
    "ruby": ([0.66, 0.08, 0.095, 1], 0.12, 0.18),
}
# Transform from authoring cm (UE Z-up) to glTF meters (+Y-up).
def gltf(p):
    return (p[0] / 100.0, p[2] / 100.0, -p[1] / 100.0)

def vec_add(a,b): return tuple(x+y for x,y in zip(a,b))
def vec_sub(a,b): return tuple(x-y for x,y in zip(a,b))
def vec_mul(a,s): return tuple(x*s for x in a)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def unit(a):
    v=math.sqrt(sum(x*x for x in a))
    if v < 1e-8: raise ValueError("Degenerate mesh face or axis")
    return tuple(x/v for x in a)

class Mesh:
    def __init__(self):
        self.triangles = {k: [] for k in MATERIALS}
    def tri(self, mat, a, b, c):
        q = [gltf(v) for v in (a,b,c)]
        normal = cross(vec_sub(q[1],q[0]), vec_sub(q[2],q[0]))
        if sum(x*x for x in normal) < 1e-14: raise ValueError("Degenerate triangle")
        self.triangles[mat].append((q,unit(normal)))
    def quad(self, mat, a,b,c,d):
        self.tri(mat,a,b,c); self.tri(mat,a,c,d)
    def box(self, mat, x,y,z, w,d,h):
        x0,x1=x-w/2,x+w/2; y0,y1=y-d/2,y+d/2; z0,z1=z-h/2,z+h/2
        p=lambda xx,yy,zz:(xx,yy,zz)
        for points in (
            (p(x0,y0,z0),p(x1,y0,z0),p(x1,y0,z1),p(x0,y0,z1)),
            (p(x1,y1,z0),p(x0,y1,z0),p(x0,y1,z1),p(x1,y1,z1)),
            (p(x1,y0,z0),p(x1,y1,z0),p(x1,y1,z1),p(x1,y0,z1)),
            (p(x0,y1,z0),p(x0,y0,z0),p(x0,y0,z1),p(x0,y1,z1)),
            (p(x0,y0,z1),p(x1,y0,z1),p(x1,y1,z1),p(x0,y1,z1)),
            (p(x0,y1,z0),p(x1,y1,z0),p(x1,y0,z0),p(x0,y0,z0)),
        ): self.quad(mat,*points)
    def cylinder(self, mat, x,y,z, radius,height, axis="z", n=20, top_radius=None):
        r2=radius if top_radius is None else top_radius
        def transform(p):
            a,b,c=p
            v=(c,b,-a) if axis=="x" else ((a,c,-b) if axis=="y" else (a,b,c))
            return (x+v[0],y+v[1],z+v[2])
        lo,hi=-height/2,height/2
        for i in range(n):
            a=2*math.pi*i/n; b=2*math.pi*(i+1)/n
            v0=transform((radius*math.cos(a),radius*math.sin(a),lo))
            v1=transform((radius*math.cos(b),radius*math.sin(b),lo))
            v2=transform((r2*math.cos(b),r2*math.sin(b),hi))
            v3=transform((r2*math.cos(a),r2*math.sin(a),hi))
            self.quad(mat,v0,v1,v2,v3)
            self.tri(mat,transform((0,0,hi)),v3,v2)
            self.tri(mat,transform((0,0,lo)),v1,v0)
    def sphere(self,mat,x,y,z,r,n=16,stacks=8):
        for j in range(stacks):
            t0=math.pi*j/stacks; t1=math.pi*(j+1)/stacks
            for i in range(n):
                a=2*math.pi*i/n; b=2*math.pi*(i+1)/n
                def p(t,q): return (x+r*math.sin(t)*math.cos(q),y+r*math.sin(t)*math.sin(q),z+r*math.cos(t))
                if j<stacks-1: self.tri(mat,p(t0,a),p(t1,a),p(t1,b))
                if j: self.tri(mat,p(t0,a),p(t1,b),p(t0,b))
    def torus(self,mat,x,y,z,major,tube,axis="z",n=32,m=8):
        def transform(p):
            a,b,c=p
            v=(c,b,-a) if axis=="x" else ((a,c,-b) if axis=="y" else (a,b,c))
            return (x+v[0],y+v[1],z+v[2])
        def p(theta,phi):
            rr=major+tube*math.cos(phi)
            return transform((rr*math.cos(theta),rr*math.sin(theta),tube*math.sin(phi)))
        for i in range(n):
            t0=2*math.pi*i/n; t1=2*math.pi*(i+1)/n
            for j in range(m):
                p0=2*math.pi*j/m; p1=2*math.pi*(j+1)/m
                self.quad(mat,p(t0,p0),p(t1,p0),p(t1,p1),p(t0,p1))
    def rod(self,mat,a,b,r=3,n=10):
        v=vec_sub(b,a); axis=unit(v); ref=(0,0,1) if abs(axis[2])<0.9 else (0,1,0)
        u=unit(cross(axis,ref)); w=cross(axis,u)
        def ring(c,theta):
            return vec_add(c,vec_add(vec_mul(u,r*math.cos(theta)),vec_mul(w,r*math.sin(theta))))
        for i in range(n):
            t=2*math.pi*i/n; q=2*math.pi*(i+1)/n
            self.quad(mat,ring(a,t),ring(a,q),ring(b,q),ring(b,t))
            self.tri(mat,a,ring(a,q),ring(a,t))
            self.tri(mat,b,ring(b,t),ring(b,q))
    def glb(self,name):
        buffer=bytearray(); views=[]; accessors=[]; primitives=[]
        def add_view(blob,target):
            while len(buffer)%4: buffer.append(0)
            off=len(buffer); buffer.extend(blob)
            idx=len(views); views.append({"buffer":0,"byteOffset":off,"byteLength":len(blob),"target":target}); return idx
        def acc(view,count,ctype,kind,minimum=None,maximum=None):
            d={"bufferView":view,"componentType":ctype,"count":count,"type":kind}
            if minimum is not None: d.update(min=minimum,max=maximum)
            idx=len(accessors); accessors.append(d); return idx
        all_points=[]
        for mat_i,(role,triangles) in enumerate(self.triangles.items()):
            if not triangles: continue
            pts=[]; normals=[]; uv=[]; idx=[]
            for q,n in triangles:
                dominant=max(range(3),key=lambda i:abs(n[i]))
                for p in q:
                    pts.extend(p); normals.extend(n)
                    # Stable meter-scale planar UVs, one projection per face.
                    uv.extend((p[2],p[1]) if dominant==0 else
                              ((p[0],p[2]) if dominant==1 else (p[0],p[1])))
                    all_points.append(p); idx.append(len(idx))
            count=len(idx)
            pos=acc(add_view(struct.pack("<%df"%len(pts),*pts),34962),count,5126,"VEC3",
                    [min(pts[i::3]) for i in range(3)],[max(pts[i::3]) for i in range(3)])
            norm=acc(add_view(struct.pack("<%df"%len(normals),*normals),34962),count,5126,"VEC3")
            tc=acc(add_view(struct.pack("<%df"%len(uv),*uv),34962),count,5126,"VEC2")
            ind=acc(add_view(struct.pack("<%dI"%count,*idx),34963),count,5125,"SCALAR")
            primitives.append({"attributes":{"POSITION":pos,"NORMAL":norm,"TEXCOORD_0":tc},
                               "indices":ind,"material":mat_i,"mode":4})
        if not primitives: raise ValueError("Empty mesh")
        mats=[]
        for role,(rgba,metal,rough) in MATERIALS.items():
            mats.append({"name":"TSTSS_"+role,"pbrMetallicRoughness":{
                "baseColorFactor":rgba,"metallicFactor":metal,"roughnessFactor":rough},
                "doubleSided":False})
        doc={"asset":{"version":"2.0","generator":MODEL_VERSION},"scene":0,
            "scenes":[{"nodes":[0]}],"nodes":[{"name":name,"mesh":0}],
            "meshes":[{"name":name,"primitives":primitives}],"materials":mats,
            "buffers":[{"byteLength":len(buffer)}],"bufferViews":views,"accessors":accessors}
        j=json.dumps(doc,separators=(",",":"),sort_keys=True).encode("utf-8")
        j+=b" "*((-len(j))%4)
        while len(buffer)%4: buffer.append(0)
        total=12+8+len(j)+8+len(buffer)
        glb=struct.pack("<4sII",b"glTF",2,total)+struct.pack("<I4s",len(j),b"JSON")+j
        glb+=struct.pack("<I4s",len(buffer),b"BIN\x00")+buffer
        return bytes(glb),{"triangles":sum(len(v) for v in self.triangles.values()),
                           "materials_used":[k for k,v in self.triangles.items() if v],
                           "bounds_glb_m":[[round(min(p[i] for p in all_points),4),
                                            round(max(p[i] for p in all_points),4)] for i in range(3)]}

def model(name):
    m=Mesh()
    box=m.box; cyl=m.cylinder; tor=m.torus; rod=m.rod; sph=m.sphere
    if name=="MooringBollard":
        cyl("dark_iron",0,0,15,24,30); cyl("brass",0,0,5,32,9)
        cyl("dark_iron",0,0,40,14,47,top_radius=18)
        cyl("brass",0,0,64,25,8)
        for a in range(8):
            t=math.tau*a/8; sph("brass",26*math.cos(t),26*math.sin(t),8,3,8,4)
    elif name=="MooringCleat":
        box("brass",0,0,5,85,28,10); cyl("dark_iron",0,0,15,10,24)
        for x in (-34,34): cyl("dark_iron",x,0,26,10,25)
        box("brass",0,0,40,115,21,13)
    elif name=="HarborLantern":
        cyl("dark_iron",0,0,12,11,25); cyl("patina",0,0,130,5,220)
        box("brass",0,0,241,55,55,8); box("brass",0,0,315,60,60,8)
        for x in (-23,23):
            for y in (-23,23): rod("dark_iron",(x,y,245),(x,y,313),2)
        cyl("amber_glass",0,0,278,18,58)
        cyl("patina",0,0,332,8,23,top_radius=0.2)
    elif name=="CargoCrate":
        box("wood",0,0,48,105,90,96)
        for z in (8,87):
            box("dark_iron",0,0,z,111,98,8)
        for x in (-48,48): box("brass",x,0,48,8,94,86)
        for y in (-40,40): box("brass",0,y,48,96,8,86)
        for x in (-32,32): cyl("brass",x,-49,77,4,3,"y")
    elif name=="RopeCoil":
        for i in range(5): tor("canvas",0,0,8+i*8,38,5,n=32,m=8)
        rod("canvas",(35,0,43),(65,22,20),4)
    elif name=="FlyerPodium":
        cyl("patina",0,0,10,35,20); cyl("brass",0,0,65,12,100)
        box("wood",0,-4,120,90,13,108)
        for x in (-45,45): box("brass",x,-14,120,6,8,114)
        for z in (66,174): box("brass",0,-14,z,92,8,6)
        tor("amber_glass",0,-17,122,24,3,axis="y")
        rod("brass",(-21,-20,122),(21,-20,122),3)
    elif name=="CaptainDesk":
        box("wood",0,0,90,180,85,12)
        for x in (-72,72):
            for y in (-30,30): box("dark_iron",x,y,44,13,13,88)
        box("brass",0,-43,84,170,5,5)
        box("canvas",20,-8,98,76,47,2)
        cyl("brass",-60,16,100,16,5); rod("brass",(-60,16,105),(-54,8,137),3)
    elif name=="GangwayAnchor":
        box("dark_iron",0,0,12,95,70,24)
        cyl("patina",0,0,42,24,40)
        tor("brass",0,0,71,28,5,axis="y")
        for x in (-38,38):
            for y in (-23,23): cyl("brass",x,y,25,5,8)
    elif name=="EngineeringWorkbench":
        box("dark_iron",0,0,84,200,90,12)
        for x in (-88,88):
            for y in (-35,35): box("patina",x,y,43,8,8,76)
        box("wood",0,0,90,188,83,10)
        box("dark_iron",0,35,145,174,8,100)
        for x in (-56,0,56): rod("brass",(x,34,105),(x,34,172),2)
    elif name=="LiftResonator":
        cyl("dark_iron",0,0,16,63,32)
        cyl("brass",0,0,47,38,33)
        for axis,r in (("z",63),("x",56),("y",49)):
            tor("brass",0,0,128,r,4,axis=axis,n=32)
        sph("teal_glass",0,0,128,23)
        for x in (-60,60): rod("patina",(x,0,35),(x,0,115),5)
        for x in (-35,35): cyl("amber_glass",x,-47,41,8,8)
    elif name=="PressureRegulator":
        box("dark_iron",0,0,18,115,75,36)
        for x in (-32,32):
            cyl("patina",x,20,80,16,115)
            tor("brass",x,20,132,17,3)
        cyl("brass",0,-43,95,48,16,"y")
        cyl("porcelain",0,-53,95,36,3,"y")
        rod("dark_iron",(0,-56,95),(22,-58,115),4)
        cyl("ruby",39,-43,37,8,15)
    elif name=="ReserveTank":
        cyl("dark_iron",0,0,85,43,145)
        cyl("brass",0,0,19,49,18); cyl("brass",0,0,155,50,20)
        for z in (43,125): tor("brass",0,0,z,44,5)
        cyl("teal_glass",0,-45,95,18,67)
        cyl("amber_glass",0,0,178,14,24)
        rod("patina",(-70,0,25),(-70,0,153),5)
        rod("patina",(-70,0,153),(-39,0,153),5)
    elif name=="SignoffPlinth":
        cyl("dark_iron",0,0,12,38,24)
        cyl("brass",0,0,73,17,107)
        box("patina",0,0,137,88,64,16)
        for x in (-24,0,24): cyl("amber_glass",x,-15,149,8,11)
        cyl("ruby",0,14,150,15,17)
    elif name=="HarmonicEngineCore":
        cyl("dark_iron",0,0,21,75,42)
        for axis in ("x","y","z"): tor("brass",0,0,116,79,7,axis=axis,n=40)
        sph("teal_glass",0,0,116,35)
        for t in (0,math.pi/2,math.pi,3*math.pi/2):
            x,y=75*math.cos(t),75*math.sin(t)
            rod("patina",(x,y,27),(x,y,192),7)
        cyl("dark_iron",0,0,205,52,14)
    elif name=="ToolRack":
        box("wood",0,0,98,140,20,190)
        for z in (34,95,162): box("brass",0,-15,z,142,8,6)
        for x in (-48,-16,16,48):
            rod("dark_iron",(x,-25,110),(x,-25,165),3)
            cyl("brass",x,-26,102,6,12,"y")
    elif name=="BridgeHelm":
        cyl("dark_iron",0,0,13,50,26)
        cyl("patina",0,0,105,15,170)
        tor("brass",0,-15,205,66,5,axis="y",n=36)
        cyl("dark_iron",0,-15,205,18,18,"y")
        for i in range(8):
            t=2*math.pi*i/8
            rod("brass",(0,-15,205),(60*math.cos(t),-15,205+60*math.sin(t)),4)
    elif name=="BridgeOrrery":
        cyl("dark_iron",0,0,10,43,20)
        cyl("brass",0,0,71,8,117)
        for ax,r in (("x",45),("y",52),("z",56)):
            tor("brass",0,0,165,r,3,axis=ax)
        sph("amber_glass",0,0,165,16)
        for t in (0,math.pi*2/3,math.pi*4/3):
            sph("teal_glass",42*math.cos(t),42*math.sin(t),165,7,12,6)
    elif name=="DeckRailModule":
        for x in (-95,-48,0,48,95):
            cyl("patina",x,0,49,5,98)
        box("brass",0,0,103,210,12,12)
        box("dark_iron",0,0,10,210,14,18)
        for x in (-95,95): sph("brass",x,0,109,9,12,6)
    elif name=="GeodesicJunction":
        sph("dark_iron",0,0,0,20)
        for a in range(6):
            t=math.tau*a/6
            v=(70*math.cos(t),70*math.sin(t),35)
            rod("brass",(0,0,0),v,7)
            sph("patina",*v,11)
        rod("brass",(0,0,0),(0,0,83),7)
    elif name=="WingHinge":
        cyl("dark_iron",0,0,0,38,90,"y")
        for y in (-43,43): cyl("brass",0,y,0,48,8,"y")
        for x in (-65,65):
            box("patina",x,0,-12,30,125,24)
            for y in (-48,48): cyl("brass",x,y,0,8,13,"y")
        rod("brass",(-65,0,38),(65,0,38),6)
    elif name=="EmergencyBeacon":
        cyl("dark_iron",0,0,11,30,22)
        cyl("patina",0,0,45,10,53)
        cyl("amber_glass",0,0,105,24,60)
        for t in (0,math.pi/2,math.pi,3*math.pi/2):
            x,y=22*math.cos(t),22*math.sin(t)
            rod("brass",(x,y,73),(x,y,140),3)
        cyl("brass",0,0,147,28,11)
    elif name=="FlotationBuoy":
        tor("canvas",0,0,0,46,14,n=40,m=12)
        for t in (0,math.pi/2,math.pi,3*math.pi/2):
            x,y=46*math.cos(t),46*math.sin(t)
            sph("amber_glass",x,y,0,8)
        for a in range(4):
            t=math.tau*a/4
            rod("dark_iron",(49*math.cos(t),49*math.sin(t),0),
                (49*math.cos(t+0.26),49*math.sin(t+0.26),1),4)
    else: raise ValueError("Unknown slice asset: "+name)
    return m

# Only the Prelude-through-Splashdown set; no post-landing NPCs, combat, or Starbourne.
ASSET_NAMES = (
    "MooringBollard","MooringCleat","HarborLantern","CargoCrate","RopeCoil",
    "FlyerPodium","CaptainDesk","GangwayAnchor","EngineeringWorkbench",
    "LiftResonator","PressureRegulator","ReserveTank","SignoffPlinth",
    "HarmonicEngineCore","ToolRack","BridgeHelm","BridgeOrrery",
    "DeckRailModule","GeodesicJunction","WingHinge","EmergencyBeacon","FlotationBuoy"
)
# Placement is visual-only, separate from seven real MilestoneActor E targets.
# x,y,z location in centimeters, yaw degrees, scale uniform. This is not physical landing.
PLACEMENTS = [
    ("FlyerPodium",-2200,-245,0,0,1),("CaptainDesk",-1550,-270,0,0,1),
    ("GangwayAnchor",-900,260,0,0,1),
    ("EngineeringWorkbench",-200,350,0,0,1),
    ("LiftResonator",-250,235,0,0,0.85),
    ("PressureRegulator",225,235,0,0,1),
    ("ReserveTank",700,230,0,0,1),
    ("SignoffPlinth",1175,220,0,0,1),
    ("HarmonicEngineCore",310,325,0,0,0.8),
    ("ToolRack",80,345,0,0,1),
    ("MooringBollard",-1870,510,0,0,1),
    ("MooringBollard",-740,510,0,0,1),
    ("MooringCleat",-1120,520,0,0,1),
    ("MooringCleat",50,520,0,0,1),
    ("HarborLantern",-2350,-515,0,0,1),
    ("HarborLantern",-1000,-515,0,0,1),
    ("HarborLantern",500,-515,0,0,1),
    ("CargoCrate",-1700,560,0,8,1),
    ("CargoCrate",-1800,650,0,-9,0.9),
    ("CargoCrate",1150,540,0,15,1),
    ("RopeCoil",-1120,590,0,0,1),
    ("RopeCoil",50,600,0,0,1),
    ("BridgeHelm",-950,1150,210,0,1),
    ("BridgeOrrery",-860,1200,210,0,0.8),
    ("DeckRailModule",-1180,1150,240,0,1),
    ("DeckRailModule",-800,1150,240,0,1),
    ("GeodesicJunction",-950,1260,450,0,1),
    ("WingHinge",-1350,1800,360,15,1),
    ("WingHinge",-560,1800,360,-15,1),
    ("EmergencyBeacon",-950,1500,360,0,1),
    ("FlotationBuoy",-550,1530,255,0,1),
]

def inventory():
    if len(ASSET_NAMES)!=len(set(ASSET_NAMES)) or len(ASSET_NAMES)!=22:
        raise ValueError("Unexpected slice-asset count or duplicates")
    if {p[0] for p in PLACEMENTS} != set(ASSET_NAMES):
        raise ValueError("All and only defined slice assets must be instantiated")
    for n,x,y,z,yaw,scale in PLACEMENTS:
        if not all(math.isfinite(v) for v in (x,y,z,yaw,scale)) or scale<=0:
            raise ValueError("Invalid placement")
        if n in {"LiftResonator","PressureRegulator","ReserveTank"} and abs(y)<200:
            raise ValueError("Control prop intrudes into central E marker")
    records=[]; data={}
    for name in ASSET_NAMES:
        blob,stats=model(name).glb(name)
        stats.update(name=name,sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob))
        if stats["triangles"]<60 or stats["triangles"]>25000:
            raise ValueError("Geometry complexity outside bounds: "+name)
        records.append(stats); data[name]=blob
    return {"version":MODEL_VERSION,"source_units":"UE centimeters",
            "glb_units":"meters Y-up","native_import_verified":False,
            "art_approved":False,"physical_water_verified":False,
            "original_objects":records,
            "placements":[dict(asset=n,x=x,y=y,z=z,yaw=yaw,scale=scale,
                               collision="NoCollision",interactive=False)
                          for n,x,y,z,yaw,scale in PLACEMENTS]},data

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    args=parser.parse_args()
    report,data=inventory()
    if args.build:
        OUT.mkdir(parents=True,exist_ok=True)
        artifacts={name+".glb": blob for name,blob in data.items()}
        artifacts["manifest.json"]=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode()
        for name,blob in artifacts.items():
            target=OUT/name
            if target.exists() and target.read_bytes()!=blob:
                raise RuntimeError("Refuse to overwrite changed source asset: "+str(target))
        for name,blob in artifacts.items():
            target=OUT/name
            if not target.exists():
                with target.open("xb") as stream: stream.write(blob)
    print(json.dumps({"status":"ORIGINAL_GLB_SOURCE_BUILT_NOT_UNREAL_IMPORTED" if args.build else
                      "GLB_SOURCE_VALID_NOT_UNREAL_IMPORTED",
                      "assets":len(report["original_objects"]),
                      "placements":len(report["placements"]),
                      "triangles":sum(r["triangles"] for r in report["original_objects"]),
                      "source_dir":str(OUT)},sort_keys=True))

if __name__=="__main__":
    main()
