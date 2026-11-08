class_name Player
extends CharacterBody3D

## First-Person Survival Horror Controller for The Black Pines.

signal stamina_changed(current: float, maximum: float)
signal health_changed(current: float, maximum: float)
signal flashlight_toggled(is_on: bool)
signal interaction_prompt_changed(text: String)
signal inspection_displayed(title: String, body: String)
signal inventory_updated(inventory: Dictionary)
signal notification_posted(message: String)

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
@export var flashlight_sway_speed: float = 12.0

var stamina: float = 100.0
var health: float = 100.0
var is_sprinting: bool = false
var stamina_timer: float = 0.0
var bob_phase: float = 0.0
var default_camera_pos: Vector3 = Vector3.ZERO
var inventory: Dictionary = {}

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
	health_changed.emit(health, 100.0)
	if flashlight:
		flashlight_toggled.emit(flashlight.visible)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		head.rotate_x(-event.relative.y * mouse_sensitivity)
		head.rotation.x = clamp(head.rotation.x, deg_to_rad(-85.0), deg_to_rad(85.0))
	
	if event.is_action_pressed("toggle_pause"):
		if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
			
	if event is InputEventMouseButton and event.pressed and Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

	if event.is_action_pressed("toggle_flashlight"):
		if flashlight:
			flashlight.visible = not flashlight.visible
			flashlight_toggled.emit(flashlight.visible)

	if event.is_action_pressed("interact"):
		if current_interactable and current_interactable.is_usable:
			current_interactable.interact(self)

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

	# Head bob
	_process_head_bob(delta, direction.length() > 0.1 and is_on_floor())
	
	# Check interactables
	_process_interaction()

func _process_head_bob(delta: float, is_moving: bool) -> void:
	if not camera:
		return
	if is_moving:
		var speed_factor: float = 1.4 if is_sprinting else 1.0
		bob_phase += delta * bob_frequency * speed_factor * TAU
		var target_y: float = default_camera_pos.y + sin(bob_phase) * bob_amplitude
		var target_x: float = default_camera_pos.x + cos(bob_phase * 0.5) * (bob_amplitude * 0.5)
		camera.position.y = lerp(camera.position.y, target_y, delta * 10.0)
		camera.position.x = lerp(camera.position.x, target_x, delta * 10.0)
	else:
		bob_phase = 0.0
		camera.position = camera.position.lerp(default_camera_pos, delta * 8.0)

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
		"toggle_pause": KEY_ESCAPE
	}
	for action in default_actions:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			var ev = InputEventKey.new()
			ev.physical_keycode = default_actions[action]
			InputMap.action_add_event(action, ev)
