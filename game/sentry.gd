extends CharacterBody3D
## One sentry type. Locked, visible aim gives dodge/counterfire a real window.
signal destroyed(id: int, at: Transform3D, kind: StringName, event_seed: int)
signal event(kind: String, data: Dictionary)
const Arena = preload("res://arena.gd")
const SPEED := 3.0
const RANGE := 6.0
const AIM_TIME := 0.6
const CYCLE := 1.8
var entity_id := 100
var event_seed := 1201
var health := 50
var is_destroyed := false
var destruction: Node3D
var combat: Node3D
var player: CharacterBody3D
var intact: Node3D
var collider: CollisionShape3D
var beam: MeshInstance3D
var aiming := false
var aim_left := 0.0
var cooldown := 0.0
var locked_direction := Vector3.FORWARD
var avoid_side := 1.0

func _ready() -> void:
    collision_layer = 4
    collision_mask = 1
    safe_margin = 0.001
    collider = CollisionShape3D.new()
    var shape := CylinderShape3D.new()
    shape.radius = 0.45
    shape.height = 0.9
    collider.shape = shape
    collider.position.y = 0.45
    add_child(collider)
    intact = Node3D.new()
    add_child(intact)
    Arena.box(intact, Vector3(0.8, 0.7, 0.8), Vector3.UP * 0.45, Color("df633b"))
    Arena.box(intact, Vector3(0.2, 0.2, 0.7), Vector3(0, 0.65, -0.5), Color("ffb970"))
    beam = Arena.box(intact, Vector3(0.065, 0.035, RANGE), Vector3(0, 0.65, -RANGE/2), Color("ff2929"))
    beam.material_override = Arena.material(Color("ff2929"), true)
    beam.visible = false

func _physics_process(dt: float) -> void:
    if is_instance_valid(player) and player.health > 0:
        fixed_step(dt, player.global_position)

func clear_sight(player_position: Vector3) -> bool:
    var from := global_position + Vector3.UP * 0.65
    var to := player_position + Vector3.UP * 0.65
    return get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(from, to, 1)).is_empty()

func fixed_step(dt: float, player_position: Vector3) -> void:
    if is_destroyed:
        return
    cooldown = maxf(0, cooldown - dt)
    var delta := player_position - global_position
    delta.y = 0
    if aiming:
        velocity = Vector3.ZERO
        aim_left = maxf(0, aim_left - dt)
        if aim_left <= 0.00001:
            aiming = false
            beam.visible = false
            cooldown = CYCLE - AIM_TIME
            combat.spawn_bolt(self, global_position + Vector3.UP * 0.65, locked_direction, 15)
            event.emit("attack", {"entity": entity_id, "position": combat.vec(global_position)})
        return
    if delta.length() <= RANGE + 0.02 and clear_sight(player_position):
        velocity = Vector3.ZERO
        if cooldown <= 0.00001 and delta.length_squared() > 0.001:
            aiming = true
            aim_left = AIM_TIME
            locked_direction = delta.normalized()
            intact.rotation.y = atan2(-locked_direction.x, -locked_direction.z)
            beam.visible = true
            event.emit("aim", {"entity": entity_id, "position": combat.vec(global_position), "target": combat.vec(player_position)})
        return
    # Sweep a lookahead at actor height. Tangential candidates route around static
    # covers; stable side selection avoids left/right oscillation at a face.
    var direction := delta.normalized()
    if test_move(global_transform, direction * 0.9):
        var found := false
        for angle in [45.0, 90.0, 135.0]:
            var candidate := direction.rotated(Vector3.UP, deg_to_rad(angle * avoid_side))
            if not test_move(global_transform, candidate * 0.9):
                direction = candidate
                found = true
                break
        if not found:
            avoid_side *= -1
            direction = direction.rotated(Vector3.UP, PI * 0.5 * avoid_side)
    intact.rotation.y = atan2(-direction.x, -direction.z)
    velocity = direction * SPEED
    velocity.y = -1
    move_and_slide()

func apply_damage(amount: int, _hit_position: Vector3, _impulse_direction: Vector3) -> void:
    if is_destroyed or amount <= 0:
        return
    health = maxi(0, health - amount)
    event.emit("sentry_damage", {"entity": entity_id, "health": health, "amount": amount})
    if health > 0:
        return
    is_destroyed = true
    aiming = false
    collision_layer = 0
    remove_child(collider)
    collider.free()
    remove_child(intact)
    intact.free()
    # Gameplay shape AND intact rendering are gone before the sole burst call.
    destruction.burst(global_transform, &"sentinel", event_seed)
    destroyed.emit(entity_id, global_transform, &"sentinel", event_seed)
