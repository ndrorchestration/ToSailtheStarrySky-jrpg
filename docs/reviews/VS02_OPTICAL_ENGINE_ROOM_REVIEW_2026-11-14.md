# TSTSS ? VS02 optical engine-room disposable review copy

**Evidence:** NATIVE UE 5.8.4 MAP COMPOSITION/READBACK PASS, NOT PIE, NOT GPU OR VISUAL APPROVAL.

**Source:** PR #837 commit e7686bcb2f262ca9de0e6f9ceba96c812b93731f. Original /Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors SHA256 a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69; source untouched.

**Isolated new map:** /Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview SHA256 bbff86677b71e73609f9bdb95559f3af9af9ab0032857c613e1b8d4d36a5d5a3. Not shipping or canonical. Its name was already explicitly allowed by the read-only coordinator.

**Native readback:** 28 actors, one LIFT StaticMeshActor, one native TSTSSAtmosphereDirector, two 65mm f/2.8 CineCameraActor comparisons at 751.55cm manual-focus and disabled-depth-of-field, and a disabled opt-in TSTSSReviewFocusReceiver. The original four sun/sky/fog actor lights were removed from the COPY ONLY to avoid duplicate lighting.

**Replay:** unreal/Tools/stage_vs02_optical_playtest.py locks the historical source HEAD and uses the two-phase prepare (Save Map As) and compose (new Editor process) workflow. Environment flags TSTSS_VS02_OPTICAL_PHASE, TSTSS_VS02_OPTICAL_EXPECTED_HEAD, and TSTSS_VS02_OPTICAL_STAGE_EXPLICIT=1 are mandatory; clean source, Windows/UE5.8.4 and destination collision checks fail closed. Receipt files in unreal/Saved/OpticalVS02Stage are local-only and NOT a public GitHub artifact. Native readback tool: unreal/Tools/readback_vs02_optical_playtest.py.

**OPEN:** Real Ender PIE and story-derived BoardedAureateWake state, C key event, proximity, camera return after four seconds, input movement/look recovery, physical splashdown, Lit GPU review/DOF, audio/accessibility/performance and creator visual approval. No SaveGame schema, story, Starbourne, party gates or production maps altered.

**Merges:** KEEP DRAFT and UNMERGED. Historical #835/#836 receipts remain scoped.

**Additional bounded path proposed in next review commit:** Once the V5 First Wake story has actually earned EngineeringChecked, the original VS02 ship scene offers an explicit PIE-only [O] trip to the camera-review copy via one-use in-memory GameInstance ticket (no story skip or SaveGame write). In the copy, approach LIFT and press [C] to opt in to camera focus; normal [K] still requires actual Launched progression before opening sky. No direct map loading grants story authorization, and these prompts/controls remain unverified by real keyboard PIE until tested.

## V2 provisional optical exposure/framing ? native UE saved map and readback

A bounded GUI UE5.8.4 D3D12 comparison established a Lit whiteout. The original editor viewport had 95.345% near-white pixels. A -4 EV trial reduced clipping to 16.808%, and -7 EV to 0.115%. A north-rail-facing reframe from LIFT + (-380, +650, +260) cm at -6 EV produced approximately 0.50% near-white clipping and removed the reversed station-label occlusion. These are descriptive pixel checks on Editor-window screenshots with editor overlays, not calibrated photometric data.

After the test, a guarded native UE Editor process saved ONLY the nonshipping EngineFocus_V1/M_EnginePresentationReview map with two identical 65mm f/2.8 CineCameraActor configurations (focus 796.555 cm, manual-DOF and no-DOF control) and -6 EV camera exposure compensation. An independent fresh native Editor readback confirmed 28 actors, one LIFT instrument, one native atmosphere director, one disabled receiver, and both camera transforms and optical settings. The current review map binary SHA256 is 06f006b42d54a990ffefa5903bda0d24e34259a424c1f6bee4a51a29f0766223; the original VS02 remains byte-identical SHA256 a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69. The historical original review map remains in Git and a local Saved backup.

The two in-memory reframe screenshots differed by mean absolute RGB values of only 0.28, 0.30 and 0.38 across pixels. The intended depth-of-field/bokeh difference is thus NOT established or creator-approved. Both the original and copied scenes are greybox and no approved character, ship or PBR art was promoted. Realtime Override warnings from an earlier Editor API call were avoided in subsequent tests by not invoking editor_set_viewport_realtime.

Source changes align the PIE-only spawned C-key camera to this draft framing/exposure, but player-operated E/K/O/C progression, authentic World/PIE focus cut, four-second camera/input restoration, varying weather exposure, GPU bokeh quality and final creator visual approval remain NOT VERIFIED. The new committed provenance manifest is in unreal/DataSource/Cinematics/VS02OpticalLookdev.review.json; retained local receipts are under unreal/Saved/OpticalVS02Stage/ExposureV2Stage. Preserve DRAFT/UNMERGED and do not touch protected main or original VS02.
