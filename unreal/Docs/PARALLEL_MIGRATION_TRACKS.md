# Unreal migration: parallel delivery tracks (draft; October 30, 2026)

## Authority and nonclaims
- Unreal branch: `feat/unreal-5-8-migration-foundation` (PR #608). Godot remains playable/reference implementation.
- October 30 creator-approved latest cast art is the visual acceptance baseline. Source artwork must be supplied, rights/provenance recorded, and individually compared in the actual engine before character acceptance.
- No Unreal Editor compile, native rendered captures, game-ready rigs, or packaged Windows executable are established by these text commits.
- Keep this PR draft; never mark the migration completed without compile, runtime, artistic and Windows acceptance evidence.

## Parallel workstreams
| Track | Native implementation target | Independent evidence gate |
| --- | --- | --- |
| First Wake | Ordered, resettable milestone state; Ender third-person control; Ionia interaction; boarding, checks, launch, sea contact, flotation, empty-reserve inspection, return | Unedited packaged gameplay capture and scene assertions for each beat |
| Character pipeline | Approved Ender/Ionia/Lyra/Reson/Aepex face+silhouette sheets; source asset IDs, model/rig materials, hair geometry and LODs | Side-by-side approved artwork versus UE renders (Ionia retains long curly blonde hair, including optional captain updo) |
| JRPG gameplay | Transactional 3-active roster combat, stats/skills/equipment, costs and damage, rollback on invalid actions | Deterministic automated tests with mirrored Godot fixtures |
| Ship/world | Aureate Wake flight, seaworthy landing, submersible, gated Moon Bridge; coast/weather/sky lighting | Separate functional tests per mode; no premature Moon Bridge gameplay claim |
| Save / continuity | Versioned stable character IDs, progression, save/load and migration mapping | Round-trip tests, save-corruption handling and backward compatibility decision |
| Delivery | Windows editor/project build, cooked content, installer, crash reports, performance profiling | Signed or clearly unsigned install/uninstall evidence, Windows Defender status, gameplay capture |

## Dependency edges
1. First Wake milestone state can land independently of the visual asset pipeline; it is not an accepted scene by itself.
2. Combat data and save schema should stabilize before UI or complete progression balancing.
3. High-fidelity characters and cinematic lighting are parallel but only art-approved after native screenshots and performance evidence.
4. Do not delete or retire Godot gameplay, change main README to claim Unreal release, or merge PR #608 without verification.

## Canon
Party order Ender (Spirit), Ionia (Earth), Lyra (Water), Reson (Fire), Aepex (Air). Three active battle members. Five Lights are story affinities, not forced magic classes; resonance is story energy, not automatic battle magic. Preserve the approved First Wake ordering and leave Lyra/Talen reunion and physical salvage unclaimed until implemented.
