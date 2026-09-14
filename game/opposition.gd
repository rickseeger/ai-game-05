extends Node3D
signal event(kind: String, data: Dictionary)
const Sentry = preload("res://sentry.gd")
const Arena = preload("res://arena.gd")
const CAP := 6
const SPAWN_INTERVAL := 15.0
const WARNING := 1.0
const MIN_DISTANCE := 8.0
var arena: Node3D
var player: CharacterBody3D
var combat: Node3D
var destruction: Node3D
var sentries: Array[CharacterBody3D] = []
var pending: Array[Dictionary] = []
var elapsed := 0.0
var next_spawn := SPAWN_INTERVAL
var next_entity := 100
var rng := RandomNumberGenerator.new()
var run_seed := 1201

func start(seed_value: int) -> void:
    clear()
    run_seed = seed_value
    rng.seed = seed_value
    elapsed = 0.0
    next_spawn = SPAWN_INTERVAL
    next_entity = 100
    warn_spawn()
    warn_spawn()

func clear() -> void:
    for sentry in sentries:
        sentry.free()
    sentries.clear()
    for warning in pending:
        warning.marker.free()
    pending.clear()

func warn_spawn() -> bool:
    if sentries.size() + pending.size() >= CAP:
        return false
    var candidates: Array[Vector3] = []
    for local_point in arena.enemy_spawn_points:
        var point: Vector3 = arena.to_global(local_point)
        if point.distance_to(player.global_position) < MIN_DISTANCE:
            continue
        var occupied := false
        for warning in pending:
            occupied = occupied or point.distance_to(warning.position) < 1.5
        for sentry in sentries:
            occupied = occupied or point.distance_to(sentry.global_position) < 1.5
        if not occupied:
            candidates.append(point)
    if candidates.is_empty():
        return false
    var point := candidates[rng.randi_range(0, candidates.size()-1)]
    var marker := Node3D.new()
    add_child(marker)
    marker.global_position = point
    Arena.ring(marker, Vector3.UP * 0.06, 0.85, Color("ff4a33"))
    Arena.label(marker, "INCOMING", Vector3(0, 0.08, 1.2), Color("ff8877"))
    var id := next_entity
    next_entity += 1
    pending.append({"id": id, "position": point, "left": WARNING, "marker": marker})
    event.emit("spawn_warning", {"entity": id, "position": combat.vec(point), "distance": point.distance_to(player.global_position)})
    return true

func _physics_process(dt: float) -> void:
    elapsed += dt
    for warning in pending.duplicate():
        warning.left -= dt
        warning.marker.scale = Vector3.ONE * (1.0 + 0.12 * sin(warning.left * TAU * 3))
        if warning.left > 0.00001:
            continue
        pending.erase(warning)
        warning.marker.free()
        # Approaching a marker never causes an unfair near-player materialization.
        if warning.position.distance_to(player.global_position) < MIN_DISTANCE:
            event.emit("spawn_cancelled", {"entity": warning.id})
            warn_spawn()
            continue
        var sentry := Sentry.new()
        sentry.entity_id = warning.id
        sentry.event_seed = run_seed + warning.id
        sentry.combat = combat
        sentry.destruction = destruction
        sentry.player = player
        sentry.event.connect(func(kind: String, data: Dictionary): event.emit(kind, data))
        sentry.destroyed.connect(on_destroyed)
        add_child(sentry)
        sentry.global_position = warning.position
        sentries.append(sentry)
        event.emit("spawn", {"entity": sentry.entity_id, "position": combat.vec(sentry.global_position),
            "distance": sentry.global_position.distance_to(player.global_position), "alive": sentries.size()})
    if elapsed + 0.00001 >= next_spawn:
        next_spawn += SPAWN_INTERVAL
        warn_spawn()

func on_destroyed(id: int, _at: Transform3D, _kind: StringName, _seed: int) -> void:
    for sentry in sentries.duplicate():
        if sentry.entity_id == id:
            sentries.erase(sentry)
            sentry.queue_free()
    event.emit("destroyed", {"entity": id, "alive": sentries.size()})
