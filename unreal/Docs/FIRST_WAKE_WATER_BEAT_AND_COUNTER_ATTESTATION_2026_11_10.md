# First Wake P0-3: source-locked water beat and stability attestation

**Review-only follow-up to [draft #783](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/783).** This is an evidence-validator hardening change, **not** a change to the Unreal physics model, buoyancy, save controls, story, actor maps, or the two-second threshold.

## Motivation and bounded correction

The previous read-only native telemetry analyzer already required two seconds of consecutively sampled physics time. However, it did not verify that the samples contributing to that time were actually in the **SeaContact** story beat, and it did not require the native gate's reported stability timer to progress consistently at every accepted frame. Thus a synthetic log could show a credible world-time interval with unrelated beat values or an inert stable counter followed by an unrealistic single jump at flotation.

The proposed validator now:
- Accepts real `Launched (4) -> SeaContact (5)` at the *first* qualifying immersion frame, with **zero** pre-contact time credited; stops its backward window there.
- Requires subsequent qualifying settled frames to be `SeaContact (5) -> SeaContact (5)`, ending in the **single** `SeaContact (5) -> FlotationConfirmed (6)` transition; unrelated beat values stop the observation window.
- Rechecks the native `stable_sec` increments against each directly observed later `dt` (within the existing bound `max(0.002, 0.15*dt)`). It refuses a two-second world clock if the native gate did not report matching consecutive timer progression.
- Keeps every previous fail-closed physical condition (tagged overlap, immersion/geometry, velocity <=25 cm/s, generation, valid frames, real world time, original map and head hash) unchanged.

New **synthetic source tests** cover legitimate 4->5 first immersion, fake 4->4 prelaunch 'wet' frames, and a jump in the stable counter. Existing tests remain.

## Exact-head and native gate

For this isolated draft head: run `python -m unittest discover -s unreal/Tools -p 'test_first_wake_water_frame_validator.py' -v`, the full integrated `test_*.py` suite, and CI. A source-test PASS **cannot** establish that a real Unreal water trace passes.

The separate necessary native gate remains: resource-safe UE 5.8.4 Windows build, registered native tests, actual D3D11 PIE W/E route, **>=2.0 directly observed pre-transition world seconds**, full source/map/log hash custody, restore/New Game negatives and native creator visual approval. At authoring time NEONTIC had only about 2.08 GiB free RAM and an Unreal Editor open, so **no additional Editor or native build was authorized**.

Do not merge this stacked review branch, loosen existing gates, promote provisional ship art, unlock restricted travel modes, or claim the vertical slice playable on source tests.