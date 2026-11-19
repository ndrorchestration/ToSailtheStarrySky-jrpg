# First Wake — contextual engineering intercom review

**IMPLEMENTED / SOURCE REVIEW ONLY.** Isolated branch
`review/firstwake-contextual-intercom-20261118`, based on draft #863 at
`73abb1a7be714d5a47b102c2f98109730579202d`. Unreal Engine 5.8.4 remains the
native target. No merges, saved-map edits, private assets or save-schema changes.

## Problem and behavior

Engineering inspections accept any station order. Previously, checking Reserve
first displayed “Complete the final signoff” even with Lift/Pressure missing;
checking Pressure after Reserve told the player to check Reserve again.

The captain now acknowledges the accepted station and reads the next check
from `UTSTSSFirstWakeState::GetReviewObjectiveText()`. Only all three inspection
bits permit a signoff cue. A successful signoff still says to await Ionia's
launch order; captions cannot release clamps or launch the ship.

A dedicated three-line HUD panel shows Ionia, her reply and the next check for
nine game seconds, independently of debug-screen messages. It replaces the
previous caption on the next accepted interaction. It disappears on expiry,
restore/reset generation, changed inspection mask/beat, invalid time or leaving
the standalone VS02 review context. It is current-pawn cosmetic state only.
At viewports below 640×480 the panel is omitted. Its authored bounds leave the
top objective and bottom interaction prompt clear; actual font fit and native
gameplay framing require GPU review.

## Verification and continuation

- Portable C++ tests compile the actual acknowledgement helper, objective,
  caption reader and caption HUD method against narrow API stand-ins. They
  exercise all six station orders, signoff restraints, wrong-world rejection,
  expiry, reset/reload invalidation and panel bounds. Fixed-signoff and removed
  restore-guard mutations must fail behavioral checks.
- Existing intercom E-gate/signoff guards, portable full-HUD development and
  shipping probes, and 38-name native registration remain required. Registration
  is not native test execution. The full `unreal/Tools/test_*.py` suite runs in CI.
- **OPEN:** exact-head UE5.8.4 UHT/UBT build and 38 native automations; genuine
  VS02 E interactions in each inspection order; timed caption replacement and
  F9/reset behavior; native 640×480 and 1280×720 font/contrast/framing captures.
  RCV-04/06/08/09 remain pending. No audio or voice is added or verified.
- Neontic was offline at this session's RDC observation. Resume native work only
  after checking current processes, source SHA, private asset custody and the
  existing resource gates. Preserve the separate title/Greenwood handoff work.

This improves the existing review engineering flow; it does not establish an
enclosed finished engine room, full-route playability or creator acceptance.

## Native replay finding and corrective follow-up

On `5210967ff0aba0b1a1b4043c0bbc693253763abb`, UE5.8.4 Editor build and
38/38 native automations passed. A scripted private-Ender PIE probe reached
VS02 through the actual Ionia and ship interaction rays. Reserve-first and
normal inspection sequences passed. Native D3D11 1326×924 captures showed
“Reserve check received” with the still-missing Lift objective, then no caption
after 9.52 game seconds. The pawn/art and room remain unfinished review assets;
synthetic positioning and flyer seeding do not constitute a human playthrough.

A repeated save/load test exposed a separate signoff defect: after the third
inspection order all three bits were present, but the signoff visibility ray
response remained Ignore. Collision restoration and the beacon's visual cache
had drifted; the cached-availability fast path could skip collision repair.
The follow-up synchronizes the story-gated signoff collision **before** the
cosmetic early return. It does not broaden interaction reach or grant a beat.
An executable regression probes both collision drift directions and repeated
replays; restoring the old ordering must fail. Native results above belong to
the earlier head; the corrective head requires fresh build/automation/replay
evidence before inheriting any acceptance.
