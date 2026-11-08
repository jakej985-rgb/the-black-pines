class_name ActiveFlare
extends Node3D

## Active burning road distress flare.
## Emits high-intensity light and casts a repulsion aura that scares away Sasquatch.

signal flare_expired
signal creature_repelled(creature: Node)

@export var burn_duration: float = 45.0
@export var repel_radius: float = 14.0
@export var base_light_energy: float = 3.2

var is_burning: bool = true
var time_remaining: float = 45.0

@onready var light: OmniLight3D = $OmniLight3D
@onready var repel_area: Area3D = $RepelArea

func _ready() -> void:
	time_remaining = burn_duration
	if repel_area:
		repel_area.body_entered.connect(_on_body_entered)
	_repel_existing_overlapping_bodies()

func _process(delta: float) -> void:
	if not is_burning:
		return

	time_remaining -= delta
	if time_remaining <= 0.0:
		_extinguish_flare()
		return

	# Flicker illumination
	if light:
		if time_remaining < 5.0:
			# Dying fade out
			var factor = time_remaining / 5.0
			light.light_energy = base_light_energy * factor * randf_range(0.3, 1.0)
		else:
			var flicker = sin(Time.get_ticks_msec() * 0.025) * 0.35 + (randf() - 0.5) * 0.25
			light.light_energy = max(0.5, base_light_energy + flicker)

func _on_body_entered(body: Node) -> void:
	if not is_burning:
		return
	_apply_repel_to_target(body)

func _repel_existing_overlapping_bodies() -> void:
	if not repel_area:
		return
	for body in repel_area.get_overlapping_bodies():
		_apply_repel_to_target(body)

func _apply_repel_to_target(body: Node) -> void:
	var is_creature = body.is_in_group("creatures") or body.name.to_lower().contains("sasquatch") or body.has_method("apply_flare_fear")
	if is_creature:
		if body.has_method("apply_flare_fear"):
			body.apply_flare_fear(global_position, 8.0)
		creature_repelled.emit(body)

func _extinguish_flare() -> void:
	is_burning = false
	if light:
		light.visible = false
	flare_expired.emit()
	queue_free()
