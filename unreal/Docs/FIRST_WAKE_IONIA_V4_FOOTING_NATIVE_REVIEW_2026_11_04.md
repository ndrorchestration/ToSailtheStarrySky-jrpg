# First Wake V4 — Ionia static footing, native-bounded review (2026-11-04)

## Authority and scope

**NONCANONICAL / ISOLATED / DRAFT / UNMERGED / NOT PLAYABLE / NOT ART APPROVED.** This source-only child of [First Wake native asset assembly PR #752](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/752) is based on exact parent `e87bba656cadaa3ef669dd839706e708bd3577d3`. Original First Wake, 10 imported art meshes, production actor/SaveGame and Starbourne access remain unchanged.

The private native scene `FirstWake_AssetAssembly_20261104_REVIEW_V3` has 34 actors (24 prior First Wake actors, including seven unique milestone labels and one PlayerStart, plus ten imported static art models). Its source map SHA-256 is `54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5`. The original V2 Prelude map SHA-256 is `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`.

## Problem — verified by separate native D3D11 geometry probe

A read-only UE5.8.4 actor-bounds audit of the unchanged V3 map measured the imported Ionia static review model at world bounds center z = **−82.3103 cm**, world height **166.5518 cm**, foot z **−165.5862 cm**, while its actor pivot was spawned at world z = 0. That put almost the whole Ionia review model below the harbor ground plane. Ender's static model bottom was about −1 cm. The defect is an asset-placement/pivot mismatch in an isolated lookdev World, **not evidence that approved art or a gameplay NPC has this geometry**.

The V3 D3D11 lookdev also produced real, hash-verified 960×540 screenshots:
- One deferred Slate callback trial correctly ended with **HOLD/no PNG** when the one-shot Unreal scripting mode exited before a callback tick.
- Real synchronous SceneCapture2D/RenderTarget V2 PNG core SHA: `a60ce5f45bca1356ced122cc95961bbd7a2ed03548ffe034644b80038b28aeae`.
- Ship-facing synchronous V3 PNG core SHA: `bec7938e8d33e4e3c46d4e4b935e42d1f332cb7f22de9633a5e08e8bbdf6e8b6`.

Both valid GPU images show a large gray/white blockout surface and black backdrop. **Visual acceptance is HOLD**: the actual ship, wing, bridge and character detail is not sufficiently legible; do not substitute pixel/PNG integrity for cinematic realism or creator approval. The separate V3 wing envelopes also show asymmetric heights, held for mechanical/visual review.

## Narrow V4 corrective source

- `unreal/Tools/stage_firstwake_ionia_footing_v4.py` verifies original exact map SHA, engine 5.8.4 and a new destination vacancy, then uses exactly **one** `LevelEditorSubsystem.new_level_from_template` to derive a separate V4 World from V3. It finds exactly one static Ionia review actor, computes the offset from actual native world bounds `-(center.z - half_extent.z)`, moves only this actor vertically, requires its new foot to be within 0.02 cm of ground and preserves the other 33 actors. Only the new V4 map is saved.
- `unreal/Tools/verify_firstwake_ionia_footing_v4.py` is intended for a **separate engine process**, opens V4 read-only and compares its 34 actors, ten art labels, PlayerStart/milestones and nine other staged-asset positions against the prior V3 native bounds JSON. It refuses missing/changed original map digests and any stale/duplicate evidence destination.
- `unreal/Tools/test_ionia_footing_v4_native_source.py` adds 12 engine-free positive/negative/offset mutation and fail-closed checks. Hosted CI runs **source only**; there is no Unreal runtime on GitHub Actions.

**Do not rerun the staging script if V4 already exists.** It intentionally refuses overwrites and should not be altered to delete prior evidence or change the canonical map.

## Actual native evidence (earlier isolated source revision)

This review experiment was carried out on the authorized NEONTIC UE5.8.4 workstation, in disposable `C:\TSTSS_AssetAssembly_20261104`, with original imported binaries untracked. Its native stage ran at parent source HEAD `e87bba656cadaa3ef669dd839706e708bd3577d3` and produced a **new V4 .umap**:

`/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V4_IONIA_FOOTING`

New map SHA-256: `09ee6d30805bcb54a2b29f0dbfe7ec8975ea9e8abd15c1f8dda1fdf975c2ce3a`. A real Editor process returned exit **0** and a stage receipt with Ionia vertical move **+165.5862 cm**, foot z **0.00 cm**.

An **independent second UE5.8.4 process** reloaded the new saved V4 World, returned exit **0**, and wrote `INDEPENDENT_NATIVE_IONIA_FOOTING_V4_READBACK_PASS_NOT_PIE`: 34 actors, ten art actors, all seven uniquely named milestones, one PlayerStart, exact foot z **0.00 cm** and nine unchanged other staged-asset locations; V3 and original V2 map hashes preserved; original configs untouched; tracked Git worktree clean.

The two process-specific JSON receipts are private in `unreal/Saved/AssetAssemblyEvidence`. Reproduction scripts were archived at `C:\TSTSS_Review`. Native static art .uasset, maps, original renders and source approved images remain **on NEONTIC only**, not in this PR. This new source child commit has **not separately rerun** the native stage (destination already exists) and source CI must not be misrepresented as exact-child-head engine execution.

## Gates and next work

1. Independent visual review with a **new** bounded real D3D11 capture of V4 showing visibly grounded Ionia, using the approved earliest facial-reference images as the authority. A geometry bottom at zero does not prove model orientation, usable footwear, physical contact, rigging or final likeness.
2. Real ship wing/bridge projection and render lookdev: AABB wing-height asymmetry, geodesic dome occlusion, provisional hull proxy, material lighting and sky/sea framing remain HOLD.
3. Player PIE test of WASD/mouse/E/J/F5/F9, seven milestone order, local SaveGame isolation and actual camera line-of-sight; no automatic gameplay proof from a native map load.
4. Real skeletal/animated Ender and Ionia, playable combat UI and distinct water physics, plus cinematic side-by-side creator signoff before any production map promotion, merge, Starbourne unlock or release.

The outcome claimed is **isolated static review geometry corrected with independent native readback**, not a playable vertical slice or approved cinematic art.
