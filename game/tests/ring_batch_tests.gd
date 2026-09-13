extends SceneTree
# Regression for drawing-only batching: reconstruct the pre-change ring as oracle.
# Pixel agreement is not a perceptual-quality assessment.
const Arena = preload("res://arena.gd")
var checks: Array[Dictionary] = []
var comparisons: Array[Dictionary] = []
var out := OS.get_environment("RING_TEST_OUT")

func _initialize() -> void:
    call_deferred("run")

func check(name_value: String, ok: bool) -> void:
    checks.append({"name": name_value, "pass": ok})
    if not ok:
        push_error("RING_ASSERT " + name_value)

func capture(parent: Node3D, other: Node3D, filename: String) -> Image:
    parent.visible = true
    other.visible = false
    await process_frame
    await process_frame
    await RenderingServer.frame_post_draw
    var image := root.get_texture().get_image()
    check("save_" + filename, image.save_png(out.path_join(filename)) == OK)
    return image

func run() -> void:
    check("rendered_x11", DisplayServer.get_name() == "X11")
    var world := Node3D.new()
    root.add_child(world)
    var camera := Camera3D.new()
    world.add_child(camera)
    camera.position = Vector3(0, 5, 6)
    camera.look_at(Vector3.ZERO)
    camera.current = true
    for radius in [0.28, 0.48, 1.35, 1.5]:
        var old := Node3D.new()
        var batched := Node3D.new()
        world.add_child(old)
        world.add_child(batched)
        var at := Vector3(0.2, 0.035, -0.1)
        var color := Color("eeb358")
        for i in 40:
            var angle := TAU * float(i) / 40.0
            var marker := Arena.box(old, Vector3(0.11, 0.02, radius * 0.16),
                at + Vector3(cos(angle), 0, sin(angle)) * radius, color)
            marker.rotation.y = -angle
            marker.material_override = Arena.material(color, true)
            marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
        Arena.ring(batched, at, radius, color)
        check("one_batch_%s" % radius, batched.get_child_count() == 1 and batched.get_child(0) is MultiMeshInstance3D)
        var batch: MultiMeshInstance3D = batched.get_child(0)
        check("all_40_%s" % radius, batch.multimesh.instance_count == 40 and batch.multimesh.visible_instance_count == -1)
        check("same_material_%s" % radius, batch.material_override.albedo_color == color and
            batch.material_override.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED and
            is_equal_approx(batch.material_override.roughness, 0.86) and
            batch.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
        # Nontrivial inherited transform also covers moving player/reticle parents.
        old.transform = Transform3D(Basis.from_euler(Vector3(0.1, 0.37, -0.05)).scaled(Vector3(1.1, 0.9, 1.2)), Vector3(-0.2, 0.1, 0.2))
        batched.transform = old.transform
        for i in 40:
            var marker: MeshInstance3D = old.get_child(i)
            check("pose_%s_%d" % [radius, i], (batch.global_transform * batch.multimesh.get_instance_transform(i)).is_equal_approx(marker.global_transform))
            check("geometry_%s_%d" % [radius, i], batch.multimesh.mesh.size == marker.mesh.size and
                batch.multimesh.mesh.get_faces() == marker.mesh.get_faces())
        var a := await capture(old, batched, "original_%s.png" % radius)
        var b := await capture(batched, old, "batched_%s.png" % radius)
        var ad := a.get_data()
        var bd := b.get_data()
        var changed := 0
        var max_delta := 0
        for i in ad.size():
            var delta := absi(int(ad[i]) - int(bd[i]))
            changed += int(delta > 0)
            max_delta = maxi(max_delta, delta)
        comparisons.append({"radius": radius, "bytes": ad.size(), "changed_bytes": changed, "max_channel_delta": max_delta})
        check("pixel_equivalence_%s" % radius, changed <= ad.size() * 0.001 and max_delta <= 3)
        batched.visible = false
        check("parent_visibility_%s" % radius, not batch.is_visible_in_tree())
        old.free()
        batched.free()
    var passed := true
    for item in checks:
        passed = passed and item["pass"]
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify({
        "passed": passed, "checks": checks, "comparisons": comparisons,
        "renderer": RenderingServer.get_video_adapter_name(), "visual_assessment": "UNASSESSED"}, "  "))
    print("RING_TEST_DONE checks=", checks.size(), " passed=", passed)
    quit(0 if passed else 1)
