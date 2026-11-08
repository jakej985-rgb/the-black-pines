class_name InspectableClue
extends Interactable

## Clues found in the forest (cryptid footprints, clawed bark, abandoned gear).

const JournalManagerClass = preload("res://scripts/systems/journal_manager.gd")

@export_multiline var inspection_text: String = "Something abnormal was here recently."
@export var clue_title: String = "Cryptid Clue"
@export var clue_id: String = ""
@export var one_time_investigation: bool = false
var investigated: bool = false

signal clue_inspected(title: String, text: String)

func _ready() -> void:
	if prompt_message == "[E] Inspect":
		prompt_message = "[E] Examine Clue"
	if clue_id.is_empty():
		clue_id = clue_title.to_snake_case()

func _on_interacted(player: Node) -> void:
	investigated = true
	clue_inspected.emit(clue_title, inspection_text)
	if JournalManagerClass.instance:
		var is_new = JournalManagerClass.instance.record_clue(clue_id, clue_title, inspection_text)
		if is_new and player and player.has_method("show_notification"):
			player.show_notification("Evidence Logged: " + clue_title)
	if player.has_method("show_inspection_dialog"):
		player.show_inspection_dialog(clue_title, inspection_text)
	if one_time_investigation:
		prompt_message = "[Examined]"
		is_usable = false
