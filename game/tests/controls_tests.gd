extends Node
## Independent driver: only Input.parse_input_event for controls, never fixed_step,
## read_input, action_press, toggle_pause or request_restart. Teleports arrange
## collision cases; finish is an explicit future-rule fixture, NOT natural win/loss.
signal after_tick
var scene: Node3D
var tick := 0
var phase := "startup"
var samples: Array[Dictionary] = []
var events: Array[Dictionary] = []
var checks: Array[Dictionary] = []
var shots: Array[Dictionary] = []
var captures: Array[String] = []
var out := ""

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    process_physics_priority = 100

func v(value: Vector3) -> Array:
    return [value.x, value.y, value.z]

func _physics_process(dt: float) -> void:
    if not is_instance_valid(scene):
        return
    tick += 1
    var p = scene.player
    samples.append({"tick": tick, "phase": phase, "dt": dt, "position": v(p.global_position),
        "velocity": v(p.velocity), "state": scene.state, "elapsed": scene.elapsed,
        "generation": scene.generation, "held": scene.controls.held.keys(),
        "aim_valid": p.aim_valid, "aim_point": v(p.aim_point), "aim_direction": v(p.aim_direction),
        "shot_count": p.shot_count, "dash_count": p.dash_count,
        "fire_remaining": p.fire_remaining, "dash_remaining": p.dash_remaining})
    after_tick.emit()

func steps(count: int) -> void:
    for i in count:
        await after_tick

func check(ok: bool, name: String, details: Variant = null) -> void:
    checks.append({"name": name, "pass": ok, "details": details})
    if not ok:
        print("CHECK_FAIL ", name, " ", details)

func key(code: Key, pressed: bool, repeat_event: bool = false) -> void:
    var event := InputEventKey.new()
    event.physical_keycode = code
    event.pressed = pressed
    event.echo = repeat_event
    events.append({"tick": tick, "phase": phase, "type": "key", "physical_keycode": code,
        "pressed": pressed, "echo": repeat_event})
    Input.parse_input_event(event)

func mouse(at: Vector2) -> void:
    var event := InputEventMouseMotion.new()
    event.position = at
    event.global_position = at
    events.append({"tick": tick, "phase": phase, "type": "motion", "position": [at.x, at.y]})
    Input.parse_input_event(event)

func button(pressed: bool, index: MouseButton = MOUSE_BUTTON_LEFT) -> void:
    var event := InputEventMouseButton.new()
    event.position = scene.controls.pointer
    event.global_position = event.position
    event.button_index = index
    event.pressed = pressed
    events.append({"tick": tick, "phase": phase, "type": "button", "button": index, "pressed": pressed})
    Input.parse_input_event(event)

func release_all() -> void:
    for code in [KEY_W, KEY_A, KEY_S, KEY_D, KEY_SPACE, KEY_ESCAPE, KEY_R]:
        key(code, false)
    button(false)

func fixture(at: Vector3, name_value: String) -> void:
    phase = name_value
    release_all()
    scene.player.global_position = at
    scene.player.velocity = Vector3.ZERO
    events.append({"tick": tick, "phase": phase, "type": "fixture_position", "position": v(at)})
    await steps(2)

func horizontal(a: Vector3, b: Vector3) -> float:
    return Vector2(a.x - b.x, a.z - b.z).length()

func observe_player(p: CharacterBody3D) -> void:
    p.fired.connect(func(origin: Vector3, direction: Vector3):
        shots.append({"tick": tick + 1, "phase": phase, "generation": scene.generation,
            "origin": v(origin), "direction": v(direction), "position": v(p.global_position),
            "aim_point": v(p.aim_point)}))

func capture(name_value: String) -> void:
    await RenderingServer.frame_post_draw
    check(get_viewport().get_texture().get_image().save_png(out.path_join(name_value + ".png")) == OK,
        "capture_" + name_value)
    captures.append(name_value + ".png")

func run(session: Node3D) -> void:
    scene = session
    out = OS.get_environment("CONTROLS_OUT")
    if out.is_empty() or not DirAccess.dir_exists_absolute(out):
        get_tree().quit(2)
        return
    observe_player(scene.player)
    scene.player_replaced.connect(observe_player)
    await steps(3)
    check(DisplayServer.get_name() != "headless", "actual_rendering")
    check(scene.player.collision_layer == 4 and scene.player.collision_mask == 1, "actor_world_only_layers")
    check(scene.player.SPEED == 5.0 and scene.player.BOLT_DAMAGE == 25, "design_speed_damage_interface")
    for action in scene.controls.KEYS:
        var mapped := InputMap.action_get_events(action)
        check(mapped.size() == 1 and mapped[0] is InputEventKey and
            mapped[0].physical_keycode == scene.controls.KEYS[action], "physical_mapping_" + action)
    var fire_map := InputMap.action_get_events("fire")
    check(fire_map.size() == 1 and fire_map[0] is InputEventMouseButton and
        fire_map[0].button_index == MOUSE_BUTTON_LEFT, "mapping_fire_left_mouse")
    await capture("initial")
    if "--negative-collision" in OS.get_cmdline_user_args():
        await fixture(Vector3(10.5, 0, 8), "negative_collision")
        scene.player.collision_mask = 0
        key(KEY_D, true)
        await steps(45)
        check(scene.player.global_position.x <= 11.602, "negative_control_wall_must_stop", v(scene.player.global_position))
        scene.player.collision_mask = 1
        release_all()
    var directions := {KEY_W: Vector3.FORWARD, KEY_A: Vector3.LEFT, KEY_S: Vector3.BACK, KEY_D: Vector3.RIGHT}
    for code in directions:
        await fixture(Vector3(-7, 0, 5), "movement_" + str(code))
        var start: Vector3 = scene.player.global_position
        key(code, true)
        await steps(1)
        check(horizontal(scene.player.global_position, start) > 0.08, "next_tick_response_" + str(code))
        await steps(11)
        var expected: Vector3 = start + directions[code]
        check(horizontal(scene.player.global_position, expected) < 0.003, "one_meter_12_ticks_" + str(code), v(scene.player.global_position - start))
        key(code, false)
        start = scene.player.global_position
        await steps(12)
        check(horizontal(scene.player.global_position, start) < 0.001, "release_stops_" + str(code))
    await fixture(Vector3(-7, 0, 8), "diagonal")
    var start: Vector3 = scene.player.global_position
    key(KEY_W, true)
    key(KEY_D, true)
    await steps(60)
    check(absf(horizontal(scene.player.global_position, start) - 5.0) < 0.005, "normalized_diagonal_5m_per_second", v(scene.player.global_position - start))
    release_all()
    phase = "opposite_keys"
    start = scene.player.global_position
    for code in [KEY_W, KEY_A, KEY_S, KEY_D]:
        key(code, true)
    await steps(12)
    check(horizontal(scene.player.global_position, start) < 0.001, "opposing_keys_cancel")
    release_all()
    key(KEY_Q, true)
    await steps(3)
    check(horizontal(scene.player.global_position, start) < 0.001, "unmapped_key_ignored")
    key(KEY_Q, false)
    for code in directions:
        var direction: Vector3 = directions[code]
        await fixture(direction * 10.5, "wall_" + str(code))
        key(code, true)
        await steps(45)
        var extent: float = scene.player.global_position.dot(direction)
        check(extent > 11.59 and extent < 11.602, "wall_stops_radius_" + str(code), extent)
        key(KEY_SPACE, true)
        await steps(1)
        check(scene.player.global_position.dot(direction) < 11.602, "dash_cannot_cross_wall_" + str(code))
        release_all()
        await steps(121)
    for case in [{"name": "west", "at": Vector3(-4, 0, 4), "key": KEY_W, "axis": Vector3.FORWARD, "limit": -2.9},
        {"name": "east", "at": Vector3(6, 0, 0), "key": KEY_A, "axis": Vector3.LEFT, "limit": -4.9},
        {"name": "north", "at": Vector3(0, 0, -2), "key": KEY_W, "axis": Vector3.FORWARD, "limit": 3.1}]:
        await fixture(case.at, "cover_" + case.name)
        key(case.key, true)
        key(KEY_SPACE, true)
        await steps(1)
        var extent: float = scene.player.global_position.dot(case.axis)
        check(extent <= case.limit + 0.001 and extent >= case.limit - 0.015, "swept_dash_stops_cover_" + case.name, extent)
        await steps(60)
        check(absf(scene.player.global_position.dot(case.axis) - case.limit) < 0.004,
            "held_movement_stops_cover_" + case.name)
        release_all()
        await steps(121)
    await fixture(Vector3(10.5, 0, 8), "wall_slide")
    key(KEY_W, true)
    key(KEY_D, true)
    start = scene.player.global_position
    await steps(60)
    check(scene.player.global_position.x < 11.602 and scene.player.global_position.z < start.z - 3.4,
        "diagonal_slides_along_wall")
    release_all()
    await fixture(Vector3(10.5, 0, 10.5), "corner_dash")
    key(KEY_S, true)
    key(KEY_D, true)
    key(KEY_SPACE, true)
    await steps(1)
    check(scene.player.global_position.x <= 11.602 and scene.player.global_position.z <= 11.602,
        "diagonal_dash_cannot_cross_corner")
    release_all()
    await steps(121)
    await fixture(Vector3(-8, 0, 8), "dash_moving")
    mouse(scene.camera.unproject_position(Vector3(-8, 0, -8)))
    key(KEY_D, true)
    key(KEY_SPACE, true)
    start = scene.player.global_position
    await steps(1)
    check(absf(scene.player.global_position.x - start.x - 3.0 - 5.0 / 60.0) < 0.003 and
        absf(scene.player.global_position.z - start.z) < 0.001, "moving_dash_prefers_movement_over_aim")
    release_all()
    await steps(121)
    await fixture(Vector3(-8, 0, 8), "dash_open")
    mouse(scene.camera.unproject_position(Vector3(8, 0, 8)))
    await steps(1)
    start = scene.player.global_position
    var dash_before: int = scene.player.dash_count
    key(KEY_SPACE, true)
    await steps(1)
    check(absf(horizontal(scene.player.global_position, start) - 3) < 0.003, "stationary_dash_3m_toward_aim")
    await steps(125)
    check(scene.player.dash_count == dash_before + 1, "held_dash_does_not_repeat_after_cooldown")
    key(KEY_SPACE, false)
    key(KEY_SPACE, true)
    await steps(1)
    check(scene.player.dash_count == dash_before + 2, "fresh_dash_after_cooldown")
    key(KEY_SPACE, false)
    key(KEY_SPACE, true)
    await steps(1)
    check(scene.player.dash_count == dash_before + 2, "dash_cooldown_rejects_new_press")
    key(KEY_SPACE, false)
    await fixture(Vector3(-6, 0, 6), "aim_and_fire")
    for target in [Vector3(8, 0, 8), Vector3(-8, 0, -7), Vector3(4, 0, 0), Vector3(0, 0, -4)]:
        mouse(scene.camera.unproject_position(target))
        await steps(1)
        check(scene.player.aim_valid and scene.player.aim_point.distance_to(target) < 0.003,
            "mouse_ground_target_" + str(target), v(scene.player.aim_point))
        var desired: Vector3 = (target - scene.player.global_position) * Vector3(1, 0, 1)
        check(scene.player.aim_direction.dot(desired.normalized()) > 0.99999,
            "gun_targets_ground_" + str(target))
    var shots_before: int = scene.player.shot_count
    button(true, MOUSE_BUTTON_RIGHT)
    await steps(2)
    check(scene.player.shot_count == shots_before, "right_mouse_does_not_fire")
    button(false, MOUSE_BUTTON_RIGHT)
    button(true)
    await steps(64)
    check(scene.player.shot_count == shots_before + 4, "hold_fire_4_commands_in_64_ticks", scene.player.shot_count - shots_before)
    button(false)
    shots_before = scene.player.shot_count
    await steps(30)
    check(scene.player.shot_count == shots_before, "fire_release_stops")
    await capture("aim_cover")
    mouse(Vector2.ZERO)
    button(true)
    await steps(30)
    check(not scene.player.aim_valid and not scene.player.reticle.visible and scene.player.shot_count == shots_before,
        "off_arena_pointer_suppresses_fire")
    button(false)
    mouse(scene.camera.unproject_position(Vector3(scene.player.global_position.x, 0, scene.player.global_position.z)))
    await steps(1)
    check(not scene.player.aim_valid, "zero_length_aim_suppressed")
    mouse(scene.camera.unproject_position(Vector3(8, 0, -8)))
    await steps(1)
    # Live viewport resizing plus actual mouse events at the new projection.
    get_window().size = Vector2i(960, 720) if get_window().size.x > 1000 else Vector2i(1280, 720)
    await steps(10)
    mouse(scene.camera.unproject_position(Vector3(8, 0, -8)))
    await steps(1)
    check(scene.player.aim_point.distance_to(Vector3(8, 0, -8)) < 0.003, "mouse_target_after_live_resize")
    await capture("resized_target")
    await fixture(Vector3(-7, 0, 8), "pause_held")
    key(KEY_W, true)
    button(true)
    key(KEY_SPACE, true)
    await steps(2)
    key(KEY_SPACE, false)
    key(KEY_ESCAPE, true)
    await steps(1)
    check(scene.state == scene.State.PAUSED and get_tree().paused and scene.panel.visible, "escape_pauses_tree_with_controls_panel")
    check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "pause_pointer_released")
    var frozen := {"at": scene.player.global_position, "time": scene.elapsed,
        "fire": scene.player.fire_remaining, "dash": scene.player.dash_remaining, "shots": scene.player.shot_count}
    check(frozen.dash > 1.9 and frozen.fire > 0.3, "pause_fixture_has_active_cooldowns")
    key(KEY_ESCAPE, true, true)
    key(KEY_D, true)
    key(KEY_SPACE, true)
    await steps(30)
    check(scene.state == scene.State.PAUSED, "escape_echo_does_not_toggle")
    check(scene.elapsed == frozen.time and scene.player.fire_remaining == frozen.fire and
        scene.player.dash_remaining == frozen.dash and scene.player.shot_count == frozen.shots and
        scene.player.global_position == frozen.at, "pause_freezes_position_clock_cooldowns_and_fire")
    key(KEY_R, true)
    await steps(1)
    check(scene.state == scene.State.PAUSED, "restart_ignored_during_pause")
    key(KEY_R, false)
    await capture("paused_controls")
    key(KEY_ESCAPE, false)
    key(KEY_ESCAPE, true)
    key(KEY_ESCAPE, false)
    phase = "resume_held"
    await steps(12)
    check(scene.state == scene.State.PLAYING and not get_tree().paused, "escape_resumes")
    check(horizontal(scene.player.global_position, frozen.at) < 0.001 and scene.player.shot_count == frozen.shots,
        "resume_does_not_resurrect_held_movement_or_fire")
    check(absf(scene.elapsed - frozen.time - 12.0 / 60.0) < 0.0001, "resume_no_clock_jump")
    key(KEY_W, true, true)
    await steps(2)
    check(horizontal(scene.player.global_position, frozen.at) < 0.001, "held_key_echo_cannot_resurrect_movement")
    release_all()
    key(KEY_W, true)
    await steps(2)
    check(horizontal(scene.player.global_position, frozen.at) > 0.16, "fresh_press_after_resume_works")
    release_all()
    var generation_before: int = scene.generation
    key(KEY_R, true)
    key(KEY_R, false)
    await steps(1)
    check(scene.generation == generation_before, "restart_ignored_while_playing")
    for terminal in [scene.State.WON, scene.State.LOST, scene.State.LOST]:
        phase = "restart_" + str(scene.generation)
        key(KEY_D, true)
        button(true)
        key(KEY_SPACE, true)
        await steps(2)
        var old_player_id: int = scene.player.get_instance_id()
        generation_before = scene.generation
        events.append({"tick": tick, "phase": phase, "type": "fixture_terminal", "state": terminal})
        scene.finish(terminal)
        await steps(2)
        check(scene.state == terminal and get_tree().paused, "terminal_freezes_" + str(generation_before))
        key(KEY_R, true)
        key(KEY_R, false)
        await steps(2)
        check(scene.generation == generation_before + 1 and scene.player.get_instance_id() != old_player_id,
            "R_recreates_player_" + str(generation_before))
        check(scene.state == scene.State.PLAYING and not get_tree().paused and scene.player.shot_count == 0 and
            scene.player.dash_count == 0 and scene.player.dash_remaining == 0 and scene.player.fire_remaining == 0,
            "restart_resets_cooldowns_and_commands_" + str(generation_before))
        check(horizontal(scene.player.global_position, scene.arena.player_spawn.origin) < 0.001,
            "restart_spawn_without_stuck_controls_" + str(generation_before))
        check(scene.find_children("*", "CharacterBody3D", true, false).size() == 1,
            "restart_one_player_no_orphans_" + str(generation_before))
        release_all()
        key(KEY_D, true)
        button(true)
        await steps(2)
        check(scene.player.global_position.x > 0.16 and scene.player.shot_count == 1,
            "restart_fresh_movement_and_fire_" + str(generation_before))
        release_all()
    phase = "focus_loss"
    key(KEY_W, true)
    button(true)
    await steps(2)
    events.append({"tick": tick, "phase": phase, "type": "fixture_focus_out_notification"})
    scene.notification(NOTIFICATION_APPLICATION_FOCUS_OUT)
    await steps(2)
    check(scene.state == scene.State.PAUSED and scene.controls.held.is_empty() and
        not scene.controls.pointer_known, "focus_loss_pauses_and_clears_input")
    key(KEY_ESCAPE, true)
    key(KEY_ESCAPE, false)
    start = scene.player.global_position
    await steps(3)
    check(horizontal(scene.player.global_position, start) < 0.001, "focus_resume_no_stuck_key")
    release_all()
    mouse(scene.camera.unproject_position(Vector3(5, 0, 5)))
    key(KEY_A, true)
    await steps(2)
    key(KEY_A, false)
    check(scene.player.aim_valid and horizontal(scene.player.global_position, start) > 0.16,
        "fresh_input_after_focus_resume")
    await capture("final_restart")
    var failures: Array[String] = []
    for entry in checks:
        if not entry.pass:
            failures.append(entry.name)
    var result := {"passed": failures.is_empty(), "checks": checks, "failures": failures,
        "engine": Engine.get_version_info().string, "display": DisplayServer.get_name(),
        "renderer": RenderingServer.get_current_rendering_method(), "captures": captures,
        "input_path": "Input.parse_input_event -> production _input/InputMap -> physics Player",
        "limits": "Automated real rendered runtime; no human observation, fun judgment, natural win/loss, projectiles or pylon colliders."}
    for item in [{"name": "results.json", "data": result}, {"name": "trace.json", "data": {
        "samples": samples, "events": events, "shots": shots}}]:
        var file := FileAccess.open(out.path_join(item.name), FileAccess.WRITE)
        file.store_string(JSON.stringify(item.data, "  ") + "\n")
        file.close()
    print("CONTROLS_TEST_DONE checks=", checks.size(), " failures=", failures.size(), " ticks=", tick)
    get_tree().paused = false
    get_tree().quit(0 if failures.is_empty() else 1)
