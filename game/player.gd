extends CharacterBody3D
## Upright unscaled arena, fixed 60Hz. Combat consumes fired; no fake projectiles.
signal fired(origin: Vector3, direction: Vector3)
signal dashed(distance: float)
signal health_changed(value: int)
signal damaged(amount: int, source: Vector3)
signal died
var health := 100
var hit_flash := 0.0
var hit_indicator: Node3D
const ArenaScript = preload("res://arena.gd")
const SPEED := 5.0
const RADIUS := 0.4
const DASH_DISTANCE := 3.0
const DASH_COOLDOWN := 2.0
const FIRE_INTERVAL := 0.35
const BOLT_DAMAGE := 25
var controls: Node
var camera: Camera3D
var gun: Node3D
var reticle: Node3D
var aim_point := Vector3.ZERO
var aim_direction := Vector3.FORWARD
var aim_valid := false
var fire_remaining := 0.0
var dash_remaining := 0.0
var shot_count := 0
var dash_count := 0

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_PAUSABLE
    collision_layer = 4
    collision_mask = 1
    safe_margin = 0.001
    var shape := CylinderShape3D.new()
    shape.radius = RADIUS
    shape.height = 0.8
    var collider := CollisionShape3D.new()
    collider.shape = shape
    collider.position.y = 0.4
    add_child(collider)
    ArenaScript.box(self, Vector3(0.65, 0.6, 0.65), Vector3.UP * 0.5, Color("249ec9"))
    ArenaScript.actor_contact(self, 0.64)
    gun = Node3D.new()
    add_child(gun)
    ArenaScript.box(gun, Vector3(0.16, 0.16, 0.65), Vector3(0, 0.65, -0.45), Color("b8efff"))
    hit_indicator = Node3D.new()
    add_child(hit_indicator)
    ArenaScript.box(hit_indicator, Vector3(0.18, 0.08, 0.65), Vector3(0, 0.12, -0.95), Color("ff4433"))
    hit_indicator.visible = false
    reticle = Node3D.new()
    add_child(reticle)
    reticle.top_level = true
    ArenaScript.ring(reticle, Vector3.UP * 0.03, 0.28, Color("ffffff"))

func _physics_process(dt: float) -> void:
    fixed_step(dt)

func fixed_step(dt: float) -> void:
    hit_flash = maxf(0, hit_flash - dt)
    hit_indicator.visible = hit_flash > 0
    if health <= 0:
        return
    var command: Dictionary = controls.read_input()
    var axes: Vector2 = command.movement
    var right := camera.global_basis.x
    right.y = 0
    right = right.normalized()
    var forward := Vector3.UP.cross(right).normalized()
    var movement := (right * axes.x - forward * axes.y).limit_length()
    fire_remaining = maxf(0, fire_remaining - dt)
    dash_remaining = maxf(0, dash_remaining - dt)
    # Real CharacterBody swept collision on all ordinary movement.
    velocity = movement * SPEED
    velocity.y = -1.0
    move_and_slide()
    update_aim(command)
    if command.dash and dash_remaining <= 0.00001:
        var direction: Vector3 = movement if movement.length_squared() > 0.01 else aim_direction
        var start := global_position
        # One swept 3m displacement, stopping at first solid contact, never teleport.
        move_and_collide(direction * DASH_DISTANCE)
        dash_remaining = DASH_COOLDOWN
        dash_count += 1
        dashed.emit(Vector2(global_position.x - start.x, global_position.z - start.z).length())
        update_aim(command)
    if command.fire and aim_valid and fire_remaining <= 0.00001:
        # Origin stays within the actor radius so a gun near cover cannot spawn
        # a future bolt on the far side of that cover. Combat must sweep from here.
        var origin := global_position + Vector3.UP * 0.65 + aim_direction * 0.25
        shot_count += 1
        fire_remaining = FIRE_INTERVAL
        fired.emit(origin, aim_direction)

func update_aim(command: Dictionary) -> void:
    var hit: Variant = camera.ground_aim(command.pointer) if command.pointer_known else null
    aim_valid = hit != null
    if aim_valid:
        aim_point = hit
        var direction: Vector3 = aim_point - global_position
        direction.y = 0
        aim_valid = direction.length_squared() > 0.0025
        if aim_valid:
            aim_direction = direction.normalized()
            gun.rotation.y = atan2(-aim_direction.x, -aim_direction.z)
            reticle.global_position = aim_point
    reticle.visible = aim_valid

func apply_damage(amount: int, source: Vector3, _impulse_direction: Vector3 = Vector3.ZERO) -> void:
    if health <= 0 or amount <= 0:
        return
    health = maxi(0, health - amount)
    hit_flash = 0.35
    var direction := source - global_position
    hit_indicator.rotation.y = atan2(-direction.x, -direction.z)
    hit_indicator.visible = true
    damaged.emit(amount, source)
    health_changed.emit(health)
    if health == 0:
        died.emit()
