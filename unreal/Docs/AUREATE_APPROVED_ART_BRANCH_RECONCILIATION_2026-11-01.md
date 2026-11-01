# Aureate Wake — Approved-art versus preview branch integration gate (2026-11-01)

**Status:** Evidence-based code review / integration plan. **No merge or native execution implied.**
**Forward engine:** UE 5.8.4 C++/Blueprints. Historical Godot tests are references, not forward build authority.

## Exact evidence compared

- Creator-approved original four-configuration reference: draft [#668](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/668), inspected head `b1d1fc52449efdff14de6d127cd8a16cca155537`. Its 1536×1024 image SHA-256 is `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`; image approval does **not** approve any mesh.
- Native-proved review stack: [#650](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/650) Editor build + 12/12 tests; [#653](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/653) Editor build + 13/13 tests, native wing StaticMesh import and preview screenshot. These receipts apply to their **exact tested commits**, not to a combined later branch.
- Ordinary form source and screenshot evidence: [#656](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/656) currently `77ee249f8a0d734eab165dcafcd16870f12f07a7`; prior native image and 13-test receipt were created at earlier source head `61e02fd2fbdcd5ae59078867b5f37f54d6e52a17`. Latest change adds the native test inventory registration; hosted source CI passes.
- New profile study [#661](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/661) `d443c68df7fd8f36a8a7ecafb9cb5b0162362c8d`: `bUseHullSilhouetteReview` (default false), 4 curved/review hull parts, 40 triangulated canopy bars, optional canopy material; **no authored pressure-rated production hull**.
- Four support geometry donor [#631](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/631) `a0be9dec82514d6c45314c0ff7d54a3f7356f96b`: GLB generator and guarded importer plus an **independent** actor `WingRootSupports` array (4 pieces).
- Current integration [#669](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/669) base `f630d57fbb9b924447bf565a7581351b49e68d1c`: reuses the already present **four** `WingRootMounts`; optional `AuthoredRootSupportMesh`, local +X start at inner anchor, fallback cube centered; 8 hull + 10 generator + 8 import source checks and 3 hosted workflows pass. **Native import/render still outstanding.**

## Actual collision of implementation authorities (not yet a merge conflict test)

Source inspection of #668's `AureateWakePreviewActor.h/.cpp` shows `bUseAuthoredBodyReview`, `AuthoredHullReviewMesh`, `AuthoredBridgeDomeReviewMesh`, and `RefreshBodyReviewMeshes()` for optional bounded-filename review imports. It also contains the **distinct** `WingRootSupports` rig from #631 and rejects body-preview transitions into/out of Orbiter.

Source inspection of #669's actor shows `bUseHullSilhouetteReview` and four `WingRootMounts` that already serve the root support GLB. **The actor files cannot be copied/cherry-picked wholesale across branches** without reconciling component ownership. Otherwise, a naïve combination may create eight root supports, discard optional body-review guards, replace the tested old code with older source, break native test inventory, or show an undesigned hull.

These are *source-level competing implementations*, not proof that Git reports a textual merge conflict. Run an isolated actual merge/conflict analysis before touching a shared integration branch.

## Proposed smallest reversible integration

1. Begin at a new detached worktree from exact reviewed #669 (or updated comparable native-passing basis). Retain all four `Wings`, two `Hydrofoils`, four `WingRootMounts`, two `HydrofoilStruts` and their original authority. **Do not import #668's `WingRootSupports` array**.
2. Port only body-review properties/atomic validation from #668, not its whole actor. Keep `bUseHullSilhouetteReview` as a distinct noncanonical teaching/view mode and `bUseAuthoredBodyReview` as another opt-in mode. Forbid simultaneous activation or implement an explicit precedence state with exact fallback/restore tests.
3. The approved *image* is an aesthetic target, not a blanket provenance bypass. Both optional body meshes must be real review-only UStaticMeshes from their allowlisted import folders. Refuse missing/out-of-scope/partially supplied bodies **without replacing one side**. Disable and restore the old hull/bridge and all transforms deterministically.
4. Keep all authored-wing transitions into/out of Orbiter fail-closed, and also keep the new body review blocked for Orbiter until a separate safe path is proven. No blueprint preview toggle may bypass story/unlock authority.
5. Native regression must establish 4 wings + 2 hydrofoils + **exactly 4** root mounts + 2 foil struts + 4 visual-only profile sections + 40 canopy bars (which remain default-off). Add explicit tests for missing mesh, out-of-folder mesh, partial assignment, preview-mode conflict, exact restore, authored-support root pivot and Orbiter denial.
6. Run native Windows UE 5.8.4 Editor/UHT/C++ compilation and full `TSTSS` automation on the exact assembled head; then import both body and root support GLBs privately. Capture reproducible fixed-camera D3D12 images in Skyborne, Seaborne, Submersible, including post-strut Seaborne, compare with the approved image. Record hashes and frame-time; assess continuous collision separately from screenshots.

## Acceptance decision

**DO NOT MERGE OR MARK ART ACCEPTED.** All source-only checkmarks on the current branches are valid for the checked heads but are not an executable combined actor. The authorized Windows `neontic` workstation was offline during this review; no new UE build, support/body import, post-strut capture, gameplay parity, soundness of mounts, or completed ship is claimed.

Shared coordination: [Notion — Parallel Unreal Development Completion & Authority Sync](https://app.notion.com/p/40bf5bad238b81e3a3b0e0cbfa61ec6d).
