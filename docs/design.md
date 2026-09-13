# Bounded game design: Breakwater

## Authority and scope

G12's persisted root is genre-open; its legacy tree name does not constrain this
choice. The verbatim root/node-1 objectives and contracts, configured SSH URL,
$100 tree authorization and initial environment are in evidence/context.json.
Harness interface located at /opt/g-harness/bin/gctl; database read read-only.
No node state, budget, tree objective or contract was changed.

Choose Godot 4.5.1 stable, GDScript, Compatibility OpenGL rendering,
GodotPhysics3D (explicitly selected), and Godot's AudioStreamPlayer3D mixer.
No plugins, purchased assets, network service, multiplayer, procedural world,
vehicle model, campaign, skill tree, Windows export or external native libraries.
One compact low-poly arena, one weapon, one enemy type, three objectives.
Linux x86_64 first and only for this mission. Built-in primitives and original
short synthesized PCM effects keep licensing and asset pipelines economical.

## Loop and player agency (specified, not implemented)

An elevated oblique 3D arena shooter, roughly a two-minute run. Destroy three
armored power pylons to drop the exit shield, then reach the marked extraction
pad alive. Pylons have real solid cover geometry; their destruction also removes
that cover, exposing the player to pursuing sentries. Merely surviving cannot win.

Arena: 24 x 24 meters, bounded walls, three pylons separated by cover, one exit.
Player: a readable blue hover-pawn, 100 health, speed 5 m/s, no jump. WASD moves
in screen-relative ground directions, mouse ray/ground intersection aims a gun,
left mouse fires a 25-damage bolt at a 0.35-second cadence, Space dashes 3 m
with a 2-second cooldown. Esc pauses/releases pointer; R restarts after win/loss.
Pause screen lists controls. No ammunition economy, reload or inventory.

Each pylon has 100 health; four deliberate hits rupture it into physical blocks.
A lock icon and remaining-pylon counter explain why the exit is closed. Pylons
may be destroyed in any order. An extraction beacon visibly opens only when all
three are gone; victory requires entering its 1.5 m radius while alive.
Health reaching zero or the 150-second countdown expiring means defeat.
Terminal state is idempotent: loss takes precedence if lethal damage and exit
entry occur on the same physics tick; pause freezes the countdown and threats.

Opposition: two sentries initially, another every 15 seconds up to six alive.
Simple direct chase and static obstacle avoidance in an intentionally open arena;
no navigation bake is required. Sentries keep 6 m range, display a 0.6-second red
aim telegraph, then launch an 8 m/s projectile for 15 damage on a 1.8-second cycle.
Projectiles collide with solid cover, never pass through it. Player shots can
kill a sentry in two hits; dead sentries shatter too. Spawn positions must be at
least 8 m from the player, with a one-second visible warning and no immediate shot.
No unavoidable contact damage; clear projectile silhouettes and directional hit
feedback make the source of danger readable. Debris itself does not hurt anyone.

The decision is advance on a pylon versus clear pursuers versus retain cover.
Dash out of a telegraphed shot or save it for reaching the next shelter. Breaking
a pylon advances the only win condition but removes protection. Destruction is
structural progress, not a decorative particle reward. Repeatable seeded spawn
variants and competing completion time/remaining health motivate another run.
Values above are bounded starting tuning, not claims of balance or enjoyment.

## Destruction and audio contract

Every pylon: exactly 32 independently simulated 0.34 m box RigidBody3D fragments,
each with its own BoxShape3D, mass 0.3 kg, from a non-overlapping 4 x 4 x 2 grid.
Sentinel death: 16 boxes using the same service, no new fragmentation algorithm.
Remove the intact mesh AND gameplay collider exactly once before fragments spawn.
Random initial velocities: X/Z uniform [-3.5, 3.5] m/s, Y [4.5, 7.5] m/s;
angular velocity independently uniform [-12, 12] rad/s per axis, seeded per event.
Gravity 9.8 m/s²; restitution 0.42, friction 0.65, linear damping 0.12,
angular damping 0.18, CCD enabled, physics 60 Hz. Boxes must rise, rotate,
descend, collide, rebound, then tumble/slide to rest. Cubes do not smoothly roll
like spheres; require visible changing contact faces, not canned trajectories.

Layers: world=1, debris=2, actors=4, projectiles=8. Debris masks only world=1;
no debris/debris collision and no blocking movement/aiming. Ground/walls fixed.
Gameplay damage must not depend on the performance lifetime of decorative debris.
Lifetime eight seconds, visually shrink/fade over the final second; cap at 192
active physical fragments. If a new event exceeds the cap, retire oldest sleeping
fragments, then oldest active ones, preserving the full new burst. Sleep is
allowed; max eight contact reports/body, explicit cleanup on restart. No forever
piles. These cap/lifetime policies belong to later implementation, not this probe.

Emit the destruction audio event in the same physics tick as collider removal
and fragments. Spatial layered low crack/thump plus high grit, no music masking
impacts. Eight voice pool, a global impact throttle of one trigger per three
ticks, further per-body 0.12 s cooldown and minimum relative impact speed 1 m/s
in the game; map impact energy to gain/pitch. Prototype uses original generated
PCM noise/chirps; first tuning pass must replace/adjust any thin sound and address
impact chatter. Add master/SFX volume and mute, no clipping, no excessive loudness.
Movie audio proves routing only, NOT strong sound or an enjoyable payoff.

Performance acceptance target (not yet proven): 60 Hz simulation and p95 frame
interval <= 33.3 ms at 1280x720 during the 192-body stress scene on a documented
Linux reference machine; seek 60 FPS on Rick's laptop. Capture frame intervals,
body counts and cleanup; cap particles before sacrificing gameplay. Software
MovieWriter timings are not this benchmark and not a promise of laptop speed.

## Module interfaces and ownership

- Session (Node): owns state PLAYING/PAUSED/WON/LOST, time/score and seed;
  start(seed), pause(bool), resolve_tick(); emits state_changed(state),
  objectives_changed(remaining). Sole owner of win/loss; restart recreates run.
- Arena (Node3D): build(seed) -> player_spawn, pylon_spawns, enemy_spawn_points,
  exit_transform; world collision and camera/ground aiming surface only.
- Player (CharacterBody3D): read_input() -> movement/aim/fire/dash;
  fixed_step(dt), apply_damage(amount, source); emits fired(origin,direction),
  health_changed(value), died. UI never mutates health directly.
- Combat: spawn_bolt(owner, origin, direction, damage); swept collision; calls
  Damageable.apply_damage(amount, hit_position, impulse_direction) once per hit.
- Pylon/Enemy (damageable actors): unique entity_id, health, destroyed guard;
  emit destroyed(id, transform, kind, event_seed) exactly once. Enemy additionally
  fixed_step(dt, player_position), telegraph and projectile events; spawn manager
  enforces cap/spacing. No actor constructs fragment bodies itself.
- Destruction (Node3D): burst(transform, kind, seed) -> event_id;
  owns fragment pool, collision policy, lifetime and impact telemetry;
  emits burst_started(id, position), impact(position, speed, material, body_id).
- Sound (Node): on_burst/on_impact; owns synthesized/assets audio, voice limiting,
  volume settings. Null output must be diagnosable, not silently called audible.
- HUD (CanvasLayer): observes session/player signals, shows health, objectives,
  clock, reticle, dash readiness and explicit terminal/restart state.
- Validation: deterministic seed/event injection, frame-time/body-count recorder;
  no alternate physics or easier "test-only" gameplay in the shipped release.

Pass immutable value data/signals across modules; Session connects them. Keep
physics in fixed-step functions and rendering in presentation nodes. Units are
meters, seconds and radians; public event ordering is part of automated tests.

## Concern-by-concern order and budget control

1. This probe + design gate: rendering, independent bodies, collision and PCM.
2. Arena/camera/player movement and aiming in isolation; collision/dash tests.
3. Damage/projectiles/intact targets; once-only death and world collision tests.
4. Destruction service with cap/lifetime/restart tests and captured stress run.
5. Sound together with destruction/impact tuning; do not postpone auditory work.
6. Enemy telegraphs, attacks, spawn limits; prove player can actually die.
7. Session objectives, cover removal, exit/timeout, HUD and restart; full loop.
8. Balance/readability and Linux export, automated acceptance, dependency/license
   inventory, release checksum. No extra content before this vertical slice works.
9. Independent exact-release interactive visual AND audible play gate; fix only
   demonstrated problems, then rerun. Root satisfaction/fun remain judgments.

Use existing tree nodes as controller sees fit; this is an implementation order,
not a tree rewrite. $100 is the authorized hard envelope, not a target to spend.
Ledger read at task time contained no G12 entries; that is NOT proof of zero model
cost. Worker cannot see its final billed usage. Controller must reconcile live
usage before dispatch. Pause elective work when remaining funds approach $20 so
Linux packaging, independent play and repairs retain a reserve; stop at authority
limit. One free stack, one arena, fixed caps, no asset commissions. If the core
loop cannot pass in that envelope, report a blocker rather than adding features
or spending past authorization. No subjective gate is waived to save money.
