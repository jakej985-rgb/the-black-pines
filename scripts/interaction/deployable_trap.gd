class_name DeployableTrap
extends Node3D

## Deployable Improvised Spike Trap.
## Snares, damages, and heavily staggers Sasquatch and cryptids.

signal trap_sprung(target: Node)

@export var damage: float = 35.0
@export var stagger_duration: float = 4.5
@export var is_armed: bool = true

@onready var trigger_area: Area3D = $TriggerArea
@onready var model_root: Node3D = $TrapModel
@onready var snap_sound: AudioStreamPlayer3D = $SnapAudio

func _ready() -> void:
	if trigger_area:
		trigger_area.body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node) -> void:
	if not is_armed:
		return
	
	# Check if creature or player
	var is_creature = body.is_in_group("creatures") or body.name.to_lower().contains("sasquatch") or body.has_method("apply_trap_stagger")
	var is_player = body.is_in_group("player") or body.has_method("take_damage") and body != self

	if not (is_creature or is_player):
		return

	spring_trap(body)

func spring_trap(target: Node) -> void:
	if not is_armed:
		return
	is_armed = false

	# Play audio
	if snap_sound:
		snap_sound.play()
	elif AudioDirector.instance:
		AudioDirector.instance.play_click()

	# Visual snap feedback: collapse/sink spikes slightly
	if model_root:
		var tween = create_tween()
		tween.tween_property(model_root, "scale", Vector3(1.0, 0.4, 1.0), 0.1)

	# Apply damage and stagger to creature
	if target:
		if target.has_method("apply_trap_stagger"):
			target.apply_trap_stagger(stagger_duration, damage)
		elif target.has_method("take_damage"):
			target.take_damage(damage)

	trap_sprung.emit(target)
