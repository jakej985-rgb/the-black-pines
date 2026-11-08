class_name Player
extends CharacterBody3D

## First-Person Survival Horror Controller for The Black Pines.

signal stamina_changed(current: float, maximum: float)
signal health_changed(current: float, maximum: float)
signal flashlight_toggled(is_on: bool)
signal flashlight_battery_changed(current: float, maximum: float)
signal interaction_prompt_changed(text: String)
signal inspection_displayed(title: String, body: String)
signal inventory_updated(inventory: Dictionary)
signal notification_posted(message: String)

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const ActiveFlareScene = preload("res://scenes/interactables/active_flare.tscn")
const DeployableTrapScene = preload("res://scenes/interactables/deployable_trap.tscn")
const HealthComponentClass = preload("res://scripts/player/health_component.gd")

var health_component = null

@export_group("Movement")
@export var walk_speed: float = 3.2
@export var sprint_speed: float = 6.0
@export var jump_velocity: float = 4.2
@export var acceleration: float = 12.0
@export var deceleration: float = 14.0
@export var mouse_sensitivity: float = 0.0022

@export_group("Stamina")
@export var max_stamina: float = 100.0
@export var stamina_drain_rate: float = 22.0
@export var stamina_regen_rate: float = 16.0
@export var stamina_regen_delay: float = 1.2

@export_group("Head Bobbing")
@export var bob_frequency: float = 2.4
@export var bob_amplitude: float = 0.045

@export_group("Flashlight")
@export var flashlight_sway_speed: float = 10.0
@export var flashlight_sway_amount: float = 0.04
@export var max_battery: float = 100.0
@export var battery: float = 100.0
@export var battery_drain_rate: float = 0.8
@export var low_battery_threshold: float = 20.0

var stamina: float = 100.0
var health: float = 100.0
var is_sprinting: bool = false
var stamina_timer: float = 0.0
var bob_phase: float = 0.0
var default_camera_pos: Vector3 = Vector3.ZERO
var inventory: Dictionary = {}
var step_dist_accum: float = 0.0
var is_flickering: bool = false
var was_on_floor: bool = true
var landing_offset: float = 0.0
var breathing_time: float = 0.0
var current_strafe: float = 0.0
var flashlight_sway: Vector2 = Vector2.ZERO
var flashlight_sway_target: Vector2 = Vector2.ZERO

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 9.8)

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var flashlight: SpotLight3D = $Head/Camera3D/Flashlight
@onready var interact_ray: RayCast3D = $Head/Camera3D/InteractRay

var current_interactable: Interactable = null

func _ready() -> void:
	_ensure_default_input_actions()
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	if camera:
		default_camera_pos = camera.position
	stamina = max_stamina
	stamina_changed.emit(stamina, max_stamina)

	health_component = get_node_or_null("HealthComponent")
	if not health_component:
		health_component = HealthComponentClass.new()
		health_component.name = "HealthComponent"
		add_child(health_component)

	health_component.health_changed.connect(func(c, m):
		health = c
		health_changed.emit(c, m)
	)
	health_component.player_died.connect(_on_player_died)
	health_component.bleed_started.connect(func():
		show_notification("HEMORRHAGE: You are bleeding! Use Antiseptic Bandage [3].")
	)

	health_changed.emit(health, 100.0)
	flashlight_battery_changed.emit(battery, max_battery)
	if flashlight:
		flashlight_toggled.emit(flashlight.visible)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and (Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED or DisplayServer.get_name() == "headless"):
		rotate_y(-event.relative.x * mouse_sensitivity)
		head.rotate_x(-event.relative.y * mouse_sensitivity)
		head.rotation.x = clamp(head.rotation.x, deg_to_rad(-85.0), deg_to_rad(85.0))
		flashlight_sway_target.x = clamp(flashlight_sway_target.x + event.relative.x * 0.0006, -flashlight_sway_amount, flashlight_sway_amount)
		flashlight_sway_target.y = clamp(flashlight_sway_target.y + event.relative.y * 0.0006, -flashlight_sway_amount, flashlight_sway_amount)
	
	if event.is_action_pressed("toggle_pause"):
		if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
			
	if event is InputEventMouseButton and event.pressed and Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	if event.is_action_pressed("toggle_flashlight"):
		if flashlight:
			if not flashlight.visible and battery <= 0.0:
				show_notification("Flashlight battery empty. Press [R] to reload.")
			else:
				flashlight.visible = not flashlight.visible
				flashlight_toggled.emit(flashlight.visible)
				if AudioDirector.instance:
					AudioDirector.instance.play_click()

	if event.is_action_pressed("reload_battery"):
		reload_flashlight_battery()

	if event.is_action_pressed("interact"):
		if current_interactable and current_interactable.is_usable:
			current_interactable.interact(self)

	if event.is_action_pressed("quick_flare"):
		deploy_flare()
	elif event.is_action_pressed("quick_trap"):
		deploy_trap()
	elif event.is_action_pressed("quick_heal"):
		use_antiseptic_bandage()

func _physics_process(delta: float) -> void:
	# Gravity
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor() and stamina > 10.0:
		velocity.y = jump_velocity
		stamina -= 10.0
		stamina_timer = stamina_regen_delay
		stamina_changed.emit(stamina, max_stamina)

	# Movement direction
	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_backward")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	# Sprint logic
	var wants_sprint: bool = Input.is_action_pressed("sprint") and input_dir.length() > 0.1 and is_on_floor()
	if wants_sprint and stamina > 0.0:
		is_sprinting = true
		stamina = max(0.0, stamina - stamina_drain_rate * delta)
		stamina_timer = stamina_regen_delay
		stamina_changed.emit(stamina, max_stamina)
	else:
		is_sprinting = false
		if stamina < max_stamina:
			if stamina_timer > 0.0:
				stamina_timer -= delta
			else:
				stamina = min(max_stamina, stamina + stamina_regen_rate * delta)
				stamina_changed.emit(stamina, max_stamina)

	var current_speed: float = sprint_speed if (is_sprinting and stamina > 0.0) else walk_speed

	if direction:
		velocity.x = move_toward(velocity.x, direction.x * current_speed, acceleration * delta * 4.0)
		velocity.z = move_toward(velocity.z, direction.z * current_speed, acceleration * delta * 4.0)
	else:
		velocity.x = move_toward(velocity.x, 0, deceleration * delta * 4.0)
		velocity.z = move_toward(velocity.z, 0, deceleration * delta * 4.0)

	move_and_slide()

	# Out-of-bounds fall recovery
	if global_position.y < -12.0:
		_respawn_from_fall()

	# Footstep audio
	var horiz_vel := Vector2(velocity.x, velocity.z).length()
	if is_on_floor() and horiz_vel > 0.3:
		step_dist_accum += horiz_vel * delta
		var threshold: float = 1.6 if is_sprinting else 2.2
		if step_dist_accum >= threshold:
			step_dist_accum = 0.0
			if AudioDirector.instance:
				var surface = _detect_ground_surface()
				AudioDirector.instance.play_footstep(is_sprinting, surface)
				if stamina < 25.0:
					AudioDirector.instance.play_heavy_breathing()
	else:
		step_dist_accum = 0.0

	# Landing impact
	if not was_on_floor and is_on_floor():
		landing_offset = -0.075
		if AudioDirector.instance:
			AudioDirector.instance.play_footstep(false)
	was_on_floor = is_on_floor()
	landing_offset = lerp(landing_offset, 0.0, delta * 9.0)

	# Camera strafe banking
	current_strafe = lerp(current_strafe, input_dir.x, delta * 8.0)
	if camera:
		camera.rotation.z = -current_strafe * deg_to_rad(1.6)

	# Head bob & breathing
	_process_head_bob(delta, direction.length() > 0.1 and is_on_floor())
	
	# Flashlight inertial sway & battery drain
	if flashlight:
		flashlight_sway = flashlight_sway.lerp(flashlight_sway_target, delta * flashlight_sway_speed)
		flashlight_sway_target = flashlight_sway_target.lerp(Vector2.ZERO, delta * 5.0)
		flashlight.rotation.y = flashlight_sway.x
		flashlight.rotation.x = flashlight_sway.y

		if flashlight.visible:
			battery = max(0.0, battery - battery_drain_rate * delta)
			flashlight_battery_changed.emit(battery, max_battery)
			if battery <= 0.0:
				flashlight.visible = false
				flashlight_toggled.emit(false)
				show_notification("Flashlight battery died! Reload with [R].")
			elif battery <= low_battery_threshold and randf() < delta * 0.25:
				trigger_flashlight_flicker(0.35)
	
	# Check interactables
	_process_interaction()

func _process_head_bob(delta: float, is_moving: bool) -> void:
	if not camera:
		return
	if is_moving:
		breathing_time = 0.0
		var speed_factor: float = 1.4 if is_sprinting else 1.0
		bob_phase += delta * bob_frequency * speed_factor * TAU
		var target_y: float = default_camera_pos.y + sin(bob_phase) * bob_amplitude + landing_offset
		var target_x: float = default_camera_pos.x + cos(bob_phase * 0.5) * (bob_amplitude * 0.5)
		camera.position.y = lerp(camera.position.y, target_y, delta * 10.0)
		camera.position.x = lerp(camera.position.x, target_x, delta * 10.0)
	else:
		bob_phase = 0.0
		breathing_time += delta
		var breath_sway_y: float = sin(breathing_time * 1.3) * 0.007
		var breath_sway_x: float = cos(breathing_time * 0.65) * 0.004
		var rest_pos = default_camera_pos + Vector3(breath_sway_x, breath_sway_y + landing_offset, 0)
		camera.position = camera.position.lerp(rest_pos, delta * 6.0)


func _process_interaction() -> void:
	if not interact_ray:
		return
	if interact_ray.is_colliding():
		var collider = interact_ray.get_collider()
		if collider is Interactable and collider.is_usable:
			if current_interactable != collider:
				current_interactable = collider
				interaction_prompt_changed.emit(collider.get_prompt())
			return
	
	if current_interactable != null:
		current_interactable = null
		interaction_prompt_changed.emit("")

func show_inspection_dialog(title: String, text: String) -> void:
	inspection_displayed.emit(title, text)

func show_notification(message: String) -> void:
	notification_posted.emit(message)

func add_inventory_item(item_name: String, qty: int = 1) -> void:
	if not inventory.has(item_name):
		inventory[item_name] = 0
	inventory[item_name] += qty
	show_notification("+%d %s (Total: %d)" % [qty, item_name, inventory[item_name]])
	inventory_updated.emit(inventory)
	if AudioDirector.instance:
		AudioDirector.instance.play_pickup()

func trigger_flashlight_flicker(duration: float = 1.6) -> void:
	if is_flickering or not flashlight or not flashlight.visible:
		return
	is_flickering = true
	var timer = 0.0
	while timer < duration:
		if not is_inside_tree():
			break
		flashlight.visible = not flashlight.visible
		if AudioDirector.instance and randf() > 0.5:
			AudioDirector.instance.play_click()
		var wait_time: float = randf_range(0.04, 0.16)
		timer += wait_time
		await get_tree().create_timer(wait_time).timeout
	if flashlight:
		flashlight.visible = true
	is_flickering = false

func _ensure_default_input_actions() -> void:
	var default_actions = {
		"move_forward": KEY_W,
		"move_backward": KEY_S,
		"move_left": KEY_A,
		"move_right": KEY_D,
		"sprint": KEY_SHIFT,
		"jump": KEY_SPACE,
		"interact": KEY_E,
		"toggle_flashlight": KEY_F,
		"toggle_pause": KEY_ESCAPE,
		"toggle_journal": KEY_J,
		"toggle_inventory": KEY_TAB,
		"quick_flare": KEY_1,
		"quick_trap": KEY_2,
		"quick_heal": KEY_3,
		"reload_battery": KEY_R
	}
	for action in default_actions:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			var ev = InputEventKey.new()
			ev.physical_keycode = default_actions[action]
			InputMap.action_add_event(action, ev)

func take_damage(amount: float, cause_bleed: bool = false, source: String = "") -> void:
	if health_component:
		health_component.take_damage(amount, cause_bleed, source)
	else:
		health = max(0.0, health - amount)
		health_changed.emit(health, 100.0)
	trigger_flashlight_flicker(0.8)

func use_antiseptic_bandage() -> bool:
	if not health_component:
		return false
	var ok = health_component.apply_antiseptic_bandage()
	if ok:
		show_notification("Treated lacerations with Antiseptic Bandage (+40 HP). Bleeding stopped.")
		if AudioDirector.instance:
			AudioDirector.instance.play_pickup()
	else:
		show_notification("No Antiseptic Bandages available in inventory.")
	return ok

func reload_flashlight_battery() -> bool:
	if battery >= max_battery:
		show_notification("Flashlight battery is already fully charged.")
		return false

	var inv = InventoryManagerClass.instance
	if not inv or not inv.has_item("battery_pack", 1):
		show_notification("No replacement D-Cell batteries in inventory.")
		return false

	if not inv.remove_item("battery_pack", 1):
		return false

	battery = max_battery
	flashlight_battery_changed.emit(battery, max_battery)
	show_notification("Inserted fresh D-Cell battery (100%).")
	if AudioDirector.instance:
		AudioDirector.instance.play_click()
	return true

func _on_player_died() -> void:
	show_notification("CRITICAL INJURY: You collapsed in the freezing fog...")
	velocity = Vector3.ZERO
	await get_tree().create_timer(1.2).timeout
	global_position = Vector3(0.0, 1.2, 5.0)
	if health_component:
		health_component.recover()
	trigger_flashlight_flicker(2.0)
	show_notification("You awaken revived near Ranger Station #04.")

func _respawn_from_fall() -> void:
	global_position = Vector3(0.0, 1.2, 5.0)
	velocity = Vector3.ZERO
	trigger_flashlight_flicker(1.5)
	notification_posted.emit("The dense fog and steep ravine drop turn you back towards Ranger Station #04.")

func _find_ground_placement(max_dist: float = 2.8) -> Dictionary:
	var world3d = get_world_3d()
	if not world3d:
		return {}
	var space_state = world3d.direct_space_state
	var cam_forward = -camera.global_transform.basis.z if camera else -transform.basis.z
	var ray_origin = (camera.global_position if camera else global_position) + cam_forward * 0.6
	var ray_end = ray_origin + cam_forward * (max_dist - 0.6) + Vector3(0, -3.5, 0)

	var query = PhysicsRayQueryParameters3D.create(ray_origin, ray_end)
	query.exclude = [self.get_rid()]
	return space_state.intersect_ray(query)

func deploy_flare() -> bool:
	var inv = InventoryManagerClass.instance
	if not inv or not inv.has_item("road_flare", 1):
		show_notification("No road flares in inventory.")
		return false

	var hit = _find_ground_placement(2.8)
	var spawn_pos: Vector3
	if not hit.is_empty():
		var normal: Vector3 = hit.get("normal", Vector3.UP)
		if normal.y < 0.4:
			show_notification("Cannot deploy flare: surface too steep.")
			return false
		spawn_pos = hit["position"] + Vector3(0, 0.05, 0)
	else:
		# Fallback placement directly in front of feet if on floor
		spawn_pos = global_position - transform.basis.z * 1.2 + Vector3(0, 0.05, 0)

	if not inv.remove_item("road_flare", 1):
		show_notification("Failed to retrieve flare from inventory.")
		return false

	var flare = ActiveFlareScene.instantiate()
	var parent_node = get_parent() if get_parent() else self
	parent_node.add_child(flare)
	flare.global_position = spawn_pos

	show_notification("Distress Flare deployed and burning!")
	if AudioDirector.instance:
		AudioDirector.instance.play_click()
	return true

func deploy_trap() -> bool:
	var inv = InventoryManagerClass.instance
	if not inv or not inv.has_item("trap_spike", 1):
		show_notification("No spike traps in inventory. Craft one via [Tab].")
		return false

	var hit = _find_ground_placement(2.5)
	var spawn_pos: Vector3
	if not hit.is_empty():
		var normal: Vector3 = hit.get("normal", Vector3.UP)
		if normal.y < 0.65:
			show_notification("Cannot deploy trap: ground is too steep.")
			return false
		spawn_pos = hit["position"]
	else:
		spawn_pos = global_position - transform.basis.z * 1.5

	# Check for overlapping existing traps within 1.4m
	for existing in get_tree().get_nodes_in_group("traps"):
		if existing is Node3D and existing.global_position.distance_to(spawn_pos) < 1.4:
			show_notification("Cannot place trap: too close to an existing trap.")
			return false

	if not inv.remove_item("trap_spike", 1):
		show_notification("Failed to retrieve trap from inventory.")
		return false

	var trap = DeployableTrapScene.instantiate()
	var parent_node = get_parent() if get_parent() else self
	parent_node.add_child(trap)
	trap.global_position = spawn_pos

	show_notification("Improvised Spike Trap armed and deployed!")
	if AudioDirector.instance:
		AudioDirector.instance.play_pickup()
	return true

func _detect_ground_surface() -> int:
	var world3d = get_world_3d()
	if not world3d:
		return 0 # PINE_NEEDLES
	var space_state = world3d.direct_space_state
	var query = PhysicsRayQueryParameters3D.create(global_position + Vector3(0, 0.4, 0), global_position + Vector3(0, -1.2, 0))
	query.exclude = [self.get_rid()]
	var result = space_state.intersect_ray(query)
	if result.is_empty():
		return 0 # PINE_NEEDLES

	var collider = result.get("collider")
	if collider:
		var name_str = (collider.name + " " + (collider.get_parent().name if collider.get_parent() else "")).to_lower()
		if name_str.contains("wood") or name_str.contains("porch") or name_str.contains("cabin") or name_str.contains("step") or name_str.contains("floor") or name_str.contains("plank"):
			return 1 # WOOD
		if name_str.contains("rock") or name_str.contains("stone") or name_str.contains("boulder"):
			return 3 # STONE
		if name_str.contains("mud") or name_str.contains("marsh") or name_str.contains("wet") or name_str.contains("water"):
			return 2 # MUD

	return 0 # PINE_NEEDLES
