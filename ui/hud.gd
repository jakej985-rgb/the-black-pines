class_name HUD
extends CanvasLayer

## Minimalist Survival Horror HUD for The Black Pines.

@onready var prompt_label: Label = $Root/PromptLabel
@onready var stamina_bar: ProgressBar = $Root/BottomLeft/StaminaBar
@onready var flashlight_label: Label = $Root/BottomRight/FlashlightLabel
@onready var notification_label: Label = $Root/TopCenter/NotificationLabel
@onready var inspection_panel: PanelContainer = $Root/InspectionPanel
@onready var inspection_title: Label = $Root/InspectionPanel/VBox/InspectionTitle
@onready var inspection_body: Label = $Root/InspectionPanel/VBox/InspectionBody

var notif_timer: float = 0.0

func _ready() -> void:
	prompt_label.text = ""
	notification_label.text = ""
	inspection_panel.visible = false

func _process(delta: float) -> void:
	if notif_timer > 0.0:
		notif_timer -= delta
		if notif_timer <= 0.0:
			notification_label.text = ""

func setup_player(player: Player) -> void:
	player.stamina_changed.connect(_on_stamina_changed)
	player.flashlight_toggled.connect(_on_flashlight_toggled)
	player.interaction_prompt_changed.connect(_on_interaction_prompt_changed)
	player.inspection_displayed.connect(_on_inspection_displayed)
	player.notification_posted.connect(_on_notification_posted)

func _unhandled_input(event: InputEvent) -> void:
	if inspection_panel.visible:
		if event.is_action_pressed("interact") or event.is_action_pressed("toggle_pause"):
			inspection_panel.visible = false
			get_viewport().set_input_as_handled()

func _on_stamina_changed(curr: float, max_val: float) -> void:
	stamina_bar.max_value = max_val
	stamina_bar.value = curr
	# Fade stamina bar when full to keep screen clean
	stamina_bar.modulate.a = 0.3 if curr >= max_val - 0.5 else 0.85

func _on_flashlight_toggled(is_on: bool) -> void:
	flashlight_label.text = "[F] FLASHLIGHT: ON" if is_on else "[F] FLASHLIGHT: OFF"
	flashlight_label.modulate = Color(1.0, 0.95, 0.7, 0.9) if is_on else Color(0.5, 0.5, 0.5, 0.5)

func _on_interaction_prompt_changed(text: String) -> void:
	prompt_label.text = text

func _on_inspection_displayed(title: String, text: String) -> void:
	inspection_title.text = title
	inspection_body.text = text
	inspection_panel.visible = true

func _on_notification_posted(msg: String) -> void:
	notification_label.text = msg
	notif_timer = 3.0
