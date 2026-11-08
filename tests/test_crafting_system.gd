extends SceneTree

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")
const CraftingManagerClass = preload("res://scripts/systems/crafting_manager.gd")

func _init() -> void:
	print("--- BEGIN CRAFTING SYSTEM TEST ---")
	await process_frame

	var journal = root.get_node_or_null("Journal")
	if not journal:
		journal = JournalManagerClass.new()
		root.add_child(journal)

	var inv = root.get_node_or_null("Inventory")
	if not inv:
		inv = InventoryManagerClass.new()
		root.add_child(inv)

	var crafting = root.get_node_or_null("Crafting")
	if not crafting:
		crafting = CraftingManagerClass.new()
		root.add_child(crafting)

	await process_frame

	# 1. Verify Recipe Registry
	var recipes = crafting.get_all_recipes()
	assert(recipes.size() >= 2, "Expected at least 2 default recipes")
	var spike_recipe = crafting.get_recipe("recipe_spike_trap")
	assert(spike_recipe["output_item_id"] == "trap_spike", "Spike trap recipe output mismatch")
	assert(spike_recipe["ingredients"]["scrap_metal"] == 1, "Spike trap scrap requirement mismatch")
	assert(spike_recipe["ingredients"]["dry_branches"] == 2, "Spike trap branches requirement mismatch")
	print("✓ Recipe registry verified.")

	# 2. Test can_craft with empty inventory
	assert(crafting.can_craft("recipe_spike_trap") == false, "Should not craft spike trap with 0 resources")
	var failed_craft = crafting.craft_recipe("recipe_spike_trap")
	assert(failed_craft == false, "Crafting with missing ingredients must fail")
	assert(inv.get_item_count("trap_spike") == 0, "No item should be granted on failed craft")
	print("✓ Insufficient resource validation verified.")

	# 3. Test Partial Ingredients
	inv.add_item("dry_branches", 2)
	assert(crafting.can_craft("recipe_spike_trap") == false, "Should not craft spike trap without scrap metal")
	var partial_fail = crafting.craft_recipe("recipe_spike_trap")
	assert(partial_fail == false, "Partial ingredient craft must fail")
	assert(inv.get_item_count("dry_branches") == 2, "Dry branches must not be consumed on failed craft")
	print("✓ Atomic protection on partial ingredients verified.")

	# 4. Add remaining ingredient and craft successfully
	inv.add_item("scrap_metal", 1)
	assert(crafting.can_craft("recipe_spike_trap") == true, "Should be able to craft spike trap with required resources")

	var craft_ok = crafting.craft_recipe("recipe_spike_trap")
	assert(craft_ok == true, "Crafting spike trap should succeed")
	assert(inv.get_item_count("dry_branches") == 0, "Dry branches should be consumed")
	assert(inv.get_item_count("scrap_metal") == 0, "Scrap metal should be consumed")
	assert(inv.get_item_count("trap_spike") == 1, "Player should have 1 trap_spike in inventory")
	print("✓ Improvised Spike Trap crafted with atomic deduction and output grant.")

	# 5. Verify Objective Progression
	assert(journal.get_objective_status("obj_craft_defense") == JournalManagerClass.ObjectiveStatus.COMPLETED, "Craft defense objective should be completed")
	assert(journal.get_objective_status("obj_survive_night") == JournalManagerClass.ObjectiveStatus.ACTIVE, "Survive night objective should be active")
	print("✓ Journal objective integration verified.")

	# 6. Test Bandage Recipe
	inv.add_item("herbs", 2)
	inv.add_item("clean_cloth", 1)
	assert(crafting.can_craft("recipe_antiseptic_bandage") == true, "Should be able to craft bandage")
	var bandage_ok = crafting.craft_recipe("recipe_antiseptic_bandage")
	assert(bandage_ok == true, "Bandage craft should succeed")
	assert(inv.get_item_count("herbs") == 1, "1 herb should remain")
	assert(inv.get_item_count("clean_cloth") == 0, "Cloth should be consumed")
	assert(inv.get_item_count("antiseptic_bandage") == 1, "Should receive 1 antiseptic bandage")
	print("✓ Antiseptic Bandage crafting verified.")

	print("--- CRAFTING SYSTEM TESTS PASSED ---")
	quit(0)
