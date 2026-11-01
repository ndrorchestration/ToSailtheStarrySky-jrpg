# UE 5.8.4 native Windows build receipt — 2026-11-01

**Scope:** Isolated, unmerged Unreal review branch `fix/unreal-ue58-v7-native-build-20261101`, created from draft PR #644 head `e06f393edb0b13319c6c19dc085a1217aa3da2e8`. This is not a `main` integration, a player build, a rendered level, or creator visual approval.

## Verified host and actual native build

- Connected Windows device: `neontic`; engine manifest reports Unreal **5.8.4** (`++UE5+Release-5.8`, changelist `58902052`), and both editor binaries and `Build.bat` exist.
- Actual toolchain: Visual Studio 2022 Build Tools MSVC **14.44.35229** (installed folder `14.44.35207`) and Windows SDK **10.0.26100.0**.
- The first genuine Editor build failed with a shared-build-environment mismatch from `BuildSettingsVersion.V5`. Both project targets now use **V7** and the explicit Unreal 5.8 include order.
- A genuine Win64 Development **Game target** compile then revealed three calls to unavailable `USceneComponent::GetComponentBounds`. Both physical water observers now use `USceneComponent::GetBounds()` with the same world-space origin and box extent measurements, without changing the story gate, overlap authority, or Orbiter policy.
- Rebuilding with `Build.bat ToSailTheStarrySky Win64 Development -Project=... -WaitMutex` returned **Result: Succeeded** and **exit code 0**, with the actual game binary at `unreal/Binaries/Win64/ToSailTheStarrySky.exe` (332,018,688 bytes). SHA-256: `e10f0dbd9981d26237ee89422a22444b66569a05884f524c0b4a299e342326d5`. This is a compiled Development binary, **not** proof of a cooked, launched, playable or packaged game.
- The Editor-target retry passed the V7 mismatch but stopped in Unreal's `SwarmInterface.Build.cs` because the **.NET Framework SDK 4.6+ / NetFxSDK** is missing. The modern bundled `dotnet` runtime is not a substitute. No Editor automation was run.

## Regression checks

- **109/109** Unreal-source Python unit tests passed after updating the two source guards for the real UE 5.8 `GetBounds()` API.
- The standalone Aureate Wake water-observer source guard passed all 11 checks.
- **7/7** Windows PowerShell engine-version and strict-hold regression cases passed.
- `git diff --check` returned exit code 0.
- The host prerequisite script now detects missing NetFxSDK and returns **`ready_for_native_build_attempt=false`** with strict exit code **2**, instead of incorrectly greenlighting an Editor build. The free Build Tools component manifest and opt-in planning script include `Microsoft.Net.Component.4.8.SDK`; plan-only mode returned 0. **No installation was initiated.**

## Remaining gates and next authorized actions

1. With the owner's approval for the operating-system installation and applicable license terms, install the **free .NET Framework 4.8 SDK** component through the existing Visual Studio Build Tools installation. Do not assume an install occurred merely because the manifest lists it.
2. Re-run `Check-UnrealHost.ps1 -RequireReady`, then `Verify-Unreal.ps1` at a clean exact branch SHA; retain real Editor build logs and named automation JSON reports.
3. Only after native Editor automation succeeds, generate an isolated First Wake review map and capture actual Unreal frames; test sea-contact/flotation, scene wiring and performance separately.
4. Keep the Godot fallback, approved character art, Five Lights, story/ship safety gates, draft-PR review boundaries, and public-release restrictions intact.

**Evidence boundary:** Real Win64 Development Game compilation and source regression success are established. Native Editor compilation, runtime gameplay, cooked packaging, cinematic rendering, physics acceptance and creator visual signoff remain **NOT VERIFIED**.
