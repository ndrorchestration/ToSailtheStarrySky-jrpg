# Aureate Wake — canonical configuration names (creator revision, 2026-11-01)

**Official player-facing labels, in order:** **Skybourne**, **Seabourne**, **Submersible**, **Starbourne**.

**Starbourne** is the newly approved name for the previous **Orbiter / Orbital form**. The first two forms are also officially spelled **Skybourne** and **Seabourne**, with the letter *u*. Submersible is unchanged.

## Implementation compatibility contract

| Canonical display label | Stable Unreal `EAureateWakeForm` identifier | Gameplay environment |
| --- | --- | --- |
| Skybourne | `Skyborne` | Atmospheric flight, levitation and docking |
| Seabourne | `Seaborne` | Marine hydrofoil and surface travel |
| Submersible | `Submersible` | Underwater exploration |
| Starbourne | `Orbiter` | Celestial/lunar travel and four solar/light sails |

The internal C++ identifiers and their ordinal order must **not** be renamed or reordered as part of this cosmetic/narrative naming revision. They appear in C++ branches, legacy Blueprints and serialization, native tests, GLB review provenance and historical engineering receipts. Unreal's `UENUM` entries now carry `UMETA(DisplayName="...")`, exposing the new names in reflected editor/Blueprint UI while retaining internal source compatibility. Future UI, dialogue, captions, tooltips, design docs and localization strings should use only the canonical display names. Explicit migration aliases in `unreal/ArtSource/ShipReview/aureate_wake_canonical_form_names_v2.json` cover older terminology.

**Starbourne remains story-locked** behind the established Moon Bridge / auroral access and clearance gates. Four equal-size radial sail panels remain arranged top, bottom, port, and starboard; the bridge stays forward-facing and the original four dragonfly wings remain the underlying identity. A name change does not approve the current 3D art, enable a new transition, clear the previously detected wing-hull collision, alter physics, or unlock the form.

The original approved illustration — `Aureate Wake_ Four Configurations.png`, SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13` — remains **exactly unchanged**. Historical files, test baselines and engine names may show *Skyborne*, *Seaborne* and *Orbiter* because they document artifacts from before the rename. Those older labels are **not current canon for presentation**. The visual design and previous review evidence remain authoritative in their own scopes.

## Verification

Run `python -m unittest discover -s unreal/Tests -p test_aureate_form_naming_v2.py -v`. The suite verifies the four names, original enum order and `UENUM` display metadata, legacy aliases, original approved-image hash, unchanged First Wake access, persistent four wings and cardinal sails, and the fail-closed Starbourne gate. Native Unreal Header Tool compilation and graphical UI presentation are independent checks; this source-only test cannot establish either.

Changes are a review-only draft PR; no main merge, story unlock, art promotion, game release or installation is authorized by the renaming.


## Native Unreal 5.8.4 verification (not yet passed)

A native reflection automation test is now registered as `TSTSS.AureateWake.Canon.FormDisplayNames` in `Source/ToSailTheStarrySky/Private/Tests/AureateWakeCanonicalFormNamesTests.cpp`. It checks the four actual reflected `UEnum` labels alongside the unchanged ordinal and internal enum strings, and the default-disabled Starbourne debug preview. This is **not executed or validated merely by passing Python CI**.

On November 1, a no-install native `ToSailTheStarrySkyEditor Win64 Development` build was attempted in detached worktree `C:\TSTSS_Unreal_FormNamingQA_20261101` at exact head `6b19e3661aaa0cee928683bb142ac6cdf02608d6` while another ship-rendering Unreal Editor and Live Coding were active. UnrealBuildTool progressed through makefile setup and target rules, but did not generate UHT/reflection or compilation output; free RAM dropped below 1 GB. To protect the independent render, only the uniquely identified **naming-build UBT** process was stopped. The active Editor/Live Coding were left running. **Native naming UHT, compile and automation: NOT VERIFIED** for that attempt. This test was subsequently added to the branch, so a new exact-head native test is necessary.

Next when the workstation has sufficient free RAM and no competing Unreal Editor/Live Coding: verify a clean detached head; execute `Build.bat ToSailTheStarrySkyEditor Win64 Development -Project=<isolated-branch>/unreal/ToSailTheStarrySky.uproject -WaitMutex -NoLiveCoding -NoHotReloadFromIDE -nowrite`; run `UnrealEditor-Cmd.exe <isolated-project>.uproject -unattended -nullrhi -nop4 -ExecCmds="Automation RunTests TSTSS.AureateWake.Canon.FormDisplayNames; Quit" -testexit="Automation Test Queue Empty"`; inspect exact-head native logs, automation result and clean worktree. Never stop unrelated Editor processes or interpret a partial tool startup as pass.
