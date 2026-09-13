extends Node
## Exercises the SAME Arena/Camera nodes as the normal preview, with actual rendering.
var checks: Array[Dictionary] = []
var failures: Array[String] = []
var captures: Array[Dictionary] = []
var out: String
var scene: Node3D

func check(ok: bool, name: String, details: Variant = null) -> void:
    checks.append({"name": name, "pass": ok, "details": details})
    if not ok:
        failures.append(name)
        print("CHECK_FAIL ", name, " ", details)

func vector(v: Vector3) -> Array:
    return [v.x, v.y, v.z]

func run(preview: Node3D) -> void:
    scene = preview
    out = OS.get_environment("ARENA_OUT")
    if out.is_empty() or not DirAccess.dir_exists_absolute(out):
        push_error("ARENA_OUT must be an existing fresh output directory")
        get_tree().quit(2)
        return
    await get_tree().physics_frame
    await get_tree().physics_frame
    var arena = scene.arena
    var camera = scene.camera
    var size := get_viewport().get_visible_rect().size
    check(RenderingServer.get_current_rendering_method() == "gl_compatibility", "compatibility_renderer")
    check(DisplayServer.get_name() != "headless", "rendering_enabled", DisplayServer.get_name())
    check(camera.projection == Camera3D.PROJECTION_PERSPECTIVE, "true_perspective_Camera3D")
    check(ProjectSettings.get_setting("physics/3d/physics_engine") == "GodotPhysics3D", "physics_stack")
    var interface: Dictionary = arena.build(1201)
    await get_tree().physics_frame
    await get_tree().physics_frame
    check(interface.keys().size() == 4, "arena_interface_fields", interface.keys())
    check(arena.pylon_spawns.size() == 3, "three_pylon_locations")
    check(arena.enemy_spawn_points.size() == 6, "six_enemy_spawn_locations")
    var bodies: Array[Node] = arena.find_children("*", "StaticBody3D", true, false)
    check(bodies.size() == 8, "idempotent_world_rebuild_eight_bodies", bodies.size())
    for body in bodies:
        check(body.collision_layer == 1 and body.collision_mask == 0, "world_layer_" + body.name)
    var floor_shape: BoxShape3D = arena.ground.get_child(0).shape
    check(floor_shape.size.is_equal_approx(Vector3(24, 0.5, 24)), "exact_24m_ground")
    var space := scene.get_world_3d().direct_space_state
    for x in [-11.9, 0.0, 11.9]:
        for z in [-11.9, 0.0, 11.9]:
            var hit := ray(space, Vector3(x, 0.15, z), Vector3(x, -1, z))
            check(not hit.is_empty() and absf(hit.position.y) < 0.001 and hit.collider == arena.ground,
                "ground_contact_%s_%s" % [x, z])
    for direction in [Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]:
        var hit := ray(space, direction * 11.0 + Vector3.UP * 0.4, direction * 13.0 + Vector3.UP * 0.4)
        check(not hit.is_empty() and absf(maxf(absf(hit.position.x), absf(hit.position.z)) - 12.0) < 0.001,
            "wall_inner_face_" + str(direction))
    for name in ["CoverWest", "CoverEast", "CoverNorth"]:
        var body: Node3D = arena.geometry.get_node(name)
        var hit := ray(space, body.position + Vector3.UP * 3, body.position)
        check(not hit.is_empty() and hit.collider == body and absf(hit.position.y - 1.2) < 0.001,
            "solid_cover_" + name)
    var spawn_points: Array[Vector3] = [arena.player_spawn.origin, arena.exit_transform.origin]
    spawn_points.append_array(arena.enemy_spawn_points)
    for spawn in arena.pylon_spawns:
        spawn_points.append(spawn.origin)
    for i in spawn_points.size():
        var shape := SphereShape3D.new()
        shape.radius = 0.4
        var query := PhysicsShapeQueryParameters3D.new()
        query.shape = shape
        query.transform.origin = spawn_points[i] + Vector3.UP * 0.5
        query.collision_mask = 1
        check(space.intersect_shape(query).is_empty(), "spawn_clear_%d" % i)
    # Sweeps are direct world collision queries, not a Player movement implementation.
    for direction in [Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]:
        var query := PhysicsShapeQueryParameters3D.new()
        var shape := SphereShape3D.new()
        shape.radius = 0.4
        query.shape = shape
        query.transform.origin = direction * 10.8 + Vector3.UP * 0.5
        query.motion = direction * 3
        query.collision_mask = 1
        var motion := space.cast_motion(query)
        check(motion[0] > 0.0 and motion[0] < 0.5, "swept_world_boundary_" + str(direction), Array(motion))
    var near_width: float = camera.unproject_position(Vector3(0.8, 0.5, 10)).distance_to(camera.unproject_position(Vector3(0, 0.5, 10)))
    var far_width: float = camera.unproject_position(Vector3(0.8, 0.5, -10)).distance_to(camera.unproject_position(Vector3(0, 0.5, -10)))
    check(near_width > far_width * 1.1, "perspective_depth_scale", {"near_px": near_width, "far_px": far_width})
    var camera_start: Transform3D = camera.global_transform
    if "--camera-negative" in OS.get_cmdline_user_args():
        camera.fov = 12.0 # Explicit negative control: the frustum test must reject this.
    var minimum_margin := 1.0
    var minimum_cube_px := 1000.0
    var locations := [Vector3.ZERO, Vector3(-11, 0, 11), Vector3(-11, 0, -11),
        Vector3(11, 0, -11), Vector3(11, 0, 11), Vector3(-11, 0, 0),
        Vector3(11, 0, 0), Vector3(0, 0, -11), Vector3(0, 0, 11)]
    for i in locations.size():
        for height in [0.0, 2.0, 4.0, 8.0]:
            scene.set_fixture(locations[i], height)
            await get_tree().process_frame
            check(camera.global_transform.is_equal_approx(camera_start), "locked_camera_%d_%.0f" % [i, height])
            # Every visual-envelope corner, not just the center of the subject.
            for x in [-12.5, 12.5]:
                for z in [-12.5, 12.5]:
                    var p := Vector3(x, height + 0.2, z)
                    var uv: Vector2 = camera.unproject_position(p) / size
                    var margin := minf(minf(uv.x, 1 - uv.x), minf(uv.y, 1 - uv.y))
                    minimum_margin = minf(minimum_margin, margin)
                    check(not camera.is_position_behind(p) and margin >= 0.045,
                        "frustum_%d_%.0f_%s_%s" % [i, height, x, z], [uv.x, uv.y])
            var p: Vector3 = locations[i] + Vector3.UP * maxf(height, 0.25)
            var cube_px: float = camera.unproject_position(p + Vector3.RIGHT * 0.17).distance_to(camera.unproject_position(p - Vector3.RIGHT * 0.17))
            minimum_cube_px = minf(minimum_cube_px, cube_px)
            check(cube_px >= 4.0, "cube_min_pixels_%d_%.0f" % [i, height], cube_px)
            var ground_screen: Vector2 = camera.unproject_position(locations[i])
            var aimed: Variant = camera.ground_aim(ground_screen)
            check(aimed != null and aimed.distance_to(locations[i]) < 0.002,
                "ground_aim_roundtrip_%d_%.0f" % [i, height])
    check(camera.ground_aim(Vector2.ZERO) == null, "off_arena_aim_is_null")
    var sky: Vector2 = camera.unproject_position(Vector3(0, 8, 0))
    var bottom: Vector2 = camera.unproject_position(Vector3.ZERO)
    check(bottom.y - sky.y > 60.0, "upward_height_screen_separation", bottom.y - sky.y)
    for spawn in spawn_points:
        check(camera.is_position_in_frustum(spawn + Vector3.UP * 0.5), "gameplay_location_in_frustum_" + str(spawn))
    # Actual viewport reads only after draw completion; no generated image substitute.
    var names := ["overview", "southwest", "northwest", "northeast", "southeast", "airborne"]
    for i in names.size():
        var height := 8.0 if i == 5 else 4.0
        scene.set_fixture(scene.fixtures[i], height)
        await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var image := get_viewport().get_texture().get_image()
        var path := out.path_join(names[i] + ".png")
        check(image.save_png(path) == OK, "capture_" + names[i])
        var pixel: Vector2 = camera.unproject_position(scene.debris[0].global_position)
        var gold_pixels := 0
        for x in range(maxi(0, int(pixel.x) - 6), mini(image.get_width(), int(pixel.x) + 7)):
            for y in range(maxi(0, int(pixel.y) - 6), mini(image.get_height(), int(pixel.y) + 7)):
                var color := image.get_pixel(x, y)
                if color.r > 0.4 and color.r > color.g * 1.08 and color.g > color.b * 1.15:
                    gold_pixels += 1
        check(gold_pixels >= 3, "rendered_airborne_gold_pixels_" + names[i], gold_pixels)
        captures.append({"file": names[i] + ".png", "pawn_ground": vector(scene.pawn.position),
            "airborne_height": height, "projected_cube": [pixel.x, pixel.y], "gold_pixels": gold_pixels})
    # Exercise the actual viewport size_changed signal in the same live process.
    var resize_to := Vector2i(960, 720) if size.x > 1000 else Vector2i(1280, 720)
    get_window().size = resize_to
    for frame in 5:
        await get_tree().process_frame
    var resized := get_viewport().get_visible_rect().size
    check(resized.is_equal_approx(Vector2(resize_to)), "live_resize_dimensions", [resized.x, resized.y])
    check(not camera.global_transform.is_equal_approx(camera_start), "live_resize_refits_camera")
    for x in [-12.5, 12.5]:
        for y in [0.0, 8.2]:
            for z in [-12.5, 12.5]:
                var uv: Vector2 = camera.unproject_position(Vector3(x, y, z)) / resized
                check(uv.x > 0.045 and uv.x < 0.955 and uv.y > 0.045 and uv.y < 0.955,
                    "live_resize_frustum_%s_%s_%s" % [x, y, z], [uv.x, uv.y])
    await RenderingServer.frame_post_draw
    check(get_viewport().get_texture().get_image().save_png(out.path_join("resized.png")) == OK, "capture_resized")
    var report := {"passed": failures.is_empty(), "failures": failures, "checks": checks,
        "engine": Engine.get_version_info().string, "renderer": RenderingServer.get_current_rendering_method(),
        "display": DisplayServer.get_name(), "viewport": [size.x, size.y],
        "camera_position": vector(camera_start.origin), "resized_camera_position": vector(camera.global_position),
        "resized_viewport": [resized.x, resized.y], "camera_fov": camera.fov,
        "minimum_frame_margin": minimum_margin, "minimum_cube_pixels": minimum_cube_px,
        "captures": captures, "evidence_mode": "real-time offscreen OpenGL viewport, not MovieWriter or human observation"}
    var file := FileAccess.open(out.path_join("results.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify(report, "  ") + "\n")
    file.close()
    print("ARENA_TEST_DONE checks=", checks.size(), " failures=", failures.size(), " output=", out)
    get_tree().quit(0 if failures.is_empty() else 1)

func ray(space: PhysicsDirectSpaceState3D, start: Vector3, end: Vector3) -> Dictionary:
    return space.intersect_ray(PhysicsRayQueryParameters3D.create(start, end, 1))
