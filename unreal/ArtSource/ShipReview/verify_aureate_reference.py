#!/usr/bin/env python3
"""Verify the original, creator-approved Aureate Wake PNG against its art contract.

Pure Python. Does NOT import, generate, or transform the approved reference.
Art approval is separate from geometric, mechanical and Unreal runtime proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

CONTRACT = Path(__file__).with_name("aureate_wake_approved_art_contract.json")


class ArtReferenceHold(ValueError):
    pass


def verify_reference(original: Path, contract_path: Path = CONTRACT) -> dict:
    with contract_path.open("r", encoding="utf-8") as fh:
        contract = json.load(fh)
    if contract.get("authority") != "CREATOR_APPROVED_VISUAL_REFERENCE":
        raise ArtReferenceHold("Expected creator-approved visual-reference authority")
    metadata = contract.get("approved_image", {})
    if (not original.is_file() or original.is_symlink() or
            original.name != metadata.get("filename")):
        raise ArtReferenceHold("Expected the unchanged approved original PNG")
    size = original.stat().st_size
    if size != metadata.get("size_bytes"):
        raise ArtReferenceHold("Reference file size disagrees with approved original")
    digest = hashlib.sha256()
    with original.open("rb") as fh:
        hdr = fh.read(24)
        if len(hdr) != 24 or hdr[:8] != b"\x89PNG\r\n\x1a\n":
            raise ArtReferenceHold("Invalid original PNG signature")
        if hdr[12:16] != b"IHDR" or struct.unpack(">I", hdr[8:12])[0] != 13:
            raise ArtReferenceHold("Original PNG is missing its valid IHDR header")
        width, height = struct.unpack(">II", hdr[16:24])
        if (width, height) != (metadata.get("width_px"), metadata.get("height_px")):
            raise ArtReferenceHold("Original reference dimensions disagree with approval")
        digest.update(hdr)
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != metadata.get("sha256"):
        raise ArtReferenceHold("Reference pixels/file changed; exact original checksum mismatch")
    if not contract.get("story_lock", {}).get("orbiter_locked", False):
        raise ArtReferenceHold("Original art contract must not unlock Orbiter")
    return {
        "status": "CREATOR_APPROVED_ORIGINAL_PNG_BYTES_VERIFIED",
        "sha256": digest.hexdigest(),
        "width": width,
        "height": height,
        "file_size": size,
        "implementation_authorized_for_review": True,
        "model_approved": False,
        "native_unreal_import_proven": False,
        "orbiter_unlocked": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    args = parser.parse_args(argv)
    try:
        result = verify_reference(args.original, args.contract)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (ArtReferenceHold, ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, "ART REFERENCE HOLD: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
