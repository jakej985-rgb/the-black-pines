class_name WeatherDirector
extends Node3D

## Dynamic Forest Weather & Atmospheric Motion Director for The Black Pines.
## Coordinates PNW wind dynamics, sinusoidal gusting, drifting forest mist,
## and intermittent cold mountain rainfall.

static var instance: WeatherDirector = null

@export_group("Wind Dynamics")
@export var wind_direction: Vector2 = Vector2(0.85, 0.52).normalized()
@export var base_wind_speed: float = 1.2
@export var base_wind_strength: float = 0.08
@export var gust_interval_min: float = 16.0
@export var gust_interval_max: float = 32.0
@export var gust_duration: float = 7.5
@export var gust_peak_multiplier: float = 2.2

@export_group("Weather Effects")
@export var rain_enabled: bool = true
@export var mist_enabled: bool = true
@export var base_rain_intensity: float = 0.4

var current_wind_speed: float = 1.2
var current_wind_strength: float = 0.08
var last_synced_wind_speed: float = -1.0
var last_synced_wind_strength: float = -1.0
var gust_intensity: float = 0.0
var time_accum: float = 0.0

var next_gust_timer: float = 12.0
var gust_elapsed: float = 0.0
var is_gusting: bool = false

var weather_cycle_time: float = 0.0
var target_rain_ratio: float = 0.35

var player_node: Node3D = null
var foliage_materials: Array[ShaderMaterial] = []

@onready var mist_particles: GPUParticles3D = get_node_or_null("MistParticles")
@onready var rain_particles: GPUParticles3D = get_node_or_null("RainParticles")

func _enter_tree() -> void:
	instance = self
	_init_foliage_materials()

func _ready() -> void:
	current_wind_speed = base_wind_speed
	current_wind_strength = base_wind_strength
	_init_foliage_materials()
	_find_player()
	
	if mist_particles:
		mist_particles.emitting = mist_enabled
	if rain_particles:
		rain_particles.emitting = rain_enabled
		rain_particles.amount_ratio = base_rain_intensity

func _init_foliage_materials() -> void:
	var needle_mat = load("res://assets/materials/mat_pine_needles.tres")
	if needle_mat is ShaderMaterial and not foliage_materials.has(needle_mat):
		foliage_materials.append(needle_mat)
	var bark_mat = load("res://assets/materials/mat_pine_bark.tres")
	if bark_mat is ShaderMaterial and not foliage_materials.has(bark_mat):
		foliage_materials.append(bark_mat)

func register_foliage_material(mat: ShaderMaterial) -> void:
	if mat and not foliage_materials.has(mat):
		foliage_materials.append(mat)
		mat.set_shader_parameter("wind_speed", current_wind_speed)
		mat.set_shader_parameter("wind_strength", current_wind_strength)

func _process(delta: float) -> void:
	time_accum += delta
	weather_cycle_time += delta
	
	# Keep weather effects centered around player
	_update_player_tracking(delta)
	
	# Update wind gusts and turbulence
	_process_wind_gusts(delta)
	
	# Periodic subtle shifting in rain intensity (intermittent PNW showers)
	_process_weather_cycles(delta)

func _update_player_tracking(delta: float) -> void:
	# Optimization: Cache player_node and only search scene tree when invalid
	if not player_node or not is_instance_valid(player_node):
		_find_player()
		if not player_node or not is_instance_valid(player_node):
			return
	
	# Follow player horizontally
	global_position.x = player_node.global_position.x
	global_position.z = player_node.global_position.z
	if abs(global_position.y - player_node.global_position.y) > 6.0:
		global_position.y = player_node.global_position.y
	else:
		global_position.y = lerp(global_position.y, player_node.global_position.y, delta * 5.0)

func _find_player() -> void:
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player_node = players[0] as Node3D
	else:
		var cam = get_viewport().get_camera_3d() if get_viewport() else null
		if cam:
			player_node = cam
	
	if player_node and is_instance_valid(player_node):
		global_position = player_node.global_position

func _process_wind_gusts(delta: float) -> void:
	var was_gusting = is_gusting
	if not is_gusting:
		next_gust_timer -= delta
		if next_gust_timer <= 0.0:
			_start_wind_gust()
	else:
		gust_elapsed += delta
		var progress: float = gust_elapsed / gust_duration
		if progress >= 1.0:
			is_gusting = false
			gust_intensity = 0.0
			next_gust_timer = randf_range(gust_interval_min, gust_interval_max)
		else:
			# Smooth sinusoidal bell curve envelope for gust
			gust_intensity = sin(progress * PI)
	
	# Only update shaders and particle materials when gusting or when gust just ended
	if is_gusting or was_gusting:
		var speed_boost: float = gust_intensity * (gust_peak_multiplier - 1.0)
		current_wind_speed = base_wind_speed * (1.0 + speed_boost)
		current_wind_strength = base_wind_strength * (1.0 + gust_intensity * 1.5)
		
		# Synchronize active foliage wind shaders only when values have measurably changed
		# Optimization: Prevents dirtying shader parameters across all materials every frame
		if abs(current_wind_speed - last_synced_wind_speed) > 0.005 or abs(current_wind_strength - last_synced_wind_strength) > 0.001:
			last_synced_wind_speed = current_wind_speed
			last_synced_wind_strength = current_wind_strength
			for mat in foliage_materials:
				if mat:
					mat.set_shader_parameter("wind_speed", current_wind_speed)
					mat.set_shader_parameter("wind_strength", current_wind_strength)
		
		# Accelerate drifting mist during gusts
		if mist_particles and mist_particles.process_material is ParticleProcessMaterial:
			var mist_mat = mist_particles.process_material as ParticleProcessMaterial
			mist_mat.initial_velocity_min = 0.5 * (1.0 + gust_intensity * 1.5)
			mist_mat.initial_velocity_max = 1.4 * (1.0 + gust_intensity * 1.5)
		
		# Tilt and speed up falling rain with wind gusts
		if rain_particles and rain_particles.process_material is ParticleProcessMaterial:
			var rain_mat = rain_particles.process_material as ParticleProcessMaterial
			var slant_x = wind_direction.x * (0.28 + gust_intensity * 0.35)
			var slant_z = wind_direction.y * (0.18 + gust_intensity * 0.35)
			rain_mat.direction = Vector3(slant_x, -1.0, slant_z).normalized()
			rain_mat.initial_velocity_min = 18.0 * (1.0 + gust_intensity * 0.35)
			rain_mat.initial_velocity_max = 24.0 * (1.0 + gust_intensity * 0.35)
	
	# Modulate AudioDirector wind if active
	if AudioDirector.instance and AudioDirector.instance.wind_player:
		var target_vol: float = -12.0 + (gust_intensity * 3.5)
		AudioDirector.instance.wind_player.volume_db = lerp(
			AudioDirector.instance.wind_player.volume_db,
			target_vol,
			delta * 2.0
		)

func _start_wind_gust() -> void:
	is_gusting = true
	gust_elapsed = 0.0

func _process_weather_cycles(delta: float) -> void:
	if not rain_enabled or not rain_particles:
		return
	
	# Long-wave subtle shift between misty lull and cold drizzle
	var wave: float = sin(weather_cycle_time * 0.05) * 0.5 + 0.5 # 0.0 to 1.0
	target_rain_ratio = clamp(base_rain_intensity * (0.3 + wave * 0.9), 0.05, 1.0)
	
	# Slightly increase rainfall during strong wind gusts
	if gust_intensity > 0.1:
		target_rain_ratio = min(1.0, target_rain_ratio + gust_intensity * 0.25)
	
	if abs(rain_particles.amount_ratio - target_rain_ratio) > 0.03:
		rain_particles.amount_ratio = lerp(rain_particles.amount_ratio, target_rain_ratio, delta * 0.8)

func trigger_gust(multiplier: float = 2.5, duration: float = 8.0) -> void:
	gust_peak_multiplier = multiplier
	gust_duration = duration
	_start_wind_gust()

func set_rain_active(active: bool) -> void:
	rain_enabled = active
	if rain_particles:
		rain_particles.emitting = active

func set_mist_active(active: bool) -> void:
	mist_enabled = active
	if mist_particles:
		mist_particles.emitting = active
