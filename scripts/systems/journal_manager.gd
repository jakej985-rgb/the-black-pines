class_name JournalManager
extends Node

## Central Objective & Investigation Journal Manager for The Black Pines.
## Manages mission goals, discovered evidence, and serializable journal state.

enum ObjectiveStatus {
	LOCKED = 0,
	ACTIVE = 1,
	COMPLETED = 2,
	FAILED = 3
}

static var instance: JournalManager = null

signal objective_status_changed(obj_id: String, status: ObjectiveStatus)
signal clue_recorded(clue_id: String, entry: Dictionary)
signal journal_visibility_toggled(is_visible: bool)

# Registered objectives: id -> Dictionary
var objectives: Dictionary = {}

# Recorded clues: clue_id -> Dictionary
var discovered_clues: Dictionary = {}

var is_journal_open: bool = false

func _enter_tree() -> void:
	instance = self

func _ready() -> void:
	_init_default_objectives()

func _init_default_objectives() -> void:
	objectives.clear()
	_register_objective(
		"obj_reach_cabin",
		"Investigate Ranger Station #04",
		"Locate the ranger station along the ridge trail and search for wardens' field logs.",
		ObjectiveStatus.ACTIVE
	)
	_register_objective(
		"obj_examine_carcass",
		"Inspect Mutilated Elk",
		"Examine the fresh carcass reported near the eastern tree clearing for predatory feeding patterns.",
		ObjectiveStatus.LOCKED
	)
	_register_objective(
		"obj_track_beast",
		"Territorial Markings",
		"Locate claw gouges on pine trunks and plaster cast bipedal footprints along the mud path.",
		ObjectiveStatus.LOCKED
	)
	_register_objective(
		"obj_craft_defense",
		"Prepare Defensive Deterrents",
		"Gather scrap metal, dry branches, and road flares to craft improvised defenses.",
		ObjectiveStatus.LOCKED
	)
	_register_objective(
		"obj_survive_night",
		"Survive & Signal",
		"Survive the cryptid's aggressive stalking pass and broadcast an emergency beacon from the shortwave radio.",
		ObjectiveStatus.LOCKED
	)

func _register_objective(id: String, title: String, description: String, initial_status: ObjectiveStatus) -> void:
	objectives[id] = {
		"id": id,
		"title": title,
		"description": description,
		"status": initial_status
	}

func set_objective_status(obj_id: String, status: ObjectiveStatus) -> void:
	if not objectives.has(obj_id):
		push_warning("Unknown objective: " + obj_id)
		return
	if objectives[obj_id]["status"] == status:
		return
	objectives[obj_id]["status"] = status
	objective_status_changed.emit(obj_id, status)

func complete_objective(obj_id: String) -> void:
	set_objective_status(obj_id, ObjectiveStatus.COMPLETED)

func activate_objective(obj_id: String) -> void:
	if objectives.has(obj_id) and objectives[obj_id]["status"] == ObjectiveStatus.LOCKED:
		set_objective_status(obj_id, ObjectiveStatus.ACTIVE)

func is_objective_completed(obj_id: String) -> bool:
	return objectives.has(obj_id) and objectives[obj_id]["status"] == ObjectiveStatus.COMPLETED

func get_objective_status(obj_id: String) -> ObjectiveStatus:
	if objectives.has(obj_id):
		return objectives[obj_id].get("status", ObjectiveStatus.LOCKED)
	return ObjectiveStatus.LOCKED

## Record a discovered clue. Returns true if newly discovered, false if already in journal.
func record_clue(clue_id: String, title: String, text: String) -> bool:
	if clue_id.is_empty():
		clue_id = title.to_snake_case()

	if discovered_clues.has(clue_id):
		return false # Prevent duplicate journal entries

	var entry = {
		"id": clue_id,
		"title": title,
		"text": text,
		"discovered_at": Time.get_time_string_from_system()
	}
	discovered_clues[clue_id] = entry
	clue_recorded.emit(clue_id, entry)

	# Dynamic objective progression based on evidence discovery
	_evaluate_progression_from_clue(clue_id)
	return true

func _evaluate_progression_from_clue(clue_id: String) -> void:
	match clue_id:
		"doc_evacuation_notice", "evacuation_notice", "door_sign":
			complete_objective("obj_reach_cabin")
			activate_objective("obj_examine_carcass")
			activate_objective("obj_track_beast")
		"clue_carcass", "elk_carcass":
			complete_objective("obj_examine_carcass")
			activate_objective("obj_craft_defense")
		"clue_clawed_tree", "clawed_tree", "clue_footprint":
			complete_objective("obj_track_beast")
			activate_objective("obj_craft_defense")
		"warden_field_journal", "field_journal", "topomap":
			activate_objective("obj_craft_defense")

func get_active_objectives() -> Array:
	var list = []
	for id in objectives:
		if objectives[id]["status"] == ObjectiveStatus.ACTIVE:
			list.append(objectives[id])
	return list

func get_completed_objectives() -> Array:
	var list = []
	for id in objectives:
		if objectives[id]["status"] == ObjectiveStatus.COMPLETED:
			list.append(objectives[id])
	return list

func get_all_clues() -> Array:
	return discovered_clues.values()

## Serialization for Save/Load
func get_save_data() -> Dictionary:
	var obj_data = {}
	for id in objectives:
		obj_data[id] = objectives[id]["status"]
	return {
		"objectives": obj_data,
		"discovered_clues": discovered_clues
	}

func load_save_data(data: Dictionary) -> void:
	if data.has("objectives"):
		for id in data["objectives"]:
			if objectives.has(id):
				objectives[id]["status"] = int(data["objectives"][id])
				objective_status_changed.emit(id, objectives[id]["status"])
	if data.has("discovered_clues"):
		discovered_clues = data["discovered_clues"].duplicate(true)
