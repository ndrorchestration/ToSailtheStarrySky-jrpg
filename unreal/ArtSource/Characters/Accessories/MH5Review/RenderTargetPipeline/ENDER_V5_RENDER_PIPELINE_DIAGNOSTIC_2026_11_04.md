# Ender V5 — verified native color-path diagnostic (2026-11-04)

**Status: NATIVE_CAPTURE_PASS / VISUAL_LIKENESS_HOLD / NONCANONICAL / DRAFT.**
Stacked on the exact V5 study source head `a2378f7d6c280393363d0767d839c7f2838241ea` in a new, separate review worktree. This is *not* a sculpt, a completed character, an approved costume, or a production-game integration.

## Experiment and verified native evidence

On the authorized NEONTIC Windows workstation, Unreal Engine **5.8.4 D3D11** loaded the actual temporary V5 MetaHuman face and previously imported V1 brass-look goggles in the disposable content-only `MH5/CastAllSandbox` project. The original full-color render had blown-out gold and an almost white face. The previously documented SceneCapture exposure-bias −2 EV trial yielded **no pixel change**, so repeating that tweak was not justified.

We made **one capture-source change**, `SceneCaptureSource.SCS_FINAL_COLOR_LDR` to `SceneCaptureSource.SCS_BASE_COLOR`. The same saved review map, original MetaHuman UAsset, V1 goggles GLB, temporary goggles transform, camera, three pointlights, and 480 × 320 RenderTarget export mechanism were reused. This is a **diagnostic G-buffer/base-color view**, not a beauty render or a fix.

| Genuine UE5.8.4 capture | Native PNG-core SHA-256 | White-clipped fraction in fixed (140,42)-(340,320) face/goggles crop |
|---|---|---|
| Original shaded FinalColor, `RenderTargetCombined02` | `212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808` | **56.417%** |
| Actual new BaseColor, `RenderTargetCombined04_BaseColor` | `33b48e1d1c9ce4b577670116bce92527bfc64d1d9d41839a1936c153080e48c0` | **0.000%** |
| Manual exposure mode/bias −2 EV, `RenderTargetCombined05_ManualExposure` | `212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808` | **56.417%**, byte-identical to original; no improvement |
| **0.1× temporary point-light power**, `RenderTargetCombined06_LightTenth` | `90de28a3d58b37f100c0c8066369c7e18aee49696cbbb5530f2dbc8776c5e58f` | **0.0072%**, actual native improvement |

The crop measures near-white pixels with **all RGB channels ≥245**; it is not a photometric/material-fidelity score. The base-color view is relatively dark: the face is gray/olive and goggles are bronze-colored. This rules out the simplistic claim that the stored base colors are uniformly white. It does **not** determine whether the clipping arises from lighting, a MetaHuman preview default material path, eye adaptation, or tonemapping. A further **genuine native low-light experiment** multiplied all three transient review-light intensities by **0.1** while leaving the camera, character, goggles, level and source hash unchanged. This yielded a distinct, legible full-color image without altering production materials. Independent raw PNG chunk CRC, receipt, source-hash and Pillow pixel comparisons passed. Within the exact same crop, white clipping declined by **56.4101 percentage points**, from **56.4173% to 0.0072%**. The image still has unapproved skin, bald scalp and old spectacle-like goggles; lower clipping is not likeness approval. The engine exporter appended 41,322 trailing bytes after a valid PNG IEND, which the verifier separately records and does not treat as image pixel data. `verify_ender_v5_native_capture_matrix_20261104.py` records all three FinalColor/Manual/0.1× native image receipts in a new deterministic report.

The real native BaseColor `capture_receipt.json` records a 480 × 320 PNG with correct PNG chunk CRCs, independent core hash, and 1,602 extra exporter bytes *after PNG IEND*, a previously known exporter quirk. The manual trial independently records valid PNG core and an identical core SHA to original FinalColor; changing to manual exposure did **not** alter pixels. A prior independent source validator confirmed original PNG core validity, and the new strict `verify_ender_v5_basecolor_diag_20261104.py` reopens both image cores using Pillow and checks crop statistics, source-only code delta and contradictory acceptance guards. Its recorded status is `NATIVE_BASECOLOR_DIAGNOSTIC_PASS_ART_HOLD`.

## Immutable source boundaries

- V5 MetaHuman UAsset SHA-256: `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`.
- Saved review map SHA-256: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`.
- **V1-only rejected spectacle-like goggles** GLB SHA-256: `76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae`.

All three hashes matched before the new render and remained identical afterward. The *only* Editor process we closed was the review process started for these particular tests. No saved Unreal map, character source, player project, production art, save file or protected branch was changed. All screenshots remain private on the authorized workstation; no image files are checked into GitHub.

## Artistic and development holds

The user rejected V1 goggles as glasses. The separate original **sealed aviator V2** design is a newer offline review candidate described in `../ENDER_GOGGLES_V2_SEALED_AVIATOR_REVIEW_2026_11_03.md`; this diagnostic uses V1 solely because it is the model already imported into MH5. **No V2 native import, wearable contact, actor attachment or V2 approval is established by these tests.** Any separate concurrent V2 trial must provide its own independently scoped source hashes and receipts.

Ender's face is not matched to the creator's first approved portraits, and realistic auburn/dark-copper hair, facial skin, fitted clothes, credible staff grip, true skeletal mesh, animation and production-game validation are still open. The MetaHuman Core Data/creator authentication dependency remains distinct from the rendering problem. Do not confuse diagnostic MetaHuman preview skeletal components with a playable/exported animation-ready character. No game or character-art promotion, release or PR merge is authorized.

## Reproduction and follow-up

1. In the isolated exact-head worktree, run `python unreal/ArtSource/Characters/Accessories/MH5Review/RenderTargetPipeline/verify_ender_v5_basecolor_diag_20261104.py` on the NEONTIC workstation with Pillow available and the private native receipts retained. It creates the unique JSON report once; do not overwrite evidence sessions.
2. Inspect the committed source-only reproducer `native_rt_ender_v5_goggles_basecolor_diag_20261104.py`: it fails closed on wrong sandbox, wrong engine, source hash drift, duplicate evidence directory or native capture failure. Do not launch into a production project.
3. The global **0.1× temporary review-light-power** test `native_rt_ender_v5_goggles_light_tenth_20261104.py` has now run successfully in the same disposable UE5.8.4 D3D11 MH5 world. Verify via `python unreal/ArtSource/Characters/Accessories/MH5Review/RenderTargetPipeline/verify_ender_v5_native_capture_matrix_20261104.py` on NEONTIC. Never overwrite its unique output directory; no screenshot binary or user references are committed. Reuse the lower-power lookdev lighting in a separate future reference-comparison session only after facial identity and sealed-goggle review gates are independently addressed.
4. Next art work requires creator-reference-aligned sculpt/proportions and a real sealed goggles fit test, independent of all diagnostic screenshots. Keep original art authority and V1 rejection intact.

These results diagnose a shading-path failure; they do **not** complete Ender.
