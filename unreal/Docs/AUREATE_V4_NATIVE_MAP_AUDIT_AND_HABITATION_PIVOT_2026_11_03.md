# Aureate Wake V4 — native four-map integrity and coupled habitation pivot

**November 3, 2026; Unreal Engine 5.8.4.** All results belong to isolated V4 preview work, not gameplay, SaveGame, released actor, creator-approved art or protected-main merge.

## 2026-11-03 follow-up: named Python automation capture controller (SOURCE ONLY)

A separate reversible review branch, `review/ue58-aureate-v4-registered-gpu-evidence-20261103`, adds `unreal/Tools/run_aureate_v4_registered_gpu_capture.py` and eight engine-free regression scenarios. The new runner uses a temporary sibling UE project descriptor (so the original `.uproject` is untouched), enables only bundled editor Python automation for that attempt, stages a uniquely named `Content/Python/test_*.py` in the disposable sandbox, runs the specific `Editor.Python` test, and requires a matching per-test Automation JSON success PLUS a native receipt/PNG hash and dimensions. Original V4 map SHA, RAM/disk/concurrency/timeout watchdogs and unchanged temporary staging safeguards remain mandatory. No third-party dependency is installed.

**Status: source implementation/preflight only, NOT a verified native GPU execution.** The 8/8 fixture tests passed in an isolated local Python mock layout before push; hosted exact-head CI must be checked separately. The test path registration and actual screenshot task await native UE 5.8.4. Valid PNG evidence would still require independent pixel-content/exposure/atmosphere checks and creator visual acceptance. Do not mark RCV-01 through RCV-09 done or transfer an old image to this head.

## Four-map read-only native audit — PASS

Previously saved V4 review maps were loaded read-only in a single Unreal Editor NullRHI session. Their file SHA-256 digests were checked before and after loading. No actors were moved or saved.

- Native host: NATIVE_FOUR_MAP_READONLY_PASS; process exit 0, native receipt FOUR_MAP_READONLY_NATIVE_AUDIT_PASS. All four maps audited.
- Actor readback: Skybourne 18; Seabourne 20; Submersible 15; Starbourne 14. Each has exactly four persistent, uniquely labeled wing identities and four comparison cameras.
- Mode features: exactly two *named hydrofoil body* actors in Seabourne; blue light rail in Submersible; four separate private static cardinal sail actors in Starbourne. No Starbourne player unlock.
- Shared provisional lookdev placement in every form: hull **(0, 0, 0) cm**, forward dome proxy **(210, 0, 122) cm**, quarters proxy **(0, 0, 60) cm**. These are NOT approved ship design dimensions.
- The first audit failed safely after Skybourne due to a false-positive foil selector that counted Seabourne's two STRUT proxies as hydrofoil BODY actors. The corrected audit uses the two exact foil-body labels. It passed in a new native run, preserving the initial failure log/receipt. No underlying map was changed.
- Private successful receipt: C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\four_map_native_readonly_audit_v2_20261103.json.

## Native common bridge and quarters pilot — PASS

Separate new full-Editor NullRHI map, not one of the four previous mode levels:

- Spawned one *static hull*, one *central pivot parent*, one *bridge child* and one *living-quarters child*: four noncanonical review actors.
- Attached both habitation children to the same pivot while preserving world positions. Applied **17.5° temporary test yaw**, confirmed both moved and their separation remained constant at **218.96118377465902 cm**. Restored zero rotation, verified both returned to their exact pretest positions, and confirmed the static hull stayed unmoved.
- Disabled collision, saved only after restoring the initial pose. Host/native state NATIVE_COUPLED_PIVOT_PASS, process exit 0. New pilot map SHA-256: **03e99b36572d11f5d745c682965b787be84d8b7054bd7beab8fe39c577d95306**. Existing Skybourne hero map remained unchanged at SHA **16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40**.
- Private source receipt: C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\coupled_habitation_native_pilot_receipt_20261103.json.

The pilot shows that the central geodesic bridge and quarters CAN be attached to one mechanical parent and rotated together. It does NOT prove pressure seals, cabin orientation/gravity, authored geodesic structure, continuous swept collision, animation integration in the main C++ actor, approved pivot axis or final form angles. Independent #702/#706 remains draft and must retain its nonfinite rotation safeguards. The pure stdlib review geometry helper validates rigid coupling and rejects nonfinite angles/axes, not replacing native Unreal quaternion or physics checks.

## GPU Skybourne V4 screenshot — STILL HOLD

A resource-safe D3D11 attempt named review04 launched at approximately **7.73 GiB free RAM**, but a bare full-Editor ExecutePythonScript invocation exited before running its queued latent screenshot task. The native receipt remained NATIVE_CAPTURE_REQUESTED_NOT_YET_DONE; **no PNG** was created. The host correctly marked NATIVE_GPU_CAPTURE_NOT_VERIFIED despite engine exit 0. Earlier V4 D3D11 failures remain preserved too.

**Next capture method:** register a named **Editor.Python automation test** and run it through the Unreal AutomationTest framework, rather than relying on a bare ExecutePythonScript process to keep its AutomationScheduler latent callback alive. A separate private Starbourne V2 pipeline previously completed actual named Editor.Python automation and D3D11 screenshot tasks, but that independent proof is NOT evidence of V4 pixel quality. Require >=6.5 GiB free RAM, >=14 GiB free disk, original map SHA, native test-controller success, a PNG's real dimensions/hash and nonblank/exposure checks. Do not repeat bare script invocations without changing the scheduling mechanism.

## Dependencies and next verification

1. Python stdlib scene-plan, geometry, pivot-math and source regression tests run without Unreal. Native map integrity is independent of GPU visuals.
2. The shared-pivot proof should inform an opt-in review-only C++ integration with unmerged #702/#706 after exact-head provenance review; no blind cherry-picks.
3. Get one actual Skybourne GPU frame through the registered automation method, then compare with the approved art and reuse matched cameras across the other modes.
4. Leave separate #724 wing/hydrofoil kinematics, #705 black-sky atmosphere, physical six-route sweeps, final material/crew-scale QA, playable First Wake acceptance and release under their own gates.

User-facing names: Skybourne, Seabourne, Submersible, Starbourne. Legacy serialized internal enum names remain Skyborne, Seaborne, Submersible and Orbiter. **Starbourne private development authorized, player reveal/unlock closed.** All native review binary maps and logs remain private on the authorized Windows workstation.
