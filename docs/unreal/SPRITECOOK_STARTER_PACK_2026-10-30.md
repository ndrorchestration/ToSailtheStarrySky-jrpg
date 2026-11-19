# SpriteCook Unreal Starter Pack — 2026-10-30

Status: **GENERATED / CONCEPT REFERENCES ONLY / NOT IMPORTED TO UNREAL / NOT VISUALLY APPROVED**.

## Ownership and budget
- SpriteCook project: `7b509eda-4250-4093-a31b-98f7af5f1220` (To Sail the Starry Sky — Unreal Starter Assets).
- Three 1024×1024 HD PNG atlas assets, 8 free credits each (24 spent; 16 remaining at generation time).
- Model: `gpt-image-2.5-flare`, `pixel=false`, quality medium, 1K, square.
- Recover current downloadable URLs from SpriteCook asset metadata; signed content URLs expire. Do not store ephemeral signed links in git.

| Asset | SpriteCook asset ID | Intent |
|---|---|---|
| Shipboard props (3×3 concept sheet) | `8d97b498-7641-44e9-a15a-289b69452ace` | Engine, wheel, gauges, staff, tuning fork, lantern, winch, chest, compass |
| Five Lights + resonance VFX (3×3 sheet) | `9e147ac4-bc67-4e33-836a-67cf56b91e8f` | Niagara reference: Spirit/Earth/Water/Fire/Air, ship levitation, aurora, sea splash, moon alignment |
| First Wake materials (3×3 concept sheet) | `f5fd7d4a-2eb2-42d4-8709-78699426bf50` | Material studies: ocean, deck, brass, bridge glass, ceramic, sailcloth, rock, sand, aurora |

## Canon protection
Creator approved the current cast artwork on October 30, 2026; **never replace it** with newly imagined SpriteCook likenesses. Ionia retains long curly blonde hair (updo permissible). The cast's Five Lights affinities are **narrative, not automatic combat magic**. Ender's staff retains centered wrap and brass ferrules. The vessel is the **Aureate Wake**. These atlases are explorations of props, effects and materials only; source details must be checked against the latest approved cast and ship visual references.

## Unreal 5.8 integration plan
1. Retrieve PNGs using SpriteCook owned asset IDs; archive unmodified originals with SHA-256 and attribution metadata.
2. Inspect sheets manually: these are whole composite images, **not** nine validated transparent isolated textures. Segment source imagery conservatively if useful; reject warped, mislabeled or merged cells.
3. Import isolated prop images to `/Game/TSTSS/Art/Reference/Props/` as 2D reference only. Model and rig actual props/ship in 3D with proper UVs, normal/roughness/metallic maps and LODs.
4. Use VFX sheet to art-direct Unreal Niagara emitters; create separately authored sprite flipbooks/materials. Never misrepresent a sheet as production-ready VFX.
5. Rebuild physically-based materials with verified tileability and proper shader maps; sheet samples are not guaranteed seamless.
6. Prototype in an isolated Unreal test map; compare against creator-approved art and First Wake runtime captures. Preserve Godot main and Unreal bootstrap PR #608 until native UE compile/render proof and human visual approval exist.

Acceptance: verified original files, provenance + licensing check, clean extraction where applicable, UE import/render screenshots, frame-time/material checks, creator aesthetic approval. No executable port or character mesh is delivered by this asset pack.
