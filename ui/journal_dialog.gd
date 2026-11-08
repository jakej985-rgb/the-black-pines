class_name JournalDialog
extends Control

## UI interface for the player's field notebook and objective log.

@onready var objectives_container: VBoxContainer = $Panel/MarginContainer/VBox/TabContainer/Objectives/Scroll/ObjectivesList
@onready var clues_container: VBoxContainer = $Panel/MarginContainer/VBox/TabContainer/Evidence/Scroll/CluesList
@onready var tab_container: TabContainer = $Panel/MarginContainer/VBox/TabContainer

func _ready() -> void:
	visible = false
	if JournalManager.instance:
		JournalManager.instance.objective_status_changed.connect(_on_objective_status_changed)
		JournalManager.instance.clue_recorded.connect(_on_clue_recorded)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_journal"):
		toggle_journal()
		get_viewport().set_input_as_handled()
	elif visible and (event.is_action_pressed("toggle_pause") or event.is_action_pressed("interact")):
		close_journal()
		get_viewport().set_input_as_handled()

func toggle_journal() -> void:
	if visible:
		close_journal()
	else:
		open_journal()

func open_journal() -> void:
	refresh_display()
	visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func close_journal() -> void:
	visible = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func refresh_display() -> void:
	_refresh_objectives()
	_refresh_clues()

func _refresh_objectives() -> void:
	if not objectives_container:
		return
	for child in objectives_container.get_children():
		child.queue_free()

	if not JournalManager.instance:
		var empty_lbl = Label.new()
		empty_lbl.text = "No active investigation."
		objectives_container.add_child(empty_lbl)
		return

	var active_objs = JournalManager.instance.get_active_objectives()
	var completed_objs = JournalManager.instance.get_completed_objectives()

	if active_objs.is_empty() and completed_objs.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "No objectives recorded."
		objectives_container.add_child(empty_lbl)
		return

	if not active_objs.is_empty():
		var sec_lbl = Label.new()
		sec_lbl.text = "-- ACTIVE OBJECTIVES --"
		sec_lbl.modulate = Color(1.0, 0.85, 0.4)
		objectives_container.add_child(sec_lbl)

		for obj in active_objs:
			var card = _create_objective_card(obj, false)
			objectives_container.add_child(card)

	if not completed_objs.is_empty():
		var sec_lbl = Label.new()
		sec_lbl.text = "-- COMPLETED --"
		sec_lbl.modulate = Color(0.5, 0.8, 0.5)
		objectives_container.add_child(sec_lbl)

		for obj in completed_objs:
			var card = _create_objective_card(obj, true)
			objectives_container.add_child(card)

func _create_objective_card(obj: Dictionary, is_completed: bool) -> PanelContainer:
	var panel = PanelContainer.new()
	var vbox = VBoxContainer.new()
	panel.add_child(vbox)

	var title_lbl = Label.new()
	var mark = "[✓] " if is_completed else "[ ] "
	title_lbl.text = mark + obj.get("title", "Objective")
	title_lbl.modulate = Color(0.6, 0.9, 0.6) if is_completed else Color(1.0, 0.95, 0.8)
	vbox.add_child(title_lbl)

	var desc_lbl = Label.new()
	desc_lbl.text = "    " + obj.get("description", "")
	desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc_lbl.modulate = Color(0.7, 0.7, 0.7)
	vbox.add_child(desc_lbl)

	return panel

func _refresh_clues() -> void:
	if not clues_container:
		return
	for child in clues_container.get_children():
		child.queue_free()

	if not JournalManager.instance:
		return

	var clues = JournalManager.instance.get_all_clues()
	if clues.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "No forensic evidence or document clues logged yet.\nExplore the forest, cabin, and trail to discover clues."
		empty_lbl.modulate = Color(0.6, 0.6, 0.6)
		clues_container.add_child(empty_lbl)
		return

	for clue in clues:
		var panel = PanelContainer.new()
		var vbox = VBoxContainer.new()
		panel.add_child(vbox)

		var title_lbl = Label.new()
		title_lbl.text = "• " + clue.get("title", "Evidence") + " (" + clue.get("discovered_at", "") + ")"
		title_lbl.modulate = Color(1.0, 0.85, 0.5)
		vbox.add_child(title_lbl)

		var body_lbl = Label.new()
		body_lbl.text = clue.get("text", "")
		body_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body_lbl.modulate = Color(0.85, 0.85, 0.85)
		vbox.add_child(body_lbl)

		clues_container.add_child(panel)

func _on_objective_status_changed(_id: String, _status: int) -> void:
	if visible:
		refresh_display()

func _on_clue_recorded(_id: String, _entry: Dictionary) -> void:
	if visible:
		refresh_display()
