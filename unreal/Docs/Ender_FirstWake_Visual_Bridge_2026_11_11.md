# Ender vertical-slice upgrade — PIE character visual bridge (2026-11-11)

**State:** source implementation **DRAFT / UNMERGED / NOT NATIVE-VERIFIED**. This is a real addition to `ATSTSSExplorerCharacter`, the existing playable First Wake player pawn—not a new concept image or an independent mockup. It is **opt-in, PIE-only**, so an absent candidate mesh leaves the original pawn unchanged.

**Exact source parent:** First Wake multipath review [PR #799](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/799) commit `2afb4b7ea6cda75dc6068014eb19c06718259539`. This child does **not** merge #793 (RPG UI/equipment), #808 (post-splashdown Lyra recruitment repair), #810 (Centering/Pulse) or other parallel drafts. Reconcile before any integrated head/build claim.

## What this code now does

`ATSTSSExplorerCharacter` has six review-only editable Blueprint inputs for a skeletal Ender candidate, sealed goggles and staff, plus off-by-default visibility flags and local attachment transforms. In **PIE only**, if a body is explicitly provided and its skeleton has a plausible bone count with matching head and hand bones, the running pawn's `USkeletalMeshComponent` binds that mesh. A separately configured goggles or staff `UStaticMeshComponent` attaches to a valid bone only when an operator intentionally enables it; missing bones and failed loads fail closed. Both accessories use no collision or overlap. No transform, mesh or palette is saved into the source `USkeletalMesh`.

This is a **visual bridge**; it does not change movement input, story milestones, saving, recruiting Lyra, inventory, jobs, combat spells, equipment status, or Starbourne story gates. The existing First Wake pawn is still player-controllable. The new review mesh is **unset by default** and no accessory is visible until an operator imports assets and binds them on a disposable PIE Blueprint subclass.

**It does NOT yet provide:** a creator-approved face, hair, styled goggles fit, finished outfit, real animated staff grip, valid animation blueprint, cloth deformation proof, native UE5.8.4 compilation, gameplay screenshot, or full vertical-slice visual acceptance.

## Creator approval recorded November 11 — definitive Ender likeness

The creator explicitly approved **the Ender portrait in the SECOND panel from the left** of the uploaded **To Sail the Starry Sky — Cast & Gameplay Bible — Main Party (Act 1)**. This supersedes all older buzz-cut/very-short hair directions. It is an image-based **visual-reference approval**, not an approval of a generated skeletal mesh or any change to the game systems.

**Match this source reference**, not a generic image lookup: youthful expressive face with subtle facial stubble; full, dark-brown hair with tousled copper/auburn texture; brass/bronze head-worn sealed aviator goggles with teal-tinted lenses; rolled olive/sage mechanic sleeves; dark leather chest harness and straps, pouches and brass hardware; restrained turquoise-glowing technical devices. Keep approved in-game bright-green eyes. Preserve his Resonator job, Harmonic Resonance Engineer trade, Spirit affinity, staff design and other canonical RPG systems. Do not copy the illustration's compact infographic text over more recent system documents.

The original source is the **user-uploaded conversation image**; the underlying binary has not been attached to this GitHub branch. Obtain and checksum the original reference file before asset generation that requires image-to-3D input. An unrelated web image is **not** an acceptable substitute.

The approved target **replaces** the old short-hair priority in the steps below, and the professional 3D likeness, hair volume, outfit, goggles and staff still need native Unreal fit/animation and creator model approval.

## Visual and personality tone to carry into final art

- **Canon look (superseded hair lock corrected November 11):** youthful expressive 22-year-old engineer with subtle stubble and bright **green** eyes, full **tousled dark copper/brown hair**, brass sealed aviator goggles with teal lenses worn on his head, olive-green rolled sleeves, layered leather harness/straps, aged brass fittings and turquoise-glowing technical devices. Match the **actual second-panel cast-bible image**, not a stock concept or older buzz-cut. Staff remains centered-wrap with twin brass ferrules.
- **Proposed tone in presentation (not a canon rewrite):** warm, credible, quietly confident expertise in older finicky harmonic-levitation engines; capable of dry humor and humility when the Aureate Wake surprises him. Convey technical competence in animation, expression and line delivery, not generic fantasy-hero posing.
- **Cinematic requirement:** believable body scale, non-flat skin and real eye shaders, tangible cloth and metal, intentional staging, atmospheric depth, good foreground/background separation, physically plausible hand contact; approved front/side/three-quarter before field promotion.
- **No generic Genesis placeholder approval:** the DAZ Genesis 9 reference is an intermediate body/rig experiment, not Ender's accepted likeness or final costume.

## Practical native setup when Neontic reconnects

1. **Do not run another editor concurrently.** Ensure exact local branch and minimum free resources from the [First Wake multipath contract](../DataSource/Integration/FirstWakeMultipath.review.json): at least 5 GiB RAM for native work, 6.5 GiB for GPU review, 14 GiB disk; no Live Coding conflict.
2. Restore a clean isolated worktree of this draft (no merge). Verify full UE5.8.4 Win64 Editor compile and the current *exact-head* native automation suite; source-only CI is insufficient.
3. Verify the local 152-bone merged Genesis 9 FBX's licensing and import it into a **new** review package. Existing local private study: `Genesis9_BaseShirtShorts_MergedRig_REVIEW.fbx`. **Do not commit DAZ-origin assets without redistribution permission.** Require 1 SkeletalMesh + 1 Skeleton, 152 bones on *this reference rig*; validate materials, scale, existing skin weights and source hash.
4. Make a **disposable** Blueprint child of `ATSTSSExplorerCharacter`. Assign `EnderSliceReviewBody` to the imported skeletal candidate. Test PIE player possession, WASD/mouse, E interactions, title handoff, input (F6/F9/F7), and expected plot state. Default pawn settings remain unchanged.
5. Capture fixed-camera native **rest → animated raised arm → hidden positive control**. Require body and shirt vertices visibly deform, with no major shoulder/sleeve clipping. Earlier editor-only tests moved hand bones around 74–75 cm but **produced zero changed pixels for actual mesh deformation**; the merged 152-bone skeleton plus real weights were only intermediate successes. Stop on no visual change; test an actual AnimSequence/AnimBP in PIE rather than repeating static PoseableMesh screenshot loops.
6. If animation succeeds, fit approved hair/head/eye/garments and the actual sealed goggles; use explicit headset/skull clearance evidence. Attach the staff to a verified hand bone/socket and require anatomical grip in idle, walk and attack. Only then toggle the visual accessory flags; the new default is false.
7. Perform actual player-controlled First Wake/Pier/ship and shore transitions; check Ender + Ionia before splashdown, Lyra only after explicit recruitment, Reson/Aepex unavailable, Starbourne fail-closed. Validate physical collision and camera occlusion. Capture lit native D3D12 screenshots and short animation proof, archive SHA receipts, and request creator review.
8. **Only after** native/gameplay/cinematic/creator acceptance seek a narrow integration merge. Do not promote a generic Genesis face, an unanimated mesh or a static staff as “finished Ender.”

## Evidence ledger

| Gate | Status |
| --- | --- |
| Pawn-level optional visual interface implemented | SOURCE PRESENT; native compile **NOT RUN** |
| Editor/PIE-only and fail-closed default | SOURCE-CHECKED WHEN CI PASSES; native runtime **NOT RUN** |
| Historical Genesis 9 skeleton import | Previous isolated sandbox **PASS** — not this integrated game |
| Rig optimization | Earlier 578 → 152 bones **PASS** in isolated sandbox |
| Visual body and shirt motion | **HOLD** — hand-bone motion without mesh pixel difference |
| Eye/hair/goggle/style likeness | **HOLD** — earlier creator reference authoritative |
| Staff on hand | **NOT RUN** — component is hidden by default |
| First Wake playable visual proof at this branch head | **NOT RUN** |
| 35 exact-head Win64 native test suite | **NOT RUN** |
| Creator approval / canonical promotion | **NOT AUTHORIZED** |

Source-level validation command: `python unreal/Tools/validate_ender_slice_visual.py` followed by `python -m unittest discover -s unreal/Tools -p 'test_ender_slice_visual_source.py' -v`. CI workflow `unreal-ender-slice-visual-source.yml` is source-only, not Unreal native QA.

## Reusable cast pipeline

Reuse the editor-only mesh/attachment interface and its acceptance tests for Ionia and Lyra **only after** each unique body, rig, hair, outfit and bones are validated; do not simply put Ender's goggles/staff on them. Preserve the approved character dossiers, and keep Reson/Aepex out of the opening party. Refer to [Notion: reusable cast production pipeline](https://app.notion.com/p/413f5bad238b815bb90ec026a16ec6e6).

## Blocker as of November 11

Neontic's connected Remote Desktop Commander devices report **offline**, so the Unreal engine, locally held private FBX, face/head assets, GPU screenshots, and PIE cannot be accessed from this turn. This draft is a **real source change** but not an actual newly playable character render. No claims of native completion or production merger are made.


## 2026-11-11 — Isolated source-only V9 copper hair attachment (unapproved)

The existing PIE-only player character gains a disabled-by-default, collision-free, head-bone-mounted static hair property (EnderSliceReviewHair, bShowEnderReviewHair, EnderReviewHairLocalOffset). The preexisting private V9 copper-hair study is NOT the creator-approved finished hairstyle and is never assigned automatically by the game mode. Blueprint must opt in explicitly. The source-only negative gates protect default invisibility and require an actual head-bone attachment. No native build, visual clearance, deformation, or art acceptance on this new branch is claimed. No ship, party, save, release or production main changes. Do not redistribute private DAZ-derived packages.
