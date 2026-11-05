# First Wake objective continuity — selective transfer from draft #734

**Status:** DRAFT / SOURCE-ONLY / NOT UE-NATIVE ACCEPTED / NOT MERGED. The creator's forward engine is Unreal Engine 5.8.4. This source-only isolated branch is based on the exact clean #735 review head `3cc3c979aba0dfe21f2929ce625459c16d19230e`; no original user Editor, map, art, SaveGame, production or protected main was modified.

## Why a selective transfer

Draft [#734](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/734) and [#735](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/735) overlap in their actor-to-water C++ automation. #734 contains **16 additional read-only objective checks** missing in #735. These check player-facing instructions after discovery, duplicate flyer rejection, Ionia hiring, boarding, Lift/Pressure/Reserve, engineering signoff, launch, sea contact, flotation, postflight recovery, final beat and reset. Instead of merging #734's unrelated older 25→26 report-registry changes or overwriting #735's more recent water safety, this draft adds precisely those assertions into the existing `TSTSS.FirstWake.InteractionToSplashdown` test.

The final Reset assertion correctly calls **`Restored->GetReviewObjectiveText()`**, not the original Story object. No quest states, commands, camera ray, physics, SaveGame schema, object movement or creator-authored dialogue were changed.

## Source verification

- `unreal/Tools/test_first_wake_objective_continuity_transfer.py`: exact ordered 16-case contract, original-state text presence, rejected/duplicate/out-of-order/wrong-string negative controls.
- Unreal source-preflight CI runs this check independently from existing actor-to-water authority and compiled state review checks.
- On NEONTIC in this isolated source checkout, 224/224 Python regression cases passed, including six focused checkpoint and compiler-contract tests. Windows VS2022 Build Tools MSVC compiled and executed the actual GetReviewObjectiveText C++ body: **16 positive behavioral cases PASS**, plus an injected wrong-objective mutation was rejected. These are **portable method/API-double proofs, not Unreal Editor native tests**.
- The objective compile probe now selects either GCC/Clang or MSVC `cl.exe` with C++17 flags and disposable output files, avoiding a false missing-compiler hold on Windows. Other older separate C++ harnesses may still require their own compiler adapters and are not certified by this check.
- The test is an engine-registered *native C++* test but has **not been executed on this exact new head** in the Unreal Editor. C++ `TestEqual(FString)` assertions must be compiled and run in the exact-head 26-test Win64 UE5.8.4 receipt before acceptance.

## Still open

- New source head Win64 Editor compilation, **26 distinct native automation successes**, protected configuration and SaveGame custody, and native V2 map readback.
- Physical player WASD/E/J/F6/F9 progression and actual player-facing HUD readable on real rendered frames.
- Actual hull-water overlap, stable two-second flotation, false-contact rejection, Chapter 1 handoff, fresh disk save/restart.
- Creator-approved Ionia dialogue/NPC recruitment, engineered ship interior, cinematic environment, Starbourne hold and production/release approval.

**Disposition plan for #734:** after exact-head source CI passes and this transfer is available as a draft PR, close the older redundant #734 **unmerged** while preserving its branch/source and this audit reference. Source closure is not approval or native verification. Keep successor stacked on #735 and #754 OPEN until genuine UE acceptance.
