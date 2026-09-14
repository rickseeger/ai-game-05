extends Node3D
## All playback is downstream of accepted destruction signals. Never drives physics.
signal audio_event(data: Dictionary)
const VOICE_LIMIT := 8
const MIN_SPEED := 1.0
const SETTINGS := "user://sound.cfg"
var gameplay_input: Node
var voices: Array[AudioStreamPlayer3D] = []
var tags: Array[String] = []
var serials: Array[int] = []
var serial := 0
var break_assets: Array[AudioStream] = []
var impact_assets: Array[AudioStream] = []
var rng := RandomNumberGenerator.new()
var previous := {"break": -1, "impact": -1}
var last_tick := -100
var body_ticks: Dictionary = {}
var master := 0.85
var sfx := 0.85
var muted := false
var bus := -1
var ui: CanvasLayer
var master_slider: HSlider
var sfx_slider: HSlider
var mute_button: CheckButton

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS # controls still work while paused
    rng.seed = 50141
    for i in 4:
        break_assets.append(load("res://audio/break_%d.wav" % i))
    for i in 6:
        impact_assets.append(load("res://audio/impact_%d.wav" % i))
    # Dedicated bus owned by this service; no duplicated master effects on restart.
    AudioServer.add_bus()
    bus = AudioServer.bus_count - 1
    AudioServer.set_bus_name(bus, "DestructionSFX_%d" % get_instance_id())
    AudioServer.set_bus_send(bus, "Master")
    var limiter := AudioEffectHardLimiter.new()
    limiter.ceiling_db = -2.0
    limiter.pre_gain_db = 0.0
    limiter.release = 0.10
    AudioServer.add_bus_effect(bus, limiter)
    for i in VOICE_LIMIT:
        var voice := AudioStreamPlayer3D.new()
        voice.process_mode = Node.PROCESS_MODE_PAUSABLE
        voice.bus = AudioServer.get_bus_name(bus)
        # Arena camera is elevated: avoid making every fracture sound far away.
        voice.unit_size = 50.0
        voice.max_distance = 0.0 # inverse attenuation only, no second distance fade
        voice.max_db = 0.0
        voice.attenuation_filter_cutoff_hz = 14000.0
        add_child(voice)
        voices.append(voice)
        tags.append("")
        serials.append(-1)
    var config := ConfigFile.new()
    if config.load(SETTINGS) == OK:
        master = clampf(float(config.get_value("audio", "master", master)), 0, 1)
        sfx = clampf(float(config.get_value("audio", "sfx", sfx)), 0, 1)
        muted = bool(config.get_value("audio", "muted", muted))
    build_ui()
    apply_settings(false)
    print("SOUND_OUTPUT driver=", AudioServer.get_driver_name(), " device=", AudioServer.output_device,
        " (routing diagnostic, NOT proof of listening)")

func bind(service: Node3D) -> void:
    if not service.burst_started.is_connected(on_burst):
        service.burst_started.connect(on_burst)
        service.impact.connect(on_impact)

func build_ui() -> void:
    ui = CanvasLayer.new()
    add_child(ui)
    var panel := PanelContainer.new()
    panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
    panel.offset_left = -320
    panel.offset_top = -94
    panel.offset_right = -12
    panel.offset_bottom = -12
    ui.add_child(panel)
    var box := VBoxContainer.new()
    panel.add_child(box)
    for title in ["Master", "SFX [- / =]"]:
        var row := HBoxContainer.new()
        box.add_child(row)
        var label := Label.new()
        label.text = title
        label.custom_minimum_size.x = 116
        row.add_child(label)
        var slider := HSlider.new()
        slider.min_value = 0
        slider.max_value = 1
        slider.step = 0.05
        slider.custom_minimum_size.x = 175
        row.add_child(slider)
        slider.gui_input.connect(claim_pointer)
        if title == "Master":
            master_slider = slider
            slider.value_changed.connect(func(value: float): set_levels(value, sfx, muted))
        else:
            sfx_slider = slider
            slider.value_changed.connect(func(value: float): set_levels(master, value, muted))
    mute_button = CheckButton.new()
    mute_button.text = "Mute [M]"
    box.add_child(mute_button)
    mute_button.gui_input.connect(claim_pointer)
    mute_button.toggled.connect(func(value: bool): set_levels(master, sfx, value))

func claim_pointer(event: InputEvent) -> void:
    # The existing input collector runs before GUI dispatch. A settings click
    # must not also leave its LMB fire latch held during live play.
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and is_instance_valid(gameplay_input):
        gameplay_input.held.erase("fire")

func set_levels(master_value: float, sfx_value: float, mute_value: bool, persist := true) -> void:
    master = clampf(master_value, 0, 1)
    sfx = clampf(sfx_value, 0, 1)
    muted = mute_value
    apply_settings(persist)

func apply_settings(persist: bool) -> void:
    AudioServer.set_bus_volume_db(0, linear_to_db(master) if master > 0 else -80.0)
    AudioServer.set_bus_mute(0, muted or master == 0)
    AudioServer.set_bus_volume_db(bus, linear_to_db(sfx) if sfx > 0 else -80.0)
    AudioServer.set_bus_mute(bus, sfx == 0)
    master_slider.set_value_no_signal(master)
    sfx_slider.set_value_no_signal(sfx)
    mute_button.set_pressed_no_signal(muted)
    if persist:
        var config := ConfigFile.new()
        config.set_value("audio", "master", master)
        config.set_value("audio", "sfx", sfx)
        config.set_value("audio", "muted", muted)
        var error := config.save(SETTINGS)
        if error != OK:
            push_warning("Audio settings could not be saved: %d" % error)

func _unhandled_key_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        match event.physical_keycode:
            KEY_M: set_levels(master, sfx, not muted)
            KEY_MINUS: set_levels(master, sfx - 0.05, muted)
            KEY_EQUAL: set_levels(master, sfx + 0.05, muted)
            _: return
        get_viewport().set_input_as_handled()

func active_count() -> int:
    var count := 0
    for voice in voices:
        count += int(voice.playing)
    return count

func choose_variant(kind: String, count: int) -> int:
    # Uniform choice excluding the immediately previous sample, not a short fixed loop.
    var choice := rng.randi_range(0, count - 2)
    if choice >= int(previous[kind]):
        choice += 1
    previous[kind] = choice
    return choice

func on_burst(id: int, at: Vector3) -> void:
    play_event("break", at, 1.0, id)

func on_impact(at: Vector3, speed: float, material: StringName, body_id: int) -> void:
    var tick := Engine.get_physics_frames()
    if material != &"metal" or not is_finite(speed) or speed < MIN_SPEED:
        return
    if tick - last_tick < 3 or tick - int(body_ticks.get(body_id, -100)) < 8:
        return
    last_tick = tick
    body_ticks[body_id] = tick
    # Short-lived routing history remains bounded even across unlimited body IDs.
    for id in body_ticks.keys():
        if tick - int(body_ticks[id]) > 8:
            body_ticks.erase(id)
    play_event("impact", at, clampf((speed * speed) / 64.0, 0.08, 1.0), body_id)

func play_event(kind: String, at: Vector3, energy: float, id: int) -> void:
    var slot := -1
    for i in voices.size():
        if not voices[i].playing:
            slot = i
            break
    if slot == -1:
        # Impact cannot steal a fracture attack. Prefer oldest impact for any steal.
        for i in voices.size():
            if tags[i] == "impact" and (slot == -1 or serials[i] < serials[slot]):
                slot = i
        if slot == -1 and kind == "break":
            slot = serials.find(serials.min())
    if slot == -1:
        audio_event.emit({"kind": kind, "id": id, "dropped": true, "tick": Engine.get_physics_frames()})
        return
    var assets: Array[AudioStream] = break_assets if kind == "break" else impact_assets
    var variant := choose_variant(kind, assets.size())
    var voice := voices[slot]
    var stolen := voice.playing
    voice.stop()
    voice.stream = assets[variant]
    voice.global_position = at
    voice.pitch_scale = rng.randf_range(0.94, 1.06) if kind == "break" else rng.randf_range(0.90, 1.12) * lerpf(0.90, 1.06, energy)
    voice.volume_db = -1.0 if kind == "break" else lerpf(-23.0, -7.0, sqrt(energy))
    tags[slot] = kind
    serials[slot] = serial
    serial += 1
    voice.play()
    audio_event.emit({"kind": kind, "id": id, "tick": Engine.get_physics_frames(),
        "frame": Engine.get_process_frames(), "usec": Time.get_ticks_usec(), "variant": variant,
        "pitch": voice.pitch_scale, "gain_db": voice.volume_db, "energy": energy,
        "slot": slot, "active": active_count(), "stolen": stolen, "dropped": false})

func clear() -> void:
    for voice in voices:
        voice.stop()
    body_ticks.clear()
    last_tick = -100

func _exit_tree() -> void:
    clear()
    if bus > 0:
        AudioServer.remove_bus(bus)
