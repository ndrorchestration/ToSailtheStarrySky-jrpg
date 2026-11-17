# Aureate Wake — four dorsal Seabourne wind-sails (review-only, 2026-11-16)

> **DRAFT / OPT-IN / NONCANONICAL DIMENSIONS / UNMERGED.** New code adds a testable preview pose and visual per-wing yaw, **not** an animated, playable, aerodynamically simulated, visually approved or collision-safe sailing system. No `.umap` or imported art assets were edited.

## Creator direction and current authority

This exact visual/mechanical direction was clarified November 16: the **original four** blue-iridescent dragonfly wings of the Aureate Wake rotate upward from Skybourne flight position into a four-sail **dorsal fore-to-aft row** for Seabourne. Wings **2 and 4 shift their stations** during that transformation so that all four stand individually upright, slightly aft-raked like the visually rhythmic funnels of RMS Titanic, **without becoming smokestacks**. Once in the Seabourne sailing mode, **each can independently swivel around the upright mount**, in a solarpunk style, to change its incidence to the wind. This is separate from Starbourne's radial four-sail arrangement and does **not** unlock that form.

Creator supplied two original vessel images, and the locked Hilltonia Harbor v3 map. TapNow produced a 2K still (node `cfaf52eb-376f-4e12-9985-421c09d48eec`) showing four tall glass sails and a pointed hull; this is direction-only, not genuine motion evidence or creator final approval. [TapNow visual study](https://app.tapnow.ai/canvas/d1f9b94e-87a1-5796-9a4e-42e382300068). [Owning Notion four-form architectural specification](https://app.notion.com/p/40af5bad238b8120bc19fad79d9bda69).

## Implementation in this isolated branch

Base: [#827](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/827), exact source `2a94a604c139fd0cf48756dae75274e05ad7833c`, already containing real `AAureateWakePreviewActor`, story-bound Seabourne restriction, four persistent wing components, two hydrofoils and the 14-actor additive coastal review map. This is **not** a merge of sibling [#828](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/828), [#845](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/845), or production main.

Changes in existing `AureateWakePreviewActor.h/.cpp`:

- `bUseSeabourneWindSailReview = false` by default, so the old Seabourne pose and any existing save/map authoring remain intact until explicitly opted in; the stable four-form enum IDs and creator-facing spellings remain untouched.
- In *opted-in* Seabourne review, the **same four `DragonflyWing_1..4` components** are posed along a distinct dorsal fore–aft row. The front/back station positions in local cm are **[+300, +105, -90, -285]**, with Y=0, upright `Pitch=98°` producing a ~8° aft rake; these are provisional illustration coordinates **not approved mechanical dimensions or collision clearances**. `+X` is ship forward in this actor.
- The existing 280-cm +X root-pivoted authored-wing option, when actually selected and available, retains its original mesh scale and uses a provisional base at Z=228cm. The basic-shape cube review instead uses a centered wing at Z=365cm with its separate proxy scale. **Neither form proves correct authored-art orientation or bridge clearance.**
- Wings **2 and 4** undergo fore/aft station changes relative to their old paired port/starboard mounts when the existing form transition interpolates into this new pose. No fifth wing and no part is silently reassigned to the Starbourne form.
- `SetSeabourneWindTrimDegrees(WingNumber, Degrees)` changes visual yaw of exactly one selected sail, preserving the other three yaw values; applies to the four persistent existing components. One-based wing number 1..4. The provisional `[-35°, +35°]` input bound is solely a *preview control limit*, **not** a swept-collision-safe limit or real wind-performance figure.
- **Fail closed** unless explicitly opted in, the complete Seabourne story binding is valid/authorizes the form, transition is settled, exactly four wings and two hydrofoils exist, target component is valid, authored-wing selection is coherent and yaw input/index are finite/in range. Never grants form switching or saved player progression; no new SaveGame schema.
- `GetSeabourneWindTrimDegrees` reports zero when invalid/unbound/disabled/revoked. On any `SnapToForm`, nonpersistent trim returns to zero. An opted-in stale Seabourne presentation is reset to the safe Skybourne *preview pose* if the story revokes all review modes. This is presentation state, not travel authorization.

## Verification classification

- **Source authored:** exact C++ actor API/implementation above plus extended *existing* `TSTSS.AureateWake.Review.SeabourneStoryGate` Unreal automation, retaining the native registry name and test count. New assertions cover opt-in default, four dorsal roots ordered fore–aft, almost-vertical slight aft rake, independent first/fourth yaw, invalid wing numbers, >35° and NaN refusal, no change in wing/hydrofoil count, state rebound trim reset, and active-story revocation.
- **Engine-free:** `unreal/Tools/test_seabourne_wind_sail_review.py` checks source invariants and negative mutations; `.github/workflows/unreal-source-preflight.yml` explicitly invokes it. A hosted success proves source checks only.
- **Native Unreal** UHT/UBT Win64 Editor build, actual native test execution, GPU/PIE and human review: **NOT YET RUN on this branch**. Past #827 native results remain historical, not transferred to this new head.
- **Geometry safety:** prior [#845](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/845) read-only V4 mesh envelope exporter and its warning about overlapping static boxes do **not** certify these new moving sail envelopes. Run actual source-hash-locked endpoint/continuous-motion and wind-yaw sweep against bridge, hull, other sails, railings and dock before any promotion. A source dimension/angle bound is not clearance evidence.
- **Gameplay:** real captain steering, wind/weather input, sail actuation rates, restoring at save/level travel, aerodynamic forces, ocean physics and tactile ship controls remain UNIMPLEMENTED here.

## Native review checklist and stop conditions

1. Neontic resources, other agent ownership and exact source SHA must be checked immediately before any native run. Honor ≥6.5 GiB free RAM for graphics and ≥14 GiB free C: with ample build overhead; do **not** launch against low disk or a foreign Unreal Editor.
2. Native Win64 Editor rebuild and existing `TSTSS.AureateWake.Review.SeabourneStoryGate` automation on exact head. Require log/receipt and clean-tree attestation.
3. In a disposable coastal map with **opt-in enabled only for the review actor**, capture end of Skybourne→Seabourne transition, views of four upright aft-raked sails and wing-2/4 mount repositioning, then individually yaw wings while comparing 2+ world angles. Obtain bridge/dome/strut/hydrofoil clearances at all intermediate poses, not only static endpoints.
4. Test story revocation during transformation and while already trimmed; ensure immediate denial, pose reset, no Starbourne player access. No altered map or accepted art until evidence is reviewed.
5. Map the four trim angles to verified local weather/wind only in a separately authorized gameplay change after physics/scaling/collision approval. Avoid treating the Daz or TapNow 2D reference as redistributable 3D mesh data.

**No branch merge, release, game-save migration or approval is authorized by this document.**
