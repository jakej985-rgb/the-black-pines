class_name CraftingManager
extends Node

## Data-Driven Crafting System for The Black Pines.
## Manages recipes, transactional ingredient consumption, and tool fabrication.

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")

static var instance: CraftingManager = null

signal recipe_crafted(recipe_id: String, output_item_id: String, output_quantity: int)
signal crafting_failed(recipe_id: String, reason: String)

const RECIPES: Dictionary = {
	"recipe_spike_trap": {
		"id": "recipe_spike_trap",
		"name": "Improvised Spike Trap",
		"output_item_id": "trap_spike",
		"output_quantity": 1,
		"ingredients": {
			"scrap_metal": 1,
			"dry_branches": 2
		},
		"description": "Crossed pine timber boards driven through with jagged corrugated metal spikes. Snares and staggers cryptids."
	},
	"recipe_antiseptic_bandage": {
		"id": "recipe_antiseptic_bandage",
		"name": "Antiseptic Herbal Bandage",
		"output_item_id": "antiseptic_bandage",
		"output_quantity": 1,
		"ingredients": {
			"herbs": 1,
			"clean_cloth": 1
		},
		"description": "Sterile cotton dressing packed with crushed forest angelica root. Stops bleeding and heals 40 HP."
	}
}

func _enter_tree() -> void:
	instance = self

func get_all_recipes() -> Array:
	return RECIPES.values()

func get_recipe(recipe_id: String) -> Dictionary:
	return RECIPES.get(recipe_id, {})

## Checks whether all ingredients are present in sufficient quantities.
func can_craft(recipe_id: String) -> bool:
	if not RECIPES.has(recipe_id):
		return false

	var inv = InventoryManagerClass.instance
	if not inv:
		return false

	var recipe = RECIPES[recipe_id]
	var ingredients: Dictionary = recipe.get("ingredients", {})

	for item_id in ingredients:
		var req_qty: int = ingredients[item_id]
		if not inv.has_item(item_id, req_qty):
			return false

	# Verify output capacity
	var out_id: String = recipe.get("output_item_id", "")
	var out_qty: int = recipe.get("output_quantity", 1)
	var out_info = inv.get_item_info(out_id)
	var max_stack: int = out_info.get("max_stack", 99)
	var current_out: int = inv.get_item_count(out_id)

	if current_out + out_qty > max_stack:
		return false

	return true

## Transactional crafting operation: atomic consumption and output grant.
func craft_recipe(recipe_id: String) -> bool:
	if not can_craft(recipe_id):
		crafting_failed.emit(recipe_id, "Insufficient resources or inventory capacity.")
		return false

	var inv = InventoryManagerClass.instance
	var recipe = RECIPES[recipe_id]
	var ingredients: Dictionary = recipe.get("ingredients", {})
	var out_id: String = recipe.get("output_item_id", "")
	var out_qty: int = recipe.get("output_quantity", 1)

	# 1. Deduct all ingredients atomically
	for item_id in ingredients:
		var req_qty: int = ingredients[item_id]
		var removed = inv.remove_item(item_id, req_qty)
		if not removed:
			push_error("Critical crafting error: ingredient deduction failed unexpectedly for " + item_id)
			crafting_failed.emit(recipe_id, "Transaction failed during deduction.")
			return false

	# 2. Grant output item
	inv.add_item(out_id, out_qty)

	# 3. Progress relevant mission objectives
	if JournalManagerClass.instance:
		JournalManagerClass.instance.complete_objective("obj_craft_defense")
		JournalManagerClass.instance.activate_objective("obj_survive_night")

	recipe_crafted.emit(recipe_id, out_id, out_qty)
	return true
