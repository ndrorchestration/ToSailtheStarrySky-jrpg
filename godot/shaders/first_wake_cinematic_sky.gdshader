shader_type canvas_item;
render_mode unshaded;

// Painted stormbreak atmosphere. All values are presentational, not weather canon.
uniform vec4 zenith : source_color = vec4(0.058, 0.126, 0.212, 1.0);
uniform vec4 afterglow : source_color = vec4(0.55, 0.44, 0.43, 1.0);
uniform vec4 horizon : source_color = vec4(0.94, 0.73, 0.46, 1.0);
uniform float cloud_density : hint_range(0.0, 1.0) = 0.48;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
float noise21(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), f.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) {
        v += a * noise21(p);
        p = p * 2.08 + vec2(8.7, 3.3);
        a *= 0.5;
    }
    return v;
}
void fragment() {
    vec2 uv = UV;
    float altitude = smoothstep(0.0, 1.0, uv.y);
    vec3 c = mix(zenith.rgb, afterglow.rgb, smoothstep(0.02, 0.74, altitude));
    c = mix(c, horizon.rgb, smoothstep(0.58, 1.0, altitude) * 0.76);
    float cloud = fbm(uv * vec2(4.6, 7.8) + vec2(11.7, 3.2));
    float cloud_band = smoothstep(0.40, 0.68, cloud + (0.5 - uv.y) * 0.12);
    float upper_cloud = smoothstep(0.16, 0.92, abs(uv.y - 0.45));
    c = mix(c, vec3(0.18, 0.27, 0.34), cloud_band * cloud_density * (0.76 - upper_cloud * 0.24));
    float sun_dist = length((uv - vec2(0.20, 0.54)) * vec2(1.65, 1.0));
    float halo = exp(-sun_dist * 7.0) * 0.29;
    float gleam = exp(-sun_dist * 25.0) * 0.43;
    c += vec3(1.0, 0.76, 0.43) * (halo + gleam);
    c += vec3(0.11, 0.14, 0.14) * (1.0 - uv.y) * 0.13;
    COLOR = vec4(clamp(c, vec3(0.0), vec3(1.0)), 1.0);
}
