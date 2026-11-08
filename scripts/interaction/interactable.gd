class_name Interactable
extends CollisionObject3D

## Base class for interactive objects in the world (clues, supplies, doors, traps).

@export var prompt_message: String = "[E] Inspect"
@export var is_usable: bool = true

signal interacted(player: Node)

func interact(player: Node) -> void:
	if not is_usable:
		return
	interacted.emit(player)
	_on_interacted(player)

func _on_interacted(_player: Node) -> void:
	pass

func get_prompt() -> String:
	return prompt_message
