shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// Photorealistic cryptid pelt & layered fur shader for The Black Pines
uniform vec4 fur_base_color : source_color = vec4(0.065, 0.052, 0.042, 1.0);

uniform vec4 fur_highlight_color : source_color = vec4(0.14, 0.11, 0.08, 1.0);
uniform float roughness_base : hint_range(0.0, 1.0) = 0.88;
uniform float wetness : hint_range(0.0, 1.0) = 0.35;
uniform float rim_strength : hint_range(0.0, 5.0) = 1.6;
uniform vec4 rim_tint : source_color = vec4(0.28, 0.24, 0.20, 1.0);
uniform float uv_scale : hint_range(0.5, 20.0) = 6.0;

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

float hair_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash(i);
	float b = hash(i + vec2(1.0, 0.0));
	float c = hash(i + vec2(0.0, 1.0));
	float d = hash(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void vertex() {
	// Subtle breathing and hair wind displacement in freezing Pacific Northwest air
	float wind = sin(TIME * 2.0 + VERTEX.y * 3.0 + VERTEX.x * 2.0) * 0.003;
	VERTEX += NORMAL * wind;
}

void fragment() {
	// Stretch UVs vertically to emulate natural downward-hanging hair strands and pelt grain
	vec2 uv = UV * uv_scale;
	vec2 strand_uv = vec2(uv.x * 18.0, uv.y * 4.5);
	
	float n1 = hair_noise(strand_uv);
	float n2 = hair_noise(strand_uv * 2.1 + vec2(3.1, 7.4));
	float strand = n1 * 0.65 + n2 * 0.35;

	// Deep rich primeval animal pelt coloration
	vec3 albedo = mix(fur_base_color.rgb, fur_highlight_color.rgb, strand * 0.45);

	// Subtle rain moisture dampening without synthetic glossy shine
	albedo *= (1.0 - wetness * 0.18);
	ALBEDO = albedo;

	// Animal fur is coarse and non-metallic (roughness 0.84 - 0.94)
	ROUGHNESS = clamp(roughness_base + (strand - 0.5) * 0.08, 0.84, 0.94);
	METALLIC = 0.0;
	SPECULAR = 0.22;

	// Zero clearcoat - removes plastic / bowling-ball shine
	CLEARCOAT = 0.0;
	CLEARCOAT_ROUGHNESS = 1.0;

	// Soft backlight scattering through silhouette hair edges
	BACKLIGHT = fur_base_color.rgb * 1.2;

	// Gentle Fresnel rim to carve dark cryptid silhouette against foggy backdrop
	RIM = rim_strength * 0.28;

	RIM_TINT = 0.6;
}

