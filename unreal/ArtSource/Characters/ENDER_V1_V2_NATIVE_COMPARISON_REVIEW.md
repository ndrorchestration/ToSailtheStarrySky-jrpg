# Ender V1 ↔ V2: paired native Unreal review stage

**Date:** 2026-11-01  
**Scope:** Unreal Engine 5.8.4 Editor Python, disposable CastAllSandbox only  
**Status:** SOURCE-STAGED / ENGINE-FREE REGRESSION PASS; NEW NATIVE COMPARISON EXECUTION NOT YET VERIFIED  
**Art authority:** creator-approved October 30 cast, not procedural source meshes. No cinematic likeness approval.

## Why this slice

Ender's existing V1 and V2 models have separate validated source hashes, engine intake receipts, independent Unreal front/three-quarter screenshots, and visible differences in their coat and hair. But those earlier shots were captured in separate runs, making consistent side-by-side judging harder. This slice generates a **single native comparison stage** with V1 and V2 at identical depth, symmetrical x-offsets and one light/camera setup. It is an observation tool, not another placeholder sculpt or a gameplay character.

The native comparison has **not** been executed on the authorized Unreal machine at this head. Never report hosted source CI as proof of a rendered scene.

## Safeguards and implemented source

- `ender_comparison_contract.py` binds exact SHA-256 and native import receipts. V1: `3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38`. V2: `e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8`.
- It refuses anything except a `CastAllSandbox` project, requires both imported Unreal StaticMeshes to remain review-only and unrigged, and forbids treating either as accepted art.
- `capture_ender_comparison_native.py` loads the existing **disposable** `TSTSS_EnderFidelityV2_Review` map, requires the correctly labeled V2 actor, spawns V1 at x=-115 cm and moves V2 to x=+115 cm in the temporary editor session. No map, imported StaticMesh, production asset or original GLB is saved.
- Two shared camera setups: **front +Y facing** and **three-quarter**. All Unreal `Rotator` calls use explicit named `pitch`, `yaw`, `roll`, protecting against the previously reproduced upside-down-camera defect.
- One lighting setup with manual exposure; no separate per-character lighting advantages. Render tasks request **1280×720 native D3D11** images and emit a task receipt that explicitly says PNG QA is pending.
- `verify_ender_comparison_report.py` must inspect **actual Unreal report `Incoming.png` files**, not filenames in task receipts. It rejects absent/duplicate views and wrong hashes, source state, map, camera list or claims of art acceptance.
- Source CI runs the pure comparison/camera/preservation tests plus syntax compilation. This proves only the source contract, never native rendering, skeletal rigging or likeness.

## Reproduction on authorized Unreal 5.8.4 Windows host

1. Use a **separate disposable** `CastAllSandbox.uproject` with previously verified V1 and V2 StaticMeshes and saved `Saved/CharacterLookdev/ender_fidelity_v1_native_intake.json` and `ender_fidelity_v2_native_intake.json`. Keep the main Unreal project closed to this script; do not reimport or overwrite any asset.
2. Verify the existing map `/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review` is present and the saved five-cast baseline map's SHA has not changed.
3. Enable the **Python Script Plugin** and **Python Automation Test Plugin** in this disposable project. Add `Content/Python/test_ender_compare_native.py` with:
   ```python
   import runpy
   runpy.run_path(r"C:\<checkout>\unreal\ArtSource\Characters\capture_ender_comparison_native.py")
   ```
4. Run `UnrealEditor-Cmd.exe <CastAllSandbox.uproject> -d3d11 -RenderOffscreen -unattended -nop4 -NoSound "-ExecCmds=Automation RunTests Editor.Python.CastAllSandbox.test_ender_compare_native; Quit" "-testexit=Automation Test Queue Empty"`. Read **actual Editor test result** (not only process exit code). The two screenshot tasks must finish and create a new `Saved/Automation/Reports/test_ender_compare_native` tree.
5. Verify the files with `python verify_ender_comparison_report.py <Saved/Automation/Reports/test_ender_compare_native> <Saved/CharacterLookdev/EnderComparisonV1V2Native/capture_task_receipt.json>`. No images should be guessed from the queued file paths.
6. Visually inspect both side-by-side frames and repeat a SHA-256 read of the saved baseline map. Record distinct source/PNG hashes and both acceptable pose/framing and remaining visual defects. Only then can the native comparison gate be marked PASS.

## Expected artistic findings, not pre-approval

V1 has separated rounded waistcoat panels and tube-like strands. V2 has connected cloth-surfaces and tapered cards. Both remain stylized low-fidelity geometry. The October 30 approved Ender artwork requires a recognizable youthful adult face, nuanced hair, practical olive/cream clothing, real cloth thickness/rig deformation, expressive eyes and a believable two-ended staff grip. **The approved source art wins over both candidate meshes.** Do not silently select green vs auburn/copper hair. Preserve Ionia's long curly blonde hair and party height order **Reson > Aepex > Ender > Ionia > Lyra**.

## Acceptance boundaries

**Allowed:** separate, reversible review automation and factual reports.  
**Not allowed:** touching First Wake, gameplay pawn or combat, spawning automated player characters, changing canonical story or visuals, modifying Godot, merging, releasing, or claiming creator approval. Next modeling gate remains owner-guided sculpt/retopology, proper hair topology, materials and skeletal animation rather than endless procedural geometry details.

Tracked against [Ender V2 review PR #654](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/654) and [art/rigging specialist issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649).
