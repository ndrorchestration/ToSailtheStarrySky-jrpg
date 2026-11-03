# Ender V4 facial-topology study — UE 5.8.4 native review

Date: 2026-11-02 US/Eastern (native log UTC 2026-11-03). **REVIEW ONLY / NONCANONICAL STATIC STUDY / CINEMATIC LIKENESS FAIL-HOLD.** Stacked on [draft V3 PR #716](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/716), itself on camera QA #715. This V4 source does not replace or promote the existing approved cast or production game pawn.

## Actual approved reference and source-of-truth boundaries

Accessible approved character visual documents include October 30 `To Sail the Starry Sky: Core Cast.png`, `Core Cast Bible.png`, `Character Bible.png`, and a separate September `Ender: Solarpunk RPG Character Sheet.png`. The most recent approved cast visual shows a young adult Ender, dark/green-looking tousled hair, bright green eyes, worn brass forehead goggles, dark olive mechanical field outfit, and resonant staff. The historical stylized Ender solo sheet has short dark auburn/brown hair and an anime-style younger face. Visuals differ in literal hair color and realism; the project records a **HOLD** for the conflicting hair-color treatment. No invented measurements or image-generated Level 1 stats are treated as canon. Ender is 22; the height order remains **Reson > Aepex > Ender > Ionia > Lyra**, exact numeric heights unspecified.

V4's eye, brow, nose, ear and chin positions are **provisional model-space engineering hypotheses**; no actual landmark correspondence has been measured or artist approved from the 2D reference.

## Scope of implemented V4 source candidate

Derived isolated `FidelityCandidates/EnderV4/Ender_ender_anatomy_v4.glb` from source V3. Final GLB SHA-256 **`ac36e1d23044ca79d5a954dc8cb85cff8461117c026674ed77fe2e482acaca0b`**, size **436,292 bytes**, **20,088 indexed triangles**, **178 individually named components**, **36 material sections**. Original cast, Ender V1, V2 and V3 GLB hashes were checked unchanged. `build_ender_fidelity_v4.py` creates one connected, closed, radial/longitudinal face mesh with cheek, orbital, brow, nasal bridge and tapered jaw planes; removes oversized detached V3 nose/eyes/ears, substitutes smaller separate anatomical study shapes and eyelid edges, and retains V3 hair cards, V2 waistcoat, goggles, green eye intent, full straight centered-wrap brass-ferrule staff.

**Not a professional head retopology**: the ring topology is sculpt/visual study only, not facial muscle loops, UV skin texturing, eye-socket deformation topology, groom simulation or production skeletal skinning. Hair remains noncanonical temporary green.

Native view #1 exposed an eye issue: the shallow eyes at source z=0.111 m were still visibly floating in front of the face. The initial V4 GLB and genuine native frames were preserved locally under `C:\TSTSS_EnderV4FirstNativeEvidence_20261102` (model), with D3D11 log and screenshots in `C:\E7\CastAllSandbox`; initial GLB SHA **`f6966c2781dd68a04244bb0f0083390fbd9244ef807e8ef2267b91ab03e3a5fc`**. A small source revision recessed eyes/iris/pupil and eyelid vertices toward the orbital face. The initial branch candidate was **not committed**; final V4 renders below are from the revised SHA `ac36...`. This is an actual measured iteration, not a claim of reference-fidelity pass.

## Exact native Windows verification, separate from hosted CI

Authorized `neontic` Windows workstation, local Unreal Engine **5.8.4**, disposable projects only.

- First `C:\E7\CastAllSandbox` test: real Unreal NullRHI StaticMesh native import SUCCESS; D3D11 1280×720 native front, three-quarter and profile screenshots SUCCESS; independent PNG checks PASS. First screenshot visual QA found detached/orbitally misplaced eyes.
- Final **`C:\E8\CastAllSandbox`** test: real Unreal `Editor.Python.CastAllSandbox.test_ender_v4_import_native` SUCCESS / process exit 0, imported exactly one standalone StaticMesh under `/Game/ArtLookdev/Characters/EnderAnatomyV4` from the revised pinned GLB SHA `ac36e1d23044ca79d5a954dc8cb85cff8461117c026674ed77fe2e482acaca0b`. Staff-inclusive Unreal native Z height **185.800003 cm** is only a scale sanity check, **not approved canon height**.
- Real **D3D11 SM5** screenshot automation `Editor.Python.CastAllSandbox.test_ender_v4_head_native` SUCCESS / process exit 0. Transient V4 preview actor, lamps and front/three-quarter/profile cameras; original V2 reference map actor moved transiently out of frame. **No level save** and no production asset mutation.
- `verify_ender_v4_native_captures.py` independently validated original `Saved/Automation/Reports/test_ender_v4_head_native/.../Incoming.png`, exact engine/source/asset/map receipt, all screenshot task completions, CRC/IDAT pixel decoding, 1280×720 dimensions, subject presence and distinct frame hashes. **Exit 0**, status `V4_NATIVE_SCREENSHOT_INTEGRITY_PASS_ART_HOLD`.
- Actual revised V4 front PNG SHA-256 `e754c766d3299902bd5fec3a1aac2c2da9bb40f66d38eda6c16d494bcfa23f1c` (217,778 bytes).
- Actual revised V4 three-quarter PNG SHA-256 `749447abf8ae69541dc5534fff8e484fd2f86a79a77083fb74ee7dd7fb268ceb` (213,135 bytes).
- Actual revised V4 profile PNG SHA-256 `62ee7e8b5b0dd204aefa96b23021fa05288c3ae6513a93a177abd2566c6c2b95` (158,641 bytes).
- Genuine native PNGs were preserved byte-for-byte in `ReviewCaptures/2026-11-02/EnderV4Anatomy/` in this draft; screenshots are not image-generated concept art.
- Native original saved V2 review map SHA-256 **unchanged** at `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a` before/after capture. Original original/V1/V2/V3 source GLB preserved.
- `test_ender_fidelity_v4.py` includes immutable-source and negative controls, model-space eye offset regression, generated GLB checks and false-art-approval rejection; `test_ender_v4_native_captures.py` includes native screenshot receipt/production destination negative controls. Across V1–V4 and V1/V2 camera source tests, **50/50 local source regression tests PASSED** on the finalized source. This is not bitwise Linux-vs-Windows generator parity and not an Unreal packaged game test.

## Real image QA — artistic HOLD

Native revised front, three-quarter and side images were visually inspected. Reducing the huge disconnected eye offsets and the previous nose/ear blocks improved some local structural proportions. However, the revised eyes are now too small/recessed and do not read as naturally embedded human eyes, face/jaw still has low-poly faceting, ear anatomy remains crude, hair cards look like rigid blades, goggles and skin are flat material studies, and garment surfaces remain basic. No stubble, natural skin roughness/subsurface response, eye wetness/lashes, facial expressions, shape keys, or a true sculpted resemblance to the cinematic October 30 cast. A technical source-space mesh and correctly decoded screenshots are not evidence of canonical likeness.

Art gates: **native intake PASS, native image-integrity PASS, source regressions PASS, artist reference-likeness FAIL/HOLD, PBR lookdev HOLD, rig/animation not attempted, creator approval HOLD.**

## Highest-value next small slice

Stop iterating on procedural eye ellipsoids. Transfer the current reference-approved Ender face into a *human-reviewed landmark sheet* (eyes, nasal bridge, cheekbones, ears, jaw/side profile) and author a separate facial topology sculpt with contiguous orbital/eyelid loops and proper reference-scaled hair silhouette. Use consistent face-centered Unreal cameras and reference thumbnails, original true PNGs, geometry/skin rig tests and creator signoff. Treat mismatched dark-green versus brown hair palette as an explicit artist decision, not an accidental source palette.

**Do not merge this draft stack, change Level 1 stats, write production assets, assert rig completion or release.**
