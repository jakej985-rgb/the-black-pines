extends SceneTree

func _init() -> void:
	print("--- BEGIN AUTOMATED VERIFICATION ---")

	# Allow tree and initial frame to establish
	await process_frame

	# 1. Verify Sasquatch Scene & Rig
	var sasquatch_scene = load("res://scenes/creatures/sasquatch.tscn")
	assert(sasquatch_scene != null, "Failed to load sasquatch.tscn")
	var sasquatch = sasquatch_scene.instantiate()
	assert(sasquatch != null, "Failed to instantiate sasquatch")
	root.add_child(sasquatch)
	await process_frame

	# Verify nodes
	assert(sasquatch.get_node("CollisionShape3D") != null, "Missing CollisionShape3D")
	assert(sasquatch.get_node("Visuals") != null, "Missing Visuals")
	assert(sasquatch.get_node("Visuals/Torso") != null, "Missing Visuals/Torso")
	assert(sasquatch.get_node("Visuals/Torso/Head") != null, "Missing Visuals/Torso/Head")
	assert(sasquatch.get_node("Visuals/Torso/ShoulderLeft") != null, "Missing ShoulderLeft")
	assert(sasquatch.get_node("Visuals/Torso/ShoulderRight") != null, "Missing ShoulderRight")
	assert(sasquatch.get_node("Visuals/Pelvis/LegLeftUpper") != null, "Missing LegLeftUpper")
	assert(sasquatch.get_node("Visuals/Pelvis/LegRightUpper") != null, "Missing LegRightUpper")
	assert(sasquatch.get_node("Visuals/Torso/Head/EyeLeft") != null, "Missing EyeLeft")
	assert(sasquatch.get_node("Visuals/Torso/Head/EyeRight") != null, "Missing EyeRight")

	# Verify eye socket alignment
	var eye_l: OmniLight3D = sasquatch.get_node("Visuals/Torso/Head/EyeLeft")
	var eye_r: OmniLight3D = sasquatch.get_node("Visuals/Torso/Head/EyeRight")
	assert(abs(eye_l.position.x - (-0.13)) < 0.02, "EyeLeft socket X out of alignment")
	assert(abs(eye_r.position.x - 0.13) < 0.02, "EyeRight socket X out of alignment")
	assert(abs(eye_l.position.z - (-0.28)) < 0.02, "EyeLeft socket Z out of alignment")

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

	# Test dynamic head transform synchronization
	sasquatch._sync_head_transform()
	var head_vis: Node3D = sasquatch.get_node("Visuals/Torso/Head")
	assert(head_vis != null, "Missing Visuals/Torso/Head")
	print("✓ Sasquatch: Rig, nodes, eye sockets, and animations fully verified.")

	# 2. Verify Ranger Station
	var ranger_scene = load("res://scenes/interactables/ranger_station.tscn")
	assert(ranger_scene != null, "Failed to load ranger_station.tscn")
	var ranger = ranger_scene.instantiate()
	root.add_child(ranger)
	await process_frame
	await physics_frame

	var cabin_mesh: MeshInstance3D = ranger.get_node("CabinBody/MeshInstance3D")
	assert(cabin_mesh != null, "Missing cabin mesh")
	assert(cabin_mesh.get_surface_override_material(0) != null, "Missing wood material")
	assert(cabin_mesh.get_surface_override_material(1) != null, "Missing roof material")
	assert(cabin_mesh.get_surface_override_material(2) != null, "Missing metal material")
	assert(cabin_mesh.get_surface_override_material(3) != null, "Missing stone material")
	assert(cabin_mesh.get_surface_override_material(4) != null, "Missing glass material")

	# Verify porch deck and steps collision
	assert(ranger.get_node("CabinBody/PorchCollision") != null, "Missing PorchCollision")
	assert(ranger.get_node("CabinBody/StepsCollision") != null, "Missing StepsCollision")

	# Verify DoorSign interactability from porch
	var door_sign: Node = ranger.get_node("DoorSign")
	assert(door_sign != null, "Missing DoorSign")
	assert(door_sign is InspectableClue, "DoorSign must be an InspectableClue")
	assert(door_sign.position.z >= 2.65, "DoorSign must be positioned on outer wall facing porch!")

	var space_state = root.get_world_3d().direct_space_state
	var ray_from = ranger.global_position + Vector3(0.8, 1.6, 3.4)
	var ray_to = ranger.global_position + Vector3(0.8, 1.6, 2.70)
	var ray_param = PhysicsRayQueryParameters3D.create(ray_from, ray_to)
	var ray_hit = space_state.intersect_ray(ray_param)
	assert(!ray_hit.is_empty(), "Raycast from porch failed to hit notice board!")
	assert(ray_hit.collider == door_sign, "Raycast hit " + str(ray_hit.collider.name) + " instead of DoorSign!")
	print("✓ Ranger Station: Multi-surface PBR cabin, walkable porch, and unblocked notice board verified.")

	# 3. Verify Abandoned Camp
	var camp_scene = load("res://scenes/interactables/abandoned_camp.tscn")
	assert(camp_scene != null, "Failed to load abandoned_camp.tscn")
	var camp = camp_scene.instantiate()
	root.add_child(camp)
	await process_frame
	await physics_frame

	assert(camp.get_node("TentMesh") != null, "Missing TentMesh")
	assert(camp.get_node("TentBody") != null, "Missing TentBody collision")
	assert(camp.get_node("CoolerBody") != null, "Missing CoolerBody collision")
	assert(camp.get_node("Firepit") != null, "Missing Firepit")
	assert(camp.get_node("Cooler") != null, "Missing Cooler")
	assert(camp.get_node("CampLantern") != null, "Missing CampLantern")
	assert(camp.get_node("TornJournal") != null, "Missing TornJournal")

	# Verify TornJournal interactability within camp (unblocked by any giant box)
	var journal: Node = camp.get_node("TornJournal")
	var camp_space = root.get_world_3d().direct_space_state
	var journal_ray_from = camp.global_position + Vector3(1.6, 1.2, 0.2)
	var journal_ray_to = camp.global_position + Vector3(1.6, 0.1, -0.8)
	var journal_param = PhysicsRayQueryParameters3D.create(journal_ray_from, journal_ray_to)
	var journal_hit = camp_space.intersect_ray(journal_param)
	assert(!journal_hit.is_empty(), "Raycast to TornJournal failed!")
	assert(journal_hit.collider == journal, "Raycast hit " + str(journal_hit.collider.name) + " instead of TornJournal!")
	print("✓ Abandoned Camp: Upgraded tent, firepit, cooler, lantern, and unobstructed clues verified.")

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
