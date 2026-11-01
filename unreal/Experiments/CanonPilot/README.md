# Pilot C — Canon-as-Code (public-safe / advisory)

Issue: [#676](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/676). This contract is deliberately restricted to *public-safe* facts from creator instructions and existing [character authority](../../../docs/CHARACTER_AND_ART_AUTHORITY.md). The relative order is Reson > Aepex > Ender > Ionia > Lyra. The latter two ordering supersedes an older incomplete public note; no heights or stat magnitudes are invented.

Python 3 / standard library:

~~~sh
python unreal/Experiments/CanonPilot/check_canon.py --self-test
python unreal/Experiments/CanonPilot/check_canon.py unreal/Experiments/CanonPilot/unknown_observations.json
~~~

The included observation envelope has NO measured values and therefore MUST produce UNKNOWN for all seven assertions. Self-test uses generated **synthetic fixtures only** with five deliberately failing cases, an unknown-field case and missing-evidence control.

For native source observations, populate the same keys from an inspected native export, set source_kind=native_receipt and attach an exact 40-digit Git SHA plus evidence location. A matching observation remains MATCHES_REPORTED_NATIVE_RECEIPT_NOT_INDEPENDENTLY_VERIFIED; it never constitutes creator art acceptance. Independent adapters/review are future work.

No restricted moon/postgame details, hidden mechanics, absolute stats, public-approved art assets, gameplay changes or Orbiter unlock. Review-only; merge requires explicit owner review.

## 2026-11-01 — Measured-to-ordinal adapter (synthetic validation complete)

`derive_observations.py` now converts separately supplied measurements into an advisory observation envelope for `check_canon.py`. **The code does not extract measurements from an Unreal build**. Use it only with explicitly labelled, source-scoped data; do not copy the synthetic values in its self-test into production stats or canon.

```sh
python unreal/Experiments/CanonPilot/derive_observations.py --self-test
python unreal/Experiments/CanonPilot/derive_observations.py your-private-measurements.json > your-private-ordinal-observations.json
python unreal/Experiments/CanonPilot/check_canon.py your-private-ordinal-observations.json
```

The input must have `schema_version: 1`, `source_kind` (`synthetic`, `native_receipt` or `not_observed`), and `measurements` fields. Optional sections: five-character `height_cm`, `starting_mp`, `starting_hp` mappings, or `ship` fields from an inspected source. Every measured ranking requires **all five** distinct, finite, positive numeric values. Missing measurements, invalid numbers, or ties are **omitted and therefore evaluated UNKNOWN**, never guessed. In particular, absolute test numbers are not canon. `native_receipt` requires source SHA and evidence location but metadata alone does **not** independently prove the measurement. Generated native-observation envelopes need separate reviewer verification.

The [hosted engine-free workflow](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/workflows/unreal-experimental-qa-review.yml) runs synthetic derivation and missing-evidence controls. Native character meshes, starting gameplay stats, and scene/ship state have not been bound to this adapter, so production compliance remains UNKNOWN.


## 2026-11-01 — First source-bound candidate observation (NOT native)

[Draft PR #643](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/643) retains its five *unrigged lookdev candidate* measurements in `unreal/ArtSource/Characters/Candidates/manifest.json`. The pinned source commit is `d629faae0838fb1116c629bb8cec480899dfc9d9` and the Git manifest blob is `b4e67081c711ef6350b6df612d21756b89b884ea`. Sorted candidate values are **Reson 1.93 m > Aepex 1.85 m > Ender 1.74 m > Ionia 1.68 m > Lyra 1.65 m**. These numbers are **provisional model-generation choices, not approved canonical body heights**.

`check_pinned_cast_manifest.py` verifies the exact blob bytes, five names, valid per-candidate source-asset digest formats and ordinal height order. The `candidate_manifest` evidence class in `check_canon.py` only permits this one pinned source and the one height-order observation; starting HP, MP and ship assertions remain `UNKNOWN`. The check does **not** inspect binary GLB geometry or Unreal import orientation, and cannot establish cinematic likeness. Other candidate manifests require an explicitly reviewed new pin.

The public repo CI job fetches this *separate exact SHA*, uses `git show` to extract the manifest and runs both checkers. [Engine-free GitHub Actions #41345248199](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41345248199) reports all steps SUCCESS after two test-harness fixes: (1) preserving UNKNOWN for unrelated canon facts; (2) keeping diagnostic text off machine-readable JSON stdout. This is an observable source-bound success, not real runtime or art admission.

To reproduce locally from the repo root, if the pinned SHA is accessible:

```sh
git fetch --no-tags --depth=1 origin d629faae0838fb1116c629bb8cec480899dfc9d9
git show FETCH_HEAD:unreal/ArtSource/Characters/Candidates/manifest.json > /tmp/pr643-manifest.json
python3 unreal/Experiments/CanonPilot/check_pinned_cast_manifest.py /tmp/pr643-manifest.json > /tmp/pr643-candidate-observation.json
python3 unreal/Experiments/CanonPilot/check_canon.py /tmp/pr643-candidate-observation.json
```

Expected status: height order `MATCHES_PINNED_LOOKDEV_MANIFEST_NOT_NATIVE_OR_CANON`, six remaining canon assertions `UNKNOWN`. Real native rendered heights, start-of-game HP/MP, and story-authority decisions must be independently reconciled before any further promotion.
