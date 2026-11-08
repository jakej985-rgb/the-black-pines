extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")

func _init() -> void:
	print("--- BEGIN INVENTORY STATE TEST ---")
	await process_frame

	var inv = InventoryManagerClass.new()
	root.add_child(inv)
	await process_frame

	# 1. Test item info registry
	var scrap_info = inv.get_item_info("scrap_metal")
	assert(scrap_info["name"] == "Rusted Scrap Metal", "Item name lookup failed")
	assert(scrap_info["max_stack"] == 10, "Scrap metal max stack should be 10")
	print("✓ Item registry lookup verified.")

	# 2. Test Add Items & Stack Limits
	var add_res = inv.add_item("scrap_metal", 4)
	assert(add_res == true, "Add 4 scrap metal should succeed")
	assert(inv.get_item_count("scrap_metal") == 4, "Item count should be 4")

	# Add up to max_stack (10)
	inv.add_item("scrap_metal", 6)
	assert(inv.get_item_count("scrap_metal") == 10, "Item count should be 10 (max)")

	# Exceeding max stack should fail
	var over_res = inv.add_item("scrap_metal", 1)
	assert(over_res == false, "Adding beyond max_stack should return false")
	assert(inv.get_item_count("scrap_metal") == 10, "Item count should not exceed max_stack")
	print("✓ Item addition and stack limit clamping verified.")

	# 3. Test Atomic Removal
	# Trying to remove 15 when only 10 exist must fail atomically (no partial removal)
	var remove_excess = inv.remove_item("scrap_metal", 15)
	assert(remove_excess == false, "Removing more than available should return false")
	assert(inv.get_item_count("scrap_metal") == 10, "Item count must remain unchanged on failed removal")

	# Valid removal
	var remove_valid = inv.remove_item("scrap_metal", 3)
	assert(remove_valid == true, "Removing valid quantity should succeed")
	assert(inv.get_item_count("scrap_metal") == 7, "Item count should be 7")
	print("✓ Atomic item removal and rollback verified.")

	# 4. Test World Object Collection Persistence
	var world_uid = "/root/Forest/ScrapMetal_01"
	assert(inv.can_collect_world_object(world_uid) == true, "Object should be collectible initially")
	inv.mark_world_object_collected(world_uid)
	assert(inv.can_collect_world_object(world_uid) == false, "Object must NOT be collectible once picked up")
	print("✓ World pickup tracking verified.")

	# 5. Test Serialization
	var save_data = inv.get_save_data()
	var inv2 = InventoryManagerClass.new()
	root.add_child(inv2)
	await process_frame

	inv2.load_save_data(save_data)
	assert(inv2.get_item_count("scrap_metal") == 7, "Restored inventory count mismatch")
	assert(inv2.can_collect_world_object(world_uid) == false, "Restored world pickup state mismatch")
	print("✓ Inventory serialization roundtrip verified.")

	# Clean up
	inv.queue_free()
	inv2.queue_free()

	print("--- INVENTORY STATE TESTS PASSED ---")
	quit(0)
