class_name JournalDialog
extends Control

## UI interface for the player's field notebook and objective log.

@onready var objectives_container: VBoxContainer = $Panel/MarginContainer/VBox/TabContainer/Objectives/Scroll/ObjectivesList
@onready var clues_container: VBoxContainer = $Panel/MarginContainer/VBox/TabContainer/Evidence/Scroll/CluesList
@onready var tab_container: TabContainer = $Panel/MarginContainer/VBox/TabContainer

func _ready() -> void:
	visible = false
	if tab_container:
		tab_container.tab_changed.connect(func(_idx): _focus_active_tab())
	# Optimization: Connect state update signals. When the dialog is hidden, signal handlers
	# avoid re-building controls offscreen because open_journal() calls refresh_display() on open.
	if JournalManager.instance:
		JournalManager.instance.objective_status_changed.connect(_on_objective_status_changed)
		JournalManager.instance.clue_recorded.connect(_on_clue_recorded)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_journal"):
		toggle_journal()
		get_viewport().set_input_as_handled()
	elif visible and event.is_action_pressed("toggle_inventory"):
		close_journal()
	elif visible and (event.is_action_pressed("toggle_pause") or event.is_action_pressed("interact")):
		close_journal()
		get_viewport().set_input_as_handled()
	elif visible and event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_Q or event.physical_keycode == KEY_E:
			var step = -1 if event.physical_keycode == KEY_Q else 1
			_switch_tab(step)
			get_viewport().set_input_as_handled()

func _switch_tab(direction: int) -> void:
	if not tab_container or tab_container.get_tab_count() == 0:
		return
	var count = tab_container.get_tab_count()
	tab_container.current_tab = (tab_container.current_tab + direction + count) % count
	_focus_active_tab()

func toggle_journal() -> void:
	if visible:
		close_journal()
	else:
		open_journal()

func open_journal() -> void:
	var inventory = get_parent().get_node_or_null("InventoryDialog") if get_parent() else null
	if inventory and inventory.visible:
		inventory.close_inventory()
	refresh_display()
	visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_focus_active_tab()

func _focus_active_tab() -> void:
	if not tab_container:
		return
	var current_bar = tab_container.get_tab_bar()
	if current_bar:
		current_bar.grab_focus()

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
	# Optimization: Only rebuild objective UI controls if the journal dialog is currently visible.
	# When hidden, open_journal() refreshes the layout on open, avoiding offscreen node allocations
	# and layout calculations during exploration or world progression events.
	# Expected performance impact: Eliminates 100% of offscreen UI control allocations and queue_free churn.
	if visible:
		refresh_display()

func _on_clue_recorded(_id: String, _entry: Dictionary) -> void:
	# Optimization: Only rebuild evidence UI controls if the journal dialog is currently visible.
	# When hidden, open_journal() refreshes the layout on open, avoiding offscreen node allocations
	# and layout calculations during exploration or world progression events.
	# Expected performance impact: Eliminates 100% of offscreen UI control allocations and queue_free churn.
	if visible:
		refresh_display()
