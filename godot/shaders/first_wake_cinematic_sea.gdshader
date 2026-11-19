shader_type canvas_item;
render_mode unshaded;

// Small, bounded GPU shader: no particle systems, texture imports or readbacks.
uniform vec4 deep_water : source_color = vec4(0.07, 0.24, 0.31, 1.0);
uniform vec4 shallow_water : source_color = vec4(0.25, 0.49, 0.54, 1.0);
uniform float motion_scale : hint_range(0.0, 1.0) = 1.0;
uniform float glint_strength : hint_range(0.0, 1.0) = 0.58;

float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
void fragment() {
    vec2 uv = UV;
    float t = TIME * motion_scale * 0.34;
    float distance_fade = smoothstep(0.02, 0.98, uv.y);
    float w1 = sin(uv.x * 38.0 + uv.y * 25.0 + t * 1.1);
    float w2 = sin(uv.x * 71.0 - uv.y * 47.0 - t * 1.4);
    float w3 = sin(uv.x * 125.0 + uv.y * 83.0 + t * 0.65);
    float swell = w1 * 0.5 + w2 * 0.34 + w3 * 0.16;
    vec3 c = mix(shallow_water.rgb, deep_water.rgb, distance_fade * 0.83);
    c += vec3(0.07, 0.13, 0.14) * swell * (0.24 + distance_fade * 0.65);
    float golden_path = exp(-pow((uv.x - 0.20) * (2.1 + 4.0 * uv.y), 2.0) * 5.0);
    float stripes = smoothstep(0.78, 0.98, sin(uv.y * 270.0 + w1 * 1.5));
    float bright = stripes * golden_path * (0.13 + distance_fade * 0.62);
    float foam = smoothstep(0.92, 1.0, sin(uv.y * 103.0 + w2 * 0.9));
    float fine_grain = hash21(floor(uv * vec2(310.0, 130.0)));
    bright *= mix(0.55, 1.0, fine_grain);
    c += vec3(1.0, 0.78, 0.42) * bright * glint_strength;
    c += vec3(0.16, 0.34, 0.31) * foam * distance_fade * 0.10;
    COLOR = vec4(clamp(c, vec3(0.0), vec3(1.0)), 1.0);
}
