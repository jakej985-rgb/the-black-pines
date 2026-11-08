shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

// Base PBR Textures
uniform sampler2D texture_albedo : source_color, filter_linear_mipmap_anisotropic, hint_default_white;
uniform sampler2D texture_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_roughness : hint_default_white, filter_linear_mipmap_anisotropic;
uniform sampler2D texture_ao : hint_default_white, filter_linear_mipmap_anisotropic;

// PBR Base Parameters (Rocks: roughness 0.85 - 0.95, metallic 0.0)
uniform vec4 albedo_tint : source_color = vec4(0.85, 0.82, 0.80, 1.0);
uniform vec3 uv_scale = vec3(1.0, 1.0, 1.0);
uniform float normal_scale : hint_range(0.0, 4.0) = 1.6;
uniform float roughness_min : hint_range(0.0, 1.0) = 0.85;
uniform float roughness_max : hint_range(0.0, 1.0) = 0.95;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;

// Weathering - Pacific Northwest Dampness, Moss & Grime
uniform float dampness : hint_range(0.0, 1.0) = 0.60;
uniform float moss_amount : hint_range(0.0, 1.0) = 0.40;
uniform vec4 moss_color : source_color = vec4(0.18, 0.27, 0.12, 1.0);
uniform float moss_roughness : hint_range(0.7, 1.0) = 0.92;
uniform float dirt_amount : hint_range(0.0, 1.0) = 0.30;
uniform vec4 dirt_color : source_color = vec4(0.13, 0.10, 0.08, 1.0);
uniform float dirt_roughness : hint_range(0.7, 1.0) = 0.88;

varying vec3 v_world_pos;
varying vec3 v_world_normal;

void vertex() {
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
	
	// Enforce standardized rock roughness bounds [0.85, 0.95]
	float base_rough = clamp(mix(roughness_min, roughness_max, rough_tex), roughness_min, roughness_max);

	// Organic weathering coordinates
	vec2 world_uv = v_world_pos.xz * 0.8 + v_world_pos.yy * 0.4;
	float weather_noise = fbm2(world_uv);
	
	// 1. Moss Weathering Layer
	// Accumulates on upward surfaces (rain/spores settle on top of rocks)
	float up_facing = clamp(v_world_normal.y, 0.0, 1.0);
	float moss_mask = smoothstep(0.35, 0.85, up_facing + (weather_noise - 0.5) * 0.6);
	moss_mask = clamp(moss_mask * moss_amount * 1.5, 0.0, 1.0);
	
	// 2. Dirt / Grime Crevice Weathering Layer
	// Accumulates in crevices (low AO) and sheltered lower facets
	float crevice_factor = (1.0 - ao_tex) * 0.7 + (1.0 - up_facing) * 0.3;
	float dirt_mask = smoothstep(0.2, 0.7, crevice_factor + (1.0 - weather_noise) * 0.3);
	dirt_mask = clamp(dirt_mask * dirt_amount * (1.0 - moss_mask * 0.8), 0.0, 1.0);
	
	// Blend Dirt and Moss into Base Albedo and Roughness
	vec3 weathered_alb = mix(base_alb, dirt_color.rgb, dirt_mask * 0.85);
	weathered_alb = mix(weathered_alb, moss_color.rgb, moss_mask * 0.90);
	
	float weathered_rough = mix(base_rough, dirt_roughness, dirt_mask);
	weathered_rough = mix(weathered_rough, moss_roughness, moss_mask);
	
	// 3. Dampness / Rain Weathering Layer
	// Rain darkens porous rock and causes water sheen
	weathered_alb *= mix(1.0, 0.68, dampness * 0.85);
	// Dampness lowers roughness on non-mossy stone (wet shiny granite/basalt)
	float wet_sheen_rough = weathered_rough * mix(1.0, 0.55, dampness);
	float final_rough = mix(weathered_rough, wet_sheen_rough, 1.0 - moss_mask * 0.6);
	
	// Wet surfaces have higher specular reflectance to catch moonlight & flashlight
	float final_specular = mix(0.45, 0.82, dampness * 0.75 * (1.0 - moss_mask * 0.5));
	
	ALBEDO = weathered_alb;
	ROUGHNESS = final_rough;
	METALLIC = metallic;
	SPECULAR = final_specular;
	NORMAL_MAP = norm_map;
	NORMAL_MAP_DEPTH = normal_scale;
	AO = ao_tex;
}
