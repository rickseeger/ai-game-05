extends "res://controls_session.gd"
## Complete production session. Resolve only AFTER movement and combat damage.
signal objectives_changed(remaining: int)
const REQUIRED_PYLONS := 3
const DEADLINE := 150.0
const EXTRACTION_RADIUS := 1.5
var destroyed_pylons: Dictionary = {}
var _clock_error := 0.0
var loss_reason := ""
const Destruction = preload("res://destruction.gd")
const Target = preload("res://destructible_target.gd")
const Combat = preload("res://combat.gd")
const Opposition = preload("res://opposition.gd")
const Sound = preload("res://sound.gd")
var sound: Node3D
var debris: Node3D
var combat: Node3D
var opposition: Node3D
var targets: Array[Node3D] = []
var hud_panel: PanelContainer

func _ready() -> void:
    super._ready()
    # Player/sentries/manager: 0; Combat swept damage: 10; resolution: 20.
    process_physics_priority = 20
    debris = Destruction.new()
    add_child(debris)
    sound = Sound.new()
    add_child(sound)
    sound.bind(debris)
    sound.gameplay_input = controls
    combat = Combat.new()
    add_child(combat)
    opposition = Opposition.new()
    opposition.arena = arena
    opposition.combat = combat
    opposition.destruction = debris
    add_child(opposition)
    build_session_hud()
    rebuild_combat()
    refresh_hud()
    if "--integration-test" in OS.get_cmdline_user_args():
        var tests = load("res://tests/integration_tests.gd").new()
        add_child(tests)
        tests.call_deferred("run", self)
    if "--opposition-test" in OS.get_cmdline_user_args():
        var tests = load("res://tests/opposition_tests.gd").new()
        add_child(tests)
        tests.call_deferred("run", self)

func rebuild_combat() -> void:
    destroyed_pylons.clear()
    _clock_error = 0.0
    loss_reason = ""
    combat.clear()
    opposition.clear()
    sound.clear()
    debris.clear()
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
        target.destroyed.connect(on_target_destroyed)
    player.add_to_group("player")
    # Do not finish from died: all bolts in this physics tick must resolve first.
    opposition.player = player
    opposition.start(run_seed)
    arena.set_extraction_open(false)
    refresh_hud()
    objectives_changed.emit(remaining_pylons())

func rebuild_run() -> void:
    # Full-session retry clears aim; leave accepted isolated controls unchanged.
    controls.pointer = Vector2.ZERO
    controls.pointer_known = false
    if is_instance_valid(opposition):
        rebuild_combat()

func on_fired(origin: Vector3, direction: Vector3) -> void:
    super.on_fired(origin, direction)
    if is_instance_valid(combat):
        combat.spawn_bolt(player, origin, direction, player.BOLT_DAMAGE)

func build_session_hud() -> void:
    # Reuse the inherited labels and terminal panel; no second HUD state model.
    var style := StyleBoxFlat.new()
    style.bg_color = Color("09131eee")
    for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
        style.set_content_margin(side, 10)
    hud_panel = PanelContainer.new()
    hud.get_parent().add_child(hud_panel)
    hud.reparent(hud_panel)
    hud_panel.add_theme_stylebox_override("panel", style)
    hud_panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
    hud_panel.offset_left = 12
    hud_panel.offset_right = -12
    hud_panel.offset_top = 10
    hud_panel.offset_bottom = 118
    hud_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    hud.add_theme_color_override("font_color", Color("e1f5ff"))
    hud.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
    panel.add_theme_stylebox_override("panel", style)
    panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
    panel.offset_left = -330
    panel.offset_right = 330
    panel.offset_top = -125
    panel.offset_bottom = 125
    panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    message.mouse_filter = Control.MOUSE_FILTER_IGNORE
    message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    message.add_theme_color_override("font_color", Color("e1f5ff"))

func refresh_hud() -> void:
    if not is_instance_valid(player):
        return
    var seconds_left := ceili(maxf(0.0, DEADLINE - elapsed))
    var clock := "%d:%02d" % [seconds_left / 60, seconds_left % 60]
    var extraction := "OPEN - reach the north pad" if extraction_unlocked() else "LOCKED - destroy all pylons"
    hud.text = "BREAKWATER | Destroy THREE pylons, then reach EXTRACT alive before time runs out.\nPylons: %d / 3 destroyed | Extraction: %s\nTime: %s | Health: %d / 100 | Dash: %s | Sentries: %d\nWASD move | Mouse aim | Hold LMB fire | Space dash | Esc pause | M mute" % [
        destroyed_pylons.size(), extraction, clock, player.health,
        "READY" if player.dash_remaining <= 0.00001 else "%.1fs" % player.dash_remaining,
        opposition.sentries.size() if is_instance_valid(opposition) else 0]
    panel.visible = state != State.PLAYING
    var title := "PAUSED - Esc to resume"
    if state == State.WON:
        title = "VICTORY - extracted alive!\nR to retry"
    elif state == State.LOST:
        title = "DEFEAT - " + ("time ran out" if loss_reason == "timeout" else "health depleted") + "\nR to retry"
    message.text = title + "\n\nDestroy three pylons, then enter the north EXTRACT pad.\nWASD move | Mouse aim | Hold LMB fire\nSpace dash (2s cooldown) | Esc pause/resume\nRelease and re-press controls after resume/retry."

func remaining_pylons() -> int:
    return maxi(0, REQUIRED_PYLONS - destroyed_pylons.size())

func extraction_unlocked() -> bool:
    return remaining_pylons() == 0

func on_target_destroyed(id: int, _at: Transform3D, kind: StringName, _seed: int) -> void:
    if state != State.PLAYING or kind != &"pylon" or destroyed_pylons.has(id):
        return
    # Accept only an actual destroyed target in THIS run, not enemy deaths or
    # unknown/stale IDs. Repeated deliveries cannot advance progress or re-emit.
    for target in targets:
        if target.entity_id == id and target.is_destroyed:
            destroyed_pylons[id] = true
            arena.set_extraction_open(extraction_unlocked())
            refresh_hud()
            objectives_changed.emit(remaining_pylons())
            return

func in_extraction() -> bool:
    var center: Vector3 = (arena.global_transform * arena.exit_transform).origin
    # Ground-plane radius matches the existing arena ring and grounded pawn.
    var offset := Vector2(player.global_position.x - center.x, player.global_position.z - center.z)
    return offset.length_squared() <= EXTRACTION_RADIUS * EXTRACTION_RADIUS

func resolve_tick() -> void:
    if state != State.PLAYING:
        return
    # Loss-before-win, including final pylon + exit + lethal hit on the same tick.
    if player.health <= 0:
        loss_reason = "death"
        finish(State.LOST)
    elif elapsed >= DEADLINE:
        loss_reason = "timeout"
        finish(State.LOST)
    elif extraction_unlocked() and in_extraction():
        finish(State.WON)

func _physics_process(dt: float) -> void:
    if state == State.PLAYING:
        # Compensated sum: 9000 ordinary 60Hz steps reach exactly 150 seconds,
        # without an epsilon that could lose a run before its actual deadline.
        var increment := dt - _clock_error
        var next := elapsed + increment
        _clock_error = (next - elapsed) - increment
        elapsed = next
        resolve_tick()
    refresh_hud()
