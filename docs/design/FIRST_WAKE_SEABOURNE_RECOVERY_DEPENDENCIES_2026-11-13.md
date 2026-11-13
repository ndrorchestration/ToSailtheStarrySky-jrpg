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

## 2026-11-13 ship preview actor integration — isolated follow-on

Reused the established AAureateWakePreviewActor implementation from the local historical ship-art review checkout (historical source head e336a7759f751cfdabf0cc0444e0817eaf6ae2f9) instead of creating a competing geometry/transition controller. Its four wing components, two hydrofoils, stable legacy C++ enum IDs, approved display spellings and optional artist-supplied review mesh hooks are preserved. The default BasicShapes remain noncanonical geometric proxies. No approved art asset was promoted or imported.

- Added BindReviewStory(UTSTSSFirstWakeState*) to the existing preview actor with fail-closed RequestForm: unbound/unstated, pre-splashdown Seabourne, post-splashdown Skybourne, Submersible and Starbourne requests are rejected. The old bAllowOrbiterPreview debug flag cannot bypass the story gate.
- Upon story binding following save/travel, the ship snaps to the authorized geometry; if story advances during an active preview it can articulate the wings and deploy hydrofoils into Seabourne; a revoked in-progress transition is cancelled.
- ATSTSSExplorerCharacter::BeginPlay now binds any already placed Aureate preview actor found in a scoped local standalone TSTSS review scene to the same First Wake state that was restored through the existing shoreline route. This does NOT spawn an actor, add or change any UMAP, or grant a ship movement mode.
- After a current review actor is placed, the scene can exercise the real four-wing/two-hydrofoil component transitions while the story remains authoritative.
- The legacy VS05_DenithFuelShanty review map has a runtime-only in-world sign substitution targeting the existing FuelShop actor label: 'COASTAL RECOVERY | Survey the ship'. This substitution has compiled but remains unverified by a rendered/PIE scene inspection. Existing saved maps and asset labels remain unchanged.

Native exact-source verification on this follow-on working tree:
- Unreal Engine 5.8 Editor build: PASS, log unreal/Saved/AureateDockReviewSignageBuild_20261113.log (local, ignored).
- Native automation TSTSS.AureateWake: 2/2 PASS, zero failure markers, editor exit 0; log unreal/Saved/SeabourneFinal_TSTSS_AureateWake_20261113.log (local, ignored). Includes form-name, geometry, wing articulation, hydrofoil deployment, denied mode, restored state and transition-revocation checks.
- Native automation TSTSS.FirstWake: 8/8 PASS, zero failure markers, editor exit 0; log unreal/Saved/SeabourneFinal_TSTSS_FirstWake_20261113.log (local, ignored).

Still blocked: no Aureate preview actor is placed in the shipped/review maps in this integration checkout, so no native PIE or render proof of its visual presence. Authentic approved visual geometry, boat locomotion/buoyancy, player helm, ocean navigation, ship menu interaction, coastal story content, audio/animation review and final art approval remain distinct pending work. Do not describe this as a finished ship, playable sailing, or cinematic acceptance.

## 2026-11-13 — Independent coastal Seabourne review world

Read-only Unreal native audit of legacy VS05: 20 actors, SHA-256 5c83e7125eb97aa42d951e89ff1b530600bcc1738287b441f681d44bfaf963bd, and no placed Aureate Wake preview actor. The source map remains byte-identical.

FAILED EXPERIMENT, NOT SHIPPED: EditorAssetLibrary.duplicate_asset(source, destination) followed by EditorLoadingAndSavingUtils.load_map(destination) crashed the Unreal Editor (exit 3, EditorServer.cpp line 2544, "World Memory Leaks: 2 leaks objects and packages"). Python referenced a temporary duplicated world/package during the load. No destination map was saved by this attempt; VS05 remained intact. The unsafe script has been moved to ignored unreal/Saved/UNSAFE_DuplicateLevelCrash_20261113.py; log saved at unreal/Saved/SeabourneNativeStagingRun_20261113.log. DO NOT RE-RUN THIS DUPLICATE/LOAD PATH UNCHANGED.

SAFE ALTERNATIVE: authored a new blank Unreal review world without loading/duplicating another map in that commandlet. New independent path: /Game/TSTSS/Review/SeabourneRecovery/L_CoastalShip_SeabourneReview (SHA-256 52a63dc730fb42c7571255a6ea1b0fd5eafb1b41afe5ec59e90ca071d380115e). Created with unreal/Tools/stage_seabourne_fresh_review.py. The one-shot script refuses overwrites or another project root. Scene includes twelve actors: one native Aureate Wake geometry preview in Seabourne editor pose, coastline, walkable pier/rails, visual ocean, PlayerStart, lighting and explicit noncanonical review notice. It does not inherit VS05 story state. Runtime story-binding remains handled by ATSTSSExplorerCharacter in existing review worlds.

The native editor actor exposes an editor-only EditorReviewPose with ApplyEditorReviewPose(), as Unreal Python has no rerun_construction_scripts method for this native actor. This is strictly cosmetic staging, not permission to unlock other forms. Native UE5.8 Editor compile PASS (local unreal/Saved/AureateEditorPoseAPI_Build_20261113.log). Independent saved-map reopening PASS (unreal/Tools/verify_seabourne_fresh_review.py, unreal/Saved/SeabourneFreshReadbackRun_20261113.log): one ship, Seabourne pose, four wings, two hydrofoils, PlayerStart. Post-map regression TSTSS.AureateWake 2/2 PASS and TSTSS.FirstWake 8/8 PASS, editor exit 0, zero failure markers (unreal/Saved/SeabournePostMap_TSTSS_AureateWake_20261113.log and SeabournePostMap_TSTSS_FirstWake_20261113.log). Evidence logs and JSON receipts are local, not published.

REMAINING GATES: No creator-approved 3D ship asset promotion, GPU screenshot, PIE walkthrough, in-game visual acceptance, water-borne movement/buoyancy, helm, coastal quest implementation, or ship-menu UI integration has been verified. The staged geometry scene is not a playable sea voyage. Existing playable maps and protected main remain untouched; this work is isolated and review-only.
