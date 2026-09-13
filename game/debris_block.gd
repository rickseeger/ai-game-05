extends RigidBody3D
## GodotPhysics owns all trajectories. Only contact observations are recorded here.
var body_id := 0
var event_id := 0
var age := 0.0
var visual_scale := 1.0
var color := Color.WHITE
var contact_count := 0
var pending_speed := 0.0
var pending_position := Vector3.ZERO
var previous_velocity := Vector3.ZERO
var previous_spin := Vector3.ZERO
var last_impact_age := -1.0

func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
    contact_count = state.get_contact_count()
    for i in contact_count:
        var normal := state.get_contact_local_normal(i)
        var point := state.get_contact_local_position(i)
        # Contact coordinates/normals are world-space for GodotPhysics3D.
        var incoming := previous_velocity + previous_spin.cross(point - state.transform.origin)
        var relative := incoming - state.get_contact_collider_velocity_at_position(i)
        var speed := maxf(0.0, -relative.dot(normal))
        if speed > pending_speed:
            pending_speed = speed
            pending_position = point
    previous_velocity = state.linear_velocity
    previous_spin = state.angular_velocity
