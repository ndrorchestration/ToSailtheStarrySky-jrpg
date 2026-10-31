# Unreal Engine 5.8 migration — experimental source track

This is the **native UE 5.8.4 C++ migration/review track** with First Wake state and contact gates, an Aureate Wake four-wing C++ review actor, generated 3D wing/root-support model candidates, source QA and a guarded scene-art binding workflow. It has **not yet passed native UE compilation, in-editor level physics or cinematic visual acceptance**. The existing playable Godot build and historical browser materials remain preserved while the Unreal port is developed.

## Windows native setup and verified status (October 31, 2026)

1. Install **Unreal Engine 5.8.4** through Epic Games Launcher; wait until the editor executable, `Build.bat` and `Engine/Build/Build.version` exist. An `UE_5.8` folder alone is **not** proof of a completed install.
2. Install Microsoft's free Visual Studio C++ Build Tools with the exact `unreal/Tools/TSTSS-UE58.vsconfig` file. First run the non-installing `unreal/Tools/Prepare-UnrealBuildTools.ps1` to inspect its requirements. Any actual installation requires its **explicit** `-Install -AcceptPackageAgreements` switches and may require administrator approval. Do not start overlapping large installations without checking disk capacity.
3. From an isolated **clean** checkout run `& .\\unreal\\Tools\\Check-UnrealHost.ps1 -RequireReady`. Only after the actual 5.8.4+, MSVC x64 and Windows SDK checks pass, run `& .\\unreal\\Tools\\Verify-Unreal.ps1 -EngineRoot 'C:\\Program Files\\Epic Games\\UE_5.8'` to compile and test the native Editor target.
4. After a genuine UE build and native automation success, use the separate non-destructive wing/support GLB review importers and the guarded First Wake ship binder in **`/Game/TSTSS/Review/FirstWake_Benchmark_V1` only**. Native frames, actual splashdown/water physics, material quality and creator approval remain independent acceptance gates.

At the latest verified Windows review head on `neontic`, **97/97 Python source/asset tests passed**. The host check still reports no completed UE editor/build binaries, MSVC x64 or Windows SDK. [Draft integration PR #642](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/642) and [exact first-build evidence / handoff](Docs/UE58_NATIVE_FIRST_BUILD_HANDOFF_2026-10-31.md) record the boundaries. Local source test success is **not** an Unreal game build or playable scene.

The October 30 creator-approved character design reference remains authoritative; a static approved illustration is not an automatically rigged/importable 3D game character. Corrected wing and support GLBs are **review-only**, not production-approved art.

## First real Unreal screenshot review (queued, not rendered)

The new [four-camera native capture contract](Docs/FIRST_WAKE_UE58_NATIVE_SCREENSHOT_GATE_2026-10-31.md) uses the actual [First Wake benchmark scene](Tools/build_first_wake_benchmark.py) and [guarded art binder](Tools/bind_first_wake_review_ship_art.py). It defines Prelude harbor/ship/boarding shots and a **Chapter I Splashdown composition** without forging physical flotation or story milestones. The [capture/PNG receipt tool](Tools/capture_first_wake_review.py) schedules UE5.8 Editor high-resolution screenshots only in that isolated review map and can separately verify four physically present 1920×1080 PNG outputs by byte hash and PNG CRC/size. It refuses unlocked Orbiter, unbound art, mismatched component inventories, or swapped production/non-review meshes.

```powershell
python unreal/Tools/capture_first_wake_review.py --inspect --run-id Review20261031
python -m unittest discover -s unreal/Tests -p "test_first_wake_capture_receipts.py" -v
```

These commands **do not generate screenshots**. At the newest GitHub integrated source check, **107 offline tests** passed, including the capture contract. Unreal Editor screenshots, native C++ compilation, final sky/ocean shaders, real 3D character rigs, sea physics, cinematic approval and installer remain unverified. The source-only screenshot workflow does not authorize publication of unreleased candidate artwork.

## Migration constraints

- **Art lock:** User explicitly approved the latest full-cast artwork on October 30, 2026. Treat its designs as the authoritative visual target; do not substitute pixel/legacy sprites. Source image files, individual face references and asset licensing/provenance must be attached or linked before producing game-ready meshes.
- **Story lock:** First Wake starts with Ender finding Ionia's flyer, hiring her, boarding the Aureate Wake, doing engineering checks, launching, sea landing/flotation and inspecting empty reserves. Lyra and Talen's reunion/salvage requires authored acceptance; do not invent it as complete.
- **Party lock:** Ender → Ionia → Lyra → Reson → Aepex. Three active combat members planned. Party resonance is story energy, not automatic combat magic.
- **Five Lights:** Ender/Spirit, Ionia/Earth, Lyra/Water, Reson/Fire, Aepex/Air are narrative affinities, not mandatory magic classes.
- **Game systems:** Preserve deterministic, transactional combat semantics and data-driven stats, costs and skills. Define UE native serialization IDs and versioned save migrations before replacing Godot saves.
- **Ship/world:** Aureate Wake supports flight, sea, submersible and hidden Moon Bridge modes, staged behind separate feature gates. Planet and moon traversal remain future milestones.
- **Quality:** Prioritize creator-approved cinematic art with documented budget and performance targets. A technical compile or frame capture is not art approval.

## Next thin vertical slice

A single noncanonical test map with a third-person Ender pawn, Ionia interaction, boarding trigger and a sea-contact event; use isolated authored assets and capture Windows packaged-build evidence. Only then port the full First Wake beats and combat UI. Do not merge based on this README/scaffold alone.
