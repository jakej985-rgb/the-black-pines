extends SceneTree

## Standalone regression tests for inspection dismissal and modal mouse-capture guards.
## Run: godot --headless -s res://tests/test_modal_input.gd
## Exits with code 0 on success, 1 on failure.
## Note: the headless DisplayServer ignores mouse mode changes, so mouse-mode
## assertions only run with a real display (e.g. `godot -s res://tests/test_modal_input.gd`).
## Skipped assertions are counted and reported; pass `-- --require-mouse` to make
## any skipped mouse-mode assertion fail the run (use this in CI with a display).

var _failures: int = 0
var _skipped: int = 0
var _hud: Node = null


func _initialize() -> void:
	_ensure_actions()
	_hud = load("res://ui/hud.tscn").instantiate()
	root.add_child(_hud)
	# Defer so @onready vars and _ready() have run.
	call_deferred("_run_all")


func _run_all() -> void:
	_test_dismiss_key(KEY_SPACE, "Space")
	_test_dismiss_key(KEY_ENTER, "Enter")
	_test_dismiss_key(KEY_KP_ENTER, "KP_Enter")
	_test_space_dismiss_releases_jump()
	_test_echo_does_not_dismiss()
	_test_unrelated_key_does_not_dismiss()
	_test_close_inspection_is_idempotent()
	_test_inventory_close_keeps_cursor_with_inspection_open()
	_test_journal_close_keeps_cursor_with_inspection_open()
	_test_inspection_close_keeps_cursor_with_inventory_open()
	_test_guard_decisions_headless()
	_test_escape_dismisses_inspection()
	_test_interact_dismisses_inspection()

	if _skipped > 0:
		printerr("SKIPPED %d mouse-mode assertion(s) (headless display)" % _skipped)
		if "--require-mouse" in OS.get_cmdline_user_args():
			_failures += _skipped
	if _failures == 0:
		print("ALL TESTS PASSED")
	else:
		printerr("%d TEST(S) FAILED" % _failures)
	quit(1 if _failures > 0 else 0)


# --- helpers ---------------------------------------------------------------

func _ensure_actions() -> void:
	var defaults = {"jump": KEY_SPACE, "interact": KEY_E, "toggle_pause": KEY_ESCAPE, "toggle_journal": KEY_J, "toggle_inventory": KEY_TAB}
	for action in defaults:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			var ev := InputEventKey.new()
			ev.physical_keycode = defaults[action]
			InputMap.action_add_event(action, ev)


func _key(code: Key, echo: bool = false) -> InputEventKey:
	var ev := InputEventKey.new()
	ev.physical_keycode = code
	ev.pressed = true
	ev.echo = echo
	return ev


## Dispatch a key through the real engine pipeline (Input state + viewport
## GUI/unhandled routing) instead of calling _unhandled_input directly.
func _send(ev: InputEvent) -> void:
	Input.parse_input_event(ev)
	Input.flush_buffered_events()


func _open_inspection() -> void:
	_hud._on_inspection_displayed("Test Clue", "Body")


func _reset() -> void:
	_hud.close_inspection()
	if _hud.inventory_dialog.visible:
		_hud.inventory_dialog.visible = false
	if _hud.journal_dialog.visible:
		_hud.journal_dialog.visible = false
	Input.action_release("jump")


func _mouse_testable() -> bool:
	if DisplayServer.get_name() != "headless":
		return true
	_skipped += 1
	return false


func _check(cond: bool, name: String) -> void:
	if cond:
		print("PASS: ", name)
	else:
		_failures += 1
		printerr("FAIL: ", name)


# --- tests -----------------------------------------------------------------

func _test_dismiss_key(code: Key, label: String) -> void:
	_reset()
	_open_inspection()
	_check(_hud.inspection_panel.visible, "%s: inspection opens" % label)
	_send(_key(code))
	_check(not _hud.inspection_panel.visible, "%s dismisses inspection" % label)
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED, "%s dismiss recaptures mouse" % label)


func _test_space_dismiss_releases_jump() -> void:
	_reset()
	_open_inspection()
	# Real dispatch: Input registers the Space press as "jump" before the HUD sees it.
	_send(_key(KEY_SPACE))
	_check(not Input.is_action_pressed("jump"), "Space dismiss releases jump action")
	_check(not Input.is_action_just_pressed("jump"), "Space dismiss clears jump just_pressed")


func _test_echo_does_not_dismiss() -> void:
	_reset()
	_open_inspection()
	_send(_key(KEY_ENTER, true))
	_check(_hud.inspection_panel.visible, "Echo Enter does not dismiss")


func _test_unrelated_key_does_not_dismiss() -> void:
	_reset()
	_open_inspection()
	_send(_key(KEY_W))
	_check(_hud.inspection_panel.visible, "Unrelated key (W) does not dismiss")


func _test_close_inspection_is_idempotent() -> void:
	_reset()
	if _mouse_testable():
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_hud.close_inspection() # already hidden -> must be a no-op
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE, "close_inspection on hidden panel does not recapture")
	_check(not _hud.inspection_panel.visible, "close_inspection on hidden panel stays hidden")


func _test_inventory_close_keeps_cursor_with_inspection_open() -> void:
	_reset()
	_hud.inventory_dialog.visible = true
	_hud.inspection_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_hud.inventory_dialog.close_inventory()
	_check(not _hud.inventory_dialog.visible, "close_inventory hides inventory")
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE, "close_inventory keeps cursor while inspection open")


func _test_journal_close_keeps_cursor_with_inspection_open() -> void:
	_reset()
	_hud.journal_dialog.visible = true
	_hud.inspection_panel.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_hud.journal_dialog.close_journal()
	_check(not _hud.journal_dialog.visible, "close_journal hides journal")
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE, "close_journal keeps cursor while inspection open")


func _test_inspection_close_keeps_cursor_with_inventory_open() -> void:
	_reset()
	_hud.inspection_panel.visible = true
	_hud.inventory_dialog.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	_hud.close_inspection()
	_check(not _hud.inspection_panel.visible, "close_inspection hides panel")
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_VISIBLE, "close_inspection keeps cursor while inventory open")


## Display-independent: asserts the guard decision itself, so a regression that
## recaptures the cursor while another modal is open fails even in headless runs.
func _test_guard_decisions_headless() -> void:
	_reset()
	var inv = _hud.inventory_dialog
	var jrn = _hud.journal_dialog
	_check(not inv.is_other_modal_open(), "inventory guard: nothing open -> recapture allowed")
	_check(not jrn.is_other_modal_open(), "journal guard: nothing open -> recapture allowed")
	_hud.inspection_panel.visible = true
	_check(inv.is_other_modal_open(), "inventory guard: inspection open -> keep cursor")
	_check(jrn.is_other_modal_open(), "journal guard: inspection open -> keep cursor")
	_hud.inspection_panel.visible = false
	jrn.visible = true
	_check(inv.is_other_modal_open(), "inventory guard: journal open -> keep cursor")
	jrn.visible = false
	inv.visible = true
	_check(jrn.is_other_modal_open(), "journal guard: inventory open -> keep cursor")
	inv.visible = false


func _test_escape_dismisses_inspection() -> void:
	_reset()
	_open_inspection()
	_send(_key(KEY_ESCAPE))
	_check(not _hud.inspection_panel.visible, "Esc dismisses inspection")
	if _mouse_testable():
		_check(Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED, "Esc dismiss recaptures mouse")


func _test_interact_dismisses_inspection() -> void:
	_reset()
	_open_inspection()
	_send(_key(KEY_E))
	_check(not _hud.inspection_panel.visible, "E dismisses inspection")
