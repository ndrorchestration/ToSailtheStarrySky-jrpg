"""Deterministic, original, static 3D Ender goggles — provisional review art only.

No purchased/reference mesh, no external dependencies. Units: meters.
Model-space: X = temple-to-temple, +Y = outward/forward, Z = up.
This is NOT a fitted MetaHuman accessory, rigged character, or approved art.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

PI = math.pi
PARTS = {}


def add(name, vertices, triangles):
    bucket = PARTS.setdefault(name, {"p": [], "f": []})
    offset = len(bucket["p"])
    bucket["p"].extend(vertices)
    bucket["f"].extend([(a+offset,b+offset,c+offset) for a,b,c in triangles])


def torus(name, center, ring_radius, tube_radius, segments=64, sides=12):
    cx,cy,cz=center
    vertices=[];triangles=[]
    for i in range(segments):
        ang=2*PI*i/segments
        for j in range(sides):
            phi=2*PI*j/sides
            d=ring_radius+tube_radius*math.cos(phi)
            vertices.append((cx+d*math.cos(ang),cy+tube_radius*math.sin(phi),cz+d*math.sin(ang)))
    for i in range(segments):
        for j in range(sides):
            a=i*sides+j;b=((i+1)%segments)*sides+j;c=((i+1)%segments)*sides+(j+1)%sides;d=i*sides+(j+1)%sides
            triangles.extend(((a,b,c),(a,c,d)))
    add(name,vertices,triangles)


def sphere(name, center, radius, rings=10, steps=14):
    cx,cy,cz=center
    verts=[];tri=[]
    for i in range(rings+1):
        polar=PI*i/rings
        for j in range(steps):
            az=2*PI*j/steps
            verts.append((cx+radius*math.sin(polar)*math.cos(az),cy+radius*math.cos(polar),cz+radius*math.sin(polar)*math.sin(az)))
    for i in range(rings):
        for j in range(steps):
            a=i*steps+j;b=(i+1)*steps+j;c=(i+1)*steps+(j+1)%steps;d=i*steps+(j+1)%steps
            if i>0:tri.append((a,b,d))
            if i<rings-1:tri.append((d,b,c))
    add(name,verts,tri)


def bowed_lens(cx):
    # Gently curved real geometry, with transparent PBR material.
    radii=[0.0,0.007,0.014,0.021,0.0238]
    sections=64; vertices=[];faces=[]
    for k,r in enumerate(radii):
        for j in range(sections):
            ang=2*PI*j/sections
            vertices.append((cx+r*math.cos(ang),0.0115+0.0032*(1-(r/0.024)**2),r*math.sin(ang)))
    for k in range(len(radii)-1):
        for j in range(sections):
            a=k*sections+j;b=k*sections+(j+1)%sections;c=(k+1)*sections+j;d=(k+1)*sections+(j+1)%sections
            faces.extend([(a,b,c),(b,d,c)])
    add('Emerald_glass_lenses',vertices,faces)


def tube(name, controls, radius, rings=10):
    vertices=[];tri=[]
    # Tangent-aligned tube sweep (controls are sufficiently dense).
    for i,pt in enumerate(controls):
        prev=controls[max(0,i-1)];nxt=controls[min(i+1,len(controls)-1)]
        tx,ty,tz=(nxt[j]-prev[j] for j in range(3))
        l=math.sqrt(tx*tx+ty*ty+tz*tz)
        tx,ty,tz=tx/l,ty/l,tz/l
        # For strap/bridge tube tangent, prefer Z as normal helper.
        ux,uy,uz=-ty,tx,0.0
        ln=math.sqrt(ux*ux+uy*uy+uz*uz)
        if ln<1e-6:ux,uy,uz=1.0,0.0,0.0
        else:ux,uy,uz=ux/ln,uy/ln,uz/ln
        vx,vy,vz=ty*uz-tz*uy,tz*ux-tx*uz,tx*uy-ty*ux
        for j in range(rings):
            ang=2*PI*j/rings;c=math.cos(ang)*radius;s=math.sin(ang)*radius
            vertices.append((pt[0]+c*ux+s*vx,pt[1]+c*uy+s*vy,pt[2]+c*uz+s*vz))
    for i in range(len(controls)-1):
        for j in range(rings):
            a=i*rings+j;b=i*rings+(j+1)%rings;c=(i+1)*rings+j;d=(i+1)*rings+(j+1)%rings
            tri.extend(((a,b,c),(b,d,c)))
    add(name,vertices,tri)


def band(name, path, width=0.014,thickness=0.0018):
    # Sewn leather strap following back-of-head arc; each segment gets 8 vertices.
    verts=[];faces=[]
    for i, (x,y) in enumerate(path):
        prev=path[max(i-1,0)];nxt=path[min(i+1,len(path)-1)]
        dx,dy=nxt[0]-prev[0],nxt[1]-prev[1]
        l=math.hypot(dx,dy);dx,dy=dx/l,dy/l
        nx,ny=-dy,dx
        for n,z in ((-1,-width/2),(1,width/2)):
            for depth in (-1,1):
                verts.append((x+depth*nx*thickness/2,y+depth*ny*thickness/2,z))
    for i in range(len(path)-1):
        a=i*4;b=(i+1)*4
        # outer and inner broad surfaces plus two narrow edges
        for k,h in ((0,0),(1,1),(2,2),(3,3)):
            an=a+k;bn=b+k;an2=a+((k+1)%4);bn2=b+((k+1)%4)
            faces.extend(((an,bn,an2),(an2,bn,bn2)))
    add(name,verts,faces)


def build():
    if PARTS:raise RuntimeError('generator cannot be run twice in same process')
    for cx in (-0.0345,0.0345):
        torus('Aged_brass_rims',(cx,0.0090,0),0.0262,0.00265)
        torus('Bevelled_gold_inlay',(cx,0.0131,0),0.0229,0.00075,64,8)
        torus('Deep_oiled_leather_gasket',(cx,0.0020,0),0.0268,0.0037)
        torus('Dark_metal_bezel',(cx,0.0060,0),0.0249,0.0011,64,8)
        bowed_lens(cx)
        # Actual small rivets at three edges of each ring.
        for ang in (0,2*PI/3,4*PI/3):
            sphere('Warm_brass_rivets',(cx+0.0262*math.cos(ang),0.0135,0.0262*math.sin(ang)),0.00115,8,10)
    # Curved arched central bridge, with two solder-like articulated terminals.
    path=[(x,0.015+0.0020*(1-(x/0.0115)**2),0.007+0.005*(1-(x/0.0115)**2)) for x in [-0.0115+i*0.023/24 for i in range(25)]]
    tube('Aged_brass_rims',path,0.0024,10)
    for x in (-0.0121,0.0121):sphere('Warm_brass_rivets',(x,0.015,0.007),0.0033,10,12)
    # Two temples, curved side arm via brass hinge and worn leather strap.
    for side in (-1,1):
        controls=[(side*(0.0600+i*0.0015),0.006-i*0.0014,0.000) for i in range(13)]
        tube('Warm_brass_hinges',controls,0.0027,10)
        path_side=[]
        for i in range(15):
            t=i/14
            path_side.append((side*(0.078+0.012*t),-0.016-0.082*t))
        band('Stitched_dark_leather_strap',path_side,0.017,0.0022)
        torus('Warm_brass_hinges',(side*0.078,-0.018,0),0.004,0.001,20,8)
        sphere('Warm_brass_rivets',(side*0.078,-0.018,0.009),0.0018,8,10)
    # Flexible rear section across skull, with subtle low-profile adjusting buckle.
    rear=[(-0.09+i*0.18/48,-0.098-0.035*math.sin(PI*i/48)) for i in range(49)]
    band('Stitched_dark_leather_strap',rear,0.017,0.0022)
    # Stitch points along top edge. Small full 3D points, not texture dots.
    for side in (-1,1):
        for i in range(7):
            t=(i+1)/8
            sphere('Thread_stitch_hardware',(side*(0.078+0.012*t),-0.016-0.082*t,0.0082),0.00048,5,8)


MATERIALS=[
 ('Aged_brass_rims',(0.49,0.31,0.12,1),0.84,0.36,'OPAQUE'),
 ('Bevelled_gold_inlay',(0.81,0.56,0.24,1),0.90,0.19,'OPAQUE'),
 ('Deep_oiled_leather_gasket',(0.075,0.048,0.032,1),0.0,0.88,'OPAQUE'),
 ('Dark_metal_bezel',(0.09,0.095,0.100,1),0.86,0.33,'OPAQUE'),
 ('Emerald_glass_lenses',(0.12,0.46,0.32,0.45),0.0,0.16,'BLEND'),
 ('Warm_brass_rivets',(0.66,0.43,0.19,1),0.87,0.29,'OPAQUE'),
 ('Warm_brass_hinges',(0.46,0.29,0.12,1),0.85,0.4,'OPAQUE'),
 ('Stitched_dark_leather_strap',(0.16,0.089,0.051,1),0.0,0.92,'OPAQUE'),
 ('Thread_stitch_hardware',(0.68,0.60,0.46,1),0.0,0.74,'OPAQUE'),
]


def encode(out:Path):
    build()
    g={'asset':{'version':'2.0','generator':'TSTSS custom deterministic Ender goggles prototype 1.0','extras':{'unit':'meters','model_coordinate_contract':'+X lateral, +Y forward, +Z up','art_status':'NONCANONICAL_NOT_FITTED'}},
       'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':'Ender_Resonance_Goggles_Review_Only'}],
       'meshes':[{'name':'Ender_resonance_goggles_prototype','primitives':[]}],
       'buffers':[],'bufferViews':[],'accessors':[],'materials':[]}
    data=bytearray();triangle_count=0;vertex_count=0
    def append(buffer, target=None):
        while len(data)%4:data.append(0)
        off=len(data);data.extend(buffer)
        obj={'buffer':0,'byteOffset':off,'byteLength':len(buffer)}
        if target:obj['target']=target
        g['bufferViews'].append(obj)
        return len(g['bufferViews'])-1
    def accessor(view,type,count,component,mins=None,maxs=None):
        obj={'bufferView':view,'byteOffset':0,'componentType':component,'count':count,'type':type}
        if mins is not None:obj['min']=mins;obj['max']=maxs
        g['accessors'].append(obj);return len(g['accessors'])-1
    for mat_index,(name,color,metal,rough,mode) in enumerate(MATERIALS):
        p={'name':name,'pbrMetallicRoughness':{'baseColorFactor':list(color),'metallicFactor':metal,'roughnessFactor':rough},'doubleSided':mode=='BLEND'}
        if mode=='BLEND':p['alphaMode']='BLEND'
        g['materials'].append(p)
        bucket=PARTS.get(name)
        if not bucket:continue
        verts=bucket['p'];faces=bucket['f']
        norms=[[0.,0.,0.] for _ in verts]
        for a,b,c in faces:
            va,vb,vc=verts[a],verts[b],verts[c]
            ux,uy,uz=(vb[k]-va[k] for k in range(3))
            vx,vy,vz=(vc[k]-va[k] for k in range(3))
            n=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx)
            for ix in (a,b,c):
                for k in range(3):norms[ix][k]+=n[k]
        normals=[]
        for n in norms:
            length=math.sqrt(sum(z*z for z in n))
            normals.append(tuple(z/length for z in n) if length>1e-12 else (0.,1.,0.))
        positions_bytes=b''.join(struct.pack('<fff',*map(float,p)) for p in verts)
        normals_bytes=b''.join(struct.pack('<fff',*map(float,p)) for p in normals)
        ix_bytes=b''.join(struct.pack('<III',*f) for f in faces)
        xs=[p[0] for p in verts];ys=[p[1] for p in verts];zs=[p[2] for p in verts]
        pi=accessor(append(positions_bytes,34962),'VEC3',len(verts),5126,[min(xs),min(ys),min(zs)],[max(xs),max(ys),max(zs)])
        ni=accessor(append(normals_bytes,34962),'VEC3',len(verts),5126)
        fi=accessor(append(ix_bytes,34963),'SCALAR',len(faces)*3,5125)
        g['meshes'][0]['primitives'].append({'attributes':{'POSITION':pi,'NORMAL':ni},'indices':fi,'material':mat_index,'mode':4})
        triangle_count+=len(faces);vertex_count+=len(verts)
    g['buffers'].append({'byteLength':len(data)})
    json_bytes=json.dumps(g,separators=(',',':'),sort_keys=True).encode('utf-8')
    while len(json_bytes)%4:json_bytes+=b' '
    while len(data)%4:data.append(0)
    length=12+8+len(json_bytes)+8+len(data)
    glb=b'glTF'+struct.pack('<II',2,length)+struct.pack('<I',len(json_bytes))+b'JSON'+json_bytes+struct.pack('<I',len(data))+b'BIN\0'+bytes(data)
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError('refuse to overwrite review asset')
    out.write_bytes(glb)
    extent=[min(p[k] for bucket in PARTS.values() for p in bucket['p']) for k in range(3)], [max(p[k] for bucket in PARTS.values() for p in bucket['p']) for k in range(3)]
    report={'status':'DETACHED_PROCEDURAL_3D_ACCESSORY_SOURCE_PASS_NOT_FITTED_OR_APPROVED','source_generation':'ORIGINAL_CODE_NO_EXTERNAL_ASSETS','file':out.name,'sha256':hashlib.sha256(glb).hexdigest(),'byte_length':len(glb),'triangle_count':triangle_count,'vertex_count':vertex_count,'material_count':len(g['materials']),'source_units':'meters','axis_contract':'X lateral Y forward Z up','bounds_min_m':extent[0],'bounds_max_m':extent[1],'canonical':False,'fitted_to_enders_face':False,'rigged':False,'native_unreal_import_verified':False,'shader_appearance_verified':False}
    receipt=out.with_suffix('.json')
    if receipt.exists():raise FileExistsError('refuse report overwrite')
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('Ender_goggles_noncanonical.glb'))
    args=parser.parse_args();print(json.dumps(encode(args.output),indent=2))
