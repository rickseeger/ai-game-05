extends "res://controls_session.gd"
## Threat integration slice. Session remains the sole terminal-state owner.
## Pylon objectives/exit/countdown/audio/balance remain with their existing nodes.
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
    player.add_to_group("player")
    player.died.connect(func(): finish(State.LOST))
    opposition.player = player
    opposition.start(run_seed)

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
    hud.text = "BREAKWATER / OPPOSITION SLICE — objectives pending | destruction audio enabled\nWASD move | Mouse aim | Hold LMB fire | Space dash | Esc pause\nHealth: %d / 100   Dash: %s   Sentries: %d\nRed line: locked aim (0.6s) | Red bolt: 15 damage | Sentry: two hits" % [
        player.health, "READY" if player.dash_remaining <= 0.00001 else "%.1fs" % player.dash_remaining,
        opposition.sentries.size() if is_instance_valid(opposition) else 0]
