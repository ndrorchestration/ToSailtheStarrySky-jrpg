# Ender V5 — private first-approved-face candidate QA (2026-11-03)

**Status:** SOURCE PROVENANCE / STRUCTURAL IMAGE MARKS PASS; ARTIST-LIKENESS, PRIMARY FACE SELECTION AND METAHUMAN INDEX MAPPING **HOLD**.

Stacked on Ender V5 native landmark atlas [draft PR #721](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/721) at exact reviewed parent `7425d3cf6ab44afef1d5ee51e02b15a50946f800`, which enforces the creator's **first approved faces preferred** decision. No existing game code, MetaHuman asset, approved concept art or main branch is modified. This is not a sculpt, render, rig or art promotion.

## Confirmed artwork and source priority

The creator's earlier instruction is **"the faces from the first are most correct."** The first approved realistic portraits take priority for facial identity. The later daylight ship-deck group is **secondary for attire, materials, equipment and lighting**, not for eye/nose/chin mapping. The exact primary older face must still be confirmed; this is not permission to select one automatically.

The private original sources are:
- `Aetherwake: Steampunk Skybound Crew.png` (earlier realistic face candidate)
- `Aetherwake: JRPG Character Design Board.png` (earlier realistic face candidate)
- `Ender: Solarpunk RPG Character Sheet.png` (approved individual stylized cross-check)

Their original **exact SHA-256 hashes and original pixel dimensions** were independently checked against the existing `ender_v5_reference_priority.json` inventory in the user's private file collection. The private `Ender_V5_Private_Face_Landmark_Proposals.json` (three crops × four marks) was evaluated without writing any source image or private pixel coordinates into GitHub.

## Deliverable

`verify_ender_v5_private_face_candidates.py` is a **standard-library-only** CLI accepting a private 2D proposal JSON and a local directory containing originals. It requires exact source SHA-256, PNG signature/width/height, four intended image-space landmarks per source, valid crop boundaries, image-left/right eye order, plausible vertical nose/chin ordering, source priority and **all fail-closed non-approval guardrails**. It outputs a *private summary receipt* that contains no proposed pixel coordinates, original image bytes, anatomy labels or MetaHuman native index selection.

Seven synthetic-data regression tests in `test_ender_v5_private_face_candidates.py` reject substituted image bytes, reference-policy drift, recent secondary artwork being promoted to facial authority, fabricated MetaHuman indices/artist approval, invalid crop or coordinate geometry, and source-publication changes. Synthetic tests do **not** independently verify the private originals; those were checked separately through the private file review.

### Private real-source check, separated from public CI

Three original image hashes and dimensions matched the existing approved-source inventory. All 12 provisional image marks were inside the documented crops and passed simple structural ordering checks. The **individual stylized reference** warrants particular manual scrutiny because its eyes follow an oblique line and its nose/chin placement is ambiguous. The private montage and private QA receipt were generated in the current conversation container; **neither is committed to GitHub**. They are visual *review* artifacts, not an approved facial registration or Unreal render.

No native `MetaHumanCharacterEditorSubsystem` face landmarks were modified, selected or semantically registered in this milestone. The existing 79 indices and saved V5 MetaHuman asset remain the previously verified **unmapped** data baseline. Face and hair art remain on hold. In particular, incidental historical ages, labels and height numbers printed on source image collages must not override approved story canon (Ender is 22 and his height rank is Reson > Aepex > Ender > Ionia > Lyra).

## CLI use (on an authorized computer with private references)

```powershell
python unreal/ArtSource/Characters/verify_ender_v5_private_face_candidates.py `
  --private-proposal "PATH_TO_PRIVATE_PROPOSALS.json" `
  --private-image-directory "PATH_TO_PRIVATE_APPROVED_REFERENCES" `
  --output "PATH_TO_PRIVATE_QA_RECEIPT.json"
```

No private art, candidate pixel coordinates, privately generated montage, or native UE binary is required in GitHub. **Do not check in the private input or output.** This script validates provenance and simple geometry, not photographic anatomical correctness.

## Acceptance and next small reversible step

- **Verified:** three private source hashes and dimensions, 12 proposed points inside source crops, source-priority hold and local synthetic negative-control behavior.
- **Unresolved:** artist-authenticated anatomical eye centers/nose tip/chin, perspective/camera metadata, precise primary earlier face, hair-color conflict, semantic MetaHuman index mapping, MetaHuman optional Core Data, true facial-sculpt A/B renders, rig/animation and creator visual signoff.
- **Next:** review and correct the provisional four marks in an **authorized private art session** with the earliest approved realistic images side by side. If one face is selected as primary, register point identity against the native 79-index atlas with explicit pose/handedness verification. Only then create an isolated, reversible MetaHuman facial *edit candidate*; do not touch approved cast or production pawn.

**No merge, release or art promotion.** Keep [art-fidelity issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649) open.
