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
4. No assets, startup config, world maps, authoritative party inventory, production save data, sea physics, or Starbourne gates were changed.

## Local verification

- `python -m unittest -v test_first_wake_opening_and_dock_rescue test_first_wake_prelude_geometry test_first_wake_objective_review`: **31 passed**.
- `python check_first_wake_dock_guard_compiled.py` under VS2022 Build Tools `vcvars64`: **13 actual-header C++ cases passed**; mutated-threshold negative control rejected.
- Four existing portable source-extracted C++ probes passed: input binding (28), objectives (16), save guard (10), HUD (21 review + 1 shipping).
- `git diff --check`: passed before the review note was written.
- **Native UHT/UBT build, map load, PIE fall/return, title click-through and visual approval: NOT RUN.** At development time Neontic showed approximately 7.4 GiB free RAM and 14.0 GiB free disk. A new full worktree Editor build is deliberately held to avoid disrupting parallel work or filling the system drive.

## Required native review gates (not yet established)

1. Confirm no competing Unreal Editor/build and sufficient RAM/disk headroom. Build `ToSailTheStarrySkyEditor Win64 Development` from this exact branch, with one parallel build action.
2. Run `TSTSS.FirstWake.ReviewDockReturnBoundaries` inside native Unreal Editor and record exact commit, log and test pass/fail.
3. In a disposable opening-screen world using `ATSTSSOpeningReviewMode`, click **New Game**: confirm fresh traversal prelude and first **E** objective without skipping Ionia hiring or inspections.
4. In disposable copies of First Wake prelude, harbor and shoreline, step off the collision floor. Verify return only after a supported anchor has been observed; no unintended save/progression. Repeat on a sea map to confirm **no rescue**.
5. Inspect visual/topographic gameplay quality, player control, collisions and streaming, with captured screenshots. Maintain review-only until creator approves.
6. Author and validate the actual startup title-level map and boot selection separately; the project currently defaults to `/Engine/Maps/Entry`, and this branch does **not** change that.
7. Preserve the slice roster: Ender, Ionia and Lyra only. Reson, Aepex and Starbourne remain unavailable/gated.

**Disallowed claims:** Native compile success, PIE run, visual evidence, complete shipping title flow, or integrated playable vertical slice.
