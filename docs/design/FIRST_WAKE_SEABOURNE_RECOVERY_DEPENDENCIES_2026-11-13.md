# First Wake → Seabourne recovery: implementation dependency contract

Status: creator-directed narrative change, implementation pending. 2026-11-13.

## Controlling story direction
- First Wake opens with a cinematic Skybourne flight, followed by a real emergency splashdown.
- Following splashdown, Aureate Wake is operational at sea but Skybourne is plot-locked for multiple story acts; the crew must sail between quest locations while Ender diagnoses the unusual harmonic failure and identifies/obtains required rare components.
- Do not resolve the failure with a conveniently placed Captain Denith fuel cache near the crash. Captain Denith remains Ionia's previous captain.
- `VS05_DenithFuelShanty` is a legacy **asset identifier**, not an approved in-world place name. Preserve map and asset references until a reviewed migration.
- The ship's whimsical, apparently protective or stubborn personality should remain ambiguous: engineering response, harmonic phenomenon, or something more. No explicit sentience reveal is authorized.
- Ender is a competent old-system harmonic specialist whose understanding grows through observation, repair, and earned collaboration. Ionia retains captain authority; only Ender, Ionia and Lyra are available in the opening slice. All Five Lights remain necessary for later culmination.
- Approved names: Skybourne, Seabourne, Submersible, Starbourne. Starbourne remains fail-closed.

## Verified source coupling at integration checkout 31c58a38d56ad0b695a73e55aa5c27f7b5ca9b64
- `unreal/Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp` currently routes `VS04_SplashdownSea` on `FlotationConfirmed` to `/Game/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty`, then routes the legacy map on `EmptyReserveInspected` to `L_VS06_ShoreMagicEnemyGear_Review`.
- `unreal/Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp` explicitly references the legacy map for review interaction, beacon refresh, and locked objective feedback.
- `unreal/Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp` scopes a splashdown greybox marker to that legacy map.
- These identifiers are *implementation dependencies*, not permission to retain the rejected fuel-cache story.

## Ordered engineering migration
1. Inventory all C++/Blueprint/map/quest/UI/audio references to `VS05_DenithFuelShanty`, `EmptyReserveInspected`, and fuel-related objective copy. Preserve assets and save compatibility.
2. Define post-splashdown state and ship configuration authorization independently of presentation. Default to Seabourne-only; deny Skybourne, Submersible and Starbourne until individually authorized. Do not infer that all ship modes share one unlock.
3. Persist ship restriction and recovery objective across save/load, scene travel and reload. Include negative tests for unauthorized mode changes and story skipping.
4. Replace the convenient fuel-cache objective with coastal recovery, diagnosis and voyage milestones; retain existing scene routing until replacements are playable.
5. Provide traversable Seabourne navigation, meaningful coastal stops and player-facing objectives before removing review route scaffolding.
6. Layer ship personality through authored audiovisual cues with explicit provenance and creator review; no claim of approved VFX, dialogue, music or sentience.
7. Validate native UE build, automated route/gate tests, PIE sailing, navigation boundaries, objective clarity, and cinematic review at an exact commit. Never mark this plan as implementation evidence.

## Scope guard
Documentation only. No runtime state machine, map asset, native test, save format, canon approval, merge or release is changed by this document.

## 2026-11-13 review implementation receipt

- Integration base (before local edits): 31c58a38d56ad0b695a73e55aa5c27f7b5ca9b64.
- Added review-only story-derived GetReviewShipMode / IsReviewShipModeAuthorized fail-closed gate; no new save slot or mode unlock.
- ATSTSSExplorerCharacter exposes read-only Blueprint getter and authorization check. Objective feedback includes Seabourne-only / flight-locked status after flotation.
- Legacy EmptyReserveInspected and map identifiers stay unchanged for save/migration safety; provisional in-world objective copy is now a hull/harmonic survey followed by a coastal survey, not a convenient Denith fuel cache.
- Native Unreal Engine 5.8 Editor build: PASS (local log unreal/Saved/SeabourneRecoveryBuild_20261113.log; not committed).
- Native automation TSTSS.FirstWake: 8/8 PASS, 0 failures, editor exit 0 (local log unreal/Saved/SeabourneRecoveryFirstWakeNative_20261113.log; not committed).
- UNVERIFIED: physical ship configuration switch, rendered transformation, actual sailing gameplay, PIE walkthrough, map asset renaming, or creator visual approval. Ship-controller code is not present in this checkout; the gate is available to future Blueprint/controllers but cannot yet block unknown external switching code.
- Test runner changes to DefaultEngine.ini and DefaultInput.ini were reverted as editor side effects.
