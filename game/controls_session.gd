extends Node3D
## Controls integration only: no opposition, damage, objectives, countdown or win rules.
## Later rule owner calls finish(WON/LOST); R exercises this same restart path.
signal state_changed(state: int)
signal player_replaced(player: CharacterBody3D)
const ArenaScript = preload("res://arena.gd")
const CameraScript = preload("res://arena_camera.gd")
const InputScript = preload("res://player_input.gd")
const PlayerScript = preload("res://player.gd")
enum State { PLAYING, PAUSED, WON, LOST }
var state := State.PLAYING
var arena: Node3D
var camera: Camera3D
var controls: Node
var player: CharacterBody3D
var hud: Label
var panel: PanelContainer
var message: Label
var elapsed := 0.0
var run_seed := 1201
var generation := 0
var shots := 0

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_PAUSABLE
    process_physics_priority = -10
    arena = ArenaScript.new()
    add_child(arena)
    var environment := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("09131e")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("bed5ea")
    env.ambient_light_energy = 0.30
    environment.environment = env
    add_child(environment)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-58, -32, 0)
    sun.light_color = Color("fff0d0")
    sun.light_energy = 0.65
    sun.shadow_enabled = true
    add_child(sun)
    camera = CameraScript.new()
    add_child(camera)
    camera.configure(arena)
    controls = InputScript.new()
    add_child(controls)
    controls.pause_requested.connect(toggle_pause)
    controls.restart_requested.connect(request_restart)
    var canvas := CanvasLayer.new()
    add_child(canvas)
    hud = Label.new()
    hud.position = Vector2(16, 12)
    hud.add_theme_font_size_override("font_size", 16)
    canvas.add_child(hud)
    panel = PanelContainer.new()
    panel.position = Vector2(24, 120)
    panel.custom_minimum_size = Vector2(510, 180)
    canvas.add_child(panel)
    message = Label.new()
    message.add_theme_font_size_override("font_size", 20)
    panel.add_child(message)
    start(1201)
    if "--controls-test" in OS.get_cmdline_user_args():
        var tests = load("res://tests/controls_tests.gd").new()
        add_child(tests)
        tests.call_deferred("run", self)

func start(seed_value: int) -> void:
    get_tree().paused = false
    run_seed = seed_value
    controls.set_enabled(true)
    if is_instance_valid(player):
        remove_child(player)
        player.free()
    player = PlayerScript.new()
    player.controls = controls
    player.camera = camera
    add_child(player)
    player.global_transform = arena.global_transform * arena.player_spawn
    elapsed = 0.0
    shots = 0
    generation += 1
    player.fired.connect(on_fired)
    state = State.PLAYING
    Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    rebuild_run()
    player_replaced.emit(player)
    state_changed.emit(state)
    refresh_hud()

func rebuild_run() -> void:
    # Extension point inside the ONE restart boundary, before observers see PLAYING.
    pass

func on_fired(_origin: Vector3, _direction: Vector3) -> void:
    shots += 1
    # Visible command acknowledgement, NOT a hit/damage/projectile simulation.
    refresh_hud()

func toggle_pause() -> void:
    if state == State.PLAYING:
        pause(true)
    elif state == State.PAUSED:
        pause(false)

func pause(value: bool) -> void:
    if state not in [State.PLAYING, State.PAUSED]:
        return
    state = State.PAUSED if value else State.PLAYING
    controls.set_enabled(not value)
    player.velocity = Vector3.ZERO
    get_tree().paused = value
    Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    state_changed.emit(state)
    refresh_hud()

func finish(result: int) -> void:
    # Integration boundary, not a claim that the game can yet win or lose.
    if state != State.PLAYING or result not in [State.WON, State.LOST]:
        return
    state = result
    controls.set_enabled(false)
    player.velocity = Vector3.ZERO
    get_tree().paused = true
    Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    state_changed.emit(state)
    refresh_hud()

func request_restart() -> void:
    if state in [State.WON, State.LOST]:
        start(run_seed)

func _notification(what: int) -> void:
    if what == NOTIFICATION_APPLICATION_FOCUS_OUT and is_instance_valid(controls):
        controls.pointer_known = false
        if state == State.PLAYING:
            pause(true)
        else:
            controls.clear_controls()

func _physics_process(dt: float) -> void:
    if state == State.PLAYING:
        elapsed += dt
    refresh_hud()

func refresh_hud() -> void:
    hud.text = "BREAKWATER / CONTROLS SLICE (no combat or run objectives yet)\nWASD move | Mouse aim | Hold LMB fire | Space dash | Esc pause\nDash: %s   Fire commands: %d (25 damage / bolt interface)" % [
        "READY" if player.dash_remaining <= 0.00001 else "%.1fs" % player.dash_remaining, shots]
    panel.visible = state != State.PLAYING
    var title := "PAUSED — Esc to resume"
    if state in [State.WON, State.LOST]:
        title = ("WON" if state == State.WON else "LOST") + " — R to restart"
    message.text = title + "\n\nWASD: move    Mouse: ground aim\nLeft mouse: fire    Space: dash (2s cooldown)\nEsc: pause/resume    R: restart after win/loss\nRelease and re-press controls after resume/restart."
