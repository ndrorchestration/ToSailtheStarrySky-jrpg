# Aureate Wake — native envelope snapshot and source-only screen

**Review only.** This successor builds on commit 84e655382cf4368d1c0c20eb7dfdf4a9b163b3d6, the fail-closed swept-box verifier stacked on #747. It does not change the Aureate Wake actor, maps, game saves, story, or the Starbourne lock. It recreates a bounded implementation because the earlier converter and runner were not accessible; it is not a claim that those files were recovered.

The Unreal recorder reads each StaticMeshActor's unique label, mesh asset path, static-mesh local bounding box, and component-to-world translation, quaternion, and scale. It does not save a map or spawn an actor. The host verifies the isolated V4 review project, UE 5.8.4, exact clean source commit, no competing Unreal/build processes, resources, and input map SHA before launch; it protects the map, project descriptor and default configs during launch and checks them and SaveGames afterward. Output, candidate and log must be new and outside the project and source checkout.

## Native export

On Neontic, use a clean committed source checkout and a new output path in a pre-existing private directory. The only admissible project is the private V4 review sandbox. For the known coupled-habitation map:

    python unreal/Tools/run_aureate_envelope_export_native.py export --map /Game/TSTSS/Review/Scenes/AureateV4_Skybourne_CoupledHabitation_20261104 --map-sha256 14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362 --frame OPERATOR_ASSERTED_SHARED_SHIP_FRAME --expected-head FULL_40_CHARACTER_COMMIT_SHA --output C:/TSTSS_Review/NEW_PRIVATE_DIRECTORY/start.json

Export another independently hash-checked review map or independently prepared pose to a distinct path. The frame name is an **operator assertion**, not proof the two maps share a physical reference frame. A saved map is a snapshot and does not itself supply an animation trajectory. Candidate files and logs are retained for diagnosis; a failed host postcheck does not certify an existing candidate.

## Compare two snapshots

Create a JSON mapping with distinct observed actor labels for each endpoint. Each side must include exactly the obstacle roles hull, bridge, quarters, deck and the wings FORE_PORT, FORE_STARBOARD, AFT_PORT, AFT_STARBOARD. The expected shape is:

    {"start":{"hull":"label", "bridge":"label", "quarters":"label", "deck":"label", "FORE_PORT":"label", "FORE_STARBOARD":"label", "AFT_PORT":"label", "AFT_STARBOARD":"label"}, "end":{"hull":"label", "bridge":"label", "quarters":"label", "deck":"label", "FORE_PORT":"label", "FORE_STARBOARD":"label", "AFT_PORT":"label", "AFT_STARBOARD":"label"}}

Those labels are placeholders and must be replaced with distinct observed labels; the actual map may not provide all required bodies. Then run:

    python unreal/Tools/run_aureate_envelope_export_native.py combine --start START.json --end END.json --labels LABELS.json --clearance CENTIMETERS --output NEW_REPORT.json

The adapter changes quaternion order from Unreal XYZW to the verifier's WXYZ, keeps wing bounds in the component's local frame and maps static obstacle bounds into oriented world boxes. It refuses duplicate labels, missing roles, changed mesh paths/bounds, nonpositive scale, incompatible frame names, and any obstacle transform change. The last restriction is essential: the existing verifier treats obstacles as static and cannot validate a moving bridge/quarters. Required clearance is explicitly supplied by the operator; no canon or safety threshold is invented.

The output records snapshot/map hashes, the supplied mapping hash, provisional configuration and verifier verdict. Exit 0 means only that the supplied boxes and interpolated model yielded CLEAR_UNDER_ENVELOPES; reject, unproven and invalid outcomes exit nonzero. It is **not** native collision, mesh contact, swept physics, realistic animation, sufficient crew clearance, visual approval, or gameplay authorization. Asset package bytes, common frame equivalence and the actual transition path require independent verification. A mismatch or missing body is a HOLD, not a reason to substitute a fabricated proxy.

## Verification boundary

The Python tests use synthetic records and a simulated Unreal API. A real commandlet snapshot must be reported separately with exact source commit, map hash and local receipt; no positive claim about the other endpoint or actual transition follows from one snapshot. Keep the output and private review art out of the public repository.

## Native review checkpoint

On Neontic, an earlier source commit 641f6f0cde099f2622711526928995ccecd88707 ran the recorder in Unreal 5.8.4 on the SHA-locked coupled Skybourne review map, producing ten StaticMeshActor records and preserving the original map. One snapshot was supplied as both endpoints solely to smoke-test the source pipeline at rest. Eight of 22 box pairs returned REJECT_CLEARANCE_VIOLATION with zero clearance. This is an oriented-box overlap warning for the single review pose, not proof of mesh contact or any movement path. That run predates subsequent host-receipt changes and cannot establish those changes were natively exercised; re-run at the current exact commit before claiming current native verification.
