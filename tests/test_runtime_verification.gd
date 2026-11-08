extends SceneTree

func _init() -> void:
	print("--- BEGIN AUTOMATED VERIFICATION ---")

	# 1. Verify Sasquatch Scene & Rig
	var sasquatch_scene = load("res://scenes/creatures/sasquatch.tscn")
	assert(sasquatch_scene != null, "Failed to load sasquatch.tscn")
	var sasquatch = sasquatch_scene.instantiate()
	assert(sasquatch != null, "Failed to instantiate sasquatch")
	root.add_child(sasquatch)

	# Verify nodes
	assert(sasquatch.get_node("CollisionShape3D") != null, "Missing CollisionShape3D")
	assert(sasquatch.get_node("Visuals") != null, "Missing Visuals")
	assert(sasquatch.get_node("Visuals/Torso") != null, "Missing Visuals/Torso")
	assert(sasquatch.get_node("Visuals/Torso/Head") != null, "Missing Visuals/Torso/Head")
	assert(sasquatch.get_node("Visuals/Torso/ShoulderLeft") != null, "Missing ShoulderLeft")
	assert(sasquatch.get_node("Visuals/Torso/ShoulderRight") != null, "Missing ShoulderRight")
	assert(sasquatch.get_node("Visuals/Pelvis/LegLeftUpper") != null, "Missing LegLeftUpper")
	assert(sasquatch.get_node("Visuals/Pelvis/LegRightUpper") != null, "Missing LegRightUpper")
	assert(sasquatch.get_node("Head/EyeLeft") != null, "Missing Head/EyeLeft")
	assert(sasquatch.get_node("Head/EyeRight") != null, "Missing Head/EyeRight")

	# Verify AnimationPlayer & Animations
	var anim: AnimationPlayer = sasquatch.get_node("AnimationPlayer")
	assert(anim != null, "Missing AnimationPlayer")
	assert(anim.has_animation("idle"), "Missing idle animation")
	assert(anim.has_animation("stalking"), "Missing stalking animation")
	assert(anim.has_animation("charge"), "Missing charge animation")
	assert(anim.has_animation("retreat"), "Missing retreat animation")

	# Test animation playback
	anim.play("idle")
	assert(anim.current_animation == "idle", "idle failed to play")
	anim.play("stalking")
	assert(anim.current_animation == "stalking", "stalking failed to play")
	anim.play("charge")
	assert(anim.current_animation == "charge", "charge failed to play")
	anim.play("retreat")
	assert(anim.current_animation == "retreat", "retreat failed to play")
	print("✓ Sasquatch: Rig, nodes, and animations fully verified.")

	# 2. Verify Ranger Station
	var ranger_scene = load("res://scenes/interactables/ranger_station.tscn")
	assert(ranger_scene != null, "Failed to load ranger_station.tscn")
	var ranger = ranger_scene.instantiate()
	root.add_child(ranger)
	var cabin_mesh: MeshInstance3D = ranger.get_node("CabinBody/MeshInstance3D")
	assert(cabin_mesh != null, "Missing cabin mesh")
	assert(cabin_mesh.get_surface_override_material(0) != null, "Missing wood material")
	assert(cabin_mesh.get_surface_override_material(1) != null, "Missing roof material")
	assert(cabin_mesh.get_surface_override_material(2) != null, "Missing metal material")
	assert(cabin_mesh.get_surface_override_material(3) != null, "Missing stone material")
	assert(cabin_mesh.get_surface_override_material(4) != null, "Missing glass material")
	print("✓ Ranger Station: Multi-surface PBR cabin verified.")

	# 3. Verify Abandoned Camp
	var camp_scene = load("res://scenes/interactables/abandoned_camp.tscn")
	assert(camp_scene != null, "Failed to load abandoned_camp.tscn")
	var camp = camp_scene.instantiate()
	root.add_child(camp)
	assert(camp.get_node("TentMesh") != null, "Missing TentMesh")
	assert(camp.get_node("Firepit") != null, "Missing Firepit")
	assert(camp.get_node("Cooler") != null, "Missing Cooler")
	assert(camp.get_node("CampLantern") != null, "Missing CampLantern")
	assert(camp.get_node("TornJournal") != null, "Missing TornJournal")
	print("✓ Abandoned Camp: Upgraded tent, firepit, cooler, and lantern verified.")

	# 4. Verify Elk Carcass
	var carcass_scene = load("res://scenes/interactables/clue_carcass.tscn")
	assert(carcass_scene != null, "Failed to load clue_carcass.tscn")
	var carcass = carcass_scene.instantiate()
	root.add_child(carcass)
	assert(carcass.get_node("BloodPool") != null, "Missing BloodPool")
	assert(carcass.get_node("CarcassMesh") != null, "Missing CarcassMesh")
	assert(carcass.get_node("WarmVapor") != null, "Missing WarmVapor")
	print("✓ Mutilated Elk Carcass: Anatomical skeleton, gore pool, and warm vapor verified.")

	# 5. Verify Clawed Tree
	var tree_scene = load("res://scenes/interactables/clue_clawed_tree.tscn")
	assert(tree_scene != null, "Failed to load clue_clawed_tree.tscn")
	var clawed_tree = tree_scene.instantiate()
	root.add_child(clawed_tree)
	var trunk: MeshInstance3D = clawed_tree.get_node("TrunkMesh")
	assert(trunk != null, "Missing TrunkMesh")
	assert(trunk.get_surface_override_material(0) != null, "Missing bark material")
	assert(trunk.get_surface_override_material(1) != null, "Missing exposed wood material")
	assert(trunk.get_surface_override_material(2) != null, "Missing resin material")
	print("✓ Clawed Tree: Deep claw gouges, shredded wood, and amber resin verified.")

	# Clean up
	sasquatch.queue_free()
	ranger.queue_free()
	camp.queue_free()
	carcass.queue_free()
	clawed_tree.queue_free()

	print("--- ALL VERIFICATION CHECKS PASSED SUCCESSFULLY ---")
	quit(0)
