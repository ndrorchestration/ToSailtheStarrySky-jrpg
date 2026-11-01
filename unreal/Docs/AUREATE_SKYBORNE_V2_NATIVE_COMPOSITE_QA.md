# Aureate Wake — native Skyborne composite visual QA (2026-11-01)

**Authority:** Creator-approved 1536 × 1024 four-configuration artwork, unchanged SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`. Current 3D output is **NONCANONICAL REVIEW ART, NOT APPROVED**.

## Reproduced native outcome

Windows Unreal Engine **5.8.4-58902052**, GPU **D3D11 SM5**, isolated asset-only project `C:\TSTSS_Unreal_V2NativeQA_20261101\NativeArtReviewSandbox`. This project is separate from the live editor/production maps, and the earlier body-only map `/Game/TSTSS/Review/V2_Body_Studio` remains saved and unmodified.

- **Exact source/provenance:** V2 hull/dome generated from detached Git source commit `62f1fc32422e7278e28922de9abeef93c4c47153`, plus review-only C++ Skyborne pose contract from [draft #686](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/686), head `b7ab291fdfc3f4f82281cc9a9824a83d0e356d70`.
- **Exact imported wing provenance:** ten `.uasset` files (wing, root support, materials and textures) copied from the previously imported, never-merged, exact-head native review checkout `fcfd39b3961a6e923c076c1903d1a98bb94c6614`. All 10 source/destination SHA-256 pairs independently MATCH. The source worktree was untouched.
- **New native UE level:** `/Game/TSTSS/Review/V2_Skyborne_Assembly_V1`; saved `V2_Skyborne_Assembly_V1.umap`, 50,140 bytes. Two V2 hull/bridge body meshes were reused; **exactly four dragonfly wings and four root supports** added, using the Skyborne root-pivot positions/rotations and support links from C++ `AAureateWakePreviewActor::RootPivotedWingPose` and `UpdateRootSupportTransforms`, plus four dedicated CineCameraActors. Wings measured ~296.37 cm along the native mesh +X dimension; support mesh ~100.00 cm. All collision disabled for visuals; **not the compiled ship actor**.
- **Native commandlet:** `UnrealEditor-Cmd.exe -run=pythonscript -nullrhi` returned `SKYBORNE_STAGE_EXIT=0`; output `native_skyborne_stage_receipt.json`.
- **Genuine four-camera GPU render:** Unreal D3D11 automation test `Editor.Python.AureateWakeNativeQA.test_skyborne_assembly` returned `Result={Success}`, `TEST COMPLETE. EXIT CODE: 0`. All four 1920×1080 `Incoming.png` files passed independent PNG IEND/CRC, resolution, unique SHA, and nonblank variation checks. SHA-256 receipts:
  - Three-quarter: `21dd41da3595022e56b736fc8080c4ab3734f2e29914364e1c0c0d0295294ea6`
  - Port side: `54de9835f1d3e75b0c0a470fd1562d1f545ce3cabf182636b4bc5353f0f9703d`
  - Dorsal: `a8656e44e046bf126f6fc5e645f5b91a68cea881a8b94df64c558c6e04cb64de`
  - Bow perspective: `336d91b290156b2dbe5b4fe44a89f47812388cc5d83bb7b20e3e73cfc537d`
- Native output remains on the authorized Windows machine under `NativeArtReviewSandbox\Saved\Automation\Reports\test_skyborne_assembly`. Contact sheet: `NativeArtReviewSandbox\Saved\ReviewReceipts\AureateWake_V2_Skyborne_UE58_NativeFourView.png`. No screenshots, binary assets or personal desktop paths were committed or publicly deployed.

## Independent visual review and acceptance hold

Actual render shows a white slab-like primary hull, a simple gold-ribbed geodesic dome with no convincingly inhabitable cockpit, and four working cyan/glittering wing surfaces on exposed skeletal hinges. Root supports appear present but need a more natural blended root-to-hull join and sweep. The overall silhouette is **far short** of the approved elegant dragonfly vessel; high-quality ivory/gold/navy mechanical layering, fuller glass bridge interior, articulated fairings, coherent deck proportions and camera-matched silhouettes remain missing.

**Non-evidence:** This exact composite uses native static mesh actors—not the C++ ship preview actor. Therefore it does **not** prove #686 native UHT compilation, actual rig transitions, full sea landing/hydrofoil behavior, pressure integrity, seamless wing fold, crew collision, story progression or Orbiter clearance. The prior attempted full-editor C++ build remained blocked by unrelated Live Coding in the already-running Editor; do not stop that Editor without authority.

## Reproducible source-side guard

`unreal/Tools/aureate_skyborne_composite_plan.py --validate` (standalone Python) emits the four-wing Skyborne arrangement and checks the C++ source for exact root-pivot and visual support equations. `unreal/Tests/test_aureate_skyborne_composite_plan.py` enforces 8 pose/mirroring, provenance, count and authority invariants. Separate CI does not assert that native screenshots have been produced on GitHub runners.

**Next acceptance priority:** artist-authored high-fidelity hull and bridge redesign in a new isolated revision, preserve four reviewed wings, test real attached supports and collision; then native screenshot comparison with the approved image and creator signoff. Do not merge this PR or unlock Orbiter.
