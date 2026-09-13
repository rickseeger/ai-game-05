extends Node3D
## World only. Spawn values are local to Arena; use to_global for translated arenas.
## The bounded layout is intentionally seed-invariant. Pylons/actors belong to callers.
const HALF_EXTENT := 12.0
const WORLD_LAYER := 1
var player_spawn := Transform3D(Basis.IDENTITY, Vector3(0, 0, 10))
var pylon_spawns: Array[Transform3D] = []
var enemy_spawn_points: Array[Vector3] = []
var exit_transform := Transform3D(Basis.IDENTITY, Vector3(0, 0, -10))
var ground: StaticBody3D
var geometry: Node3D

func _ready() -> void:
    build(1201)

func build(_seed: int = 1201) -> Dictionary:
    # Idempotent rebuild: no deferred colliders left behind during a restart.
    if is_instance_valid(geometry):
        remove_child(geometry)
        geometry.free()
    geometry = Node3D.new()
    geometry.name = "WorldGeometry"
    add_child(geometry)
    pylon_spawns.assign([
        Transform3D(Basis.IDENTITY, Vector3(-8, 0, -7)),
        Transform3D(Basis.IDENTITY, Vector3(8, 0, -6)),
        Transform3D(Basis.IDENTITY, Vector3(0, 0, 6))])
    enemy_spawn_points.assign([Vector3(-10, 0, -10), Vector3(10, 0, -10),
        Vector3(-10, 0, 10), Vector3(10, 0, 10),
        Vector3(-10, 0, 0), Vector3(10, 0, 0)])
    ground = solid_box("Ground", Vector3(24, 0.5, 24), Vector3(0, -0.25, 0), Color("354b56"))
    # Inner wall faces are precisely +/-12m; floor playable surface is y=0.
    solid_box("WestWall", Vector3(0.5, 0.75, 25), Vector3(-12.25, 0.375, 0), Color("657782"))
    solid_box("EastWall", Vector3(0.5, 0.75, 25), Vector3(12.25, 0.375, 0), Color("657782"))
    solid_box("NorthWall", Vector3(24, 0.75, 0.5), Vector3(0, 0.375, -12.25), Color("657782"))
    solid_box("SouthWall", Vector3(24, 0.75, 0.5), Vector3(0, 0.375, 12.25), Color("657782"))
    solid_box("CoverWest", Vector3(3, 1.2, 1), Vector3(-4, 0.6, 2), Color("8a9695"))
    solid_box("CoverEast", Vector3(1, 1.2, 3), Vector3(4, 0.6, 0), Color("8a9695"))
    solid_box("CoverNorth", Vector3(3, 1.2, 1), Vector3(0, 0.6, -4), Color("8a9695"))
    for i in range(-10, 12, 2):
        box(geometry, Vector3(0.025, 0.012, 24), Vector3(i, 0.012, 0), Color("49626a"))
        box(geometry, Vector3(24, 0.012, 0.025), Vector3(0, 0.012, i), Color("49626a"))
    for i in pylon_spawns.size():
        var p := pylon_spawns[i].origin
        ring(geometry, p + Vector3.UP * 0.025, 1.35, Color("eeb358"))
        label(geometry, "P%d" % (i + 1), p + Vector3(2.0, 0.15, 0), Color("ffd88b"))
    ring(geometry, exit_transform.origin + Vector3.UP * 0.025, 1.5, Color("55e0b5"))
    box(geometry, Vector3(1.6, 0.025, 0.18), Vector3(0, 0.03, -10), Color("55e0b5"))
    box(geometry, Vector3(0.18, 0.025, 1.6), Vector3(0, 0.03, -10), Color("55e0b5"))
    label(geometry, "EXTRACT", Vector3(-3.6, 0.15, -10), Color("86ffe0"))
    return {"player_spawn": player_spawn, "pylon_spawns": pylon_spawns.duplicate(),
        "enemy_spawn_points": enemy_spawn_points.duplicate(), "exit_transform": exit_transform}

func solid_box(id: String, size: Vector3, at: Vector3, color: Color) -> StaticBody3D:
    var body := StaticBody3D.new()
    body.name = id
    body.collision_layer = WORLD_LAYER
    body.collision_mask = 0
    geometry.add_child(body)
    body.position = at
    var shape := BoxShape3D.new()
    shape.size = size
    var collider := CollisionShape3D.new()
    collider.shape = shape
    body.add_child(collider)
    box(body, size, Vector3.ZERO, color)
    return body

static func material(color: Color, unshaded: bool = false) -> StandardMaterial3D:
    var m := StandardMaterial3D.new()
    m.albedo_color = color
    m.roughness = 0.86
    if unshaded:
        m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    return m

static func box(parent: Node3D, size: Vector3, at: Vector3, color: Color) -> MeshInstance3D:
    var instance := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = size
    instance.mesh = mesh
    instance.material_override = material(color)
    parent.add_child(instance)
    instance.position = at
    return instance

static func ring(parent: Node3D, at: Vector3, radius: float, color: Color) -> void:
    # Keep every marker and its exact geometry/material; batch only submission.
    # Hundreds of tiny separate draws dominate this scene on software OpenGL.
    var mesh := BoxMesh.new()
    mesh.size = Vector3(0.11, 0.02, radius * 0.16)
    var multi := MultiMesh.new()
    multi.transform_format = MultiMesh.TRANSFORM_3D
    multi.mesh = mesh
    multi.instance_count = 40
    for i in 40:
        var angle := TAU * float(i) / 40.0
        multi.set_instance_transform(i, Transform3D(Basis(Vector3.UP, -angle),
            at + Vector3(cos(angle), 0, sin(angle)) * radius))
    var markers := MultiMeshInstance3D.new()
    markers.multimesh = multi
    markers.material_override = material(color, true)
    markers.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    parent.add_child(markers)

static func label(parent: Node3D, text: String, at: Vector3, color: Color) -> void:
    var node := Label3D.new()
    node.text = text
    node.font_size = 48
    node.pixel_size = 0.012
    node.modulate = color
    node.outline_size = 8
    parent.add_child(node)
    node.position = at
    node.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    # Upright text is a location label, not painted floor geometry. Keep depth tests.
    node.pixel_size = 0.016

static func actor_contact(parent: Node3D, radius: float) -> void:
    var pad := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius
    mesh.height = 0.012
    mesh.radial_segments = 32
    pad.mesh = mesh
    pad.material_override = material(Color("102632"), true)
    pad.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    parent.add_child(pad)
    pad.position.y = 0.014
    ring(parent, Vector3.UP * 0.035, radius, Color("79e5fa"))
