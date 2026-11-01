# Protagonists — creator character and visual authority

**Purpose:** make creator-locked identity/art details available to agents working without Notion. This **supersedes the blanket "hair/eye/costume open" text** in [CHARACTER_ART_DIRECTION.md](CHARACTER_ART_DIRECTION.md) where explicit creator locks below exist. It does *not* imply that all in-game art has passed review.

## Known group-image identification

For the creator-supplied five-person group references (nighttime airship and daytime solarpunk) and derivative turnaround/action concepts, **left to right = Ionia · Ender · Aepex · Lyra · Reson**. Incorrect generated labels **Elsie, Jax, Rhys, Lira, Marco** must not be used. These reference sheets **are not automatically accepted atlases**, final costumes or permission to overwrite individual dossier canon.

## Character locks and production caution

| Character | Creator-established characterization / appearance | Avoid |
|---|---|---|
| **Ender (22)** | Protagonist, Rift Scholar: youthful/slender adult; **short auburn/dark copper hair, bright green eyes, brass forehead goggles with green lenses**, olive vest, cream short-sleeved embroidered shirt, dark trousers, brown boots and leather satchel; carries an **unshortened full-length staff** with wrapping at the *longitudinal midpoint* and brass ferrules. Curious/anxious/idealistic, studies boundaries and anomalous correspondences. | Generic wizard costume, muscular adult hero, arbitrary weapon shortening, wrong grip/strap, unapproved changes to approved full-body likeness. |
| **Lyra (24)** | Long **red hair**, adult sensitive listener to frequency/dream phenomena; unusually receptive, not merely the only person who can use magic. **Mother of Talen (5)**, with independent aspirations and agency. | Short/other-color hair without approval, childlike proportions, generic forest priestess or fully resolved job/magic identity. |
| **Ionia (28)** | **Long curly blonde hair is required**. Default hair may be down; a partial pin-up or a full captain's updo is allowed when the recognizable natural curls, blonde tone and same face remain visible. Young but seasoned Captain of the Aureate Wake, Lyra's cousin, warm caretaker and practiced navigator; navy/white/gold uniform is current visual production direction; **green eyes required in the aligned native source candidate**. Ship entrusted by Denith after 10 years' service. | Shortened/straightened default hair, a completely different face between hairstyles, elder/farmer caricature, blue-iris candidate left uncorrected, automatic promotion of one-frame sprite / assumed caster role. |
| **Reson (25)** | **Tallest** protagonist, broad and powerfully built, youthful military-athletic weapon master; rifle-type firearm, pike and sword, ex-military, gruff with a heart of gold. Socially extroverted, confident and playful (not a shallow jock). | Elderly scarred brute, frail/mage-first silhouette, made-up military insignia or service branch. |
| **Aepex (27)** | **Second-tallest**, taller than Ender; angular **sharp undercut**, visible tattoos; lean/lanky muscular technical specialist, inventor, computers/interfaces/diagnostics as well as mechanics. Confident and relaxed; reserved, dry humor versus Reson's outgoing swagger. | Frail recluse, generic mage/mechanic, omission of information technology, invented signature weapon/job. |

**Relative height, tallest to shortest (creator-locked):** Reson > Aepex > Ender > Ionia > Lyra. Never derive exact heights from a perspective-distorted composition.

**Ender source-of-truth image:** approved creator appearance in [PR #261](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/261), exact source proof [at committed SHA](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/1e54efdc313067c7361a74438fda201112167cca/art-staging/field/ender/approved-appearance-20261008.png), SHA-256 `619517944ebe12b295bf5f780abb1a49bce2449230654fb8c49b11e8380546fd`. A checked-in image is evidence of a referenced appearance, **not permission to declare later animation/costume variations approved**.

**Sprite continuation:** draft [PR #262](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/262) staged candidate walk/action strips. Walking needs clear near/far leg phase progression and seamless contact cycle; back carry needs full staff length, centered wrapping, end-ferrules, ankle/boot clearance, believable retention and drawing/return transitions. Six static poses do not prove movement continuity. Art readiness remains **NOT_READY** until genuine Godot-scale playback + creator review.

**Ionia native art:** original source in stacked native review [PR #307](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/307) is a **single-frame candidate**, not final multi-direction sprite/animation. Verify green-eye rendering, source provenance and 64×96-ish intended logical gameplay readability before upgrading. Existing pixel/vector placeholders should not be described as accepted high-fidelity art.

**Talen (5):** precocious, enjoys how the ship works, blocks, drawing and painting. Preserve personhood, curiosity and routine. Do not invent powers or portray him as a normal playable battle mage.

## Level 1 gameplay stat rankings (separate from visual canon)

The creator has locked strict relative starting combat-stat rules: **Ender has the highest MAG and MP; Lyra the second-highest MAG and MP; Lyra the lowest HP; Ender the second-lowest HP**. The other three each begin with less MAG/MP than Lyra and more HP than Ender, without an established internal order. See [the implementation reconciliation and acceptance inequalities](LEVEL_ONE_STAT_RANK_CANON_2026_11_01.md). **No numerical MAG/MP/HP values are locked**; generated character-sheet numbers must not override this design contract. Narrative Five Lights do not automatically grant executable spells or bonuses.

## Approval and visual test

Keep original layered source, consent/provenance, conversion pipeline, per-action frames/hashes and candidate status. Require side-by-side at native logical size, readable foot-grounding/collision, noninterpenetrating occlusion, plausible gait, matching light and texture, motion playback, and creator visual signoff. A CI green check is **not** a style pass.

## Sources

[Notion character-art contract](https://app.notion.com/p/3e2f5bad238b8109b13ce1328d65910c), [Notion art library](https://app.notion.com/p/3e3f5bad238b81999b97cd821db6603b), [dossiers directory](https://app.notion.com/p/3e0f5bad238b812bac52c594d1465c29), [art recovery](https://app.notion.com/p/3fef5bad238b81358ee3e85a1fc27467), [repo existing character contract](CHARACTER_ART_DIRECTION.md).
