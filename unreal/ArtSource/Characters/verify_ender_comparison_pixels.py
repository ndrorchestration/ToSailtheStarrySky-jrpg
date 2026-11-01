"""Inspect *actual* native Unreal compare frames for two visible silhouettes.

This is a conservative pixel-coverage gate, not a likeness/rig/art approval.
Uses only Python's standard library; decodes PNG filters 0..4 (RGB/RGBA,
8-bit, noninterlaced). All other formats fail closed. An earlier CRC/IDAT
validator independently checks the full container in verify_report.
"""
import argparse
import json
from pathlib import Path
import statistics
import struct
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def decode_png_rgb(path):
    data = Path(path).read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError("Not a PNG")
    at = len(PNG_MAGIC)
    compressed = bytearray()
    size = None
    channels = None
    reached_end = False
    while at + 12 <= len(data):
        length = struct.unpack_from(">I", data, at)[0]
        kind = data[at + 4: at + 8]
        end = at + 8 + length
        if end + 4 > len(data):
            raise ValueError("Truncated PNG chunk")
        payload = data[at + 8:end]
        crc = struct.unpack_from(">I", data, end)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError("PNG chunk CRC mismatch")
        at = end + 4
        if kind == b"IHDR":
            if size is not None or length != 13:
                raise ValueError("Invalid PNG IHDR")
            width, height, depth, mode, comp, filt, interlace = struct.unpack(
                ">IIBBBBB", payload)
            if not (0 < width <= 4096 and 0 < height <= 4096):
                raise ValueError("Unsupported PNG dimensions")
            if depth != 8 or mode not in (2, 6) or comp or filt or interlace:
                raise ValueError("Only 8-bit noninterlaced RGB/RGBA PNG supported")
            channels = 3 if mode == 2 else 4
            size = (width, height)
        elif kind == b"IDAT":
            if size is None:
                raise ValueError("Missing PNG IHDR")
            compressed.extend(payload)
        elif kind == b"IEND":
            if length != 0 or at != len(data):
                raise ValueError("Malformed PNG IEND or trailing bytes")
            reached_end = True
            break
    if not reached_end or not compressed or size is None:
        raise ValueError("Missing PNG data/end")
    width, height = size
    stride = width * channels
    inflater = zlib.decompressobj()
    raw = inflater.decompress(bytes(compressed), height * (stride + 1) + 1)
    raw += inflater.flush()
    if not inflater.eof or len(raw) != height * (stride + 1):
        raise ValueError("Invalid or oversized PNG pixel stream")
    rows = []
    previous = bytearray(stride)
    cursor = 0
    for _ in range(height):
        method = raw[cursor]
        scanline = raw[cursor + 1: cursor + stride + 1]
        cursor += stride + 1
        if method > 4:
            raise ValueError("Invalid PNG scanline filter")
        current = bytearray(stride)
        for i, val in enumerate(scanline):
            left = current[i - channels] if i >= channels else 0
            above = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if method == 0:
                predictor = 0
            elif method == 1:
                predictor = left
            elif method == 2:
                predictor = above
            elif method == 3:
                predictor = (left + above) // 2
            else:
                p = left + above - upper_left
                distances = (abs(p - left), abs(p - above), abs(p - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            current[i] = (val + predictor) & 255
        rows.append(bytes(current))
        previous = current
    return size, channels, rows


def check_pair_coverage(path, expected=(1280, 720), min_fraction=0.012):
    """Require visible, non-clipped subjects in *both* separated image regions."""
    (width, height), channels, rows = decode_png_rgb(path)
    if (width, height) != tuple(expected):
        raise ValueError("Native comparison screenshot size mismatch")

    # Sample four image corners to estimate a stable empty-stage background.
    corners = []
    for y in (max(0, height // 40), height - 1 - max(0, height // 40)):
        row = rows[y]
        for x in (max(0, width // 40), width - 1 - max(0, width // 40)):
            at = x * channels
            corners.append(tuple(row[at:at + 3]))
    bg = [statistics.median(px[channel] for px in corners) for channel in range(3)]
    coverage = {}
    for key, lo, hi in (("EnderV1_left", 0.06, 0.46),
                        ("EnderV2_right", 0.54, 0.94)):
        n = 0
        visible = 0
        white = 0
        # Sparse, deterministic scan to keep validation suitable for CI.
        for y in range(int(height * .10), int(height * .92), 2):
            row = rows[y]
            for x in range(int(width * lo), int(width * hi), 2):
                at = x * channels
                rgb = row[at:at + 3]
                n += 1
                if all(channel >= 248 for channel in rgb):
                    white += 1
                if (max(abs(rgb[i] - bg[i]) for i in range(3)) > 36
                        and max(rgb) > 28):
                    visible += 1
        fraction = visible / n if n else 0.
        blown_out = white / n if n else 1.
        if fraction < min_fraction:
            raise ValueError(key + " appears missing, black or background-only")
        if blown_out > 0.20:
            raise ValueError(key + " overexposed/clipped")
        coverage[key] = {
            "foreground_fraction": round(fraction, 4),
            "white_clip_fraction": round(blown_out, 4),
        }
    l = coverage["EnderV1_left"]["foreground_fraction"]
    r = coverage["EnderV2_right"]["foreground_fraction"]
    if min(l, r) == 0 or max(l, r) / min(l, r) > 8:
        raise ValueError("Comparison camera failed to frame both subjects comparably")
    return {
        "status": "BOTH_IMAGE_HALVES_VISIBLE_NOT_LIKENESS_APPROVAL",
        "observed_background_rgb": bg,
        "regions": coverage,
        "creator_approved": False,
        "rigging_verified": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("native_png", type=Path)
    args = parser.parse_args()
    print(json.dumps(check_pair_coverage(args.native_png), indent=2))
