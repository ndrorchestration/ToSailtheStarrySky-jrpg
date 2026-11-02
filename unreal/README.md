# Unreal Engine 5.8 migration — experimental source track

> **Current implementation routing (2026-11-01):** The creator has made Unreal Engine 5.8.4 the **primary target for new development**, while Godot/JS playables remain preserved as historical or reference baselines. This is a draft-branch work policy, not evidence of production gameplay or a migration merge. See [Unreal-first dependency authority](../docs/UNREAL_DEPENDENCY_AND_DOCUMENTATION_AUTHORITY_2026-11-01.md). The approved ship form labels are **Skybourne, Seabourne, Submersible, Starbourne**, with historical C++ enum IDs retained and Starbourne progression locked.

> **Later independent native asset-only results (2026-11-01):** Isolated V2 and V3 ship *review* StaticMeshes were imported natively into Unreal 5.8.4, placed in separate UE review maps, and captured in actual four-view D3D11 automation images on the connected Windows device. See [four-wing composite QA](Docs/AUREATE_SKYBORNE_V2_NATIVE_COMPOSITE_QA.md) and [V3 UV shading QA](Docs/AUREATE_V3_TANGENT_UV_REPAIR.md). These newer results supersede only the historical statement that **no UE screenshots exist**; they do **not** prove successful exact-head Unreal game Editor C++/UHT build, actor transforms, First Wake playability, approved cinematic art, or release. The Starbourne native-name automation has a separate resource-safe [acceptance gate](Docs/STARBOURNE_NATIVE_REFLECTION_ACCEPTANCE.md) and remains unverified.

This is the **native UE 5.8.4 C++ migration/review track** with First Wake state and contact gates, an Aureate Wake four-wing C++ review actor, generated 3D wing/root-support model candidates, source QA and a guarded scene-art binding workflow. On November 1, 2026, its **Win64 Development Game target compiled successfully** on the connected Windows host after real UE 5.8 API corrections. **Editor compilation remains blocked by the missing .NET Framework SDK**, and in-editor level physics, playable packaging and cinematic visual acceptance remain unverified. See the [exact native build receipt](Docs/UE58_NATIVE_BUILD_RECEIPT_2026-11-01.md). The existing playable Godot build and historical browser materials remain preserved while the Unreal port is developed.

## Windows native setup and verified status (October 31, 2026)

1. Install **Unreal Engine 5.8.4** through Epic Games Launcher; wait until the editor executable, `Build.bat` and `Engine/Build/Build.version` exist. An `UE_5.8` folder alone is **not** proof of a completed install.
2. Install Microsoft's free Visual Studio C++ Build Tools with the exact `unreal/Tools/TSTSS-UE58.vsconfig` file, including the **.NET Framework 4.8 SDK** required by Unreal Editor's SwarmInterface. First run the non-installing `unreal/Tools/Prepare-UnrealBuildTools.ps1` to inspect its requirements. Any actual installation requires its **explicit** `-Install -AcceptPackageAgreements` switches and may require administrator approval. Do not start overlapping large installations without checking disk capacity.
3. From an isolated **clean** checkout run `& .\\unreal\\Tools\\Check-UnrealHost.ps1 -RequireReady`. Only after the actual 5.8.4+, MSVC x64 and Windows SDK checks pass, run `& .\\unreal\\Tools\\Verify-Unreal.ps1 -EngineRoot 'C:\\Program Files\\Epic Games\\UE_5.8'` to compile and test the native Editor target.
4. After a genuine UE build and native automation success, use the separate non-destructive wing/support GLB review importers and the guarded First Wake ship binder in **`/Game/TSTSS/Review/FirstWake_Benchmark_V1` only**. Native frames, actual splashdown/water physics, material quality and creator approval remain independent acceptance gates.

**November 1 native update:** The Windows host now has UE 5.8.4, MSVC x64 and Windows SDK, and the real Win64 Development **Game target built successfully** after V7 target and component-bounds fixes. **109/109 Python source tests and 7/7 PowerShell host-gate tests passed.** The Editor build is still blocked by the absent .NET Framework SDK 4.6+; native automation, map rendering, water physics and playable packaging have not passed. See [the November 1 receipt](Docs/UE58_NATIVE_BUILD_RECEIPT_2026-11-01.md). The [October 31 handoff](Docs/UE58_NATIVE_FIRST_BUILD_HANDOFF_2026-10-31.md) remains historical evidence.

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
