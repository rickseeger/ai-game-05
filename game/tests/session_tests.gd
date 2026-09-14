extends SceneTree
## ISOLATED production-rule fixtures, not a natural full-session route.
## Position/clock injection and frozen threats are explicit isolation only.
var session: Node3D
var checks: Array[Dictionary] = []
var events: Array[Dictionary] = []
var scenario := ""
var out := ""
var shooter: StaticBody3D

func _initialize() -> void:
    out = OS.get_environment("SESSION_OUT")
    call_deferred("run")

func check(label: String, condition: bool) -> void:
    checks.append({"name": label, "pass": condition, "scenario": scenario})
    print("SESSION_ASSERT ", label, " ", "PASS" if condition else "FAIL")
    if not condition:
        push_error("SESSION_ASSERT " + label)

func record(kind: String, data: Dictionary = {}) -> void:
    events.append({"kind": kind, "data": data.duplicate(true), "scenario": scenario,
        "tick": Engine.get_physics_frames(), "state": session.state,
        "health": session.player.health, "elapsed": session.elapsed,
        "remaining": session.remaining_pylons()})

func reset(label: String) -> void:
    scenario = label
    session.start(1201)
    session.set_physics_process(false)
    session.opposition.clear()
    session.opposition.set_physics_process(false)
    session.player.set_physics_process(false)
    session.player.died.connect(func(): record("died"))
    for target in session.targets:
        target.destroyed.connect(func(id, _at, kind, _seed): record("destroyed", {"id": id, "kind": kind}))

func exit_center() -> Vector3:
    return (session.arena.global_transform * session.arena.exit_transform).origin

func destroy_target(index: int) -> void:
    session.targets[index].apply_damage(100, Vector3.ZERO, Vector3.FORWARD)

func unlock() -> void:
    for i in 3:
        destroy_target(i)

func frames(count: int) -> void:
    for i in count:
        await physics_frame
        await process_frame

func snapshot() -> Dictionary:
    return {"state": session.state, "elapsed": session.elapsed,
        "remaining": session.remaining_pylons(), "reason": session.loss_reason}

func run() -> void:
    session = load("res://opposition.tscn").instantiate()
    root.add_child(session)
    session.state_changed.connect(func(state): record("state", {"value": state}))
    session.objectives_changed.connect(func(remaining): record("progress", {"remaining": remaining}))
    session.combat.event.connect(func(kind, data): record("combat_" + kind, data))
    session.debris.burst_started.connect(func(id, _at): record("burst", {"id": id, "bodies": session.debris.bodies.size()}))
    session.sound.audio_event.connect(func(data): record("audio", data))
    shooter = StaticBody3D.new()
    shooter.collision_layer = 0
    shooter.collision_mask = 0
    session.add_child(shooter)
    reset("progress_and_radius")
    check("rendered_X11", DisplayServer.get_name() == "X11")
    check("production_priority_after_player_and_combat", session.process_physics_priority > session.combat.process_physics_priority and session.combat.process_physics_priority > session.player.process_physics_priority)
    check("exact_three_registered_pylons", session.targets.size() == 3 and session.remaining_pylons() == 3)
    session.player.global_position = exit_center()
    session.resolve_tick()
    check("locked_exit_rejects_entry", session.state == session.State.PLAYING and not session.extraction_unlocked())
    session.targets[0].destroyed.emit(1, Transform3D.IDENTITY, &"pylon", 0)
    session.on_target_destroyed(999, Transform3D.IDENTITY, &"pylon", 0)
    check("alive_and_unknown_events_ignored", session.remaining_pylons() == 3)
    destroy_target(2)
    var before := events.size()
    session.targets[2].apply_damage(100, Vector3.ZERO, Vector3.ZERO)
    check("target_itself_emits_once", events.size() == before)
    for i in 5:
        session.targets[2].destroyed.emit(3, Transform3D.IDENTITY, &"pylon", 0)
    check("duplicate_delivery_counts_once", session.remaining_pylons() == 2 and events.slice(before).filter(func(e): return e.kind == "progress").is_empty())
    session.on_target_destroyed(2, Transform3D.IDENTITY, &"sentinel", 0)
    check("enemy_deaths_do_not_count", session.remaining_pylons() == 2)
    destroy_target(0)
    session.resolve_tick()
    check("two_pylons_still_locked", session.remaining_pylons() == 1 and session.state == session.State.PLAYING)
    session.player.global_position = exit_center() + Vector3(1.501, 0, 0)
    destroy_target(1)
    session.resolve_tick()
    check("third_unlocks_not_remote_victory", session.extraction_unlocked() and session.state == session.State.PLAYING)
    check("progress_notifications_3_2_1_0", events.filter(func(e): return e.scenario == scenario and e.kind == "progress").map(func(e): return e.data.remaining) == [3, 2, 1, 0])
    session.player.global_position = exit_center() + Vector3(1.5, 0, 0)
    session.resolve_tick()
    check("radius_boundary_wins", session.state == session.State.WON)
    var stable := snapshot()
    before = events.size()
    session.player.apply_damage(100, Vector3.ZERO)
    session.targets[0].destroyed.emit(1, Transform3D.IDENTITY, &"pylon", 0)
    session.finish(session.State.LOST)
    session.pause(false)
    for i in 5:
        session._physics_process(200.0)
        session.resolve_tick()
    check("won_terminal_idempotent", snapshot() == stable and events.slice(before).filter(func(e): return e.kind in ["state", "progress"]).is_empty())

    reset("death")
    session.player.apply_damage(100, Vector3.ZERO)
    check("death_does_not_finish_inside_damage", session.state == session.State.PLAYING)
    session.resolve_tick()
    check("death_loses_after_damage", session.state == session.State.LOST and session.loss_reason == "death")
    stable = snapshot()
    before = events.size()
    unlock()
    session.player.global_position = exit_center()
    session.finish(session.State.WON)
    session.pause(false)
    session._physics_process(20.0)
    session.resolve_tick()
    check("lost_terminal_ignores_late_progress_and_win", snapshot() == stable and events.slice(before).filter(func(e): return e.kind in ["state", "progress"]).is_empty())

    reset("deadline_steps")
    for i in 8999:
        session._physics_process(1.0 / 60.0)
    check("8999_ticks_still_playing", session.state == session.State.PLAYING and session.elapsed < 150.0)
    record("before_deadline")
    session._physics_process(1.0 / 60.0)
    check("9000_ticks_timeout_exactly", session.state == session.State.LOST and session.elapsed == 150.0 and session.loss_reason == "timeout")
    reset("deadline_epsilon")
    session.elapsed = 150.0 - 0.0000001
    session.resolve_tick()
    check("no_early_epsilon_loss", session.state == session.State.PLAYING)
    session.elapsed = 150.0
    session.resolve_tick()
    check("exact_deadline_loses", session.state == session.State.LOST)
    reset("deadline_overshoot")
    session.elapsed = 149.99
    session._physics_process(0.02)
    check("deadline_crossing_loses", session.state == session.State.LOST)
    reset("timeout_beats_win")
    unlock()
    session.player.global_position = exit_center()
    session.elapsed = 150.0
    session.resolve_tick()
    check("timeout_beats_extraction", session.state == session.State.LOST and session.loss_reason == "timeout")
    reset("just_before_deadline_win")
    unlock()
    session.player.global_position = exit_center()
    session.elapsed = 150.0 - 0.0000001
    session.resolve_tick()
    check("just_before_deadline_can_win", session.state == session.State.WON)

    reset("pause_real_engine")
    session.set_physics_process(true)
    session.opposition.set_physics_process(true)
    session.opposition.start(1201)
    await frames(3)
    session.pause(true)
    var clock: float = session.elapsed
    var threat_clock: float = session.opposition.elapsed
    var warning: float = session.opposition.pending[0].left
    await frames(10)
    session._physics_process(200.0) # State guard also protects explicit calls.
    session.resolve_tick()
    check("pause_freezes_clock_and_threats", session.elapsed == clock and session.opposition.elapsed == threat_clock and session.opposition.pending[0].left == warning and session.state == session.State.PAUSED)
    session.pause(false)
    await frames(3)
    check("resume_advances_active_clock", session.elapsed > clock and session.opposition.elapsed > threat_clock)

    # Real swept combat -> target -> fragments -> sound -> objectives. Test places
    # actors and emits bolts through production on_fired; not an input-driven run.
    reset("combat_progression")
    session.set_physics_process(true)
    for i in 3:
        var target = session.targets[i]
        session.player.global_position = target.global_position + Vector3(0, 0, 2)
        await frames(2)
        for shot in 4:
            session.on_fired(session.player.global_position + Vector3(0, 0.65, -0.25), Vector3.FORWARD)
            await frames(21)
            check("pylon_%d_shot_%d_health" % [i, shot], target.health == maxi(0, 100 - (shot + 1) * 25))
        check("pylon_%d_cover_removed" % i, target.is_destroyed and not is_instance_valid(target.intact))
        check("pylon_%d_real_fragments" % i, session.debris.bodies.filter(func(b): return b.event_id == session.debris.next_event - 1).size() == 32)
    check("combat_three_distinct_unlock", session.remaining_pylons() == 0 and session.state == session.State.PLAYING)
    var bursts := events.filter(func(e): return e.scenario == scenario and e.kind == "burst")
    var audio := events.filter(func(e): return e.scenario == scenario and e.kind == "audio" and e.data.kind == "break" and not e.data.dropped)
    check("combat_bursts_sound_same_tick", bursts.size() == 3 and audio.size() == 3 and bursts.all(func(b): return audio.any(func(a): return a.tick == b.tick and a.data.id == b.data.id)))
    check("solver_impacts_reach_sound", events.any(func(e): return e.scenario == scenario and e.kind == "audio" and e.data.kind == "impact" and not e.data.dropped))
    session.player.global_position = exit_center()
    await frames(2)
    check("combat_progress_then_entry_wins", session.state == session.State.WON)
    await RenderingServer.frame_post_draw
    check("render_capture_saved", root.get_texture().get_image().save_png(out.path_join("combat-victory-fixture.png")) == OK)

    # Both insertion orders must finish ALL damage first, not pause inside died.
    for hostile_first in [false, true]:
        reset("same_tick_hostile_first_" + str(hostile_first))
        destroy_target(0)
        destroy_target(1)
        session.targets[2].apply_damage(75, Vector3.ZERO, Vector3.FORWARD)
        session.player.global_position = exit_center()
        session.player.apply_damage(85, Vector3.ZERO)
        await frames(2) # Register the teleported player in the real physics space.
        var pylon_origin: Vector3 = session.targets[2].global_position + Vector3(0, 0.65, 0.8)
        var hostile_origin := exit_center() + Vector3(0, 0.65, 0.5)
        if hostile_first:
            session.combat.spawn_bolt(shooter, hostile_origin, Vector3.FORWARD, 15)
        session.on_fired(pylon_origin, Vector3.FORWARD)
        if not hostile_first:
            session.combat.spawn_bolt(shooter, hostile_origin, Vector3.FORWARD, 15)
        session.set_physics_process(true)
        await frames(2)
        check("same_tick_all_damage_processed_" + str(hostile_first), session.player.health == 0 and session.remaining_pylons() == 0 and session.combat.bolts.is_empty())
        check("same_tick_loss_beats_victory_" + str(hostile_first), session.state == session.State.LOST and session.loss_reason == "death")
        var deaths := events.filter(func(e): return e.scenario == scenario and e.kind == "died")
        var progress := events.filter(func(e): return e.scenario == scenario and e.kind == "progress" and e.data.remaining == 0)
        var terminal := events.filter(func(e): return e.scenario == scenario and e.kind == "state" and e.data.value == session.State.LOST)
        check("same_engine_tick_order_" + str(hostile_first), deaths.size() == 1 and progress.size() == 1 and terminal.size() == 1 and deaths[0].tick == progress[0].tick and deaths[0].tick == terminal[0].tick and deaths[0].state == session.State.PLAYING and progress[0].state == session.State.PLAYING and events.find(terminal[0]) > events.find(deaths[0]) and events.find(terminal[0]) > events.find(progress[0]))

    # Production tick at the deadline still processes gameplay damage before loss.
    reset("deadline_damage_order")
    session.targets[0].apply_damage(75, Vector3.ZERO, Vector3.FORWARD)
    await frames(2)
    session.on_fired(session.targets[0].global_position + Vector3(0, 0.65, 0.8), Vector3.FORWARD)
    session.elapsed = 150.0 - 1.0 / 60.0
    session.set_physics_process(true)
    await frames(2)
    check("deadline_tick_damage_before_timeout", session.remaining_pylons() == 2 and session.state == session.State.LOST and session.loss_reason == "timeout")
    var failed := checks.filter(func(c): return not c.pass)
    var result := {"passed": failed.is_empty(), "checks": checks, "events": events,
        "engine": Engine.get_version_info(), "renderer": RenderingServer.get_video_adapter_name(),
        "scope": "Isolated production session fixtures with actor/clock injection and frozen threats; NOT natural full-session play or subjective quality."}
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(result, "  "))
    print("SESSION_TEST_DONE checks=", checks.size(), " failures=", failed.size())
    paused = false
    session.queue_free()
    await process_frame
    quit(0 if failed.is_empty() else 1)
