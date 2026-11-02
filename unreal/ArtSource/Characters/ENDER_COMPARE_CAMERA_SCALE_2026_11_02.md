# Ender V1/V2 three-quarter camera-scale verification (review-only)

Date: 2026-11-02. Engine target: Unreal Engine 5.8.4 Win64, D3D11 SM5.
Authority: October 30 creator-approved cast, approved Ender full-body art, and Character Art Direction Contract. **Neither V1 nor V2 is an approved production model**.

## Scope

Follow-up to draft PR #663. Preserve its exact parent `54428984ead786a554749f88e459292320d6a833`.
The front comparison retains the same perspective settings and original exact PNG bytes.
The three-quarter comparison switches from the unfair single perspective camera to **one 480 cm-width orthographic camera**, shared lighting, same view direction, and source-native +Y forward. The subjects stay at symmetric X=±115 cm, same Y and Z; no mesh, actor, UAsset, .umap, source GLB, SaveGame, First Wake, gameplay pawn, or production art change.

A fail-closed receipt now requires the declared per-camera projection contract.
The independent PNG check additionally measures each three-quarter region's foreground vertical extent and rejects a ratio below 0.88. This is a technical **staff-inclusive** apparent-height gate, *not* evidence of matched anatomy, expressions, proper material response, rigging, creator likeness or art admission. Negative controls cover missing and shortened synthetic subjects.

## Native evidence and limits

Original source material was copied only into `C:\E4\CastAllSandbox` (fresh disposable test project), retaining the existing unrigged V1/V2 native intake receipts. The previously validated V1 and V2 GLB SHA-256 values remain `3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38` and `e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8`.

- Native command: `UnrealEditor-Cmd.exe C:\E4\CastAllSandbox\CastAllSandbox.uproject -d3d11 -RenderOffscreen -unattended -nop4 -NoSound "-ExecCmds=Automation RunTests Editor.Python.CastAllSandbox.test_ender_compare_native; Quit" "-testexit=Automation Test Queue Empty"`.
- Actual Unreal automation: `Editor.Python.CastAllSandbox.test_ender_compare_native` **Success / exit 0**; log `C:\E4\EnderCameraNative.log`.
- Independent repository verifier: `verify_ender_comparison_report.py` **exit 0**, `NATIVE_COMPARISON_IMAGE_INTEGRITY_PASS_NOT_ART_ACCEPTANCE`. Verifies real `Saved/Automation/Reports/test_ender_compare_native/.../Incoming.png`, distinct SHA, pixel content, source receipt hashes, explicit camera mode and unchanged saved map checksum.
- Front `comparison_front.png`: **1280×720**, SHA-256 `350d8453d54aa0283b464caa47814bf8505769e57c99861b0dfe075db13efb5a`, byte-identical to the prior perspective-front native screenshot.
- Corrected three-quarter `comparison_three_quarter.png`: **1280×720**, SHA-256 `90e100eabf4f74c055c3f96a88f9b7b991c76831205a59b81e7bdc289d1053b9`.
- Independent foreground extents: V1 **496px**, V2 **496px**, ratio **1.0000**; both regions visible; per-region foreground ratios **0.1372** and **0.1380**.
- Original and copied V2 review map SHA-256: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`, unchanged.
- Standalone camera-contract / screenshot / safety suite: **21/21 local tests PASS** after an additional synthetic short-subject negative control.
- The E4 live native execution used a source-equivalent checkout with camera-script SHA-256 `e0ed1e312e69f7c8478a87897e9dca039e818954007a2bb2f45cf75a5508f166`. Native execution occurs on the temporary worktree code, not on a packaged/merged game build.

An independent E5 sandbox reproduced **the same image SHA-256 values**, successful native test and unchanged map. A temporary orthographic exposure-bias variation produced bit-identical frames and was **reverted**, so it is not promoted as an improvement. Native evidence stays local to the authorized Windows workstation, not a GitHub Actions native render or published artifact.

## Visual QA observations, not approvals

The corrected three-quarter view permits a fairer **apparent scale** comparison than the former perspective image, but the orthographic rendering appears excessively flat/bright, making facial and cloth nuances difficult to judge. This remains a light/lookdev concern, and the visibility threshold's absence of clipped white pixels does not certify desirable lighting. Even at equal scale, both candidates retain procedural facial anatomy, stiff hair clumps/cards, little cloth thickness, rudimentary staff-hand contact, rigid joints, and placeholder materials. V2's connected waistcoat panels are incremental geometry improvement, not cinematic likeness.

Do not silently select green versus auburn/copper hair; later creator-approved image and individual Ender full-body proof must be reconciled explicitly. Preserve approved green eyes, brass goggles, olive/cream layered outfit, slender adult silhouette and straight two-ended staff with centered wrap and brass ferrules.

## Gate and next smallest art task

- **PASS:** Native isolated comparison execution; per-camera projection contract; both actual PNG checks; staff-inclusive apparent-scale equality; unchanged map and baseline source GLB; 21 local source safety tests.
- **HOLD:** Lighting/material/face visibility and creator likeness; true head retopology; groom/hair physics; cloth thickness/deformation; skeletal mesh; idle/locomotion/combat animation; playable pawn and owner approval.
- **NEXT PROPOSAL:** One separate, noncanonical Ender V3 **head-and-hair landmark sculpt** under the canonical image references. Deliver a head geometry source asset, clear front/side/three-quarter turnarounds under legible controlled lighting, facial landmark notes and hair-color decision flagged unresolved. Require native UE intake/capture, technical mesh check, explicit visual owner acceptance, and a new isolated draft PR. No mesh replacement, game runtime integration, new numerical stats or story changes.

Do not merge this candidate or call the asset production-ready. The prior image, source and official art approval gates stay distinct.
