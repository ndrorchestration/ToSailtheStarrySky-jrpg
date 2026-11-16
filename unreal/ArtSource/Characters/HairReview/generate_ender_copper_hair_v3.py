"""Original Ender broad-layer hair V3: isolated STATIC GLB sculpt study.

No external textures/reference pixels, licensed DAZ or MetaHuman mesh, rig, groom
or production asset is included. All dimensions are provisional. Does not use UE.
The newer creator-approved portrait targets tousled dark-brown/copper hair;
this procedural study is NOT a claim of visual reference match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np

TAU = math.tau
RX, RY, RZ = 0.082, 0.101, 0.104  # Unverified study scalp, metres; front +Y
COLORS = (
    ("UmberRootShell", (.061, .027, .021, 1.), .92),
    ("DeepChestnutVolumes", (.117, .050, .035, 1.), .83),
    ("WarmCopperPlanes", (.176, .073, .045, 1.), .80),
    ("SoftDarkUnderlayers", (.083, .034, .029, 1.), .91),
)
PARTS = {name: [] for name, *_ in COLORS}
COUNTS = {}


def unit(v):
    v = np.asarray(v, dtype=np.float64)
    mag = float(np.linalg.norm(v))
    if mag < 1e-8:
        raise ValueError("Zero-length tangent or surface normal")
    return v / mag


def scalp(az, polar, lift=0.):
    p = np.array((RX*math.cos(az)*math.sin(polar),
                  RY*math.sin(az)*math.sin(polar),
                  RZ*math.cos(polar)), dtype=np.float64)
    n = unit((p[0]/(RX*RX), p[1]/(RY*RY), p[2]/(RZ*RZ)))
    return p+n*lift, n


def add(material, vertices, faces, category):
    v = np.asarray(vertices, dtype=np.float64)
    f = np.asarray(faces, dtype=np.uint32)
    if v.ndim != 2 or v.shape[1] != 3 or len(f) == 0:
        raise AssertionError("Bad mesh part " + category)
    tri = v[f]
    twice_areas = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0],
                                            tri[:, 2]-tri[:, 0]), axis=1)
    if not np.isfinite(v).all() or np.min(twice_areas) < 1e-12:
        raise AssertionError("Degenerate mesh part " + category)
    PARTS[material].append((v, f))
    COUNTS[category] = COUNTS.get(category, 0) + 1


def scalp_shell():
    # One continuous root cap hides scalp splits. No copied skull/face meshes.
    rings, around = 24, 64
    verts = []
    faces = []
    for j in range(rings+1):
        t = j/rings
        for k in range(around):
            az = TAU*k/around
            front = max(0., math.sin(az))
            back = max(0., -math.sin(az))
            end_polar = 1.76 - .13*front + .22*back
            p, _ = scalp(az, .014 + t*end_polar, .001)
            verts.append(p)
    for j in range(rings):
        for k in range(around):
            q = (k+1)%around
            a, b = j*around+k, j*around+q
            c, d = (j+1)*around+k, (j+1)*around+q
            faces.extend(((a,c,b), (b,c,d)))
    add("UmberRootShell", verts, faces, "continuous_root_shell")


def bezier(p0, p1, p2, p3, t):
    u=1.-t
    center=u**3*p0+3*u*u*t*p1+3*u*t*t*p2+t**3*p3
    tang=3*u*u*(p1-p0)+6*u*t*(p2-p1)+3*t*t*(p3-p2)
    return center, unit(tang)


def sculpted_blade(root, normal, sweep, width, length, material, category, twist=0.):
    """Wide shallow curved volume, NOT a tubular bunch of noodle strands.

    Top and underside share sealed sidewalls. A domed seven-point cross-section
    gives a broad overlapping shape suitable for later manual sculpt/retopo.
    """
    sweep = unit(sweep)
    p0 = root - normal*.001
    p1 = root + normal*.012 + sweep*(length*.21) + np.array((0.,0.,.003))
    p2 = root + normal*.019 + sweep*(length*.70) + np.array((0.,0.,-.009))
    p3 = root + normal*.007 + sweep*length + np.array((0.,0.,-.020))
    segments, across_count=14, 7
    vertices=[]
    for j in range(segments+1):
        t=j/segments
        center, tangent=bezier(p0,p1,p2,p3,t)
        outward=unit((center[0]/(RX*RX),center[1]/(RY*RY),
                      center[2]/(RZ*RZ)))
        sideways=np.cross(tangent,outward)
        if np.linalg.norm(sideways)<.08:
            sideways=np.cross(tangent,np.array((0.,1.,0.)))
        sideways=unit(sideways)
        top=unit(np.cross(sideways,tangent))
        if np.dot(top,outward)<0:
            top=-top
        w=width*((.52+.48*math.sin(math.pi*(.13+.75*t)))*(1.-t)**.61+.065)
        w=max(w,.0008)
        roll=twist*t
        across_vec=unit(sideways*math.cos(roll)+top*math.sin(roll))
        upper_vec=unit(top*math.cos(roll)-sideways*math.sin(roll))
        for upper in (True,False):
            for k in range(across_count):
                x=2*k/(across_count-1)-1
                curve=.0015*(1.-x*x)+.0015*math.sin(math.pi*t)*(1.-x*x)
                depth=(.0013+curve) if upper else -.0011
                vertices.append(center + across_vec*(x*w) + upper_vec*depth)
    faces=[]
    stride=2*across_count
    for j in range(segments):
        for surf in (0,1):
            offset=surf*across_count
            for k in range(across_count-1):
                a=j*stride+offset+k
                b=a+1
                c=(j+1)*stride+offset+k
                d=c+1
                faces.extend(((a,b,c),(b,d,c)) if surf==0 else ((a,c,b),(b,c,d)))
        for k in (0,across_count-1):
            a=j*stride+k
            b=j*stride+across_count+k
            c=(j+1)*stride+k
            d=(j+1)*stride+across_count+k
            faces.extend(((a,c,b),(b,c,d)) if k==0 else ((a,b,c),(b,d,c)))
    # Seal roots/tips so the asset is a valid closed volume per sculpted section.
    for j in (0,segments):
        base=j*stride
        for k in range(across_count-1):
            a,b=base+k,base+k+1
            c,d=base+across_count+k,base+across_count+k+1
            faces.extend(((a,b,c),(b,d,c)) if j==0 else ((a,c,b),(b,c,d)))
    add(material,vertices,faces,category)


def build():
    scalp_shell()
    # 24 swept broad top layers instead of V2's 104 round lock cylinders.
    for i in range(24):
        az=(i*2.399963229728653+.24)%TAU
        polar=.23+.91*math.sqrt((i+.5)/24)
        if math.sin(az)>.7 and polar>1.02:
            polar=1.02
        p,n=scalp(az,polar,.001)
        swirl=unit((-math.sin(az),math.cos(az),-.16))
        direction=unit(.73*swirl+.34*n+np.array((0.,0.,-.20)))
        width=.010+.007*((i%7)/6)
        length=.029+.015*((i%5)/4)
        material=("DeepChestnutVolumes","WarmCopperPlanes","DeepChestnutVolumes",
                  "SoftDarkUnderlayers")[i%4]
        sculpted_blade(p,n,direction,width,length,material,"crown_planes",
                       twist=.10*math.sin(i*1.7))

    # Nine contiguous asymmetric swept bang masses; silhouette deliberately
    # keeps the brow/eyeline open rather than laying tubes across the forehead.
    for i in range(9):
        az=.63+(i/8)*1.87
        polar=.90+.09*math.sin(i*1.31)
        p,n=scalp(az,polar,.0025)
        direction=unit((-.28-.13*(i%3),.43,-.90))
        sculpted_blade(p,n,direction,.012+.005*((i%3)/2),
                       .047+.012*((i%4)/3),
                       "WarmCopperPlanes" if i%3==0 else "DeepChestnutVolumes",
                       "swept_fringe", twist=.08*(i-4)/4)

    for side in (-1,1):
        for i in range(9):
            az=(.05 if side==1 else math.pi-.05)+(i%3-1)*.12
            polar=1.20+(i//3)*.17
            p,n=scalp(az,polar,.0017)
            direction=unit((side*.55, -.05, -.72))
            sculpted_blade(p,n,direction,.008+.003*(i%3),
                           .033+.007*(i%4)/3,
                           "SoftDarkUnderlayers" if i%4==0 else
                           "DeepChestnutVolumes","temple_sheets")
    for i in range(12):
        az=math.pi+.16+(i/11)*(math.pi-.32)
        polar=1.54+.17*(i%4)/3
        p,n=scalp(az,polar,.0015)
        direction=unit((.17*math.sin(i*1.41),-.30,-.93))
        sculpted_blade(p,n,direction,.010+.003*(i%5)/4,
                       .043+.010*(i%3)/2,
                       "SoftDarkUnderlayers" if i%2 else
                       "DeepChestnutVolumes","layered_nape")


def glb_bytes():
    # Source-generated glTF 2.0 one StaticMesh, four matte PBR primitives.
    buf=bytearray()
    views=[]
    accessors=[]
    primitives=[]
    materials=[]
    summary={}
    all_verts=[]
    def align():
        while len(buf)%4:buf.append(0)
    def add_accessor(arr, width, component_type, target):
        arr=np.ascontiguousarray(arr)
        align()
        offset=len(buf)
        buf.extend(arr.tobytes())
        views.append({"buffer":0,"byteOffset":offset,
                      "byteLength":arr.nbytes,"target":target})
        a={"bufferView":len(views)-1,"componentType":component_type,
           "count":len(arr),"type":width}
        if width=="VEC3" and component_type==5126:
            a["min"]=np.min(arr,axis=0).astype(float).tolist()
            a["max"]=np.max(arr,axis=0).astype(float).tolist()
        accessors.append(a)
        return len(accessors)-1
    for name,color,rough in COLORS:
        meshes=PARTS[name]
        v=np.concatenate([m[0] for m in meshes]).astype(np.float32)
        faces=[]
        offset=0
        for verts,f in meshes:
            faces.append(f+offset)
            offset+=len(verts)
        f=np.concatenate(faces).astype(np.uint32)
        normals=np.zeros_like(v)
        t=v[f]
        fn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        for k in range(3):np.add.at(normals,f[:,k],fn)
        lengths=np.linalg.norm(normals,axis=1)
        if np.min(lengths)<1e-12:
            raise AssertionError("Zero vertex normal in "+name)
        normals=normals/lengths[:,None]
        mi=len(materials)
        materials.append({"name":name,"doubleSided":True,
            "pbrMetallicRoughness":{"baseColorFactor":color,
                                  "metallicFactor":0.,"roughnessFactor":rough}})
        primitives.append({"attributes":{
            "POSITION":add_accessor(v,"VEC3",5126,34962),
            "NORMAL":add_accessor(normals.astype(np.float32),"VEC3",5126,34962)},
            "indices":add_accessor(f.flatten(),"SCALAR",5125,34963),
            "material":mi,"mode":4})
        all_verts.append(v)
        summary[name]={"parts":len(meshes),"vertices":len(v),
                       "triangles":len(f)}
    align()
    positions=np.concatenate(all_verts)
    bounds=np.vstack((np.min(positions,axis=0),np.max(positions,axis=0)))
    dims=100*(bounds[1]-bounds[0])
    if not (np.all(dims>np.array((15.,15.,12.))) and
            np.all(dims<np.array((32.,33.,32.)))):
        raise AssertionError("Provisional hair GLB bounds out of range "+repr(dims))
    triangles=sum(v["triangles"] for v in summary.values())
    if triangles>40000 or len(primitives)!=4:
        raise AssertionError("Hair proxy triangle/material budget")
    doc={"asset":{"version":"2.0","generator":"TSTSS Ender broad-layer V3 static study"},
         "scene":0,"scenes":[{"nodes":[0]}],
         "nodes":[{"mesh":0,"name":"EnderBroadLayerHairV3_STATIC_REVIEW"}],
         "meshes":[{"name":"EnderBroadLayerHairV3_STATIC_REVIEW",
                    "primitives":primitives}],
         "accessors":accessors,"bufferViews":views,
         "buffers":[{"byteLength":len(buf)}],"materials":materials,
         "extras":{"review_only":True,"source_authored":True,
                   "creator_approved":False,"head_fit_verified":False,
                   "native_render_verified":False,"animation":False,
                   "rigged":False,"groom":False,"gameplay_asset":False,
                   "user_reference_pixels_included":False,
                   "current_appearance_target":"tousled dark-brown copper, art hold"}}
    js=json.dumps(doc,sort_keys=True,separators=(",",":")).encode("utf-8")
    js+=b" "*((-len(js))%4)
    return (struct.pack("<4sII",b"glTF",2,12+8+len(js)+8+len(buf))
            +struct.pack("<I4s",len(js),b"JSON")+js
            +struct.pack("<I4s",len(buf),b"BIN\x00")+buf),summary,dims


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir",required=True,type=Path)
    args=parser.parse_args()
    out=args.outdir.resolve()
    if not out.is_dir():
        raise RuntimeError("FAIL_CLOSED: output directory must exist")
    glb=out/"Ender_BroadLayerHair_V3_NONCANONICAL.glb"
    receipt=out/"Ender_BroadLayerHair_V3_SOURCE_RECEIPT.json"
    if glb.exists() or receipt.exists():
        raise RuntimeError("FAIL_CLOSED: source/evidence exists; no overwrite")
    build()
    data,stats,dims=glb_bytes()
    glb.write_bytes(data)
    result={"status":"SOURCE_STATIC_HAIR_V3_CREATED_ART_HOLD",
        "sha256":hashlib.sha256(data).hexdigest(),"file_bytes":len(data),
        "triangle_total":sum(v["triangles"] for v in stats.values()),
        "materials":list(stats),"parts":COUNTS,
        "dimensions_cm":[round(float(x),4) for x in dims],
        "creator_approved":False,"ue_native_import":False,
        "gameplay_animated":False,"skull_goggles_fit":False,
        "reference_likeness_verified":False}
    receipt.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
