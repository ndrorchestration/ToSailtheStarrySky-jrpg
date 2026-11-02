# First Wake V2 — independently isolated Unreal review and native persistence gate

**2026-11-01 · Draft, review-only.** Stacked exclusively on [Prelude PR #694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694) at the verified source head `502cb9d7aa0666909a2eb3cc86ba2ac91f273a4a`. No production map, storyline, main branch, installer or published art is changed.

## Reconciliation

Contrary to earlier assumptions, [#694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694) **already tracks** `unreal/Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap`. The independently cloned file in `C:\TSTSS_PreludeV2_IndependentReview_20261101` is **56,053 bytes**, SHA-256 `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`; it matches the older shared V2 sandbox byte-for-byte. No binary copying, map regeneration or overwrite is necessary.

This review fixes a QA provenance weakness: native V1 and V2 verification scripts were previously run in the same sandbox and collided over receipts. The new independent verifier `unreal/Tools/verify_first_wake_v2_independent.py` accepts only the exact separate project directory `C:\TSTSS_PreludeV2_IndependentReview_20261101\unreal`, locks the map hash and writes a unique `Saved/PreludeV2IndependentQA/v2_native_validation.json` receipt if—and only if—all checks succeed. Any existing receipt fails closed.

## Source-side verified

Nine engine-free negative-control tests on Windows PASS, covering immutable tracked map bytes, strict project-folder guard, WASD/mouse/E/F5/F9 action mapping and native C++ bindings, interaction range/trace source, exact distinct test slot, cleanup, no unauthorized map save or SeaContact/Orbiter controls. Source CLI emits `native_execution: false`. These tests verify **wiring in source**, not the physical keyboard or player camera.

## Native verification specification (not yet executed)

An independent UE5.8.4 Editor Python run must load the real compiled C++ actors and confirm:
- Exactly seven unique milestone actors, correctly typed and traced; correct PlayerStart and GameMode's `TSTSSExplorerCharacter`.
- Harbor floor blocking collision, ocean mesh **NoCollision**, no fake splashdown markers.
- Temporary, unsaved `UTSTSSFirstWakeState` rejects premature Ionia/signoff, accepts flyer → Ionia hiring → boarding → distinct Lift/Pressure/Reserve → engineering signoff, rejects duplicate checks, does **not** enter Chapter 1 Act 1.
- Native `UTSTSSPersistence.save_progress` / `load_progress` round-trip of the engineering-checked Prelude and 7-bit inspection evidence in a dedicated **nonplayer** slot `tstss_prelude_v2_independent_qa`. It refuses any pre-existing slot and always deletes a newly created test slot, failing if cleanup fails.
- Before/after SHA locks for saved V2 map and the two tracked default `.ini` files. It never saves a map.

**This does not inject E/F5/F9 keypresses, run PIE or exercise the pawn's private input methods.** It tests the lower native save service only, not user-facing quickload or actual walkability. It also does not render D3D11/D3D12, validate cinematic character likeness, ship physics, or cause SeaContact. Passing this native script would still not constitute a playable Chapter 1.

## Current native compilation hold

An isolated UE5.8.4 Editor build for the clean checkout reached UHT (26 generated files) but UnrealBuildTool returned a **Live Coding active** conflict in a *parallel, unrelated Unreal session*. No native run of this new V2 persistence script is claimed. The other workstream's Editor and shaders were not interrupted. When Live Coding is no longer active, build the source-locked isolated project and run an explicit `-ExecutePythonScript` wrapper with `sys.argv=[path, '--native']`; treat an exit code zero alone as inadequate until the expected receipt exists, its hash and map/config hashes verify, and the log has no Python errors.

**Production gate:** Subsequent independent PIE interaction-range/keyboard/mouse, F5/F9 user action, save restoration, cinematics, ocean water-contact proof, and end-user acceptance are still OPEN. Do not merge or promote the review map without the creator's authorization.
