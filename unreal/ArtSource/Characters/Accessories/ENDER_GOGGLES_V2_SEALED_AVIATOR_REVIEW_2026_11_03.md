# November 4 native development update — supersedes the November 3 pending status

The November 3 note below was correct *before* the native import. **V2 is now reproduced on NEONTIC and successfully imported into an isolated UE 5.8.4 review project, with three genuine native GPU screenshots.** See the [full reviewed V2 native evidence report](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/0016a2c53f0e5ff785f2053a278f6b0fa229523c/unreal/ArtSource/Characters/Accessories/V2Sealed/ENDER_V2_NATIVE_DEVELOPMENT_2026_11_04.md).

- **Actual native StaticMesh import:** PASS, one mesh, 11 slots, 19.2×8.02×19.171 cm imported axes, without changing V1 or Ender.
- **Native temporary orientation/placement:** PASS only for correct world axes and 79-point outer bounding-box proximity. Physical fit and hair/strap clipping **not proven**.
- **Native GPU render:** three real V2-and-Ender V5 views PASS technically: above-brow front, 3 cm lower front, lower three-quarter. Images remain private on NEONTIC; evidence receipts and source committed.
- **Creator and production holds:** brass overexposed, green lenses dark, face likeness and hair unfinished, no approved physical fit, no production rig, no game/canon promotion. The V1 design remains explicitly **rejected as glasses**, despite its historical technical evidence.

The newer generator is committed to `Accessories/V2Sealed/ender_aviator_goggles_v2_generator.py`; its NEONTIC rebuilt GLB has the same mesh/material/bounds counts as the originally delivered source, but different serialization SHA. The executable native import, three GPU capture scripts, regression tests and exact receipts are under `Accessories/V2Sealed/`. Prior text stating “not staged on NEONTIC” or “native import unverified” is **historical, not current**.

---

# Ender goggles corrective design — **V2 sealed aviator prototype**

**2026-11-03; draft review art; not canonical.** The creator rejected the existing V1 candidate as **glasses**, not goggles. V1's prior static Unreal import and V5+goggles screenshot prove only that *V1* rendered; they do not constitute approval of a goggles design. Preserve its evidence and do not silently rebrand it.

## Newly built outside Unreal, independently validated as real 3D geometry

A **new** complete 3D GLB was generated from original procedural source (not an image-only redesign). V2 uses: two deep enclosed optical barrels (approximately 5 cm face-to-lens), inner padded elastomer seals, metal lateral wind guards, curved emerald glass lenses, reinforced bridge, patinated brass/gold rims, and **one continuous 27 mm-wide leather/fabric headband passing behind the head**, with stitched edges, side buckles, and padded junctions. **No thin spectacle temple arms remain**. The creator's facial reference image, source V5 MetaHuman asset, color locks and game remain unchanged.

**Artifact verified in a separate local 3D runtime:**
- Original V2 GLB filename `Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb`; SHA-256 `e46af39346a953c36c010e6f103ff700b8d13ed32a41cf44c0af3b69f0c296d0`.
- One glTF mesh, **11 physically distinct material primitives**, **57,288 triangles**, 29,792 vertices; no skin or animation.
- Source units meters, +X horizontal, **+Y lens-forward**, +Z up. Full approximate model dimensions **19.20 cm width × 19.17 cm front-to-back including strap × 8.02 cm height**.
- Materials: aged brass, brushed gold, patinated bronze, dark/edge leather, elastomer seal, emerald glass, turquoise accent, dark iron, waxed fabric and stitching.
- Geometry-loader round trip passed; separate front, 3/4, side and three-view VTK previews were rendered **directly from the V2 GLB**, not synthesized from text or captured in Unreal.
- Editable generator Python and guarded UE5.8 import helper were packaged with GLB, preview image, JSON source validation and README as a private conversation deliverable. The new binary/source is **not yet staged on NEONTIC** or checked into GitHub. This GitHub note is an audit record, not the asset itself.

## Fail-closed next development slice

1. Transfer the exact user-approved, SHA-bound V2 GLB to the authorized workstation; do **not** overwrite V1. Use a uniquely named candidate folder in an isolated content-only Unreal project. Guard for the exact SHA above; import one StaticMesh with 11 materials and validate scale and axis conversion. **Native V2 import: NOT EXECUTED / NOT VERIFIED.**
2. Use the previously validated `SceneCapture2D → RenderTarget` method for a native front and side 3D screenshot, including view of the continuous strap and deep eyecups. Do not claim V2 native screenshot until actual image receipts exist.
3. Visually inspect against the **earliest creator-approved Ender face**. Evaluate facial proportions, forehead/eyebrow position, inner seal/head clipping, apparent width, hair clearance, lens tint and side coverage. A source-level fit is not enough: no rig attachment, author acceptance or game promotion until actual proof exists.
4. Maintain the original MetaHuman Core Data/Epic authentication and production-rig HOLD. Keep all V2 and V1 art review-only, draft, unmerged.

**Status:** `V2_TRUE_SEALED_GOGGLES_3D_SOURCE=PASS`; `V2_OFFLINE_MESH_PREVIEW=PASS`; `V2_NATIVE_UNREAL_IMPORT=UNVERIFIED`; `V2_NATIVE_RENDER=UNVERIFIED`; `V2_FACIAL_FIT=UNVERIFIED`; `V2_CANONICAL_APPROVAL=HOLD`.
