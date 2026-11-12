# First Wake: opening route and dock safety (review candidate)

**Authority:** REVIEW ONLY; not canonical, not approved, not playable-proven, not merged.
**Isolated branch:** `review/ue58-opening-and-dock-rescue-20261111`
**Local worktree:** `C:\TSTSS_DockOpening_20261111`
**Exact base before edits:** `76268b8975ec3ce7b7644b6223c09d4889b658a2`
**Unreal version:** installed 5.8 / target 5.8.4. No engine rendering claim.

## Changes made

1. The explicitly opted-in `TSTSSOpeningReviewWidget` New Game button now checks whether the **native, seven-stop playable prelude** map exists, then calls `OpenLevel` on `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2`. It keeps the menu intact when the target is missing. This is not an automatic default startup title map.
2. The `TSTSSExplorerCharacter` review walk safety pass stores a supported-ground anchor after five WorldStatic downward floor traces on the character's center and near-capsule points. A falling pawn more than 400 cm below the anchor can be returned to a verified teleport spot. Only non-shipping PIE/Game, player-controlled pawns, exact allowlisted map names and the `/Game/TSTSS/Review/` namespace qualify.
3. Native automation source registers positive/negative decision cases; source tests also check that recovery cannot advance story beats, issue sea-contact events, mutate save slots or transition maps.
4. No approved assets, startup config, authoritative party inventory, production save data, sea physics or Starbourne gates were changed.
5. A separate native review-only title world was created at `/Game/TSTSS/Review/Opening/L_FirstWake_TitleReview` (8,754 bytes, SHA-256 `63fb6f34ba7b4e46da77d45f0d72d32c69aa03dbc8ec7897bdff0f1bbde6f3f5`) with `/Script/ToSailTheStarrySky.TSTSSOpeningReviewMode`. The title mode uses a spectator pawn instead of spawning an unfloored Explorer. It does not change `/Engine/Maps/Entry` as the default map. No private title movie is present, so the existing fallback typography is expected.

## Local verification

- `python -m unittest -v test_first_wake_opening_and_dock_rescue test_first_wake_prelude_geometry test_first_wake_objective_review`: **31 passed**.
- `python check_first_wake_dock_guard_compiled.py` under VS2022 Build Tools `vcvars64`: **13 actual-header C++ cases passed**; mutated-threshold negative control rejected.
- Four existing portable source-extracted C++ probes passed: input binding (28), objectives (16), save guard (10), HUD (21 review + 1 shipping).
- `git diff --check`: passed before the review note was written.
- **First native Editor build: FAILED at a concrete C++ type mismatch.** Exact tested source head `bfe98d1ac5bebcd8204872a516e140e415dfd854`; Visual Studio 2022 toolchain and Unreal 5.8 UBT/UHT ran. `TSTSSAudioSubsystem.cpp:99` incorrectly declared `UAudioComponent* const*` for a `TMap<FName, TObjectPtr<UAudioComponent>>` lookup. Log: `unreal/Saved/OpeningDockReview/ubt_editor_bfe98d1.log`, exit receipt `6` (OtherCompilationError). The minimal review-branch repair uses `const TObjectPtr<UAudioComponent>*` without changing playback semantics. Associated source test added; 46 relevant source tests passed after the repair. **Repaired Editor build PASS** on `4841d8d36e68c7fd4329a4c9eca2366695b105ea`; **updated title-mode Editor build PASS** on `697bbd5e71a636d025ca80428d1c0c46f1b5831e`, each with exit code 0. **Native Unreal automation PASS** on `4841d8d`: `TSTSS.FirstWake.ReviewDockReturnBoundaries` reported `Test Completed. Result={Success}`, one test performed, exit 0. **Native title map authoring PASS** at `697bbd5`, receipt `unreal/Saved/OpeningDockReview/title_native_authoring.json`; source prelude SHA remained `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`. Editor-generated drift in `DefaultEngine.ini` and `DefaultInput.ini` was restored from exact committed contents, then future Editor sessions protected those configs as read-only. **Native title map reopen/readback PASS at `cf511a0`**: the GameMode override and source/target map SHA-256 digests match; readback receipt `unreal/Saved/OpeningDockReview/title_native_readback.json`. **Exact-commit automation PASS** at `cf511a0`: one successful `ReviewDockReturnBoundaries` test, exit 0. **Standalone Win64 Development launch and New Game click-through PASS** at `cf511a0` using one scoped synthetic mouse click in the actual Windows game window. Log confirms title `TSTSSOpeningReviewMode` loads, then New Game routes to the existing playable Prelude under `TSTSSGameMode`; the objective HUD displays `Find Ionia's flyer`. Captures: `unreal/Saved/OpeningDockReview/title_standalone_before.png` and `prelude_standalone_after_click.png` (local Saved evidence only). **PIE fall/return remains unverified**: a bounded backwards key-input trial produced no fall-return log and is inconclusive, not a PASS. **Visual review gate NOT PASSED**: prelude appears very dark, its review marker text is mirrored from the spawn viewpoint, and Unreal displays a six-object lighting-rebuild warning. No production visual promotion. Current relevant source tests: 47 PASS.

## Native verification matrix (completed gates distinguished from pending)

1. **PASS** — Native UBT/UHT Editor build on `697bbd5`, single-action compilation, exit 0.
2. **PASS on prior compiled head** — Unreal Editor automation `TSTSS.FirstWake.ReviewDockReturnBoundaries`, one successful test at `4841d8d`; rerun at final title asset commit for exact-head evidence.
3. **PARTIAL PASS** — Standalone title UI rendered, New Game click routed into the prelude and HUD showed the initial flyer objective. Actual first **E** activation, Ionia hiring and inspection traversal remain to be exercised.
4. In disposable copies of First Wake prelude, harbor and shoreline, step off the collision floor. Verify return only after a supported anchor has been observed; no unintended save/progression. Repeat on a sea map to confirm **no rescue**.
5. **VISUAL GATE FAIL / REWORK NEEDED** — Captured screenshots show dark prelude presentation, reversed review marker text and six unbuilt lighting objects. Repair using a disposable visual review derivative or gated map-authoring pass; do not mislabel as cinematic approval.
6. **Native authoring PASS, runtime pending** — Title review map saved with GameMode override; reopen/readback, click-through and visual review pending. Project still defaults to `/Engine/Maps/Entry` and must not be auto-promoted.
7. Preserve the slice roster: Ender, Ionia and Lyra only. Reson, Aepex and Starbourne remain unavailable/gated.

**Disallowed claims:** PIE fall-recovery validated, first E objective completed, visual approval, complete shipping title flow, merged content, or integrated finished vertical slice. Native compile, map readback and standalone title click-through are evidenced above.
