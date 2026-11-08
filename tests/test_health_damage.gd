extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const HealthComponentClass = preload("res://scripts/player/health_component.gd")
const PlayerScene = preload("res://scenes/player/player.tscn")

func _init() -> void:
	print("--- BEGIN HEALTH & DAMAGE TEST ---")
	await process_frame

	var inv = root.get_node_or_null("Inventory")
	if not inv:
		inv = InventoryManagerClass.new()
		root.add_child(inv)
	inv.items.clear()

	var world = Node3D.new()
	world.name = "TestWorld"
	root.add_child(world)

	var player = PlayerScene.instantiate()
	world.add_child(player)
	await process_frame

	var health_comp = player.health_component
	assert(health_comp != null, "Player must possess a HealthComponent")
	assert(health_comp.current_health == 100.0, "Initial health should be 100")
	assert(health_comp.is_bleeding == false, "Player should not start bleeding")
	assert(health_comp.is_dead == false, "Player should not start dead")
	print("✓ Health initial state verified.")

	# 1. Test Exact Damage and Bounds Clamping
	health_comp.take_damage(25.0, false, "Cryptid Swipe")
	assert(health_comp.current_health == 75.0, "Health should decrease by exactly 25.0")
	assert(player.health == 75.0, "Player health property must synchronize")

	# Overkill damage clamping
	health_comp.heal(25.0)
	assert(health_comp.current_health == 100.0, "Healing should restore health to max")
	health_comp.heal(50.0)
	assert(health_comp.current_health == 100.0, "Healing must not exceed max_health (100.0)")
	print("✓ Damage and health bounds clamping verified.")

	# 2. Test Hemorrhage (Bleeding) Over Time
	health_comp.take_damage(20.0, true, "Claw Puncture")
	assert(health_comp.is_bleeding == true, "Player should enter bleeding state")
	assert(health_comp.current_health == 80.0, "Initial swipe damage applied")

	# Simulate 2 seconds of bleed tick (2.0 dps * 2.0 = 4.0 damage)
	health_comp._process(2.0)
	assert(is_equal_approx(health_comp.current_health, 76.0), "Bleed tick damage over time applied")
	print("✓ Bleeding status and tick damage verified.")

	# 3. Test Treatment with Antiseptic Bandage
	# Attempt treatment without bandage in inventory
	assert(inv.get_item_count("antiseptic_bandage") == 0, "No bandages in inventory initially")
	var failed_treat = health_comp.apply_antiseptic_bandage()
	assert(failed_treat == false, "Treatment without bandage must fail")
	assert(health_comp.is_bleeding == true, "Player must continue bleeding on failed treatment")

	# Grant bandage and apply treatment
	inv.add_item("antiseptic_bandage", 2)
	assert(inv.get_item_count("antiseptic_bandage") == 2, "Inventory has 2 bandages")

	var success_treat = health_comp.apply_antiseptic_bandage()
	assert(success_treat == true, "Treatment with bandage should succeed")
	assert(health_comp.is_bleeding == false, "Bleeding must be stopped by bandage")
	assert(inv.get_item_count("antiseptic_bandage") == 1, "Exactly 1 bandage must be consumed")
	assert(health_comp.current_health > 76.0, "Health should increase by 40 (or clamped to 100)")
	print("✓ Antiseptic bandage wound dressing and bleeding cure verified.")

	# 4. Test Death, Downed State, and Recovery
	health_comp.take_damage(200.0, true, "Fatal Crush")
	assert(health_comp.current_health == 0.0, "Health should reach 0")
	assert(health_comp.is_dead == true, "Player must enter dead/downed state")
	assert(health_comp.is_bleeding == false, "Bleeding must stop on death")

	# Recovery reset
	health_comp.recover()
	assert(health_comp.is_dead == false, "Player should no longer be dead after recovery")
	assert(health_comp.current_health == 75.0, "Recovered health should be set to survival baseline 75.0")
	assert(inv.get_item_count("antiseptic_bandage") == 1, "Inventory items must not be lost on death recovery")
	print("✓ Death, downed state, and safe recovery verified.")

	# Clean up
	world.queue_free()

	print("--- HEALTH & DAMAGE TESTS PASSED ---")
	quit(0)
