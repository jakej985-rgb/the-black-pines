shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_burley, specular_schlick_ggx;

// Textures
uniform sampler2D texture_albedo : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_roughness : hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_ao : hint_default_white, filter_linear_mipmap_anisotropic;

// Parameters
uniform vec4 albedo_tint : source_color = vec4(0.85, 0.82, 0.78, 1.0);
uniform float uv_scale : hint_range(5.0, 50.0) = 25.0;
uniform float normal_scale : hint_range(0.0, 4.0) = 1.4;
uniform float roughness_mult : hint_range(0.0, 2.0) = 1.0;

// Wet Mud / Puddle Settings
uniform float puddle_threshold : hint_range(-1.0, 1.0) = -0.05;
uniform float puddle_softness : hint_range(0.01, 0.5) = 0.22;
uniform vec4 puddle_color : source_color = vec4(0.12, 0.10, 0.08, 1.0);
uniform float puddle_roughness : hint_range(0.0, 0.5) = 0.08;

varying vec3 v_world_pos;
varying vec3 v_world_normal;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_normal = (MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz;
}

// Pseudo-random noise for macro-scale variation
float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
	           mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void fragment() {
	vec2 uv_detail = UV;
	vec2 uv_macro = v_world_pos.xz * 0.04; // Large 25m macro coordinates

	// Macro variation noise
	float macro_n = noise(uv_macro);
	float macro_n2 = noise(uv_macro * 2.3 + vec2(5.2, 1.7));

	// Dual-scale texture sampling
	vec4 alb_detail = texture(texture_albedo, uv_detail);
	vec4 alb_macro = texture(texture_albedo, uv_macro * 4.0);
	vec3 base_alb = mix(alb_detail.rgb, alb_macro.rgb, 0.25 * macro_n) * albedo_tint.rgb;

	// Darken slightly in macro valleys for organic soil color depth
	base_alb *= (0.85 + 0.3 * macro_n2);

	// Normal and Roughness sampling
	vec3 norm_map = texture(texture_normal, uv_detail).rgb;
	float rough_map = texture(texture_roughness, uv_detail).r * roughness_mult;
	float ao_map = texture(texture_ao, uv_detail).r;

	// Wet Puddle Calculation
	// Puddles pool in low elevation depressions where the ground normal faces upward
	float flatness = clamp(v_world_normal.y, 0.0, 1.0);
	float depth_factor = puddle_threshold - v_world_pos.y;
	float puddle_mask = smoothstep(0.0, puddle_softness, depth_factor) * smoothstep(0.75, 0.98, flatness);

	// Macro noise breaks up puddle edges organically
	puddle_mask = clamp(puddle_mask * (0.6 + 0.8 * macro_n), 0.0, 1.0);

	// Blend wet puddle properties
	vec3 final_albedo = mix(base_alb, puddle_color.rgb, puddle_mask * 0.7);
	float final_roughness = mix(rough_map, puddle_roughness, puddle_mask);

	// Puddle centers flatten normal to produce clean mirror water reflection
	vec3 final_normal = mix(norm_map, vec3(0.5, 0.5, 1.0), puddle_mask * 0.85);

	ALBEDO = final_albedo;
	ROUGHNESS = final_roughness;
	SPECULAR = mix(0.4, 0.9, puddle_mask);
	NORMAL_MAP = final_normal;
	NORMAL_MAP_DEPTH = mix(normal_scale, 0.2, puddle_mask);
	AO = ao_map;
}
