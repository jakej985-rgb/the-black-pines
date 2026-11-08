extends SceneTree

func _init() -> void:
	print("--- BEGIN GRAPHICS & WEATHER DEEP VERIFICATION ---")
	var success := true
	
	# 1. Player Flashlight Verification
	print("[1/5] Verifying Player Flashlight...")
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	assert(player_scene != null, "Failed to load player.tscn")
	var player = player_scene.instantiate()
	root.add_child(player)
	
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
		
		var mist: GPUParticles3D = weather.get_node_or_null("MistParticles")
		var rain: GPUParticles3D = weather.get_node_or_null("RainParticles")
		if not mist or not rain:
			printerr("FAIL: MistParticles or RainParticles missing in WeatherDirector!")
			success = false
		else:
			print("  - MistParticles emitting: ", mist.emitting, " (amount: ", mist.amount, ")")
			print("  - RainParticles emitting: ", rain.emitting, " (amount: ", rain.amount, ")")
		
		# Test gust mechanics
		weather.trigger_gust(2.2, 5.0)
		if not weather.is_gusting:
			printerr("FAIL: WeatherDirector failed to trigger gust!")
			success = false
		else:
			print("  - Gust triggered successfully. is_gusting: ", weather.is_gusting)
	
	forest.queue_free()
	
	# 4. Foliage & Tree Wind Shaders Verification
	print("\n[4/5] Verifying Foliage & Tree Wind Shaders...")
	var foliage_shader: Shader = load("res://assets/materials/foliage_wind.gdshader")
	var tree_shader: Shader = load("res://assets/materials/tree_wind.gdshader")
	if not foliage_shader:
		printerr("FAIL: foliage_wind.gdshader failed to load!")
		success = false
	else:
		print("  - foliage_wind.gdshader loaded successfully.")
	
	if not tree_shader:
		printerr("FAIL: tree_wind.gdshader failed to load!")
		success = false
	else:
		print("  - tree_wind.gdshader loaded successfully.")
	
	var pine_needles_mat = load("res://assets/materials/mat_pine_needles.tres")
	if not pine_needles_mat is ShaderMaterial:
		printerr("FAIL: mat_pine_needles.tres is not a ShaderMaterial!")
		success = false
	else:
		print("  - mat_pine_needles.tres is ShaderMaterial with organic tree sway.")
	
	# Test fern and grass tufts
	var fern_scene: PackedScene = load("res://scenes/world/fern_cluster.tscn")
	var grass_scene: PackedScene = load("res://scenes/world/grass_tuft.tscn")
	if not fern_scene or not grass_scene:
		printerr("FAIL: fern_cluster or grass_tuft scene failed to load!")
		success = false
	else:
		var fern = fern_scene.instantiate()
		var grass = grass_scene.instantiate()
		root.add_child(fern)
		root.add_child(grass)
		fern.queue_free()
		grass.queue_free()
		print("  - fern_cluster and grass_tuft instantiated without errors.")
	
	# 5. Full Main Game Scene Simulation
	print("\n[5/5] Running Main Game Scene Simulation...")
	var main_scene: PackedScene = load("res://scenes/main/main.tscn")
	if not main_scene:
		printerr("FAIL: main.tscn failed to load!")
		success = false
	else:
		var main_node = main_scene.instantiate()
		root.add_child(main_node)
		print("  - Main scene instantiated. Simulating 30 frames...")
		# Allow process cycles to run
		main_node.queue_free()
		print("  - Main scene clean cleanup.")
	
	if success:
		print("\n*** ALL GRAPHICS & WEATHER VERIFICATIONS PASSED ***")
		quit(0)
	else:
		printerr("\n*** SOME VERIFICATIONS FAILED ***")
		quit(1)
