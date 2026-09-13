extends Node
## Event-fed controls, not global polling: transitions cannot resurrect held input.
signal pause_requested
signal restart_requested
const KEYS := {"move_left": KEY_A, "move_right": KEY_D, "move_up": KEY_W,
    "move_down": KEY_S, "dash": KEY_SPACE, "pause": KEY_ESCAPE, "restart": KEY_R}
var held: Dictionary = {}
var dash_edge := false
var enabled := true
var pointer := Vector2.ZERO
var pointer_known := false

static func install_mapping() -> void:
    for action in KEYS:
        if not InputMap.has_action(action):
            InputMap.add_action(action)
        InputMap.action_erase_events(action)
        var event := InputEventKey.new()
        event.physical_keycode = KEYS[action]
        InputMap.action_add_event(action, event)
    if not InputMap.has_action("fire"):
        InputMap.add_action("fire")
    InputMap.action_erase_events("fire")
    var button := InputEventMouseButton.new()
    button.button_index = MOUSE_BUTTON_LEFT
    InputMap.action_add_event("fire", button)

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    install_mapping()
    Input.use_accumulated_input = false

func clear_controls() -> void:
    held.clear()
    dash_edge = false

func set_enabled(value: bool) -> void:
    enabled = value
    clear_controls()

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion or event is InputEventMouseButton:
        pointer = event.position
        pointer_known = true
    if event is InputEventKey and event.echo:
        return
    for action in ["move_left", "move_right", "move_up", "move_down", "dash", "fire", "pause", "restart"]:
        if not event.is_action(action):
            continue
        if event.is_released():
            held.erase(action)
            continue
        if not event.is_pressed() or held.has(action):
            continue
        if action == "pause":
            held[action] = true
            pause_requested.emit()
        elif action == "restart":
            held[action] = true
            restart_requested.emit()
        elif enabled:
            held[action] = true
            if action == "dash":
                dash_edge = true

func read_input() -> Dictionary:
    var movement := Vector2(float(held.has("move_right")) - float(held.has("move_left")),
        float(held.has("move_down")) - float(held.has("move_up"))).limit_length()
    var result := {"movement": movement, "pointer": pointer, "pointer_known": pointer_known,
        "fire": enabled and held.has("fire"), "dash": enabled and dash_edge}
    dash_edge = false
    return result
