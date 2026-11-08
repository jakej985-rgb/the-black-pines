shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// Photorealistic cryptid pelt & layered fur shader for The Black Pines
uniform vec4 fur_base_color : source_color = vec4(0.08, 0.065, 0.055, 1.0);
uniform vec4 fur_highlight_color : source_color = vec4(0.18, 0.14, 0.11, 1.0);
uniform float roughness_base : hint_range(0.0, 1.0) = 0.84;
uniform float wetness : hint_range(0.0, 1.0) = 0.65;
uniform float rim_strength : hint_range(0.0, 5.0) = 2.4;
uniform vec4 rim_tint : source_color = vec4(0.35, 0.32, 0.28, 1.0);
uniform float uv_scale : hint_range(0.5, 20.0) = 4.0;

void vertex() {
	// Subtle breathing and hair wind displacement in freezing Pacific Northwest air
	float wind = sin(TIME * 2.2 + VERTEX.y * 3.5 + VERTEX.x * 2.5) * 0.0035;
	VERTEX += NORMAL * wind;
}

void fragment() {
	vec2 uv = UV * uv_scale;
	
	// Procedural hair strand & clump noise
	float hair_noise = sin(uv.x * 32.0 + sin(uv.y * 12.0) * 2.0) * 0.5 + 0.5;
	float matted_clump = sin(uv.y * 8.0 + uv.x * 4.0) * 0.5 + 0.5;

	vec3 albedo = mix(fur_base_color.rgb, fur_highlight_color.rgb, hair_noise * 0.35 + matted_clump * 0.25);

	// Rain wetness darkening: moisture deepens color saturation in valley fog
	albedo *= (1.0 - wetness * 0.22);
	ALBEDO = albedo;

	// Roughness variation: coarse dry hair is 0.85, rain-dampened clumps drop to 0.45
	ROUGHNESS = mix(roughness_base, 0.42, wetness * hair_noise);
	METALLIC = 0.02;

	// Clearcoat wet moisture layer: creates sharp specular glints under flashlight beam
	CLEARCOAT = wetness * 0.85;
	CLEARCOAT_ROUGHNESS = 0.18;

	// Translucent backlight scattering through thin hair tips / silhouette edges
	BACKLIGHT = vec3(0.08, 0.06, 0.05);

	// Fresnel rim illumination to carve cryptid silhouette against dark forest
	RIM = rim_strength * 0.45;
	RIM_TINT = 0.55;
}
