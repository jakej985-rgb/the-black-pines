class_name CollectibleItem
extends Interactable

## Pickable resource in the wilderness (scrap, batteries, sticks, herbs).

@export var item_name: String = "Supplies"
@export var quantity: int = 1

func _ready() -> void:
	prompt_message = "[E] Pick up " + item_name

func _on_interacted(player: Node) -> void:
	if player.has_method("add_inventory_item"):
		player.add_inventory_item(item_name, quantity)
	elif player.has_method("show_notification"):
		player.show_notification("Acquired: " + str(quantity) + "x " + item_name)
	
	# Small pickup animation / sound placeholder before freeing
	queue_free()
