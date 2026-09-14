extends Node3D
## Call burst/clear from normal fixed-step logic, not a physics query flush callback.
## The owner removes its intact mesh/collider BEFORE calling burst in the same tick.
signal burst_started(id: int, position: Vector3)
signal impact(position: Vector3, speed: float, material: StringName, body_id: int)
signal fragment_retired(body_id: int, reason: String, age: float, was_sleeping: bool)
const Block = preload("res://debris_block.gd")
const CAP := 192
const TTL := 8.0
const FADE_START := 7.0
const SIDE := 0.34
var bodies: Array[RigidBody3D] = []
var next_event := 1
var next_body := 1
var tick := 0
var last_impact_tick := -100
var batch: MultiMeshInstance3D
var batch_dirty := true

func _ready() -> void:
    # One render batch, still one independent rigid body + shape for EVERY cube.
    batch = MultiMeshInstance3D.new()
    var multi := MultiMesh.new()
    multi.transform_format = MultiMesh.TRANSFORM_3D
    multi.use_colors = true
    var mesh := BoxMesh.new()
    mesh.size = Vector3.ONE * SIDE
    multi.mesh = mesh
    multi.instance_count = CAP
    multi.visible_instance_count = 0
    batch.multimesh = multi
    var material := ShaderMaterial.new()
    material.shader = preload("res://debris_surface.gdshader")
    material.set_shader_parameter("instance_colors", true)
    batch.material_override = material
    add_child(batch)

func _process(_dt: float) -> void:
    batch.multimesh.visible_instance_count = bodies.size()
    var inverse := global_transform.affine_inverse()
    for i in bodies.size():
        var body = bodies[i]
        # Always copy the final engine pose, including the frame it falls asleep.
        var pose: Transform3D = inverse * body.global_transform
        pose.basis = pose.basis.scaled(Vector3.ONE * body.visual_scale)
        batch.multimesh.set_instance_transform(i, pose)
        if batch_dirty:
            batch.multimesh.set_instance_color(i, body.color)
    batch_dirty = false

func burst(at: Transform3D, kind: StringName, event_seed: int) -> int:
    if kind not in [&"pylon", &"sentinel"]:
        push_error("Unknown destruction kind: " + str(kind))
        return -1
    var count := 32 if kind == &"pylon" else 16
    while bodies.size() + count > CAP:
        var victim: RigidBody3D = bodies[0]
        for candidate in bodies:
            if candidate.sleeping:
                victim = candidate
                break
        retire(victim, "cap")
    var id := next_event
    next_event += 1
    var rng := RandomNumberGenerator.new()
    rng.seed = event_seed
    # Ignore actor scale/shear so every collision box remains exactly 0.34m.
    var rotation_basis := at.basis.orthonormalized()
    for i in count:
        var body := Block.new()
        body.body_id = next_body
        next_body += 1
        body.event_id = id
        body.mass = 0.3
        body.linear_damp_mode = RigidBody3D.DAMP_MODE_REPLACE
        body.angular_damp_mode = RigidBody3D.DAMP_MODE_REPLACE
        body.linear_damp = 0.12
        body.angular_damp = 0.18
        body.continuous_cd = true
        body.contact_monitor = true
        body.max_contacts_reported = 8
        body.collision_layer = 2
        body.collision_mask = 1
        var material := PhysicsMaterial.new()
        material.friction = 0.65
        material.bounce = 0.42
        body.physics_material_override = material
        var shape := BoxShape3D.new()
        shape.size = Vector3.ONE * SIDE
        var collision := CollisionShape3D.new()
        collision.shape = shape
        body.add_child(collision)
        body.color = Color.from_hsv(0.065 + rng.randf() * 0.065, 0.78, 0.98)
        add_child(body)
        # Nonoverlapping 4x4x2 grid; caller transform is ground-level target base.
        var offset := Vector3((i % 4 - 1.5) * 0.36, 0.25 + (i / 16) * 0.36,
            ((i / 4) % 4 - 1.5) * 0.36)
        body.global_transform = Transform3D(rotation_basis, at.origin + rotation_basis * offset)
        body.linear_velocity = Vector3(rng.randf_range(-3.5, 3.5),
            rng.randf_range(4.5, 7.5), rng.randf_range(-3.5, 3.5))
        body.angular_velocity = Vector3(rng.randf_range(-12, 12),
            rng.randf_range(-12, 12), rng.randf_range(-12, 12))
        body.previous_velocity = body.linear_velocity
        body.previous_spin = body.angular_velocity
        bodies.append(body)
    batch_dirty = true
    burst_started.emit(id, at.origin)
    return id

func retire(body: RigidBody3D, reason: String) -> void:
    var id: int = body.body_id
    var age: float = body.age
    var asleep := body.sleeping
    bodies.erase(body)
    batch_dirty = true
    remove_child(body)
    body.free() # Removes physics RID now, not one frame after the cap was exceeded.
    fragment_retired.emit(id, reason, age, asleep)

func clear() -> void:
    for body in bodies.duplicate():
        retire(body, "restart")
    last_impact_tick = -100
    if is_instance_valid(batch):
        batch.multimesh.visible_instance_count = 0

func _physics_process(dt: float) -> void:
    tick += 1
    for body in bodies.duplicate():
        body.age += dt
        if body.age >= TTL:
            retire(body, "ttl")
            continue
        # Shrink only the mesh; NEVER scale the physics body or steer its motion.
        body.visual_scale = clampf((TTL - body.age) / (TTL - FADE_START), 0.001, 1.0)
        if body.pending_speed >= 1.0 and body.age - body.last_impact_age >= 0.12 and tick - last_impact_tick >= 3:
            last_impact_tick = tick
            body.last_impact_age = body.age
            impact.emit(body.pending_position, body.pending_speed, &"metal", body.body_id)
        body.pending_speed = 0.0
