# Ender visual review — static lookdev candidate

**Verdict: visually below production target; not accepted as an Unreal character.** This review compares the four-angle offline `Candidates/Ender_turntable.png` from this branch with the exact Ender source-of-truth image identified by `docs/CHARACTER_AND_ART_AUTHORITY.md` (approved appearance from PR #261, SHA-256 `619517944ebe12b295bf5f780abb1a49bce2449230654fb8c49b11e8380546fd`) and the private October 30 five-character cast sheet. The latter is useful for group relationships but contains a green-versus-copper Ender hair conflict. October 31 generated visual-bible sheets are supplementary design exploration, not character or gameplay canon; some panels swap names and assign inconsistent stats. Reference images are intentionally not copied into this branch.

| Priority | Visible candidate finding | Required production correction and check |
|---|---|---|
| 1 | Separate olive waistcoat panels now expose the cream shirt, but they and the back still read as smooth oval forms. Limbs remain cylinders and boots remain bulbs. The approved Ender has a fitted waistcoat, open collar and embroidered sleeves, practical trousers, layered belts, laced boots and a youthful, slender silhouette. | Author a fitted sculpt and clothing layers with folds and seams. Compare front, side and back at the same scale as the approved full-body image, then inspect a neutral-lit UE frame and an in-scene frame. |
| 2 | Hair is a single rounded cap; eyes and face are schematic. Forehead goggles are identifiable, but the approved expressive face and hair shape are absent. The model's dark green hair follows the October 30 group sheet, while the exact approved Ender appearance and written character lock say auburn/dark copper. | Resolve hair authority with the creator. Sculpt facial landmarks, hair masses and goggle straps, and create material/texture detail. Obtain an approved close-up and profile review. |
| 3 | The full-length staff now meets a gloved palm with four small curved fingers and a thumb visible in the offline views. Their anatomy and grasp still read as a schematic fixed pose; the shaft, wrap, ferrules, satchel and strap remain simplified. | Sculpt a believable staff grasp, verify hand/staff clearance and retention in front/side/back views, then skin and test draw, carry and locomotion animation in UE. |

## Native Unreal 5.8.4 evidence — November 2, review-only

The Windows NEONTIC workstation became reachable. A separate, content-only Unreal 5.8.4 project imported the unchanged static Ender GLB and wrote an `IMPORT_PASS_REVIEW_PENDING` receipt. Source SHA-256: `d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2`. Imported extents X/Y/Z: 56.32 / 31.60 / 185.80 cm. This proves only native StaticMesh intake, not skinning or playable game compilation.

Calibrated transient point-light intensities of 300 / 125 / 125 (Unreal Editor intensity settings) produced a **legible but primitive** four-view native screenshot set at 800×450 in `Saved/CharacterLookdev/NativeCaptures/ender643_review07_labeled` on the authorized workstation. Screenshot CRC, dimensions and independent SHA-256 checks passed, while the receipt expressly says `CAPTURE_FILES_PRESENT_UNREVIEWED`.

| Native view | Capture SHA-256 | Visual assessment |
|---|---|---|
| Front +Y | `26712a00e5575b751dbe132a95c0c912612f0bed5659e454b73720e3e847a5c7` | Upright silhouette, goggles and staff visible; facial anatomy still schematic |
| Profile +X | `e3e6c16c5dcfbe581bccc82634358d947a302efe2dd731b7fd16004f5f579dc1` | Approximate pose and staff proximity; hair and boots are blocky |
| Rear −Y | `861f6a9242cfe872d265b96954a90d82823b1d2595bf7953ad621ea6a7bf542e` | Back waistcoat reads as a rounded oval, clothing fit not credible |
| Front three-quarter (+X,+Y) | `2a8e57fd18d7139f0d516caacad250bde8519b6e445522cf2cbbeb45dae97483` | Goggle/staff silhouette visible; grip and facial expression cannot be approved |

Earlier isolated attempts remain preserved: `review02` produced four overexposed PNGs; `review03` stalled with no PNGs; `review04_single` improved visibility; `review05_single` reduced extreme highlights; `review06_four` proved the calibrated full-set process but exposed camera-label/axis mismatches. `review07_labeled` corrected camera direction using *transient unsaved camera relocation*, not edits to the original level.

**QA verdict: STATIC_LOOKDEV_NATIVE_RENDER_PASS / VISUAL_QUALITY_FAIL / RIG_NOT_VERIFIED / CANON_NOT_AUTHORIZED.** These native renders permit concrete art critique, but still do not establish production likeness, acceptable clothing silhouettes, anatomically credible staff contact, skeletal deformation, animation or gameplay integration. The copper/auburn-versus-green hair reference conflict requires creator resolution. No candidate mesh or image has been accepted as canonical.

The geometry checker and deterministic regeneration establish structural validity of the GLB. The calibrated Unreal captures establish native static rendering with visibly upright geometry. They do not replace high-fidelity sculpt, materials, skin/rig, gameplay tests or creator sign-off. Keep the PR draft/unmerged and all captures in the separate review sandbox.
