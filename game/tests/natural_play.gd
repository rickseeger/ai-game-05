extends Node
## Read-only observer plus ordinary InputEvents. Never writes production state.
var s: Node3D
var out: String
var mode: String
var tick := 0
var phase := 0
var phase_tick := 0
var keys: Dictionary = {}
var firing := false
var events: FileAccess
var physics: FileAccess
var frames: FileAccess
var running := false
var initial_generation := 0
var terminal_tick := -1
var last_frame_usec := 0
var done := false
var pause_snapshot: Dictionary
var capture_frames: Dictionary = {}
var capture_busy := false
var replay: Dictionary = {}
var replay_enabled := false

func v(a: Vector3) -> Array:
    return [a.x, a.y, a.z]

func record(kind: String, data: Dictionary = {}) -> void:
    var row := data.duplicate(true)
    row.kind = kind
    row.tick = tick
    row.engine_tick = Engine.get_physics_frames()
    row.frame = Engine.get_process_frames()
    row.usec = Time.get_ticks_usec()
    row.generation = s.generation
    row.phase = phase
    events.store_line(JSON.stringify(row))

func snapshot() -> Dictionary:
    var targets: Array = []
    for t in s.targets:
        targets.append({"id":t.entity_id,"health":t.health,"destroyed":t.is_destroyed,"intact":is_instance_valid(t.intact)})
    var enemies: Array = []
    for e in s.opposition.sentries:
        enemies.append({"id":e.entity_id,"p":v(e.global_position),"health":e.health,"aiming":e.aiming})
    return {"state":s.state,"time":s.elapsed,"health":s.player.health,"p":v(s.player.global_position),
        "remaining":s.remaining_pylons(),"unlocked":s.extraction_unlocked(),"inside":s.in_extraction(),
        "reason":s.loss_reason,"targets":targets,"enemies":enemies,"pending":s.opposition.pending.size(),
        "bolts":s.combat.bolts.size(),"debris":s.debris.bodies.size(),"visible_debris":s.debris.batch.multimesh.visible_instance_count,
        "shots":s.shots,"player_shots":s.player.shot_count,"dashes":s.player.dash_count,"dash_left":s.player.dash_remaining,
        "fire_left":s.player.fire_remaining,"held":s.controls.held.duplicate(),"pointer_known":s.controls.pointer_known,
        "aim_valid":s.player.aim_valid,"opposition_time":s.opposition.elapsed,"next_spawn":s.opposition.next_spawn,
        "next_enemy":s.opposition.next_entity,"voices":s.sound.active_count(),"body_throttle":s.sound.body_ticks.size(),
        "clock_error":s._clock_error,"nodes":s.get_tree().get_node_count(),"buses":AudioServer.bus_count,
        "master":s.sound.master,"sfx":s.sound.sfx,"muted":s.sound.muted,
        "collisions":range(s.player.get_slide_collision_count()).map(func(i):return str(s.player.get_slide_collision(i).get_collider().name))}

func attach() -> void:
    s.player.fired.connect(func(a: Vector3,b: Vector3):record("fired",{"p":v(a),"direction":v(b)}))
    s.player.damaged.connect(func(a: int,b: Vector3):record("damage",{"amount":a,"source":v(b),"health":s.player.health}))
    s.player.dashed.connect(func(d: float):record("dash",{"distance":d}))
    for t in s.targets:
        t.destroyed.connect(func(id: int,at: Transform3D,kind: StringName,seed_value: int):
            record("target_destroyed",{"id":id,"p":v(at.origin),"target_kind":kind,"seed":seed_value,"snapshot":snapshot()}))

func body_row(b: RigidBody3D) -> Dictionary:
    return {"id":b.body_id,"event":b.event_id,"age":b.age,"p":v(b.global_position),"v":v(b.linear_velocity),
        "w":v(b.angular_velocity),"contacts":b.contact_count,"colliders":b.get_colliding_bodies().map(func(c):return str(c.name)),"sleeping":b.sleeping,"rotation":v(b.rotation)}

func run(owner: Node3D) -> void:
    s = owner
    out = OS.get_environment("NATURAL_OUT")
    mode = OS.get_environment("NATURAL_MODE")
    events = FileAccess.open(out.path_join("events.jsonl"),FileAccess.WRITE)
    physics = FileAccess.open(out.path_join("physics.jsonl"),FileAccess.WRITE)
    frames = FileAccess.open(out.path_join("frames.jsonl"),FileAccess.WRITE)
    process_mode = Node.PROCESS_MODE_ALWAYS
    process_physics_priority = -8
    initial_generation = s.generation
    s.combat.event.connect(record)
    s.opposition.event.connect(record)
    s.sound.audio_event.connect(func(d: Dictionary):record("audio",{"audio":d}))
    s.debris.burst_started.connect(func(id: int,at: Vector3):
        var bodies: Array = []
        for b in s.debris.bodies:
            if b.event_id == id:bodies.append(body_row(b))
        record("burst",{"id":id,"p":v(at),"bodies":bodies})
        if OS.get_environment("NATURAL_MOVIE")=="1":
            for delta in [0,30,60,90,180,360]:capture_frames[Engine.get_process_frames()+delta]=true)
    s.debris.impact.connect(func(at: Vector3,speed: float,mat: StringName,id: int):
        record("impact",{"id":id,"p":v(at),"speed":speed,"material":mat}))
    s.debris.fragment_retired.connect(func(id: int,why: String,age: float,asleep: bool):
        record("retired",{"id":id,"reason":why,"age":age,"sleeping":asleep}))
    s.objectives_changed.connect(func(n: int):record("progress",{"remaining":n}))
    s.state_changed.connect(func(_state: int):
        record("state",snapshot())
        if OS.get_environment("NATURAL_MOVIE")=="1":capture_frames[Engine.get_process_frames()]=true)
    s.player_replaced.connect(func(_p: CharacterBody3D):
        record("reset",snapshot())
        attach())
    attach()
    record("initial",snapshot())
    record("environment",{"display":DisplayServer.get_name(),"audio":AudioServer.get_driver_name(),"physics_hz":Engine.physics_ticks_per_second,"mode":mode})
    var replay_path := OS.get_environment("NATURAL_REPLAY")
    replay_enabled = not replay_path.is_empty()
    if replay_enabled:
        for e in JSON.parse_string(FileAccess.get_file_as_string(replay_path)):
            var n := int(e.tick)
            if not replay.has(n):replay[n]=[]
            replay[n].append(e)
    running = true

func key(code: int, down: bool) -> void:
    if bool(keys.get(code,false)) == down:return
    keys[code] = down
    var e := InputEventKey.new()
    e.physical_keycode = code
    e.pressed = down
    record("input_key",{"code":code,"pressed":down})
    Input.parse_input_event(e)

func aim(at: Vector3,fire: bool) -> void:
    at.y = 0
    var p: Vector2 = s.camera.unproject_position(at)
    var e := InputEventMouseMotion.new()
    e.position = p
    record("input_mouse",{"p":[p.x,p.y],"world":v(at)})
    Input.parse_input_event(e)
    if fire != firing:
        firing = fire
        var b := InputEventMouseButton.new()
        b.button_index = MOUSE_BUTTON_LEFT
        b.position = p
        b.pressed = fire
        record("input_fire",{"p":[p.x,p.y],"pressed":fire})
        Input.parse_input_event(b)

func release() -> void:
    for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_SPACE,KEY_ESCAPE,KEY_R]:key(code,false)
    aim(Vector3(0,0,6),false)

func move_to(at: Vector3, dash := true) -> bool:
    var d: Vector3 = at-s.player.global_position
    d.y = 0
    key(KEY_D,d.x>0.12)
    key(KEY_A,d.x< -0.12)
    key(KEY_S,d.z>0.12)
    key(KEY_W,d.z< -0.12)
    key(KEY_SPACE,dash and d.length()>4.0 and s.player.dash_remaining<0.00001)
    return d.length()<0.24

func clear_shot(at: Vector3) -> bool:
    var a: Vector3 = s.player.global_position+Vector3.UP*0.65
    var b := at+Vector3.UP*0.65
    var q := PhysicsRayQueryParameters3D.create(a,b,1|4,[s.player.get_rid()])
    var hit: Dictionary = s.get_world_3d().direct_space_state.intersect_ray(q)
    if hit.is_empty():return true
    return hit.position.distance_to(b)<0.9

func shoot(objective: int = -1) -> void:
    var chosen: Node3D = null
    var distance := 1000.0
    for e in s.opposition.sentries:
        var d: float = e.global_position.distance_to(s.player.global_position)
        if d<distance and clear_shot(e.global_position):
            chosen=e
            distance=d
    if chosen != null and (distance<8.0 or objective<0):
        aim(chosen.global_position,true)
    elif objective>=0 and not s.targets[objective].is_destroyed:
        aim(s.targets[objective].global_position,true)
    else:aim(Vector3(0,0,6),false)

func next_phase() -> void:
    phase += 1
    phase_tick = tick
    record("phase",snapshot())

func victory_route() -> void:
    if phase not in [4,5,8]:shoot()
    match phase:
        0:
            if move_to(Vector3(2.5,0,9)):next_phase()
        1:
            if move_to(Vector3(2.5,0,-9)):next_phase()
        2:
            if move_to(Vector3(0,0,-10)):next_phase()
        3:
            move_to(Vector3(0,0,-10),false)
            if tick-phase_tick>60:
                record("early_extraction",snapshot())
                next_phase()
        4:
            shoot(0)
            if s.targets[0].is_destroyed:next_phase()
        5:
            shoot(1)
            if s.targets[1].is_destroyed:next_phase()
        6:
            if move_to(Vector3(2.5,0,-8)):next_phase()
        7:
            if move_to(Vector3(2.5,0,3)):next_phase()
        8:
            move_to(Vector3(2.5,0,3),false)
            shoot(2)
            if s.targets[2].is_destroyed:next_phase()
        9:
            if tick-phase_tick>540:next_phase()
        10:
            if move_to(Vector3(2.5,0,-9)):next_phase()
        11:move_to(Vector3(0,0,-10))

func _physics_process(_dt: float) -> void:
    if not running or done:return
    tick += 1
    record("sample",snapshot())
    var bodies: Array = []
    for b in s.debris.bodies:bodies.append(body_row(b))
    if not bodies.is_empty():physics.store_line(JSON.stringify({"tick":tick,"engine_tick":Engine.get_physics_frames(),"frame":Engine.get_process_frames(),"generation":s.generation,"bodies":bodies}))
    if replay_enabled:
        if s.state in [s.State.WON,s.State.LOST] and terminal_tick<0:
            terminal_tick=tick
            record("terminal",snapshot())
        elif s.state==s.State.PLAYING:terminal_tick=-1
        for e in replay.get(tick,[]):
            if e.kind=="input_key":
                var event := InputEventKey.new()
                event.physical_keycode=int(e.code)
                event.pressed=e.pressed
                record("input_key",{"code":int(e.code),"pressed":e.pressed})
                Input.parse_input_event(event)
            elif e.kind=="input_mouse":
                var event := InputEventMouseMotion.new()
                event.position=Vector2(e.p[0],e.p[1])
                record("input_mouse",{"p":e.p})
                Input.parse_input_event(event)
            elif e.kind=="input_fire":
                var event := InputEventMouseButton.new()
                event.button_index=MOUSE_BUTTON_LEFT
                event.position=Vector2(e.p[0],e.p[1])
                event.pressed=e.pressed
                record("input_fire",{"p":e.p,"pressed":e.pressed})
                Input.parse_input_event(event)
            elif e.kind=="end":call_deferred("finish","finished")
            else:record(e.kind,snapshot())
        if tick>14000:finish("watchdog")
        return
    if tick>14000:
        finish("watchdog")
        return
    if s.state in [s.State.WON,s.State.LOST]:
        if terminal_tick<0:
            terminal_tick=tick
            record("terminal",snapshot())
            release()
        if tick-terminal_tick==60:
            key(KEY_R,true)
        return
    if terminal_tick>=0:
        key(KEY_R,false)
        terminal_tick=-1
        phase=0
        phase_tick=tick
        keys.clear()
        firing=false
    if tick==30:
        release()
        key(KEY_ESCAPE,true)
        pause_snapshot=snapshot()
        record("pause_start",pause_snapshot)
        return
    if tick==31:key(KEY_ESCAPE,false)
    if tick==90:
        record("pause_end",snapshot())
        key(KEY_ESCAPE,true)
        return
    if tick==91:key(KEY_ESCAPE,false)
    if s.state != s.State.PLAYING:return
    var cycle: int = s.generation-initial_generation
    if mode=="timeout" and cycle==0:
        shoot()
        return
    if cycle==0:
        victory_route()
    elif cycle==1 and mode!="timeout":
        # Fresh input replay: remove southern cover, then expose oneself by
        # withholding counterfire. Threats remain at full production strength.
        if s.elapsed<3:
            move_to(Vector3(2,0,9),false)
            shoot(2)
        else:release()
    else:
        if s.elapsed<3:
            move_to(Vector3(2,0,9),false)
            shoot(2)
        else:
            release()
            if s.elapsed>3.5 and s.sound.active_count()==0:call_deferred("finish","finished")

func _process(_dt: float) -> void:
    if not running or done:return
    var now := Time.get_ticks_usec()
    frames.store_line(JSON.stringify({"frame":Engine.get_process_frames(),"tick":tick,"usec":now,"interval_usec":now-last_frame_usec,"engine_process":Performance.get_monitor(Performance.TIME_PROCESS),"physics_process":Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)}))
    last_frame_usec=now
    if capture_frames.has(Engine.get_process_frames()) and not capture_busy:
        capture_busy=true
        var frame := Engine.get_process_frames()
        await RenderingServer.frame_post_draw
        var name := "frame_%05d.png" % frame
        var image := get_viewport().get_texture().get_image()
        var code := image.save_png(out.path_join(name))
        var projected: Array = []
        for b in s.debris.bodies:
            var pixel: Vector2 = s.camera.unproject_position(b.global_position)
            projected.append({"id":b.body_id,"pixel":[pixel.x,pixel.y],"age":b.age})
        record("capture",{"file":name,"captured_frame":frame,"error":code,"projected_bodies":projected,"snapshot":snapshot()})
        capture_busy=false

func finish(reason: String) -> void:
    if done:return
    if reason=="finished" and s.sound.active_count()>0:return
    done=true
    record("end",{"reason":reason,"snapshot":snapshot()})
    events.close()
    physics.close()
    frames.close()
    print("NATURAL_END ",reason," generation=",s.generation," phase=",phase," state=",s.state)
    # Remove observer closures before tree teardown (no gameplay mutation).
    for source in [s,s.player,s.combat,s.opposition,s.sound,s.debris]+s.targets:
        for sig in source.get_signal_list():
            for connection in source.get_signal_connection_list(sig.name):
                if connection.callable.get_object()==self:
                    source.disconnect(sig.name,connection.callable)
    get_tree().quit(0 if reason=="finished" else 1)
