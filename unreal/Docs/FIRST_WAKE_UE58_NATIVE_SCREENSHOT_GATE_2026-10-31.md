# First Wake native 3D screenshot capture and verifiable review receipts

**Date:** 2026-10-31. **Status: EDITOR EXECUTION NOT YET VERIFIED.** This is review-only tooling for the existing Aureate Wake vessel study and Prelude → Chapter 1 scene benchmark; it is neither a game capture nor artistic approval until actual Unreal 5.8.4 PNG images and engine logs are obtained.

## Implementation

- [`capture_first_wake_review.py`](../Tools/capture_first_wake_review.py) references the four **existing** CineCameraActor positions in `build_first_wake_benchmark.py`; it does **not** invent new shots, spawn actors, alter camera transforms, save maps, modify water physics/story events, or unlock Orbiter.
- Sequence **01–03** represents **Prelude**: harbor/hiring context, Aureate Wake silhouette, gangway/boarding composition. Shot **04** represents **Chapter I, Act I: Splashdown**, but **only** as a staged composition; the actual Chapter I state begins when physical `FlotationConfirmed` is reached, not from a review camera or a scenic ocean mesh.
- All screenshot requests require the exact map `/Game/TSTSS/Review/FirstWake_Benchmark_V1`, exactly one matching CineCameraActor for each source shot, one compiled `AureateWakePreviewActor`, four wings, four supports, two hydrofoils, a stationary Skyborne pose, the hidden Orbiter disabled, and **both imported corrected authored wing/root-support meshes already bound**. A cube-only blockout is insufficient for this capture gate.
- Uses Epic's [UE5.8 AutomationLibrary.take_high_res_screenshot](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AutomationLibrary) with each camera at **1920×1080**, HDR off, and the documented [AutomationScheduler latent tick method](https://dev.epicgames.com/documentation/unreal-engine/write-editor-tests-with-python-in-unreal-engine). The call merely **schedules** the task. Only the Editor can actually finish rendering and create files; offline Python cannot.
- `--verify-files` opens **four real PNG files**, checks signature, IHDR size, chunk CRCs, presence of IDAT/IEND and exact 1920×1080 dimensions; computes SHA-256 and byte sizes for a review receipt. It rejects a partial set and does **not** assert that matching image bytes necessarily came from Unreal rather than another source; correlate them with Editor logs and the clean Git head.
- Hosted CI requires pure-Python shot planning and mocked Editor/PNG regressions. These are **not** substitutes for engine shader, native frame-time, or aesthetic evidence.

## No-engine plan check (safe now)

```powershell
python unreal/Tools/capture_first_wake_review.py --inspect --run-id Review20261031
python -m unittest discover -s unreal/Tests -p test_first_wake_capture_receipts.py -v
```

No screenshots are created by either command.

## When UE5.8.4, MSVC x64 and SDK are available

1. Finish native `Check-UnrealHost.ps1 -RequireReady` and `Verify-Unreal.ps1` on a clean exact-head checkout; do not bypass their tests.
2. In Unreal Editor, open **only** the isolated First Wake benchmark map. Enable the Python Editor Script Plugin as required. Create the review map only if absent, using the guarded benchmark builder. Do not touch the playable level or use a pre-existing dirty map.
3. Import the corrected 280 cm wing GLB and 100 cm root-support GLB through their respective isolated review importers. The bridge/wing surfaces are **not** creator-approved cinematic artwork. Bind them only through `bind_first_wake_review_ship_art.py`, inspecting its guarded conditions; manual review and save remain explicit.
4. In an active, rendering **Unreal Editor**, execute `capture_first_wake_review.py --capture-in-editor --run-id Review20261031`. The tool registers asynchronous screenshots. Run inside the Editor Python test/automation context that services `AutomationScheduler`; if the task cannot tick, mark a capture HOLD rather than success. The script returns **CAPTURE_TASKS_SCHEDULED_NOT_VERIFIED**, not image proof.
5. Locate all four actual screenshot PNGs in the Unreal Editor's output and copy them to an isolated review folder; filenames match the `--inspect` plan. **Do not guess the output path**, overwrite existing shots, or publish candidate art without approval.
6. Validate all four actual files by running:

```powershell
python unreal/Tools/capture_first_wake_review.py --verify-files --run-id Review20261031 --capture-dir "C:\Path\To\Actual\Unreal\Screenshots"
```

Preserve the generated receipt output alongside screenshots, engine logs, Git SHA, editor version, GPU and build/test proof. Compare light, water shader, ship read, environmental silhouettes and readable foreground characters. Capture separate physical SeaContact/FlotationConfirmed instrumentation for Chapter I acceptance; **do not infer physics or crew progression from a screenshot**.

## Current limits and dependencies

- The source/CI tests demonstrate plan safety and offline file checks, not a native Unreal 5.8.4 screenshot. As last inspected, RDC was **offline**, the previous Windows host audit lacked a complete UE5.8.4 installation and MSVC/SDK, and the editor screenshot API has **not** been exercised.
- Four camera views currently render a **noncanonical blockout level** without finished cast, foliage, weather, coastal shaders, character rigs or approved PBR materials. No claim of cinematic-quality gameplay yet.
- Preserve all Five Lights canon, the Ionia-first Prelude, the **FlotationConfirmed** Chapter I boundary, correct crew order, independent waterline observer gates, and the hidden Moon Bridge progression.
- Native API and screenshot output behavior must be rechecked against the installed UE5.8.4 Python plugin. Fail closed on API drift, incomplete image files, interrupted captures, or new story/actor authority conflicts.
