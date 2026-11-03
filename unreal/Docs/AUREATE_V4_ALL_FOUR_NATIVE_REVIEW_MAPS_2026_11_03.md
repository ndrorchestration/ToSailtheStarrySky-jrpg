# Aureate Wake cinematic V4 — four genuine Unreal review maps
**Independent same-day verification:** The four previously saved V4 review maps now PASSed a native read-only UE5.8.4 load/actor/identity/SHA audit. A NEW separate pilot proves bridge+quarters can rigidly share one rotating parent, with 17.5-degree provisional rotation and original pose restoration. It does not certify the real production gimbal, transform collision or final materials. [Exact audit/pivot evidence](AUREATE_V4_NATIVE_MAP_AUDIT_AND_HABITATION_PIVOT_2026_11_03.md). GPU V4 screenshot remains HOLD.


**November 3, 2026.** Unreal 5.8.4-58902052+++UE5+Release-5.8. Review source draft PR #732. Four separate noncanonical, nonplayable static layout studies, not approved cinematic ship models and not a playable transformation system.

## Native map evidence, independently file-hashed after the engine exited

| Review form | Native actors | Saved map SHA-256 | Distinction |
| --- | ---: | --- | --- |
| Skybourne | 18 | 16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40 | Four wing identities with V4 imported gold filigree and shared hull trim |
| Seabourne | 20 | b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a | Exactly two hydrofoil proxies, two imported V4 foil-detail meshes, two struts |
| Submersible | 15 | 815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35 | Four tucked but visible wings and imported blue lighting rail |
| Starbourne | 14 | 953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00 | Four equal radial sail detail instances, INTERNAL STATIC STUDY ONLY |

The first Skybourne review map was assembled in a successful full Unreal Editor session. A separate full-Editor NullRHI session produced the other three maps using the same shared hull, geodesic bridge proxy, living-quarters proxy, open observation deck and four stable wing identities. Each review form has four camera ROLES with matched nominal camera coordinates; no true film output or approved cinematic frame was generated.

**Native evidence:** the three-form host result is NATIVE_THREE_FORM_STAGE_PASS, exit 0. Its Unreal embedded-Python receipt is THREE_NATIVE_FULL_EDITOR_REVIEW_MAPS_STAGED_PASS, listing 20 + 15 + 14 actors and three separate .umap checksums. The older Skybourne receipt separately establishes 18 actors. All four persisted file hashes were independently rechecked on Windows after the native process and each matched the native receipt. There were no remaining UnrealEditor-Cmd processes. Total **67 review actors across four maps**, not a single runtime actor or 67 new pieces of production content.

Native receipts and review binary artifacts stay on the authorized Windows workstation under C:\tmp\TSTSS_AureateCinematicV4_Native_20261103, with import source GLBs under C:\tmp\TSTSS_AureateCinematicV4_Output_20261103. None are merged into production, published as user-approved models, or represented as final rendered images.

## Authority and design limits

One vessel, not four separate canonical hulls. Exactly four principal dragonfly-wing identities (FORE_PORT, FORE_STARBOARD, AFT_PORT and AFT_STARBOARD) persist through the review maps. Exactly two Seabourne foils. Submersible wing roots remain visible, though folded. Four equal Starbourne radial sail modules are a **private internal development** study; player form access, story reveal, moon route and save progression remain LOCKED. Legacy C++ enum names can remain to preserve serialization; user-facing names are Skybourne, Seabourne, Submersible and Starbourne.

The geodesic bridge and quarters need a common coupled central transform. Currently the bridge and quarters in these maps are static BLOCKOUT placeholders; no true pivot, rotating habitation, pressure hull, structural load path, continuous swept collision or cabin-scale art approval has been demonstrated. Their proposed spatial dimensions are not canon.

## Performance and implementation strategy

1. Deterministic, dependency-free Python generates five GLB accessories and a checksum-bound four-form layout-plan JSON; source tests catch geometry/UV/naming and provenance defects before any engine launch.
2. One native import verified all five Unreal StaticMeshes and four slots each. Full Editor NullRHI scripting, NOT the fast headless PythonScript commandlet, is used for actor scene staging.
3. Reuse common hull/wing identities and comparison cameras across all modes; change only the mode-specific foil, light and sail detail. Separate heavy GPU rendering into one-hero-frame-at-a-time jobs rather than four concurrent renderer sessions.
4. A prior D3D11 Skybourne render attempt failed safely due precheck and then RAM watchdog; it did not produce a PNG. GPU rendering now requires at least **6.5 GiB free RAM**, 14 GiB free disk, a unique attempt token, and a 1.5 GiB available-RAM stop threshold for only the child process. NullRHI actor staging continues to use 4.2 GiB preflight.
5. Demand real native D3D11/D3D12 3/4, top, side and bridge/hinge captures, pixel checks, author review, and then independently verified continuous 6-route swept clearances. Black-sky issue #705 remains independently held.
6. No silent integration of unmerged #702/#706 bridge/quarters rotation or #724/#695 wing/hydrofoil motion. First Wake playable/SaveGame acceptance is a separate lane.

## Evidence boundaries

**PASS:** five native imported four-slot meshes, one full Editor single-actor pilot, four saved native 3D review maps, all four map hashes, preservation of the user's running Editor process, Starbourne player-story lock.

**NOT VERIFIED / NOT AUTHORIZED:** rendered V4 GPU frames, high-cinematic artistic likeness, real geodesic glass, pressure and hydrodynamics, physical or continuous transformation, approved rotation/rig, packaged game, replayable gameplay, player Starbourne unlock, branch merge and release.

Source documents: AUREATE_V4_NATIVE_SKYBOURNE_SCENE_EVIDENCE_2026_11_03.md and AUREATE_V4_DEPENDENCIES_AND_ACCELERATION_2026_11_03.md.
