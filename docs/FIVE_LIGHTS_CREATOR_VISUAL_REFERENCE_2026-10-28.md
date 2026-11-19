# Five Lights — Creator's October 28 visual reference handoff (candidate authority reconciliation)

**Status:** Creator-selected high-fidelity **appearance target** for future cinematic portraits and field sprite production; **not** authoring-ready transparent directional atlases, approved animation, or a change to narrative/mechanics canon. October 28, 2026. Documentation-only, draft and unmerged.

## Why this entry exists

The creator explicitly rejected the older Godot four-way SVG placeholder designs and their wrong visual identities, and supplied an illustrated five-character expedition sheet, several cinematic images and a newer five-character visual-bible composition. Future visual work must not present the older candidate SVGs as the intended appearance standard merely because Godot CI passes. Preserve the old sources for regression comparisons, not aesthetic default selection.

The selected visual layout **left to right** is **Ionia, Ender, Aepex, Lyra, Reson**. See existing [character authority](../CHARACTER_AND_ART_AUTHORITY.md). The latest provided image references are currently in the creator's project/chat art custody; *they are not yet checked into this public repository* and no SHA-256 for those unstored source files is asserted here.

## Visual targets visible in the creator-supplied references

| Character | Current creator-directed look target | Production cautions |
| --- | --- | --- |
| Ionia | Curly blonde hair, green eyes, youthful adult, layered cream/brown expedition clothing with botanical motifs, leaf circlet and leather gear | Existing source lock describes a navy/white/gold captain uniform. Treat as a **costume-era/variant conflict requiring reconciliation**, not a retcon of Captain Ionia, Denith or the Aureate Wake. |
| Ender | Short teal/green hair, teal/green eyes, forehead brass goggles, green outfit, vial/utility straps and a youthful lean build | Older creator-approved Ender likeness specifies dark copper/auburn hair, a different uniform and full-length center-wrapped staff. This is an **explicit appearance-reference conflict**, not permission to erase that source, shorten the staff, or convert the Rift Scholar into an engineer-only character. |
| Aepex | Tall lean masculine silhouette, tousled blond undercut, visible tattoos, dark layered leather/gear and maroon cloth/scarf | Do not reclassify the systems/invention specialist as a rogue class merely because generated art printed a job caption. Validate against the character dossier. |
| Lyra | Adult red-haired woman, long wavy hair, layered blue-and-cream embroidered dress, warm expressions and small herbal accessories | Preserve adult identity, independent agency, son Talen, dream/frequency sensitivity. Do not turn her into a mandatory healer class solely from illustration labels. |
| Reson | Broad adult masculine silhouette, dark hair and mustache, backward burgundy cap, red scarf, cream sleeves and leather harness | Preserve weapon-master background, physical durability, character age and relative height. The image's pilot/solar-engineer caption is **not** authorized to replace narrative canon. |

The appearance mapping is a **visual production target under creator review**. Earlier creator-locked details remain visible and are not silently deleted; conflicting points must be approved in a single explicit costume/identity revision before the production sprite atlas is called approved.

## Source-art production pipeline (do not skip)

1. Acquire the best resolution individual source layers for these correct five identities; preserve original raw images, acquisition/provenance, source dates, exact checksums and authorized review status. Do not use previous anime-styled Ionia-red/Lyra-blonde candidate atlas references as identity source.
2. **Cinematic dialogue proof first:** five readable high-fidelity portraits; First Wake may show only Ender/Ionia at the right recruitment/story timing. A cropped presentation sheet with parchment backgrounds is a portrait **review crop**, not a transparent field actor.
3. **Genuine high-fidelity field art:** independently author transparent north/south/east/west poses and six or more truly distinct walk phases per orientation, respecting clear anatomy and no mirror shortcuts for asymmetrical hair, gear, staff, scarves or tattoos. Preserve editable working files.
4. **Native Godot quality gate:** imported textures and alpha, 960 × 640 actual GL captures, source identity, adequate sprite visibility, actual collision-travel animation, foot-ground planting, occlusion, directional continuity, realistic material matching, reduced-motion support and native-regression tests.
5. **Gameplay/release boundaries:** no early Lyra, Aepex or Reson recruitment; no spells granted by story resonance; no silent chapter state/save mutation. Windows installer/Defender custody remains an independent release gate. No CI passing code test may be presented as a creator-approved art pass.

## Current engineering scope

Draft [#563](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/563) and [#569](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/569) test native directional motion using **older unapproved** candidate SVGs. They are useful physics/control comparators, **not the correct current aesthetic target**. Do not merge them as final visual content.

A standalone Godot 4.7.2 high-fidelity *cinematic gallery* was assembled from the creator-supplied best available images with five static portrait, expression and outfit references, source-file hashes and an optional **read-only** Ender/Ionia dialogue portrait adapter. This local packaged review material is **not yet in GitHub**. Its static crops are not animated actors. Native rendering and visual signoff on that local project are still unverified.

## Explicit unresolved gates

- Resolve the new Ender teal-hair reference against previously approved auburn source and staff, and Ionia's botanical outfit against the established captain uniform.
- Distinguish aspirational appearance images from approved in-world costume epochs.
- Obtain truly source-isolated, transparent high-resolution motion frames before promoting any five-character field pack.
- Capture authentic native gameplay images and have the creator confirm visual consistency.

**No edits to earlier canon, roster, roles, mechanisms, assets, story, builds or releases in this document-only PR.**
