extends Node
var session: Node3D
var service: Node3D
var out := ""
var tick := 0
var recording := false
var checks: Array[Dictionary] = []
var events: Array[Dictionary] = []
var frames: Array[Dictionary] = []
var samples: FileAccess
var intervals: FileAccess
var last_usec := 0
var capture_busy := false
var capture_tick := -100
var destroyed_count := 0
var initial: Array = []
var peak_count := 0
var seed_value := 1201
var no_capture := false
var performance_only := false
var first_ids: Array[int] = []
var first_state: Dictionary = {}
var failures: Array[String] = []

func check(label: String, value: bool) -> void:
    checks.append({"name": label, "pass": value, "tick": tick})
    if not value:
        failures.append(label)
        push_error("DESTRUCTION_ASSERT " + label)

func v3(v: Vector3) -> Array:
    return [v.x, v.y, v.z]

func record_event(kind: String, data: Dictionary) -> void:
    data["kind"] = kind
    data["tick"] = tick
    data["engine_tick"] = Engine.get_physics_frames()
    data["unix_seconds"] = Time.get_unix_time_from_system()
    events.append(data)

func on_burst(id: int, at: Vector3) -> void:
    record_event("burst", {"id": id, "position": v3(at), "count": service.bodies.size()})
    if tick == 1:
        check("collider_removed_before_burst", not is_instance_valid(session.targets[2].intact))

func on_retired(id: int, reason: String, age: float, asleep: bool) -> void:
    record_event("retire", {"id": id, "reason": reason, "age": age, "sleeping": asleep})

func on_destroyed(_id: int, _at: Transform3D, _kind: StringName, _seed: int) -> void:
    destroyed_count += 1
    record_event("destroyed", {"count": destroyed_count})

func run(owner: Node3D) -> void:
    session = owner
    service = owner.debris
    # Fixture events are injected on the normal fixed-step path, before child physics.
    process_physics_priority = -5
    out = OS.get_environment("DESTRUCTION_OUT")
    no_capture = "--no-captures" in OS.get_cmdline_user_args()
    performance_only = "--performance" in OS.get_cmdline_user_args()
    if not OS.get_environment("DESTRUCTION_SEED").is_empty():
        seed_value = int(OS.get_environment("DESTRUCTION_SEED"))
    session.run_seed = seed_value
    session.make_targets()
    service.burst_started.connect(on_burst)
    service.fragment_retired.connect(on_retired)
    service.impact.connect(func(at: Vector3, speed: float, material: StringName, id: int):
        record_event("impact", {"position": v3(at), "speed": speed, "material": material, "id": id}))
    session.targets[2].destroyed.connect(on_destroyed)
    samples = FileAccess.open(out.path_join("physics.csv"), FileAccess.WRITE)
    samples.store_line("tick,unix_seconds,id,event,age,x,y,z,vx,vy,vz,qx,qy,qz,qw,wx,wy,wz,contacts,sleeping,scale")
    intervals = FileAccess.open(out.path_join("frames.csv"), FileAccess.WRITE)
    intervals.store_line("unix_seconds,tick,interval_ms,physics_ms,active,sleeping,capture_overlap")
    await get_tree().physics_frame
    check("rendered_x11", DisplayServer.get_name() == "X11")
    check("engine_451", Engine.get_version_info().string.begins_with("4.5.1"))
    check("physics_60hz", Engine.physics_ticks_per_second == 60)
    check("gravity_9_8", is_equal_approx(ProjectSettings.get_setting("physics/3d/default_gravity"), 9.8))
    last_usec = Time.get_ticks_usec()
    recording = true

func _process(_dt: float) -> void:
    if not recording:
        return
    var now := Time.get_ticks_usec()
    var sleeping := 0
    for body in service.bodies:
        sleeping += int(body.sleeping)
    intervals.store_line("%.6f,%d,%.6f,%.6f,%d,%d,%d" % [Time.get_unix_time_from_system(), tick,
        float(now - last_usec) / 1000.0, Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000,
        service.bodies.size(), sleeping, int(capture_busy or tick - capture_tick < 4)])
    last_usec = now

func snapshot() -> Array:
    var result: Array = []
    for b in service.bodies:
        result.append({"p": v3(b.global_position), "v": v3(b.linear_velocity), "w": v3(b.angular_velocity)})
    return result

func _physics_process(_dt: float) -> void:
    if not recording:
        return
    tick += 1
    if tick == 1:
        var target = session.targets[2]
        for i in 3:
            target.apply_damage(25, target.global_position, Vector3.UP)
        check("three_hits_intact", target.health == 25 and is_instance_valid(target.intact) and service.bodies.is_empty())
        target.apply_damage(25, target.global_position, Vector3.UP)
        target.apply_damage(100, target.global_position, Vector3.UP)
        check("once_only_destruction", destroyed_count == 1 and target.is_destroyed)
        check("pylon_32", service.bodies.size() == 32)
        initial = snapshot()
        for b in service.bodies:
            first_ids.append(b.body_id)
            first_state[b.body_id] = {"up": false, "down": false, "contact": false, "bounce": false,
                "spin": false, "tumble": false, "sleep": false, "previous_vy": b.linear_velocity.y,
                "previous_q": b.quaternion, "start_y": b.global_position.y}
        var config_ok := true
        for b in service.bodies:
            config_ok = config_ok and is_equal_approx(b.mass, 0.3) and b.collision_layer == 2 and b.collision_mask == 1 and b.continuous_cd
            config_ok = config_ok and is_equal_approx(b.physics_material_override.friction, 0.65) and is_equal_approx(b.physics_material_override.bounce, 0.42)
            config_ok = config_ok and b.max_contacts_reported == 8 and b.get_child(0).shape is BoxShape3D
        check("rigid_body_configuration", config_ok)
        if "--negative-gravity" in OS.get_cmdline_user_args():
            for b in service.bodies:
                b.gravity_scale = 0.0
        if "--negative-ground" in OS.get_cmdline_user_args():
            for b in service.bodies:
                b.collision_mask = 0
    if tick == 390:
        for feature in ["up", "down", "contact", "bounce", "spin", "tumble", "sleep"]:
            var count := 0
            for s in first_state.values():
                count += int(s[feature])
            check("all_32_" + feature, count == 32)
    if tick == 400:
        var aligned: bool = service.batch.multimesh.visible_instance_count == service.bodies.size()
        for i in service.bodies.size():
            var b = service.bodies[i]
            var pose: Transform3D = service.global_transform * service.batch.multimesh.get_instance_transform(i)
            aligned = aligned and pose.origin.distance_to(b.global_position) < 0.001 and pose.basis.is_equal_approx(b.global_basis)
        check("render_batch_matches_sleeping_rigid_poses", aligned)
    if tick == 420:
        check("payoff_retained_seven_seconds", service.bodies.size() == 32)
    if tick == 451:
        check("final_second_visual_shrink", service.bodies.size() == 32 and service.bodies[0].visual_scale < 0.6 and service.bodies[0].visual_scale > 0.4)
    if tick == 490:
        check("eight_second_cleanup", service.bodies.is_empty() and service.get_child_count() == 1)
    if tick == 510:
        for target in session.targets:
            if is_instance_valid(target.intact):
                target.apply_damage(100, target.global_position, Vector3.UP)
        service.clear()
        for i in 6:
            service.burst(Transform3D(Basis.IDENTITY, Vector3((i % 3 - 1) * 7, 0, -6 if i < 3 else 6)), &"pylon", seed_value + 10 + i)
        check("six_simultaneous_192", service.bodies.size() == 192)
    if tick == 630:
        for i in 3:
            service.burst(session.arena.pylon_spawns[i], &"pylon", seed_value + 20 + i)
        check("repeat_active_cap_192", service.bodies.size() == 192)
    if tick == 900:
        for i in 3:
            service.burst(session.arena.pylon_spawns[i], &"pylon", seed_value + 30 + i)
        check("repeat_sleeping_cap_192", service.bodies.size() == 192)
    if tick == 1390:
        check("stress_ttl_cleanup", service.bodies.is_empty() and service.get_child_count() == 1)
        # Same seeded event, exact initial conditions independent of prior pool history.
        service.burst(session.arena.pylon_spawns[2], &"pylon", seed_value + 2)
        check("seed_repeatability", snapshot() == initial)
        service.clear()
        service.burst(Transform3D.IDENTITY, &"sentinel", seed_value)
        check("sentinel_16", service.bodies.size() == 16)
        service.clear()
        check("explicit_clear", service.bodies.is_empty() and service.get_child_count() == 1)
        for i in 3:
            service.burst(Transform3D.IDENTITY, &"pylon", seed_value + i)
            session.finish(session.State.LOST)
            session.request_restart()
            check("session_restart_cleanup_%d" % i, service.bodies.is_empty() and service.get_child_count() == 1 and session.targets.size() == 3)
        service.burst(Transform3D.IDENTITY, &"sentinel", seed_value + 44)
        var age: float = service.bodies[0].age
        session.pause(true)
        await get_tree().create_timer(0.15, true).timeout
        check("pause_freezes_debris", is_equal_approx(service.bodies[0].age, age))
        session.pause(false)
        service.clear()
        # Natural mixed-state cap fixture: oldest bodies still falling from height,
        # newer bodies on the floor sleep. No forced sleep or scripted trajectory.
        service.burst(Transform3D(Basis.IDENTITY, Vector3(0, 100, 0)), &"pylon", seed_value + 80)
        for i in 5:
            service.burst(Transform3D(Basis.IDENTITY, Vector3((i % 3 - 1) * 6, 0, 6)), &"pylon", seed_value + 81 + i)
        await get_tree().create_timer(5.5, false, true).timeout
        var oldest_id: int = service.bodies[0].body_id
        check("mixed_oldest_awake", not service.bodies[0].sleeping)
        var expected: Array[int] = []
        for body in service.bodies:
            if body.sleeping and expected.size() < 16:
                expected.append(body.body_id)
        check("mixed_younger_sleepers", expected.size() == 16)
        var event_start := events.size()
        service.burst(Transform3D.IDENTITY, &"sentinel", seed_value + 90)
        var actual: Array[int] = []
        for e in events.slice(event_start):
            if e.kind == "retire":
                actual.append(e.id)
        check("sleepers_before_older_active", actual == expected and service.bodies[0].body_id == oldest_id)
        service.clear()
        finish()
        return
    peak_count = maxi(peak_count, service.bodies.size())
    if service.bodies.size() > 192:
        check("cap_never_exceeded", false)
    for b in service.bodies:
        var p: Vector3 = b.global_position
        var v: Vector3 = b.linear_velocity
        var q: Quaternion = b.quaternion
        var w: Vector3 = b.angular_velocity
        if b.body_id in first_state:
            var s: Dictionary = first_state[b.body_id]
            s.up = s.up or p.y > s.start_y + 0.4
            s.down = s.down or v.y < -1.0
            s.contact = s.contact or b.contact_count > 0
            s.bounce = s.bounce or (s.contact and s.previous_vy < -0.5 and v.y > 0.3)
            var turn: float = q.angle_to(s.previous_q)
            s.spin = s.spin or turn > 0.03
            s.tumble = s.tumble or (s.contact and p.y < 0.5 and turn > 0.015)
            s.sleep = s.sleep or b.sleeping
            s.previous_vy = v.y
            s.previous_q = q
        if performance_only:
            continue
        samples.store_line("%d,%.6f,%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%d,%.6f" % [tick,
            Time.get_unix_time_from_system(), b.body_id, b.event_id, b.age, p.x,p.y,p.z,v.x,v.y,v.z,q.x,q.y,q.z,q.w,w.x,w.y,w.z,b.contact_count,int(b.sleeping),b.visual_scale])
    if not no_capture and tick in [1,10,30,60,90,96,102,108,114,120,126,132,138,144,150,210,300,390,450,479,490,511,540,600,631,660,720,900,930,1020,1190,1385]:
        capture()

func capture() -> void:
    var at_tick := tick
    capture_busy = true
    await RenderingServer.frame_post_draw
    var filename := "frame_%04d.png" % at_tick
    var error := get_viewport().get_texture().get_image().save_png(out.path_join(filename))
    frames.append({"file": filename, "tick": at_tick, "observed_tick": tick,
        "unix_seconds": Time.get_unix_time_from_system(), "error": error})
    capture_tick = tick
    capture_busy = false

func finish() -> void:
    recording = false
    samples.close()
    intervals.close()
    var report := {"passed": failures.is_empty(), "checks": checks, "failures": failures,
        "seed": seed_value, "initial": initial, "events": events, "frames": frames,
        "peak_count": peak_count, "ticks": tick, "engine": Engine.get_version_info(),
        "renderer": RenderingServer.get_video_adapter_name(), "display": DisplayServer.get_name(),
        "visual_assessment": "UNASSESSED: rendered files are not perception", "no_captures": no_capture, "performance_only": performance_only}
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(report, "  "))
    print("DESTRUCTION_TEST_DONE checks=", checks.size(), " failures=", failures.size(), " ticks=", tick)
    get_tree().quit(0 if failures.is_empty() else 1)
