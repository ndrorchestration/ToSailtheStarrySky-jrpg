#!/usr/bin/env python3
"""Read-only, fail-closed receipt preflight for a real UE PNG; not a renderer."""
import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

PRE_STRUT_SEABORNE_SHA256 = "7df11a853a970a5e10c4984a87ff490f5099a84aec13a1711282f4b0873ee302"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

def validate_png_container(raw):
    """Validate bounded PNG chunk structure and CRC, not source authenticity."""
    if len(raw) < 8 or raw[:8] != PNG_MAGIC or len(raw) > 64 * 1024 * 1024:
        raise ValueError("missing PNG signature or excessive file size")
    position, count, saw_idat, saw_iend = 8, 0, False, False
    while position < len(raw):
        if len(raw) - position < 12:
            raise ValueError("truncated PNG chunk")
        length = struct.unpack_from(">I", raw, position)[0]
        if length > len(raw) - position - 12:
            raise ValueError("invalid PNG chunk size")
        chunk_type = raw[position + 4:position + 8]
        payload = raw[position + 8:position + 8 + length]
        expected_crc = struct.unpack_from(">I", raw, position + 8 + length)[0]
        actual_crc = zlib.crc32(chunk_type + payload) & 0xffffffff
        if expected_crc != actual_crc:
            raise ValueError("PNG chunk CRC mismatch")
        if count == 0:
            if chunk_type != b"IHDR" or length != 13:
                raise ValueError("first PNG chunk must be 13-byte IHDR")
        elif chunk_type == b"IHDR":
            raise ValueError("duplicate PNG IHDR")
        if chunk_type == b"IDAT":
            saw_idat = True
        if chunk_type == b"IEND":
            if length != 0 or not saw_idat:
                raise ValueError("missing IDAT or invalid IEND")
            saw_iend = True
            position += length + 12
            if position != len(raw):
                raise ValueError("unexpected bytes after PNG IEND")
            break
        position += length + 12
        count += 1
    if not saw_iend:
        raise ValueError("PNG missing IEND")
    return struct.unpack(">II", raw[16:24])


def check(meta):
    required = ["source_sha", "build_sha", "capture_path", "capture_sha256",
                "engine_version", "renderer", "map", "camera", "capture_utc",
                "form", "pixel_width", "pixel_height", "post_strut_build"]
    if any(k not in meta for k in required):
        raise ValueError("missing capture receipt fields")
    if not all(re.fullmatch("[0-9a-f]{40}", meta[k]) for k in ("source_sha","build_sha")):
        raise ValueError("exact source/build commit SHAs required")
    if meta["source_sha"] != meta["build_sha"]:
        raise ValueError("capture must be tied to exact built source head")
    if meta["engine_version"] != "5.8.4" or meta["renderer"] != "D3D12":
        raise ValueError("native UE 5.8.4 D3D12 claim required")
    if meta["form"] != "Seaborne" or meta["post_strut_build"] is not True:
        raise ValueError("post-strut Seaborne capture required")
    if not meta["map"] or not meta["camera"] or not meta["capture_utc"]:
        raise ValueError("map, camera and UTC capture time required")
    if (meta["pixel_width"], meta["pixel_height"]) != (1280, 720):
        raise ValueError("this bounded review requires 1280x720")
    if not re.fullmatch("[0-9a-f]{64}", meta["capture_sha256"]):
        raise ValueError("64-digit screenshot digest required")
    if meta["capture_sha256"] == PRE_STRUT_SEABORNE_SHA256:
        raise ValueError("known pre-strut Seaborne PNG refused")
    path = Path(meta["capture_path"])
    if not path.is_file():
        raise ValueError("no screenshot at capture_path; NOT_VERIFIED")
    raw = path.read_bytes()
    width, height = validate_png_container(raw)
    if (width, height) != (1280, 720):
        raise ValueError("actual PNG dimensions mismatch")
    if hashlib.sha256(raw).hexdigest() != meta["capture_sha256"]:
        raise ValueError("PNG SHA-256 mismatch")
    return "PNG_INTEGRITY_PASS__NATIVE_RENDER_PROVENANCE_AND_VISUAL_REVIEW_PENDING"

def self_test():
    template = {"source_sha":"a"*40,"build_sha":"a"*40,
                "capture_path":"/this-file-should-not-exist-tstss.png",
                "capture_sha256":"b"*64,"engine_version":"5.8.4",
                "renderer":"D3D12","map":"/Game/Review","camera":"ReviewCamera",
                "capture_utc":"2026-11-01T20:00:00Z","form":"Seaborne",
                "pixel_width":1280,"pixel_height":720,"post_strut_build":True}
    for bad in ({**template, "capture_sha256":PRE_STRUT_SEABORNE_SHA256},
                {**template, "post_strut_build":False},
                {**template, "renderer":"CPU"},
                template):
        try:
            check(bad)
        except ValueError:
            continue
        raise AssertionError("negative control accepted")
    print("PASS: four fail-closed preflight negative controls (no native capture)")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("receipt", nargs="?")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.receipt:
        p.error("receipt JSON required")
    try:
        result = check(json.loads(Path(a.receipt).read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        print("NOT_VERIFIED:", exc)
        raise SystemExit(1)
    print(result)
    print("This is local file integrity only; source provenance, native D3D12 authenticity,")
    print("two strut attachments, visual/collision suitability and creator approval remain UNVERIFIED.")

if __name__ == "__main__":
    main()
