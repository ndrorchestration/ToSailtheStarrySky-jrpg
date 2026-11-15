# Aureate Wake — fail-closed swept-clearance verifier (review tooling)

**2026-11-03 | SOURCE-ONLY REVIEW TOOLING | NOT ENGINE EVIDENCE | NO TRANSITION ADMISSION**

Adds a deterministic, stdlib-only Python reference model that decides whether the four wing envelopes can move through a form transition without coming within a required clearance of the hull, bridge, quarters or deck envelopes, or of each other. It exists because `AAureateWakePreviewActor` still explicitly holds hard transitions "pending clearance" and no continuous check existed.

**This does not clear any transition, accept any geometry, or say anything about the real ship.** It checks only the envelopes it is given. The committed example config is synthetic.

**Handoff labels:** the verifier and its tests are **IMPLEMENTED** (source-only review tooling). Every angle or clearance it reports is an **OPEN** review finding, not an approved limit. Stacked on draft [#747](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/747) (head `59817b554acaf6305f60cc028342fa04b778bb07`), itself a child of draft #732 (`a3aa4df309b379da333f6524aeece74ce0dbabe7`). No creator canon, native evidence or Starbourne content is involved.

## Files

| File | Role |
| --- | --- |
| `ArtSource/ShipReview/aureate_swept_clearance.py` | Verifier and CLI (`python aureate_swept_clearance.py CONFIG.json`; exit 0 only for CLEAR) |
| `ArtSource/ShipReview/aureate_swept_clearance_example_SYNTHETIC.json` | Input-schema example with invented envelopes |
| `Tests/test_aureate_swept_clearance.py` | 25 tests, including a seeded brute-force soundness check |
| `Tests/test_aureate_swept_clearance_crosscheck_747.py` | 5 tests anchoring the verifier to the independent #747 AABB audit (skipped if the #747 module is absent) |

## Method

- **Interpolation model** matches the native `Interpolate`: location Lerp, rotation Slerp, scale Lerp. The native smoothstep easing only reparameterizes `[0, 1]` and does not change the swept set.
- **Sweep:** adaptive bisection over `t`. For a segment, every point of a moving body stays within `B = |Δposition| + Δangle·|scale·reach| + |Δscale·reach|` of its start pose. The segment is proven clear when the start pose is separated by `clearance + B_a + B_b` (obstacles inflated per axis, a superset of the Minkowski sum with a ball). Otherwise it is bisected.
- **Overlap test:** separating-axis test on oriented boxes; touching counts as a hit.
- **Pairs checked:** each wing against each obstacle role, and each wing pair moving simultaneously.
- **Clearance inflation caveat:** a required clearance greater than zero inflates the obstacle box along its own local axes. For an axis-aligned obstacle that is exact; for a rotated obstacle it over-inflates (up to about a factor of 1.7 along some world directions). It never under-reports, but a rotated obstacle's clearance margin is stricter than a true ball margin. With a clearance of 0 there is no inflation and contact angles are exact for the supplied boxes.

## Fail-closed behavior

| Verdict | Meaning | CLI exit |
| --- | --- | --- |
| `CLEAR_UNDER_ENVELOPES` | Proven clear for the supplied envelopes and model only | 0 |
| `REJECT_CLEARANCE_VIOLATION` | A sampled pose is inside the required clearance | 1 |
| `FAIL_CLOSED_UNPROVEN` | Depth or evaluation budget reached with an unresolved segment (includes grazing real collisions) | 1 |
| `FAIL_CLOSED_INVALID_INPUT` | Missing obstacle role, wrong wing identity set, non-finite number, non-positive extent or scale, bad header, unreadable file | 1 |

Required obstacle roles: `hull`, `bridge`, `quarters`, `deck`. Required wing identities: `FORE_PORT`, `FORE_STARBOARD`, `AFT_PORT`, `AFT_STARBOARD`. Every result lists what was **not** checked.

## Cross-check against PR #747 (2026-11-15, source-only)

#747 audits the same bridge/quarters/fore-wing review layout with axis-aligned boxes and its in-repo fixture holds the exact boxes (extracted there from SHA-pinned private GLBs; not re-derived here). Replaying those boxes through this verifier, with the habitat yawing about the common pivot `(40, 0, 72)` cm:

| Quantity | #747 AABB audit | This verifier (oriented habitat box, #747's wing box) | This verifier (oriented habitat and oriented wing box) |
| --- | --- | --- | --- |
| Rest lateral gap, bridge to fore wing | 17.560 cm | 17.560 cm (reproduced to 0.01 cm) | not comparable (see caveat above) |
| Rest lateral gap, quarters to fore wing | 13.708 cm | 13.708 cm (reproduced to 0.01 cm) | not comparable |
| First contact, bridge | about 4.5° | about 4.94° | about 9.6° |
| First contact, quarters | about 3.6° | about 3.87° | about 5.15° |

How to read it:

- The contact angles move later as the envelopes tighten (4.5 to 4.94 to 9.6 for the bridge, 3.6 to 3.87 to 5.15 for the quarters), as they must, because each step replaces a looser box with a tighter one.
- The sweep result agrees with an independent dense scan at 0.01° steps to within 0.02°, and errs on the early side.
- **The qualitative finding is unchanged:** under every envelope tried, the temporary 17.5° common-pivot yaw is rejected, and first contact occurs at roughly a fifth to just over half of that angle. This is a result about boxes, not about the real meshes, which are tighter than their bounds, so it does not establish a safe or maximum angle either.

## Verified here, and what is not

- **Verified:** 30/30 local tests pass (25 verifier, 5 cross-check). Mutation checks made the suites fail as intended: a motion bound forced to zero broke 6 verifier tests, and a wrong rotation half-angle broke 2 cross-check tests. #747's own 10 tests still pass on this stack.
- **NOT verified:** that the envelopes correspond to the native Unreal meshes; real wing geometry (boxes only, so conservative but loose); hydrofoils, struts and root supports; the rotating bridge/quarters assembly (#702/#706); water, buoyancy, pressure, structure; creator approval. Starbourne is out of scope.
- A CLEAR result on envelopes exported from native meshes would still be a source-side screen, not a native collision receipt.

## Next gate

Add an Unreal-side exporter that writes native wing/hull/bridge/quarters/deck oriented-box envelopes (with the exact map SHA-256) in this schema; the 15-actor coupled-habitation map from #732 is the natural first input. Only then can the verifier produce a result about the real Skybourne to Submersible route. Until then every transition stays held.
