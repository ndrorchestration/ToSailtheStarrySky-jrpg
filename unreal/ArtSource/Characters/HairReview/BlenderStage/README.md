# Ender V3 original hair — isolated Blender 5.2.4 LTS authoring handoff

**SOURCE-ONLY STAGED; NO DCC SCENE, NATIVE GPU RENDER, FACE FIT OR GAME CHARACTER IS APPROVED.**

This directory contains source copies of the installed Neontic portable DCC gate and its Blender scene builder. There is no paid Daz/MetaHuman character or proprietary hair in this repository.

- Official portable Blender 5.2.4 LTS ZIP and official SHA-256 were verified before staging to `C:\TSTSS_Tools\BlenderPortable\blender-5.2.4-windows-x64`. ZIP SHA256: `bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c`. Local executable exists, but no Blender process was started in this character pass.
- Source geometry: the original [V3 Ender hair review GLB](../CandidatesV3/Ender_BroadLayerHair_V3_NONCANONICAL.glb), pinned SHA256 `bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e`. It is a **rejected/unapproved static study**, not final hair.
- `Start-TSTSSCharacterHairReview.ps1` is **check-only by default**. Missing source, existing saved .blend, active Unreal Editor/LiveCoding/Blender/UBT, under 6.5 GiB free RAM or 14 GiB disk cause a HOLD and exit without starting Blender. It never kills another user's process. It requires the exact expected Neontic paths.
- Once the independent session ends and gates pass, an operator may explicitly use `.` plus `Start-TSTSSCharacterHairReview.ps1 -Launch` from an approved isolated worktree. The result is only a **local editable Blender scene** with the real original V3 source mesh and four study cameras and studio lights. This step was **not executed** in the current work.
- The Python builder refuses any existing scene/receipt file and never exports to Unreal, DAZ, production art, or main. Local `bpy` runtime behavior, camera labels, actual glTF import and screenshots **remain untested until Blender executes**.
- The local DAZ Genesis 9 Starter Essentials hair is **not** loaded or copied; direct use of DAZ 3D content in an interactive game needs the applicable Interactive License per [Daz official terms](https://www.daz3d.com/daz-licenses#interactive). No such entitlement has been verified.
- A completed .blend is **not** enough for character acceptance. The creator-approved November 11 Ender portrait controls the facial likeness, full tousled brown/copper hair, green eyes, stubble, aviator goggles, olive outfit and double-ferrule staff. Source and GPU multi-angle review, scalp-goggle intersection checks, rig/skin/cloth motion, actual player pawn and creator approval must follow.

Exact local preflight evidence (Nov 15 evening): Whiteout UnrealEditor PID 19268 and LiveCodingConsole PID 7176 remained active; safe launcher printed `TSTSS_DCC_HOLD` and exit 2 with no Blender process. Portable stage had ~16.23 GiB C free and ~4.32 GiB RAM free after unpacking. No game assets or protected maps were modified. Keep PR #761 draft/unmerged.
