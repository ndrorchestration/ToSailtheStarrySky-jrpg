# Aetherwake Windows desktop build — RETIRED / SECURITY HOLD

> **DO NOT BUILD, DOWNLOAD, INSTALL, EXECUTE, RESTORE, WHITELIST OR
> REDISTRIBUTE THE HISTORICAL NW.js/NSIS INSTALLER OR UNINSTALLER.**
> This guide documents a **historical** Aetherwake desktop path, not an
> active player download, build, packaging, or release procedure.
> [Security issue #293](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/293)
> records a real Windows Defender detection against a QA NSIS uninstaller;
> the security classification remains unresolved. No installer is cleared.
> The project's active forward development target is **Unreal Engine 5.8**;
> the original NW.js/JS material is preserved only as historical context.
>
> The GitHub legacy desktop publisher is intentionally disabled, and the
> local `scripts/build-windows-release.ps1` refuses before invoking any
> build or installer. **Important limitation:** the historical direct
> `npm run package:windows` script still exists in `package.json`;
> this direct CLI is **not protected by those two wrapper guards** and
> MUST NOT be executed. The source-only retirement checks do not certify
> complete repository-wide containment. Remediation requires a separate
> explicitly reviewed, fail-closed CLI gate and historical dependency
> compatibility/security review.
>
> Everything below this warning is **archival 2026-09/10 evidence and
> procedure, superseded by the October 19–28 security hold**. Past
> PASS statuses and artifact names are **not current release authorization**.
> No commands, links or installer steps below should be followed.


Aetherwake retains its HTTP-served browser path for development and automated smoke testing. The supported player-facing path is a packaged NW.js desktop build.

## For players

The desktop window opens at **1440×960** by default. Maximizing the window enlarges the game further while preserving its 3:2 aspect ratio. **Alt+Enter** or **F11** toggles true NW.js fullscreen; **Escape** exits fullscreen. The internal 960×640 coordinate system stays unchanged so authored UI, combat positions, and input geometry remain stable.


1. Download **Aetherwake-Setup.exe** from a Windows desktop release.
2. Run the installer and choose the install location if needed.
3. Launch Aetherwake from the created desktop or Start Menu shortcut.

The standard installer installs the packaged runtime per-user under `%LOCALAPPDATA%\\Programs\\Aetherwake`, does not require administrator elevation, and does not require Python, PowerShell, a manually started HTTP server, or opening an HTML file.

**Fallback:** **Aetherwake-Windows.zip** is also published for manual extraction. Extract the ZIP completely, then run **Aetherwake.exe** from the extracted folder. Keep the extracted files together.

Do not use superseded self-extracting/SFX artifacts. If Windows Defender flags an artifact, do not whitelist or bypass it; preserve the exact detection name and SHA-256 for a false-positive report.

## Current verification state — 2026-10-06

The exact current Preview 0.1 candidate is PR #250 head `46f50c581d992bf581bb6b6d7961a9421b8b779d`.

Technical evidence on that exact source is green:

- hosted smoke run `37557721548`: **SUCCESS**;
- current-head seven-frame evidence captured locally on NeonPC with no browser errors;
- title-ready evidence now shows the actual title/menu;
- the earlier opaque cyan/teal scanline failure is not reproduced;
- local packaged `Aetherwake.exe` reached runtime-ready + first-frame on NeonPC;
- Windows workflow-dispatch run `37559269564`: **SUCCESS**;
- no-admin installer build: **PASS**;
- exact installed-candidate launch: **PASS** with `DESKTOP_RENDER_READINESS=PASS`;
- portable ZIP verification: **PASS**;
- SHA-256 manifest generation: **PASS**;
- prerelease publication: **PASS**;
- published installer re-download, hash verification, isolated install, and installed launch on NeonPC: **PASS**.

Published candidate hashes:

```text
7feb6de364264617095a59dd9329a99ebfa77a144b0f5887a7ae7ff064f6221d  Aetherwake-Setup.exe
4c6efc6ea1cecf6468fb983fd8ff5fd5d0ce8645262779551841f663c5326173  Aetherwake-Windows.zip
```

The remaining release gate is **human/player acceptance**, not Windows packaging. Technical PASS does not establish visual approval or player acceptance. The exact protocol and acceptance boundary are documented in `docs/PREVIEW_0_1_ACCEPTANCE.md`.

The GitHub Actions artifact-quota issue remains open as infrastructure debt, but it is no longer blocking current Preview 0.1 human review because exact-head review evidence is available through the RDC/local handoff.

## For maintainers

The production desktop layout intentionally follows the same structural pattern used by RPG Maker MV/NW.js games such as the Memories reference: the NW.js launcher/runtime lives at the package root, a minimal root `package.json` points to `www/index-embedded.html`, and the game payload lives under `www/`. Development files, tests, docs, and npm tooling are not part of the player runtime.

The release-critical path is intentionally a **single pinned Windows job**. This avoids a previously demonstrated GitHub Actions artifact-storage/quota failure mode and ensures the bytes that are published are the same bytes that were built and tested.

The job performs, in order:

1. lockfile install and desktop packaging contract;
2. staged Memories-style NW.js Windows build;
3. portable ZIP creation;
4. NSIS installer compilation;
5. clean per-user installer execution;
6. launch the installed `Aetherwake.exe` and require an application-level readiness marker proving `setup()` completed and a 960×640 first frame rendered;
7. portable ZIP layout verification;
8. SHA-256 generation;
9. release publication only for manual/tagged release runs.

No `upload-artifact` / `download-artifact` transfer is on the release-critical path. The maintainer-local Windows script remains the independent fallback when hosted runners are unavailable.

Local build requirements:

- Node.js 22+
- npm
- NSIS for installer compilation
- Windows for final install/launch verification

Local commands:

~~~powershell
.\scripts\build-windows-release.ps1
~~~

The local release script runs the desktop contract, builds the Windows runtime, compiles the NSIS installer, installs it into a clean temporary directory, launches the installed game, requires a runtime-ready + completed-first-frame marker with the expected 960×640 canvas, and writes SHA-256 hashes. It is the maintainer fallback when hosted CI cannot allocate runners.

## Launch contract

The desktop shell must:

- launch `www/index-embedded.html` from a minimal launcher-root `package.json`;
- keep the launcher/runtime separate from the `www/` game payload;
- exclude development-only files from the player runtime;
- preserve the 960×640 logical render surface while presenting it at 1440×960 by default and scaling it responsively to the largest 3:2 area available when resized/maximized/fullscreen;
- expose native NW.js fullscreen through Alt+Enter and F11, with Escape returning to windowed mode;
- run without Python or a separately started HTTP server;
- keep the browser-served path available as a fallback;
- build Aetherwake-Setup.exe plus Aetherwake-Windows.zip in the same Windows job that verifies them;
- avoid GitHub Actions artifact storage/transfer on the release-critical path;
- publish only after the exact candidate passes a real Windows install plus application-level runtime-ready/first-frame smoke;
- install per-user without requiring administrator elevation or the pre-install startup confirmation;
- publish Aetherwake-Windows.zip as the manual fallback;
- fail visibly if packaging or the entry point is invalid.

The packaged build does not change gameplay semantics. The internal game coordinate system remains 960×640, while the player-facing desktop window defaults to 1440×960 and the canvas scales proportionally with the window.
