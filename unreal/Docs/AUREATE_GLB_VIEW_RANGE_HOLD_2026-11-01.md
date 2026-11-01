# Aureate Wake — GLB buffer-view start and accessor range HOLD

**2026-11-01 · Unreal 5.8.4 review · ENGINE-FREE QA ONLY · NOT CANONICAL ART**

## Defect and correction

The previous complete-vertex auditor combined `bufferView.byteOffset` and `accessor.byteOffset` before verifying range. A negative accessor offset could be cancelled by a positive buffer-view offset, making the reader consume bytes *before* the declared view. Existing checks only enforced the end of the view and beginning of the BIN chunk. Malformed or malicious GLB geometry could therefore be screened against incorrect data.

This additive review draft stacks directly on [PR #670](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/670), retaining its exact Windows-bound generated-GLB receipt SHA `04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73` as a **historical receipt from the parent SHA**, not transferring native success to this new draft.

The reader now validates the buffer-view offset, accessor offset, byte length, and stride independently. Offsets must be nonnegative, four-byte aligned integer values (not booleans); stride must be at least 12 bytes and four-byte aligned. Every VEC3 float32 position must be fully contained within its *own* declared view, which must itself fit within the embedded BIN chunk. Boolean accessor vertex counts are rejected instead of being treated as integers.

## Logical-buffer admission extension

A GLB's embedded BIN chunk may include up to three trailing alignment bytes that are **not** part of the logical `buffers[0].byteLength` data region. The guard now requires exactly one embedded logical buffer, rejects external URI/unknown buffer extensions, verifies the declared length is a nonnegative integer and agrees with BIN chunk size within the allowed padding, and forbids all position buffer views from reaching into declared padding or undeclared logical bytes. This also rejects invalid BIN and JSON chunk alignment/ranges before decoding positions.

The synthetic fixture now declares its own logical buffer size, and two additional test methods cover positions reading valid physical but **out-of-range logical** bytes and malformed logical buffer declarations. This is a strict review-asset intake policy, not full glTF extension interoperability.

## Regression cases

Existing generator-generated real wing/126-pose fixtures remain unchanged. New negative tests reject:
- Negative accessor offsets cancelled by positive view offsets, the originally exploitable case
- Negative view offsets cancelled by positive accessor offsets
- Declared views extending beyond the embedded BIN chunk
- Boolean/unaligned/noninteger offsets and view lengths, unaligned strides
- Boolean position counts

The suite runs via `python unreal/Tools/test_aureate_full_vertex_coverage.py` and the existing Unreal source preflight. No engine or editor is needed. This is a **fail-closed admission policy for the known deterministic review asset**, not an exhaustive generic glTF verifier. Source CI is necessary but not sufficient for UE import, physical collision, or cinematic art fidelity.

## Remaining gates

Native UE 5.8.4 testing remains blocked while another editor has Live Coding active, and other separate agent jobs may be running. Do not shut down another editor, merge either draft, or promote placeholders/art. New branch SHA must get its own engine-free CI evidence, and a later isolated Windows verification may be performed after active Unreal work completes. Orbiter remains fail-closed.
