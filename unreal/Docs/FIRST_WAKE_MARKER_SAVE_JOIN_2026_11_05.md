# First Wake: passable markers + isolated F6/F9 review saving — November 5, 2026

**Status:** source integration candidate only; do not merge, approve art, release, or claim playable completion.

## Exact provenance and authority

The new `review/ue58-firstwake-marker-save-join-20261105` branch is based on [draft #770](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/770), exact base HEAD `2e930d4d67e0c3efc8c583957bf1d073fbd36516`, which incorporates the source-locked [#769](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/769) F6 PIE isolation/First Wake objectives and the native Prelude map QA admission fix. This branch selectively integrates **only three source files** from [draft #771](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/771) change `dbcb9ae910cd4eefffc9ec76fe5a0b0f02357e57`: `ATSTSSMilestoneActor` constructor, `BeginPlay` collision policy and related native contract assertions. It deliberately does **not** transplant #771's earlier unsafe F5-in-PIE handling or unrelated standalone PIE diagnostics.

### Integration rationale

The first three native real-input milestones (Flyer, Ionia, Boarding) had already been observed on a separate review head. A **separate** #771 GUI session's log reports all seven ordered real E interactions through engineering signoff, with Lift/Pressure/Reserve mask 0→1→3→7. This **does not verify the new integration candidate**. #771 directly fixes pawn movement obstruction from map-serialized BlockAll milestone meshes. The gameplay still needs to preserve visibility-line-trace targeting and 300 cm pawn-to-impact reach, wrong-order denial, and genuine state ownership.

The new combined branch is designed to retain #770's **PIE F6 isolated SaveGame slot, intentional absence of an F5 gameplay-save binding in PIE, guarded F9 load, original seven-marker V2 map, and read-only exact-head gates**, while adopting the #771 pass-through `QueryOnly` collision behavior for the marker meshes in both newly constructed and serialized review actors.

### Source safeguards

Only a single explicitly named disposable join root `TSTSS_MarkerSaveJoin_20261105` is added to inner map-QA/outer launcher/PIE read-only readiness allowlists; wrong SHA, renamed-suffix checkout, dirty Git, existing saves, concurrent Editor/LiveCoding, minimum 5 GiB native / 6.5 GiB GUI free RAM and minimum 14 GiB disk still fail closed. Native map QA remains read-only. No original map, shipped UE config, story canon, Starbourne gate, combat formula, approved art or existing player SaveGame is changed.

The local join checkout is **sparse/source-only to conserve disk**, so a successful source test in this checkout is **not** evidence that the full UE project can compile or render there. **Before any exact-head native QA, expand to the complete required source/content tree, verify the original map hash, build Win64 UE5.8.4 and execute all 29 registered native automations at the JOIN head, and produce fresh independent map-QA receipts**. Parent/other-branch native successes do not transfer.

### Known evidence and next work

- #770 parent: 273 source checks, Win64 native build, 29 automations and seven-marker native map readback PASS at its own source head. Actual later F6 keyboard smoke produced exactly one isolated 1,995-byte review save and F9 feedback; changed-state restore remains **NOT ESTABLISHED**. Shift+F5 produced zero save writes but did not stop PIE in that observed session. Normal red toolbar Stop did stop PIE safely.
- #771 sibling: seven ordered marker E accepts reported in real UE5.8.4 PIE log at #771 source. Verify source custody and independent receipt before upgrading it beyond a narrow diagnostic observation.
- JOIN branch: source-level integration only until new exact-head native and P01–P13 PIE evidence exists.
- Next acceptance: expand disposable join environment only when other Unreal Editor sessions are idle and disk/RAM admission holds; verify full native build, 29/29 automations, seven real marker readback, then actual **seven-stop** WASD/E/J and **save at objective A → advance E to B → F9 restore objective A** in one fresh empty-save PIE workspace. Distinctly test game restart persistence and genuine Skyborne→Seaborne hull contact separately.
- Art review remains a separate P0 requirement: cinematic Ender/Ionia, Aureate Wake four-form geometry, physically lit ocean/sky, no mirrored caption labels and real native GPU images. Do not confuse Shader Complexity screenshots or placeholder assets with approved art.

No protected-main merge, dependency upgrade, model inference session, binary asset promotion or Starbourne unlock authorized.
