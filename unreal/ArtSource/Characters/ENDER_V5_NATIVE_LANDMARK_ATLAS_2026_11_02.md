# Ender V5 MetaHuman — read-only 79-landmark technical index atlas

**Date:** November 2, 2026 (US/Eastern). **Reversible milestone: native landmark indexing verified; reference matching and character likeness NOT established.**

Stacked on [draft MetaHuman authoring feasibility PR #719](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/719) at parent commit `8ae75a6f5809c76581ca98a502954d164c80c58f`. Source-side changes are restricted to a new isolated Unreal inspection script, an independent evidence verifier, a source-only atlas renderer, six negative-control tests, technical image/CSV/JSON outputs and documentation. Protected main, runtime/game project, canonical cast, source Ender V1–V4, raw MetaHuman V5 asset and the saved reference map are unchanged.

## Canon and approved reference boundary

Approved references from the private project Library are:
- **`To Sail the Starry Sky: Core Cast.png`** (approved later group appearance, young adult Ender with bright green eyes, brass goggles, dark/green-looking tousled hair).
- **`Ender: Solarpunk RPG Character Sheet.png`** (older approved individual reference with bright green eyes, brass goggles, brown/auburn hairstyle, youthful anime-JRPG proportions).

Do not silently resolve the hair-color and realism/style mismatch; the established written individual art lock and later approved cast group must be reconciled by the creator. Ender is 22, carries a resonance fighting staff with centered wrap and brass ferrules; the relative height order remains **Reson > Aepex > Ender > Ionia > Lyra**. No numerical canonical heights or facial landmark measurements were inferred from drawings. The original reference images are **not copied into the public GitHub branch**.

## November 3 creator decision — earliest approved faces take precedence (review-only)

The creator clarified: **“the faces from the first are most correct.”** The more recent realistic five-person daylight ship-deck picture is **secondary and usable only when necessary for clothing, equipment, materials or cinematic lighting**; it is not authorized as a 2D-to-3D face-landmark source. Preserve established individual character locks and the known five-person identities independently of misleading generated character-bible role/stat labels.

Two earlier realistic Ender face sources have been located in the private project library, `Aetherwake: Steampunk Skybound Crew.png` and `Aetherwake: JRPG Character Design Board.png`; `Ender: Solarpunk RPG Character Sheet.png` remains the earlier approved individual style cross-check. The precise primary image and feature-level agreement across these styles **have not been creator-approved for face mapping**. Treat the generated later `Core Cast` collage's swapped identities/roles/statistics as untrustworthy for anatomy. Do not infer exact landmark measurements from illustrations or conflate image-plane left/right with anatomical left/right.

The source-controlled `ender_v5_reference_priority.json` and `verify_ender_v5_reference_priority.py` now enforce a **fail-closed reference contract** with four intentionally empty image landmark slots (image-left eye center, image-right eye center, nose tip, chin). Six engine-free regression/negative-control tests reject unauthorized facial-reference precedence changes, secondary-image promotion, invented image pixels or native indices, silent hair-color resolution and claims of an approved sculpt. A private, provisional three-reference comparison sheet was prepared outside GitHub for human review; **no privately supplied source PNG or proposed pixel coordinate is committed**, and the 79-index native CSV remains `UNMAPPED_REQUIRES_HUMAN_REVIEW`.

This is a *pre-sculpt governance/readiness increment only*. The earlier-face instruction does not resolve auburn/copper versus green hair, 2D-to-3D semantic correspondence, missing optional MetaHuman Core Data, materials, skin, rig, gameplay or owner final likeness approval. Any supervised A/B face edit requires an artist-confirmed primary source and four reviewed feature-to-native-index correspondences first. See [character art issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649) for the hold.

## Exact native Windows Unreal 5.8.4 proof

Authorized `neontic`, new disposable `C:\MH2\CastAllSandbox`, **NullRHI / no renderer**. A newly isolated local `.uproject` enabled `MetaHumanCharacter` only in that clone; no install, downloaded content, other software changes, saved game maps or production assets.

One Unreal Python automation `Editor.Python.CastAllSandbox.test_ender_v5_landmark_atlas_native` returned **Success / exit 0**. Read-only `capture_ender_v5_native_landmarks.py` loaded the prior real `MetaHumanCharacter` V5 UObject, registered `MetaHumanCharacterEditorSubsystem`, retrieved exactly **79** ordered native facial-landmark `unreal.Vector` positions, then deregistered without calling face translation, commit, save, assembly or rigging functions. Asset hash checked before/after: **`7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd`** (757,405-byte native `.uasset` from V5). Previously verified V2 saved map hash also unchanged before/after: **`025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`**.

Native 79-point JSON SHA-256 **`9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed`**. Coordinate spans in centimetres: **X=17.838, Y=21.692, Z=26.850**; precise per-point values and bounds in `ReviewEvidence/2026-11-02/EnderV5LandmarkAtlas/native_landmark_index.json`. A second, independent Python script `verify_ender_v5_native_landmark_atlas.py` re-read actual native engine log and unchanged original asset/map bytes and **exited 0** with `V5_NATIVE_INDEX_COORDINATES_VERIFIED_NOT_REFERENCE_MATCHED`. This is **native MetaHuman API data**, NOT a native D3D11 render or a source-image registration.

### Technical visual index and handoff worksheet

- [Native index atlas PNG](ReviewEvidence/2026-11-02/EnderV5LandmarkAtlas/TechnicalAtlas/v5_native_79_index_atlas.png) — **2560×1450**, technical two-panel projection only, PNG SHA-256 **`13faf1b8400123a8a0227b4938db199c7b700ec165b327f66ebcd594042e6652`**. Left panel projects source-space **X vs Z**; right panel projects **Y vs Z**. These are native coordinate plots, **not Unreal screenshots, not the approved art**, and the horizontal directions do not certify that we have matched camera pose to any approved image.
- [Unmapped artist worksheet CSV](ReviewEvidence/2026-11-02/EnderV5LandmarkAtlas/TechnicalAtlas/v5_landmark_index_unmapped.csv) — 79 rows indexed 0–78, native X/Y/Z cm, blank semantic-label, approved-reference filename, image pixel coordinates and **UNMAPPED_REQUIRES_HUMAN_REVIEW** state. CSV SHA **`99a2b7ffcc7cbb0c752d0371e38c1b8f11b1cd39fb606b4ad439579026ebf556`**.
- [Atlas manifest](ReviewEvidence/2026-11-02/EnderV5LandmarkAtlas/TechnicalAtlas/atlas_manifest.json) records all input/output hashes, projection axes, non-art status and missing source-image registration.

All 79 *indices* are verified. **No native index has been authoritatively labeled 'left eye center', 'nose tip', 'jaw', etc.** We must not derive anatomical semantic correspondences just by sorting coordinate values. The worksheet is designed for manual reference matching by a character artist with calibrated front and side artwork/face renders.

## Verification and known limitations

- Native Unreal automation: **PASS / exit 0**, actual local log `C:\MH2\V5NativeLandmarkAtlas.log` (UTC November 3).
- Independent actual native proof: **PASS / exit 0** — 79 unique consecutive indices, finite native position components, bounds integrity, actual `.uasset` checksum, unchanged .umap checksum, genuine Editor automation success marker.
- Source-only negative controls: **6 focused checks** cover false art approval, non-unique/index order failure, extreme-bound tampering, nonfinite coordinates, code path no-op restrictions, complete CSV and actual PNG pixel integrity. This does not establish reference registration or true photogrammetry.
- MetaHuman Creator optional Core Data and skin-texture synthesis are still **missing/disabled** from the earlier V5 native findings; no attempt to install was made. No skin authoring, rigging, hair groom, MetaHuman assembly or native cinematic rendering in this milestone.
- **NO changes** to the default MetaHuman face; no facial pose edits, no gameplay integration, no creator art approval, no saved game map or source release.
- The image on this branch is a **Python/Pillow technical diagram**, not output of Unreal's D3D11 viewport. It intentionally contains no approved artwork and no private user likeness data.

### Cross-platform Git SHA-256 byte-custody correction

GitHub's first Linux engine-free workflow correctly detected that Git had normalized CRLF to LF for the raw Windows native JSON/CSV evidence, changing bytes and invalidating the original native SHA-256 in the atlas manifest. The failure was a **source evidence byte mismatch**, not a failed Unreal mesh or geometric coordinate test. Added a narrowly scoped \`ReviewEvidence/.../EnderV5LandmarkAtlas/.gitattributes\` to mark exactly the 79-point JSON and unmapped CSV as \`-text\`, then staged them with \`git add --renormalize\`. Verified that indexed Git blobs now exactly match the actual native Windows files' SHA-256 values, and added a regression test to catch any future line-ending drift. No numerical coordinates, artwork or source engine assets changed.

## Acceptance and next minimum reversible art step

Current **PASS**: source custody, real 79 indexed native API landmarks, independent proof, technical coordinate plots and unmapped review worksheet. **HOLD**: anatomical semantic index labels, source reference pixel coordinates, perspective/camera matching, naturalistic eye/eyelid sculpt, skin/groom materials, rig/animation, gameplay and owner acceptance.

**Next:** have a human reviewer annotate *both approved reference styles* (where and how they disagree) for **four features only**: paired eye centers, nasal tip and chin. Resolve stylization and hair color separately. Assign semantic names only to verified MetaHuman indices, with screenshot evidence showing point selection and camera pose, and record ownership/date. No automatic face edits until the label mapping is approved. After that, make tiny supervised facial-landmark changes in a **new disposable MetaHuman project**, capture native before/after under fixed camera conditions, check no accidental rig/skin changes and seek explicit creator visual signoff before integration.

The approved cast is unchanged, and this draft should remain unmerged.
