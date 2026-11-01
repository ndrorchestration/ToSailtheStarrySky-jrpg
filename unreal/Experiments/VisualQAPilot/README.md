# Pilot B — bounded native Unreal Seaborne screenshot verification

Owner: [GitHub #675](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/675). Current source target: draft [PR #656](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/656) (**stacked on #653**), which reports Windows UE 5.8.4 build and 13/13 native + 31/31 Python checks passing. Historical Seaborne PNG SHA-256: `7df11a853a970a5e10c4984a87ff490f5099a84aec13a1711282f4b0873ee302`. It is explicitly a **PRE-strut** screenshot; never use it to claim post-strut rendering.

## Native operator sequence

1. Inspect current PR #656 head and SHA. The template SHA is a *dated snapshot* and MUST be refreshed after comparing with the actual checked-out head. Do not run against the unrelated main branch; current PR #656 native code is stacked.
2. Check that workstation has available Unreal 5.8.4 Windows D3D12 and the isolated review .uproject/.umap and no conflicting editor process. Avoid killing unrelated workloads.
3. From the isolated current-head build with new ReviewHydrofoilStrut components, open the Seaborne review map. Use pinned camera `ReviewCamera`/exact view and make ONE native 1280x720 screenshot; inspect both struts on the real frame.
4. Keep native render command, stdout/stderr, source/build SHAs, component counts, map/camera, UTC timestamp, GPU, engine and screenshot hash in a separate private evidence receipt. If startup stalls, stop only the isolated review process and record NOT_VERIFIED.
5. Copy `capture_receipt_template.json` to a local receipt, populate actual fields, set post_strut_build=true ONLY after verifying actual build/source, and run the bounded read-only checker:

~~~sh
python unreal/Experiments/VisualQAPilot/check_capture.py --self-test
python unreal/Experiments/VisualQAPilot/check_capture.py path/to/actual-capture-receipt.json
~~~

The template is deliberately incomplete and FAILS. The checker verifies PNG header, pixel dimensions, SHA-256, and required metadata, and rejects known old screenshot bytes. **It cannot authenticate D3D12 origin, validate video pipeline, independently confirm source/build SHA, visually inspect supports or certify art.** A checker PASS is therefore only PNG file integrity, with native/visual provenance pending separate operator review.

Never merge PR #656, replace canonical art, override Orbiter request refusal, change story or publicize postgame content as part of this pilot. Later continuous clearance, supporting physics and finished hull/bridge are distinct slices.

## 2026-11-01 — Container-integrity test extension

`check_capture.py` additionally validates bounded PNG structure, chunk lengths, CRC-32 checksums, mandatory IDAT and final IEND, beyond exact dimensions and full-file SHA-256. `test_capture_receipt.py` exercises a fully encoded **Python-generated synthetic PNG** and four rejection cases. The synthetic PNG is **never** a native Unreal screenshot. Passing tests show the receipt checker accepts a structurally valid file and rejects known malformed/obsolete examples; they do not validate pixel contents, Unreal renderer provenance, ship geometry, hydrofoil placement or cinematic fidelity.

```sh
python -m unittest discover -s unreal/Experiments/VisualQAPilot -p 'test_*.py' -v
```

**Remaining true native step:** After the authorized Windows workstation comes online, execute ONE isolated #656 exact-head D3D12 Seaborne review capture, retain build/map/camera and renderer logs, verify both hydrofoil struts visually, and attach a reviewer decision. Current status remains **POST_STRUT_NATIVE_RENDER=NOT_VERIFIED**. Do not use #677's main-based pilot branch as the actual #656 compiled ship source; it only supplies independent verification utilities.
