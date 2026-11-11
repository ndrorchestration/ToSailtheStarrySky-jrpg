# V1 Enemy Combat Sandbox — Native Source-Locked Evidence

**Recorded:** November 11, 2026 (ET)
**Scope:** isolated, noncanonical TSTSS Unreal enemy review branch; NOT First Wake production scene.

## Exact-head custody

- Authored and verified source head: `58788f305b32075ab0b898644cb96868f31d2b9a`.
- Engine: Unreal Engine 5.8.4, Windows Editor, on Neontic.
- Full native `Verify-Unreal.ps1` execution: **PASS**; native Win64 Editor build PASS; **32/32 native automation tests PASS**, 0 failed, 0 not-run.
- Native source evidence: `unreal/Saved/MigrationEvidence/58788f305b32-20261111T074231246Z-70f7f53e/` (`head.txt`, `build.log`, `automation.log`, `AutomationReport/index.json`).
- Exact-head build-only receipt separately established by `Verify-Unreal.ps1 -SkipTests`, held locally in `Saved/MigrationEvidence`.
- The original 15-enemy gallery file stayed identical at SHA-256 `deb70ffeecedf572c8bd5b2fab3a515e748d95d27fb2d31f8c0bef2f34c0a022`.

## New native map

- Package: `/Game/TSTSS/Review/SliceEnemyCombatSandbox_V1`.
- Artifact: `unreal/Content/TSTSS/Review/SliceEnemyCombatSandbox_V1.umap`.
- File length: 297088 bytes.
- SHA-256: `108c7582ef8f8073907fbd9d78bd7f487a98b5fb6df927335fadb0fb500f4250`.
- Native Editor author commandlet: `NATIVE_COMBAT_MAP_SAVED_NOT_PIE`, 0 errors / 0 warnings.
- Source-linked local author receipt: `Saved/EnemyGalleryV1/combat-receipt.json`.
- Independent native reload status: `NATIVE_V1_MAP_RELOAD_AND_REVIEW_METHODS_PASS_NOT_PIE`, 0 errors / 0 warnings.
- Local readback receipt: `Saved/EnemyGalleryV1/combat-native-readback.json`.

## Independently checked (native, not PIE)

- All 15 enemy actors and exactly one compiled `ATSTSSSliceEnemyReviewBattleConsole` reloaded from V1.
- Console retains the default `Review_HarborBanditPatrol` wave, one native camera, one instruction sign, and reflected Blueprint-callable battle methods.
- Calling attack before starting an encounter was denied.
- Calling a battle with Ender alone was accepted, then an out-of-range enemy slot was denied.
- Calling a normal attack at valid slot 1 was accepted through the existing combat manager.
- Explicit post-splashdown scenario selection was accepted.
- The original gallery map and V1 map hashes remained unchanged across readback.

## Review instructions (PIE interaction not yet independently confirmed)

Open V1 in Unreal Editor 5.8.4, click Play-in-Editor, focus the gameplay viewport. Use F7 for Ender-only, F8 for recruited Ionia, F9 for post-splashdown Lyra, then J/K for the two enemy slots. The BattleConsole actor provides a review camera, world instructions, and a temporary debug status overlay. Choosing a stage starts only an isolated synthetic encounter; it never advances the campaign.

## Boundaries still open

- Keyboard input delivery, actual PIE victory/defeat, input conflicts, and production UI have not been independently verified in a running GPU Editor viewport.
- Current creatures are built-in BasicShapes proxies; no approved character meshes, skeletons, combat animations, Niagara, audio, cinematic lighting, or final visual QA.
- There is no live First Wake encounter spawn, no SaveGame changes, no story canon approval, and no production merge.
- All test receipts are bound to the **source head above**, not automatically to the later Git commit that adds this binary `.umap` and receipt document.

**Disposition:** native C++ build + 32 automation tests PASS; native V1 map save/reload and review-method smoke PASS; visual/PIE/story gates OPEN; remain DRAFT and UNMERGED.
