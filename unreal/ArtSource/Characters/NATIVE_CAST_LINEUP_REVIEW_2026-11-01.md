# Unreal 5.8.4 cast intake and static lineup — native review evidence (2026-11-01)

Status: **NATIVE STATIC IMPORT PASS / NATIVE REVIEW-MAP SAVE PASS / VISUAL ACCEPTANCE HOLD**.

## Provenance and isolation

- Exact source: draft [PR #643](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/643) head `63dbfac2ce9f76658229ccb451b7b0269225ba4b` (unmerged, stacked on Unreal foundation).
- Authorized Windows RDC host `neontic`, Unreal Editor **5.8.4-58902052+++UE5+Release-5.8**, with installed Win64 SDK and Visual Studio 2022 Build Tools.
- Clean, independent Git checkout `C:\TSTSS_Unreal_CharacterReview_20261101`, plus separate disposable, *content-only* Unreal test projects under `C:\TSTSS_CastImportSandbox_20261101` and `C:\TSTSS_CastAllSandbox_20261101`. Neither playable Godot nor the actual Unreal game project was modified.
- Source preflight: `TSTSS_CAST_PREFLIGHT_PASS` for all five. Geometry checker PASS: Ender 10836, Ionia 10764, Lyra 11600, Reson 8736, Aepex 9120 triangles.

## Native UE receipts (not simulation)

`UnrealEditor-Cmd.exe` with the built-in Python Script Plugin and `-nullrhi` executed `editor_intake.py` on two separate disposable projects, with exit code **0** both times.

1. **Ender first:** `Saved/CharacterLookdev/ender_native_20261101_a.json`; `IMPORT_PASS_REVIEW_PENDING`; Ender source SHA-256 `d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2`; actual `/Game/ArtLookdev/Characters/Ender/Ender/StaticMeshes/Ender.Ender` and on-disk `.uasset` verified.
2. **Five-character pass:** `Saved/CharacterLookdev/five_cast_20261101_a.json`; `IMPORT_PASS_REVIEW_PENDING`, exactly Ender, Ionia, Lyra, Reson, Aepex; all five `StaticMesh` asset files verified. Native bounds in centimetres (X, Y, Z): Ender 56.316/31.600/185.800 (staff-inclusive), Ionia 54.412/31.100/166.552, Lyra 52.416/32.200/163.578, Reson 69.384/31.100/191.336, Aepex 58.404/31.100/185.184.
3. **Lineup stage:** `stage_cast_lineup.py` on the five-character disposable project: `Saved/CharacterLookdev/cast_lineup_stage.json` reports `STAGED_STATIC_REVIEW_ONLY` and contains five named static actors, an engine-cube 180 cm calibration marker, and map `/Game/ArtLookdev/ReviewMaps/TSTSS_CastLineup_Review`. The actual `.umap` was verified on disk; UE command process exit code **0**. The tool validates receipt/source hashes, native asset paths and immutable map/receipt destinations before stage.
4. **Engine-free regression:** `python -m unittest discover -s unreal/ArtSource/Characters -p test_stage_cast_lineup.py -v` — **9 PASS** on Windows, including rejected source mutations and canonical height-order violations.

## Canonical relative height authority — creator correction 2026-11-01

**Tallest to shortest: Reson > Aepex > Ender > Ionia > Lyra.** This is *canon*. The current source's intrinsic model choices (1.93, 1.85, 1.74, 1.68, 1.65 m respectively) respect the ranking but exact numbers are **not canon**. Never infer Ender's height from the top of his 1.84 m staff. The lineup validator uses the intrinsic per-character source metadata rather than the maximum bounds of props.

## Reproduce on a new disposable UE project

1. From this PR source, run `python unreal/ArtSource/Characters/editor_intake.py --preflight-only` and `python unreal/ArtSource/Characters/check_cast_geometry.py`.
2. Create an **empty** UE 5.8.4 content-only project with the built-in Python Script Plugin enabled.
3. Set `TSTSS_CAST_IMPORT=all` and a new `TSTSS_CAST_SESSION` label. Run `editor_intake.py` from Unreal Editor Python scripting. Confirm exact five imported assets and saved receipt.
4. Set `TSTSS_CAST_INPUT_SESSION` to that label; execute `stage_cast_lineup.py` from the Editor. Never run on a live/production map or a project containing the reserved review map path.
5. Open the created review map in a **renderer-enabled** Editor session; compare front, profile, back and three-quarter likeness/costuming/materials against the actual approved illustrations. Screenshots must show the exact source SHA and UE version. Apply artistic review separately.

## Remaining HOLD

`-nullrhi` verifies the native asset and map pipeline but **does not render** images. No cinematic 3D likeness, facial/hair sculpt, rig, skin weights, locomotion, staff grasp/draw animation, performance/LOD or gameplay integration is verified. Current models remain intentionally rough static candidates, not approved 3D character art. Preserve the existing Ender copper/auburn versus October 30 group-sheet green hair discrepancy for creator visual resolution, and retain Ionia's long curly blonde hair direction. Do not merge into main, overwrite approved source art, or change First Wake narrative/gameplay.
