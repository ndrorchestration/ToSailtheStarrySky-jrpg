# TSTSS — native UE 5.8.4 cast renderer diagnostic, 2026-11-01

**Disposition: RENDERER / SCREENSHOT PIPELINE PROVEN; VISUAL QUALITY FAIL; ART ADMISSION HOLD.**
This is a strictly isolated, **noncanonical static lookdev review** stacked on [PR #646](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/646), which itself stacks on #643. The preserved source models are NOT production sculpt, rigged characters, or approved visual likeness. Nothing here authorizes Godot/main merges, character replacement, releases, or canon changes.

## Exact native evidence

- Authorized Windows **neontic**, Unreal Engine **5.8.4-58902052+++UE5+Release-5.8**, Intel Iris Xe integrated GPU; **D3D11 SM5** renderer.
- Original saved standalone map: `C:\TSTSS_CastAllSandbox_20261101\Content\ArtLookdev\ReviewMaps\TSTSS_CastLineup_Review.umap`. SHA-256 after four renderer trials remains **`6614a8a8c378f8eada5a8ff2788afae9ca49832e507b27ed942a8076a478b49a`**. All camera, lighting, and experimental 180° actor roll operations were **transient and unsaved**.
- Native Python Automation Test plugin was necessary. An initial `-ExecutePythonScript` invocation failed with `AttributeError: module 'unreal' has no attribute 'AutomationScheduler'` because the scheduler belongs to the opt-in `PythonAutomationTest` plugin. Another naive `-ExecutePythonScript` invocation queued tasks but exited before execution. Both are historical failures, not passes.
- With the plugin enabled **only in the disposable test `.uproject`**, an `Editor.Python.CastAllSandbox.test_cast_render_review_v4` automation run completed **Success**; five `TSTSS_RENDER_TASK_DONE` messages and `TSTSS_RENDER_TASKS_RECORDED` were observed in the real engine log; **five PNGs** saved by Unreal's automation report pipeline under `Saved/Automation/Reports/test_cast_render_review_v4`.
- Unreal captured actual images at **1280×720**. Passing the image filename to `AutomationLibrary.take_high_res_screenshot` does **not** place the PNG at that filename; the automation report uses nested `.../<requested-name>/Windows/D3D11_SM5/Incoming.png`. The companion validator reads the *real files*, checks PNG structure, IDAT inflation, CRC, actual dimensions, and SHA-256. The requested output path in task receipts is not image proof.
- Tested the companion engine-free source validator: **8 / 8 PASS**, including a negative test rejecting exact duplicate camera images and tests for corrupt CRCs, wrong dimensions, truncated images, implausibly blank data, and report-path resolution.
- **Image-quality defect confirmed:** v4 native Ender `Ender_profile` and `Ender_three_quarter` files are exact duplicate 17,709-byte images (visually black), so the independent full-five screenshot gate **FAILS** with `Different camera views produced duplicate image bytes`. Other screenshots are dim and blockout quality; earlier v1 shots were blown out, v2 underexposed, and v3/v4 expose an apparent imported orientation/camera mismatch. An automation `Success` is not photographic or artistic acceptance.
- The first v4 snapshot, failed profile snapshot, and lineup snapshot are committed **only as diagnostic evidence**, deliberately prefixed `REVIEW_FAILED_`:
  - [Ender front (failed art QA)](ReviewCaptures/2026-11-01/REVIEW_FAILED_Ender_front.png)
  - [Ender profile (blank, failed)](ReviewCaptures/2026-11-01/REVIEW_FAILED_Ender_profile.png)
  - [Five-cast lineup (failed art QA)](ReviewCaptures/2026-11-01/REVIEW_FAILED_Five_cast_lineup.png)
  These screenshots are **not** the private October 30 approved group illustration and do not replace its authority.

## Reproduction boundaries

1. Prepare a **separate disposable UE 5.8.4 project**, not the TSTSS First Wake playable project; enable the built-in **Python Script Plugin** and the editor **Python Automation Test** plugin in that disposable project only.
2. Run the guarded `editor_intake.py` for **all five** static GLBs, `stage_cast_lineup.py`, and then `verify_cast_lineup_reload.py` in a new native Editor. Require their existing receipts in `Saved/CharacterLookdev` before proceeding. Never overwrite an existing map or capture output folder.
3. Copy a Python test wrapper into disposable `Content/Python/test_cast_render_review.py` containing `import runpy; runpy.run_path(r"<absolute checked-out path>/unreal/ArtSource/Characters/capture_cast_render_review.py")`. This keeps the capture implementation versioned without adding it to any production game.
4. Invoke `UnrealEditor-Cmd.exe <disposable .uproject> -d3d11 -RenderOffscreen -unattended -nop4 -NoSound "-ExecCmds=Automation RunTests Editor.Python.<project-name>.test_cast_render_review; Quit" "-testexit=Automation Test Queue Empty"`. Read the actual automation JSON/test log, **not** just the process exit status. For the original native run, `<project-name>=CastAllSandbox`; this name is intentionally guarded in the script.
5. Validate actual PNGs: `python unreal/ArtSource/Characters/verify_render_pngs.py <disposable Saved/Automation/Reports/test_cast_render_review>`. This gate currently **FAILS** on the known native run. Retain that failure as a negative benchmark.
6. Only after all five unique, adequately lit, nonblank views pass should an expert compare to approved close-up/profile references. Ender's copper/auburn-versus-green hair conflict is unresolved; don't silently choose either source. Preserve Ionia's long curly blonde hair and cast height ranking **Reson > Aepex > Ender > Ionia > Lyra**; the numeric heights are NOT canon.

## Smallest reversible next correction

Determine whether the imported upside-down / side-on appearance comes from glTF Y-up-to-Unreal Z-up conversion, actor roll, camera forward vector, or framing. Use one **isolated Ender** screenshot first; record imported mesh orientation + camera pose, actor world transform, and exposure metrics. Only promote a fixed transform into the review pipeline after a repeatable native front/profile/back comparison, then validate five distinct images without overexposure. Subsequently progress to actual modeled hair, face, clothing, goggles, staff hand-contact, skeletal rig, motion, and creator visual approval. The GLBs, story progression, gameplay pawn and protected main remain unchanged.
