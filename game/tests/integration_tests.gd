extends Node
## Default-entry integration. Terminal setup is an explicitly forced fixture,
## NEVER a natural victory. Pause, movement, firing, dash and R use InputEvents.
signal after_tick
var scene: Node3D
var out := ""
var checks: Array[Dictionary] = []
var snapshots: Array[Dictionary] = []
var events: Array[Dictionary] = []
var phase := "default_launch"
var initial_nodes := 0
var initial_buses := 0
var progress_events := 0
var state_events := 0
var replace_events := 0

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS
    process_physics_priority = 100

func _physics_process(_dt: float) -> void:
    after_tick.emit()

func steps(n: int) -> void:
    for i in n:
        await after_tick

func check(label: String, value: bool) -> void:
    checks.append({"phase": phase, "name": label, "pass": value})
    print("INTEGRATION_ASSERT ", phase, " / ", label, " ", "PASS" if value else "FAIL")
    if not value:
        push_error(label)

func key(code: Key, pressed: bool, echo_value := false) -> void:
    var e := InputEventKey.new()
    e.physical_keycode = code
    e.pressed = pressed
    e.echo = echo_value
    Input.parse_input_event(e)
    events.append({"kind": "input_key", "phase": phase, "tick": Engine.get_physics_frames(), "code": code, "pressed": pressed, "echo": echo_value})

func tap(code: Key) -> void:
    key(code, true)
    key(code, false)

func mouse(at: Vector2) -> void:
    var e := InputEventMouseMotion.new()
    e.position = at
    e.global_position = at
    Input.parse_input_event(e)

func button(pressed: bool) -> void:
    var e := InputEventMouseButton.new()
    e.position = scene.controls.pointer
    e.global_position = e.position
    e.button_index = MOUSE_BUTTON_LEFT
    e.pressed = pressed
    Input.parse_input_event(e)

func v(a: Vector3) -> Array:
    return [a.x, a.y, a.z]

func count_nodes(n: Node) -> int:
    var result := 1
    for child in n.get_children():
        result += count_nodes(child)
    return result

func rect(c: Control) -> Array:
    var r := c.get_global_rect()
    return [r.position.x, r.position.y, r.size.x, r.size.y]

func snapshot(label: String) -> Dictionary:
    var p = scene.player
    var t: Array = []
    for target in scene.targets:
        t.append({"id": target.entity_id, "health": target.health, "destroyed": target.is_destroyed,
            "intact": is_instance_valid(target.intact), "callbacks": target.destroyed.get_connections().size()})
    var voices: Array = []
    for voice in scene.sound.voices:
        voices.append(voice.playing)
    var s := {"label": label, "phase": phase, "tick": Engine.get_physics_frames(),
        "state": scene.state, "generation": scene.generation, "elapsed": scene.elapsed,
        "clock_error": scene._clock_error, "health": p.health, "loss_reason": scene.loss_reason,
        "remaining": scene.remaining_pylons(), "unlocked": scene.extraction_unlocked(),
        "marker": scene.arena.extraction_label.text, "position": v(p.global_position),
        "velocity": v(p.velocity), "aim_valid": p.aim_valid, "pointer_known": scene.controls.pointer_known,
        "pointer": [scene.controls.pointer.x, scene.controls.pointer.y], "held": scene.controls.held.keys(),
        "dash_edge": scene.controls.dash_edge, "input_enabled": scene.controls.enabled,
        "fire_remaining": p.fire_remaining, "dash_remaining": p.dash_remaining,
        "shots": scene.shots, "shot_count": p.shot_count, "dash_count": p.dash_count,
        "targets": t, "bolts": scene.combat.bolts.size(), "bolt_visuals": scene.combat.get_child_count(),
        "bodies": scene.debris.bodies.size(), "rendered_bodies": scene.debris.batch.multimesh.visible_instance_count,
        "voices": voices, "audio_history": scene.sound.body_ticks.size(),
        "sentries": scene.opposition.sentries.size(), "pending": scene.opposition.pending.map(func(w): return {"id": w.id, "left": w.left, "position": v(w.position)}),
        "opposition_elapsed": scene.opposition.elapsed, "next_spawn": scene.opposition.next_spawn,
        "nodes": count_nodes(scene), "buses": AudioServer.bus_count,
        "player_callbacks": p.fired.get_connections().size(),
        "burst_callbacks": scene.debris.burst_started.get_connections().size(),
        "impact_callbacks": scene.debris.impact.get_connections().size(),
        "pause_callbacks": scene.controls.pause_requested.get_connections().size(),
        "restart_callbacks": scene.controls.restart_requested.get_connections().size(),
        "hud": scene.hud.text, "message": scene.message.text, "panel_visible": scene.panel.visible,
        "paused": get_tree().paused, "hud_rect": rect(scene.hud), "panel_rect": rect(scene.panel)}
    snapshots.append(s)
    return s

func capture(label: String) -> void:
    await RenderingServer.frame_post_draw
    check("capture_" + label, get_viewport().get_texture().get_image().save_png(out.path_join(label + ".png")) == OK)
    snapshot(label)

func on_state(value: int) -> void:
    state_events += 1
    events.append({"kind": "state", "value": value, "phase": phase, "remaining": scene.remaining_pylons(), "elapsed": scene.elapsed, "tick": Engine.get_physics_frames()})

func on_progress(value: int) -> void:
    progress_events += 1
    events.append({"kind": "progress", "value": value, "phase": phase, "tick": Engine.get_physics_frames()})

func verify_reset(old_ids: Array, expected_generation: int) -> void:
    var s := snapshot("reset")
    check("fresh_player_clock_and_input", s.health == 100 and s.elapsed == 0 and s.clock_error == 0 and s.generation == expected_generation and s.state == scene.State.PLAYING and s.input_enabled and not s.paused and s.held.is_empty() and not s.dash_edge and not s.pointer_known and s.pointer == [0.0, 0.0] and not s.aim_valid and s.velocity == [0.0, 0.0, 0.0] and s.position == v(scene.arena.player_spawn.origin))
    check("cooldowns_shots_and_damage_feedback_reset", s.dash_remaining == 0 and s.fire_remaining == 0 and s.shots == 0 and s.shot_count == 0 and s.dash_count == 0 and scene.player.hit_flash == 0 and not scene.player.hit_indicator.visible)
    check("three_fresh_solid_pylons_and_locked_exit", s.remaining == 3 and not s.unlocked and s.loss_reason == "" and s.marker == "EXTRACT [LOCKED]" and s.targets.size() == 3 and s.targets.all(func(t): return t.health == 100 and not t.destroyed and t.intact and t.callbacks == 1))
    check("prior_objects_freed", old_ids.all(func(id): return not is_instance_id_valid(id)))
    check("bolts_debris_voices_cleared_immediately", s.bolts == 0 and s.bolt_visuals == 0 and s.bodies == 0 and s.rendered_bodies == 0 and s.audio_history == 0 and not s.voices.any(func(playing): return playing))
    check("opposition_seed_clock_warnings_restored", s.sentries == 0 and s.pending.size() == 2 and s.pending[0].id == 100 and s.pending[1].id == 101 and s.pending.all(func(w): return w.left == 1.0) and s.opposition_elapsed == 0 and s.next_spawn == 15.0)
    check("no_node_bus_or_callback_growth", s.nodes == initial_nodes and s.buses == initial_buses and s.player_callbacks == 1 and s.burst_callbacks == 1 and s.impact_callbacks == 1 and s.pause_callbacks == 1 and s.restart_callbacks == 1)
    check("hud_reset_before_return", "Pylons: 0 / 3" in s.hud and "LOCKED" in s.hud and "Time: 2:30" in s.hud and "Health: 100 / 100" in s.hud and "Dash: READY" in s.hud and not s.panel_visible)

func run(session: Node3D) -> void:
    scene = session
    out = OS.get_environment("INTEGRATION_OUT")
    initial_nodes = count_nodes(scene)
    initial_buses = AudioServer.bus_count
    scene.state_changed.connect(on_state)
    scene.objectives_changed.connect(on_progress)
    scene.player_replaced.connect(func(_p): replace_events += 1)
    scene.combat.event.connect(func(kind, data): events.append({"kind": "combat_" + kind, "data": data, "phase": phase, "tick": Engine.get_physics_frames()}))
    scene.sound.audio_event.connect(func(data): events.append({"kind": "audio", "data": data, "phase": phase, "tick": Engine.get_physics_frames()}))
    check("actual_default_main_scene", get_tree().current_scene == scene and scene.scene_file_path == ProjectSettings.get_setting("application/run/main_scene") and scene.scene_file_path == "res://opposition.tscn")
    check("linux_rendered_production_services", OS.get_name() == "Linux" and DisplayServer.get_name() == "X11" and scene.combat.get_script().resource_path == "res://combat.gd" and scene.debris.get_script().resource_path == "res://destruction.gd" and scene.sound.get_script().resource_path == "res://sound.gd" and scene.opposition.get_script().resource_path == "res://opposition.gd")
    snapshot("launch")
    await steps(3)
    await capture("default-playing")
    var gen: int = scene.generation
    tap(KEY_R)
    check("R_ignored_while_playing", scene.generation == gen)
    # Real default spawn -> ground aim -> four ordinary LMB hits on nearby P3.
    mouse(scene.camera.unproject_position(scene.targets[2].global_position))
    button(true)
    await steps(80)
    button(false)
    check("normal_input_combat_destroys_pylon_and_routes_sound", scene.targets[2].is_destroyed and scene.remaining_pylons() == 2 and scene.debris.bodies.size() == 32 and events.any(func(e): return e.kind == "audio" and e.data.kind == "break" and not e.data.dropped))
    check("production_opposition_spawns", scene.opposition.sentries.size() == 2)
    mouse(scene.camera.unproject_position(Vector3(8, 0, 8)))
    key(KEY_A, true)
    key(KEY_SPACE, true)
    button(true)
    await steps(2)
    tap(KEY_ESCAPE)
    var frozen := snapshot("pause-start")
    check("pause_hud_live_bindings", frozen.paused and frozen.panel_visible and "PAUSED" in frozen.message and "Pylons: 1 / 3" in frozen.hud and "Dash: READY" not in frozen.hud and "Sentries: 2" in frozen.hud)
    tap(KEY_R)
    key(KEY_ESCAPE, true, true)
    key(KEY_D, true)
    await steps(20)
    var later := snapshot("pause-end")
    check("pause_freezes_all_active_timers_and_world", scene.generation == gen and later.elapsed == frozen.elapsed and later.opposition_elapsed == frozen.opposition_elapsed and later.position == frozen.position and later.fire_remaining == frozen.fire_remaining and later.dash_remaining == frozen.dash_remaining and later.bodies == frozen.bodies and later.state == scene.State.PAUSED)
    await capture("paused-visible")
    scene.hud.visible = false
    await capture("paused-hud-hidden")
    scene.hud.visible = true
    scene.panel.visible = false
    await capture("paused-panel-hidden")
    scene.panel.visible = true
    await capture("paused-restored")
    scene.panel.visible = false
    await capture("extraction-locked")
    scene.arena.extraction_marker.visible = false
    await capture("locked-marker-hidden")
    scene.arena.extraction_marker.visible = true
    await capture("locked-marker-restored")
    scene.panel.visible = true
    get_window().size = Vector2i(960, 720)
    await steps(3)
    await capture("paused-4x3")
    check("hud_and_panel_fit_4x3", scene.hud.get_global_rect().end.x <= 960 and scene.hud.get_global_rect().end.y < scene.panel.get_global_rect().position.y and scene.panel.get_global_rect().end.x <= 960 and scene.panel.get_global_rect().end.y < 600)
    get_window().size = Vector2i(1280, 720)
    tap(KEY_ESCAPE)
    await steps(3)
    check("resume_advances_without_resurrecting_held_controls", scene.state == scene.State.PLAYING and scene.elapsed > frozen.elapsed and scene.opposition.elapsed > frozen.opposition_elapsed and scene.controls.held.is_empty() and scene.player.shot_count == frozen.shot_count and scene.player.global_position.distance_to(Vector3(frozen.position[0], frozen.position[1], frozen.position[2])) < 0.002)
    key(KEY_A, false)
    key(KEY_D, false)
    key(KEY_SPACE, false)
    button(false)

    for cycle in 6:
        phase = "forced_terminal_cycle_%d" % cycle
        var mode: String = ["victory", "death", "timeout"][cycle % 3]
        await steps(65) # Real opposition always active; wait for fresh warning spawns.
        check("retry_has_live_opposition", scene.opposition.sentries.size() >= 2)
        # Fixtures deliberately dirty every reset domain. No bypass claims.
        scene.player.apply_damage(15, Vector3(8, 0, 0))
        scene.player.dash_remaining = 1.25
        scene.player.fire_remaining = 0.2
        scene.elapsed = 42.0
        for target in scene.targets:
            if not target.is_destroyed:
                target.apply_damage(100, Vector3.ZERO, Vector3.FORWARD)
        scene.on_fired(scene.player.global_position + Vector3.UP, Vector3.LEFT)
        scene.controls.held["move_up"] = true
        scene.controls.held["fire"] = true
        scene.controls.dash_edge = true
        scene.controls.pointer_known = true
        scene.controls.pointer = Vector2(350, 400)
        scene.player.global_position = (scene.arena.global_transform * scene.arena.exit_transform).origin
        check("fixture_dirty_live_domains", scene.remaining_pylons() == 0 and scene.debris.bodies.size() >= 64 and scene.combat.bolts.size() > 0 and scene.sound.active_count() > 0)
        if mode == "death":
            scene.player.apply_damage(100, Vector3.ZERO)
        elif mode == "timeout":
            scene.elapsed = 150.0
        var before: int = state_events
        scene.resolve_tick()
        check("terminal_correct_and_single_callback", state_events == before + 1 and scene.state == (scene.State.WON if mode == "victory" else scene.State.LOST) and get_tree().paused and scene.panel.visible and "R to retry" in scene.message.text and ("VICTORY" if mode == "victory" else "DEFEAT") in scene.message.text)
        check("terminal_health_time_reason_hud", ("Health: %d / 100" % scene.player.health) in scene.hud.text and (mode != "timeout" or ("Time: 0:00" in scene.hud.text and "time ran out" in scene.message.text)) and (mode != "death" or "health depleted" in scene.message.text))
        scene.resolve_tick()
        tap(KEY_ESCAPE)
        check("terminal_idempotent_and_cannot_resume", state_events == before + 1 and get_tree().paused)
        if cycle < 3:
            await capture(mode + "-fixture")
            if cycle == 0:
                scene.panel.visible = false
                await capture("extraction-open-fixture")
                scene.arena.extraction_marker.visible = false
                await capture("victory-marker-hidden")
                scene.arena.extraction_marker.visible = true
                await capture("victory-marker-restored")
                scene.panel.visible = true
        var old_ids: Array = [scene.player.get_instance_id()]
        for target in scene.targets:
            old_ids.append(target.get_instance_id())
        for sentry in scene.opposition.sentries:
            old_ids.append(sentry.get_instance_id())
        for body in scene.debris.bodies:
            old_ids.append(body.get_instance_id())
        for bolt in scene.combat.bolts:
            old_ids.append(bolt.visual.get_instance_id())
        var expected_gen: int = scene.generation + 1
        var prev_progress := progress_events
        var prev_replace := replace_events
        before = state_events
        tap(KEY_R)
        verify_reset(old_ids, expected_gen)
        check("exactly_one_reset_notification_each", progress_events == prev_progress + 1 and state_events == before + 1 and replace_events == prev_replace + 1)
        check("playing_observers_see_complete_reset", events.filter(func(e): return e.kind == "state")[-1].remaining == 3 and events.filter(func(e): return e.kind == "state")[-1].elapsed == 0)
        await steps(3)
        check("no_stale_fire_or_dash_after_retry", scene.player.shot_count == 0 and scene.player.dash_count == 0 and scene.combat.bolts.is_empty() and scene.player.health == 100 and scene.sound.active_count() == 0)
        mouse(scene.camera.unproject_position(Vector3(8, 0, 8)))
        key(KEY_D, true)
        button(true)
        var at: Vector3 = scene.player.global_position
        await steps(2)
        key(KEY_D, false)
        button(false)
        check("fresh_input_moves_and_fires_once_after_retry", scene.player.global_position.x > at.x and scene.player.shot_count == 1 and scene.shots == 1 and scene.combat.bolts.size() == 1)
        snapshot("replay-live")
    phase = "final_replay"
    tap(KEY_ESCAPE)
    await capture("final-retry-paused")
    var failed := checks.filter(func(c): return not c.pass)
    var result := {"passed": failed.is_empty(), "checks": checks, "snapshots": snapshots, "events": events,
        "engine": Engine.get_version_info(), "renderer": RenderingServer.get_video_adapter_name(),
        "scope": "Actual default entry; ordinary InputEvents for initial pylon and controls, forced terminal fixtures for six repeated victory/death/timeout resets. NOT natural full-session victories or subjective quality."}
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
    print("INTEGRATION_DONE checks=", checks.size(), " failures=", failed.size())
    get_tree().paused = false
    get_tree().quit(0 if failed.is_empty() else 1)
