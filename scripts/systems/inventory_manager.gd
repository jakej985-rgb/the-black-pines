class_name InventoryManager
extends Node

## Inventory & Evidence Manager for The Black Pines.
## Manages resource stacks, tools, consumables, evidence items, and world pickup persistence.

static var instance: InventoryManager = null

signal item_added(item_id: String, quantity: int, new_total: int)
signal item_removed(item_id: String, quantity: int, new_total: int)
signal inventory_changed()
signal inventory_visibility_toggled(is_visible: bool)

enum ItemType {
	RESOURCE = 0,
	TOOL = 1,
	CONSUMABLE = 2,
	EVIDENCE = 3
}

const ITEM_REGISTRY: Dictionary = {
	"scrap_metal": {
		"id": "scrap_metal",
		"name": "Rusted Scrap Metal",
		"type": ItemType.RESOURCE,
		"max_stack": 10,
		"description": "Sharp corrugated sheet metal salvaged from the ranger station."
	},
	"dry_branches": {
		"id": "dry_branches",
		"name": "Dry Pine Branches",
		"type": ItemType.RESOURCE,
		"max_stack": 20,
		"description": "Seasoned resinous timber limbs suitable for rigid trap construction."
	},
	"herbs": {
		"id": "herbs",
		"name": "Forest Angelica Herbs",
		"type": ItemType.RESOURCE,
		"max_stack": 10,
		"description": "Wild medicinal roots found in damp loam. Possesses natural clotting properties."
	},
	"clean_cloth": {
		"id": "clean_cloth",
		"name": "Clean Cotton Cloth",
		"type": ItemType.RESOURCE,
		"max_stack": 5,
		"description": "Dry cotton bandages from the station emergency supply."
	},
	"road_flare": {
		"id": "road_flare",
		"name": "Roadside Distress Flare",
		"type": ItemType.TOOL,
		"max_stack": 4,
		"description": "Magnesium highway flare. Burns intensely, repelling cryptid stalkers."
	},
	"trap_spike": {
		"id": "trap_spike",
		"name": "Improvised Spike Trap",
		"type": ItemType.TOOL,
		"max_stack": 3,
		"description": "A spring-loaded board with sharpened metal spikes. Snares and staggers the beast."
	},
	"antiseptic_bandage": {
		"id": "antiseptic_bandage",
		"name": "Antiseptic Bandage",
		"type": ItemType.CONSUMABLE,
		"max_stack": 5,
		"description": "Herbal-treated field dressing. Stops bleeding and restores 40 HP."
	},
	"battery_pack": {
		"id": "battery_pack",
		"name": "D-Cell Batteries",
		"type": ItemType.CONSUMABLE,
		"max_stack": 4,
		"description": "Fresh industrial batteries. Restores 50% flashlight charge."
	},
	"evid_plaster_cast": {
		"id": "evid_plaster_cast",
		"name": "Plaster Footprint Cast",
		"type": ItemType.EVIDENCE,
		"max_stack": 1,
		"description": "48cm five-toed bipedal footprint cast taken at the trailhead."
	},
	"evid_fur_sample": {
		"id": "evid_fur_sample",
		"name": "Cryptid Fur Sample",
		"type": ItemType.EVIDENCE,
		"max_stack": 1,
		"description": "Coarse hollow-core guard hairs recovered from clawed pine bark."
	},
	"evid_rifle_casings": {
		"id": "evid_rifle_casings",
		"name": "Spent .30-06 Casings",
		"type": ItemType.EVIDENCE,
		"max_stack": 1,
		"description": "Fired brass cartridges recovered near the ranger station porch."
	}
}

# Stores active item inventory: item_id -> quantity (int)
var items: Dictionary = {}

# Tracks collected world objects to prevent duplication: uid -> bool
var collected_world_objects: Dictionary = {}

func _enter_tree() -> void:
	instance = self

func get_item_info(item_id: String) -> Dictionary:
	return ITEM_REGISTRY.get(item_id, {
		"id": item_id,
		"name": item_id.capitalize(),
		"type": ItemType.RESOURCE,
		"max_stack": 99,
		"description": "Unknown item."
	})

func has_item(item_id: String, min_quantity: int = 1) -> bool:
	return items.get(item_id, 0) >= min_quantity

func get_item_count(item_id: String) -> int:
	return items.get(item_id, 0)

## Adds an item to the inventory. Returns true if added, false if invalid or stack full.
func add_item(item_id: String, quantity: int = 1) -> bool:
	if quantity <= 0:
		return false

	var info = get_item_info(item_id)
	var max_stack = info.get("max_stack", 99)
	var current = items.get(item_id, 0)

	if current >= max_stack:
		return false

	var add_amount = min(quantity, max_stack - current)
	items[item_id] = current + add_amount

	item_added.emit(item_id, add_amount, items[item_id])
	inventory_changed.emit()
	return true

## Removes an item from the inventory. Returns true if successful, false if insufficient.
func remove_item(item_id: String, quantity: int = 1) -> bool:
	if quantity <= 0:
		return false

	var current = items.get(item_id, 0)
	if current < quantity:
		return false # Atomic failure: do not remove partial amount

	var new_total = current - quantity
	if new_total <= 0:
		items.erase(item_id)
		new_total = 0
	else:
		items[item_id] = new_total

	item_removed.emit(item_id, quantity, new_total)
	inventory_changed.emit()
	return true

## World pickup tracking
func can_collect_world_object(world_uid: String) -> bool:
	if world_uid.is_empty():
		return true
	return not collected_world_objects.get(world_uid, false)

func mark_world_object_collected(world_uid: String) -> void:
	if not world_uid.is_empty():
		collected_world_objects[world_uid] = true

## Serialization
func get_save_data() -> Dictionary:
	return {
		"items": items.duplicate(true),
		"collected_world_objects": collected_world_objects.duplicate(true)
	}

func load_save_data(data: Dictionary) -> void:
	if data.has("items"):
		items = data["items"].duplicate(true)
	if data.has("collected_world_objects"):
		collected_world_objects = data["collected_world_objects"].duplicate(true)
	inventory_changed.emit()
