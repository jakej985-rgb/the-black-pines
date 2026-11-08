shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// Base PBR Textures
uniform sampler2D texture_albedo : source_color, filter_linear_mipmap_anisotropic, hint_default_white;
uniform sampler2D texture_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_roughness : hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_ao : hint_default_white, filter_linear_mipmap_anisotropic;

// PBR Base Parameters (Bark/Wood: roughness 0.75 - 0.90, metallic 0.0)
uniform vec4 albedo_tint : source_color = vec4(0.85, 0.82, 0.78, 1.0);
uniform vec3 uv_scale = vec3(1.0, 1.0, 1.0);
uniform float normal_scale : hint_range(0.0, 4.0) = 1.6;
uniform float roughness_min : hint_range(0.0, 1.0) = 0.75;
uniform float roughness_max : hint_range(0.0, 1.0) = 0.90;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;

// Weathering - Pacific Northwest Dampness, Moss & Grime
uniform float dampness : hint_range(0.0, 1.0) = 0.55;
uniform float moss_amount : hint_range(0.0, 1.0) = 0.35;
uniform vec4 moss_color : source_color = vec4(0.20, 0.30, 0.13, 1.0);
uniform float moss_roughness : hint_range(0.7, 1.0) = 0.88;
uniform float dirt_amount : hint_range(0.0, 1.0) = 0.25;
uniform vec4 dirt_color : source_color = vec4(0.12, 0.09, 0.07, 1.0);
uniform float dirt_roughness : hint_range(0.7, 1.0) = 0.85;

// Trunk Wind Sway (Active when trunk_wind_sway > 0.0, e.g. for living pine tree trunks)
uniform float trunk_wind_sway : hint_range(0.0, 1.0) = 0.0;
uniform vec2 wind_direction = vec2(0.85, 0.52);
uniform float wind_speed : hint_range(0.0, 5.0) = 1.1;
uniform float wind_strength : hint_range(0.0, 1.0) = 0.14;
uniform float gust_frequency : hint_range(0.0, 3.0) = 0.35;
uniform float gust_strength : hint_range(0.0, 1.0) = 0.09;
uniform float canopy_height_reference : hint_range(1.0, 25.0) = 14.0;

varying vec3 v_world_pos;
varying vec3 v_world_normal;

void vertex() {
	if (trunk_wind_sway > 0.001) {
		vec3 world_pos_init = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
		vec2 wind_dir = normalize(wind_direction);
		vec2 wind_perp = vec2(-wind_dir.y, wind_dir.x);
		
		float h = clamp(VERTEX.y / canopy_height_reference, 0.0, 1.3);
		float trunk_flex = pow(h, 1.6);
		
		float primary_wave = sin(TIME * wind_speed + world_pos_init.x * 0.12 + world_pos_init.z * 0.15);
		float secondary_wave = cos(TIME * (wind_speed * 0.7) + world_pos_init.x * 0.08 - world_pos_init.z * 0.1);
		float gust = max(0.0, sin(TIME * gust_frequency + primary_wave * 0.5 + world_pos_init.x * 0.05 + world_pos_init.z * 0.06));
		
		float main_sway = (primary_wave * 0.7 + secondary_wave * 0.3) * wind_strength + (gust * gust_strength);
		float total_displacement = main_sway * trunk_flex * trunk_wind_sway;
		
		float lateral_cross = sin(TIME * (wind_speed * 0.85) + world_pos_init.x * 0.2) * 0.18 * total_displacement;
		
		VERTEX.x += wind_dir.x * total_displacement + wind_perp.x * lateral_cross;
		VERTEX.z += wind_dir.y * total_displacement + wind_perp.y * lateral_cross;
		VERTEX.y -= total_displacement * total_displacement * 0.04;
	}
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

// Procedural hash & 2D noise for organic weathering patches
float hash21(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise2(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash21(i + vec2(0.0, 0.0)), hash21(i + vec2(1.0, 0.0)), u.x),
	           mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm2(vec2 p) {
	float val = 0.0;
	val += 0.5000 * noise2(p); p *= 2.02;
	val += 0.2500 * noise2(p); p *= 2.03;
	val += 0.1250 * noise2(p);
	return val;
}

void fragment() {
	vec2 uv = UV * uv_scale.xy;
	
	// Sample Base PBR maps
	vec4 alb_tex = texture(texture_albedo, uv);
	vec3 base_alb = alb_tex.rgb * albedo_tint.rgb;
	
	vec3 norm_map = texture(texture_normal, uv).rgb;
	float rough_tex = texture(texture_roughness, uv).r;
	float ao_tex = texture(texture_ao, uv).r;
	
	// Enforce standardized wood roughness bounds [0.75, 0.90]
	float base_rough = clamp(mix(roughness_min, roughness_max, rough_tex), roughness_min, roughness_max);

	// Organic weathering coordinates
	vec2 world_uv = v_world_pos.xz * 0.7 + vec2(v_world_pos.y * 0.2, 0.0);
	float weather_noise = fbm2(world_uv);
	
	// 1. Moss Weathering Layer
	// Clings to upward facets (tops of logs, stumps, fence rails) and rain-facing bark
	float up_facing = clamp(v_world_normal.y, 0.0, 1.0);
	float moss_mask = smoothstep(0.40, 0.85, up_facing + (weather_noise - 0.5) * 0.55);
	moss_mask = clamp(moss_mask * moss_amount * 1.4, 0.0, 1.0);
	
	// 2. Dirt / Aging Layer
	// Accumulates in bark grooves and base of trunks near soil
	float crevice_factor = (1.0 - ao_tex) * 0.75 + (1.0 - up_facing) * 0.25;
	float dirt_mask = smoothstep(0.25, 0.75, crevice_factor + (1.0 - weather_noise) * 0.25);
	dirt_mask = clamp(dirt_mask * dirt_amount * (1.0 - moss_mask * 0.7), 0.0, 1.0);
	
	// Blend Dirt and Moss into Base Albedo and Roughness
	vec3 weathered_alb = mix(base_alb, dirt_color.rgb, dirt_mask * 0.80);
	weathered_alb = mix(weathered_alb, moss_color.rgb, moss_mask * 0.88);
	
	float weathered_rough = mix(base_rough, dirt_roughness, dirt_mask);
	weathered_rough = mix(weathered_rough, moss_roughness, moss_mask);
	
	// 3. Dampness / Rain Weathering Layer
	// Rain water penetrates porous wood grain, deepening dark brown tones
	weathered_alb *= mix(1.0, 0.72, dampness * 0.8);
	// Rain creates specular sheen on wet bark & wood
	float wet_sheen_rough = weathered_rough * mix(1.0, 0.58, dampness);
	float final_rough = mix(weathered_rough, wet_sheen_rough, 1.0 - moss_mask * 0.55);
	
	// Specular response under flashlight and moonlight
	float final_specular = mix(0.42, 0.78, dampness * 0.70 * (1.0 - moss_mask * 0.5));
	
	ALBEDO = weathered_alb;
	ROUGHNESS = final_rough;
	METALLIC = metallic;
	SPECULAR = final_specular;
	NORMAL_MAP = norm_map;
	NORMAL_MAP_DEPTH = normal_scale;
	AO = ao_tex;
}
