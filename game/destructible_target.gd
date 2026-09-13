extends Node3D
## Minimal damageable integration boundary. Combat and opposition are separate.
signal destroyed(id: int, at: Transform3D, kind: StringName, event_seed: int)
const Arena = preload("res://arena.gd")
var entity_id := 0
var health := 100
var kind: StringName = &"pylon"
var event_seed := 1201
var is_destroyed := false
var intact: StaticBody3D
var destruction: Node3D

func _ready() -> void:
    intact = StaticBody3D.new()
    intact.collision_layer = 1 # Solid cover for actors, debris and future projectiles.
    intact.collision_mask = 0
    add_child(intact)
    var size := Vector3(1.42, 0.86, 1.42)
    var collider := CollisionShape3D.new()
    var shape := BoxShape3D.new()
    shape.size = size
    collider.shape = shape
    collider.position.y = 0.43
    intact.add_child(collider)
    Arena.box(intact, size, Vector3(0, 0.43, 0), Color("eeb358"))

func apply_damage(amount: int, _hit_position: Vector3, _impulse_direction: Vector3) -> void:
    if is_destroyed or amount <= 0:
        return
    health = maxi(0, health - amount)
    if health != 0:
        return
    is_destroyed = true
    remove_child(intact)
    intact.free()
    # Both observable events occur only after cover is absent. No sound is played here.
    if is_instance_valid(destruction):
        destruction.burst(global_transform, kind, event_seed)
    destroyed.emit(entity_id, global_transform, kind, event_seed)
