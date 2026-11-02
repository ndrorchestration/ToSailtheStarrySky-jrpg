# Starbourne naming: safe native Unreal verification procedure

**Authority:** Creator-approved four player-facing Aureate Wake names: **Skybourne, Seabourne, Submersible, Starbourne**. Do not rename the stable serialized C++ enum values \`Skyborne/Seaborne/Submersible/Orbiter\` or the existing native art assets. Starbourne and the Moon Bridge remain story-locked.

## Exact-head verification

A bounded native command has been added at \`unreal/Tools/Verify-StarbourneNames.ps1\`. It is **not a background scheduled job**. From a **clean, isolated Git checkout** pinned to the branch SHA and with UE 5.8.4 already installed:

\`\`\`powershell
pwsh -NoProfile -File .\unreal\Tools\Verify-StarbourneNames.ps1 -PreflightOnly
# When and only when the separate Unreal rendering jobs have finished,
# the machine has >=6 GiB free physical RAM, and preflight exits 0:
pwsh -NoProfile -File .\unreal\Tools\Verify-StarbourneNames.ps1
\`\`\`

The script fails closed **before Unreal launches** when an Unreal Editor/commandlet, Live Coding console, or UnrealBuildTool is detected, or when the measured free RAM is under 6 GiB. It also refuses dirty source worktrees, unavailable engine/native prerequisites, and existing evidence output folders. It does not install software, kill processes, merge, deploy, or modify the game scene.

If ready, it invokes UE 5.8.4's native Editor C++ build with disabled Live Coding/hot reload, then an isolated null-renderer automation of \`TSTSS.AureateWake.Canon.FormDisplayNames\`. It accepts only a successful build, successful commandlet exit, **exact matching reported test in Unreal's JSON report** with state Success, and clean unchanged source SHA. Native evidence lives under \`unreal/Saved/StarbourneNative/<exact SHA>/\`, which must not be overwritten or counted as PASS without \`verified.json\`.

The native test checks **actual reflected \`UEnum\` UI names** and preserved numeric C++ values and verifies the default Starbourne debug-preview lock. The original fifteen required project-native automation declarations remain mandatory in the full \`Verify-Unreal.ps1\` suite; the Starbourne script targets this single specific test to minimize resource load.

## Verified vs unverified

As of November 1, 2026, an earlier separate native compilation attempt stopped after UnrealBuildTool makefile/rules because another D3D12 ship-rendering Editor plus Live Coding was active and memory fell below 1 GB. The native reflection test remains **NOT VERIFIED**. Source and hosted CI checks, including exact naming order, legacy IDs, fail-closed Starbourne lock, full native test inventory and four-form source contracts, have passed. A passing preflight is **not** a native compile or verified displayed-name result.

No gameplay, wing, hull or transform mode is authorized by this cosmetic name change.
