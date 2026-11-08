shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

// Organic Foliage Wind-Sway Shader for The Black Pines.
// Gently sways ferns, weeds, and tall grass in the night breeze.

uniform vec4 albedo : source_color = vec4(0.08, 0.16, 0.09, 1.0);
uniform float roughness : hint_range(0.0, 1.0) = 0.82;
uniform float wind_speed : hint_range(0.0, 5.0) = 1.5;
uniform float wind_strength : hint_range(0.0, 0.5) = 0.07;
uniform float gust_frequency : hint_range(0.0, 3.0) = 0.6;

void vertex() {
	// Sway vertices based on height from root
	float height_factor = clamp(VERTEX.y, 0.0, 1.5);
	vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	
	float wave = sin(TIME * wind_speed + world_pos.x * 1.8 + world_pos.z * 1.4);
	float gust = sin(TIME * gust_frequency + world_pos.x * 0.6 + world_pos.z * 0.8);
	
	float total_sway = (wave * 0.7 + gust * 0.5) * wind_strength * height_factor;
	VERTEX.x += total_sway;
	VERTEX.z += total_sway * 0.6;
}

void fragment() {
	ALBEDO = albedo.rgb;
	ROUGHNESS = roughness;
}
