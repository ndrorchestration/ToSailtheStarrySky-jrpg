# Resonator — creator-selected Ender vertical-slice primary job

This folder contains **review-only source data**, not an imported Content asset,
a shipping gameplay class, or permission to cast any spell.

The JSON DataTable row identifies the creator-selected `Resonator` class and four
curriculum families: Resonance/Harmonic, Correspondence, Psion/Psychic, and
Synergy/Combination. His permanent profession is Harmonic Resonance Engineer.
His four **innate** magical affinities remain Aether, Resonance/Harmonic,
Correspondence, and Lumen; Five Lights Spirit is separately narrative.

`ReviewSelectable` permits selection in an **explicitly unlocked review state**
only. The source row contains no starting skills, school mastery or equipment
permissions and never changes Ender's independent Shine progression.

`TSTSS.Design.HybridJobTableReadback` loads this exact file into a disposable
Unreal DataTable. It verifies import, metadata, review-only positive job choice,
denial without explicit unlock, denial of unlearned Psychic magic, and revocation.
The GitHub Python source test checks the JSON metadata independently; its passing
does not establish native UE C++/UHT compilation, in-editor automation, actual
party loadout, playable combat or save continuity.

Authoring specification:
https://app.notion.com/p/414f5bad238b8114a732c153578fd190
