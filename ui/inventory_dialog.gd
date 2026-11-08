class_name InventoryDialog
extends Control

## UI interface for the player's survival inventory and gear.

const InventoryManagerClass = preload("res://scripts/systems/inventory_manager.gd")
const CraftingManagerClass = preload("res://scripts/systems/crafting_manager.gd")

@onready var resources_list: VBoxContainer = $Panel/Margin/VBox/Tabs/Resources/Scroll/List
@onready var tools_list: VBoxContainer = $Panel/Margin/VBox/Tabs/Tools/Scroll/List
@onready var evidence_list: VBoxContainer = $Panel/Margin/VBox/Tabs/Evidence/Scroll/List
@onready var crafting_list: VBoxContainer = $Panel/Margin/VBox/Tabs/Crafting/Scroll/List
@onready var desc_label: Label = $Panel/Margin/VBox/ItemDetails/DescriptionLabel

func _ready() -> void:
	visible = false
	if InventoryManagerClass.instance:
		InventoryManagerClass.instance.inventory_changed.connect(refresh_display)
	if CraftingManagerClass.instance:
		CraftingManagerClass.instance.recipe_crafted.connect(func(_rid, _oid, _qty): refresh_display())

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_inventory"):
		toggle_inventory()
		get_viewport().set_input_as_handled()
	elif visible and (event.is_action_pressed("toggle_pause") or event.is_action_pressed("interact")):
		close_inventory()
		get_viewport().set_input_as_handled()

func toggle_inventory() -> void:
	if visible:
		close_inventory()
	else:
		open_inventory()

func open_inventory() -> void:
	refresh_display()
	visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func close_inventory() -> void:
	visible = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func refresh_display() -> void:
	_populate_category(resources_list, [InventoryManager.ItemType.RESOURCE])
	_populate_category(tools_list, [InventoryManager.ItemType.TOOL, InventoryManager.ItemType.CONSUMABLE])
	_populate_category(evidence_list, [InventoryManager.ItemType.EVIDENCE])
	_populate_crafting()

func _populate_category(container: VBoxContainer, allowed_types: Array) -> void:
	if not container:
		return
	for child in container.get_children():
		child.queue_free()

	if not InventoryManagerClass.instance:
		return

	var found = 0
	for item_id in InventoryManagerClass.instance.items:
		var info = InventoryManagerClass.instance.get_item_info(item_id)
		if info.get("type", 0) in allowed_types:
			found += 1
			var row = _create_item_row(item_id, info, InventoryManagerClass.instance.items[item_id])
			container.add_child(row)

	if found == 0:
		var empty_lbl = Label.new()
		empty_lbl.text = "No items in this category."
		empty_lbl.modulate = Color(0.6, 0.6, 0.6)
		container.add_child(empty_lbl)

func _populate_crafting() -> void:
	if not crafting_list:
		return
	for child in crafting_list.get_children():
		child.queue_free()

	if not CraftingManagerClass.instance:
		return

	var recipes = CraftingManagerClass.instance.get_all_recipes()
	if recipes.is_empty():
		var empty_lbl = Label.new()
		empty_lbl.text = "No crafting blueprints available."
		empty_lbl.modulate = Color(0.6, 0.6, 0.6)
		crafting_list.add_child(empty_lbl)
		return

	for recipe in recipes:
		var recipe_id: String = recipe.get("id", "")
		var recipe_name: String = recipe.get("name", recipe_id)
		var can_make: bool = CraftingManagerClass.instance.can_craft(recipe_id)

		var hbox = HBoxContainer.new()
		hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var info_btn = Button.new()
		info_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		info_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT

		# Format ingredients list
		var ing_parts: Array = []
		var ingredients: Dictionary = recipe.get("ingredients", {})
		for item_id in ingredients:
			var req: int = ingredients[item_id]
			var owned: int = InventoryManagerClass.instance.get_item_count(item_id) if InventoryManagerClass.instance else 0
			var item_info = InventoryManagerClass.instance.get_item_info(item_id) if InventoryManagerClass.instance else {}
			var item_name = item_info.get("name", item_id)
			ing_parts.append("%dx %s (%d/%d)" % [req, item_name, owned, req])

		info_btn.text = "%s [%s]" % [recipe_name, ", ".join(ing_parts)]
		info_btn.mouse_entered.connect(func():
			if desc_label:
				desc_label.text = recipe.get("description", "")
		)
		hbox.add_child(info_btn)

		var craft_btn = Button.new()
		craft_btn.text = "Craft"
		craft_btn.custom_minimum_size = Vector2(90, 0)
		craft_btn.disabled = not can_make
		craft_btn.pressed.connect(func():
			var success = CraftingManagerClass.instance.craft_recipe(recipe_id)
			if success and desc_label:
				desc_label.text = "Crafted 1x %s successfully!" % recipe_name
		)
		hbox.add_child(craft_btn)

		crafting_list.add_child(hbox)

func _create_item_row(item_id: String, info: Dictionary, qty: int) -> Button:
	var btn = Button.new()
	var max_stack = info.get("max_stack", 99)
	btn.text = "%s  x%d / %d" % [info.get("name", item_id), qty, max_stack]
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.mouse_entered.connect(func():
		if desc_label:
			desc_label.text = info.get("description", "")
	)
	return btn

