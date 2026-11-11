# TSTSS three-party equipment rig/socket readiness (review only)

## Verified availability

These are older unapproved static cast candidates from a prior isolated character study; they are not rigged gameplay actors. All three have zero glTF skins and zero animations, so no character bone/socket placement can be established from these sources.

| Cast | Static meshes | Skins | Animations | Mesh height (m; Y-up) | SHA-256 short |
| --- | ---: | ---: | ---: | ---: | --- |
| Ender | 1 | 0 | 0 | 1.858 | d516f68b4930 |
| Ionia | 1 | 0 | 0 | 1.666 | e2df1d205a28 |
| Lyra | 1 | 0 | 0 | 1.635 | ca430c86e0b6 |

The model heights above are source mesh bounding boxes, not approved character stature or proportions. Newer Ender fidelity/hair candidates exist elsewhere, but have not been established as approved gameplay skeletal actors by this audit.

## Implemented socket safety contract

- UTSTSSPartyGearReviewMountComponent::TryAttachToSkeletalSocketsReview is opt-in; requires a registered actor-owned SkeletalMeshComponent with an actual skeletal mesh asset.
- All three requested socket names must be present, nonempty and distinct. All three gear mount components must be registered and owned by the same actor.
- Previous mount parents, names and relative transforms are cached; failed attachments attempt rollback.
- This socket adapter does not grant party recruitment, inventory, skills, class, or persistent SaveGame updates.
- Native negative regression asserts that an unrigged character cannot be treated as a valid skeletal fit.

## Required before art or gameplay promotion

1. Approved rigged and skinned actors for Ender, Ionia and Lyra; weapon, torso and head sockets authored per skeleton.
2. Independently reviewed grip and fit transforms and multi-angle screenshots during animation, not static overlap.
3. Coat cloth/skin deformation, sealed goggles/eye alignment, collision, and material lighting review.
4. Player UI coupled to real inventory ownership and separate Lyra recruitment (not splashdown alone).
5. Native D3D12/PIE proof, exact-head strict full native automation, creator review.

## Full-30 native suite diagnostic (NOT strict-accepted)

Prior head 96ecd18 compiled and its actual NullRHI Unreal suite reported 30/30 Success, zero failed and zero not-run. The strict verifier withheld its final success because the engine rewrote two tracked configuration files. Those files were restored to tracked hashes. A later retry was blocked by the mandatory 14 GiB free-disk requirement. See PartyEquipment_ThirtyNativeTests_Diagnostic_2026_11_10.report.json.
