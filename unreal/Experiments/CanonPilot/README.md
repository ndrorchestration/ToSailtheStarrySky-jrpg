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
