#!/usr/bin/env python3
"""Fail-closed importer for the deterministic Aureate Wake BODY review pair.

No actor binding, level editing, gameplay, story or art promotion. Native import
is opt-in and requires a verified Unreal Editor with Interchange enabled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

from build_aureate_body_review import (STATUS, NAMES, MANIFEST, SCALE, build_payloads)

DESTINATIONS = (
    '/Game/TSTSS/Review/ShipArt/HullCandidateV1',
    '/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1',
)

class BodyReviewHold(ValueError):
    pass


def preflight(folder: Path) -> dict:
    folder=folder.resolve(strict=True)
    mpath=folder/MANIFEST
    if not mpath.is_file():raise BodyReviewHold('Missing exact named manifest')
    try: manifest=json.loads(mpath.read_text(encoding='utf-8'))
    except (ValueError,OSError,UnicodeError) as e:raise BodyReviewHold('Invalid review manifest') from e
    if manifest.get('status')!=STATUS or manifest.get('binding')!='UNAUTHORIZED_PENDING_NATIVE_IMPORT_AND_CREATOR_REVIEW':
        raise BodyReviewHold('Review-only authority/provenance missing')
    if ((manifest.get('source_units'),manifest.get('gltf_linear_units'),manifest.get('source_to_gltf_scale'),manifest.get('axis_remap'))
         !=('centimeters','meters',.01,'UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP')):
        raise BodyReviewHold('Meter and up-axis provenance missing')
    if manifest.get('orbiter_authorized') is not False or manifest.get('gameplay_modified') is not False:
        raise BodyReviewHold('No Orbiter/gameplay authority is permitted')
    if set(manifest.get('sha256',{}))!=set(NAMES):
        raise BodyReviewHold('Expected exactly the two review GLB receipts')
    claims={}
    for idx,name in enumerate(NAMES):
        path=folder/name
        if not path.is_file() or path.is_symlink() or path.stat().st_size>10_000_000:
            raise BodyReviewHold('Missing, symlinked, or oversized review GLB: '+name)
        payload=path.read_bytes()
        sha=hashlib.sha256(payload).hexdigest()
        if manifest['sha256'][name]!=sha:
            raise BodyReviewHold('GLB SHA mismatch: '+name)
        if len(payload)<36 or payload[:4]!=b'glTF':
            raise BodyReviewHold('Invalid GLB header')
        version,total=struct.unpack_from('<II',payload,4)
        if version!=2 or total!=len(payload):raise BodyReviewHold('GLB header size/version mismatch')
        length,kind=struct.unpack_from('<I4s',payload,12)
        if kind!=b'JSON' or length%4 or 20+length+8>len(payload):raise BodyReviewHold('Invalid GLB JSON chunk')
        bsize,btype=struct.unpack_from('<I4s',payload,20+length)
        if btype!=b'BIN\0' or bsize%4 or 20+length+8+bsize!=len(payload):
            raise BodyReviewHold('Invalid GLB BIN chunk length')
        try: doc=json.loads(payload[20:20+length])
        except (ValueError,UnicodeError) as e:raise BodyReviewHold('Invalid GLB JSON payload') from e
        extras=doc.get('extras',{})
        if extras.get('authority')!=STATUS or extras.get('sourceToGltfScale')!=SCALE or extras.get('axisRemap')!='UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP':
            raise BodyReviewHold('Missing embedded GLB review provenance')
        if (len(doc.get('meshes',[]))!=1 or len(doc['meshes'][0].get('primitives',[]))!=3 or
            len(doc.get('materials',[]))!=3 or doc['buffers'][0]['byteLength']>bsize):
            raise BodyReviewHold('Expected exactly three full-fidelity material sections')
        pmin=[];pmax=[]
        for mi,prim in enumerate(doc['meshes'][0]['primitives']):
            if not all(k in prim.get('attributes',{}) for k in ('POSITION','NORMAL','TEXCOORD_0')):
                raise BodyReviewHold('Missing shader mesh attribute')
            if prim.get('material')!=mi:raise BodyReviewHold('Unexpected material mapping')
            acc=doc['accessors'][prim['attributes']['POSITION']]
            if acc['count']<3 or acc['type']!='VEC3' or len(acc.get('min',[]))!=3:
                raise BodyReviewHold('Missing position bounds')
            pmin.append(acc['min']);pmax.append(acc['max'])
        mins=[min(p[i] for p in pmin) for i in range(3)]
        maxs=[max(p[i] for p in pmax) for i in range(3)]
        if idx==0 and not (-4.01<mins[0]<-3.95 and 3.95<maxs[0]<4.01 and -.55<mins[1]<-.20 and -.20<maxs[1]<.55):
            raise BodyReviewHold('Hull bounds not in intended 8m metre-scale envelope')
        if idx==1 and not (-1.02<mins[0]<-.88 and .88<maxs[0]<1.02 and -.76<mins[1]<-.5 and .48<maxs[1]<.65):
            raise BodyReviewHold('Bridge glass dome bounds not in meter-scale envelope')
        if idx==1 and doc['materials'][0].get('alphaMode')!='BLEND':
            raise BodyReviewHold('Bridge glazing requires reviewed glass material provenance')
        claims[name]={'sha256':sha,'bounds_m':{'min':mins,'max':maxs},
                      'material_sections':3,'target':DESTINATIONS[idx]}
    return {'status':STATUS,'authority':'REVIEW_ONLY_NOT_GAMEPLAY','verified':claims,
            'native_import':'NOT_ESTABLISHED','art_approval':'NOT_ESTABLISHED',
            'orbiter_authorized':False}


def import_review(folder:Path,receipt:dict)->dict:
    try: import unreal
    except ImportError as e:raise BodyReviewHold('Native Unreal Editor Python required') from e
    for required in ('EditorAssetLibrary','AssetImportTask','AssetToolsHelpers','StaticMesh','load_asset'):
        if not hasattr(unreal,required):raise BodyReviewHold('Missing Unreal import API: '+required)
    lib=unreal.EditorAssetLibrary
    for dest in DESTINATIONS:
        if lib.does_directory_exist(dest) and lib.list_assets(dest,recursive=True,include_folder=False):
            raise BodyReviewHold('Destination occupied; refusing overwrite: '+dest)
    result=[]
    for name,dest in zip(NAMES,DESTINATIONS):
        task=unreal.AssetImportTask()
        task.set_editor_property('filename',str((folder/name).resolve(strict=True)))
        task.set_editor_property('destination_path',dest)
        task.set_editor_property('automated',False)  # user/editor review of Interchange orientation/materials
        task.set_editor_property('replace_existing',False)
        task.set_editor_property('save',True)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        paths=list(task.get_editor_property('imported_object_paths'))
        models=[unreal.load_asset(path) for path in paths]
        if not any(isinstance(a,unreal.StaticMesh) for a in models if a is not None):
            # UE5.8 may place mesh in nested Interchange subfolders. Fail rather
            # than binding or promoting a partially imported candidate.
            raise BodyReviewHold('StaticMesh not found among imported objects for '+name)
        result.append({'filename':name,'imported_paths':paths,'review_destination':dest})
    return {'status':'NATIVE_IMPORTED_REVIEW_ONLY_NOT_BOUND_OR_APPROVED','assets':result,
            'art_approved':False,'orbiter_authorized':False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',required=True,type=Path)
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--check',action='store_true')
    m.add_argument('--import-review',action='store_true')
    args=p.parse_args(argv)
    try:
        receipt=preflight(args.folder)
        if args.import_review:
            receipt['native_import_result']=import_review(args.folder,receipt)
        print(json.dumps(receipt,indent=2,sort_keys=True))
    except (BodyReviewHold,OSError,ValueError,KeyError,IndexError,TypeError) as e:
        p.exit(1,'BODY LOOKDEV HOLD: '+str(e)+'\n')


if __name__=='__main__':main()
