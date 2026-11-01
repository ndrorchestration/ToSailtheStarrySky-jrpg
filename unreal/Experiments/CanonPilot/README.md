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
