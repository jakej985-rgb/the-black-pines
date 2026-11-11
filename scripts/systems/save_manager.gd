class_name SaveManager
extends Node

## Save and Load Persistence System for The Black Pines.
## Serializes and validates player transform, health, battery, inventory,
## evidence journal, and world pickup persistence to JSON.

const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")
const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const MissionDirectorClass = preload("res://scripts/systems/mission_director.gd")

static var instance: SaveManager = null

const SAVE_PATH: String = "user://black_pines_save.json"
const CURRENT_VERSION: int = 1

signal game_saved(filepath: String)
signal game_loaded(filepath: String)
signal save_corrupted(reason: String)

func _enter_tree() -> void:
	instance = self

## Security helper: validates that save paths reside strictly within the user:// sandboxed storage,
## avoid directory traversal (..) sequences, and use the .json extension.
## Only flat paths (no subdirectories) are allowed, so saves cannot cross a symlinked directory.
static func is_valid_save_path(path: String) -> bool:
	if not path.begins_with("user://"):
		return false
	if ".." in path or "\\" in path:
		return false
	if "/" in path.trim_prefix("user://"):
		return false
	if not path.ends_with(".json"):
		return false
	return true

func has_save_file(path: String = SAVE_PATH) -> bool:
	if not is_valid_save_path(path):
		return false
	return FileAccess.file_exists(path)

func delete_save_file(path: String = SAVE_PATH) -> void:
	if not is_valid_save_path(path):
		push_error("Blocked attempt to delete invalid save path: " + path)
		return
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)

func save_game(player: Node = null, path: String = SAVE_PATH) -> bool:
	if not is_valid_save_path(path):
		push_error("Blocked attempt to save to invalid or unauthorized path: " + path)
		return false
	var save_dict: Dictionary = {
		"version": CURRENT_VERSION,
		"timestamp": Time.get_unix_time_from_system(),
		"player": {},
		"inventory": {},
		"journal": {},
		"mission": {}
	}

	# 1. Player state
	if player:
		save_dict["player"] = {
			"position": [player.global_position.x, player.global_position.y, player.global_position.z],
			"rotation_y": player.rotation.y,
			"health": player.health if "health" in player else 100.0,
			"battery": player.battery if "battery" in player else 100.0,
			"flashlight_on": player.flashlight.visible if ("flashlight" in player and player.flashlight) else true
		}

	# 2. Inventory state
	var inv = InventoryManagerClass.instance
	if inv:
		save_dict["inventory"] = inv.get_save_data()

	# 3. Journal state
	var journal = JournalManagerClass.instance
	if journal:
		save_dict["journal"] = journal.get_save_data()

	# 4. Mission state
	var mission = MissionDirectorClass.instance
	if mission:
		save_dict["mission"] = {
			"state": int(mission.get_state())
		}

	var json_str = JSON.stringify(save_dict, "\t")
	var file = FileAccess.open(path, FileAccess.WRITE)
	if not file:
		push_error("Failed to open save file for writing: " + path)
		return false

	file.store_string(json_str)
	file.close()
	game_saved.emit(path)
	return true

func load_game(player: Node = null, path: String = SAVE_PATH) -> bool:
	if not is_valid_save_path(path):
		save_corrupted.emit("Blocked attempt to load invalid or unauthorized path: " + path)
		return false

	if not FileAccess.file_exists(path):
		push_warning("Save file does not exist: " + path)
		return false

	var file = FileAccess.open(path, FileAccess.READ)
	if not file:
		save_corrupted.emit("Could not read save file.")
		return false

	var content = file.get_as_text()
	file.close()

	var test_json = JSON.new()
	var parse_err = test_json.parse(content)
	if parse_err != OK:
		save_corrupted.emit("Corrupted JSON data at line %d: %s" % [test_json.get_error_line(), test_json.get_error_message()])
		return false

	var data = test_json.get_data()
	if not (data is Dictionary):
		save_corrupted.emit("Save data payload is not a valid Dictionary.")
		return false

	# Version check
	var version = data.get("version", 0)
	if version != CURRENT_VERSION:
		save_corrupted.emit("Incompatible save version: %d (expected %d)" % [version, CURRENT_VERSION])
		return false

	# 1. Restore Player state
	if player and data.has("player") and data["player"] is Dictionary:
		var p_data: Dictionary = data["player"]
		if p_data.has("position") and p_data["position"] is Array and p_data["position"].size() >= 3:
			player.global_position = Vector3(p_data["position"][0], p_data["position"][1], p_data["position"][2])
		if p_data.has("rotation_y"):
			player.rotation.y = p_data["rotation_y"]
		if p_data.has("health") and "health" in player:
			player.health = p_data["health"]
			if "health_component" in player and player.health_component:
				player.health_component.current_health = p_data["health"]
		if p_data.has("battery") and "battery" in player:
			player.battery = p_data["battery"]
		if p_data.has("flashlight_on") and "flashlight" in player and player.flashlight:
			player.flashlight.visible = p_data["flashlight_on"]

	# 2. Restore Inventory state
	if data.has("inventory") and data["inventory"] is Dictionary:
		var inv = InventoryManagerClass.instance
		if inv:
			inv.load_save_data(data["inventory"])

	# 3. Restore Journal state
	if data.has("journal") and data["journal"] is Dictionary:
		var journal = JournalManagerClass.instance
		if journal:
			journal.load_save_data(data["journal"])

	# 4. Restore Mission state
	if data.has("mission") and data["mission"] is Dictionary:
		var mission = MissionDirectorClass.instance
		if mission:
			var m_state = data["mission"].get("state", int(MissionDirectorClass.MissionState.IN_PROGRESS))
			mission.set_state(m_state as MissionDirectorClass.MissionState)

	game_loaded.emit(path)
	return true
