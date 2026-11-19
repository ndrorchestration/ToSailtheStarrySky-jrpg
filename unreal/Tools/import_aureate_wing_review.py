#!/usr/bin/env python3
"""Preflight and opt-in import of one corrected Aureate Wake GLB, review-only.

Use --check offline. Run --import-review only inside Unreal Editor Python with
Interchange plugins enabled. Never binds an actor, edits a level or promotes art.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

FILENAME = 'AureateWake_Wing_Lookdev.glb'
ASSET_DIR = '/Game/TSTSS/Review/ShipArt/WingCandidateV2'
STATUS = 'NONCANONICAL_REVIEW_NOT_ART_ACCEPTED'


class WingReviewHold(ValueError):
    pass


def preflight(glb_path: Path, manifest_path: Path) -> dict:
    glb_path = glb_path.resolve(strict=True)
    manifest_path = manifest_path.resolve(strict=True)
    if glb_path.name != FILENAME or glb_path.suffix != '.glb':
        raise WingReviewHold('Expected the named one-wing review GLB')
    if glb_path.stat().st_size > 20_000_000:
        raise WingReviewHold('Unexpectedly oversized GLB')
    blob = glb_path.read_bytes()
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise WingReviewHold('Manifest unreadable or invalid') from exc
    if manifest.get('status') != STATUS:
        raise WingReviewHold('GLB manifest is not an isolated noncanonical review candidate')
    if (manifest.get('source_units'), manifest.get('gltf_linear_units'), manifest.get('source_to_gltf_scale')) != ('centimeters', 'meters', 0.01):
        raise WingReviewHold('Scale correction absent; old v1 GLB is NOT safe to import')
    expected = manifest.get('sha256', {}).get(FILENAME)
    digest = hashlib.sha256(blob).hexdigest()
    if expected != digest:
        raise WingReviewHold('GLB does not match its exact SHA-256 receipt')
    if len(blob) < 28 or blob[:4] != b'glTF':
        raise WingReviewHold('Invalid GLB header')
    version, total = struct.unpack_from('<II', blob, 4)
    if version != 2 or total != len(blob):
        raise WingReviewHold('Invalid GLB version or length')
    jlen, jtype = struct.unpack_from('<I4s', blob, 12)
    if jtype != b'JSON' or jlen % 4 or 20 + jlen + 8 > len(blob):
        raise WingReviewHold('Invalid JSON chunk')
    bsize, btype = struct.unpack_from('<I4s', blob, 20 + jlen)
    if btype != b'BIN\0' or bsize % 4 or 20 + jlen + 8 + bsize != len(blob):
        raise WingReviewHold('Invalid BIN chunk')
    try:
        doc = json.loads(blob[20:20+jlen])
    except (UnicodeDecodeError, ValueError) as exc:
        raise WingReviewHold('Invalid GLB JSON') from exc
    if doc.get('extras', {}).get('authority') != STATUS or doc.get('extras', {}).get('sourceToGltfScale') != 0.01:
        raise WingReviewHold('GLB lacks authoritative review-only meter-scale metadata')
    meshes = doc.get('meshes', [])
    if len(meshes) != 1 or len(meshes[0].get('primitives', [])) != 3:
        raise WingReviewHold('Expected one wing with three material submeshes')
    if len(doc.get('materials', [])) != 3:
        raise WingReviewHold('Expected membrane, rib and root material sections')
    for primitive in meshes[0]['primitives']:
        attrs = primitive.get('attributes', {})
        if not all(key in attrs for key in ('POSITION', 'NORMAL', 'TEXCOORD_0')):
            raise WingReviewHold('Incomplete mesh attribute map')
    pos = doc['accessors'][meshes[0]['primitives'][0]['attributes']['POSITION']]
    if not (abs(pos['max'][0] - 2.8) < 0.001 and abs(pos['min'][0]) < 0.001):
        raise WingReviewHold('One-wing membrane span is not 2.8 meters')
    if doc.get('buffers', [{}])[0].get('byteLength', 0) > bsize:
        raise WingReviewHold('GLB buffer length mismatch')
    return {'authority': 'REVIEW_ONLY_NOT_GAMEPLAY', 'sha256': digest,
            'membrane_span_cm': round(pos['max'][0] * 100, 2),
            'material_sections': len(doc['materials']), 'review_destination': ASSET_DIR}


def import_review(glb_path: Path, preflight_receipt: dict) -> dict:
    try:
        import unreal
    except ImportError as exc:
        raise WingReviewHold('Unreal Editor Python required for --import-review') from exc
    required = ('EditorAssetLibrary', 'AssetImportTask', 'AssetToolsHelpers', 'StaticMesh', 'load_asset')
    if not all(hasattr(unreal, name) for name in required):
        raise WingReviewHold('This Python environment does not expose Unreal Editor import APIs')
    library = unreal.EditorAssetLibrary
    if library.does_directory_exist(ASSET_DIR) and library.list_assets(ASSET_DIR, recursive=True, include_folder=False):
        raise WingReviewHold('Destination already contains assets: refusing overwrite or reimport')
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', str(glb_path.resolve(strict=True)))
    task.set_editor_property('destination_path', ASSET_DIR)
    task.set_editor_property('automated', False)  # Artist must choose/inspect Interchange pipeline.
    task.set_editor_property('replace_existing', False)
    task.set_editor_property('save', True)
    # Editorial preview, no level edits, actor binding, feature activation, or save modifications.
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths = list(task.get_editor_property('imported_object_paths'))
    models = [unreal.load_asset(p) for p in paths]
    if not any(isinstance(asset, unreal.StaticMesh) for asset in models if asset is not None):
        raise WingReviewHold('No StaticMesh returned by Interchange; manually inspect candidate folder')
    return {'candidate_assets': paths, 'status': 'IMPORTED_REVIEW_ONLY_NOT_ART_ACCEPTED',
            'source_sha256': preflight_receipt['sha256']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--glb', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--import-review', action='store_true')
    args = parser.parse_args(argv)
    try:
        info = preflight(args.glb, args.manifest)
        if args.import_review:
            info['import_result'] = import_review(args.glb, info)
        print(json.dumps(info, indent=2))
    except (WingReviewHold, OSError, KeyError, TypeError, IndexError) as exc:
        parser.exit(1, 'WING IMPORT HOLD: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()