class_name Sasquatch
extends CharacterBody3D

## Cryptid stalker entity for The Black Pines.
## Watches from the shadows, flickers player equipment, and vanishes into the fog.

enum State { STALKING, ALERTED, RETREATING, GONE }

@export var stalk_distance_trigger: float = 14.0
@export var retreat_speed: float = 7.5

var current_state: State = State.STALKING
var player_ref: Player = null
var look_at_timer: float = 0.0
var retreat_timer: float = 0.0

@onready var eye_glow_left: OmniLight3D = $Head/EyeLeft
@onready var eye_glow_right: OmniLight3D = $Head/EyeRight
@onready var visual_root: Node3D = $Visuals
@onready var anim_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
	if anim_player:
		anim_player.play("stalking")

	# Find player in scene tree
	await get_tree().process_frame
	player_ref = get_tree().get_first_node_in_group("player")
	if not player_ref:
		# Fallback search
		var main = get_parent().get_parent()
		if main and main.has_node("Player"):
			player_ref = main.get_node("Player")

func _physics_process(delta: float) -> void:
	if not player_ref:
		return

	match current_state:
		State.STALKING:
			_process_stalking(delta)
		State.ALERTED:
			_process_alerted(delta)
		State.RETREATING:
			_process_retreating(delta)

func _process_stalking(delta: float) -> void:
	# Ensure stalking animation is active
	if anim_player and anim_player.current_animation != "stalking":
		anim_player.play("stalking")

	# Slowly orient towards the player
	var target_pos: Vector3 = player_ref.global_position
	target_pos.y = global_position.y
	var target_basis = Basis.looking_at(target_pos - global_position, Vector3.UP)
	global_basis = global_basis.slerp(target_basis, delta * 2.0)

	var dist_to_player: float = global_position.distance_to(player_ref.global_position)

	# Check if player is approaching too close
	if dist_to_player <= stalk_distance_trigger:
		_trigger_encounter()
		return

	# Check if player is looking directly at creature with flashlight on
	if player_ref.flashlight and player_ref.flashlight.visible:
		var cam = player_ref.camera
		if cam:
			var to_creature = (global_position + Vector3(0, 1.8, 0)) - cam.global_position
			var forward = -cam.global_transform.basis.z
			var dot = forward.dot(to_creature.normalized())
			if dot > 0.94 and dist_to_player < 36.0:
				look_at_timer += delta
				if look_at_timer >= 0.7:
					_trigger_encounter()
			else:
				look_at_timer = max(0.0, look_at_timer - delta)

func _trigger_encounter() -> void:
	if current_state != State.STALKING:
		return
	current_state = State.ALERTED

	if anim_player:
		anim_player.play("charge")

	# Creature roar
	if AudioDirector.instance:
		AudioDirector.instance.play_cryptid_roar(global_position)

	# Flicker player's flashlight and trigger notification
	if player_ref:
		player_ref.trigger_flashlight_flicker(2.2)
		player_ref.show_notification("SOMETHING IS WATCHING FROM THE PINES")

	# Brief freeze before rapid retreat
	await get_tree().create_timer(0.4).timeout
	current_state = State.RETREATING
	retreat_timer = 2.8

func _process_alerted(_delta: float) -> void:
	pass

func _process_retreating(delta: float) -> void:
	if anim_player and anim_player.current_animation != "retreat":
		anim_player.play("retreat")

	retreat_timer -= delta
	# Move backward away from player
	if player_ref:
		var away_dir = (global_position - player_ref.global_position).normalized()
		away_dir.y = 0.0
		velocity = away_dir * retreat_speed
		move_and_slide()

	# Fade eye glow and vanish into fog
	var alpha = clamp(retreat_timer / 1.5, 0.0, 1.0)
	if eye_glow_left:
		eye_glow_left.light_energy = alpha * 0.8
	if eye_glow_right:
		eye_glow_right.light_energy = alpha * 0.8

	if retreat_timer <= 0.0:
		current_state = State.GONE
		queue_free()
