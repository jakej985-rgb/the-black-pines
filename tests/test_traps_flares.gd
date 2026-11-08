extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const ActiveFlareScene = preload("res://scenes/interactables/active_flare.tscn")
const DeployableTrapScene = preload("res://scenes/interactables/deployable_trap.tscn")
const SasquatchScene = preload("res://scenes/creatures/sasquatch.tscn")
const PlayerScene = preload("res://scenes/player/player.tscn")

func _init() -> void:
	print("--- BEGIN TRAPS & FLARES TEST ---")
	await process_frame

	# Setup managers and root environment
	var inv = root.get_node_or_null("Inventory")
	if not inv:
		inv = InventoryManagerClass.new()
		root.add_child(inv)
	inv.items.clear()

	var world = Node3D.new()
	world.name = "TestWorld"
	root.add_child(world)

	var player = PlayerScene.instantiate()
	player.name = "Player"
	world.add_child(player)
	player.global_position = Vector3(0, 0, 0)
	await process_frame

	# 1. Test Deployment Rejection when inventory empty
	assert(inv.get_item_count("road_flare") == 0, "Initial flares should be 0")
	var flare_empty_res = player.deploy_flare()
	assert(flare_empty_res == false, "Deploying flare with 0 flares must fail")
	assert(world.get_tree().get_nodes_in_group("flares").size() == 0, "No flare should be spawned")

	var trap_empty_res = player.deploy_trap()
	assert(trap_empty_res == false, "Deploying trap with 0 traps must fail")
	assert(world.get_tree().get_nodes_in_group("traps").size() == 0, "No trap should be spawned")
	print("✓ Empty inventory deployment rejection verified.")

	# 2. Test Flare Deployment & Consumption
	inv.add_item("road_flare", 2)
	assert(inv.get_item_count("road_flare") == 2, "Inventory should have 2 flares")

	var flare_res = player.deploy_flare()
	assert(flare_res == true, "Deploy flare should succeed")
	assert(inv.get_item_count("road_flare") == 1, "Exactly 1 flare must be consumed")

	var active_flares = world.get_tree().get_nodes_in_group("flares")
	assert(active_flares.size() == 1, "Exactly 1 active flare should be present in scene")
	var deployed_flare = active_flares[0]
	assert(deployed_flare != null, "Deployed flare should not be null")
	assert(deployed_flare.is_burning == true, "Deployed flare should be burning")
	assert(deployed_flare.light.light_energy > 0.0, "Flare light should be illuminating")
	print("✓ Active Flare deployment and item consumption verified.")

	# 3. Test Trap Deployment & Consumption
	inv.add_item("trap_spike", 2)
	assert(inv.get_item_count("trap_spike") == 2, "Inventory should have 2 traps")

	var trap_res = player.deploy_trap()
	assert(trap_res == true, "Deploy trap should succeed")
	assert(inv.get_item_count("trap_spike") == 1, "Exactly 1 trap must be consumed")

	var active_traps = world.get_tree().get_nodes_in_group("traps")
	assert(active_traps.size() == 1, "Exactly 1 active trap should be present")
	var deployed_trap = active_traps[0]
	assert(deployed_trap != null, "Deployed trap should not be null")
	assert(deployed_trap.is_armed == true, "Trap should start armed")
	print("✓ Spike Trap deployment and item consumption verified.")

	# 4. Test Overlap Prevention
	var overlap_trap_res = player.deploy_trap()
	assert(overlap_trap_res == false, "Deploying trap too close to existing trap must be rejected")
	assert(inv.get_item_count("trap_spike") == 1, "Trap count must remain 1 after rejected overlap")
	print("✓ Trap overlap rejection verified.")

	# 5. Test Creature Response to Flare Fear Aura
	var sasquatch = SasquatchScene.instantiate() as Sasquatch
	world.add_child(sasquatch)
	sasquatch.global_position = deployed_flare.global_position + Vector3(3.0, 0, 0)
	await process_frame

	# Trigger flare repel check
	deployed_flare._apply_repel_to_target(sasquatch)
	assert(sasquatch.current_state == Sasquatch.State.FEARED, "Sasquatch should enter FEARED state when repelled by flare")
	assert(sasquatch.fear_timer > 0.0, "Fear timer should be active")
	print("✓ Creature fear reaction to burning flare verified.")

	# 6. Test Creature Triggering Deployable Trap
	sasquatch.global_position = deployed_trap.global_position
	var initial_health = sasquatch.creature_health
	deployed_trap.spring_trap(sasquatch)
	assert(deployed_trap.is_armed == false, "Trap must disarm after springing")
	assert(sasquatch.current_state == Sasquatch.State.STAGGERED, "Sasquatch should enter STAGGERED state from trap")
	assert(sasquatch.creature_health < initial_health, "Creature should take trap spike damage")

	# Verify single-use atomic disarm (repeated calls have no effect)
	deployed_trap.spring_trap(sasquatch)
	assert(deployed_trap.is_armed == false, "Trap should stay disarmed")
	print("✓ Creature snare, stagger, and single-use disarm verified.")

	# Clean up
	world.queue_free()

	print("--- TRAPS & FLARES TESTS PASSED ---")
	quit(0)
