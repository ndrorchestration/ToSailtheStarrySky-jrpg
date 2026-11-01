# Aureate Wake V2 — approved-direction procedural art study (NOT final art)

**Creative authority:** Creator-approved `Aureate Wake_ Four Configurations.png` (1536 × 1024; SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`). The original is the visual reference. **The generated 3D models are not artistically approved, canonical, rigged, or production-ready.**

## Why V2 exists

Actual Unreal 5.8.4 ship screenshots from [draft PR #655](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/655) demonstrated four cyan/gold wings attached to **rectangular gray placeholder hull/bridge geometry**. [Draft PR #664](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/664) introduced a separate tapered procedural hull and geodesic dome, but its dark graphite color was not aligned with the now-approved **ivory/pearl, gold/brass and deep navy** body design. This V2 is a small reproducible lookdev adjustment **within the same review-only lineage**, not a claim that the final hull has been modeled.

## Source implementation

- `unreal/ArtSource/ShipReview/build_aureate_fidelity_v2.py` generates `AureateWake_WhiteGoldHull_V2_REVIEW.glb`, `AureateWake_BlueGlassBridge_V2_REVIEW.glb`, and their SHA-256 manifest.
- Surface material slots for hull: **pearl ivory enamel, warm gold filigree, deep navy engineering**. Adds mirrored navy aft engineering pods, fine gold nacelle rails, small blue side insets, and forebody bow-intake details. Existing body envelope, four wing anchors, and small forward-deck panel remain provisional.
- Dome: **translucent blue glass, gold geodesic ribbing, navy lower collar**, with additional discreet framing. No claim of pressure-sealed geometry, crew walkability, animated canopy, or actual glass quality in Unreal.
- Original V1 GLBs are **unchanged byte for byte**. A backwards-compatible optional materials argument to the shared glTF encoder enables V2 without changing default V1 outputs, which are pinned by their original SHA-256 values.
- Original approved artwork is **not rewritten, transformed or embedded** into new generated art. Source references its unchanged checksum.
- `unreal/Tests/test_aureate_fidelity_v2.py` checks deterministic regeneration, original two V1 SHA-256 hashes, material color/glass slots, metre-scale boundaries, increased detail, manifest non-approval, tamper rejection and no engine/gameplay writes.

## Deterministic source-only QA

```powershell
python unreal/ArtSource/ShipReview/build_aureate_fidelity_v2.py --build --output-dir unreal/Saved/AureateApprovedDirectionV2
python unreal/ArtSource/ShipReview/build_aureate_fidelity_v2.py --verify --output-dir unreal/Saved/AureateApprovedDirectionV2
python -m unittest discover -s unreal/Tests -p 'test_aureate_fidelity_v2.py' -v
python -m unittest discover -s unreal/Tests -p 'test_aureate_fidelity_v2_intake.py' -v
python unreal/ArtSource/ShipReview/import_aureate_fidelity_v2.py --check --folder unreal/Saved/AureateApprovedDirectionV2
```

Dedicated GitHub CI runs **both V1 and V2** tests and writes review output to a temporary folder. It does not install software or ship binary assets.

## Precise Unreal gate after workstation returns

1. Confirm exact checked-out source commit, no live editor/other worktree conflict, and no existing occupied candidate folders.
2. Run the deterministic V2 generator and independently verify SHA-256, unit conversion `UE centimetres/X forward/Z up -> glTF metres/Y up`, component bounds, normals, and orientation.
3. **Only within an authorized Unreal Editor Python session**, optionally run `import_aureate_fidelity_v2.py --import-review --folder <existing-verified-folder>`. Its distinct V2 review folders must be empty; existing folders are never overwritten. Native StaticMesh bounds (Unreal centimetres, X forward/Z up) are screened and wrong-axis/wrong-scale imports are rejected. A partial import failure requires a manual review of the isolated candidate folder, never automatic deletion.
4. Import the two V2 assets **only into isolated review folders**, never the game-ready actor or approved art library; confirm Interchange materials and glass actually render.
5. Compare matched top/front/side/three-quarter images with the original approved reference for the recognizably **ivory pointed bow, gold details, forward geodesic blue-clear dome and four veined wings**. Check seam/scale with the old wing-root support meshes. Do not inherit screenshots from older versions.
6. Separately verify Skyborne, Seaborne hydrofoils, Submersible partially visible folded wings, animation clearance and crew-scale before proposing model acceptance. **Orbiter/Moon Bridge stay story-locked.**

**Unverified / explicit hold:** Native UE import, material/glass appearance, new screenshots, final art fidelity, pressure protection, physical hydrofoils, real gameplay, continuous swept collision, creator model approval. No main merge, production promotion or release is authorized.
