# Ender V5 — native 3D authoring readiness and green-eye study

**Evidence date:** November 3, 2026 (US/Eastern). **Scope:** reversible Unreal Engine 5.8.4 source-side and sandbox-only character work. **Art status:** unapproved. The earlier approved character faces remain the likeness authority; the newer five-person ship-deck image is secondary for clothes, materials and lighting.

## Verified native toolchain

Engine: `5.8.4-58902052+++UE5+Release-5.8`. The installed MetaHumanCharacter editor provides `get_face_landmarks`, `translate_face_landmarks`, `commit_face_state`, `request_auto_rigging`, `request_texture_sources`, and `build_meta_human` (plus face coefficient and editor registration methods). The Epic-supplied local Python examples for face sculpt, auto-rig and assembly are installed. An isolated **read-only** native probe completed with exit code 0 at `C:\MH2\CastAllSandbox\Saved\CharacterLookdev\V5RigReadiness\native_capabilities_review01.json`. No rig or character render is inferred from API availability.

## Rig attempt: blocked, not completed

A byte-identical noncanonical copy of the unrigged Ender V5 base was created under `C:\MH3\CastAllSandbox`. The clone initially matched original MetaHuman UAsset SHA-256 `7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd` and V2 review map SHA-256 `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`.

A native **joints-only MetaHuman auto-rig cloud-service trial** started using the isolated clone. The Unreal log showed:
- `MetaHuman Optional Content folder not found` — character Creator functionality limited; default texture synthesis and skin editing disabled.
- `No existing persistent auth credentials were found for automatic login` — Epic account portal/browser sign-in was launched.
- The isolated process was stopped at the authentication prerequisite. Its Saved-only receipt is `OPERATOR_STOPPED_AT_EPIC_AUTH_AND_OPTIONAL_CONTENT_GATE`.

**No authenticated rigging result, downloadable Core Data installation, high-resolution texture, skeletal asset, cinematic assembly, character animation or purchase was achieved.** The browser sign-in step belongs to the owner; do not copy any sign-in URL into the repository.

## Actual native MetaHuman eye-parameter authoring: persisted in MH4 only

A second byte-identical clone `C:\MH4\CastAllSandbox` was used for a minimal, canonical-color-aligned **green iris parameter study**. Without any cloud service, software installation, hair decision, or facial geometry sculpt:

- Both eyes' MetaHuman `global_tint` were set to RGBA `(0.25, 0.78, 0.24, 1)`, with `global_saturation = 1.35`, leaving the existing iris pattern, pupils, sclera and face sculpt otherwise untouched by the script.
- Initial in-memory editing passed but saving with the default dirty-only behavior did not alter the UAsset. That incomplete attempt is preserved as `green_iris_parameter_study01.json` with status `PARAMETER_STUDY_FAILED`.
- Retried the native edit using `EditorAssetLibrary.save_loaded_asset(character, only_if_is_dirty=False)`. **Native save succeeded**; new sandbox asset SHA-256 `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`, different from the original.
- A fresh independent Unreal Editor session reopened the saved MetaHuman and confirmed left/right tint and saturation persisted. Receipt: `C:\MH4\CastAllSandbox\Saved\CharacterLookdev\EnderV5EyeLookdev\green_iris_reopen_verification01.json`, status `REOPENED_SAVED_V5_GREEN_IRIS_PARAMETER_PASS`.
- Facial integrity: a first stricter read found a transient mismatch at landmark index 46. Two subsequent **read-only native** index audits, one in the original `MH2` and one in the edited `MH4`, each reproduced the original **79/79** indexed `(x,y,z)` coordinates exactly at the established five-decimal precision. Both reports give `mismatch_count = 0`, `maximum_difference_cm = 0`. Cause of the earlier one-off discrepancy is unconfirmed; the repeatability evidence does not authorize cinematic likeness approval.
- Original MH2 UAsset and review-map hashes remain unchanged. The work was performed with `-nullrhi`: this is **not a visual or native GPU rendering pass**.

Reproduction source scripts committed to this draft: `native_ender_v5_green_iris_mh4_study.py`, `verify_native_ender_v5_green_iris.py`, `verify_native_ender_v5_face_repeatability.py`. They are sandbox-specific and fail closed outside expected isolated project paths/hashes. Their native receipts and modified `.uasset` remain only on the authorized workstation, **not** committed as production art.

## Art and build sequence, held at explicit gates

1. **Primary facial identity:** review earlier approved Ender faces, register only actual approved eye centers, nose tip and chin against the 79-index native atlas. Do not treat geometric ±X pairing as anatomical identities. Copper/auburn-versus-dark/green hair conflict remains held; goggles and full-length centered-grip brass-ferrule staff remain character locks.
2. **Face and body authoring:** make small face-sculpt comparisons in *new isolated copies* and obtain creator visual acceptance before rigging the production head. A rig may restrict later head/body edits; do not spend remote rigging work on an unapproved likeness.
3. **One-time owner prerequisites:** in Epic Games Launcher > installed Unreal Engine 5.8 > Options, enable **MetaHuman Creator Core Data** if missing; complete the Epic sign-in in Unreal Editor using the user's own account. Check available disk space before downloading. No automatic purchases or third-party asset installs.
4. **Rig and assemble:** only after reference and prerequisites pass, run authenticated MetaHuman auto-rig and high-resolution texture requests on a disposable candidate. Assemble both a **UE Cine** character for high-fidelity cinematics and a **UE Optimized** character for gameplay if compatible with the rig/materials. Record actual Unreal output paths, skeleton, skin weights, deformations, face controls, performance, and proof frames before game integration.
5. **Outfits/hair and gameplay:** model Ender's cream shirt, olive waistcoat, boots, satchel, goggles, and hand-to-staff contact at true 3D fidelity, with fit-tested geometry and appropriate skin weights. After Ender passes, reuse the same pipeline for Ionia, Lyra, Reson, and Aepex, preserving distinct approved facial identity and canonical height order `Reson > Aepex > Ender > Ionia > Lyra`.

**Hard hold:** `3D_ASSET_PARAMETER_EDIT=VERIFIED_IN_SANDBOX`; `GREEN_IRIS_VISUAL_ACCEPTANCE=NOT_ESTABLISHED`; `CLOUD_RIG=BLOCKED_BY_AUTHENTICATION`; `CORE_DATA=ABSENT`; `FULL_BODY_RIG_AND_CINEMATIC_ASSEMBLY=NOT_ESTABLISHED`; `PLAYABLE_CANON_PROMOTION=NOT_AUTHORIZED`. Draft remains unmerged. No gameplay project, approved character reference, base V5 face mesh, or production Unreal content has been promoted.

## Official Epic workflow documentation

- [Getting Started with MetaHuman Creator](https://dev.epicgames.com/documentation/en-us/metahuman/getting-started-with-metahuman-creator)
- [MetaHuman Creator Python scripting](https://dev.epicgames.com/documentation/metahuman/python-scripting-for-metahuman-creator)
- [MetaHuman character assembly](https://dev.epicgames.com/documentation/metahuman/assembly)
