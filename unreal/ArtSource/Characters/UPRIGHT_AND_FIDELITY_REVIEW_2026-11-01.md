# Unreal cast — upright review display and original-art fidelity workstream

Date: November 1, 2026. Status: **native imported anatomy upright; existing rendered evidence inverted; derived display copies upright; production art still rejected.**

This is an isolated review slice on top of draft PR #647, which stacks on #646 and #643. It does **not** modify a production scene, GLB, Unreal StaticMesh, Godot game, protected main, rig, or art canon.

## The actual problem

The raw native D3D11 screenshots in PR #647 show the characters upside down. An earlier test used only bounding-box extrema and mistakenly treated that as proof of orientation. A trial 180-degree actor roll did not resolve the screenshot evidence. Another 180-degree camera-roll test returned a black screenshot. Neither should be promoted as a valid model/import fix.

The correct test is semantic geometry inside Unreal 5.8.4: find hair and boot-material polygons in the *actual imported StaticMesh description*, read vertex positions, and establish a positive head-to-foot Z relationship. The read-only native check [check_cast_native_landmarks.py](check_cast_native_landmarks.py) passed for all five characters on authorized Windows host neontic. Results (hair median Z minus boots-material median Z, cm):

| Ender | Ionia | Lyra | Reson | Aepex |
|--:|--:|--:|--:|--:|
| +57.61 | +117.53 | +112.92 | +156.47 | +156.23 |

All five have near-zero minimum world Z and hair at greater Z than boot-material geometry. The script writes an explicit saved receipt with Unreal version and NOT-APPROVED flags. These are material-associated semantic checks, not artistic approval or a test of the final screenshots. The exact numerical body heights are not approved canon; **Reson > Aepex > Ender > Ionia > Lyra** is locked.

## Fixed GitHub presentation copies (not fixed camera)

To address the upside-down images *in GitHub*, [derive_upright_review_png.py](derive_upright_review_png.py) creates immutable 180-degree rotated display copies from the original native screenshot bytes. Raw evidence in #647 is unchanged. Four unit tests passed on Windows with Pillow 12.3.0, proving rotation pixel mapping and no overwrite.

- [Ender — upright display derivative](ReviewCaptures/2026-11-01/UPRIGHT_DERIVED_Ender_front.png)
- [Full party — upright display derivative](ReviewCaptures/2026-11-01/UPRIGHT_DERIVED_Five_cast_lineup.png)

These raster derivatives are **not new Unreal renders**. Captured source and corrected output hashes are recorded by the script. Camera roll, +X/+Y front-axis and profile framing still require independent native correction. The screenshots reveal coarse current geometry that remains unacceptable as finished art.

## Six-disciplinary character fidelity crew

Track the [expert workstream in GitHub issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649): native technical artist, character sculptor, hair/costume modeler, material/lighting artist, rigging/animation engineer, and QA/narrative-canon reviewer. The review tasks are not a claim that six autonomous agents are continuously modeling.

Gate high-fidelity work against the actually accessible creator-approved October 30 cast artwork and the Notion Character Art Direction & Implementation Contract. Character-specific authoritative constraints include Ionia's long blonde curls, Lyra's red hair, Reson's tall military styling and mustache, Aepex's sandy-blonde undercut/tattoos, and Ender's green eyes, goggles, practical fighting staff and olive/cream scholar styling. The conflicting Ender hair references remain held. Synthetic visual-bible images must not silently supersede creator-approved specifications.

**Proposed acceptance sequence:** Ender full-body/front/profile render with correct orientation and light; compare to approved closeups; model head/hair/goggles/staff beyond primitive ellipsoids; finish Ionia curls and face and Lyra red-hair face; then Reson and Aepex; then native animation/rig and gameplay tests. Every visual comparison must include exact source and engine SHA, cameras, and an actual legible render. Artistic approval remains creator-controlled.

The existing weekly Starry Sky read-only audit now incorporates these six review disciplines. A separate daily recurring job could not be created because five active automations already occupy the five available slots. The weekly audit is not autonomous ongoing 3D production.

## Native Unreal capture fix — subsequently verified (same date)

**Previous camera/root-cause hold resolved for this isolated review slice.** The original review script constructed camera rotations as positional calls like `unreal.Rotator(0, yaw, 0)`, which bound the intended yaw to the wrong angle. The fix uses explicit `unreal.Rotator(pitch=0.0, yaw=float(yaw), roll=0.0)` for the camera and named angles for lights. Native face-axis geometry confirms Ender's pupil plane is at **+Y ≈ +10.8 cm** ahead of his shirt center near Y≈0; portrait cameras now use the observed +Y facing axis. Non-Ender actors move far away only during isolated Ender captures; their original staging coordinates are restored and temporarily rotated to face the lineup camera. None of these temporary test transforms are saved.

**Verified real UE 5.8.4 D3D11 automation:** `Editor.Python.CastAllSandbox.test_cast_render_review_v10` completed **Success**, five screenshot tasks completed, and five native 1280×720 PNGs passed the independent PNG/decompression/CRC/dimension/nonidentical SHA image gate with exit code **0**. They are distinct, legible, and visibly upright:

- [Native Ender front — corrected camera, no raster transform](ReviewCaptures/2026-11-01/NATIVE_CORRECT_ORIENTATION_Ender_front.png)
- [Native Ender profile](ReviewCaptures/2026-11-01/NATIVE_CORRECT_ORIENTATION_Ender_profile.png)
- [Native Ender rear](ReviewCaptures/2026-11-01/NATIVE_CORRECT_ORIENTATION_Ender_back.png)
- [Native Ender three-quarter](ReviewCaptures/2026-11-01/NATIVE_CORRECT_ORIENTATION_Ender_three_quarter.png)
- [Native five-character front lineup](ReviewCaptures/2026-11-01/NATIVE_CORRECT_ORIENTATION_Five_cast_lineup.png)

The saved original review map still hashes to **`6614a8a8c378f8eada5a8ff2788afae9ca49832e507b27ed942a8076a478b49a`**, confirming the test did not modify it. The standalone test `test_camera_rotator_contract.py` prevents regression to positional angle constructors and is executed in source CI.

**Art approval stays HOLD.** These images demonstrate orientation, lighting legibility, camera framing and nonblank native output; they do not establish likeness to the creator-approved artwork, rigging, animation, high-fidelity materials or game-scene integration. The older upside-down raw images and labeled 180° display derivatives remain as provenance only; these new five PNGs are direct native Unreal captures and supersede the derivatives for technical review. Full character sculpt/rig/motion work proceeds only under issue #649 and the established canon gate.
