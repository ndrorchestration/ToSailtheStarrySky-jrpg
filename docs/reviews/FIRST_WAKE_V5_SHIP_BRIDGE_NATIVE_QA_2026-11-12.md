# First Wake V5 ship-route bridge — native build, targeted automation, and safe disk remediation

**Date / host:** November 12, 2026; Neontic, Unreal Engine 5.8.4 Windows Editor (Win64 Development).
**Authority:** NATIVE BUILD + **2 TARGETED NATIVE AUTOMATION TESTS PASS** at exact C++/map source commit `505de74c3b958ff8d3ffc084a221418182925b2f`. **NOT ACTUAL V5→SHIP→SKY PLAYTRAVERSAL, NOT COMPLETE AUTOMATION INVENTORY, NOT FULL VERTICAL SLICE, NOT CREATOR VISUAL APPROVAL, NOT MERGED.**
**Review branch:** `review/ue58-v5-ship-route-bridge-20261112` (draft [PR #816](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/816), based on `review/ue58-opening-and-dock-rescue-20261111`).

## Native engineering evidence

- **Build:** `Build.bat ToSailTheStarrySkyEditor Win64 Development -Project=C:\TSTSS_V5RouteBridge_20261112\unreal\ToSailTheStarrySky.uproject -WaitMutex -NoHotReload -NoXGE -MaxParallelActions=1`. UHT accepted, six actions built (PCH, module compile, static import lib, resource, DLL, target metadata). UnrealBuildTool reported **Result: Succeeded** and **exit code 0**. The exact code head was checked clean immediately before invocation.
- **Native automation command:** `UnrealEditor-Cmd.exe <project> "-ExecCmds=Automation RunTests TSTSS.FirstWake.Review" "-TestExit=Automation Test Queue Empty" -unattended -nop4 -nosplash -nullrhi -NoSound -NoCompile -log`. Runtime returned **exit code 0** and reported **2 tests performed**. The native log specifically recorded **Result={Success}** for:
  - `TSTSS.FirstWake.ReviewDockReturnBoundaries`
  - `TSTSS.FirstWake.ReviewObjectivesAreReadOnly`
- **Local retained evidence receipts:** `unreal/Saved/ResourceCleanup/v5ship_native_build_505de74.exit` and `.log`; `unreal/Saved/ResourceCleanup/v5ship_native_automation_505de74.exit` and `.log`; `unreal/Saved/Logs/ToSailTheStarrySky.log`. These are workstation receipts, not published native test artifacts. The original verified V5 parent remains at `d4d860b4a6565a4791aab557758b895b3540ffd2` and was not modified.
- **Selected source regression suite:** 106/106 Python source and contract tests passed earlier on the exact code revision; these are independent from the native automation tests.

## Disk-space remediation and scope

Host C: was **11.454 GiB free**, below the established **14 GiB pre-native build** admission gate. The cleanup removed **only** `unreal/Intermediate/Build` directories (generated UHT/UBT/compile caches) from four clean, inactive review worktrees after checking exact branch/revision, Git status, untracked/ignored nature, no reparse points, and no running referencing tool/build processes:

1. `C:\TSTSS_AudioReview_20261111`
2. `C:\Users\Admin\work\TSTSS-Slice-Enemies-20261110`
3. `C:\TSTSS_CameraReviewFix_20261111`
4. `C:\Users\Admin\work\TSTSS-LyraStage-Reconcile-20261110`

**No source, Content assets, Saved receipts/screenshots, project configuration, Git refs, or existing Binaries were deleted.** Running Node processes referenced the npm `_npx` cache, which was intentionally **not touched**. Those four folders can regenerate their own build intermediates when revisited (extra future compile time is the tradeoff).

Native Editor compilation subsequently consumed approximately 2.57 GiB in the **new child** build worktree. After additional scoped cleanup and native automation, the latest measured free space was **15.611 GiB C:** and **7.77 GiB free RAM**. These values are a momentary measurement, not a promise that future heavy builds will always be admitted. Cleanup logs are preserved locally at:
- `unreal/Saved/ResourceCleanup/20261112_reclaim_generated_build_only.json`
- `unreal/Saved/ResourceCleanup/20261112_after_native_build_topup.json`
- `unreal/Saved/ResourceCleanup/20261112_lyra_stage_build_cache_topup.json`

## Remaining evidence gates

- **LIVE REVIEW ROUTE STILL OPEN:** V5 title and first E interaction were verified on parent code, **not** on this ship-bridge code revision. Need full seven-step E progression, V5 K→VS02, proper story-state restoration at VS02, actual VS02 footing/camera/interactions and VS02 K→sky.
- **Full native inventory still OPEN:** the two review automation identities are not the complete larger native test suite; hostile destination, save/replay, water, Lyra and menu tests still require integrated evidence.
- **Sea-contact and stable-flotation native physics still required:** transition to the water map cannot itself satisfy contact; reserve inspection and later Lyra recruitment must be witnessed.
- **Cinematic/art/audio gates unchanged:** no render approval, character art approval, music playback or packaged Windows game is claimed.
- **Authority:** no production merge, Starbourne unlock, Reson/Aepex early party access, or new engine-module/plugin declaration.

**Disposition:** Disk blocker corrected, native code compiled and targeted automated guard checks passed. Continue with real K/E gameplay and environmental collision review before any proposal to promote PR #816.
