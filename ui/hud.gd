class_name HUD
extends CanvasLayer

## Minimalist Survival Horror HUD for The Black Pines.

@onready var crosshair: ColorRect = $Root/Crosshair
@onready var prompt_label: Label = $Root/PromptLabel
@onready var stamina_bar: ProgressBar = $Root/BottomLeft/StaminaBar
@onready var health_bar: ProgressBar = $Root/BottomLeft/HealthBar
@onready var bleed_label: Label = $Root/BottomLeft/BleedLabel
@onready var flashlight_label: Label = $Root/BottomRight/FlashlightLabel
@onready var notification_label: Label = $Root/TopCenter/NotificationLabel
@onready var inspection_backdrop: ColorRect = $Root/InspectionBackdrop
@onready var inspection_panel: PanelContainer = $Root/InspectionPanel
@onready var inspection_title: Label = $Root/InspectionPanel/VBox/InspectionTitle
@onready var inspection_body: Label = $Root/InspectionPanel/VBox/InspectionBody

var notif_timer: float = 0.0

@onready var journal_dialog: Control = $Root/JournalDialog
@onready var inventory_dialog: Control = $Root/InventoryDialog

# Optimization: Cache last modal_open state to avoid mutating crosshair properties unnecessarily
var _last_modal_open: Variant = null

func _ready() -> void:
	prompt_label.text = ""
	notification_label.text = ""
	inspection_panel.visible = false
	if inspection_backdrop:
		inspection_backdrop.visible = false
	if bleed_label:
		bleed_label.visible = false

	# Optimization: Event-driven modal visibility updates.
	# Rather than polling multiple modal states every frame in _process() (60-144+ FPS),
	# connect to the visibility_changed signals of the modal dialogs and panels.
	# Expected performance impact: Completely eliminates crosshair modal visibility polling
	# (saving 3,600 to 8,640+ evaluations per minute) with zero frame overhead.
	if inspection_panel:
		inspection_panel.visibility_changed.connect(_update_crosshair_visibility)
	if journal_dialog:
		journal_dialog.visibility_changed.connect(_update_crosshair_visibility)
	if inventory_dialog:
		inventory_dialog.visibility_changed.connect(_update_crosshair_visibility)
	_update_crosshair_visibility()

	# Optimization: Start with processing disabled since there are no active notifications.
	# Rather than running _process() every frame (60-144+ FPS) when no notification is visible,
	# we enable processing on-demand only when a notification is displayed.
	set_process(false)

func _process(delta: float) -> void:
	# Optimization: On-demand notification timer processing.
	# When the notification countdown reaches 0, clear text and disable processing immediately
	# so the engine spends zero CPU cycles invoking _process() on this CanvasLayer while idle.
	# Expected performance impact: Eliminates ~99% of HUD per-frame calls during normal gameplay.
	if notif_timer > 0.0:
		notif_timer -= delta
		if notif_timer <= 0.0:
			notif_timer = 0.0
			notification_label.text = ""
			set_process(false)
	else:
		set_process(false)

func _update_crosshair_visibility() -> void:
	if not crosshair:
		return
	var modal_open: bool = inspection_panel.visible or (journal_dialog and journal_dialog.visible) or (inventory_dialog and inventory_dialog.visible)
	if modal_open != _last_modal_open:
		_last_modal_open = modal_open
		crosshair.visible = not modal_open

var current_flashlight_on: bool = true
var current_battery: float = 100.0

func setup_player(player: Player) -> void:
	player.stamina_changed.connect(_on_stamina_changed)
	player.health_changed.connect(_on_health_changed)
	player.flashlight_toggled.connect(_on_flashlight_toggled)
	player.flashlight_battery_changed.connect(_on_flashlight_battery_changed)
	player.interaction_prompt_changed.connect(_on_interaction_prompt_changed)
	player.inspection_displayed.connect(_on_inspection_displayed)
	player.notification_posted.connect(_on_notification_posted)
	if player.health_component:
		player.health_component.bleed_started.connect(func(): if bleed_label: bleed_label.visible = true)
		player.health_component.bleed_stopped.connect(func(): if bleed_label: bleed_label.visible = false)

func close_inspection() -> void:
	inspection_panel.visible = false
	if inspection_backdrop:
		inspection_backdrop.visible = false
	_update_crosshair_visibility()

func _unhandled_input(event: InputEvent) -> void:
	if inspection_panel.visible:
		if event.is_action_pressed("interact") or event.is_action_pressed("toggle_pause"):
			close_inspection()
			get_viewport().set_input_as_handled()
		elif event.is_action_pressed("toggle_inventory") or event.is_action_pressed("toggle_journal"):
			close_inspection()

func _on_health_changed(curr: float, max_val: float) -> void:
	if health_bar:
		health_bar.max_value = max_val
		health_bar.value = curr
		health_bar.modulate.a = 0.4 if curr >= max_val - 0.5 else 0.95

func _on_stamina_changed(curr: float, max_val: float) -> void:
	stamina_bar.max_value = max_val
	stamina_bar.value = curr
	# Fade stamina bar when full to keep screen clean
	stamina_bar.modulate.a = 0.3 if curr >= max_val - 0.5 else 0.85

func _on_flashlight_toggled(is_on: bool) -> void:
	current_flashlight_on = is_on
	_update_flashlight_display()

func _on_flashlight_battery_changed(curr: float, _max_val: float) -> void:
	current_battery = curr
	_update_flashlight_display()

func _update_flashlight_display() -> void:
	if not flashlight_label:
		return
	if current_battery <= 0.0:
		flashlight_label.text = "[F] FLASHLIGHT: DEPLETED [R]"
		flashlight_label.modulate = Color(0.9, 0.25, 0.2, 0.9)
	elif current_flashlight_on:
		flashlight_label.text = "[F] FLASHLIGHT: ON (%d%%)" % int(current_battery)
		if current_battery <= 20.0:
			flashlight_label.modulate = Color(1.0, 0.5, 0.2, 0.95)
		else:
			flashlight_label.modulate = Color(1.0, 0.95, 0.7, 0.9)
	else:
		flashlight_label.text = "[F] FLASHLIGHT: OFF (%d%%)" % int(current_battery)
		flashlight_label.modulate = Color(0.5, 0.5, 0.5, 0.5)

func _on_interaction_prompt_changed(text: String) -> void:
	prompt_label.text = text
	if crosshair:
		if text != "":
			crosshair.color = Color(1.0, 0.9, 0.5, 0.95)
			crosshair.offset_left = -3.0
			crosshair.offset_top = -3.0
			crosshair.offset_right = 3.0
			crosshair.offset_bottom = 3.0
		else:
			crosshair.color = Color(1.0, 1.0, 1.0, 0.5)
			crosshair.offset_left = -2.0
			crosshair.offset_top = -2.0
			crosshair.offset_right = 2.0
			crosshair.offset_bottom = 2.0

func _on_inspection_displayed(title: String, text: String) -> void:
	if journal_dialog and journal_dialog.visible and journal_dialog.has_method("close_journal"):
		journal_dialog.close_journal()
	if inventory_dialog and inventory_dialog.visible and inventory_dialog.has_method("close_inventory"):
		inventory_dialog.close_inventory()
	inspection_title.text = title
	inspection_body.text = text
	inspection_panel.visible = true
	if inspection_backdrop:
		inspection_backdrop.visible = true
	_update_crosshair_visibility()

func _on_notification_posted(msg: String) -> void:
	notification_label.text = msg
	notif_timer = 3.0
	# Re-enable process loop to tick down notification timer
	set_process(true)
