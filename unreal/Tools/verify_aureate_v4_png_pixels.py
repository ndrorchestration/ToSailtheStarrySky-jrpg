"""Stdlib-only conservative PNG pixel integrity for review-only UE screenshot receipts.

Checks actual PNG chunks, zlib scanlines, filters, pixels and basic dynamic
range. This is NOT an aesthetic, creator-approval or exposure-quality verdict.
"""
import struct
import zlib

PNG_SIG = b'\x89PNG\r\n\x1a\n'
EXPECTED_DIMENSIONS = (1280, 720)


def _paeth(a, b, c):
    p = a + b - c
    da, db, dc = abs(p - a), abs(p - b), abs(p - c)
    if da <= db and da <= dc:
        return a
    if db <= dc:
        return b
    return c


def inspect_png_pixels(raw, dimensions=EXPECTED_DIMENSIONS):
    """Return conservative content metrics or fail closed on malformed/flat PNG."""
    if not isinstance(raw, bytes) or not raw.startswith(PNG_SIG):
        raise ValueError('PNG signature absent')
    pos = len(PNG_SIG)
    header = None
    chunks = []
    idat = bytearray()
    ended = False
    while pos + 12 <= len(raw):
        length = struct.unpack_from('>I', raw, pos)[0]
        kind = raw[pos + 4:pos + 8]
        next_pos = pos + 12 + length
        if next_pos > len(raw):
            raise ValueError('Truncated PNG chunk')
        data = raw[pos + 8:pos + 8 + length]
        crc = struct.unpack_from('>I', raw, pos + 8 + length)[0]
        if zlib.crc32(kind + data) & 0xffffffff != crc:
            raise ValueError('PNG chunk CRC mismatch')
        chunks.append(kind)
        if kind == b'IHDR':
            if header is not None or len(data) != 13 or len(chunks) != 1:
                raise ValueError('Invalid or repeated PNG IHDR')
            header = struct.unpack('>IIBBBBB', data)
        elif kind == b'IDAT':
            if header is None or ended:
                raise ValueError('PNG IDAT out of order')
            idat.extend(data)
            if len(idat) > 32 * 1024 * 1024:
                raise ValueError('PNG IDAT is too large')
        elif kind == b'IEND':
            if length != 0 or header is None:
                raise ValueError('Invalid PNG IEND')
            ended = True
            pos = next_pos
            break
        elif kind[0] & 0x20 == 0 and kind not in (b'PLTE',):
            raise ValueError('Unsupported critical PNG chunk')
        pos = next_pos
    if not ended or pos != len(raw) or b'IDAT' not in chunks:
        raise ValueError('Missing IEND, IDAT, or trailing bytes')
    width, height, bit_depth, color_type, comp, filt, interlace = header
    if (width, height) != dimensions or bit_depth != 8 or color_type not in (2, 6) or (comp, filt, interlace) != (0, 0, 0):
        raise ValueError('Unsupported screenshot PNG dimensions/format')
    channels = 3 if color_type == 2 else 4
    stride = width * channels
    expected = height * (stride + 1)
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(bytes(idat), expected + 1)
    decoded += decoder.flush()
    if len(decoded) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError('PNG IDAT scanlines incomplete or excessive')
    previous = bytearray(stride)
    hist = set()
    channel_values = set()
    valid_samples = 0
    sample_count = 0
    for row in range(height):
        offset = row * (stride + 1)
        filter_type = decoded[offset]
        data = decoded[offset + 1:offset + 1 + stride]
        if filter_type > 4:
            raise ValueError('Unsupported PNG row filter')
        output = bytearray(stride)
        for i, byte in enumerate(data):
            left = output[i - channels] if i >= channels else 0
            above = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            pred = (0, left, above, (left + above) // 2,
                    _paeth(left, above, upper_left))[filter_type]
            output[i] = (byte + pred) & 255
        previous = output
        # Sample every 16 pixels and every fourth scanline; ~14k samples at 720p.
        if row % 4:
            continue
        for x in range(0, width, 16):
            base = x * channels
            r, g, b = output[base:base + 3]
            # Unreal screenshots may store zero alpha while preserving valid RGB.
            # Inspect visible RGB; keep alpha/material acceptance for later review.
            luminance = (54 * r + 183 * g + 19 * b) // 256
            hist.add(luminance)
            channel_values.add((r // 8, g // 8, b // 8))
            sample_count += 1
            if 4 < luminance < 250:
                valid_samples += 1
    if not sample_count or len(hist) < 12 or max(hist) - min(hist) < 20:
        raise ValueError('Screenshot appears flat/black/white by sampled luminance')
    if len(channel_values) < 12 or valid_samples / sample_count < 0.025:
        raise ValueError('Screenshot lacks varied, visible color content')
    return {'dimensions': [width, height], 'color_type': color_type,
            'sample_count': sample_count, 'distinct_luma_values': len(hist),
            'luma_min': min(hist), 'luma_max': max(hist),
            'visible_sample_fraction': round(valid_samples / sample_count, 5),
            'color_sample_buckets': len(channel_values),
            'art_approved': False, 'contrast_review_pending': True}
