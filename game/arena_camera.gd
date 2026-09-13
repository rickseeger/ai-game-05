extends Camera3D
## Deliberately arena-locked, not a following camera: no edge pan or target lag.
## Fits the entire 26 x 26 x 8m visual envelope at every viewport aspect ratio.
## A target at any boundary or airborne height therefore never shifts the ground.
const FOCUS := Vector3(0, 2, 0)
const VISUAL_HALF := 13.0
const AIRBORNE_CEILING := 8.0
const FRAME_FILL := 0.88
var arena: Node3D

func configure(world: Node3D) -> void:
    arena = world
    projection = Camera3D.PROJECTION_PERSPECTIVE
    keep_aspect = Camera3D.KEEP_HEIGHT
    fov = 52.0
    near = 0.1
    far = 160.0
    current = true
    refit()
    if not get_viewport().size_changed.is_connected(refit):
        get_viewport().size_changed.connect(refit)

func refit() -> void:
    var size := get_viewport().get_visible_rect().size
    if size.y <= 0 or not is_instance_valid(arena):
        return
    var focus: Vector3 = arena.to_global(FOCUS)
    # Slightly shallower than the former 0.9 Z/Y ratio: rendered ID/clean-pass
    # tests show more airborne surface and less cyan overlap. No yaw/follow/zoom.
    var direction: Vector3 = arena.global_basis * Vector3(0, 1, 1.2).normalized()
    global_position = focus + direction
    look_at(focus, arena.global_basis.y)
    var tan_y := tan(deg_to_rad(fov * 0.5)) * FRAME_FILL
    var tan_x := tan_y * size.x / size.y
    var distance := 1.0
    for x in [-VISUAL_HALF, VISUAL_HALF]:
        for y in [0.0, AIRBORNE_CEILING]:
            for z in [-VISUAL_HALF, VISUAL_HALF]:
                var p: Vector3 = global_basis.inverse() * (arena.to_global(Vector3(x, y, z)) - focus)
                distance = maxf(distance, p.z + maxf(absf(p.x) / tan_x, absf(p.y) / tan_y))
    global_position = focus + direction * distance

func ground_aim(screen_position: Vector2) -> Variant:
    # Ground-only intersection: cover and decorative fragments cannot steal aim.
    # A miss returns null, rather than snapping an off-arena pointer to a wall.
    var plane := Plane(arena.global_basis.y.normalized(), arena.global_position)
    var hit: Variant = plane.intersects_ray(project_ray_origin(screen_position), project_ray_normal(screen_position))
    if hit == null:
        return null
    var local: Vector3 = arena.to_local(hit)
    if absf(local.x) > 12.0 or absf(local.z) > 12.0:
        return null
    return hit
