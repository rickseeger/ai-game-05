extends "res://controls_session.gd"
## Production rules on the accepted opposition slice; default launch/HUD polish
## are separate integration work. Resolve only AFTER movement and combat damage.
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
    player_replaced.connect(func(_player): sound.clear())
    combat = Combat.new()
    add_child(combat)
    opposition = Opposition.new()
    opposition.arena = arena
    opposition.combat = combat
    opposition.destruction = debris
    add_child(opposition)
    rebuild_combat()
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
    objectives_changed.emit(remaining_pylons())

func start(seed_value: int) -> void:
    super.start(seed_value)
    if is_instance_valid(opposition):
        rebuild_combat()

func on_fired(origin: Vector3, direction: Vector3) -> void:
    super.on_fired(origin, direction)
    if is_instance_valid(combat):
        combat.spawn_bolt(player, origin, direction, player.BOLT_DAMAGE)

func refresh_hud() -> void:
    super.refresh_hud()
    hud.text = "BREAKWATER / SESSION RULES SLICE — status UI pending | destruction audio enabled\nWASD move | Mouse aim | Hold LMB fire | Space dash | Esc pause\nHealth: %d / 100   Dash: %s   Sentries: %d\nRed line: locked aim (0.6s) | Red bolt: 15 damage | Sentry: two hits" % [
        player.health, "READY" if player.dash_remaining <= 0.00001 else "%.1fs" % player.dash_remaining,
        opposition.sentries.size() if is_instance_valid(opposition) else 0]

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
