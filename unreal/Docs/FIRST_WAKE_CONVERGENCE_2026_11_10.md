# First Wake: reconciled input / persistence / physical-water source successor (2026-11-10)

Status: **ISOLATED DRAFT / SOURCE TESTED / NOT NATIVE-ACCEPTED / NO RELEASE**.

## Authority and source provenance

- Water/physics base: draft PR [#788](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/788), pinned commit `d9548f449e3dd5fd50b19bb04b7bc93ad599b58a` (inherits #781 and #783).
- Input / explicit Continue source: draft PR [#789](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/789), pinned commit `fdd86c229ba1964b6b2d3312cdec32950bfdfec8` (inherits #782 and older review lineage).
- Intended new review branch: `review/ue58-firstwake-convergence-20261110`. Do **not** merge directly into protected `main` until native exact-head evidence, verification and review.
- Master [Notion VS matrix](https://app.notion.com/p/3ecf5bad238b8103b313f79ea816a9b5); GitHub P0 issue [#754](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/754). This is VS-A01/A02 candidate work only; it does **not** satisfy VS-E01 or approve art.

## Conflict reconciliation and safeguards

The two descendants diverged at `11063930de397c056b5058a048af88be96c804b1`; a direct merge exposed 11 overlaps. Manually reconciled the source with these rules:

- Preserve stricter witnessed `2.0` **pre-transition** water-window qualification, explicit same-beat contact-to-flotation provenance, freeze/jump rejection and dry/recovery negative controls. Prior `1.9943 s` evidence still **FAILS** the strict threshold.
- Preserve pass-through pawn collision when restoring milestone actors; reject obsolete reblocking that prevents the player from moving.
- Preserve bounded PIE-only F6 save + F9 same-session restore, normal standalone F5 save, and Shift+F5 safeguards; **F7 is a separately mapped two-press, preview/confirm prelaunch Continue action**. No silent old-slot adoption. The sidecar manifest is a guarded review mechanism, not a release-quality atomic save coordinator.
- Remove a duplicated F6 input mapping introduced by ancestor overlap; preserve one and only one F5/F6/F7/F9 binding. Update the portable compiled method harness to cover F7 only under `WITH_EDITOR`, including 25 source-extracted C++ binding cases and negative mutations.
- Keep the 6.5 GiB *free physical RAM* graphical threshold, 14 GiB C: free disk reserve, exact-head/map/source/saves admission, and no competing Editor process. Preserve the newer source water adapter and both source QA/asset staging checks without dropping the complete suite.
- Keep inherited historical runbooks for evidence lineage; they are not a claim that the current combined revision has been played or rendered.

## Verification and acceptance status

- Local Python source suite: **361/361 PASS** (includes positive/negative tests across save, map, water, input, class, and importer contracts). Must rerun after any further change.
- Diff whitespace: clean at initial reconciliation. The full GitHub source preflight / compiled checks and UE 5.8.4 Editor build are **separate** gates; final candidate head must be pinned to its own CI evidence.
- Compiled portable binding harness: **25 source-extracted C++ input cases PASS** with MSVC BuildTools developer environment; mutated PIE F5 collision, game F6 collision, and F6-to-F5 config changes rejected. This is **not** UE compilation or physical keyboard delivery.
- Neontic check: no UnrealEditor/LiveCodingConsole processes were observed. Latest free physical RAM during integration fluctuated between 4.3 and 6.3 GiB; graphical review requires >=6.5 GiB, hence **DO NOT launch graphical Unreal**. C: disk reserve was ~19.14 GiB (>=14 GiB). Recheck capacity immediately before each native attempt.
- **Not verified on combined head**: UE Editor compilation, 29 native automations, actual F6/F7/F9 keyboard behavior, two-process Continue, physical 2-second pre-transition flotation, maps/assets in Lit-mode D3D rendering, cinematics, Ender rig, Ionia cutscenes, original VFX/audio, packaged build, creator acceptance.

## Next exact-head acceptance sequence

1. Run hosted source preflight, source inventory and smoke at the new commit. Repair any failed gate without dropping tests or relaxing critical holds.
2. Confirm resource admission, then run a **single isolated native UE 5.8.4 Win64 build + 29 tests** on the exact combined head, retaining logs and source SHA. Preserve both original reviewed maps and user SaveGames.
3. Native PIE interact in correct story order; F6 save, changed-state F9 restoration, F7 preview then confirm in a separate fresh Editor process, malformed/foreign/partial sidecar rejection, Shift+F5 no-write, and replay after reset.
4. Native flight and water trace: genuine player-authorized launch, actual hull/tagged-water overlap and immersion, independently sampled contiguous 2.0 seconds of qualified pre-transition stable flotation, dry/stale-rewind negatives, then aftermath. Record frame timestamps, engine/map/source/log SHA and witness.
5. Bring only creator-approved Ender/Ionia/Aureate visuals, shaders, atmospherics, Niagara effects, Sequencer shots and audio into the same map; compare Lit-mode native frames and gameplay readability against the [Chapter One cinematic checklist](https://app.notion.com/p/407f5bad238b819eab81c2b7bb769361).
6. Complete one continuous playable and visual acceptance pass before any merge or packaging status promotion.

## Fail-closed disposition

Until these gates pass, do not mark the vertical slice complete, merge the draft, delete/overwrite user saves, unlock Starbourne, imply full five-person recruitment, or replace the strict water requirement with the old native timer or with source-only evidence.
