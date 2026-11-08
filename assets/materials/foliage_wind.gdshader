shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

// Organic Foliage Wind-Sway Shader for The Black Pines.
// Simulates natural multi-harmonic sinusoidal gusts, directional breeze, and organic bend for undergrowth.

uniform vec4 albedo : source_color = vec4(0.08, 0.16, 0.09, 1.0);
uniform float roughness : hint_range(0.0, 1.0) = 0.82;
uniform vec2 wind_direction = vec2(0.85, 0.52);
uniform float wind_speed : hint_range(0.0, 5.0) = 1.5;
uniform float wind_strength : hint_range(0.0, 0.5) = 0.08;
uniform float gust_frequency : hint_range(0.0, 3.0) = 0.6;
uniform float gust_strength : hint_range(0.0, 0.5) = 0.06;
uniform float height_max : hint_range(0.1, 5.0) = 1.2;
uniform float leaf_flutter : hint_range(0.0, 0.1) = 0.02;

void vertex() {
	vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 wind_dir = normalize(wind_direction);
	vec2 wind_perp = vec2(-wind_dir.y, wind_dir.x);
	
	// Sway vertices based on height from base
	float height_factor = clamp(VERTEX.y / max(height_max, 0.05), 0.0, 1.5);
	float bend = pow(height_factor, 1.3);
	
	// Natural multi-harmonic sinusoidal wind model
	float primary_wave = sin(TIME * wind_speed + world_pos.x * 1.5 + world_pos.z * 1.2);
	float harmonic_wave = cos(TIME * (wind_speed * 0.65) + world_pos.x * 0.9 - world_pos.z * 0.7);
	float gust = max(0.0, sin(TIME * gust_frequency + primary_wave * 0.4 + world_pos.x * 0.5 + world_pos.z * 0.6));
	
	// Subtle high-frequency leaf fluttering
	float flutter = sin(TIME * (wind_speed * 3.2) + VERTEX.x * 8.0 + VERTEX.z * 6.0) * leaf_flutter * height_factor;
	
	float main_sway = (primary_wave * 0.7 + harmonic_wave * 0.3) * wind_strength + (gust * gust_strength);
	float total_displacement = (main_sway * bend) + flutter;
	
	// Perpendicular gentle swirl
	float cross_drift = sin(TIME * (wind_speed * 0.8) + world_pos.z * 0.8) * 0.15 * main_sway * bend;
	
	VERTEX.x += wind_dir.x * total_displacement + wind_perp.x * cross_drift;
	VERTEX.z += wind_dir.y * total_displacement + wind_perp.y * cross_drift;
	// Recoil dip under gust pressure
	VERTEX.y -= total_displacement * total_displacement * 0.1;
}

void fragment() {
	ALBEDO = albedo.rgb;
	ROUGHNESS = roughness;
}
