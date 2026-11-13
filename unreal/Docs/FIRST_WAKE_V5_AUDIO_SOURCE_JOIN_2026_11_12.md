# First Wake V5 and audio source join — review only

This isolated integration starts from V5 object/material review commit `ac7152b4fb6a69b8b1878350efa176362ec2a6c5` (PR #820) and joins local audio review commit `fde6546d544f0ddb0b9cc1d26fdcd5774542de3a`. Both share `2afb4b7ea6cda75dc6068014eb19c06718259539` as merge base. Neither source branch nor protected main was changed.

The join adds an opt-in surface-aware footstep director, audio scene-binding inventory, original synthetic QA loop generator, and a guarded disposable audio-map staging tool. The scene-binding inventory is planning data: it does not place actors or bind sound assets into the V5 opening. The staging tool targets a separate VS01 review-map copy, not the V5 playable opening, and requires a clean detached AudioReview worktree, exact source SHA, original QA receipts, native classes, and resource admission. This join does not make the playable opening audible.

The only textual conflict was the loop-handle validity expression in TSTSSAudioSubsystem.cpp. The V5 parent version was retained; its UE 5.8.4 build and 36-test receipt apply to that parent, not this new joined revision. The audio source assertion was aligned with the retained guarded expression. All other merge changes require native integration verification.

Before the integration commit, `python -m unittest discover -s unreal/Tools -p 'test_*.py'` passed 601 tests on the combined working tree; the audio-specific suite passed 29. These are source and Python tests, not proof of UE C++ compilation, actor placement, playback, route traversal, visual quality, or creator acceptance.

At admission on Neontic, approximately 5.86 GiB RAM and 16.35 GiB C: disk were free; RAM was below the 6.5 GiB interactive audio/graphics staging threshold. No native build, Unreal editor, audio import, map mutation or playback test was run for this join. Previously reported parent-head evidence must not be attributed to the join.

Next: recheck resource and concurrent-process gates; compile and run native tests against this exact joined revision in an isolated checkout; stage original QA audio in its guarded disposable map; verify actual playback, mute, transitions, surface mapping and captions; then design and test a safe V5-specific binding with the live route. Verify audio rights and conduct listening/mix review before promotion. Separately complete the player-driven E route, physical splashdown and visual acceptance. Keep Lyra recruitment after splashdown, Reson and Aepex unavailable, and Starbourne locked.
