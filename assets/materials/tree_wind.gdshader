shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

// Organic Tree Canopy Wind-Sway Shader for The Black Pines.
// Simulates trunk flex, upper canopy drift, and pine branch cluster fluttering.

uniform vec4 albedo_color : source_color = vec4(0.06, 0.14, 0.08, 1.0);
uniform float roughness : hint_range(0.0, 1.0) = 0.8;
uniform sampler2D normal_texture : hint_normal;
uniform float normal_scale : hint_range(0.0, 5.0) = 1.8;
uniform vec3 uv1_scale = vec3(2.0, 2.0, 2.0);

uniform vec2 wind_direction = vec2(0.85, 0.52);
uniform float wind_speed : hint_range(0.0, 5.0) = 1.1;
uniform float wind_strength : hint_range(0.0, 1.0) = 0.14;
uniform float gust_frequency : hint_range(0.0, 3.0) = 0.35;
uniform float gust_strength : hint_range(0.0, 1.0) = 0.09;
uniform float canopy_height_reference : hint_range(1.0, 25.0) = 14.0;
uniform float branch_flutter : hint_range(0.0, 0.2) = 0.035;

void vertex() {
	vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 wind_dir = normalize(wind_direction);
	vec2 wind_perp = vec2(-wind_dir.y, wind_dir.x);
	
	// Tree sway increases with vertex height
	float h = clamp(VERTEX.y / canopy_height_reference, 0.0, 1.3);
	float trunk_flex = pow(h, 1.6);
	
	// Natural multi-frequency sinusoidal wind gusts
	float primary_wave = sin(TIME * wind_speed + world_pos.x * 0.12 + world_pos.z * 0.15);
	float secondary_wave = cos(TIME * (wind_speed * 0.7) + world_pos.x * 0.08 - world_pos.z * 0.1);
	float gust = max(0.0, sin(TIME * gust_frequency + primary_wave * 0.5 + world_pos.x * 0.05 + world_pos.z * 0.06));
	
	// High-frequency needle / branch turbulence
	float flutter = sin(TIME * (wind_speed * 2.8) + VERTEX.x * 3.5 + VERTEX.y * 2.0 + VERTEX.z * 3.5) * branch_flutter * h;
	
	float main_sway = (primary_wave * 0.7 + secondary_wave * 0.3) * wind_strength + (gust * gust_strength);
	float total_displacement = (main_sway * trunk_flex) + flutter;
	
	// Lateral sway with slight perpendicular swirl
	float lateral_cross = sin(TIME * (wind_speed * 0.85) + world_pos.x * 0.2) * 0.18 * main_sway * trunk_flex;
	
	VERTEX.x += wind_dir.x * total_displacement + wind_perp.x * lateral_cross;
	VERTEX.z += wind_dir.y * total_displacement + wind_perp.y * lateral_cross;
	// Realistic slight downward dip when bending under gust force
	VERTEX.y -= total_displacement * total_displacement * 0.04;
}

void fragment() {
	vec2 uv = UV * uv1_scale.xy;
	ALBEDO = albedo_color.rgb;
	ROUGHNESS = roughness;
	NORMAL_MAP = texture(normal_texture, uv).rgb;
	NORMAL_MAP_DEPTH = normal_scale;
}
