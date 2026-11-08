class_name Sasquatch
extends CharacterBody3D

## Cryptid stalker entity for The Black Pines.
## Features comprehensive state-driven encounter behavior:
## IDLE_ROAM, STALKING, INVESTIGATING (noise), FLANKING, ALERTED, ATTACK_CHARGE, RETREATING, STAGGERED, FEARED, GONE.

enum State {
	IDLE_ROAM,
	STALKING,
	INVESTIGATING,
	FLANKING,
	ALERTED,
	ATTACK_CHARGE,
	RETREATING,
	STAGGERED,
	FEARED,
	GONE
}

signal state_changed(old_state: State, new_state: State)

@export var stalk_distance_trigger: float = 14.0
@export var charge_speed: float = 8.5
@export var retreat_speed: float = 7.5
@export var roam_speed: float = 2.2
@export var melee_range: float = 2.0
@export var attack_damage: float = 28.0
@export var noise_hearing_radius: float = 22.0

var current_state: State = State.STALKING
var player_ref: Player = null
var look_at_timer: float = 0.0
var retreat_timer: float = 0.0
var stagger_timer: float = 0.0
var fear_timer: float = 0.0
var flank_timer: float = 0.0
var flank_direction: float = 1.0 # 1.0 for right, -1.0 for left
var attack_cooldown: float = 0.0
var has_attacked: bool = false
var fear_source_pos: Vector3 = Vector3.ZERO
var noise_target_pos: Vector3 = Vector3.ZERO
var creature_health: float = 120.0
var eye_mat: StandardMaterial3D = null

# Node contract preservation: tests require these exact node paths
@onready var head_visual: Node3D = get_node_or_null("Visuals/Torso/Head")
@onready var head_node: Node3D = get_node_or_null("Head") if has_node("Head") else get_node_or_null("Visuals/Torso/Head")
@onready var eye_glow_left: OmniLight3D = get_node_or_null("Head/EyeLeft") if has_node("Head/EyeLeft") else get_node_or_null("Visuals/Torso/Head/EyeLeft")
@onready var eye_glow_right: OmniLight3D = get_node_or_null("Head/EyeRight") if has_node("Head/EyeRight") else get_node_or_null("Visuals/Torso/Head/EyeRight")
@onready var eye_mesh_left: MeshInstance3D = get_node_or_null("Head/EyeMeshLeft") if has_node("Head/EyeMeshLeft") else get_node_or_null("Visuals/Torso/Head/EyeMeshLeft")
@onready var eye_mesh_right: MeshInstance3D = get_node_or_null("Head/EyeMeshRight") if has_node("Head/EyeMeshRight") else get_node_or_null("Visuals/Torso/Head/EyeMeshRight")
@onready var visual_root: Node3D = get_node_or_null("Visuals")
@onready var anim_player: AnimationPlayer = get_node_or_null("AnimationPlayer")

func _ready() -> void:
	if anim_player:
		anim_player.play("stalking")

	if eye_mesh_left and eye_mesh_left.mesh and eye_mesh_left.mesh.material:
		eye_mat = eye_mesh_left.mesh.material.duplicate() as StandardMaterial3D
		eye_mesh_left.material_override = eye_mat
		if eye_mesh_right:
			eye_mesh_right.material_override = eye_mat

	_sync_head_transform()

	# Find player in scene tree
	await get_tree().process_frame
	player_ref = get_tree().get_first_node_in_group("player")
	if not player_ref:
		var main = get_parent().get_parent() if get_parent() else null
		if main and main.has_node("Player"):
			player_ref = main.get_node("Player")

func set_state(new_state: State) -> void:
	if current_state == new_state:
		return
	var old = current_state
	current_state = new_state
	state_changed.emit(old, new_state)

func get_current_state_name() -> String:
	match current_state:
		State.IDLE_ROAM: return "IDLE_ROAM"
		State.STALKING: return "STALKING"
		State.INVESTIGATING: return "INVESTIGATING"
		State.FLANKING: return "FLANKING"
		State.ALERTED: return "ALERTED"
		State.ATTACK_CHARGE: return "ATTACK_CHARGE"
		State.RETREATING: return "RETREATING"
		State.STAGGERED: return "STAGGERED"
		State.FEARED: return "FEARED"
		State.GONE: return "GONE"
		_: return "UNKNOWN"

func _physics_process(delta: float) -> void:
	_sync_head_transform()

	if attack_cooldown > 0.0:
		attack_cooldown -= delta

	if not player_ref:
		return

	match current_state:
		State.IDLE_ROAM:
			_process_idle_roam(delta)
		State.STALKING:
			_process_stalking(delta)
		State.INVESTIGATING:
			_process_investigating(delta)
		State.FLANKING:
			_process_flanking(delta)
		State.ALERTED:
			_process_alerted(delta)
		State.ATTACK_CHARGE:
			_process_attack_charge(delta)
		State.RETREATING:
			_process_retreating(delta)
		State.STAGGERED:
			_process_staggered(delta)
		State.FEARED:
			_process_feared(delta)

func _sync_head_transform() -> void:
	if head_visual and head_node and head_node != head_visual:
		head_node.global_transform = head_visual.global_transform

func _process_idle_roam(delta: float) -> void:
	if anim_player and anim_player.current_animation != "stalking":
		anim_player.play("stalking")

	var dist = global_position.distance_to(player_ref.global_position)
	if dist <= 30.0:
		set_state(State.STALKING)
	elif player_ref.is_sprinting and dist <= noise_hearing_radius:
		noise_target_pos = player_ref.global_position
		set_state(State.INVESTIGATING)

func _process_stalking(delta: float) -> void:
	if anim_player and anim_player.current_animation != "stalking":
		anim_player.play("stalking")

	var diff = player_ref.global_position - global_position
	diff.y = 0.0
	if diff.length_squared() > 0.05:
		var target_basis = Basis.looking_at(diff.normalized(), Vector3.UP)
		var q_curr = global_basis.get_rotation_quaternion()
		var q_target = target_basis.get_rotation_quaternion()
		global_basis = Basis(q_curr.slerp(q_target, delta * 2.0).normalized())

	var dist_to_player: float = global_position.distance_to(player_ref.global_position)

	# Stimulus: Sprint noise
	if player_ref.is_sprinting and dist_to_player <= noise_hearing_radius:
		noise_target_pos = player_ref.global_position
		set_state(State.INVESTIGATING)
		return

	# Trigger encounter if player is too close
	if dist_to_player <= stalk_distance_trigger:
		_trigger_encounter()
		return

	# Stimulus: Flashlight direct beam
	if player_ref.flashlight and player_ref.flashlight.visible:
		var cam = player_ref.camera
		if cam:
			var target_point: Vector3 = head_node.global_position if head_node else (global_position + Vector3(0, 1.8, 0))
			var to_creature = target_point - cam.global_position
			var forward = -cam.global_transform.basis.z
			var dot = forward.dot(to_creature.normalized())
			if dot > 0.94 and dist_to_player < 36.0:
				look_at_timer += delta
				if look_at_timer >= 0.6:
					_trigger_encounter()
			else:
				look_at_timer = max(0.0, look_at_timer - delta)

func _process_investigating(delta: float) -> void:
	if anim_player and anim_player.current_animation != "stalking":
		anim_player.play("stalking")

	var to_noise = noise_target_pos - global_position
	to_noise.y = 0.0
	var dist = to_noise.length()

	if dist > 3.0:
		var move_dir = to_noise.normalized()
		velocity = move_dir * roam_speed
		look_at(global_position + move_dir, Vector3.UP)
		move_and_slide()
	else:
		# Arrived at noise location, transition to flanking or stalking
		flank_timer = 4.0
		flank_direction = 1.0 if randf() > 0.5 else -1.0
		set_state(State.FLANKING)

func _process_flanking(delta: float) -> void:
	if anim_player and anim_player.current_animation != "stalking":
		anim_player.play("stalking")

	flank_timer -= delta
	var to_player = player_ref.global_position - global_position
	to_player.y = 0.0
	var dist = to_player.length()

	# Circle lateral vector
	var forward = to_player.normalized()
	var lateral = Vector3(-forward.z, 0, forward.x) * flank_direction
	var flank_vel = (lateral * 0.8 + forward * 0.3).normalized() * (roam_speed * 1.5)
	velocity = flank_vel
	look_at(global_position + forward, Vector3.UP)
	move_and_slide()

	if flank_timer <= 0.0 or dist <= stalk_distance_trigger:
		_trigger_encounter()

func _trigger_encounter() -> void:
	if current_state == State.ALERTED or current_state == State.ATTACK_CHARGE:
		return
	set_state(State.ALERTED)

	if anim_player:
		anim_player.play("charge")

	if AudioDirector.instance:
		AudioDirector.instance.play_cryptid_roar(global_position)

	if player_ref:
		player_ref.trigger_flashlight_flicker(2.2)
		player_ref.show_notification("SOMETHING IS WATCHING FROM THE PINES")

	# Telegraph brief pause before charge
	await get_tree().create_timer(0.4).timeout
	if current_state == State.ALERTED:
		has_attacked = false
		set_state(State.ATTACK_CHARGE)

func _process_alerted(_delta: float) -> void:
	velocity = Vector3.ZERO
	move_and_slide()

func _process_attack_charge(delta: float) -> void:
	if anim_player and anim_player.current_animation != "charge":
		anim_player.play("charge")

	var diff = player_ref.global_position - global_position
	diff.y = 0.0
	var dist = diff.length()

	if dist > 0.1:
		var charge_dir = diff.normalized()
		velocity = charge_dir * charge_speed
		look_at(global_position + charge_dir, Vector3.UP)
		move_and_slide()

	# Melee impact
	if dist <= melee_range and not has_attacked:
		has_attacked = true
		if player_ref.has_method("take_damage"):
			player_ref.take_damage(attack_damage, true, "Sasquatch Maul")
		# Hit and disengage into fog
		set_state(State.RETREATING)
		retreat_timer = 3.0

func _process_retreating(delta: float) -> void:
	if anim_player and anim_player.current_animation != "retreat":
		anim_player.play("retreat")

	retreat_timer -= delta
	if player_ref:
		var diff = player_ref.global_position - global_position
		diff.y = 0.0
		if diff.length_squared() > 0.05:
			var target_basis = Basis.looking_at(diff.normalized(), Vector3.UP)
			var q_curr = global_basis.get_rotation_quaternion()
			var q_target = target_basis.get_rotation_quaternion()
			global_basis = Basis(q_curr.slerp(q_target, delta * 3.0).normalized())

		var away_dir = -diff.normalized()
		velocity = away_dir * retreat_speed
		move_and_slide()

	# Fade eye glow and emission into fog
	var alpha = clamp(retreat_timer / 1.5, 0.0, 1.0)
	if eye_glow_left:
		eye_glow_left.light_energy = alpha * 0.8
	if eye_glow_right:
		eye_glow_right.light_energy = alpha * 0.8
	if eye_mat:
		eye_mat.emission_energy_multiplier = alpha * 4.5

	if retreat_timer <= 0.0:
		set_state(State.GONE)
		queue_free()

func _process_staggered(delta: float) -> void:
	stagger_timer -= delta
	velocity = Vector3.ZERO
	move_and_slide()
	if stagger_timer <= 0.0:
		set_state(State.RETREATING)
		retreat_timer = 3.5

func _process_feared(delta: float) -> void:
	fear_timer -= delta
	var diff = global_position - fear_source_pos
	diff.y = 0.0
	if diff.length_squared() > 0.05:
		var away_dir = diff.normalized()
		velocity = away_dir * retreat_speed
		move_and_slide()
	if fear_timer <= 0.0:
		set_state(State.RETREATING)
		retreat_timer = 2.0

func apply_trap_stagger(duration: float, damage: float) -> void:
	creature_health -= damage
	stagger_timer = duration
	set_state(State.STAGGERED)
	velocity = Vector3.ZERO
	if anim_player:
		anim_player.play("stalking")
	if AudioDirector.instance:
		AudioDirector.instance.play_cryptid_roar(global_position)

func apply_flare_fear(flare_pos: Vector3, duration: float) -> void:
	fear_source_pos = flare_pos
	fear_timer = duration
	set_state(State.FEARED)
	if anim_player:
		anim_player.play("retreat")

func take_damage(amount: float) -> void:
	creature_health -= amount
	if creature_health <= 0.0:
		set_state(State.RETREATING)
		retreat_timer = 2.0
