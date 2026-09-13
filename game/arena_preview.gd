extends Node3D
## Presentation fixtures only. No input, player physics, damage, debris physics or rules.
const ArenaScript = preload("res://arena.gd")
const CameraScript = preload("res://arena_camera.gd")
var arena: Node3D
var camera: Camera3D
var pawn: Node3D
var contact: Node3D
var debris: Array[MeshInstance3D] = []
var caption: Label
var elapsed := 0.0
var tour := true
var testing := false
var tour_trace: Array[Dictionary] = []
var tour_frame := 0
var tour_out := ""
var fixtures := [Vector3(0, 0, 10), Vector3(-11, 0, 11), Vector3(-11, 0, -11),
    Vector3(11, 0, -11), Vector3(11, 0, 11), Vector3(0, 0, 0)]

func _ready() -> void:
    arena = ArenaScript.new()
    arena.name = "Arena"
    add_child(arena)
    var environment := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("09131e")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("bed5ea")
    env.ambient_light_energy = 0.30
    env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
    environment.environment = env
    add_child(environment)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-58, -32, 0)
    sun.light_color = Color("fff0d0")
    sun.light_energy = 0.65
    sun.shadow_enabled = true
    sun.directional_shadow_max_distance = 90
    sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
    add_child(sun)
    camera = CameraScript.new()
    camera.name = "ArenaCamera"
    add_child(camera)
    camera.configure(arena)
    for spawn in arena.pylon_spawns:
        # Not gameplay cover. Later Pylon owns its own once-removable collider.
        ArenaScript.box(self, Vector3(1.1, 2.2, 1.1), spawn.origin + Vector3.UP * 1.1, Color("be793b"))
        ArenaScript.box(self, Vector3(1.2, 0.22, 1.2), spawn.origin + Vector3.UP * 2.0, Color("ffd277"))
    for at in [Vector3(-9, 0, 0), Vector3(9, 0, 4)]:
        ArenaScript.box(self, Vector3(0.75, 0.85, 0.75), at + Vector3.UP * 0.425, Color("ea6662"))
    pawn = Node3D.new()
    pawn.name = "ScriptedPawnStandIn"
    add_child(pawn)
    ArenaScript.box(pawn, Vector3(0.8, 0.7, 0.95), Vector3.UP * 0.55, Color("249ec9"))
    ArenaScript.box(pawn, Vector3(0.18, 0.2, 0.65), Vector3(0, 0.8, -0.6), Color("b8efff"))
    contact = Node3D.new()
    add_child(contact)
    ArenaScript.actor_contact(contact, 0.72)
    for i in 7:
        var cube := ArenaScript.box(self, Vector3.ONE * 0.34, Vector3.ZERO, Color("ffce70"))
        var surface := ShaderMaterial.new()
        surface.shader = preload("res://debris_surface.gdshader")
        surface.set_shader_parameter("tint", Color("ffce70"))
        cube.material_override = surface
        debris.append(cube)
    var canvas := CanvasLayer.new()
    add_child(canvas)
    caption = Label.new()
    caption.position = Vector2(20, 8)
    caption.add_theme_font_size_override("font_size", 14)
    canvas.add_child(caption)
    set_fixture(fixtures[0], 4)
    tour_out = OS.get_environment("ARENA_OUT")
    if "--arena-test" in OS.get_cmdline_user_args():
        testing = true
        tour = false
        var tests = load("res://tests/arena_tests.gd").new()
        add_child(tests)
        tests.run(self)

func set_fixture(at: Vector3, height: float) -> void:
    pawn.position = at
    contact.position = Vector3(at.x, 0, at.z)
    for i in debris.size():
        var phase := float(i) / 6.0
        debris[i].position = Vector3(at.x + (phase - 0.5) * 1.3, maxf(0.25, height - phase * 1.4), at.z)
        debris[i].rotation = Vector3(phase * 2.4, height * 0.7, phase * 4.1)
    caption.text = "BREAKWATER  /  ARENA + CAMERA FIXTURE (not gameplay)
Blue: stand-in   Amber: pylon / nonphysical cubes   Mint: extraction
Ground (%.1f, %.1f) m    Airborne sample %.1f m    Fixed perspective / no player input" % [at.x, at.z, height]

func _process(delta: float) -> void:
    if not tour:
        return
    elapsed += delta
    var index := int(elapsed / 2.0) % fixtures.size()
    var next := (index + 1) % fixtures.size()
    var blend := smoothstep(0.0, 1.0, fmod(elapsed, 2.0) / 2.0)
    var at: Vector3 = fixtures[index].lerp(fixtures[next], blend)
    # Analytic POSITION fixture, emphatically not the later destruction implementation.
    var height := 0.3 + sin(fmod(elapsed, 2.0) / 2.0 * PI) * 7.7
    set_fixture(at, height)

    if not tour_out.is_empty():
        tour_frame += 1
        tour_trace.append({"frame": tour_frame, "delta": delta, "elapsed": elapsed,
            "x": at.x, "z": at.z, "height": height,
            "camera_x": camera.position.x, "camera_y": camera.position.y, "camera_z": camera.position.z})
        if tour_frame in [1, 120, 240, 360, 480, 600]:
            capture_tour_frame(tour_frame)

func capture_tour_frame(frame: int) -> void:
    await RenderingServer.frame_post_draw
    var result := get_viewport().get_texture().get_image().save_png(tour_out.path_join("tour_%04d.png" % frame))
    print("TOUR_CAPTURE frame=", frame, " result=", result)

func _exit_tree() -> void:
    if not testing and not tour_out.is_empty():
        var file := FileAccess.open(tour_out.path_join("tour.json"), FileAccess.WRITE)
        file.store_string(JSON.stringify({"frames": tour_trace, "fixture_only": true,
            "description": "Ordinary real-time rendering, scripted stand-ins, no MovieWriter"}, "  ") + "\n")
        file.close()
        print("ARENA_TOUR_DONE frames=", tour_trace.size())
