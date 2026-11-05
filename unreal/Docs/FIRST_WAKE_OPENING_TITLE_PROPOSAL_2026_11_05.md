# First Wake — opening screen and beginning

**Status:** review proposal, 2026-11-05. The creator's existing story decisions remain authoritative. New dialogue, staging, music and timings below are proposals, not approved canon. Implementation is a separate opt-in Unreal screen; no native build, render, playthrough or creator visual acceptance has been established for it.

## Player experience proposal

### Title
Look across the harbor and the Aureate Wake beneath a veil of deep blue. Let warm light and the ship's dragonfly-inspired wings draw the eye. Use the full game title and a single prominent **New Game** control. A quiet melodic phrase suggests the importance of sound; this is a musical direction, not a completed score. The opt-in review can play the creator-provided title video from a private local movie file, including its soundtrack, with a live New Game control aligned over the painted button. If the file cannot be opened, the original text menu is the fallback. Native rendering, input, sound and packaging still require verification.

### 1. The harbor — approximately 2 minutes
Fade from the title to a lived-in harbor at morning. Ender arrives with his staff and tools, responding to an opportunity to repair a ship's harmonic levitation engine. Before a lore explanation, give the player control: walk toward a posted job and examine it. Nearby sound, movement and ship silhouettes establish a working place. No exposition dump.

### 2. The captain — approximately 2–3 minutes
The job leads Ender to Captain Ionia and the Aureate Wake. She needs someone who can listen to an engine others have written off. Their conversation shows her decisiveness and his careful attention; she hires him. Example exchange, **proposed only**:

> **Ionia:** “Everyone else told me what was broken. Tell me what you hear.”
>
> **Ender:** “It isn't silent. It's trying to find the next note.”

Ionia is the first to join Ender. Precise recruitment timing and gameplay implementation remain to be integrated and verified.

### 3. The ship and the repair — approximately 4–6 minutes
Board the Wake. Let the player explore the deck, meet Ionia aboard, and inspect lift, pressure and reserve systems. Each inspection should tell the player something tangible about the ship and Ender's approach to fixing it. After addressing the problem, Ender and Ionia prepare the first launch. The present native review lane exposes ordered interaction markers, not finished conversations, repairs, or recruited character gameplay.

### 4. First flight and emergency — approximately 3–5 minutes
The Wake rises. Give the moment room to feel joyful before a problem forces an emergency sea landing. Preserve a clear cause and physical sequence; the exact failure, shot sequence, gameplay and dialogue need authoring. Sea contact and safe flotation must come from the existing physical/story checks, not a title or cinematic shortcut.

### 5. Lyra and Talen
After splashdown, introduce Lyra and her five-year-old son Talen through a personal, grounded encounter. Lyra joins after Ionia. Later, Ionia's Denith shanty gives Ender the resonance melody that solves the fuel problem. Treat the exact dialogue, scene placement and mechanics as proposed until reviewed.

## Implementation and review boundary

- The opening review mode and widget are additive source candidates. The mode is selected explicitly; normal startup and configuration are unchanged.
- **New Game** only closes the overlay and returns control to the already-loaded review level. It does not create, overwrite, erase or load a save, initialize a party, load a map, or implement a full production new-game flow.
- No options, continue, quit, cinematic camera, subtitles, save slots or localization have been implemented. The movie soundtrack has a review playback path but has not been heard or verified in Unreal.
- Native compilation, actual control testing, safe map selection, readability at multiple resolutions, capture against the approved ship, and creator visual review are outstanding.
- The isolated candidate is based on draft PR #772, not protected main. Its inherited milestone and F6/F9 review behavior applies only when the appropriate separately available review map is loaded. No claim is made that a private map ships with this source.
- Keep current five-character and ship visual approvals, Ionia-first ordering, Lyra-after-splashdown, Starbourne gate, and save boundaries unchanged.
