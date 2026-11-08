extends SceneTree

func _init() -> void:
	print("--- BEGIN GRAPHICS & WEATHER DEEP VERIFICATION ---")
	var success := true
	
	# 1. Player Flashlight Verification
	print("[1/5] Verifying Player Flashlight & Inertial Optics...")
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	assert(player_scene != null, "Failed to load player.tscn")
	var player = player_scene.instantiate()
	root.add_child(player)
	await process_frame
	
	var flashlight: SpotLight3D = player.get_node_or_null("Head/Camera3D/Flashlight")
	if not flashlight:
		printerr("FAIL: Flashlight node not found!")
		success = false
	else:
		print("  - Flashlight spot_angle: ", flashlight.spot_angle)
		print("  - Flashlight spot_attenuation: ", flashlight.spot_attenuation)
		print("  - Flashlight light_specular: ", flashlight.light_specular)
		print("  - Flashlight shadow_enabled: ", flashlight.shadow_enabled)
		print("  - Flashlight projector: ", flashlight.light_projector)
		
		if flashlight.spot_angle > 38.0 or flashlight.spot_angle < 30.0:
			printerr("FAIL: Flashlight spot_angle out of realistic cone bounds: ", flashlight.spot_angle)
			success = false
		if flashlight.light_specular > 0.85:
			printerr("FAIL: Flashlight specular is not grounded: ", flashlight.light_specular)
			success = false
		if not flashlight.shadow_enabled:
			printerr("FAIL: Flashlight shadows not enabled!")
			success = false
		if not flashlight.light_projector:
			printerr("FAIL: Flashlight cookie projector is null!")
			success = false
		
		var fill_light: OmniLight3D = flashlight.get_node_or_null("FillLight")
		if not fill_light or fill_light.light_energy > 0.3:
			printerr("FAIL: FillLight missing or too harsh: ", fill_light.light_energy if fill_light else "null")
			success = false
		else:
			print("  - FillLight subtle bounce energy: ", fill_light.light_energy)
	
	# Test flashlight inertial sway direction
	var motion_ev = InputEventMouseMotion.new()
	motion_ev.relative = Vector2(80.0, 40.0)
	player._unhandled_input(motion_ev)
	print("  - Mouse move right (+80.0) -> flashlight_sway_target.x: ", player.flashlight_sway_target.x)
	if player.flashlight_sway_target.x <= 0.0:
		printerr("FAIL: Flashlight sway target X is negative (leads camera instead of lagging behind)!")
		success = false
	else:
		print("  - Flashlight horizontal inertial lag correctly opposes camera turn direction.")
	
	if player.flashlight_sway_target.y <= 0.0:
		printerr("FAIL: Flashlight sway target Y is negative (leads camera pitch instead of lagging behind)!")
		success = false
	else:
		print("  - Flashlight vertical inertial lag correctly opposes camera pitch direction.")
	
	# Test flashlight toggling
	if player.has_method("trigger_flashlight_flicker"):
		print("  - Flashlight flicker logic ready.")
	
	player.queue_free()
	
	# 2. Forest Lighting, Fog & Atmosphere Verification
	print("\n[2/5] Verifying Forest Lighting & Volumetric Atmosphere...")
	var forest_scene: PackedScene = load("res://scenes/world/forest.tscn")
	assert(forest_scene != null, "Failed to load forest.tscn")
	var forest = forest_scene.instantiate()
	root.add_child(forest)
	await process_frame
	
	var world_env: WorldEnvironment = forest.get_node_or_null("WorldEnvironment")
	if not world_env or not world_env.environment:
		printerr("FAIL: WorldEnvironment or Environment missing in forest.tscn")
		success = false
	else:
		var env: Environment = world_env.environment
		print("  - Ambient light energy: ", env.ambient_light_energy)
		print("  - Volumetric fog enabled: ", env.volumetric_fog_enabled)
		print("  - Volumetric fog density: ", env.volumetric_fog_density)
		print("  - Volumetric fog albedo: ", env.volumetric_fog_albedo)
		print("  - Volumetric fog length: ", env.volumetric_fog_length)
		print("  - Volumetric fog emission: ", env.volumetric_fog_emission)
		print("  - Glow bloom: ", env.glow_bloom)
		print("  - Tonemap mode: ", env.tonemap_mode)
		
		if env.ambient_light_energy > 0.35:
			printerr("FAIL: Ambient light energy is too high (>0.35), causing gray wash!")
			success = false
		if not env.volumetric_fog_enabled:
			printerr("FAIL: Volumetric fog is not enabled!")
			success = false
		if env.volumetric_fog_albedo.r > 0.2:
			printerr("FAIL: Volumetric fog albedo is too bright, causing gray wash!")
			success = false
		if env.glow_bloom > 0.08:
			printerr("FAIL: Glow bloom is unrestrained (>0.08)!")
			success = false
	
	var moon: DirectionalLight3D = forest.get_node_or_null("DirectionalLight3D")
	if not moon:
		printerr("FAIL: DirectionalLight3D moonlight missing!")
		success = false
	else:
		print("  - Moonlight energy: ", moon.light_energy)
		print("  - Moonlight shadow enabled: ", moon.shadow_enabled)
		print("  - Moonlight volumetric fog energy: ", moon.light_volumetric_fog_energy)
		print("  - Moonlight directional shadow max distance: ", moon.directional_shadow_max_distance)
		if moon.light_energy > 0.6:
			printerr("FAIL: Moonlight is too harsh (>0.6)!")
			success = false
		if not moon.shadow_enabled:
			printerr("FAIL: Moonlight shadows not enabled!")
			success = false
	
	# 3. WeatherDirector Verification
	print("\n[3/5] Verifying WeatherDirector in Forest...")
	var weather: WeatherDirector = forest.get_node_or_null("WeatherDirector")
	if not weather:
		printerr("FAIL: WeatherDirector node missing in forest.tscn!")
		success = false
	else:
		print("  - WeatherDirector found.")
		print("  - Base wind speed: ", weather.base_wind_speed)
		print("  - Base wind strength: ", weather.base_wind_strength)
		print("  - Wind direction: ", weather.wind_direction)
		print("  - Registered foliage materials count: ", weather.foliage_materials.size())
		if weather.foliage_materials.size() < 2:
			printerr("FAIL: WeatherDirector did not bind foliage and bark materials for dynamic sway!")
			success = false
		
		var mist: GPUParticles3D = weather.get_node_or_null("MistParticles")
		var rain: GPUParticles3D = weather.get_node_or_null("RainParticles")
		if not mist or not rain:
			printerr("FAIL: MistParticles or RainParticles missing in WeatherDirector!")
			success = false
		else:
			print("  - MistParticles emitting: ", mist.emitting, " (amount: ", mist.amount, ")")
			print("  - RainParticles emitting: ", rain.emitting, " (amount: ", rain.amount, ")")
			var rain_mat = rain.process_material as ParticleProcessMaterial
			if rain_mat and rain_mat.particle_flag_align_y:
				print("  - RainParticles aligned along velocity vector (particle_flag_align_y = true).")
			else:
				printerr("FAIL: Rain particles do not have particle_flag_align_y enabled!")
				success = false
		
		# Test gust mechanics & dynamic foliage synchronization
		weather.trigger_gust(2.5, 6.0)
		weather._process_wind_gusts(0.1)
		if not weather.is_gusting:
			printerr("FAIL: WeatherDirector failed to trigger gust!")
			success = false
		else:
			print("  - Gust active. current_wind_speed: ", weather.current_wind_speed, ", current_wind_strength: ", weather.current_wind_strength)
			var needles_mat: ShaderMaterial = load("res://assets/materials/mat_pine_needles.tres")
			var synced_speed = needles_mat.get_shader_parameter("wind_speed")
			if abs(synced_speed - weather.current_wind_speed) > 0.01:
				printerr("FAIL: Needles material wind_speed not synced to WeatherDirector gust: ", synced_speed)
				success = false
			else:
				print("  - Tree needles material dynamically synced to gust speed: ", synced_speed)
	
	forest.queue_free()
	
	# 4. Foliage & Tree Wind Shaders Verification
	print("\n[4/5] Verifying Foliage & Tree Wind Shaders...")
	var foliage_shader: Shader = load("res://assets/materials/foliage_wind.gdshader")
	var tree_shader: Shader = load("res://assets/materials/tree_wind.gdshader")
	var wood_shader: Shader = load("res://assets/materials/wood_weathered.gdshader")
	if not foliage_shader or not tree_shader or not wood_shader:
		printerr("FAIL: One or more shaders failed to load!")
		success = false
	else:
		print("  - foliage_wind.gdshader, tree_wind.gdshader, wood_weathered.gdshader loaded.")
	
	var pine_needles_mat: ShaderMaterial = load("res://assets/materials/mat_pine_needles.tres")
	var pine_bark_mat: ShaderMaterial = load("res://assets/materials/mat_pine_bark.tres")
	if not pine_needles_mat or not pine_bark_mat:
		printerr("FAIL: mat_pine_needles or mat_pine_bark failed to load!")
		success = false
	else:
		var bark_sway = pine_bark_mat.get_shader_parameter("trunk_wind_sway")
		print("  - Pine needles shader: ", pine_needles_mat.shader.resource_path)
		print("  - Pine bark trunk_wind_sway: ", bark_sway)
		if bark_sway == null or float(bark_sway) < 0.99:
			printerr("FAIL: mat_pine_bark trunk_wind_sway is not enabled (trees will detach from stiff trunks)!")
			success = false
		else:
			print("  - Pine bark trunk wind sway synchronized with needle canopy.")
	
	# Test tree archetypes instantiation
	var pine_scene = load("res://scenes/world/pine_tree.tscn")
	var fir_scene = load("res://scenes/world/tree_douglas_fir.tscn")
	var tall_pine_scene = load("res://scenes/world/tree_pine_tall.tscn")
	if not pine_scene or not fir_scene or not tall_pine_scene:
		printerr("FAIL: Tree archetype scenes failed to load!")
		success = false
	else:
		var t1 = pine_scene.instantiate()
		var t2 = fir_scene.instantiate()
		var t3 = tall_pine_scene.instantiate()
		root.add_child(t1)
		root.add_child(t2)
		root.add_child(t3)
		t1.queue_free()
		t2.queue_free()
		t3.queue_free()
		print("  - Living pine and fir tree archetypes instantiated without errors.")
	
	# 5. Full Main Game Scene Multi-Frame Simulation
	print("\n[5/5] Running Main Game Scene Multi-Frame Simulation...")
	var main_scene: PackedScene = load("res://scenes/main/main.tscn")
	if not main_scene:
		printerr("FAIL: main.tscn failed to load!")
		success = false
	else:
		var main_node = main_scene.instantiate()
		root.add_child(main_node)
		
		# Simulate 15 frames so GraphicsSettingsManager applies presets and updates WorldEnvironment
		for i in range(15):
			await process_frame
		
		var forest_node = main_node.get_node_or_null("Forest")
		if not forest_node:
			printerr("FAIL: Forest node missing in Main scene!")
			success = false
		else:
			var active_env = forest_node.get_node("WorldEnvironment").environment
			var active_moon = forest_node.get_node("DirectionalLight3D")
			print("  - Post-initialization Active Fog Density: ", active_env.volumetric_fog_density)
			print("  - Post-initialization Active Fog Length: ", active_env.volumetric_fog_length)
			print("  - Post-initialization Active SSAO Radius: ", active_env.ssao_radius)
			print("  - Post-initialization Active SSAO Intensity: ", active_env.ssao_intensity)
			print("  - Post-initialization Active SSIL Intensity: ", active_env.ssil_intensity)
			print("  - Post-initialization Active Moon Shadow Distance: ", active_moon.directional_shadow_max_distance)
			
			if abs(active_env.volumetric_fog_density - 0.016) > 0.001:
				printerr("FAIL: Active fog density was clobbered by GraphicsSettings: ", active_env.volumetric_fog_density)
				success = false
			if abs(active_env.volumetric_fog_length - 72.0) > 0.5:
				printerr("FAIL: Active fog length was clobbered by GraphicsSettings: ", active_env.volumetric_fog_length)
				success = false
			if abs(active_env.ssao_radius - 2.0) > 0.05:
				printerr("FAIL: Active SSAO radius was clobbered by GraphicsSettings: ", active_env.ssao_radius)
				success = false
			if abs(active_env.ssil_intensity - 0.5) > 0.05:
				printerr("FAIL: Active SSIL intensity was clobbered by GraphicsSettings: ", active_env.ssil_intensity)
				success = false
			if abs(active_moon.directional_shadow_max_distance - 75.0) > 0.5:
				printerr("FAIL: Active moonlight shadow distance was clobbered: ", active_moon.directional_shadow_max_distance)
				success = false
		
		main_node.queue_free()
		print("  - Main scene clean cleanup.")
	
	if success:
		print("\n*** ALL GRAPHICS & WEATHER VERIFICATIONS PASSED ***")
		quit(0)
	else:
		printerr("\n*** SOME VERIFICATIONS FAILED ***")
		quit(1)
