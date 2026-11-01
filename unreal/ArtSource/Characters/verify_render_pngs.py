"""Independent PNG integrity/identity proof for Unreal cast renderer captures.

No Unreal dependency. A passing task log is not screenshot proof: actual
files must exist with expected dimensions, CRC-clean chunks and varied pixels.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

EXPECTED = {
    "Ender_front": (1280, 960),
    "Ender_profile": (1280, 960),
    "Ender_back": (1280, 960),
    "Ender_three_quarter": (1280, 960),
    "Five_cast_lineup": (1600, 900),
}
PNG_HEADER = b"\x89PNG\r\n\x1a\n"

def inspect_png(path, expected):
    data = Path(path).read_bytes()
    if len(data) < 60 or not data.startswith(PNG_HEADER):
        raise ValueError("Not a plausible PNG: " + str(path))
    offset = len(PNG_HEADER)
    seen_ihdr = False
    seen_idat = False
    seen_iend = False
    width = height = None
    compressed = bytearray()
    while offset + 12 <= len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        begin = offset + 8
        end = begin + size
        if end + 4 > len(data):
            raise ValueError("Truncated PNG chunk")
        kind = data[offset + 4:offset + 8]
        value = data[begin:end]
        crc = struct.unpack_from(">I", data, end)[0]
        if zlib.crc32(kind + value) & 0xffffffff != crc:
            raise ValueError("PNG CRC mismatch: " + str(kind))
        if not seen_ihdr:
            if kind != b"IHDR" or size != 13:
                raise ValueError("PNG must begin with IHDR")
            width, height, depth, mode, comp, filt, interlace = struct.unpack(">IIBBBBB", value)
            if (width, height) != expected or depth not in (8, 16) or mode not in (2, 6) or comp or filt or interlace:
                raise ValueError("Unexpected PNG format or dimensions")
            seen_ihdr = True
        elif kind == b"IDAT":
            seen_idat = True
            compressed.extend(value)
        elif kind == b"IEND":
            if size or end + 4 != len(data):
                raise ValueError("Malformed PNG end or trailing data")
            seen_iend = True
            break
        offset = end + 4
    if not (seen_ihdr and seen_idat and seen_iend) or len(compressed) < 8:
        raise ValueError("PNG lacks required chunks")
    # Validate DEFLATE payload as well as container CRCs.
    pixels = zlib.decompress(compressed)
    stride = width * (4 if mode == 6 else 3) * (depth // 8)
    if len(pixels) != height * (stride + 1):
        raise ValueError("PNG pixel payload length mismatch")
    # This is a weak non-blank sanity check, not a perceptual quality claim.
    if len(set(pixels[:min(len(pixels), 8192)])) < 3:
        raise ValueError("PNG pixel payload lacks variation")
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "width": width, "height": height, "format": "PNG",
            "pixel_coverage_valid": True}

def verify(directory):
    folder = Path(directory)
    report = {}
    for name, dimensions in EXPECTED.items():
        p = folder / (name + ".png")
        report[name] = inspect_png(p, dimensions)
    return {"status": "PNG_CONTAINER_AND_PIXEL_PASS", "images": report,
            "visual_likeness_approved": False, "cinematic_fidelity_approved": False}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_render_pngs.py <render-output-directory>")
    print(json.dumps(verify(sys.argv[1]), indent=2))
