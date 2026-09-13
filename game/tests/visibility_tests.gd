extends SceneTree
# Counterfactual render passes measure actual depth occlusion, not projected bounds.
var scene: Node3D
var out: String
var records: Array = []
var palette: Array[Material] = []
func _initialize() -> void:
    run.call_deferred()
func capture(name: String) -> void:
    await process_frame
    await RenderingServer.frame_post_draw
    assert(root.get_texture().get_image().save_png(out.path_join(name + ".png")) == OK)
func run() -> void:
    out = OS.get_environment("ARENA_OUT")
    scene = load("res://arena_preview.tscn").instantiate()
    root.add_child(scene)
    scene.tour = false
    scene.testing = true
    await process_frame
    assert(DisplayServer.get_name() != "headless")
    assert(scene.camera.projection == Camera3D.PROJECTION_PERSPECTIVE)
    var original: Array[Material] = []
    for i in 7:
        original.append(scene.debris[i].material_override)
        var m := StandardMaterial3D.new()
        m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
        m.albedo_color = Color8((i+1)*32, 0, 255)
        palette.append(m)
    var cases: Array = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("CROWDING_CASES")))
    var locked: Transform3D = scene.camera.global_transform
    for case in cases:
        for step in [0, 6, 12, 18, 24]:
            var dt := float(step - 12) / 60.0
            var at := Vector3.ZERO
            var height := 0.0
            if case.has("elapsed"):
                var t := maxf(0, float(case.elapsed) + dt)
                var index: int = int(t / 2.0) % scene.fixtures.size()
                var blend := smoothstep(0.0, 1.0, fmod(t, 2.0) / 2.0)
                at = scene.fixtures[index].lerp(scene.fixtures[(index+1)%scene.fixtures.size()], blend)
                height = 0.3 + sin(fmod(t, 2.0)/2.0*PI)*7.7
            else:
                at = Vector3(case.x, 0, case.z)
                height = case.height + dt
            scene.set_fixture(at, height)
            var prefix: String = "%s_%02d" % [case.id, step]
            await capture(prefix + "_color")
            for cube in scene.debris: cube.visible = false
            await capture(prefix + "_clean")
            for i in 7:
                scene.debris[i].visible = true
                scene.debris[i].material_override = palette[i]
            await capture(prefix + "_ids")
            for cube in scene.debris: cube.visible = false
            for i in 7:
                scene.debris[i].visible = true
                await capture(prefix + "_solo%d" % i)
                scene.debris[i].visible = false
            for i in 7:
                scene.debris[i].visible = true
                scene.debris[i].material_override = original[i]
            assert(scene.camera.global_transform.is_equal_approx(locked))
            var poses: Array = []
            for cube in scene.debris:
                poses.append([vec(cube.transform.origin), vec(cube.rotation)])
            records.append({"prefix": prefix, "poses": poses, "actor": vec(scene.camera.unproject_position(at + Vector3.UP*0.55)),
                "contact": vec(scene.camera.unproject_position(at)), "exit": vec(scene.camera.unproject_position(Vector3(0,0,-10))),
                "label": vec(scene.camera.unproject_position(Vector3(-3.6,0.15,-10)))})
    var f := FileAccess.open(out.path_join("visibility.json"), FileAccess.WRITE)
    f.store_string(JSON.stringify({"records": records, "viewport": vec(root.size), "camera": vec(locked.origin),
        "description": "Actual color + debris-hidden reference + depth-tested per-object ID + isolated ID passes. Diagnostic passes are NOT production appearance."}, "  "))
    print("VISIBILITY_DONE records=", records.size())
    quit()

func vec(v: Variant) -> Array:
    if v is Vector3: return [v.x,v.y,v.z]
    return [v.x,v.y]
