# Unreal-first documentation and dependency authority — 2026-11-01

**Status:** Review-only coordination update, not a playable-build, art, native C++ compile, release or dependency-upgrade receipt.

## Current implementation policy

The creator's latest direction supersedes older October Godot-first *work assignment* text: **prioritize Unreal Engine 5.8.4 / C++ and native Unreal art, world, gameplay and First Wake implementation**. Preserve Godot 4.7.2/GDScript gameplay, historical native QA and plot contracts as a **separate reference and regression oracle**; it is not automatically the target of new Unreal feature tasks. The legacy JavaScript/p5.js/NW.js prototype remains preserved, with no unsolicited extension or release. The creator-approved narrative, Five Lights, crew art, ship image, and progression gates outrank engine implementation proposals.

This policy does **not** imply that an unmerged UE branch has replaced GitHub `main`. Before edits, identify the exact base SHA and the relevant PR. Do not merge unrelated draft work or copy candidate art into production based on this file.

Canonical Aureate Wake display forms: **Skybourne, Seabourne, Submersible, Starbourne**. Retain the legacy serialized C++ identifiers `Skyborne/Seaborne/Submersible/Orbiter` and gate Starbourne behind the original story and clearance restrictions. Reference: `unreal/Docs/AUREATE_WAKE_CANONICAL_CONFIGURATION_NAMES_2026-11-01.md` (draft PR #699, not merged at this writing).

## Verified manifest/dependency inventory on PR #699 branch

| Area | Observed repository declaration | Safe action now | Admission gate |
| --- | --- | --- | --- |
| Unreal engine | `unreal/ToSailTheStarrySky.uproject` has `EngineAssociation: "5.8"`; external installed engine 5.8.4 is the native verification target | Document the actual local `Engine/Build/Build.version` patch; keep association compatible; no UE install/update | C++ UHT + Editor compile on clean pinned SHA, then named automation + representative render |
| Unreal runtime module | `unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs` declares **Core, CoreUObject, Engine, InputCore** | Keep these four built-in module dependencies until source implementation shows a real need for more | Native build/UHT proof for every changed module |
| Third-party Unreal plugins | No plugin enabled or declared in the tracked `.uproject` | **Do not add** marketplace plugins, water plugins, Niagara modules, Nanite helpers, or marketplace art by assumption | Need concrete feature, version/rights check, clean import/compile, rollback strategy and explicit review |
| Windows toolchain | `unreal/Tools/TSTSS-UE58.vsconfig` lists MSVC C++ workload, Win11 SDK 26100 and .NET Framework 4.8 SDK | Inventory installed tools using non-installing `Check-UnrealHost.ps1`; avoid duplicate installs | Exact host readiness report plus real Editor build; toolchain presence alone is not proof |
| Native Starbourne labels | `unreal/Tools/Verify-StarbourneNames.ps1` preflight and `TSTSS.AureateWake.Canon.FormDisplayNames` native test | Run lightweight source and process/RAM checks; preserve other Editor sessions | No competing UE/Live Coding processes and at least 6 GiB available; successful UHT, C++ build, UE automation report |
| Existing root npm track | `package.json` is still named **Aetherwake** and declares `nw`, `nwjs`, `nw-builder`, `playwright`; `package-lock.json` tracks this legacy desktop/test runtime | Leave existing package names, versions, scripts and lockfile unchanged; document ownership | Separate legacy security/build audit plus npm tests and installer/signed-or-unsigned custody evidence before updates |
| Godot reference | Native Godot 4.7.2/GDScript story and regression work remains historical evidence in separate branches | Preserve snapshots and references, do not delete or auto-replace | Cross-engine save/plot/party equivalence tests before migration of authority |
| Python review tools | `unreal/Tools`, `unreal/Tests` and `unreal/ArtSource` use multiple independent local source and geometry checks | Prefer Python standard library for new lightweight QA; pin extra Python libraries only if genuinely needed | CI and Windows source tests, asset hashes and separate native import/render evidence |

**Notable trap:** Some Unreal readmes and preflight documents contain *historically correct, date-bound* statements that no native screenshot ever existed or that a particular host lacked the .NET Framework SDK. The separate, later **native V2/V3 review StaticMesh imports and real D3D11 frames** do exist as evidence within the isolated review workspaces; those do **not** establish a successful exact-head C++ ship game Editor build, physics, First Wake completion, packaging or art approval. Do not retroactively rewrite older dated receipts; point readers to the newest exact-head result and its boundaries.

## Recommended documentation maintenance, in order

1. **Agent routing/engine authority:** keep `AGENTS.md`, `README.md` and `docs/AGENT_HANDOFF_INDEX.md` consistent with Unreal-first *new* development. Retain links to Godot/legacy documentation as historical or cross-engine evidence.
2. **One status ledger:** in `unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md` or a separate dated addendum, record per-feature **SOURCE / NATIVE UHT / NATIVE IMPORT / RENDER / GAMEPLAY / ART APPROVAL / RELEASE** independently, with PR, SHA and source of evidence. Never infer one from another.
3. **Four-form naming:** propagate Skybourne, Seabourne, Submersible, Starbourne in *new* player-facing labels, cast/ship handoff and visual bible; preserve old enum IDs, historical image text and provenance receipts.
4. **Asset provenance:** for each new hull, wing, cockpit, weather shader, character and spell, record source, rights, deterministic build inputs, GLB/texture hashes, native asset path, preview images and creator review status.
5. **First Wake → Splashdown integration:** keep a checklist linking ordered narrative milestones, actual scene wiring, party/save roundtrips, ship-water physics and accessible captions to native test receipts.
6. **Performance/test budgets:** record target Windows hardware, RHI, image resolution, frame-time/GPU/memory budgets and actual Unreal Insights or benchmark evidence before marking an optimization accepted.
7. **Architecture/compatibility:** explicitly catalog which engine owns saves, enemy tables, character appearance, cinematic art and chapter progression. Do not treat an older engine's code path as an automatically available UE function.

## Dependency-change rule

**Docs, metadata, test registration and a bounded review importer** can change now. Changing actual engine version, npm lockfile, C# module dependencies, Unreal plugins, glTF importer versions, shader backends or native SDK installations must be a **separate dependency PR** with justification, a reproducible baseline, pinned or constrained versions, compatibility tests, a rollback, and no unauthorized installation. Verify source and native acceptance separately.

At writing, the Unreal C++ naming build remained blocked by competing Editor/Live Coding sessions and low memory; the fail-closed preflight at a prior head returned HOLD without starting an engine build. No claim is made that the latest naming branch compiled in native UE.

## Navigation

- [Unreal README](../unreal/README.md) and [native test commands](../unreal/Docs/UNREAL_TEST_COMMANDS.md)
- [Starbourne native reflection gate](../unreal/Docs/STARBOURNE_NATIVE_REFLECTION_ACCEPTANCE.md)
- [Aureate Wake approved art and name update](../unreal/Docs/AUREATE_WAKE_APPROVED_ART_REFERENCE_2026-11-01.md)
- [Production verification matrix](../unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md)
- [Godot migration coordination](GODOT_MIGRATION_COORDINATION.md)
- [Canon/reveal policy](CANON_AND_REVEAL_POLICY.md)

**No merge, publication, dependency installation, release, or Starbourne unlock is authorized by this document.**
