#!/usr/bin/env python3
"""Editable Seabourne assembly; original mesh candidates, no paid generation.

Centimetre design datums are provisional. This exports one shared wing mesh
instanced FOUR times under independent azimuth nodes, plus a shared hull,
fixed forward dome and TWO attached foil assemblies. No gameplay access.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'Tools'))
from author_aureate_wing_glb import build as build_wing
from build_aureate_body_review import Surface, encode_glb
from build_aureate_fidelity_v2 import deterministic_payloads

STATUS = 'NONCANONICAL_EDITABLE_SEABOURNE_REVIEW'
STATIONS = (105., -25., -155., -285.)
ROOT_Z = 115.
DECK_Z = 33.
PITCH = 98.
FILES = {'hull': 'AureateWake_WhiteGoldHull_V2_REVIEW.glb',
         'bridge': 'AureateWake_BlueGlassBridge_V2_REVIEW.glb',
         'wing': 'AureateWake_Wing_Lookdev.glb',
         'mast': 'AureateWake_DorsalMount_REVIEW.glb',
         'foil': 'AureateWake_HydrofoilAssembly_REVIEW.glb'}


def material(name, color, metal=.7, rough=.3):
    return {'name': name, 'doubleSided': True, 'pbrMetallicRoughness': {
        'baseColorFactor': color, 'metallicFactor': metal, 'roughnessFactor': rough}}


MATERIALS = [material('ReviewWarmBrass', [.78,.47,.16,1]),
             material('ReviewNavyEngineering', [.025,.065,.10,1], .45),
             material('ReviewIvoryFoil', [.86,.82,.69,1], .25)]


def mount():
    brass, navy, ivory = [Surface(n) for n in ('MastBrass','MastNavy','MastIvory')]
    # Geometry is relative to the wing pivot, leaving actor scale at ONE.
    brass.tube((0,0,-82),(0,0,-75),12,16)
    navy.tube((0,0,-75),(0,0,-9),4.8,16)
    brass.tube((0,0,-12),(0,0,0),10,20)
    for side in (-1,1):
        brass.tube((0,side*10,-78),(0,side*3,-55),1.6,8)
        ivory.tube((0,side*4.9,-67),(0,side*4.9,-20),1.2,8)
    return encode_glb('DorsalMount', [brass,navy,ivory], MATERIALS)


def foil():
    brass, navy, ivory = [Surface(n) for n in ('FoilBrass','FoilNavy','FoilIvory')]
    # Root at the actual hull flank, strut down and outward to a curved foil.
    brass.tube((0,0,0),(0,0,-10),9,16)
    navy.tube((0,0,-7),(0,55,-105),5,12)
    brass.tube((0,46,-88),(0,57,-107),6,12)
    sections=[]
    profile=[(-1,0),(-.65,.075),(0,.105),(.65,.055),(1,0),(.4,-.035),(-.6,-.04)]
    for y,chord,z in ((22,56,-105),(45,72,-106),(90,65,-104),(137,39,-98),(153,5,-93)):
        sections.append([(chord*.5*x,y,z+chord*h) for x,h in profile])
    for a,b in zip(sections,sections[1:]):
        for i in range(len(a)):
            j=(i+1)%len(a)
            ivory.quad(a[i],b[i],b[j],a[j])
    for ring,reverse in ((sections[0],True),(sections[-1],False)):
        for i in range(1,len(ring)-1):
            a,b,c=ring[0],ring[i],ring[i+1]
            ivory.tri(a,c,b) if reverse else ivory.tri(a,b,c)
    brass.tube(sections[0][0],sections[1][0],1.,8)
    return encode_glb('HydrofoilAssembly', [brass,navy,ivory], MATERIALS)


def unpack(blob):
    magic,version,total=struct.unpack_from('<4sII',blob)
    if (magic,version,total)!=(b'glTF',2,len(blob)): raise ValueError('Invalid GLB')
    size,kind=struct.unpack_from('<I4s',blob,12)
    if kind!=b'JSON': raise ValueError('Missing JSON')
    doc=json.loads(blob[20:20+size])
    length,kind=struct.unpack_from('<I4s',blob,20+size)
    if kind!=b'BIN\0': raise ValueError('Missing BIN')
    return doc,blob[28+size:28+size+length]


def pack(doc,binary):
    raw=json.dumps(doc,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    raw+=b' '*(-len(raw)%4)
    binary+=b'\0'*(-len(binary)%4)
    return (struct.pack('<4sII',b'glTF',2,28+len(raw)+len(binary))+
            struct.pack('<I4s',len(raw),b'JSON')+raw+
            struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def quaternion_yaw(degrees):
    a=math.radians(degrees)*.5
    return [0,math.sin(a),0,math.cos(a)]


def assembly(parts,trim=(0.,0.,0.,0.)):
    if len(trim)!=4 or any(not math.isfinite(t) or abs(t)>35 for t in trim):
        raise ValueError('Exactly four finite provisional trims within +/-35 required')
    doc={'asset':{'version':'2.0','generator':'TSTSS shared-hull rig review'},
         'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[], 'meshes':[],
         'accessors':[], 'bufferViews':[], 'materials':[], 'images':[],
         'textures':[], 'samplers':[], 'buffers':[],
         'extras':{'authority':STATUS,'units':'meters','gameplay_authority':False,
                   'dimensions':'PROVISIONAL_NOT_CANON','continuous_clearance':'NOT_PROVEN'}}
    binary=bytearray()
    for key in ('hull','bridge','mast','foil','wing'):
        src,buf=unpack(parts[FILES[key]])
        offs={k:len(doc[k]) for k in ('accessors','bufferViews','materials','images','textures','samplers')}
        while len(binary)%4: binary.append(0)
        offset=len(binary); binary.extend(buf)
        for v in src['bufferViews']:
            v=copy.deepcopy(v); v['byteOffset']=v.get('byteOffset',0)+offset
            doc['bufferViews'].append(v)
        for a in src['accessors']:
            a=copy.deepcopy(a);a['bufferView']+=offs['bufferViews'];doc['accessors'].append(a)
        for im in src.get('images',[]):
            im=copy.deepcopy(im);im['bufferView']+=offs['bufferViews'];doc['images'].append(im)
        doc['samplers'].extend(copy.deepcopy(src.get('samplers',[])))
        for t in src.get('textures',[]):
            t=copy.deepcopy(t);t['source']+=offs['images'];t['sampler']+=offs['samplers'];doc['textures'].append(t)
        for m in src['materials']:
            m=copy.deepcopy(m)
            tex=m.get('pbrMetallicRoughness',{}).get('baseColorTexture')
            if tex: tex['index']+=offs['textures']
            doc['materials'].append(m)
        mesh=copy.deepcopy(src['meshes'][0])
        for p in mesh['primitives']:
            p['attributes']={k:v+offs['accessors'] for k,v in p['attributes'].items()}
            p['indices']+=offs['accessors'];p['material']+=offs['materials']
        doc['meshes'].append(mesh)
    nodes=[{'name':'AureateWake_SHARED_HULL_REVIEW','children':[1,2,3,5,7,9,11,12]},
           {'name':'SharedHull','mesh':0},
           {'name':'ForwardBridge_FIXED','mesh':1,'translation':[2.4,.95,0]}]
    for i,(x,yaw) in enumerate(zip(STATIONS,trim),1):
        a=math.radians(PITCH)*.5
        nodes.extend([{'name':f'SailAzimuth_{i}','mesh':2,
                       'translation':[x*.01,ROOT_Z*.01,0],
                       'rotation':quaternion_yaw(yaw),'children':[len(nodes)+1]},
                      {'name':f'DragonflyWing_{i}','mesh':4,
                       'rotation':[0,0,math.sin(a),math.cos(a)]}])
    for side,yaw in ((1,0),(-1,180)):
        nodes.append({'name':f'Hydrofoil_{"Starboard" if side==1 else "Port"}',
                      'mesh':3,'translation':[0,.05,-side*.72],
                      'rotation':quaternion_yaw(yaw)})
    doc['nodes']=nodes;doc['buffers']=[{'byteLength':len(binary)}]
    return pack(doc,bytes(binary))


def build(trim=(0.,0.,0.,0.)):
    parts=deterministic_payloads()
    wing,texture,_=build_wing()
    parts.update({FILES['wing']:wing,FILES['mast']:mount(),FILES['foil']:foil(),
                  'AureateWake_Wing_Albedo.png':texture})
    parts['AureateWake_SharedHull_Seabourne_REVIEW.glb']=assembly(parts,trim)
    report={'status':STATUS,'files':FILES,'source_units':'centimeters',
            'gltf_units':'meters','wing_count':4,'hydrofoil_count':2,
            'single_wing_mesh_instanced':True,'trim_degrees':list(trim),
            'mast_stations_x_cm':list(STATIONS),'wing_pivot_z_cm':ROOT_Z,
            'mast_foot_z_cm':DECK_Z,'bridge_translation_cm':[240,0,95],
            'source_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in parts.items()},
            'creator_3d_approval':False,'continuous_clearance_proven':False,
            'gameplay_modified':False,'starbourne_unlocked':False,
            'lineage':{'wing_source':'4fc7e6f7235a22346aed9372df2e5e4a0d1a54d2',
                       'body_source':'e336a7759f751cfdabf0cc0444e0817eaf6ae2f9 (local review checkpoint)',
                       'native_actor_baseline':'e8948deb01370a7bb5b2dadf38a0b1d8fe4694d7'}}
    parts['AureateWake_SharedHull_Manifest.json']=(json.dumps(report,indent=2,sort_keys=True)+'\n').encode()
    return parts,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--trim',type=float,nargs=4,default=(0.,0.,0.,0.))
    args=p.parse_args()
    parts,report=build(tuple(args.trim))
    dest=args.output_dir.resolve()
    if dest.exists() and any(dest.iterdir()): p.error('Refuse occupied output folder')
    dest.mkdir(parents=True,exist_ok=True)
    for name,data in parts.items(): (dest/name).write_bytes(data)
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=='__main__': main()
