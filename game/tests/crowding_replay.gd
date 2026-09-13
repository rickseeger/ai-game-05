extends SceneTree
## Replays the original crowded states; never moves cubes apart to improve a result.
var scene: Node3D
var records: Array[Dictionary] = []
var checks: Array[String] = []
func check(ok: bool, id: String) -> void:
    assert(ok, id)
    checks.append(id)
func _initialize() -> void:
    run.call_deferred()
func run() -> void:
    scene = load("res://arena_preview.tscn").instantiate()
    root.add_child(scene)
    scene.tour = false
    scene.testing = true
    await process_frame
    var out := OS.get_environment("ARENA_OUT")
    var input = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CROWDING_CASES")))
    var locked: Transform3D = scene.camera.global_transform
    if "--verify-presentation" in OS.get_cmdline_user_args():
        check(scene.debris.size() == 7, "same_seven_crowded_cubes")
        for i in scene.debris.size():
            var cube: MeshInstance3D = scene.debris[i]
            check(cube.mesh is BoxMesh and cube.mesh.size.is_equal_approx(Vector3.ONE * 0.34), "same_cube_geometry_%d" % i)
            check(cube.material_override is ShaderMaterial and cube.material_override.shader == load("res://debris_surface.gdshader"), "production_debris_surface_%d" % i)
        var pad: MeshInstance3D = scene.contact.get_child(0)
        check(pad.mesh is CylinderMesh and is_equal_approx(pad.position.y - pad.mesh.height / 2.0, 0.008), "contact_pad_at_ground_not_actor_height")
        check(pad.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "contact_pad_no_false_shadow")
        var ring: MultiMeshInstance3D = scene.contact.get_child(1)
        check(ring.multimesh.instance_count == 40, "contact_ring_still_batched_forty_markers")
        var labels := scene.arena.geometry.find_children("*", "Label3D", true, false)
        check(labels.size() == 4, "four_location_labels")
        for label in labels:
            check(label.billboard == BaseMaterial3D.BILLBOARD_ENABLED and not label.no_depth_test, "world_depth_tested_billboard_" + label.text)
        check(scene.camera.projection == Camera3D.PROJECTION_PERSPECTIVE, "perspective_unchanged")
        check(DisplayServer.get_name() != "headless", "actual_renderer")
    for case in input:
        for step in 25:
            var dt := float(step - 12) / 60.0
            var at := Vector3.ZERO
            var height := 0.0
            if case.has("elapsed"):
                var t := maxf(0, float(case.elapsed) + dt)
                var index: int = int(t / 2.0) % scene.fixtures.size()
                var blend := smoothstep(0.0, 1.0, fmod(t, 2.0) / 2.0)
                at = scene.fixtures[index].lerp(scene.fixtures[(index + 1) % scene.fixtures.size()], blend)
                height = 0.3 + sin(fmod(t, 2.0) / 2.0 * PI) * 7.7
            else:
                at = Vector3(case.x, 0, case.z)
                height = case.height + dt
            scene.set_fixture(at, height)
            await process_frame
            await RenderingServer.frame_post_draw
            check(scene.camera.global_transform.is_equal_approx(locked), "%s_camera_locked_%d" % [case.id, step])
            if step % 6 == 0:
                var filename: String = "%s_%02d.png" % [case.id, step]
                assert(root.get_texture().get_image().save_png(out.path_join(filename)) == OK)
                var cubes: Array = []
                for cube in scene.debris:
                    cubes.append({"position": [cube.position.x, cube.position.y, cube.position.z],
                        "rotation": [cube.rotation.x, cube.rotation.y, cube.rotation.z]})
                records.append({"case": case.id, "step": step, "offset_seconds": dt,
                    "file": filename, "at": [at.x, at.y, at.z], "height": height, "cubes": cubes,
                    "actor_screen": [scene.camera.unproject_position(at).x, scene.camera.unproject_position(at).y],
                    "cluster_screen": [scene.camera.unproject_position(scene.debris[3].position).x, scene.camera.unproject_position(scene.debris[3].position).y]})
    var file := FileAccess.open(out.path_join("sequence.json"), FileAccess.WRITE)
    file.store_string(JSON.stringify({"records": records, "checks": checks, "viewport": [root.size.x, root.size.y],
        "description": "25 real rendered frames per deterministic 60Hz presentation-clock window; five saved frames; analytic fixtures unchanged, NOT physics or continuous desktop video"}, "  "))
    print("CROWDING_REPLAY_DONE records=", records.size())
    quit(0)
