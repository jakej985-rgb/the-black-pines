class_name MissionDirector
extends Node

## Mission Director for The Black Pines.
## Coordinates vertical-slice chapter objectives, emergency radio broadcast,
## and end-of-mission extraction resolution.

const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")
const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")

static var instance: MissionDirector = null

enum MissionState {
	NOT_STARTED = 0,
	IN_PROGRESS = 1,
	EXTRACTION_READY = 2,
	COMPLETED = 3,
	FAILED = 4
}

signal mission_state_changed(new_state: MissionState)
signal extraction_signaled
signal mission_completed(summary: Dictionary)

var current_state: MissionState = MissionState.IN_PROGRESS
var mission_start_time: float = 0.0

func _enter_tree() -> void:
	instance = self

func _ready() -> void:
	mission_start_time = Time.get_unix_time_from_system()

func get_state() -> MissionState:
	return current_state

func set_state(state: MissionState) -> void:
	if current_state == state:
		return
	current_state = state
	mission_state_changed.emit(state)

## Evaluates whether requirements for emergency radio broadcast are met.
func can_call_extraction() -> bool:
	if current_state == MissionState.COMPLETED:
		return false

	var journal = JournalManagerClass.instance
	if not journal:
		return false

	# Must have investigated cabin, gathered evidence, and crafted defensive traps
	var cabin_done = journal.is_objective_completed("obj_reach_cabin")
	var clues_gathered = journal.discovered_clues.size() >= 2
	var defense_done = journal.is_objective_completed("obj_craft_defense")

	return cabin_done and (clues_gathered or defense_done)

## Trigger emergency broadcast from the shortwave radio at Ranger Station #04.
func trigger_emergency_broadcast() -> bool:
	if not can_call_extraction():
		return false

	set_state(MissionState.EXTRACTION_READY)
	extraction_signaled.emit()

	var journal = JournalManagerClass.instance
	if journal:
		journal.complete_objective("obj_survive_night")

	set_state(MissionState.COMPLETED)
	var summary = {
		"status": "EXTRACTED",
		"evidence_count": journal.discovered_clues.size() if journal else 0,
		"time_elapsed": Time.get_unix_time_from_system() - mission_start_time
	}
	mission_completed.emit(summary)
	return true
