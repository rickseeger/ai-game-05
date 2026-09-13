extends Node3D
# Deliberately a probe: no player, enemies, target logic, or game progression.
const COUNT = 32
var rng = RandomNumberGenerator.new()
var bodies: Array[RigidBody3D] = []
var tick = 0
var trace: FileAccess
var events: FileAccess
var players: Array[AudioStreamPlayer3D] = []
var next_voice = 0
var last_impact_tick = -10
var out_dir = ""

func material(color: Color) -> StandardMaterial3D:
    var m = StandardMaterial3D.new()
    m.albedo_color = color
    m.roughness = 0.75
    return m

func box(parent: Node3D, size: Vector3, color: Color) -> void:
    var mesh = MeshInstance3D.new()
    var shape = BoxMesh.new()
    shape.size = size
    mesh.mesh = shape
    mesh.material_override = material(color)
    parent.add_child(mesh)
    var collider = CollisionShape3D.new()
    var collision = BoxShape3D.new()
    collision.size = size
    collider.shape = collision
    parent.add_child(collider)

func tone(frequency: float, duration: float, seed_value: int) -> AudioStreamWAV:
    var sound = AudioStreamWAV.new()
    sound.format = AudioStreamWAV.FORMAT_16_BITS
    sound.mix_rate = 48000
    var data = PackedByteArray()
    var samples = int(duration * 48000)
    data.resize(samples * 2)
    var noise = RandomNumberGenerator.new()
    noise.seed = seed_value
    for i in range(samples):
        var t = float(i) / 48000.0
        var env = pow(1.0 - t / duration, 3.0) * minf(t / 0.004, 1.0)
        var value = (0.65 * sin(TAU * (frequency * t - 45.0 * t * t)) + 0.35 * noise.randf_range(-1, 1)) * env
        data.encode_s16(i * 2, int(value * 18000))
    sound.data = data
    return sound

func _ready() -> void:
    rng.seed = 1201
    out_dir = OS.get_environment("PROBE_OUT")
    if out_dir.is_empty():
        out_dir = ProjectSettings.globalize_path("user://probe")
    DirAccess.make_dir_recursive_absolute(out_dir)
    trace = FileAccess.open(out_dir.path_join("physics.csv"), FileAccess.WRITE)
    events = FileAccess.open(out_dir.path_join("events.csv"), FileAccess.WRITE)
    trace.store_line("tick,id,x,y,z,vx,vy,vz,qx,qy,qz,qw,wx,wy,wz,contacts")
    events.store_line("tick,event,id")
    var camera = Camera3D.new()
    camera.position = Vector3(12, 10, 17)
    add_child(camera)
    camera.look_at(Vector3(0, 2, 0))
    camera.current = true
    var listener = AudioListener3D.new()
    camera.add_child(listener)
    listener.make_current()
    var light = DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-55, -30, 0)
    light.light_energy = 1.5
    add_child(light)
    var environment = WorldEnvironment.new()
    environment.environment = Environment.new()
    environment.environment.background_mode = Environment.BG_COLOR
    environment.environment.background_color = Color(0.035,0.05,0.09)
    environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.environment.ambient_light_color = Color(0.6,0.7,0.9)
    environment.environment.ambient_light_energy = 0.65
    add_child(environment)
    var ground = StaticBody3D.new()
    ground.position.y = -0.25
    box(ground, Vector3(40,0.5,40), Color(0.14,0.21,0.26))
    add_child(ground)
    # Perspective grid provides depth/scale cues without non-physics geometry tricks.
    for i in range(-10, 11, 2):
        for axis in range(2):
            var line = MeshInstance3D.new()
            var line_mesh = BoxMesh.new()
            line_mesh.size = Vector3(20,0.006,0.025) if axis == 0 else Vector3(0.025,0.006,20)
            line.mesh = line_mesh
            line.position = Vector3(0,0.006,i) if axis == 0 else Vector3(i,0.006,0)
            line.material_override = material(Color(0.3,0.38,0.4))
            add_child(line)
    for i in range(8):
        var player = AudioStreamPlayer3D.new()
        player.max_distance = 60
        player.unit_size = 10
        player.volume_db = -8
        add_child(player)
        players.append(player)
    var label = Label.new()
    label.text = "G12 TECH PROBE | 32 rigid cubes | GodotPhysics3D | seed 1201\nNot gameplay. Auto-exits after 7 simulated seconds."
    label.position = Vector2(20, 18)
    add_child(label)
    print("PROBE engine=", Engine.get_version_info().string, " renderer=", RenderingServer.get_video_adapter_name(), " audio=", AudioServer.get_driver_name(), " movie=", OS.has_feature("movie"))

func spawn() -> void:
    for i in range(COUNT):
        var body = RigidBody3D.new()
        body.position = Vector3((i % 4 - 1.5) * 0.43, 1.3 + (i / 16) * 0.43, ((i / 4) % 4 - 1.5) * 0.43)
        body.mass = 0.3
        body.linear_damp = 0.12
        body.angular_damp = 0.18
        body.contact_monitor = true
        body.max_contacts_reported = 8
        body.continuous_cd = true
        # Ground contact only: removes debris/debris cost and initial-overlap instability.
        body.collision_layer = 2
        body.collision_mask = 1
        var physics_material = PhysicsMaterial.new()
        physics_material.bounce = 0.42
        physics_material.friction = 0.65
        body.physics_material_override = physics_material
        box(body, Vector3(0.34,0.34,0.34), Color.from_hsv(float(i) / COUNT * 0.16 + 0.02,0.8,0.95))
        body.linear_velocity = Vector3(rng.randf_range(-3.5,3.5), rng.randf_range(4.5,7.5), rng.randf_range(-3.5,3.5))
        body.angular_velocity = Vector3(rng.randf_range(-12,12),rng.randf_range(-12,12),rng.randf_range(-12,12))
        body.body_entered.connect(on_collision.bind(i))
        add_child(body)
        bodies.append(body)
    play_sound(Vector3(0,2,0), true)
    events.store_line("%d,destruction_sound,-1" % tick)

func play_sound(pos: Vector3, destruction: bool) -> void:
    var player = players[next_voice % players.size()]
    next_voice += 1
    player.position = pos
    player.stream = tone(95.0 if destruction else 260.0, 0.45 if destruction else 0.10, next_voice)
    player.play()

func on_collision(_other: Node, id: int) -> void:
    events.store_line("%d,ground_contact,%d" % [tick,id])
    if tick - last_impact_tick >= 3:
        play_sound(bodies[id].position, false)
        events.store_line("%d,impact_sound,%d" % [tick,id])
        last_impact_tick = tick

func _physics_process(_delta: float) -> void:
    tick += 1
    if tick == 30:
        spawn()
    for i in range(bodies.size()):
        var b = bodies[i]
        var q = b.quaternion
        var p = b.position
        var v = b.linear_velocity
        var w = b.angular_velocity
        trace.store_line("%d,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%d" % [tick,i,p.x,p.y,p.z,v.x,v.y,v.z,q.x,q.y,q.z,q.w,w.x,w.y,w.z,b.get_contact_count()])
    if tick == 420:
        trace.close()
        events.close()
        print("PROBE_DONE ticks=", tick, " bodies=", bodies.size(), " out=", out_dir)
        get_tree().quit()
