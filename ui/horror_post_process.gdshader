shader_type canvas_item;

// Cinematic Horror Post-Processing Shader for The Black Pines.
// Adds film grain, edge vignette, and chromatic aberration.

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;
uniform float vignette_intensity : hint_range(0.0, 1.0) = 0.45;
uniform float vignette_radius : hint_range(0.0, 1.5) = 0.85;
uniform float grain_intensity : hint_range(0.0, 0.2) = 0.038;
uniform float chromatic_aberration : hint_range(0.0, 0.02) = 0.0025;

float random_grain(vec2 uv, float time) {
    return fract(sin(dot(uv + vec2(time * 0.05, -time * 0.03), vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 center_offset = uv - vec2(0.5);
    float dist = length(center_offset);

    // Chromatic aberration at screen periphery
    vec2 ca_offset = center_offset * dist * chromatic_aberration * 6.0;
    float r = texture(SCREEN_TEXTURE, uv - ca_offset).r;
    float g = texture(SCREEN_TEXTURE, uv).g;
    float b = texture(SCREEN_TEXTURE, uv + ca_offset).b;
    vec3 col = vec3(r, g, b);

    // Vignette
    float vig = smoothstep(vignette_radius, vignette_radius - 0.45, dist);
    col *= mix(1.0 - vignette_intensity, 1.0, vig);

    // Film Grain
    float grain = (random_grain(uv, TIME) - 0.5) * grain_intensity;
    col += grain;

    COLOR = vec4(col, 1.0);
}
