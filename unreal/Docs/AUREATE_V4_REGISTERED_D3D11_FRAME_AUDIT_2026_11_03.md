# Aureate Wake V4 — registered D3D11 frame evidence and cinematic quality HOLD
**Evidence audit:** November 3, 2026. **Source PR:** #732, initially inspected at `c182cea3def0440999fe5e271efa2ebbb8461c59`. All observations are **NONCANONICAL review work** in a disposable UE 5.8.4 sandbox, not production art, gameplay or a release gate.

## What changed after the earlier screenshot HOLD

The prior `review04` bare `-ExecutePythonScript` job exited zero without ticking its `AutomationScheduler` callback or producing any PNG. Later *private workstation* experiments switched to a **registered Editor.Python named automation test** using `-ExecCmds=Automation RunTest ...;Quit` and generated real GPU screenshots. The native engine is `5.8.4-58902052+++UE5+Release-5.8`, with D3D11_SM5 on Intel Iris Xe Graphics.

**This audit did not launch a new Unreal process or capture a new image.** Remote Desktop Commander was connected for a read-only source/evidence inspection. The independent pixel checker ran on the local saved images and original map binaries; it made no edits.

| Private registered attempt | Automation06 — original V4 Skybourne | Automation07 — authored 280 cm leaf-wing review |
| --- | --- | --- |
| Controller | Named Editor.Python test succeeded | Named Editor.Python test succeeded |
| Engine exit | 0 | 0 |
| PNG | Real 1280×720 D3D11 | Real 1280×720 D3D11 |
| PNG SHA-256 | `53e0decf002523bac81ad93a9dcf01170ba47e881bdbc0bbc896c26aae2bc050` | `75cd3e64b2a24ad20c898ebe2cb89d7797cc1ae80cb40a5a3075406a945899fe` |
| Unchanged source map SHA-256 | `16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40` | `93b0940c75bcd0269d0d20dbf55aaf2bfad3c2f903f82d4daf835797be220e95` |
| Mean RGB luma (0–255) | 21.76 | 24.59 |
| Near-black pixels (all RGB channels below 12) | **84.41%** | **84.87%** |
| Nearly white pixels (all channels above 245) | 0.04% | 0.01% |
| Integrity/pixel-file readback | **PASS** | **PASS** |
| Cinematic visual acceptance | **HOLD** | **HOLD** |

On each candidate, an independent Python/Pillow audit re-read the PNG bytes and the actual saved `.umap`, recomputed SHA-256, decoded the image dimensions and pixels, compared the hashes to BOTH native and host receipts, and verified the native/host controller and no-save/no-unlock flags. All eight evidence-integrity checks passed in each case. These integrity checks **do not** measure artistic approval or prove physics.

**Registered automation report caveat:** Both attempts had Unreal automation state `Success` with **one warning**, because the screenshot had no approved ground-truth comparison image. That warning must not be presented as approved image similarity or as a failed automation execution.

## Visual review against the cinematic target

**Technical render generation: PASS; realistic-cinematic presentation: NOT ACCEPTED.** Inspection of the two real PNGs shows a predominantly black background; the small floating ship is strongly separated from its surroundings rather than embedded in atmospheric depth. The original view retains rectangular stand-in wings, a blocky quarters volume and spherical bridge placeholder. The second shows four legible, bright cyan/gold *leaf-shaped* wing candidates, which are a promising wing-identity direction but not a realistic material, aerodynamic structure, rig or final silhouette sign-off.

Realism is defined here by believable **scale, curvature and lighting**. Cinematic presentation requires intentional **framing, atmospheric depth and readable visual contrast**. These frames prove camera and native detail readback but **do not yet meet** the visual direction: near-black background, provisional bridge geometry, unspecified crew scale, transient review lighting, unapproved wing pose/mesh and incomplete environmental integration. Do not assume a captured `SkyAtmosphere` actor fixes the black-sky review; the actual pixels still show the black field. Separate issue #705 remains a visual hold.

The Automation07 map is a **fresh authored-wing review map**, not a replacement for the checksum-pinned original Skybourne map. The 280 cm leaf-wing design is private/noncanonical; no saved actor is promoted to the playable Aureate Wake.

## Grounded provenance on the authorized workstation

- Original review project: `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\AureateCinematicV4Sandbox`.
- Automation06 host receipt: `skybourne_v4_d3d11_automation06_host_receipt.json`; PNG + native receipt: `SkybourneV4NativeGPU_20261103_Automation06\`.
- Automation07 host receipt: `skybourne_v4_leaf_d3d11_automation07_host_receipt.json`; PNG + native receipt: `SkybourneV4LeafGPU_20261103_Automation07\`.
- Independent read-only checker (local, outside Git): `audit_registered_skybourne_gpu_frames_20261103.py`.
- Compare artifact (private only): `SkybourneV4_BeforeAfter_AuthoredLeaf_PRIVATE_20261103.png`, with its own provenance JSON. It rearranges original native screenshots without retouching the rendered scene.
- Private named-test registration, local host runners and transient capture variants were found on the workstation. **Their exact tested source is not represented by the existing pre-audit PR #732 head**, so no source-reproducibility claim is made for that GitHub revision.

## Next single bounded milestone

1. Preserve both real images and all native/host reports, including the failed Automation05 and earlier attempts. No overwriting their paths, approving comparison baselines, or altering the original saved form maps.
2. In **one new, unique, disposable review context**, isolate and correct the **actual black-background/atmosphere rendering**, using the proven *registered* Python automation method and **one** matched THREE_QUARTER Skybourne camera. Prefer a visible skydome/sky gradient and a physically coherent key/fill strategy over exposure-only brightening. Treat all new lighting and geometry as temporary until creator review.
3. Retain the GPU resource preflight: **at least 6.5 GiB free RAM and 14 GiB free disk**, 1.5 GiB low-memory child-only watchdog, no competing Unreal commandlet. Demand exact map SHA before/after, successful named test, image SHA/dimensions, and automatic black/clipping checks.
4. Only after improved background *and* visual side-by-side review, extend to matched cameras for Seabourne/Submersible. Keep Starbourne a **private static development study**; player/story gate remains LOCKED.

**Unchanged authority:** PR #732 stays draft and unmerged. No production C++ actor, SaveGame, source model or four original review maps was modified by this audit. No Starbourne player unlock, cinematic approval, continuous physical clearance, water/pressure validation or distribution is authorized.


## Automation09 preflight — prepared, NOT executed

A uniquely named **camera-relative solid cyclorama** experiment was source-prepared on the private Windows workstation from the safely archived Automation06 source. The bounded change moves the temporary backdrop center from hard-coded world coordinates to the camera's forward vector at 6,500 cm. The private capture and runner scripts passed Python compilation and a new registered Editor.Python entry was prepared **without touching the original V4 maps or the archived source**.

The GPU runner immediately **refused execution because free physical RAM was below its 6.5 GiB launch gate**. No UnrealEditor-Cmd process was launched, no Automation09 GPU image/host receipt/native log was created, and there is **no evidence that camera-relative placement fixes the black background**. A follow-up native-process check found no orphan commandlet; independent SHA and pixel integrity rechecks of Automation06 and Automation07 remained PASS. Do not weaken the resource gate or repeatedly retry while memory fluctuates around the threshold. Preserve this failed preflight as a separate source-prepared, **NATIVE_NOT_RUN** experiment. The old standalone 08 preparer also refused due to an archived source location before creating any runtime artifact.

The next GPU work remains exactly one unique, guarded registered-test run under sufficient stable RAM/disk headroom, with pixel validation and unchanged original maps. **No four-form GPU campaign, cinematic signoff, production promotion, or Starbourne unlock is authorized.**

## November 3, 21:12 Eastern follow-up — runtime resource gate remains HOLD

**Verified current PR head before this addendum:** `438d44b38a657c717734216c5dd8aaf17118db8b` (open, draft, unmerged); **8/8 exact-head hosted workflows completed SUCCESS**. These remain hosted source checks, not Unreal rendered image or physics acceptance.

On connected workstation `neontic`, the preflight found the existing user `UnrealEditor` process active, **no competing `UnrealEditor-Cmd.exe` process**, and approximately **16.97 GiB free disk**. Correct Windows native physical-memory telemetry returned approximately **3.96 GiB available RAM** in the later check (earlier same-session Windows CIM returned ~3.59 GiB). The runner's **6.5 GiB minimum GPU launch condition is not met**. The camera-relative `Automation09` registered-test source and host runner were read and match the planned disposable sandbox, explicit original Skybourne map SHA, named D3D11 automation test, no level-save call, and fail-closed native/PNG receipts. **No new D3D11 launch, new PNG, new map, or new actor is claimed in this follow-up.**

The existing user Editor and browser processes were observed, **not closed, terminated, trimmed or changed**. Do not silently free resources by terminating software, reduce thresholds, or run overlapping GPU attempts. When RAM is safely available, use the already prepared, uniquely named `Automation09` run once; check 6.5 GiB free RAM, 14 GiB disk, original map SHA and no competing commandlet *immediately before launch*, then verify the native test controller, PNG SHA/dimensions and actual pixel histogram. In particular, a camera-relative developer billboard is **not** an accepted physical sky, and #705 remains an independent atmosphere/black-sky HOLD.

**Authority:** earlier native screenshot-generation successes remain PASS; realistic-cinematic quality remains HOLD; Starbourne player/story gate CLOSED; PR draft/unmerged and original four review maps untouched.

### Independently rehashed original V4 maps, without Unreal launch

A fresh direct Windows `certutil -hashfile ... SHA256` read of all four original disposable V4 `.umap` files returned the following **exact expected checksums** (all match the native four-map audit receipts):

| Review map | Recomputed SHA-256 | Result |
| --- | --- | --- |
| Skybourne | `16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40` | PASS |
| Seabourne | `b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a` | PASS |
| Submersible | `815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35` | PASS |
| Starbourne, developer-only static | `953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00` | PASS |

This is **file-integrity evidence only**; it does not re-run the Unreal four-map readback, prove GPU images from all four forms, approve art, or authorize a Starbourne player/story unlock. Automation09 remains **NOT LAUNCHED** until its resource gate passes.
