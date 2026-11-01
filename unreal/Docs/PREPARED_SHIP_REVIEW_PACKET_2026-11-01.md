# Prepared Aureate Wake review packet: source gate (2026-11-01)

**Status:** Offline recomputation verified; noncanonical review; no native art acceptance.

This source-only gate is stacked on draft PR #645. It does not change default ship meshes, First Wake story, waterline physics, saves, Godot fallback, or levels. It uses Python and Git already on the machine. No installation or Unreal Editor execution is required.

## Read-only run

Local packet: C:\TSTSS_Unreal_Windows_QA_PR644\unreal\Saved\ReviewPreparation_e06f393

    python unreal/Tools/verify_prepared_ship_review.py --packet "C:\TSTSS_Unreal_Windows_QA_PR644\unreal\Saved\ReviewPreparation_e06f393"

The packet is pinned to source SHA e06f393edb0b13319c6c19dc085a1217aa3da2e8 and includes the corrected 280 cm wing GLB, its PNG and hash manifest, the 100 cm root-support GLB and its hash manifest, and a 6-transition/126-pose saved clearance receipt.

The verifier does not write files. It checks path containment, hashes, noncanonical review status, meter scale, source ancestry and exact reviewed-file drift. It recomputes 900-points-per-primitive / 20-step ordinary-form clearances, demands exact equality with the saved receipt, and inspects the four 1920x1080 camera definitions. Windows PowerShell 5.1 writes the saved clearance JSON as BOM-marked UTF-16LE; the verifier also accepts UTF-8 without converting the preserved artifact.

## Measured offline results

- 4 wings, 6 directed transitions among Skyborne, Seaborne and Submersible, 21 time samples per transition, 126 sampled poses
- 1,240 sampled vertices, 19.94 cm minimum proxy-AABB separation, 189.85 cm minimum interwing-AABB separation
- Authentic wing and support hashes and exact unmodified reviewed source confirmed
- Four camera definitions, not four generated screenshots

Independent default-budget recheck (3,325 points) produced the same separation margins, but the saved receipt uses the 1,240-point recipe. This verifier replays the exact saved recipe.

## Limitations and gates

- Sampled AABB separation is not continuous swept-volume clearance, engine collision, or physical flotation proof.
- The temporary hull/bridge geometry is not production art. The approximately 28 cm root-to-hull visual gap remains unresolved.
- There is no native Unreal imported mesh, cinematic render, shader approval, gameplay playtest, packaging or creator visual acceptance in this packet.
- Orbiter remains locked. The ordinary-form checks do not authorize lunar or hidden-mode paths.
- Noncanonical review meshes must not be promoted as approved character/ship production art.
- The packet is stored under Saved/ and is not committed; no main merge or release is authorized.

## Testing

    python -m unittest discover -s unreal/Tests -p "test_prepared_ship_review_packet.py" -v

The isolated regression tests exercise receipt encodings, forged measurements, path escape, camera tampering and source-provenance drift. Follow with full offline Unreal source tests before committing any changes. Draft PR reviews remain required.
