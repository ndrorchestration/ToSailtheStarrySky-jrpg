# First Wake — Unreal cinematic benchmark V1 (review-only)
**Date:** 2026-10-31  
**Authority:** P0 asset/visual review infrastructure, NOT the playable game, art approval, physics proof, or shipped build.  
**Parent:** draft Aureate Wake geometry PR #610 (itself stacked on unmerged UE migration PR #608).

## What was actually implemented
- `unreal/Tools/build_first_wake_benchmark.py`: deterministic composition with a harbor quay, traversable-looking (but **not** physics-validated) pier, placeholder gangway, mooring posts, shoreline study, visual-only sea plane and building blockout.
- Reuses the real `AAureateWakePreviewActor` from PR #610, **not** another fake ship. Leaves its default Skyborne pose and locked Orbiter state unchanged.
- Four camera angles: harbor establishing, ship three-quarter, gangway, sea-landing composition. Each viewpoint has a fixed eye/target pair.
- Authoring markers for **approved Ender and Ionia meshes** and the flyer/harmonic engine; there are **no substitute character models**. Lyra/Talen are not preflight spawns.
- SkySun, SkyFill, atmospheric sky and low sea haze for repeatable look-development.
- Non-destructive safeguards: missing compiled actor fails before changing the scene; refuses overwriting an existing review map; refuses to leave a dirty current map. Does not change startup level.
- Pure-Python layout assertions and automated regression tests under `unreal/Tests/`.

## Local source check (no UE needed)
From repository root on a machine with Python 3.11:

```powershell
py -3.11 -m py_compile unreal/Tools/build_first_wake_benchmark.py unreal/Tests/test_first_wake_benchmark_spec.py
py -3.11 -m unittest discover -s unreal/Tests -p "test_first_wake_benchmark_spec.py" -v
py -3.11 unreal/Tools/build_first_wake_benchmark.py --validate
```

## Native Unreal acceptance sequence (PENDING; cannot substitute source tests)
1. Check out this **exact review branch** in a clean workspace, record commit SHA, Windows GPU, driver, UE and compiler versions. Compile UE **5.8** project and modules.
2. In Unreal Editor, enable **Python Editor Script Plugin** and **Editor Scripting Utilities** under Edit → Plugins, then restart. Both are Editor-only and must **not** run as packaged game logic.
3. Save any unsaved scene edits. Open **Tools → Execute Python Script** (or Output Log Python mode) and choose `unreal/Tools/build_first_wake_benchmark.py` with `--build`. If file menu cannot pass arguments, in the Python console use:
   ```python
   import sys
   sys.argv = ["build_first_wake_benchmark.py", "--build"]
   exec(compile(open(r"FULL_PATH_TO_REPO\unreal\Tools\build_first_wake_benchmark.py", encoding="utf-8").read(),
                "build_first_wake_benchmark.py", "exec"))
   ```
   For a command-line run, pass the script argument after its filename via Epic's `-ExecutePythonScript` route. This creates **only** `/Game/TSTSS/Review/FirstWake_Benchmark_V1`. If that map exists, the tool refuses to overwrite it.
4. Open the generated map. Confirm a single `TSTSS_REVIEW_AureateWake` actor, four persistent wings, two hydrofoils and the four named camera actors. Manually inspect cast import slots: they are *markers*, not playable 3D characters.
5. For each camera capture an authentic Unreal renderer image at **1920 × 1080**, record exact map/game branch, GPU, render preset, exposure policy, and image hashes. Prefer fixed camera transform/exposure across before/after variants.
6. Replace provisional dock/sea/wing geometry with accepted meshes, UVs, PBR material instances and LOD/Nanite policy as appropriate. Use original approved October 30 cast art as the authoritative source for likeness. Confirm Ionia's **long curly blonde hair**, including optional Captain updo; no unapproved replacement artwork.
7. Measure representative p50/p95/p99 CPU/GPU frame times, memory and shader hitches with Unreal Insights / GPU profiler **on actual target Windows hardware**. Review accessibility and contrast at the intended gameplay camera.
8. Only after native compile, captures, geometry/asset review, and creator signoff can the visual results be considered for actual playable First Wake integration.

## Strict boundaries
- The sea plane is **render-only**. It is not a water collision volume, buoyancy system or flotation proof; `SeaContact` and `FlotationConfirmed` must be derived by the authoritative physics observer with real hull velocity/overlap measurements.
- Cameras are review viewpoints, not an approved cutscene timeline. No artificial narrative progression, combat ability, save or crew recruitment is wired by this script.
- No Moon Bridge reveal, Submersible unlock or Orbiter preview activation.
- Materials and meshes are primitive blockouts, **not cinematic-quality art**. Runtime capture, artwork import, Unreal compile and character approval remain UNVERIFIED.
- No main-branch merge, public deployment, Windows installer or creator art signoff is implied.

## Review shot contract
| ID | Shot purpose | Must show | Prohibited inference |
|---|---|---|---|
| 01 | Harbor establishing | Coast/berth orientation, legible ship silhouette | Complete traversable map |
| 02 | Ship three-quarter | 4-wing read, forward bridge, hull form | Approved 3D ship |
| 03 | Boarding | Cohesive gangway/dock relationship | Accepted story boarding/collision |
| 04 | Sea composition | Frame/lighting against ocean | Flotation, sea contact or cinematic sequence verified |

**Source references:** [UE Editor Python](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python); [Editor actor subsystem](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorActorSubsystem?application_version=5.8); [Editor map save](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorLoadingAndSavingUtils?application_version=5.8).

**Next art task:** obtain original approved cast source files and create Ender and Ionia 3D modeling/rigging-ready turnaround packs; import and render against this stage after native engine validation.
