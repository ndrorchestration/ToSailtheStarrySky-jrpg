# Aureate Wake — native envelope exporter (review tooling)

**2026-11-16 | SOURCE-ONLY | NOT ENGINE EVIDENCE | NO TRANSITION ADMISSION**

Closes the "next gate" in `AUREATE_SWEPT_CLEARANCE_VERIFIER_2026-11-03.md`: a read-only Unreal recorder plus a pure converter, so the first native run on the Windows workstation can feed real wing/hull/bridge/quarters/deck oriented boxes into the swept-clearance verifier.

**Handoff labels:** converter, recorder source, runner and tests are **IMPLEMENTED** (source-only). The recorder has **never run in Unreal**: native behaviour, label names and tolerances are **OPEN** until the first Neontic run. Stacked on the verifier branch, itself on draft #747/#732. No canon, art approval or Starbourne content.

## Files
| File | Role |
| --- | --- |
| `Tools/export_aureate_envelopes_native.py` | Read-only Editor script: dumps one map's actor transforms, mesh-local bounds and engine world AABBs to a NEW snapshot JSON; records map SHA-256 before and after load |
| `Tools/aureate_envelope_records.py` | Pure converter `build_config(from_snapshot, to_snapshot, required_clearance)`; fail-closed |
| `Tools/run_aureate_envelope_export_native.py` | `export` (Windows, gated: RAM ≥ 4.2 GiB, disk ≥ 14 GiB, no other commandlet, no overwrite, watchdog) and `combine` (any OS; runs the verifier; exit 0 only for CLEAR) |
| `Tests/test_aureate_envelope_records.py` | 24 converter tests (synthetic snapshots) |
| `Tests/test_aureate_envelope_export_source_contract.py` | 12 tests: no mutating calls, gates present, exporter run against a fake `unreal` module, combine CLI |

## Run recipe (Neontic, OPEN)
1. `run_aureate_envelope_export_native.py export --map /Game/TSTSS/Review/<from-form map> --form Skybourne --out <new>.json`
2. Same for the to-form map (e.g. Submersible).
3. `run_aureate_envelope_export_native.py combine --from-snapshot A.json --to-snapshot B.json --clearance <cm> --out <new>.json`

## Fail-closed rules
Wrong schema/units, non-64-hex map SHA, same form twice, label token matching 0 or >1 actors, any non-finite number or boolean, non-unit quaternion, non-positive or mirrored scale, non-positive extents, wing mesh bounds differing between forms, **obstacles moving between forms** (the verifier models obstacles as static, so a rotating bridge/quarters assembly cannot be screened yet), missing engine AABB, and derived box disagreeing with the engine AABB by > 0.05 cm (catches a wrong quaternion order or transform composition).

Default role labels come from the #732 15-actor map: hull = pearl hull proxy + cinematic trim, bridge = geodesic dome, quarters = curved quarters, deck = observation deck proxy.

## Verified here, and what is not
- **Verified:** 36 new tests pass; mutation checks (no scale on offset, no engine self-check, wrong axis, duplicates allowed, exporter quaternion order swapped, exporter calling a save) each fail the suites.
- **NOT verified:** any real Unreal run; that `get_actor_bounds` and `StaticMesh.get_bounds` behave as assumed; label names on the real maps; the (x,y,z,w) to [w,x,y,z] handling against a native quaternion (the AABB self-check is the guard); hydrofoils, struts, rotating habitation; creator approval. A CLEAR on exported boxes is a source-side screen, not a collision receipt.
