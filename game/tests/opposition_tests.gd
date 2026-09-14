extends Node
## Input-driven natural scenarios plus explicitly labeled isolated contract fixtures.
var session: Node3D
var out := ""
var mode := "inactive"
var tick := 0
var events: Array[Dictionary] = []
var checks: Array[Dictionary] = []
var failures: Array[String] = []
var trace: Array[Dictionary] = []
var frames: Array[Dictionary] = []
var running := false
var finishing := false
var captures := false
var capture_busy := false
var frame_index := 0
var controls_started := false
var audio_events: Array[Dictionary] = []
var impact_sources: Array[Dictionary] = []
var target_id := -1
var dash_used := false

func check(label: String, value: bool) -> void:
    checks.append({"name": label, "pass": value, "tick": tick})
    if not value:
        failures.append(label)
        push_error("OPPOSITION_ASSERT " + label)

func record(kind: String, data: Dictionary) -> void:
    var item := data.duplicate(true)
    item.kind = kind
    item.tick = tick
    item.engine_tick = Engine.get_physics_frames()
    item.unix_seconds = Time.get_unix_time_from_system()
    events.append(item)

func attach_player() -> void:
    session.player.damaged.connect(func(amount: int, source: Vector3):
        record("player_damage", {"amount": amount, "health": session.player.health, "source": session.combat.vec(source)}))
    session.player.died.connect(func(): record("player_died", {"health": session.player.health}))
    session.player.fired.connect(func(origin: Vector3, direction: Vector3):
        record("player_fired", {"origin": session.combat.vec(origin), "direction": session.combat.vec(direction)}))
    session.player.dashed.connect(func(distance: float): record("player_dash", {"distance": distance}))

func run(owner: Node3D) -> void:
    session = owner
    process_mode = Node.PROCESS_MODE_ALWAYS
    process_physics_priority = -8
    out = OS.get_environment("OPPOSITION_OUT")
    mode = OS.get_environment("OPPOSITION_SCENARIO")
    captures = OS.get_environment("OPPOSITION_CAPTURE") == "1"
    session.sound.audio_event.connect(func(data: Dictionary): audio_events.append(data.duplicate(true)))
    session.debris.impact.connect(func(_at: Vector3, speed: float, _material: StringName, id: int):
        impact_sources.append({"id": id, "tick": Engine.get_physics_frames(), "speed": speed}))
    session.combat.event.connect(record)
    session.opposition.event.connect(record)
    session.debris.burst_started.connect(func(id: int, at: Vector3):
        record("burst", {"id": id, "position": session.combat.vec(at), "bodies": session.debris.bodies.size()}))
    session.state_changed.connect(func(state: int): record("state", {"state": state}))
    # Ordinary same-seed restart records both initial warnings, no scenario buff.
    session.start(1201)
    attach_player()
    running = true
    check("real_rendered_x11", DisplayServer.get_name() == "X11")
    check("physics_60hz", Engine.physics_ticks_per_second == 60)
    if mode == "focused":
        focused()

func key(code: int, pressed: bool) -> void:
    var e := InputEventKey.new()
    e.physical_keycode = code
    e.pressed = pressed
    Input.parse_input_event(e)
    record("input_key", {"code": code, "pressed": pressed})

func mouse(at: Vector3, fire: bool) -> void:
    var point: Vector2 = session.camera.unproject_position(at)
    var motion := InputEventMouseMotion.new()
    motion.position = point
    Input.parse_input_event(motion)
    if fire != controls_started:
        var button := InputEventMouseButton.new()
        button.button_index = MOUSE_BUTTON_LEFT
        button.position = point
        button.pressed = fire
        Input.parse_input_event(button)
        controls_started = fire
        record("input_fire", {"pressed": fire, "pointer": [point.x, point.y]})

func active_input() -> void:
    # Wait for genuine incoming fire/damage, then counter through actual mouse and
    # dash InputEvents. No health override, direct damage or enemy debuff here.
    if session.player.health == 100:
        return
    if not dash_used:
        var nearest: CharacterBody3D = null
        for sentry in session.opposition.sentries:
            if nearest == null or sentry.global_position.distance_to(session.player.global_position) < nearest.global_position.distance_to(session.player.global_position):
                nearest = sentry
        if nearest != null:
            mouse(nearest.global_position, false)
        key(KEY_A, true)
        key(KEY_SPACE, true)
        dash_used = true
    else:
        key_release_once()
    var chosen: CharacterBody3D = null
    for sentry in session.opposition.sentries:
        if sentry.entity_id == target_id:
            chosen = sentry
    if chosen == null and not session.opposition.sentries.is_empty():
        chosen = session.opposition.sentries[0]
        target_id = chosen.entity_id
        record("bot_target", {"entity": target_id})
    if chosen != null:
        mouse(chosen.global_position, true)
    else:
        mouse(session.player.global_position + Vector3.FORWARD, false)

var released := false
func key_release_once() -> void:
    if not released:
        key(KEY_SPACE, false)
        key(KEY_A, false)
        released = true

func _physics_process(_dt: float) -> void:
    if not running or finishing:
        return
    tick += 1
    if mode == "active" and session.state == session.State.PLAYING:
        active_input()
    var enemies: Array = []
    for sentry in session.opposition.sentries:
        enemies.append({"id": sentry.entity_id, "p": session.combat.vec(sentry.global_position),
            "health": sentry.health, "aiming": sentry.aiming, "aim_left": sentry.aim_left})
    trace.append({"tick": tick, "unix_seconds": Time.get_unix_time_from_system(), "time": session.elapsed, "health": session.player.health,
        "state": session.state, "player": session.combat.vec(session.player.global_position),
        "enemies": enemies, "bolts": session.combat.bolts.size(), "debris": session.debris.bodies.size()})
    if mode == "focused":
        return
    if session.state == session.State.LOST:
        check("natural_lethal_pressure" if mode == "inactive" else "active_survives", mode == "inactive")
        check("zero_health_terminal", session.player.health == 0)
        check("seven_15_damage_hits", events.filter(func(e): return e.kind == "player_damage").size() == 7)
        finish()
    elif mode == "active" and tick >= 1800:
        check("active_survives_30_seconds", session.player.health > 0 and session.state == session.State.PLAYING)
        check("actively_threatened_and_hurt", not events.filter(func(e): return e.kind == "player_damage").is_empty())
        check("player_shot_counterplay", events.filter(func(e): return e.kind == "destroyed").size() >= 2)
        check("real_input_fire", session.player.shot_count >= 4)
        check("real_input_dash", session.player.dash_count == 1)
        finish()
    elif tick >= 3600:
        check("inactive_fails_within_60_seconds", false)
        finish()

func _process(_dt: float) -> void:
    if running and captures and not capture_busy and not finishing:
        capture()

func capture() -> void:
    capture_busy = true
    var sampled_tick := tick
    await RenderingServer.frame_post_draw
    frame_index += 1
    var filename := "frame_%05d.png" % frame_index
    var image := get_viewport().get_texture().get_image()
    var error := image.save_png(out.path_join(filename))
    frames.append({"file": filename, "tick": sampled_tick, "observed_tick": tick,
        "unix_seconds": Time.get_unix_time_from_system(), "error": error})
    capture_busy = false

func verify_rendered_cue(s: CharacterBody3D) -> void:
    # Isolated rendering fixture ONLY: freeze normal physics without a pause HUD,
    # toggle just the real beam, flush each change, then restore before resuming.
    # Natural inactive/active scenarios never enter this function.
    get_tree().paused = true
    var before: float = s.aim_left
    var endpoints: Array = []
    for z in [-s.RANGE / 2.0, s.RANGE / 2.0]:
        var p: Vector2 = session.camera.unproject_position(s.beam.to_global(Vector3(0, 0, z)))
        endpoints.append([p.x, p.y])
    var samples: Array = []
    for visible in [true, false, true]:
        s.beam.visible = visible
        await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var filename: String = ["cue_on.png", "cue_off.png", "cue_restored.png"][samples.size()]
        var image := get_viewport().get_texture().get_image()
        var error := image.save_png(out.path_join(filename))
        check("cue_capture_" + filename, error == OK)
        samples.append({"file": filename, "unix_seconds": Time.get_unix_time_from_system(),
            "tick": tick, "engine_tick": Engine.get_physics_frames(), "visible": visible})
    check("cue_capture_does_not_advance_attack", s.aim_left == before and s.aiming and s.beam.visible)
    FileAccess.open(out.path_join("cue-render.json"), FileAccess.WRITE).store_string(JSON.stringify({
        "fixture": "paused physics; production beam on/off/restored; no gameplay changes",
        "endpoints": endpoints, "frames": samples, "aim_left": before,
        "width": 1280, "height": 720, "subjective_readability": "UNASSESSED"}, "  "))
    get_tree().paused = false

func wait_ticks(count: int) -> void:
    for i in count:
        await get_tree().physics_frame

func fixture_reset() -> void:
    session.start(1201)
    session.opposition.clear()
    session.opposition.set_physics_process(false)
    attach_player()
    session.player.global_position = Vector3(0, 0, 10)

func fixture_sentry(at: Vector3) -> CharacterBody3D:
    var s = load("res://sentry.gd").new()
    s.entity_id = 900 + tick
    s.destruction = session.debris
    s.combat = session.combat
    s.player = session.player
    s.event.connect(record)
    session.add_child(s)
    s.global_position = at
    return s

func focused() -> void:
    fixture_reset()
    var s = fixture_sentry(Vector3(-10, 0, 10))
    var start := events.size()
    await wait_ticks(120)
    check("pursues_to_six_meter_range", s.global_position.x > -7 and s.global_position.distance_to(session.player.global_position) <= 6.03)
    await wait_ticks(180)
    var aims: Array = events.slice(start).filter(func(e): return e.kind == "aim")
    var attacks: Array = events.slice(start).filter(func(e): return e.kind == "attack")
    check("attacks_exist", attacks.size() >= 2)
    if attacks.size() >= 2 and aims.size() >= 2:
        check("aim_36_ticks", attacks[0].engine_tick - aims[0].engine_tick == 36)
        check("cycle_108_ticks", attacks[1].engine_tick - attacks[0].engine_tick == 108)
    check("projectile_damage_15", session.player.health < 100 and (100-session.player.health) % 15 == 0)
    s.free()
    fixture_reset()
    # Real static cover collision, fired through the same combat API.
    session.player.global_position = Vector3(0, 0, 2)
    s = fixture_sentry(Vector3(-8, 0, 2))
    s.set_physics_process(false)
    await wait_ticks(2)
    start = events.size()
    session.combat.spawn_bolt(s, Vector3(-8, 0.65, 2), Vector3.RIGHT, 15)
    await wait_ticks(80)
    check("cover_stops_enemy_bolt", session.player.health == 100 and events.slice(start).any(func(e): return e.kind == "hit" and e.damage == 0 and e.collider == "CoverWest"))
    check("cover_blocks_sight", not s.clear_sight(session.player.global_position))
    s.set_physics_process(true)
    start = events.size()
    await wait_ticks(360)
    check("obstacle_avoidance_reaches_attack", events.slice(start).any(func(e): return e.kind == "attack"))
    s.free()
    fixture_reset()
    s = fixture_sentry(Vector3(0, 0, 3))
    s.set_physics_process(false)
    await wait_ticks(2)
    session.combat.spawn_bolt(s, Vector3(0, 0.65, 3), Vector3.BACK, 15)
    await wait_ticks(70)
    check("intact_pylon_is_cover", session.player.health == 100 and session.targets[2].health == 100)
    for i in 3:
        session.combat.spawn_bolt(session.player, Vector3(0, 0.65, 9.75), Vector3.FORWARD, 25)
        await wait_ticks(21)
    check("three_player_bolts_leave_pylon", session.targets[2].health == 25 and is_instance_valid(session.targets[2].intact))
    session.combat.spawn_bolt(session.player, Vector3(0, 0.65, 9.75), Vector3.FORWARD, 25)
    await wait_ticks(21)
    check("fourth_player_bolt_removes_cover", session.targets[2].is_destroyed and not is_instance_valid(session.targets[2].intact) and session.debris.bodies.size() == 32)
    session.combat.spawn_bolt(s, Vector3(0, 0.65, 3), Vector3.BACK, 15)
    await wait_ticks(70)
    check("destroyed_cover_exposes_player", session.player.health == 85)
    check("debris_does_not_block_bolts", session.debris.bodies.size() == 32 and session.combat.bolts.is_empty())
    s.free()
    fixture_reset()
    s = fixture_sentry(Vector3(-6, 0, 10))
    s.set_physics_process(false)
    await wait_ticks(2)
    var observed: Array = []
    var burst_callback := func(_id: int, _at: Vector3):
        observed.append(not is_instance_valid(s.intact) and not is_instance_valid(s.collider) and s.collision_layer == 0)
    session.debris.burst_started.connect(burst_callback)
    var deaths: Array = []
    s.destroyed.connect(func(id: int, _at: Transform3D, kind: StringName, _seed: int): deaths.append([id, kind]))
    session.combat.spawn_bolt(session.player, Vector3(-0.25, 0.65, 10), Vector3.LEFT, 25)
    await wait_ticks(21)
    check("first_player_bolt_sentry_25", s.health == 25 and not s.is_destroyed)
    session.combat.spawn_bolt(session.player, Vector3(-0.25, 0.65, 10), Vector3.LEFT, 25)
    await wait_ticks(21)
    s.apply_damage(25, Vector3.ZERO, Vector3.ZERO)
    s.apply_damage(-25, Vector3.ZERO, Vector3.ZERO)
    check("second_bolt_once_only_death", s.health == 0 and s.is_destroyed and deaths.size() == 1)
    check("sixteen_service_fragments", session.debris.bodies.size() == 16)
    check("collider_and_mesh_removed_before_burst", observed == [true])
    var bolt_count: int = session.combat.next_id
    s.fixed_step(10, session.player.global_position)
    check("dead_sentry_cannot_attack", session.combat.next_id == bolt_count)
    session.debris.burst_started.disconnect(burst_callback)
    s.free()
    fixture_reset()
    # Locked aim does not magically track a dodging player after the warning.
    s = fixture_sentry(Vector3(-6, 0, 10))
    await wait_ticks(8)
    var locked: Vector3 = s.locked_direction
    check("red_aim_visible_before_attack", s.aiming and s.beam.visible)
    await verify_rendered_cue(s)
    session.player.global_position = Vector3(0, 0, 7)
    await wait_ticks(82)
    check("locked_aim_dodge_avoids_damage", locked.is_equal_approx(Vector3.RIGHT) and session.player.health == 100)
    s.free()
    fixture_reset()
    s = fixture_sentry(Vector3(-3, 0, 10))
    await wait_ticks(4)
    start = events.size()
    # Two real swept bolts at the designed 21-tick cadence arrive during aim.
    session.combat.spawn_bolt(session.player, Vector3(-0.25, 0.65, 10), Vector3.LEFT, 25)
    await wait_ticks(21)
    session.combat.spawn_bolt(session.player, Vector3(-0.25, 0.65, 10), Vector3.LEFT, 25)
    await wait_ticks(50)
    check("counterfire_interrupts_telegraphed_attack", s.is_destroyed and not events.slice(start).any(func(e): return e.kind == "attack"))
    check("counterfire_preserves_health", session.player.health == 100)
    s.free()
    fixture_reset()
    session.player.global_position = Vector3(-8, 0, 2)
    await wait_ticks(2)
    start = events.size()
    session.combat.spawn_bolt(session.player, Vector3(-7.75, 0.65, 2), Vector3.RIGHT, 25)
    await wait_ticks(30)
    check("static_cover_stops_player_bolt", events.slice(start).any(func(e): return e.kind == "hit" and e.friendly and e.damage == 0 and e.collider == "CoverWest"))
    fixture_reset()
    # Manager-only clock fixture: normal 1/60 steps, sentries frozen solely to
    # isolate spawn policy. Natural scenarios below do NOT freeze or heal actors.
    var freeze := func(kind: String, _data: Dictionary):
        if kind == "spawn":
            session.opposition.sentries.back().set_physics_process(false)
    session.opposition.event.connect(freeze)
    start = events.size()
    session.opposition.start(1201)
    check("two_initial_warnings", session.opposition.pending.size() == 2 and session.opposition.sentries.is_empty())
    for i in 59:
        session.opposition._physics_process(1.0/60)
    check("no_spawn_before_one_second", session.opposition.sentries.is_empty())
    session.opposition._physics_process(1.0/60)
    check("two_spawn_after_one_second", session.opposition.sentries.size() == 2)
    for i in 840:
        session.opposition._physics_process(1.0/60)
    check("next_warning_at_15_seconds", session.opposition.pending.size() == 1 and session.opposition.sentries.size() == 2)
    for i in 3660:
        session.opposition._physics_process(1.0/60)
    check("spawn_cap_six", session.opposition.sentries.size() == 6 and session.opposition.pending.is_empty() and not session.opposition.warn_spawn())
    check("all_spawns_eight_meters", events.slice(start).filter(func(e): return e.kind == "spawn").all(func(e): return e.distance >= 8.0))
    session.opposition.start(1201)
    var invaded: Vector3 = session.opposition.pending[0].position
    session.player.global_position = invaded
    start = events.size()
    for i in 60:
        session.opposition._physics_process(1.0/60)
    check("approached_warning_cancelled", events.slice(start).any(func(e): return e.kind == "spawn_cancelled"))
    check("replacement_warned_not_instant", events.slice(start).any(func(e): return e.kind == "spawn_warning") and session.opposition.pending.size() >= 1)
    session.opposition.event.disconnect(freeze)
    fixture_reset()
    session.opposition.set_physics_process(true)
    session.opposition.start(1201)
    await wait_ticks(10)
    var before: float = session.opposition.elapsed
    var warning_left: float = session.opposition.pending[0].left
    session.pause(true)
    await wait_ticks(20)
    check("pause_freezes_spawn_clock", session.opposition.elapsed == before and session.opposition.pending[0].left == warning_left)
    session.pause(false)
    s = fixture_sentry(Vector3(-6, 0, 10))
    await wait_ticks(4)
    var aim_left: float = s.aim_left
    session.combat.spawn_bolt(s, Vector3(-6, 0.65, 10), Vector3.RIGHT, 15)
    var position: Vector3 = session.combat.bolts[0].p
    session.pause(true)
    await wait_ticks(20)
    check("pause_freezes_aim_and_bolt", s.aim_left == aim_left and session.combat.bolts[0].p == position)
    session.pause(false)
    s.free()
    session.player.apply_damage(-15, Vector3.ZERO)
    check("negative_player_damage_ignored", session.player.health == 100)
    session.player.apply_damage(200, Vector3.LEFT)
    session.player.apply_damage(15, Vector3.LEFT)
    # Production terminal resolution is end-of-tick, not inside died emission.
    await wait_ticks(2)
    check("lethal_idempotent", session.player.health == 0 and session.state == session.State.LOST and events.filter(func(e): return e.kind == "player_died").size() == 1)
    key(KEY_R, true)
    await wait_ticks(2)
    key(KEY_R, false)
    check("input_restart_cleans_threats", session.state == session.State.PLAYING and session.player.health == 100 and session.combat.bolts.is_empty() and session.debris.bodies.is_empty() and session.opposition.pending.size() == 2)
    finish()

func finish() -> void:
    if finishing:
        return
    finishing = true
    if capture_busy:
        await RenderingServer.frame_post_draw
    # Capture terminal/result with a matching explicit sample in the trace.
    if captures:
        await capture()
    running = false
    # Observe production combat -> target/sentry -> destruction -> sound, not
    # synthetic calls to the sound API. Original gameplay assertions stay intact.
    if mode in ["focused", "active"]:
        var bursts := events.filter(func(e): return e.kind == "burst")
        var attacks := audio_events.filter(func(e): return e.kind == "break" and not e.dropped)
        check("combat_audio_real_breaks_exercised", bursts.size() >= 2)
        check("combat_audio_once_per_same_tick_burst", attacks.size() == bursts.size() and bursts.all(func(b):
            return attacks.filter(func(a): return a.id == b.id and a.tick == b.engine_tick).size() == 1))
        var impacts := audio_events.filter(func(e): return e.kind == "impact" and not e.dropped)
        check("combat_audio_ground_impacts_exercised", not impacts.is_empty())
        check("combat_audio_impacts_same_tick_thresholded", impacts.all(func(a):
            return impact_sources.any(func(i): return i.id == a.id and i.tick == a.tick and i.speed >= 1.0)))
        check("combat_audio_eight_voice_bound", audio_events.all(func(a): return a.dropped or (a.active >= 1 and a.active <= 8)))
    var result := {"passed": failures.is_empty(), "scenario": mode, "checks": checks,
        "failures": failures, "ticks": tick, "health": session.player.health,
        "state": session.state, "events": events, "frames": frames,
        "audio_events": audio_events, "impact_sources": impact_sources,
        "engine": Engine.get_version_info(), "renderer": RenderingServer.get_video_adapter_name(),
        "visual_assessment": "UNASSESSED: no available image perception; files not visually inspected"}
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
    FileAccess.open(out.path_join("trace.json"), FileAccess.WRITE).store_string(JSON.stringify(trace))
    print("OPPOSITION_TEST_DONE scenario=", mode, " checks=", checks.size(), " failures=", failures.size(), " ticks=", tick, " health=", session.player.health)
    get_tree().quit(0 if failures.is_empty() else 1)
