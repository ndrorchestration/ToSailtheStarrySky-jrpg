# First Wake — multi-path Unreal integration candidate (2026-11-10)

**State: source/asset integration candidate only. NOT native-accepted, playable, art-approved, merged into protected main, or releasable.** Source of truth for this candidate: `unreal/DataSource/Integration/FirstWakeMultipath.review.json`. Historic upstream PR commits there identify exactly what was imported, not current status of those evolving PRs.

## What has been integrated in the isolated review worktree

- #792 — water contact, pretransition flotation, E interactions, F6 save/F9 load, F7 preview/confirm prelaunch Continue.
- #790 — 10-shot cinematic requirements and story chronology.
- #796 — 11 independently authorable lighting looks and source tests.
- #794 — six UE 5.8.4 review maps and ten native material assets with prior map-readback evidence.
- #795 — 22 deterministic GLB environment/ship object prefabs (additive source snapshot, rather than importing unrelated historical #766 ancestry).
- #793 — 14 original three-character GLB equipment meshes, imported review assets, QA gallery and fail-closed equipment stage contract.
- #797 — nine proposed Ender Resonator spell rows, native C++ review VFX actor, source-gated cue selection and isolated authoring script.
- #798 — C++ sun/moon, weather, atmosphere, fog, cloud and precipitation review director and authoring script.
- #791 — three 3D enemy review silhouettes, guarded encounter/AI and six candidate abilities (additive source snapshot only, rather than importing unrelated main ancestry).

All import paths remain in the review namespace. Original PRs remain open/draft. The object and enemy snapshot file content was copied from the exact source commits shown in the machine manifest. Nothing in this branch automatically promotes ReviewSelectable/ReviewExecutable to CreatorApproved, adds mastery or abilities to Ender, recruits Lyra before splashdown, or opens Starbourne.

## Critical integration reconciliation

- Distinct native automation names from parallel paths were united into an exact **35-test** registry; previously hardcoded counts from individual 29–32-name tracks were reconciled in the PowerShell assertion/negative-fixture scripts, native-readiness guards, and source-admission tests. Do **not** relax these checks or accept stale 30-name reports.
- Both magic and equipment source-preflight path triggers are preserved. Source-only tests confirm duplicate names, missing proof, forged automation totals and unsafe native admission are rejected.
- Gameplay controls: PIE F6 quicksave, F9 session quickload, F7 twice only for prelaunch Continue; standalone F5 quicksave. Shift+F5 in PIE must never be used as a save shortcut. Water landing requires directly observed >=2.0 s pretransition flotation.
- The first two party members are Ender and Captain Ionia. Lyra joins only after splashdown. Reson and Aepex are excluded from this slice, not from broader game canon.
- The 6 native review maps, equipment gallery, spell VFX comparison scene and sky/lighting preview scripts are **separate review assets and authoring paths**. They have not been connected into a single gameplay map or shown to function together; do not call this a completed vertical slice.

## Ordered next native gates

1. Close other Editor/Live Coding sessions without interrupting their owners. Confirm clean exact commit, >=5.0 GiB physical RAM, >=14 GiB disk.
2. Native UE 5.8.4 Win64 UHT/C++ Editor build and all **35 distinct named Editor automations** on this exact commit. No existing native receipt transfers across merge commits.
3. Under >=6.5 GiB physical RAM with no competing GPU/Editor session, author a disposable review level and verify imported map/material/prop/equipment assets and spawned atmosphere, lighting, spell and enemy actors against the **combined** project binaries.
4. Record source and built asset hashes, map readback, real Lit D3D captures, visual fidelity, screenshot comparisons, performance, sound/animation and failure paths. A source script or generated static proxy is not a verified cinematic result.
5. Execute two real player-driven Prelude to splashdown PIE runs, with E, F6, F7, F9 and negative tests, water stability and chapter transition. Audit chronology and unlocked-skill guards, then seek creator visual approval.

**NEONTIC safety hold during source integration:** Unreal Editor + LiveCodingConsole were active. Native build/Editor/PIE was deliberately not started, and no existing game worktree/session/config/save was overwritten.

## Cross-path source gate

`python -m unittest discover -s unreal/Tools -p "test_*.py"`

`powershell -NoProfile -ExecutionPolicy Bypass -File unreal/Tools/Test-NativeAutomationReportFixtures.ps1`

The `test_first_wake_multipath_review.py` guard additionally verifies all nine lane sources, registered native-test inventory, 6 maps, 22 GLBs, 14 equipment GLBs, player order, input isolation and strictly unapproved evidence states, with negative mutation tests.
