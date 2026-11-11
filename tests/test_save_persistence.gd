extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")
const MissionDirectorClass = preload("res://scripts/systems/mission_director.gd")
const SaveManagerClass = preload("res://scripts/systems/save_manager.gd")
const PlayerScene = preload("res://scenes/player/player.tscn")

const TEST_SAVE_PATH = "user://test_save_persistence.json"
const CORRUPT_SAVE_PATH = "user://test_corrupt_save.json"

func _init() -> void:
	print("--- BEGIN SAVE & PERSISTENCE TEST ---")
	await process_frame

	# Set up singletons in SceneTree root
	var inv = root.get_node_or_null("Inventory")
	if not inv:
		inv = InventoryManagerClass.new()
		inv.name = "Inventory"
		root.add_child(inv)

	var journal = root.get_node_or_null("Journal")
	if not journal:
		journal = JournalManagerClass.new()
		journal.name = "Journal"
		root.add_child(journal)

	var mission = root.get_node_or_null("Mission")
	if not mission:
		mission = MissionDirectorClass.new()
		mission.name = "Mission"
		root.add_child(mission)

	var save_mgr = root.get_node_or_null("Save")
	if not save_mgr:
		save_mgr = SaveManagerClass.new()
		save_mgr.name = "Save"
		root.add_child(save_mgr)

	var world = Node3D.new()
	world.name = "TestWorld"
	root.add_child(world)

	var player = PlayerScene.instantiate()
	world.add_child(player)
	await process_frame

	# Ensure clean slate for test save path
	save_mgr.delete_save_file(TEST_SAVE_PATH)
	assert(not save_mgr.has_save_file(TEST_SAVE_PATH), "Test save file should not exist initially")

	# 1. Mutate player state
	player.global_position = Vector3(12.5, 4.2, -35.8)
	player.rotation.y = 1.25
	player.health = 68.0
	if player.health_component:
		player.health_component.current_health = 68.0
	player.battery = 45.0
	player.flashlight.visible = true

	# 2. Mutate inventory state
	inv.items.clear()
	inv.collected_world_objects.clear()
	inv.add_item("scrap_metal", 5)
	inv.add_item("road_flare", 2)
	inv.add_item("trap_spike", 1)
	inv.mark_world_object_collected("cabin_battery_01")
	inv.mark_world_object_collected("trailhead_flare_02")

	# 3. Mutate journal state
	journal.complete_objective("obj_reach_cabin")
	journal.complete_objective("obj_examine_carcass")
	journal.record_clue("clue_carcass", "Mutilated Elk Carcass", "Massive crushing trauma and ripped throat.")
	journal.record_clue("clue_clawed_tree", "Clawed Bark", "Deep territorial gouges 3.2m above ground.")

	# 4. Mutate mission state
	mission.set_state(MissionDirectorClass.MissionState.IN_PROGRESS)
	assert(mission.can_call_extraction() == true, "Player should be eligible for extraction after cabin + 2 clues")

	# 5. Save Game
	var save_success = save_mgr.save_game(player, TEST_SAVE_PATH)
	assert(save_success == true, "Save operation should succeed")
	assert(save_mgr.has_save_file(TEST_SAVE_PATH) == true, "Save file must exist on disk after save")
	print("✓ Game state successfully saved to disk.")

	# 6. Reset all states to initial/different values to verify loading restores them
	player.global_position = Vector3.ZERO
	player.rotation.y = 0.0
	player.health = 100.0
	if player.health_component:
		player.health_component.current_health = 100.0
	player.battery = 100.0
	player.flashlight.visible = false

	inv.items.clear()
	inv.collected_world_objects.clear()

	journal.objectives["obj_reach_cabin"]["status"] = JournalManagerClass.ObjectiveStatus.LOCKED
	journal.objectives["obj_examine_carcass"]["status"] = JournalManagerClass.ObjectiveStatus.LOCKED
	journal.discovered_clues.clear()

	mission.set_state(MissionDirectorClass.MissionState.NOT_STARTED)

	# 7. Load Game
	var load_success = save_mgr.load_game(player, TEST_SAVE_PATH)
	assert(load_success == true, "Load operation should succeed")

	# 8. Verify restored state
	assert(is_equal_approx(player.global_position.x, 12.5), "Player position X should be restored")
	assert(is_equal_approx(player.global_position.y, 4.2), "Player position Y should be restored")
	assert(is_equal_approx(player.global_position.z, -35.8), "Player position Z should be restored")
	assert(is_equal_approx(player.rotation.y, 1.25), "Player rotation Y should be restored")
	assert(is_equal_approx(player.health, 68.0), "Player health should be restored")
	assert(is_equal_approx(player.health_component.current_health, 68.0), "Player health component should be restored")
	assert(is_equal_approx(player.battery, 45.0), "Player battery should be restored")
	assert(player.flashlight.visible == true, "Player flashlight state should be restored")

	assert(inv.get_item_count("scrap_metal") == 5, "Restored scrap metal count")
	assert(inv.get_item_count("road_flare") == 2, "Restored road flare count")
	assert(inv.get_item_count("trap_spike") == 1, "Restored trap spike count")
	assert(inv.can_collect_world_object("cabin_battery_01") == false, "World pickup 'cabin_battery_01' should stay marked as collected")
	assert(inv.can_collect_world_object("trailhead_flare_02") == false, "World pickup 'trailhead_flare_02' should stay marked as collected")
	assert(inv.can_collect_world_object("unopened_box") == true, "Uncollected pickup should remain collectable")

	assert(journal.is_objective_completed("obj_reach_cabin"), "Journal objective obj_reach_cabin should be restored to COMPLETED")
	assert(journal.is_objective_completed("obj_examine_carcass"), "Journal objective obj_examine_carcass should be restored to COMPLETED")
	assert(journal.discovered_clues.has("clue_carcass"), "Journal clue_carcass should be restored")
	assert(journal.discovered_clues.has("clue_clawed_tree"), "Journal clue_clawed_tree should be restored")

	assert(mission.get_state() == MissionDirectorClass.MissionState.IN_PROGRESS, "Mission state should be restored to IN_PROGRESS")
	print("✓ Round-trip game state serialization & restoration verified.")

	# 9. Test Mission Director Extraction Loop
	var radio_broadcast_result = mission.trigger_emergency_broadcast()
	assert(radio_broadcast_result == true, "Emergency broadcast must succeed when conditions are met")
	assert(mission.get_state() == MissionDirectorClass.MissionState.COMPLETED, "Mission should be COMPLETED after extraction broadcast")
	assert(journal.is_objective_completed("obj_survive_night"), "obj_survive_night objective should be completed")
	print("✓ Mission emergency broadcast and extraction loop verified.")

	# 10. Test Corruption and Missing File Resilience
	var missing_load = save_mgr.load_game(player, "user://non_existent_file_xyz.json")
	assert(missing_load == false, "Loading non-existent save file must gracefully return false")

	var corrupt_file = FileAccess.open(CORRUPT_SAVE_PATH, FileAccess.WRITE)
	corrupt_file.store_string("{ this is invalid json syntax !!!")
	corrupt_file.close()

	var corrupt_signal_fired = [false]
	save_mgr.save_corrupted.connect(func(reason): corrupt_signal_fired[0] = true)
	var corrupt_load = save_mgr.load_game(player, CORRUPT_SAVE_PATH)
	assert(corrupt_load == false, "Loading corrupted save file must return false")
	assert(corrupt_signal_fired[0] == true, "save_corrupted signal should be emitted on corrupted JSON")
	print("✓ Save corruption and error handling verified.")

	# 11. Test Path Traversal and Unauthorized Path Security
	assert(SaveManagerClass.is_valid_save_path("user://save_01.json") == true, "Valid save path should pass")
	assert(SaveManagerClass.is_valid_save_path("user://saves/slot1.json") == true, "Valid nested save path should pass")
	assert(SaveManagerClass.is_valid_save_path("user://../escape.json") == false, "Path traversal with .. must be rejected")
	assert(SaveManagerClass.is_valid_save_path("res://scripts/malicious.gd") == false, "res:// paths must be rejected")
	assert(SaveManagerClass.is_valid_save_path("/etc/shadow") == false, "Absolute OS paths must be rejected")
	assert(SaveManagerClass.is_valid_save_path("user://save.exe") == false, "Non-JSON extensions must be rejected")

	var traversal_saved = save_mgr.save_game(player, "user://../escaped_save.json")
	assert(traversal_saved == false, "Saving with path traversal sequence must fail")

	var traversal_corrupt_fired = [false]
	save_mgr.save_corrupted.connect(func(reason): traversal_corrupt_fired[0] = true)
	var traversal_loaded = save_mgr.load_game(player, "user://../escaped_save.json")
	assert(traversal_loaded == false, "Loading path with traversal must fail")
	assert(traversal_corrupt_fired[0] == true, "save_corrupted signal must fire on invalid path attempt")
	print("✓ Path traversal and unauthorized path protections verified.")

	# Clean up files & nodes
	save_mgr.delete_save_file(TEST_SAVE_PATH)
	save_mgr.delete_save_file(CORRUPT_SAVE_PATH)
	world.queue_free()

	print("--- SAVE & PERSISTENCE TESTS PASSED ---")
	quit(0)
