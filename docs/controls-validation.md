# Node 3 execution: Breakwater player controls

## Authority, baseline and scope

Assigned work only: G12 node 3, ai-game-05. Read design.md, acceptance.md,
validation.md and arena/camera interfaces before editing. Checkout began at
4ab50bf71af221da7b8fa4342a9053d93aa19e39, following arena implementation
d649df50a96cccb200226bb7886f65abd0e42082. No mission/harness state was modified.
Followed accepted Breakwater, not the obsolete vehicular-combat description.

Before editing, independently relaunched the existing arena at 1280x720 and
960x720: 337 assertions each, zero failures; independent PNG decoding and five
checker negative controls passed. Fresh artifacts: evidence/arena/node3-baseline-720p,
node3-baseline-4x3 and node3-baseline-checks.json. Arena, camera, preview and arena
tests are unchanged. run_arena.py explicitly selects the old preview scene now
that the default game scene is controls.tscn.

Node 2 remains blocked solely on unperformed independent visual assessment.
These reruns do NOT resolve that limitation. This worker has no visual/audio
perception tool or observed desktop. No claim of playability, enjoyment, root
completion, natural victory/defeat or controller acceptance is made.

## Production implementation

- player_input.gd installs physical WASD / Space / Escape / R and left mouse
  InputMap entries. Actual InputEventKey/Mouse events feed production _input;
  no test-only motion path or global action polling. Opposing axes cancel and
  diagonal axes normalize. Keyboard echo cannot retrigger dash/pause/restart.
- player.gd is a real CharacterBody3D on actors=4, mask world=1. A radius 0.4m,
  height 0.8m cylinder rests on the real floor; ordinary move_and_slide is 5m/s
  at 60Hz, relative to the camera ground basis. No jump, acceleration lag or
  inertial drift. Release stops on the next physics tick.
- Space is an edge-triggered 3m swept move_and_collide displacement with a 2s
  cooldown. It follows movement, or last valid aim while stationary (initial
  fallback: north). It stops on contact, never teleports through cover/walls;
  diagonal corner collision is exercised. Dash is instant in one physics tick,
  not invulnerability or a damage mechanic.
- Ground-only camera ray aiming ignores cover/decorative debris as specified.
  Gun and world reticle follow the intersection; off-arena or near-zero aim
  hides the reticle and suppresses firing, retaining last heading. Resizing
  refits the existing camera; fresh mouse events still round-trip.
- Holding LMB emits fired(origin, direction) immediately when ready, then every
  0.35s (21 physics ticks). BOLT_DAMAGE=25 is exposed for later Combat. Origin
  is 0.65m high, 0.25m ahead, inside the pawn footprint so the visual barrel
  cannot create bolts across adjacent cover. No projectile, damage, hit effect,
  destruction, audio or opposition implementation. HUD counts fire commands,
  not hits. Connect fired to future spawn_bolt(owner, origin, direction, 25).
- controls_session.gd integrates Arena, camera, player and controls HUD. Esc
  pauses the actual SceneTree; input router/test recorder can process while
  paused, gameplay descendants cannot. Clock and both cooldowns freeze. Mouse
  intentionally stays visible for absolute aiming, including pause. Pause
  panel lists controls and the release/re-press policy.
- State adapter exposes start(seed), pause(bool), finish(WON/LOST), state_changed
  and player_replaced. finish is a future rule-owner interface, NOT a win/loss
  rule. R is ignored while playing/paused; after either terminal state it
  recreates the player and clears input, cooldowns, shots and elapsed time.
  Static arena need not rebuild; no destructible/session objects exist yet.
  Later full Session must extend cleanup and implement health, timer, objectives,
  loss precedence and naturally reachable endings.
- Pause, terminal, restart and focus loss clear held controls and queued dash.
  No polling of still-held OS actions can resurrect them. Releases/fresh presses
  work afterward; key echoes do not. New gameplay presses while paused are
  ignored. Focus loss auto-pauses and invalidates stale pointer knowledge.

Only static arena cover exists here. Old preview pylon/enemy stand-in meshes
are not put into controls: pylon sites remain marked, but later Pylon owns its
intact collider. Static-cover checks do not prove pylon removal or bolt collision.

## Tests and actual runtime evidence

scripts/run_controls.py launches the actual main scene via Xvfb, Compatibility
OpenGL, GodotPhysics3D and explicit Dummy audio. --controls-test adds a separate
driver/observer to the SAME production nodes. It refuses old output directories,
records argv/environment/source SHA256, and kills its own group on timeout.
No headless or MovieWriter substitute is used.

game/tests/controls_tests.gd injects physical InputEventKey press/release/echo,
InputEventMouseMotion and InputEventMouseButton using Input.parse_input_event.
Events traverse actual InputMap/_input before normal production physics. Tests
never call fixed_step/read_input/movement/fire/pause/restart methods or
Input.action_press. trace.json records per-tick inputs, positions, aim, velocity,
state, cooldowns, generations and fired signals.

Labelled setup exceptions: fixture_position teleports arrange collision cases;
fixture_terminal calls finish to represent a future rule outcome; a
fixture_focus_out_notification exercises focus clearing. These are NOT player
input, natural win/loss or real OS focus change. Screenshots read the actual
viewport after frame_post_draw. Numeric/image decoding is not perception.
This validates engine input events, not keyboard hardware, OS layout handling,
end-to-end display latency or human control comfort.

Positive runs: evidence/controls/verified-720p and verified-4x3. Each passes 99
assertions with zero failures: mappings, next-tick press/release, normalized
movement, all boundaries, sliding/corners, all solid covers, dash distance and
cooldown, mouse targets/resize/invalid aim, fire cadence/release, actual Esc
pause with nonzero cooldowns frozen, echo filtering, no resume jump/stuck keys,
R eligibility, three terminal/restart cycles, fresh post-restart movement/fire,
no orphan player and focus clearing. Five real PNGs per run: initial.png,
aim_cover.png, resized_target.png, paused_controls.png, final_restart.png.
Exact counts/timings are in results.json, trace.json and launch.json; these
are NOT performance or comfort claims.

scripts/check_controls.py independently reconstructs displacement at injected
press/release tick boundaries, checks every arena-bound sample, cover endpoints,
dash distance/repeats, fired directions/origins/cadence, frozen pause intervals
and R-driven restart generations. It checks source hashes and decodes all PNGs
with FFmpeg. checks.json retains results. Six in-memory mutations are rejected:
missing input, static movement, outside-wall position, wrong targeting, paused
clock drift and stale restart shots. No mutated trace is successful evidence.

negative-collision is a fresh engine run disabling the actor world mask for one
explicit test wall case, then restoring it. Real actor leaves the arena, engine
exits 1 with negative_control_wall_must_stop, and independent trace checking
rejects it. Production has no alternate easy physics path.

Development attempt development-01 is retained byte-for-byte in
development-01.tar.gz. Three 4mm dash-contact tolerances failed: the conservative
Godot sweep stopped about 8.85mm short of cover, not through it. Final test allows
at most 15mm early stopping and forbids more than 1mm crossing; subsequent held
walking must settle within 4mm. Production collision was not weakened.

## Reproduce

Install prerequisites/pinned engine per docs/validation.md and scripts/setup.sh,
or export GODOT_BIN to a verified 4.5.1 binary. Every launch.json records the
actual binary and command. From repo root, choose fresh output names:

    python3 scripts/run_arena.py reviewer-arena-720p
    python3 scripts/run_arena.py reviewer-arena-4x3 --size 960x720
    python3 scripts/check_arena.py evidence/arena/reviewer-arena-720p evidence/arena/reviewer-arena-4x3 --self-test
    python3 scripts/run_controls.py reviewer-controls-720p
    python3 scripts/run_controls.py reviewer-controls-4x3 --size 960x720
    python3 scripts/run_controls.py reviewer-negative --negative-collision

Last command MUST exit 1. Then:

    python3 scripts/check_controls.py evidence/controls/reviewer-controls-720p evidence/controls/reviewer-controls-4x3 --negative-dir evidence/controls/reviewer-negative --self-test

Recheck stored evidence:

    python3 scripts/check_controls.py evidence/controls/verified-720p evidence/controls/verified-4x3 --negative-dir evidence/controls/negative-collision --self-test
    sha256sum -c evidence/controls/SHA256SUMS

On an actual Linux desktop:

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game --rendering-method gl_compatibility

WASD moves, mouse aims, LMB counts fire commands, Space dashes, Esc pauses/resumes.
R requires a future rule owner to supply terminal state: no invented natural
win/loss in this slice. Add res://arena_preview.tscn to launch the original tour.

## Unresolved validation and integration

Independent visual assessment for node 2 remains unperformed. This session did
not see/hear gameplay, judge responsiveness by feel or operate a visible desktop.
The later exact-release interactive visual/audible G gate remains mandatory.
These tests do not prove playability. Pylon collision, Combat, destruction, sound,
sentries, full terminal rules and their restart cleanup await their own nodes.


## Final regression / normal launch

After integration, evidence/arena/node3-final-720p reruns the explicit preview
entry point: 337 assertions pass, with independent decoded-image checks in
node3-final-checks.json. evidence/controls/normal-smoke records a normal default
main-scene launch without any test flag, rendering 120 frames then exiting 0
without script errors. This smoke test injects no input and adds no play claim.
The positive input runtime suites and their source hashes were checked again
before committing. Original probe and node2 visual-followup artifacts are
unchanged; evidence/controls/provenance.json records baseline/interface hashes.
