# Aureate Wake — fail-closed swept-clearance verifier (review tooling)

**2026-11-03 | SOURCE-ONLY REVIEW TOOLING | NOT ENGINE EVIDENCE | NO TRANSITION ADMISSION**

Adds a deterministic, stdlib-only Python reference model that decides whether the four wing envelopes can move through a form transition without coming within a required clearance of the hull, bridge, quarters or deck envelopes, or of each other. It exists because `AAureateWakePreviewActor` still explicitly holds hard transitions "pending clearance" and no continuous check existed.

**This does not clear any transition, accept any geometry, or say anything about the real ship.** It checks only the envelopes it is given. The committed example config is synthetic.

## Files

| File | Role |
| --- | --- |
| `ArtSource/ShipReview/aureate_swept_clearance.py` | Verifier and CLI (`python aureate_swept_clearance.py CONFIG.json`; exit 0 only for CLEAR) |
| `ArtSource/ShipReview/aureate_swept_clearance_example_SYNTHETIC.json` | Input-schema example with invented envelopes |
| `Tests/test_aureate_swept_clearance.py` | 25 tests, including a seeded brute-force soundness check |

## Method

- **Interpolation model** matches the native `Interpolate`: location Lerp, rotation Slerp, scale Lerp. The native smoothstep easing only reparameterizes `[0, 1]` and does not change the swept set.
- **Sweep:** adaptive bisection over `t`. For a segment, every point of a moving body stays within `B = |Δposition| + Δangle·|scale·reach| + |Δscale·reach|` of its start pose. The segment is proven clear when the start pose is separated by `clearance + B_a + B_b` (obstacles inflated per axis, a superset of the Minkowski sum with a ball). Otherwise it is bisected.
- **Overlap test:** separating-axis test on oriented boxes; touching counts as a hit.
- **Pairs checked:** each wing against each obstacle role, and each wing pair moving simultaneously.

## Fail-closed behavior

| Verdict | Meaning | CLI exit |
| --- | --- | --- |
| `CLEAR_UNDER_ENVELOPES` | Proven clear for the supplied envelopes and model only | 0 |
| `REJECT_CLEARANCE_VIOLATION` | A sampled pose is inside the required clearance | 1 |
| `FAIL_CLOSED_UNPROVEN` | Depth or evaluation budget reached with an unresolved segment (includes grazing real collisions) | 1 |
| `FAIL_CLOSED_INVALID_INPUT` | Missing obstacle role, wrong wing identity set, non-finite number, non-positive extent or scale, bad header, unreadable file | 1 |

Required obstacle roles: `hull`, `bridge`, `quarters`, `deck`. Required wing identities: `FORE_PORT`, `FORE_STARBOARD`, `AFT_PORT`, `AFT_STARBOARD`. Every result lists what was **not** checked.

## Verified here, and what is not

- **Verified:** 25/25 local tests pass. A mutation check (motion bound forced to zero) made 6 tests fail, so the suite does guard soundness.
- **NOT verified:** that the envelopes correspond to the native Unreal meshes; real wing geometry (boxes only, so conservative but loose); hydrofoils, struts and root supports; the rotating bridge/quarters assembly (#702/#706); water, buoyancy, pressure, structure; creator approval. Starbourne is out of scope.
- A CLEAR result on envelopes exported from native meshes would still be a source-side screen, not a native collision receipt.

## Next gate

Add an Unreal-side exporter that writes native wing/hull/bridge/quarters/deck oriented-box envelopes (with the exact map SHA-256) in this schema. Only then can the verifier produce a result about the real Skybourne to Submersible route. Until then every transition stays held.
