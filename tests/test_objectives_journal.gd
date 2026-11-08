extends SceneTree

func _init() -> void:
	print("--- BEGIN OBJECTIVES & JOURNAL TEST ---")
	await process_frame

	var jm = JournalManager.new()
	root.add_child(jm)
	await process_frame

	# 1. Test initial objectives
	var active = jm.get_active_objectives()
	assert(active.size() >= 1, "Must have at least 1 active objective at start")
	assert(active[0]["id"] == "obj_reach_cabin", "First objective must be obj_reach_cabin")
	print("✓ Initial objective state verified: " + str(active[0]["title"]))

	# 2. Test Clue Recording & Duplicate Prevention
	var clue_id = "test_clue_tracks"
	var res1 = jm.record_clue(clue_id, "Heavy Bipedal Tracks", "Five-toed impressions found in the mud.")
	assert(res1 == true, "First clue recording must succeed")
	assert(jm.discovered_clues.has(clue_id), "Clue must be present in journal")

	var res2 = jm.record_clue(clue_id, "Heavy Bipedal Tracks", "Duplicate interaction text.")
	assert(res2 == false, "Duplicate clue recording must be rejected")
	assert(jm.discovered_clues.size() == 1, "Discovered clues count must remain 1 after duplicate")
	print("✓ Clue recording and duplicate rejection verified.")

	# 3. Test Clue Progression
	# Inspecting evacuation notice completes obj_reach_cabin and unlocks obj_examine_carcass + obj_track_beast
	jm.record_clue("doc_evacuation_notice", "Evacuation Notice", "Station evacuated.")
	assert(jm.is_objective_completed("obj_reach_cabin"), "obj_reach_cabin should be completed by evacuation notice")
	assert(jm.objectives["obj_examine_carcass"]["status"] == JournalManager.ObjectiveStatus.ACTIVE, "obj_examine_carcass should now be ACTIVE")
	assert(jm.objectives["obj_track_beast"]["status"] == JournalManager.ObjectiveStatus.ACTIVE, "obj_track_beast should now be ACTIVE")
	print("✓ Objective progression triggered by clue discovery verified.")

	# 4. Test Serialization & Deserialization
	var save_data = jm.get_save_data()
	assert(save_data.has("objectives") and save_data.has("discovered_clues"), "Save data must contain objectives and clues")

	var jm2 = JournalManager.new()
	root.add_child(jm2)
	await process_frame
	jm2.load_save_data(save_data)

	assert(jm2.is_objective_completed("obj_reach_cabin"), "Restored manager must reflect completed objective")
	assert(jm2.discovered_clues.has(clue_id), "Restored manager must contain recorded clues")
	print("✓ Journal serialization and restoration verified.")

	# Clean up
	jm.queue_free()
	jm2.queue_free()

	print("--- OBJECTIVES & JOURNAL TESTS PASSED ---")
	quit(0)
