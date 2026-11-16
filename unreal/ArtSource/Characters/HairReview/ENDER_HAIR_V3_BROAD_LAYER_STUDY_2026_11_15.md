# Ender V3 broad-layer static hair — technical review, November 15, 2026

**Disposition: NEW SOURCE/STATIC 3D CANDIDATE, NOT NATIVE-RENDERED, NOT APPROVED OR GAMEPLAY-READY.** This supplements and does not supersede the rejected/archived V1/V2 hair studies. Do not replace any approved visual authority, production asset, First Wake pawn, Daz source, private MetaHuman or existing Unreal map.

## Art intent and change

The creator-approved November 11 Act 1 Ender portrait (second panel from left) specifies a youthful engineer with **full, tousled dark-brown hair and copper/auburn undertones**, not the older buzz-cut target. Prior V2 native UE5.8.4 D3D11 evidence found thin tangled/wicker-like locks, scalp gaps and an unnatural goggles interface. Those *visual failures are still evidence*, not proof of V3 success. The new generator takes one bounded design step toward broad overlapping silhouette masses rather than dozens of rigid tubular strands. **No source pixels or reference image are embedded.**

- Single **real glTF 2.0 static 3D GLB**, not an image, flat card collage, Unreal asset or skeletal/groom result: `CandidatesV3/Ender_BroadLayerHair_V3_NONCANONICAL.glb`.
- **64 modeled sections**: one continuous scalp/root shell; 24 swept crown sheets; nine asymmetric, brow-aware fringe forms; 18 temple sheets; 12 graduated nape layers.
- **29,280 triangles**, four nonmetallic, matte/dark-copper PBR material groups; measured source bounding dimensions **23.7763 × 23.9919 × 19.7045 cm**.
- Exact GLB SHA-256 **`bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e`**; exact binary is source-controlled alongside source code.
- Source: `generate_ender_copper_hair_v3.py` (requires NumPy; writes only to an existing explicit `--outdir`; refuses overwrite). Independent parser and negative gates: `verify_ender_copper_hair_v3.py` and `test_ender_hair_v3.py`.
- Local Windows source result: **6/6 tests pass**, including GLB structure, material/size and exterior winding checks, immutable SHA, simulated false creator approval, same-host binary regeneration twice and negative existing-output test.
- The general legacy generator is not modified; V1 and V2 GLBs, hashes, provenance and native-rejection history stay unchanged.

## Required native review / nonpromotion gates

1. When the existing Whiteout Unreal Editor has closed normally and Neontic RAM/disk thresholds pass, source-check exact HEAD, GLB SHA, active programs and original MH5 map/face/goggles hashes.
2. Use only a **new isolated native import destination** in disposable MH5 sandbox. Import V3 as one StaticMesh, require exactly four material slots and plausible cm bounds; preserve original V5 MetaHuman face, review map and goggles V2.
3. Obtain real front, left/right profile, three-quarter and rear **Lit** GPU frames against the creator-approved November 11 Ender reference and **V2 negative baseline**, with independent image checks. Inspect scalp/hairline continuity, brow visibility, brass/teal goggles fit, silhouette, roughness/highlights and three-dimensional overlap. Report honest artist judgment including possible rejection.
4. If/when visual direction passes, handoff for **manual DCC sculpt/retopology, strand-card/groom strategy, head-bone attachment, collision/strap clearance, animation/cloth deformation and actual possessed First Wake pawn test**. Never conflate a static GLB with a skeletal character or finished groom.
5. Ender's bright green eyes, approved facial likeness and stubble, olive engineer outfit, centered-wrap double-brass-ferrule staff, Spirit/Five Lights and Resonator class remain separately governed; this candidate changes **hair study only**.

## Explicit limitations

The generator uses a deliberately **approximate unverified ellipsoid scalp**. There is no native MetaHuman dimensional fit, no physical headset/strap contact, no photoreal shader, no animation or gameplay model, no likeness metric and **no creator art approval**. GLB source checks are not evidence of successful Unreal compilation or rendering. Daz licensing and private 3D references have not been redistributed. Preserve **DRAFT / UNMERGED / NONCANONICAL / ART HOLD** until native and human gates resolve.
