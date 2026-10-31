# Dragonfly venation prototype — Unreal wing mask

A deterministic UV-space 1024px RGBA mask is available with `python unreal/Tools/generate_venation_mask.py` (requires Pillow). It draws the root-to-tip longitudinal spar, two boundaries and branched supporting veins. First-pass generator locally exercised at 1024×1024 and produced 105 vector paths.

## Material integration candidate
Import the RGBA PNG as an Unreal Texture2D (mask texture compression, sRGB off for scalar mask). On `M_AureateWakeWing`, use TextureSample alpha to drive a controlled gold/opal vein overlay, optional shallow normal/bump variation and roughness contrast. Combine with `OrbiterSailBlend` already exposed by the actor to gradually reveal the photovoltaic/lightsail cell pattern. Avoid declaring functional solar hardware or true physical metamaterial simulation.

## Limitations
This is a *flat texture-space mask*, not geometric raised veins, and not an authored Unreal material. Check UV orientation, texture padding, mipmaps, aliasing and source mesh normals in UE 5.8. The currently generated thin shell remains a proof-of-concept, with source-generated materials and no native render/compile acceptance. Four equal-sized wings remain the same four units throughout the ship forms.
