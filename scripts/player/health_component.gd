class_name HealthComponent
extends Node

## Player Health, Bleeding, and Recovery Component for The Black Pines.
## Manages health values, damage mitigation, hemorrhage state, and recovery.

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")

signal health_changed(current: float, maximum: float)
signal damage_taken(amount: float, source: String)
signal bleed_started
signal bleed_stopped
signal healed(amount: float)
signal player_died
signal player_recovered

@export var max_health: float = 100.0
@export var current_health: float = 100.0
@export var bleed_dps: float = 2.0

var is_bleeding: bool = false
var bleed_timer: float = 0.0
var is_dead: bool = false

func _ready() -> void:
	current_health = clamp(current_health, 0.0, max_health)
	health_changed.emit(current_health, max_health)

func _process(delta: float) -> void:
	if is_dead:
		return

	if is_bleeding:
		bleed_timer -= delta
		var tick_damage = bleed_dps * delta
		current_health = max(0.0, current_health - tick_damage)
		health_changed.emit(current_health, max_health)
		if current_health <= 0.0:
			_trigger_death("Bleedout")
		elif bleed_timer <= 0.0:
			stop_bleeding()

func take_damage(amount: float, cause_bleed: bool = false, source: String = "") -> void:
	if is_dead or amount <= 0.0:
		return

	current_health = clamp(current_health - amount, 0.0, max_health)
	damage_taken.emit(amount, source)
	health_changed.emit(current_health, max_health)

	if cause_bleed and not is_bleeding:
		start_bleeding(25.0)

	if current_health <= 0.0:
		_trigger_death(source)

func start_bleeding(duration: float = 25.0) -> void:
	if is_dead:
		return
	is_bleeding = true
	bleed_timer = duration
	bleed_started.emit()

func stop_bleeding() -> void:
	if not is_bleeding:
		return
	is_bleeding = false
	bleed_timer = 0.0
	bleed_stopped.emit()

func heal(amount: float, stop_bleed: bool = false) -> bool:
	if is_dead or amount <= 0.0:
		return false
	if current_health >= max_health and not (stop_bleed and is_bleeding):
		return false

	current_health = min(max_health, current_health + amount)
	if stop_bleed:
		stop_bleeding()
	healed.emit(amount)
	health_changed.emit(current_health, max_health)
	return true

func apply_antiseptic_bandage() -> bool:
	var inv = InventoryManagerClass.instance
	if not inv or not inv.has_item("antiseptic_bandage", 1):
		return false

	if not inv.remove_item("antiseptic_bandage", 1):
		return false

	heal(40.0, true)
	return true

func _trigger_death(source: String) -> void:
	if is_dead:
		return
	is_dead = true
	is_bleeding = false
	current_health = 0.0
	health_changed.emit(current_health, max_health)
	player_died.emit()

func recover(respawn_pos: Vector3 = Vector3(0, 1.2, 5.0)) -> void:
	is_dead = false
	is_bleeding = false
	bleed_timer = 0.0
	current_health = 75.0
	health_changed.emit(current_health, max_health)
	player_recovered.emit()
