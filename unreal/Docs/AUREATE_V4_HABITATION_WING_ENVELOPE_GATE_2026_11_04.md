# Aureate Wake V4 — geodesic bridge, coupled quarters and wing-root envelope gate

**2026-11-04 — REALISTIC/CINEMATIC VISUAL QUALITY: P0.** Creator criteria: believable **scale, curvature and lighting**; cinematic **framing, atmospheric depth and readable contrast**. These measurements are from a **noncanonical** Skybourne UE 5.8.4 review sandbox. They are **not approved dimensions, a collision pass, or new canon**.

## Why this review is necessary

[Parent draft PR #732](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/732), inspected at exact SHA `a3aa4df309b379da333f6524aeece74ce0dbabe7`, has source CI **8/8 SUCCESS**, a genuine imported geodesic bridge dome and curved quarters, one fresh 15-actor review map, a 17.5° common-parent pivot with full pose rollback, and three genuinely rendered native D3D11 1280×720 previews. Those are bounded *native technical* results, **not** a continuous clearance or visual acceptance certificate. The temporary pivot was deliberately never approved as a mechanical rotation limit.

The newest source-pixel-preserving image comparison was rehashed on the authorized Windows workstation:

- `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\SkybourneV4_BridgeViews_Default_vs_Temporary_PRIVATE_20261104.png`, SHA-256 `cd69cf53e4c048442313250160f2327318c2ec4accac2f3d2ea29e931bc14b4b`.
- `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\SkybourneV4_LeafOnly_vs_CoupledHabitation_PRIVATE_20261104.png`, SHA-256 `c4863a839a6343c235050f2676fee6e7349a1387c8ffa494c4703d9c6bcbf20e`.

**Actual visual review:** original BRIDGE camera (`Automation14`) obscures a large part of the geodesic dome behind a brightly framed fore wing; transient unsaved BRIDGE camera (`Automation15`, eye `(610,-20,295)` cm toward `(185,0,130)` cm) centers the canopy but leaves dominant wing outlines on both sides and a placeholder-looking planar deck. Clearer dome triangles and curved quarters are meaningful progress, but the composition is not yet intentional final cinematography. The bright camera-centered unlit developer skydome is **not** physically coherent atmosphere, and D3D12 #705 black-sky concerns are separate.

## Exact bounded geometry sources and map

The source-only script `unreal/Tools/audit_aureate_v4_habitation_envelopes.py` requires actual **private** review GLBs and `.umap`, verifies their hashes before interpreting metadata, and uses only Python standard-library math. It never runs Unreal, builds a mesh, loads a production scene or modifies source assets.

| Input | Required SHA-256 |
| --- | --- |
| Geodesic bridge GLB | `a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506` |
| Curved living quarters GLB | `69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0` |
| Authored 280 cm leaf wing GLB | `04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73` |
| Disposable Skybourne coupled habitation map `.umap` | `14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362` |
| Authoring stage source, normalized LF SHA-256 | `520990a7800ce46822998bcc93e36af1b87d7c4e23bcb4cdd8f7523b9979d12d` |

The bridge is staged at `(170,0,133)` cm, the quarters at `(0,0,0)`, the common pivot at `(40,0,72)`, and the fore wing roots at `(145,-99,55)` and `(145,99,55)` cm, with source yaw/roll `(-80,-8)` and `(80,8)` degrees respectively. The script compares *imported-orientation approximations* of the GLB POSITION accessor bounds (glTF x, y-up, z-side → Unreal x, y-side, z-up), with wing yaw/roll and temporary pivot yaw. It considers **bounding boxes**, not material triangles, sockets, cockpit floors, airflow or actual Unreal collision components.

## Offline result: plausible at rest, unresolved rotation

The first independent bounded calculation (GLB SHA-matched, prior source staging readback, **not** native physics) gave:

| Pose | Bridge vs fore wing | Quarters vs fore wing |
| --- | --- | --- |
| Rest, 0° | **~17.560 cm** lateral AABB separation on each side | **~13.708 cm** lateral AABB separation on each side |
| −17.5° temporary common pivot | **Port** bridge/wing AABBs overlap | Both quarters/fore-wing AABBs overlap |
| +17.5° temporary common pivot | **Starboard** bridge/wing AABBs overlap | Both quarters/fore-wing AABBs overlap |

**New reproducible warning onset:** in 0.1° sampled offline AABB yaw steps, the fore-wing envelope first overlaps the curved quarters envelope at **approximately ±3.6°** and the dome envelope at **approximately ±4.5°** on the side toward which the shared habitation pivots. **These are NOT safe or unsafe physical rotation limits** and do not establish exact triangle contact; they are simply the earliest sampled intervals requiring actual swept/contact checks under the model's assumptions. They must not be used to clamp, approve, or drive a production animation.

**Executed exact-source audit:** on an independently detached clean copy of this child branch at `82060e7925bcd7b82b1efe42aaf01b6ed0ed4157`, the new 10-test Python source/negative-control suite **10/10 PASS**. The guarded auditor re-read all **three actual private GLBs** and the saved native `.umap`, verified every required SHA, and wrote a new local-only JSON receipt at `C:\TSTSS_Review\AureateV4_EnvelopeEvidence_20261104\aureate_v4_non_native_envelope_audit.json`, SHA-256 **`b0753c4e9fa7060553ef801607ef14b927799bb151a8e576ed65ba16aca21b65`**. Original map SHA unchanged, source Git clean. This was **not a new Unreal native execution or GPU render**, and no private art was uploaded.

Here **AABB overlap means a conservative spatial interference warning only**: it does **not prove two actual meshes intersect**. A positive resting axis gap only proves the two *approximated bound boxes* are separated under these assumed transformations; it **does not prove** continuous clearance, socket alignment, enough safety margin, elastic structures, animations or production collision. The chosen coordinate convention was correlated with native StaticMesh bounding extents; no exact engine triangle or sweep test is claimed.

**The 17.5° preview is especially unsuitable as an implicit acceptable mechanical limit.** The source-spawned review actors currently call `set_actor_enable_collision(False)` and `set_collision_enabled(NO_COLLISION)`; a successful native transform/rollback does not detect wing or canopy contact. Exact triangle geometry, authored collision, bridge/quarters docking collar, and full angle-dependent sweep remain **HOLD**.

## Crew-scale and pressure-volume ambiguity

Authoring GLB bounds (centimeters, after stage placement) yield a **geodesic shell vertical envelope approximately z=61.0–186.9**, and an **exterior quarters shell z=34.3–84.5**. The highest dome point sits about **102.4 cm** above the quarters' highest shell point. None of this establishes habitable standing room: there is **no verified floor elevation, usable inside volume, crew mannequin, viewport clearance, glass pressure rating or sealed docking collar**. Do not canonize numerical character heights from this visual proxy. A human-scale reference, floor/seat position and pressure boundary must be authored and reviewed before declaring the bridge comfortable or believable.

## Highest-priority next bounded Unreal steps

1. **Crew-scale and floor/collar review (P0):** in an isolated successor map, introduce one explicitly **noncanonical 170 cm diagnostic gauge** or approved character-sized reference without assigning protagonist canonical height. State the proposed floor and eye locations. Capture the dome from a frontal and three-quarter role with the physical volume legible; preserve the authored 4-wing identity. The gauge is a measurement tool, not a final NPC or asset.
2. **Motion envelope (P0):** sample the actual coupled bridge/quarters world transforms and all four wing solids at rest and across a bounded angle set **using collision-enabled disposable proxies or native mesh/sweep tests**; verify real contacts and full clearance. Do not claim even a small pivot-angle limit is safe based on AABB overlap thresholds or sampled gaps alone. Ensure the hull and other structures stay attached/aligned.
3. **Cinematic camera choice (P0):** compare the default occluded BRIDGE shot against a constrained near-centerline alternate and a true ship hero shot. Both should retain wing identity; avoid the current broad obstruction, placeholder deck emphasis and overexposed glass. Record original-pixel PNGs, FOV, camera coordinates, image hashes, map hashes and creator approval separately.
4. **Lighting (P0):** replace the developer unlit skydome with a physically coherent sky/environment and key/fill strategy on a separate environment review lane. #705's D3D12 physical-atmosphere acceptance remains independent and **HOLD**.
5. **No premature integration:** production actor/SaveGame, all four configurations, dynamic wing animation, pressurized habitation and Starbourne gameplay/story unlock stay unchanged. Creator art acceptance is required after side-by-side review.

## Source-only acceptance and limitations

A useful result from this auditor is **`CONSERVATIVE_AABB_OVERLAP_REVIEW_HOLD_NOT_NATIVE_COLLISION_PROOF`**, never `COLLISION_PASS`. Tests intentionally require that the status retain missing crew-floor, pressure-seal, native swept clearance, creator approval and Starbourne-gate flags. The private GLBs, binary map, GPU images and native receipts are **not committed**. Any GitHub CI result for this script is **source math and guard verification only**, not proof that UE5.8.4 executed these calculations against its true collision or display pipeline.

**Proposed review artifact only.** Do not merge into protected main, change production ship transformations, distribute private images, promote draft art, weaken existing resource watchdogs, or unlock Starbourne.
