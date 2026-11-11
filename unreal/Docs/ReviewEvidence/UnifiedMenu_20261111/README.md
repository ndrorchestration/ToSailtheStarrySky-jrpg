# First Wake unified menu ? native in-game approval capture

Draft PR #793. No merge or visual approval yet. These are unretouched 1280x720 game-client pixels captured from Unreal Engine 5.8.4 Win64 Development while the First Wake review map was running. The contact sheet scales four of these real screenshots; the individual PNG files retain native resolution.

Screens included: Character Status, Ender/Ionia equipment, Ender staff unequip (Lyra remains recruitment-locked), Aureate Wake vessel overview, ship configurations (Starbourne fail-closed), and harmonic engineering (actual inspection flags, not fabricated telemetry).

Interactive exercise: keyboard M opens the menu; sidebar and ship subtabs navigate; clicking Ender's weapon changes ResonanceStaff to UNEQUIPPED in the transient owned review ledger; Return to Voyage and M reopen exercised. Not proof of saved inventory, combat application, ship upgrades, 3D fitting, gamepad support, or cinematic art approval.

See evidence_manifest.json for sha256 and provenance. Source parent before the polish/evidence commit: 70ba58fd8f4b6530ccb4ab7e37f7a7000d524008. No other development window was terminated.

Actual running game's RHI source log states D3D12, highest feature level SM5, chosen Intel Iris Xe adapter 0. This is a D3D12 native review capture, **not** final lighting, UE5 cinematic visual acceptance or live PIE gamepad verification. The map still has separate unbuilt-lighting warnings outside the review menu.
