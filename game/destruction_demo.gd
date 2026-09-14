extends "res://controls_session.gd"
## Explicit fixture controls, not the attack/game-loop implementation.
const Destruction = preload("res://destruction.gd")
const Target = preload("res://destructible_target.gd")
const Sound = preload("res://sound.gd")
var sound: Node3D
var debris: Node3D
var targets: Array[Node3D] = []
var fixture_label: Label
var break_requested := false
var reset_requested := false

func _ready() -> void:
    super._ready()
    debris = Destruction.new()
    add_child(debris)
    sound = Sound.new()
    add_child(sound)
    sound.bind(debris)
    sound.gameplay_input = controls
    player_replaced.connect(func(_player): sound.clear())
    make_targets()
    fixture_label = Label.new()
    fixture_label.position = Vector2(16, 92)
    fixture_label.text = "DESTRUCTION FIXTURE | B: rupture all pylons | N: reset debris/targets | No combat | Audio enabled"
    hud.get_parent().add_child(fixture_label)
    if "--audio-test" in OS.get_cmdline_user_args():
        var tests = load("res://tests/audio_tests.gd").new()
        add_child(tests)
        tests.call_deferred("run", self)
    if "--destruction-test" in OS.get_cmdline_user_args():
        var tests = load("res://tests/destruction_tests.gd").new()
        add_child(tests)
        tests.call_deferred("run", self)

func make_targets() -> void:
    for target in targets:
        target.free()
    targets.clear()
    for i in arena.pylon_spawns.size():
        var target := Target.new()
        target.entity_id = i + 1
        target.event_seed = run_seed + i
        target.destruction = debris
        add_child(target)
        target.global_transform = arena.global_transform * arena.pylon_spawns[i]
        targets.append(target)

func _unhandled_key_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.physical_keycode == KEY_B:
            break_requested = true
        if event.physical_keycode == KEY_N:
            reset_requested = true

func _physics_process(dt: float) -> void:
    super._physics_process(dt)
    if reset_requested:
        reset_requested = false
        sound.clear()
        debris.clear()
        make_targets()
    if break_requested:
        break_requested = false
        for target in targets:
            target.apply_damage(100, target.global_position, Vector3.UP)

func start(seed_value: int) -> void:
    super.start(seed_value)
    break_requested = false
    reset_requested = false
    if is_instance_valid(debris):
        sound.clear()
        debris.clear()
        make_targets()
