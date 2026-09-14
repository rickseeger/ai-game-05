extends SceneTree
## Paired actual damage events at arena positions, not synthesized capture data.
## Identical seed/sample/pitch isolate the production mixer distance/pan response.
var events: Array[Dictionary] = []
var sources: Array[Dictionary] = []
var checks: Array[Dictionary] = []
var phase := ""

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var session = load("res://destruction_demo.tscn").instantiate()
    root.add_child(session)
    var sound = session.sound
    sound.set_levels(1, 1, false, false)
    sound.audio_event.connect(func(e: Dictionary):
        e["phase"] = phase
        events.append(e))
    session.debris.burst_started.connect(func(id: int, at: Vector3):
        sources.append({"phase": phase, "id": id, "tick": Engine.get_physics_frames(),
            "frame": Engine.get_process_frames(), "position": [at.x, at.y, at.z],
            "listener_distance": session.camera.global_position.distance_to(at)}))
    for t in session.targets:
        t.free()
    session.targets.clear()
    var positions := [Vector3(0, 0, 9), Vector3(0, 0, -9), Vector3(-9, 0, 0), Vector3(9, 0, 0)]
    var names := ["near", "far", "left", "right"]
    for i in positions.size():
        sound.clear()
        session.debris.clear()
        for j in 60:
            await physics_frame
        phase = names[i]
        sound.rng.seed = 50141
        sound.previous = {"break": -1, "impact": -1}
        var target = load("res://destructible_target.gd").new()
        target.entity_id = 70000 + i
        target.event_seed = 1201
        target.destruction = session.debris
        session.add_child(target)
        target.position = positions[i]
        target.apply_damage(100, target.global_position, Vector3.UP)
        checks.append({"name": phase + "_real_break_32_bodies", "pass": target.is_destroyed and session.debris.bodies.size() == 32})
        for j in 120:
            await physics_frame
        target.free()
    sound.clear()
    session.debris.clear()
    for j in 12:
        await physics_frame
    var passed := true
    for c in checks:
        passed = passed and c.pass
    var report := {"passed": passed, "checks": checks, "source": sources, "audio": events,
        "unit_size": sound.voices[0].unit_size, "max_db": sound.voices[0].max_db,
        "driver": AudioServer.get_driver_name(), "listening": "NONE: paired mixer measurements only"}
    FileAccess.open(OS.get_environment("AUDIO_OUT").path_join("results.json"), FileAccess.WRITE).store_string(JSON.stringify(report, "  "))
    print("SPATIAL_TEST_DONE passed=", passed)
    quit(0 if passed else 1)
