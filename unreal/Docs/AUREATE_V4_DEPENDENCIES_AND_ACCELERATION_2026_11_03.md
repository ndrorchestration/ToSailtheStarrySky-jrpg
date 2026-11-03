# Aureate Wake V4 — cross-track dependency and acceleration register
**Latest proven critical-path advance:** Full Editor one-actor pilot PASS and native **18-actor Skybourne** map save PASS at UE5.8.4. Fixed four identity labels, original approved image still authoritative. Native GPU screenshot is HOLD; a D3D11 startup with ~5.53 GiB free triggered a memory watchdog. **GPU minimum raised to 6.5 GiB**, with 1.5 GiB low-memory process stop; ordinary NullRHI stage remains 4.2 GiB. See [Skybourne native evidence](AUREATE_V4_NATIVE_SKYBOURNE_SCENE_EVIDENCE_2026_11_03.md) for exact map checksum. The older actor-pilot RAM HOLD in the historical baseline was resolved by the later pilot run, not by lowering any threshold.


**Effective November 3, 2026.** Narrow review-only scope: draft PR #732 stacked on #699. Active engine is UE 5.8.4; no new production engine, script package, plugin dependency, game actor/save schema or release authority is introduced.

## Canonical and engineering boundary

Original approved ship reference SHA-256: 03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13. The approved visual reference (one vessel, geodesic bridge, living quarters beneath, four persistent wing identities, ivory/gold and blue resonance styling) is not identical to prototype GLB acceptance.

Player-facing names are **Skybourne, Seabourne, Submersible, Starbourne**. Preserve older serialized Unreal enum values for compatibility. Creator explicitly permits **private internal Starbourne development** but does NOT authorize player-facing unlock, plot reveal, moon route, production release or clearance waiver. The bridge and quarters form a common coupled central assembly; actual pivot angle and physical clearance need separate verification.

The exact V4 source revision before this documentation update was 3859663cc30d70ca0feea7fa9580ae734cf1d6ab: **19/19 source tests and 7/7 hosted checks PASS**. Genuine native Unreal 5.8.4 NullRHI imported five V4 GLBs as five StaticMeshes with four material slots each, exit zero and no reported errors/warnings. Two separate headless scene attempts failed to spawn even the first actor; the read-only native probe found zero actors and an unchanged saved-map SHA. The later full Editor actor pilot was **blocked before launch** due free RAM below the safe 4.2 GiB threshold. No new V4 cinematic screenshots or assembled form scenes exist from these runs.

## Dependency map

| Layer | Independent source | Current acceptance | Integration boundary |
| --- | --- | --- | --- |
| Approved art and naming | Creator reference, canonical names | Art direction APPROVED | Production meshes NOT approved |
| V4 ship details | PR #732 Python source generator and exact GLB manifest | Offline + native mesh IMPORT PASS | No scene, rig or physics admission |
| Single actor pilot | New disposable UE full Editor with PythonScriptPlugin and EditorScriptingUtilities | RAM GATE HOLD, NOT RUN | Must precede scene staging |
| Shared layout | Deterministic V4 four-form plan, one hull and persistent wing slots | Source-only | Pose angles are not approved canon |
| Wings/hydrofoils | Draft #724 stacked on #695 / #656 | Separate draft review | No continuous swept-motion proof |
| Coupled bridge and quarters | Drafts #702 and #706 | Opt-in prototype | No V4 integration/rotation safety |
| Sky/ocean atmosphere | Draft #705 | BLACK SKY VISUAL HOLD | No accepted cinematic sky |
| Starbourne | Restricted fourth-form design authority | Private development OPEN | Story/player gate CLOSED |
| First Wake | Independent gameplay/SaveGame PRs | Separate native/PIE gates | No evidence transfer from GLB import |
| Legacy npm/NW.js security | Historical packaging lane | Separate security HOLD | No ship-related lockfile updates |

## Development acceleration: the smallest reversible pipeline

1. **Source first.** Deterministic GLB regeneration, exact SHA manifests, UV and topology tests, four-form identity checks and asset provenance run with Python stdlib only. No Unreal launch needed per geometry iteration.
2. **Import once per candidate.** Strict isolated Unreal review importer rejects occupied destinations and proves actual StaticMesh/material slots. Keep generated binaries and Unreal asset receipts outside Git; source code + guard tests + documentation are committed.
3. **Full Editor one actor first.** Epic's full editor -ExecutePythonScript path runs after level startup; the fast -run=pythonscript commandlet is effective for importing assets but failed world actor creation here. The one-actor pilot uses a fresh project and has no gameplay bindings.
4. **One hero map.** Assemble Skybourne with shared hull, geodesic forward bridge, paired quarters, four existing wings and V4 details. Prove actual materials/geometry and camera frame with real D3D11/D3D12 screenshot before making the other two ordinary form maps.
5. **Reuse identity and cameras.** Seabourne adds exactly two hydrofoils; Submersible keeps its four tucked-but-visible wings and adds light rails. Share four explicit review camera ROLES and the same core rather than inventing four unrelated ships.
6. **Private Starbourne review.** Four equal radial sail details follow the same four wing identities; private visual and engineering tests may run without player form transitions or unlock.
7. **Serialized native work.** Host runner checks 4.2 GiB free RAM and 14 GiB free disk for the full Editor pilot, refuses concurrent commandlet, and can stop only its own child process on timeout or low memory. Do not terminate the user's active Editor/Live Coding or lower thresholds.
8. **Evidence and integration.** New receipts bind exact source SHA, engine, GLB SHA, build method and true results. Merge or cross-branch promotion is separate and requires reconciliation of motion, bridge, sky, physical clearance and creator art approval. No draft changes should be silently merged to main.

## Deterministic scene layout contract

Source: unreal/Tools/author_aureate_v4_review_scene_plan.py. Its JSON manifest declares one shared vessel, four persistent wing IDs, a coupled central habitation assembly, one review accessory set per form, four matching view *roles* and strict entry gates. It intentionally carries no invented approved pose angles, camera positions or screenshots. Starbourne internal development is authorized; player unlock remains false. The JSON is a layout plan, NOT an actual Unreal map.

To verify without Unreal, run the seven engine-free tests in unreal/Tests/test_aureate_v4_review_scene_plan.py. To create a local JSON outside Git, run the plan author with --out to a previously unused path, then the same path with --check. Never overwrite existing results.

## Tooling, dependencies and documentation

- On the Windows review host, the source-side stdlib tooling runs under Python 3.14.5. The UE 5.8.4 Python plugin embeds its separate Python interpreter. Do not install source Python packages into a packaged Game.
- EditorScriptingUtilities is enabled only in the NEW disposable full-Editor actor pilot (not required for the already verified asset import, and not a production game dependency).
- No Unreal engine, VS toolchain, pip package, npm package/lockfile or C++ module upgrade was made.
- Native import/evidence: AUREATE_CINEMATIC_V4_NATIVE_IMPORT_EVIDENCE_2026_11_03.md.
- Scene design and acceptance: AUREATE_CINEMATIC_DETAIL_V4_2026-11-03.md.
- Approved art: AUREATE_WAKE_APPROVED_ART_REFERENCE_2026-11-01.md.
- Unreal tool index: unreal/Tools/README.md; host and full Editor verification must not be conflated.

## Holds

Full Editor actor creation, production assembly, native V4 cinematic renders, 3D artist approval, bridge+quarters continuous swept clearance, ocean hydrofoil physics, pressure safety, black-sky issue #705, playable First Wake/SaveGame and any Starbourne player unlock remain NOT ESTABLISHED or NOT AUTHORIZED. No protected branch merge, art promotion, installation or public distribution follows from this register.
