# First Wake cinematic shot plan (review-only)

Source: `FirstWakeShotPlan.review.json`. The numbered FW-CIN-01..10 entries are
a **proposed** art-direction and native-capture contract, not Unreal LevelSequence
assets, creator-approved art, finished gameplay or a rendered film.

## Authority and usage

- First Wake's opening order remains Ender, Ionia, then Lyra and Talen **after**
  actual sea landing; Talen is non-playable. Reson and Aepex do not join here.
- Ender diagnoses the older harmonic levitation system; Ionia commands the
  launch. Preserve the unanswered fuel mystery and Starbourne restriction.
- Per-shot lens, framing, lighting, VFX and movement are **review proposals**.
  Do not replace creator-approved ship/character designs with placeholder art.
- Keep the distinct Prelude / Chapter 1 Act 1 boundary.
- Capture only in Unreal Engine 5.8.4 with exact Git SHA, map/content hashes,
  RHI, lens/exposure, original native screenshots/clips and reproduction steps.
  Side-by-side human assessment is mandatory for visual acceptance.
- No static concept, SpriteCook atlas, generated image, source check or
  screenshot from an earlier commit constitutes native-render approval.
- Physically witnessed stable flotation requires >= 2.0 seconds of continuous
  valid **pre-transition world-time** observation; the source validator does
  not replace the independent native water-frame witness.

## Source-only tests

Run `py -3 unreal/Tools/verify_first_wake_cinematic_plan.py`, then
`py -3 -m unittest discover -s unreal/Tools -p 'test_*.py'`.

Until a real native visual pass exists, retain `final_art_verified=false`,
`creator_accepted=false`, and `evidence=[]`. Record actual captures in a
separate evidence ledger with verified hashes; never invent results.

Master acceptance: [First Wake v0.2](https://app.notion.com/p/3ecf5bad238b8103b313f79ea816a9b5).
Engineering owner: [TSTSS issue #754](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/754).

## Story-to-shot source handoffs

`FirstWakeRuntimeShotHandoffs.review.json` maps the ten proposed cinematic
shots onto the actual `ETSTSSFirstWakeBeat` enum, engineering inspection
mask and `UTSTSSWaterLandingGate::Observe` contract. The mapping carries
conservative earliest/latest *review* states and does **not** let a cinematic
advance gameplay, recruit later party members or synthesize water evidence.
The actual source validator also refuses removal of the stable two-second
pre-transition witness and replay-generation boundaries.

Run `py -3 unreal/Tools/verify_first_wake_shot_handoffs.py` and
`py -3 -m unittest discover -s unreal/Tools -p 'test_first_wake_shot_handoffs.py'`.
The combined source suite and GitHub source preflight also include these checks.

The handoff is **design/source metadata, not** a LevelSequence, an Unreal
runtime cue dispatcher, a playable route, a native render, or evidence of
human approval. Those are separate gates of the master VS matrix.
