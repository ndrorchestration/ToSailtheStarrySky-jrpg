# First Wake — Lyra recruitment and equipment-stage convergence (2026-11-10)

**Status:** SOURCE TESTED / DRAFT / NO GAMEPLAY OR NATIVE ACCEPTANCE.
**Review branch:** `review/ue58-lyra-recruited-stage-reconcile-20261110`, based on [multipath draft PR #799](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/799), source ancestor `de0a6a185fae0c5c17300762d288fa753f39a203`.
**Upstream authoritative change:** [party equipment draft PR #793](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/793), stage logic at `96ecd18cb2e969140f0dc948c658ba10d1990bbb`. The integration head previously carried older two-stage code.

## Correction

- `FirstWake`: only **Ender and Ionia** are available as slice party owners.
- `AfterSplashdown`: the physical landing has occurred, but **Lyra remains unavailable** and retains no automatically granted gear. The two-person six-item fixture remains valid.
- `LyraRecruited`: a separately established recruitment condition may authorize Lyra's three owned equipment slots, producing a nine-item three-character review fixture.
- **Reson and Aepex never become available** in this bounded slice; Talen remains nonplayable. No source code in this draft grants skills, changes combat resource cost, writes a SaveGame, or unlocks Starbourne.

This is intentionally a **pure review fixture stage**, not a substitute for a real dialogue/recruitment event. The actual story transition and persistent party state still need an explicitly authorized, tested Unreal implementation before the playable vertical slice can be considered correct.

## Changed files and evidence

- `unreal/Source/ToSailTheStarrySky/{Public,Private}/TSTSSPartySliceReviewEquipment.{h,cpp}`: port source-level three-stage guard from #793. Keep the existing gear ledger, atomic failure behavior and 35-name C++ automation registry.
- `unreal/Source/ToSailTheStarrySky/Private/Tests/TSTSSPartySliceEquipmentTests.cpp`: preserve existing native test name; assert Lyra denied at First Wake and splashdown, six items remain after splashdown, Lyra admitted with nine items only after separate recruitment, excluded crew denied, and invalid stages fail closed.
- `unreal/DataSource/Integration/FirstWakeMultipath.review.json`: add explicit cross-lane `lyra_equipment_gate` specifying `runtime_recruitment_verified=false` and `automatic_item_grants=false`; preserve previous source/provenance and old review-only asset hashes.
- `unreal/Tools/test_first_wake_lyra_recruitment_join.py`: eight focused source regression/negative mutation tests.

**Local source verification:** 447/447 total portable Python source tests PASS, focused 8/8 PASS, diff check PASS on the precommit candidate. Exact final commit and hosted checks must be collected after publishing.

**Native limitations:** independent Neontic UE5.8.4 Win64 Editor UBT build PASS was recorded on the *prior* multipath head `de0a6a185fae...`. It **does not** transfer to this changed C++ header/source. The prior 35-test native automation launch was halted because another live Editor appeared during the post-build resource gate. Do not claim native UHT, the equipment automation, actual game recruitment, or D3D acceptance for this new branch until exact-head reruns pass.

## Additional review lanes intentionally not copied

The latest #793 also contains a native `UTSTSSPartyGearReviewMountComponent`, mesh/socket tests and its own material/gallery evidence. These are **not** part of this minimal recruitment-state repair; they remain separate review assets, with dependencies and creator fitting still open. The new branch does not overwrite the original equipment manifest or import unrelated binary assets.

## Acceptance after merge review

1. Integrate the three-stage source and focused test suite into an exact-head successor of #799, keeping live contributor branches unmodified.
2. Run hosted source CI and native UHT/Editor build, then the full 35-name native registry including `TSTSS.Equipment.PartySliceStageGate`, only in a clean dedicated idle resource-admitted worktree.
3. Separately implement and replay a player-observed Lyra recruitment choice/event after witnessed physical landing, then bridge that state to party/equipment authorization and SaveGame acceptance. No immediate splashdown auto-grant.
4. Obtain distinct native 3D/rig/mesh-fitting screenshots and creator approvals for gear art before release, and preserve direct observed sea physics, ability and crew gates.
