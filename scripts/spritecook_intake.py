#!/usr/bin/env python3
"""Stage downloaded SpriteCook PNG artwork with checksums and provenance.

Offline only: no API calls, credit spending, Git merges, or Godot scene edits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
MAX_FILE_SIZE = 64 * 1024 * 1024
MAX_DIMENSION = 8192
SLUG = re.compile(r'^[a-z][a-z0-9-]{2,63}$')
ASSET_ID = re.compile(r'^[A-Za-z0-9_:-]{3,128}$')


class IntakeError(ValueError):
    pass


def inspect_png(data: bytes) -> dict:
    """Verify PNG signature, chunk bounds/CRCs and basic header integrity."""
    if len(data) < 33 or data[:8] != PNG_SIGNATURE:
        raise IntakeError('File is not a PNG')
    pos = 8
    seen_ihdr = seen_idat = seen_iend = False
    width = height = color_type = None
    alpha_capable = False
    while pos + 12 <= len(data):
        length = struct.unpack_from('>I', data, pos)[0]
        if length > MAX_FILE_SIZE or pos + 12 + length > len(data):
            raise IntakeError('Malformed PNG chunk length')
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        crc = struct.unpack_from('>I', data, pos + 8 + length)[0]
        if crc != (zlib.crc32(ctype + chunk) & 0xffffffff):
            raise IntakeError('PNG checksum mismatch')
        if not seen_ihdr and ctype != b'IHDR':
            raise IntakeError('PNG missing initial IHDR')
        if ctype == b'IHDR':
            if seen_ihdr or length != 13:
                raise IntakeError('Repeated or invalid IHDR')
            width, height, bit_depth, color_type, compression, filt, interlace = struct.unpack('>IIBBBBB', chunk)
            if not (1 <= width <= MAX_DIMENSION and 1 <= height <= MAX_DIMENSION):
                raise IntakeError('PNG dimensions out of bounds')
            if color_type not in (0, 2, 3, 4, 6) or compression != 0 or filt != 0 or interlace > 1:
                raise IntakeError('Unsupported PNG header')
            alpha_capable = color_type in (4, 6)
            seen_ihdr = True
        elif ctype == b'tRNS':
            alpha_capable = True
        elif ctype == b'IDAT':
            seen_idat = True
        elif ctype == b'IEND':
            if length != 0:
                raise IntakeError('Invalid IEND')
            seen_iend = True
            pos += length + 12
            break
        pos += length + 12
    if not (seen_ihdr and seen_idat and seen_iend) or pos != len(data):
        raise IntakeError('Incomplete PNG or unexpected trailing bytes')
    return {'width': width, 'height': height, 'color_type': color_type, 'alpha_capable': alpha_capable}


def stage(args: argparse.Namespace) -> dict:
    if not SLUG.fullmatch(args.slug):
        raise IntakeError('Slug must be 3-64 lowercase letters/numbers/hyphens and start with a letter')
    if not ASSET_ID.fullmatch(args.asset_id):
        raise IntakeError('Provide the real SpriteCook asset ID')
    if not args.source_url.startswith('https://'):
        raise IntakeError('Source URL must be https://')
    if args.credit_cost is not None and not (0 <= args.credit_cost <= 40):
        raise IntakeError('Credit cost must be 0-40')
    before, after = args.balance_before, args.balance_after
    if (before is None) != (after is None):
        raise IntakeError('Provide both before and after balance values')
    if before is not None:
        if not (0 <= after <= before <= 40):
            raise IntakeError('Invalid free credit balance')
        if args.credit_cost is None or before - after != args.credit_cost:
            raise IntakeError('Reported cost differs from balance change')
    if args.credit_cost is not None and args.credit_cost > args.max_per_asset:
        raise IntakeError('Reported credit cost exceeds per-asset limit')
    src = Path(args.png).resolve(strict=True)
    if not src.is_file() or src.suffix.lower() != '.png' or src.stat().st_size > MAX_FILE_SIZE:
        raise IntakeError('Input must be PNG no larger than 64 MiB')
    data = src.read_bytes()
    info = inspect_png(data)
    if not info['alpha_capable'] and not args.allow_opaque:
        raise IntakeError('PNG has no alpha support; use --allow-opaque for intentional opaque art')
    prompt = Path(args.prompt_file).read_text(encoding='utf-8').strip()
    if not prompt or len(prompt) > 12000:
        raise IntakeError('Prompt must be 1-12000 characters')
    dest_dir = Path(args.dest).resolve()
    dest_png = dest_dir / (args.slug + '.png')
    manifest_path = dest_dir / (args.slug + '.provenance.json')
    if dest_png.exists() or manifest_path.exists():
        raise IntakeError('Destination exists; candidate art must not be overwritten')
    sha = hashlib.sha256(data).hexdigest()
    receipt = {
        'schema': 'tstss-spritecook-candidate-v1',
        'status': 'CANDIDATE_NOT_APPROVED',
        'asset_id': args.asset_id,
        'source_url': args.source_url,
        'provider': 'SpriteCook',
        'source_sha256': sha,
        'width': info['width'],
        'height': info['height'],
        'alpha_capable': info['alpha_capable'],
        'credit_cost_reported': args.credit_cost,
        'credit_debit_verified_by_before_after_balance': before is not None,
        'balance_before': before,
        'balance_after': after,
        'prompt': prompt,
        'date_staged_utc': datetime.now(timezone.utc).isoformat(),
        'usage_note': 'Free assets are public; provenance is not artistic or release approval.',
        'qa_required': ['creator reference check', 'native Godot screenshot', 'creator acceptance'],
    }
    dest_dir.mkdir(parents=True, exist_ok=True)
    created_png = False
    try:
        with dest_png.open('xb') as out:
            created_png = True
            out.write(data)
        with manifest_path.open('x', encoding='utf-8') as out:
            json.dump(receipt, out, indent=2, ensure_ascii=False)
            out.write('\n')
    except BaseException:
        if created_png:
            dest_png.unlink(missing_ok=True)
        raise
    return {'png': str(dest_png), 'manifest': str(manifest_path), 'sha256': sha}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--png', required=True)
    p.add_argument('--slug', required=True)
    p.add_argument('--asset-id', required=True)
    p.add_argument('--source-url', required=True)
    p.add_argument('--prompt-file', required=True)
    p.add_argument('--dest', default='assets/spritecook-candidates')
    p.add_argument('--credit-cost', type=int, default=None, help='Observed cost, not estimate')
    p.add_argument('--balance-before', type=int)
    p.add_argument('--balance-after', type=int)
    p.add_argument('--max-per-asset', type=int, default=12)
    p.add_argument('--allow-opaque', action='store_true')
    args = p.parse_args(argv)
    try:
        print(json.dumps(stage(args), indent=2))
        return 0
    except (IntakeError, OSError) as exc:
        print('INTAKE FAILED: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
