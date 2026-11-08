extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const PlayerScene = preload("res://scenes/player/player.tscn")

func _init() -> void:
	print("--- BEGIN FLASHLIGHT BATTERY TEST ---")
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

	assert(player.flashlight != null, "Player must possess flashlight")
	assert(player.battery <= 100.0 and player.battery >= 99.0, "Initial battery should be ~100%")
	assert(player.max_battery == 100.0, "Max battery should be 100%")
	print("✓ Flashlight battery initial state verified.")

	# 1. Test Battery Stability while OFF
	player.flashlight.visible = false
	player.battery = 100.0
	var initial_batt = player.battery
	player._physics_process(5.0)
	assert(player.battery == initial_batt, "Battery must NOT drain while flashlight is turned off")
	print("✓ Flashlight battery stability while off verified.")

	# 2. Test Battery Drain while ON
	player.flashlight.visible = true
	var expected_drain = player.battery_drain_rate * 2.0
	player._physics_process(2.0)
	assert(is_equal_approx(player.battery, initial_batt - expected_drain), "Battery should drain proportionally while on")
	print("✓ Active battery drain verified.")

	# 3. Test Depleted State (Battery reaches 0)
	player.battery = 1.0
	player._physics_process(3.0) # Drain beyond 0
	assert(player.battery == 0.0, "Battery should clamp exactly at 0.0 without going negative")
	assert(player.flashlight.visible == false, "Flashlight must turn off automatically upon battery depletion")

	# Test Toggle Prevention when Depleted
	var fake_event = InputEventAction.new()
	fake_event.action = "toggle_flashlight"
	fake_event.pressed = true
	player._unhandled_input(fake_event)
	assert(player.flashlight.visible == false, "Cannot turn on flashlight when battery is 0")
	print("✓ Depleted shutdown and lockout verified.")

	# 4. Test Battery Reload
	# Reload without batteries in inventory
	assert(inv.get_item_count("battery_pack") == 0, "Inventory has 0 batteries initially")
	var fail_reload = player.reload_flashlight_battery()
	assert(fail_reload == false, "Reloading without battery pack must fail")
	assert(player.battery == 0.0, "Battery must remain 0 on failed reload")

	# Add battery pack and reload
	inv.add_item("battery_pack", 2)
	assert(inv.get_item_count("battery_pack") == 2, "Inventory has 2 batteries")

	var ok_reload = player.reload_flashlight_battery()
	assert(ok_reload == true, "Reload with battery pack must succeed")
	assert(player.battery == 100.0, "Battery should be restored to 100%")
	assert(inv.get_item_count("battery_pack") == 1, "Exactly 1 battery pack should be consumed")

	# Reload when already full should be rejected
	var full_reload = player.reload_flashlight_battery()
	assert(full_reload == false, "Reloading when battery is already 100% must be rejected")
	assert(inv.get_item_count("battery_pack") == 1, "Battery pack must not be consumed when already full")
	print("✓ Battery reload and inventory consumption verified.")

	# Clean up
	world.queue_free()

	print("--- FLASHLIGHT BATTERY TESTS PASSED ---")
	quit(0)
