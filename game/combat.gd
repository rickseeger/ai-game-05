extends Node3D
## All hits are swept queries on the normal physics step, not query-flush signals.
signal event(kind: String, data: Dictionary)
const Arena = preload("res://arena.gd")
const PLAYER_SPEED := 24.0
const ENEMY_SPEED := 8.0
const ENEMY_DAMAGE := 15
const TTL := 4.0
var bolts: Array[Dictionary] = []
var next_id := 1

func _ready() -> void:
    process_physics_priority = 10

func spawn_bolt(shooter: CollisionObject3D, origin: Vector3, direction: Vector3, damage: int) -> int:
    if not is_instance_valid(shooter) or direction.length_squared() < 0.001 or damage <= 0:
        return -1
    var friendly := shooter.is_in_group("player")
    var visual := Node3D.new()
    add_child(visual)
    var mesh := Arena.box(visual, Vector3(0.17, 0.17, 0.48), Vector3.ZERO,
        Color("8cffff") if friendly else Color("ff542b"))
    mesh.material_override = Arena.material(Color("8cffff") if friendly else Color("ff542b"), true)
    visual.global_position = origin
    visual.rotation.y = atan2(-direction.x, -direction.z)
    var id := next_id
    next_id += 1
    bolts.append({"id": id, "friendly": friendly, "shooter": shooter.get_rid(),
        "source": shooter.global_position, "p": origin, "direction": direction.normalized(),
        "damage": damage, "speed": PLAYER_SPEED if friendly else ENEMY_SPEED, "age": 0.0, "visual": visual})
    event.emit("bolt", {"id": id, "friendly": friendly, "damage": damage,
        "speed": PLAYER_SPEED if friendly else ENEMY_SPEED, "position": vec(origin), "direction": vec(direction)})
    return id

static func vec(v: Vector3) -> Array:
    return [v.x, v.y, v.z]

func clear() -> void:
    for bolt in bolts:
        bolt.visual.free()
    bolts.clear()

func _physics_process(dt: float) -> void:
    for bolt in bolts.duplicate():
        # Honor externally paused fixtures; production Session resolves terminal
        # outcomes at priority 20, after this entire priority-10 damage pass.
        if get_tree().paused:
            break
        var end: Vector3 = bolt.p + bolt.direction * bolt.speed * dt
        var query := PhysicsRayQueryParameters3D.create(bolt.p, end, 1 | 4, [bolt.shooter])
        var hit := get_world_3d().direct_space_state.intersect_ray(query)
        if not hit.is_empty():
            var target: Node = hit.collider
            while target != null and not target.has_method("apply_damage"):
                target = target.get_parent()
            var can_damage: bool = target != null and ((bolt.friendly and not target.is_in_group("player")) or (not bolt.friendly and target.is_in_group("player")))
            var target_id: int = target.entity_id if target != null and "entity_id" in target else 0
            event.emit("hit", {"id": bolt.id, "friendly": bolt.friendly, "damage": bolt.damage if can_damage else 0,
                "target": target_id, "collider": str(hit.collider.name), "position": vec(hit.position)})
            if can_damage:
                target.apply_damage(bolt.damage, bolt.source if not bolt.friendly else hit.position, bolt.direction)
            remove_bolt(bolt)
            continue
        bolt.p = end
        bolt.visual.global_position = end
        bolt.age += dt
        if bolt.age >= TTL:
            event.emit("expired", {"id": bolt.id})
            remove_bolt(bolt)

func remove_bolt(bolt: Dictionary) -> void:
    bolts.erase(bolt)
    bolt.visual.free()
