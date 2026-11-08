class_name CollectibleItem
extends Interactable

## Pickable resource in the wilderness (scrap, batteries, sticks, herbs).

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")

@export var item_name: String = "Supplies"
@export var item_id: String = ""
@export var world_uid: String = ""
@export var quantity: int = 1

func _ready() -> void:
	if item_id.is_empty():
		item_id = _resolve_default_item_id(item_name)
	if world_uid.is_empty():
		world_uid = str(get_path())

	if InventoryManagerClass.instance and not InventoryManagerClass.instance.can_collect_world_object(world_uid):
		queue_free()
		return

	prompt_message = "[E] Pick up " + item_name

func _resolve_default_item_id(name_str: String) -> String:
	match name_str:
		"Rusted Scrap Metal": return "scrap_metal"
		"Dry Pine Branches": return "dry_branches"
		"Roadside Distress Flare": return "road_flare"
		"Forest Angelica Herbs": return "herbs"
		"Clean Cotton Cloth": return "clean_cloth"
		"D-Cell Batteries": return "battery_pack"
		_: return name_str.to_snake_case()

func _on_interacted(player: Node) -> void:
	var success = true
	if InventoryManagerClass.instance:
		success = InventoryManagerClass.instance.add_item(item_id, quantity)
		if success:
			InventoryManagerClass.instance.mark_world_object_collected(world_uid)

	if success:
		if player and player.has_method("show_notification"):
			player.show_notification("Acquired: %dx %s" % [quantity, item_name])
		if AudioDirector.instance:
			AudioDirector.instance.play_pickup()
		queue_free()
	else:
		if player and player.has_method("show_notification"):
			player.show_notification("Cannot carry more " + item_name + " (Inventory Full)")
