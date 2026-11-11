# First Wake P0 — source convergence and playable-first execution plan

**Status:** SOURCE REVIEW CANDIDATE. **Engine:** Unreal 5.8.4.
**Branch:** `review/ue58-p0-playable-convergence-20261111`.
**Base reviewed input:** PR #799 at `2afb4b7ea6cda75dc6068014eb19c06718259539`.
**Merged reviewed lineages:** PR #809 (`abd544cefd19a0816ec431897259c88d40f9cc48`) and PR #810 (`5a0f5ffff4b67dba519e5b0b3740b7a381034186`), with #808's Lyra review-stage fix inherited from #809.
**No production merge or art approval.** This branch is for integration QA only.

## Optimization principle

Prioritize a single continuous, player-driven First Wake loop over feature breadth. Lock the narrow executable path before cosmetic expansion. Reuse verified code, native packages, and owned media when their lineage and rights permit. Run source tests at every change, build once per accepted native checkpoint, and collect original screenshots and playthrough logs on that same exact SHA. Keep source, UE automation, PIE, captured visuals, and creator approval as independent evidence classes.

## Critical path and acceptance

| Priority | Deliverable | Dependencies | Pass condition |
| --- | --- | --- | --- |
| P0 | **One trusted integration head** | PR #799 + post-splashdown Lyra gating #808 via #809 + #810 Resonator + source audio and textures from #809 | Clean source tree, full source suite, source manifests, UE Win64 build and all registered native automations on the *same* commit |
| P0 | **Title and harbor player loop** | Controls, true walkable coastline, safe dock edges, objective text, flyer and Ionia conversations | One uninterrupted PIE New Game → flyer → Ionia → engine with real WASD/mouse/E and no off-world fall |
| P0 | **Engineering and flight** | Reversible tuning, objective/inspection state, crew checks, Ionia command | Player executes repair and Ionia authorizes physical launch; drift response has visible state consequence |
| P0 | **Actual sea landing** | Physics adapter, sampled native world seconds, restore guards | Continuous directly observed >=2.0 s pre-transition stable flotation at <=25 cm/s, with dry/rewind/false-contact negatives |
| P0 | **Chapter handoff** | Real aftermath level, explicit dialogue recruitment, persistent roster | Lyra joins only after Splashdown and a separate recruitment action; Talen non-playable; no early Reson/Aepex |
| P1 | **Save and recovery** | F6 PIE, F7 preview/confirm, F9 session, F5 standalone | Process restart, in-session restore, corrupted/foreign save rejection and correct checkpoint/effects |
| P1 | **First genuine JRPG interaction** | Ender Resonator explicit unlock, Centering/Pulse, class/equipment menu | Cast cost, cue and outcome in real PIE; visible menu inventory/equipment. Combat only where narratively justified; optional test arena is not main-story completion |
| P1 | **Audio and environment polish** | Provenance, compilable source, source-authored cues, native scene | Native compiled audio without C2440, audible hooks, scene music with ownership evidence, clear lighting/exposure, accessible captions |
| P1 | **Cinematic character/world assimilation** | Approved cast/ship design, actor rigging, PBR assets, camera correction | Actual UE-lit native images/clips reviewed for character likeness, walkability, hull/shore scale, camera/lighting and performance |
| Gate | **Review executable** | All P0/P1, end-to-end evidence | Continuous native PIE, recovery negatives, packaged Windows review build and separate creator approvals; no public release without explicit authority |

## Current result, not acceptance

- Source-only merges of #809 and #810 onto the latest #799 head completed with no Git conflicts in a **new disposable worktree**. PR #808 is contained in the ancestry; no existing agent worktree was changed.
- First run: **520 tests, 6 errors/failures** because original focus-map provenance tests assumed only the dedicated CenteringPulse directory. The verifier now allows read-only SHA/manifest checks in the same Git worktree where the source lives; **native authoring and readback remain restricted to the named dedicated worktree and explicit exact HEAD**.
- Re-run after this targeted testability repair: **520/520 Python source tests PASS**, 35 registered native automation identities verified, committed shoreline native asset hash/tree manifest PASS. These are source-only receipts and do **not** establish native execution on the combined branch.
- Physical admission at last check: RAM ~8 GiB free; C: ~11.6 GiB free, **below required 14 GiB**. No UE build, gameplay, D3D capture or native audio performed; do not bypass the resource gate.

## Separate integration conflicts / deferred scope

- PR #793 (equipment and ship UI) has **four source conflicts** against the #809 lineage: explorer C++/header, equipment native test and compiled input checker. Resolve explicitly with input/save authority and three-stage Lyra gates; do not choose ours/theirs wholesale.
- PR #804's own native C2440 compile failure is not cleared by this source merge. First prove native compilation and audible PIE before relying on any inherited audio director.
- PR #811 camera orientation and the 200-actor PBR world (#806/#807) have genuine native visual observations but final-color overexposure/placeholder artifacts remain. Preserve original map receipts; stage new assets under new package/hash.
- PR #812 Ender visual candidate is unverified in native gameplay and body/shirt deformation remains HOLD.
- PR #791 enemy gallery requires verified encounter placement, map readback and combat integration, not an assumed random encounter.
- Full spherical globe, expanded cast, Starbourne and future high-altitude travel are **out of this bounded playable slice**; Starbourne remains fail-closed.

## Next safe executable step

After C: returns to >=14 GiB and physical free RAM >=6.5 GiB with no competing Unreal/LiveCoding session: run a **guarded exact-head Unreal 5.8.4 Win64 Editor compile and all registered TSTSS automations** on this isolated convergence head; then run a **single native PIE route** up to the earliest missing interaction and capture objective, map, collision and SaveGame evidence. Stop on real failure rather than skipping a scene. Native provenance must contain Git SHA, UE version, map/asset hashes, logs, screenshots, operator and failed/untested limitations.

SSoT: [Notion First Wake Master Matrix](https://app.notion.com/p/3ecf5bad238b8103b313f79ea816a9b5); [P0 Issue #754](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/754).
