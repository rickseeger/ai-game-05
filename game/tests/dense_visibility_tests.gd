extends SceneTree
# Production physics/opposition run; pause only while capturing identical-pose diagnostics.
var scene: Node3D
var out: String
var records: Array = []
func _initialize() -> void:
    run.call_deferred()
func capture(name: String) -> void:
    # Flush pending material/MultiMesh changes through two full render cycles.
    for settle in 2:
        await process_frame
        await RenderingServer.frame_post_draw
    await RenderingServer.frame_post_draw
    assert(root.get_texture().get_image().save_png(out.path_join(name + ".png")) == OK)
func poses() -> Array:
    var result: Array = []
    for b in scene.debris.bodies:
        result.append({"id": b.body_id, "position": [b.position.x,b.position.y,b.position.z],
            "velocity": [b.linear_velocity.x,b.linear_velocity.y,b.linear_velocity.z],
            "rotation": [b.rotation.x,b.rotation.y,b.rotation.z]})
    return result
func run() -> void:
    out = OS.get_environment("ARENA_OUT")
    scene = load("res://opposition.tscn").instantiate()
    root.add_child(scene)
    await physics_frame
    assert(DisplayServer.get_name() == "X11")
    scene.controls.set_enabled(false) # No injected player inputs; enemies remain active.
    for warmup in 90: await physics_frame
    assert(scene.opposition.sentries.size() == 2)
    for target in scene.targets:
        target.apply_damage(100, target.global_position, Vector3.UP)
    for i in 3:
        var at: Vector3 = [Vector3(0,0,9.5),Vector3(0,0,-9.5),Vector3(3,0,2)][i]
        scene.debris.burst(Transform3D(Basis.IDENTITY,at), &"pylon", 2207+i)
    assert(scene.debris.bodies.size() == 192)
    var batch: MultiMeshInstance3D = scene.debris.batch
    var original: Material = batch.material_override
    var original_colors: Array[Color] = []
    var diagnostic_colors: Array[Color] = []
    for i in 192:
        original_colors.append(scene.debris.bodies[i].color)
        diagnostic_colors.append(Color8((i%8)*32+16,((i/8)%8)*32+16,(i/64)*64+16))
    var material := StandardMaterial3D.new()
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.vertex_color_use_as_albedo = true
    var locked: Transform3D = scene.camera.global_transform
    for tick in range(1, 121):
        await physics_frame
        if tick in [1,12,30,60,90,120]:
            paused = true
            scene.debris._process(0)
            assert(scene.debris.bodies.size() == 192)
            var saved := poses()
            var prefix := "dense_%03d" % tick
            await capture(prefix + "_color")
            batch.visible = false
            await capture(prefix + "_clean")
            batch.visible = true
            batch.material_override = material
            for i in 192: batch.multimesh.set_instance_color(i, diagnostic_colors[i])
            await capture(prefix + "_ids")
            batch.material_override = original
            for i in 192: batch.multimesh.set_instance_color(i, original_colors[i])
            var sun: DirectionalLight3D = scene.find_children("*", "DirectionalLight3D", true, false)[0]
            sun.shadow_enabled = false
            await capture(prefix + "_no_shadows")
            sun.shadow_enabled = true
            assert(saved == poses(), "diagnostic passes must not advance physics")
            assert(scene.camera.global_transform.is_equal_approx(locked))
            records.append({"prefix": prefix, "tick": tick, "count":192, "poses":saved,
                "sentries":scene.opposition.sentries.size(), "health":scene.player.health,
                "actor": vec(scene.camera.unproject_position(scene.player.position+Vector3.UP*0.5)),
                "contact":vec(scene.camera.unproject_position(scene.player.position)),
                "exit":vec(scene.camera.unproject_position(Vector3(0,0,-10))),
                "label":vec(scene.camera.unproject_position(Vector3(-3.6,0.15,-10)))})
            paused = false
    # Pixel-level perspective oracle: identical boxes at known near/far depths.
    paused = true
    batch.visible = false
    var near_box: MeshInstance3D = scene.ArenaScript.box(scene,Vector3.ONE,Vector3(-7,0.5,9),Color.WHITE)
    var far_box: MeshInstance3D = scene.ArenaScript.box(scene,Vector3.ONE,Vector3(-7,0.5,-9),Color.WHITE)
    var m := StandardMaterial3D.new()
    m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    m.albedo_color = Color(1,0,1)
    near_box.material_override = m
    far_box.visible = false
    await capture("perspective_near")
    near_box.visible = false
    far_box.visible = true
    far_box.material_override = m
    await capture("perspective_far")
    var f := FileAccess.open(out.path_join("dense.json"),FileAccess.WRITE)
    f.store_string(JSON.stringify({"records":records,"viewport":vec(root.size),"camera":vec(locked.origin),
        "description":"192 real production RigidBody3D blocks, active opposition, original physics. Snapshot diagnostics pause simulation; not a timing benchmark or combat acceptance."}, "  "))
    print("DENSE_VISIBILITY_DONE snapshots=", records.size())
    quit()
func vec(v: Variant) -> Array:
    if v is Vector3: return [v.x,v.y,v.z]
    return [v.x,v.y]
