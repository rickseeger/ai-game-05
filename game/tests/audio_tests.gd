extends Node
## Tests call production damage/burst/solver routing. Synthetic routing units are
## explicitly tagged and muted; the recording scenario uses actual rigid bodies.
var session: Node3D
var sound: Node3D
var debris: Node3D
var checks: Array[Dictionary] = []
var audio: Array[Dictionary] = []
var source: Array[Dictionary] = []
var timeline: Array[Dictionary] = []
var tick := 0
var running := false
var phase := "unit_muted"
var out := ""
var marker: ColorRect
var peak_bodies := 0
var peak_voices := 0
var last_source_impact_tick := -100
var body_ticks: Dictionary = {}
var fixture_targets: Array[Node3D] = []
var burst_expected := 0
var impact_actual := 0
var samples: FileAccess

func check(label: String, value: bool) -> void:
    checks.append({"name": label, "pass": value, "tick": tick})
    if not value:
        push_error("AUDIO_ASSERT " + label)

func stamp(kind: String, data: Dictionary = {}) -> Dictionary:
    data.merge({"kind": kind, "tick": tick, "engine_tick": Engine.get_physics_frames(),
        "frame": Engine.get_process_frames(), "phase": phase, "usec": Time.get_ticks_usec()}, true)
    return data

func run(owner: Node3D) -> void:
    session = owner
    sound = owner.sound
    debris = owner.debris
    out = OS.get_environment("AUDIO_OUT")
    process_physics_priority = -5
    sound.audio_event.connect(func(data: Dictionary):
        data["phase"] = phase
        data["scenario_tick"] = tick
        audio.append(data))
    debris.burst_started.connect(func(id: int, at: Vector3):
        burst_expected += 1
        source.append(stamp("break", {"id": id, "position": [at.x, at.y, at.z]})))
    debris.impact.connect(func(at: Vector3, speed: float, material: StringName, id: int):
        impact_actual += 1
        var contacts := -1
        var pending := -1.0
        for b in debris.bodies:
            if b.body_id == id:
                contacts = b.contact_count
                pending = b.pending_speed
        source.append(stamp("impact", {"id": id, "speed": speed, "material": material,
            "contacts": contacts, "pending_speed": pending, "position": [at.x, at.y, at.z]}))
        check("solver_contact_%d" % impact_actual, contacts > 0 and pending >= 1.0)
        var now := Engine.get_physics_frames()
        check("source_global_throttle_%d" % impact_actual, now - last_source_impact_tick >= 3)
        check("source_body_cooldown_%d" % impact_actual, now - int(body_ticks.get(id, -100)) >= 8)
        last_source_impact_tick = now
        body_ticks[id] = now)
    samples = FileAccess.open(out.path_join("frames.csv"), FileAccess.WRITE)
    samples.store_line("scenario_tick,engine_tick,frame,active_bodies,active_voices,phase")
    marker = ColorRect.new()
    marker.position = Vector2(1190, 120)
    marker.size = Vector2(32, 32)
    marker.color = Color.BLACK
    marker.mouse_filter = Control.MOUSE_FILTER_IGNORE
    session.hud.get_parent().add_child(marker)
    sound.set_levels(1, 1, true, false)
    sound.bind(debris) # binding twice must not duplicate connections
    check("eight_preallocated_voices", sound.voices.size() == 8)
    check("one_limiter_minus2db", AudioServer.get_bus_effect_count(sound.bus) == 1 and is_equal_approx(AudioServer.get_bus_effect(sound.bus, 0).ceiling_db, -2.0))
    var before := audio.size()
    sound.on_impact(Vector3.ZERO, 0.99, &"metal", 9001)
    sound.on_impact(Vector3.ZERO, NAN, &"metal", 9001)
    sound.on_impact(Vector3.ZERO, 4.0, &"unknown", 9001)
    check("reject_subthreshold_nan_unknown_material", audio.size() == before)
    sound.on_impact(Vector3.ZERO, 1.0, &"metal", 9001)
    check("accept_threshold_and_low_energy_gain", audio.size() == before + 1 and audio[-1].gain_db < -18)
    sound.on_impact(Vector3.ZERO, 9.0, &"metal", 9002)
    check("sound_defensive_global_throttle", audio.size() == before + 1)
    for i in 3:
        await get_tree().physics_frame
    sound.on_impact(Vector3.ZERO, 9.0, &"metal", 9001)
    check("sound_defensive_body_cooldown", audio.size() == before + 1)
    sound.on_impact(Vector3.ZERO, 9.0, &"metal", 9002)
    check("energy_changes_gain", audio.size() == before + 2 and audio[-1].gain_db > -10)
    sound.clear()
    var variants: Dictionary = {}
    var pitches: Dictionary = {}
    var previous := -1
    var no_repeat := true
    for i in 24:
        sound.on_burst(10000+i, Vector3.ZERO)
        variants[audio[-1].variant] = true
        pitches[audio[-1].pitch] = true
        no_repeat = no_repeat and previous != int(audio[-1].variant)
        previous = audio[-1].variant
    check("burst_variation_no_immediate_repeat", variants.size() == 4 and pitches.size() > 8 and no_repeat)
    check("crowded_voice_cap_and_steal", sound.active_count() == 8 and audio[-1].stolen)
    sound.on_impact(Vector3.ZERO, 9.0, &"metal", 9999)
    check("impacts_cannot_steal_break_attacks", audio[-1].dropped and sound.active_count() == 8)
    sound.clear()
    check("clear_stops_voices_and_routing_history", sound.active_count() == 0 and sound.body_ticks.is_empty())
    sound.set_levels(1, 0, false, false)
    check("zero_sfx_mutes_its_bus", AudioServer.is_bus_mute(sound.bus) and not AudioServer.is_bus_mute(0))
    sound.set_levels(-1, 2, false, false)
    check("levels_clamped_and_zero_master_mutes", sound.master == 0 and sound.sfx == 1 and AudioServer.is_bus_mute(0))
    sound.set_levels(0.65, 0.35, false, false)
    check("independent_master_sfx_levels", absf(db_to_linear(AudioServer.get_bus_volume_db(0))-.65) < .001 and absf(db_to_linear(AudioServer.get_bus_volume_db(sound.bus))-.35) < .001)
    sound.master_slider.value = 0.7
    sound.sfx_slider.value = 0.4
    check("actual_slider_signals", is_equal_approx(sound.master, .7) and is_equal_approx(sound.sfx, .4))
    var key := InputEventKey.new()
    key.physical_keycode = KEY_M
    key.pressed = true
    Input.parse_input_event(key)
    await get_tree().process_frame
    check("actual_M_key_mutes", sound.muted and AudioServer.is_bus_mute(0))
    sound.on_burst(19999, Vector3.ZERO)
    for i in 3:
        await get_tree().physics_frame
    session.pause(true)
    for i in 2:
        await get_tree().process_frame # allow queued mixer start/pause commands to settle
    var paused_position: float = sound.voices[0].get_playback_position()
    for i in 6:
        await get_tree().process_frame
    print("PAUSE_DIAGNOSTIC stream_paused=", sound.voices[0].stream_paused, " before=", paused_position, " after=", sound.voices[0].get_playback_position())
    check("pause_freezes_playback", sound.voices[0].stream_paused and is_equal_approx(sound.voices[0].get_playback_position(), paused_position))
    sound.mute_button.button_pressed = false
    check("mute_control_works_paused", not sound.muted and not AudioServer.is_bus_mute(0))
    session.pause(false)
    check("resume_unpauses_playback", not sound.voices[0].stream_paused)
    sound.clear()
    var saved := ConfigFile.new()
    check("settings_persisted", saved.load(sound.SETTINGS) == OK and is_equal_approx(saved.get_value("audio", "sfx", -1), .4) and not saved.get_value("audio", "muted", true))
    var shots_before: int = session.shots
    var mouse := InputEventMouseButton.new()
    mouse.button_index = MOUSE_BUTTON_LEFT
    mouse.position = sound.sfx_slider.global_position + sound.sfx_slider.size * .5
    mouse.pressed = true
    Input.parse_input_event(mouse)
    await get_tree().process_frame
    check("slider_click_does_not_fire", not session.controls.held.has("fire") and session.shots == shots_before)
    mouse.pressed = false
    Input.parse_input_event(mouse)
    sound.set_levels(.85, .85, false)
    sound.clear()
    phase = "initial_silence"
    running = true

func break_group(count: int) -> void:
    timeline.append(stamp("damage_group", {"count": count}))
    marker.color = Color.RED
    for target in fixture_targets:
        target.free()
    fixture_targets.clear()
    for i in count:
        var target = load("res://destructible_target.gd").new()
        target.entity_id = 2000 + tick * 20 + i
        target.event_seed = target.entity_id
        target.destruction = debris
        session.add_child(target)
        target.position = Vector3((i % 3 - 1) * 6, 0, -6 if i % 6 < 3 else 6)
        if count == 1:
            target.position = session.arena.pylon_spawns[2].origin
        fixture_targets.append(target)
        var before := burst_expected
        target.apply_damage(100, target.global_position, Vector3.UP)
        target.apply_damage(100, target.global_position, Vector3.UP)
        check("once_only_damage_%d" % target.entity_id, burst_expected == before + 1 and not is_instance_valid(target.intact))

func _physics_process(_dt: float) -> void:
    if not running:
        return
    tick += 1
    marker.color = Color.BLACK
    match tick:
        60:
            phase = "single_default"
            # Remove fixture duplicates so a new intact target occupies the actual spot.
            for t in session.targets:
                t.free()
            session.targets.clear()
            break_group(1)
        300, 360, 420:
            phase = "crowded_default"
            break_group(6)
        600:
            phase = "muted"
            debris.clear()
            sound.clear()
            sound.set_levels(1, 1, true, false)
            break_group(6)
        660, 780, 1020, 1260, 1500:
            debris.clear()
            sound.clear()
            phase = "silence"
        720:
            phase = "zero_master"
            sound.set_levels(0, 1, false, false)
            break_group(6)
        840:
            phase = "low_sfx"
            sound.set_levels(1, .25, false, false)
            break_group(1)
        1080:
            phase = "max_single"
            sound.set_levels(1, 1, false, false)
            break_group(1)
        1320:
            phase = "max_overload"
            break_group(12)
        1560:
            finish()
            return
    peak_bodies = maxi(peak_bodies, debris.bodies.size())
    peak_voices = maxi(peak_voices, sound.active_count())
    samples.store_line("%d,%d,%d,%d,%d,%s" % [tick, Engine.get_physics_frames(), Engine.get_process_frames(), debris.bodies.size(), sound.active_count(), phase])

func finish() -> void:
    running = false
    samples.close()
    check("physical_cap_exercised", peak_bodies == 192)
    check("audio_voice_cap_exercised", peak_voices == 8)
    check("eventual_voice_drain", sound.active_count() == 0)
    check("real_impacts_observed", impact_actual > 50)
    var variants: Dictionary = {}
    var prior := -1
    var no_repeat := true
    var matched := 0
    for e in audio:
        if e.phase == "unit_muted" or e.dropped:
            continue
        if e.kind == "impact":
            variants[e.variant] = true
            no_repeat = no_repeat and int(e.variant) != prior
            prior = int(e.variant)
        for s in source:
            if s.kind == e.kind and s.id == e.id and s.engine_tick == e.tick:
                matched += 1
                break
    var played := 0
    for e in audio:
        if e.phase != "unit_muted" and not e.dropped:
            played += 1
    check("every_runtime_voice_has_same_tick_source", matched == played)
    check("real_impact_sample_variation", variants.size() == 6 and no_repeat)
    var failures: Array = []
    for c in checks:
        if not c.pass:
            failures.append(c.name)
    var report := {"checks": checks, "failures": failures, "passed": failures.is_empty(), "audio": audio,
        "source": source, "timeline": timeline, "peak_bodies": peak_bodies, "peak_voices": peak_voices,
        "engine": Engine.get_version_info(), "driver": AudioServer.get_driver_name(),
        "device": AudioServer.output_device, "display": DisplayServer.get_name(),
        "renderer": RenderingServer.get_video_adapter_name(), "listening": "NOT performed: worker has no auditory perception; playback path is separate evidence"}
    FileAccess.open(out.path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(report, "  "))
    print("AUDIO_TEST_DONE checks=", checks.size(), " failures=", failures)
    get_tree().quit(0 if failures.is_empty() else 1)
