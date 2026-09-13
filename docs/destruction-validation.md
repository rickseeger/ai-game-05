# Node 4 destruction execution and validation handoff

## Historical status: technical implementation delivered; contract validation BLOCKED

Current execution update: see [fresh node 4 rerun](destruction-node4-rerun.md).
Step 136 independently validates the latest source, unchanged physics and passing
reference performance. Subjective destruction quality/readability is explicitly
carried to node 9; lack of worker perception is not an execution blocker. The
measurements and original status below are preserved as historical evidence.

Read the persisted G12 node 4 contract and nodes 1/2/3 through read-only SQLite;
see evidence/destruction/prerequisites.json. Baseline source was
1b711e830de95ecf7cba533cc47b2547a1783b25. Node 1 and node 3 were accepted;
node 2 was explicitly blocked_external for visual assessment. It remains so.
No harness settings, contracts, node states or budget authorizations were changed.

Before implementation, independently launched the actual rendered arena in Godot
4.5.1: 337 assertions passed; original camera, controls, arena and main scene are
unchanged. After implementation the input-driven controls suite passed all 99
assertions, including its independent checker. These are regression measurements,
not visual acceptance of node 2 or a claim to have played the finished game.

## Source and integration boundary

- game/destruction.gd: production burst(transform, kind, seed) -> event_id,
  clear(), burst_started(id, position), impact(position, speed, material, body_id).
- game/debris_block.gd: an independent RigidBody3D with its own BoxShape3D;
  only observes real solver contacts in _integrate_forces. No custom integration,
  analytic gravity, particle trajectory, animation or scripted pose drives physics.
- game/destructible_target.gd: minimal damageable/once-only rupture adapter;
  apply_damage(amount, hit_position, impulse_direction), destroyed(id, at, kind, seed).
  Four 25-damage calls remove the intact mesh AND solid cover collider before
  burst_started, then destroyed is emitted, all within the same physics tick.
  Negative damage and repeated post-death damage have no effect.
- game/destruction_demo.gd/.tscn: explicit fixture composed with the existing
  controls session. B ruptures three targets, N clears/rebuilds the fixture.
  Existing WASD/aim/dash/Esc remain available. This is NOT weapon Combat or the
  opposition/run loop. The main scene remains the original controls slice.
- game/tests/destruction_tests.gd: actual-engine seeded fixture injection,
  assertions, contact/pose traces, screenshots, cap/restart/pause cases.
- scripts/run_destruction.py and check_destruction.py: fresh-output runner and
  independent Python trace/image/negative-control checks (stdlib + existing
  FFmpeg-based PNG checker; no new runtime dependency).

The service expects a ground-level target transform, added to a live scene before
burst is called. Rotations are orthonormalized; actor scaling does not enlarge
0.34m collision shapes. Pylons produce a nonoverlapping 4 x 4 x 2 array (32);
sentinel kind produces a 4 x 4 x 1 array (16). Each receives independent random
X/Z velocities [-3.5,3.5], Y [4.5,7.5] m/s and all-axis spin [-12,12] rad/s.
Event-seeded local RNG is isolated from gameplay RNG. IDs remain unique across
clear/restart in a service lifetime, avoiding stale audio/body ID reuse.

Mass 0.3kg, friction 0.65, restitution 0.42, linear damping 0.12 and angular
damping 0.18 (REPLACE modes, so project damping is not accidentally added), CCD,
max eight contacts, 60Hz GodotPhysics3D, gravity 9.8m/s². Debris layer=2/mask=1;
world/target cover layer=1. Actors and future projectiles ignore debris. The boxes
really contact, rebound, rotate through ground motion and naturally sleep. Cubes
are not claimed to roll smoothly like spheres. No forced sleep is used.

All 32 first-burst fragments remain physical/full-size for seven seconds; only
rendered size shrinks during second eight. Collision geometry is never resized.
TTL then removes their RIDs. The hard cap is 192, retiring oldest sleeping bodies
first, then oldest active, while retaining each complete newest burst. Under
sustained overload an older active burst CAN be cut short; this is the explicit
accepted design policy, not an unconditional eight-second guarantee at any load.
Tests include six simultaneous bursts and three more at two seconds, then three
more at 6.5 seconds: active-cap and sleeping-cap retirement are both exercised.
A separate real-physics fixture keeps oldest bodies falling from 100m while
newer ground bodies naturally sleep, proving sleepers precede older active ones.
Its height is a labelled policy stress fixture, not arena gameplay or framing.

MultiMesh batches DRAWING ONLY, copying every actual rigid-body pose each render
frame. There are still 192 separate physical bodies/shapes. This reduces draw
submission cost without replacing rigid bodies with particles. Render-to-sleeping
body pose agreement is asserted. A premature sleeping-pose caching optimization
failed that test in a fresh run and was removed; original failures are preserved.

Session owners must invoke burst/clear/damage from ordinary fixed-step code,
not inside Godot physics query-flush signals. Queue combat requests from such
callbacks and process them on the normal fixed step. Connect Sound.on_burst to
burst_started exactly once, not also to destroyed. The impact signal uses observed
incoming normal contact speed (including angular point velocity), world contact
position, material=metal and body ID. Signals are rate-limited to >=1m/s, >=0.12s
per body and >=3 ticks globally. The future Sound node owns energy-to-gain/pitch,
eight-voice pooling, mute/volume, samples and audible tuning. Nothing here plays
sound or claims the audio gate is passed. The future run-loop owner observes
destroyed exactly once for objectives and removes dead actor nodes as appropriate.

## Reproduce from the repository root

Use the pinned setup in README.md, or set GODOT_BIN to the installed 4.5.1 binary.
Actual binary here:
/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64

    export GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64
    python3 scripts/run_arena.py fresh-prerequisite
    python3 scripts/check_arena.py evidence/arena/fresh-prerequisite
    python3 scripts/run_destruction.py fresh-capture
    python3 scripts/run_destruction.py fresh-rerun --no-captures
    python3 scripts/run_destruction.py fresh-seed --seed 2207 --no-captures
    python3 scripts/run_destruction.py fresh-performance --performance
    python3 scripts/run_destruction.py fresh-no-gravity --negative-gravity --no-captures
    python3 scripts/run_destruction.py fresh-no-ground --negative-ground --no-captures
    python3 scripts/check_destruction.py evidence/destruction/fresh-capture evidence/destruction/fresh-rerun evidence/destruction/fresh-seed evidence/destruction/fresh-performance --self-test --negative evidence/destruction/fresh-no-gravity --negative evidence/destruction/fresh-no-ground --output evidence/destruction/fresh-checks.json

Negative engine runs MUST exit 1. Do not chain them with && expecting success.
Fresh directories are required; the runner refuses to overwrite earlier evidence.
Runs are ordinary real-time rendered X11/Compatibility launches via Xvfb, not
--headless or MovieWriter. Default 1280x720; the independent capture checker is
specifically for that acceptance size. Each positive engine run finishes with
34 assertions and zero failures. Exact argv, UTC start, environment, source
hashes/status, engine, CPU and renderer are recorded in each launch/results file.
The baseline commit in launch metadata is NOT claimed to contain then-uncommitted
source: the per-file SHA256 map identifies the exact subsequently committed source.

Normal interactive fixture on a graphical Linux desktop:

    "$GODOT_BIN" --path game res://destruction_demo.tscn --rendering-method gl_compatibility

Press B, watch complete arcs, N to reset; Esc pause/resume. No natural terminal
rules exist here; R belongs to the future terminal state integration and is tested
by explicit terminal injection, not claimed as a natural loss/win in this slice.

## Observed technical results

Final evidence directories: verified-1201 (captures + full telemetry), rerun-1201
(fresh process, full telemetry), varied-2207 (different seed, full telemetry),
performance-1201 (same actual physics and assertions, no captures or expensive
per-body CSV writes), negative-gravity, negative-ground. checks.json is generated
by the independent checker; comparison.json compares actual first-burst traces.

Four positive launches each pass 34 assertions. The three full positive traces
have 220256 body samples each, at 60Hz. All 32 first-burst bodies in every full
run rise, spin, fall, make solver contact, rebound, tumble, sleep and clean up.
Discrete vertical acceleration matches gravity+damping to within the checker
0.003m/s² tolerance. Both 1201 launches have identical first-arc physics excluding
wall timestamps. Seed 2207 changes initial conditions and still passes the arc.
This is observed same-VM repeatability, not a cross-platform determinism promise.

32 PNGs from the actual renderer cover early launch/flight, dense contact/tumble
sampling, rest, shrink/cleanup and repeated stress bursts. A single ground-body
arc is retained to TTL and engine tests separately validate sentinel count,
cap policy, three session restarts and pause freezing. Eight in-memory checker
mutations are rejected. Actual no-gravity and no-ground engine runs are also
rejected by both engine checks and independent trace checks. No manufactured
negative data are represented as actual successful engine evidence.

Reference performance FAILS the specified <=33.3ms p95 frame target: lightweight
capture-free performance-1201 records 324 frames with exactly 192 bodies in ticks
510..1109: median 30.909ms, p95 35.114ms, max 41.033ms. Physics-process monitor
median 1.608ms, p95 4.820ms (Godot sampled monitor, not a precise per-body profiler).
This benchmark was not run concurrently with another worker-started engine test.
It still runs test assertions and impact/frame logging. Full telemetry/capture
runs cost more; all measured intervals including outliers are retained, not
filtered into a passing result. physics.csv.gz in the lightweight run contains
only its header by design; its other results/frames remain real measured data.

Reference machine: Linux x86_64 VM, four logical CPUs, AMD EPYC 9354P exposed CPU,
Mesa 26.0.8 llvmpipe LLVM21 software renderer, OpenGL4.5 Compatibility, Xvfb,
Dummy audio. No GPU/laptop performance or perceptual smoothness is inferred.
Further performance work or a documented real Linux GPU reference run is needed;
the target has not been weakened to accommodate this machine. Simulation executes
at 60Hz but that does NOT mean presentation renders at 60fps.

Development evidence, including the parse-time timeout and stale-render-pose
failure, is retained byte-for-byte in development-history.tar.gz with member
hashes and explanations in development-history.json. The early unbatched full
trace was slower; batching helped but did not establish the performance gate.

## Exact visual review handoff: UNASSESSED, not PASS

No exposed image-input/perception tool exists in this worker session. Retried
the installed default-profile auxiliary vision capability probe; actual output
in evidence/destruction/vision-capability.txt reports vision_requirements=false,
OpenRouter payment/credit-labelled resolver failures and missing Nous auth.
Those are recorded diagnostics, not a claim to have inspected account balances.
No provider/profile/harness configuration was changed or external reviewer used.
No screenshot was visually perceived. PNG decoding, pose checks and dynamics
statistics are NOT evidence that the destruction looks convincing or weighty.

Give an image-capable independent validator these actual captures under
  evidence/destruction/verified-1201/

- frame_0001.png is the transition frame (renderer may not yet show the new batch).
  frame_0010.png and frame_0030.png: early upward breakup/flight.
- frame_0060.png: early ground contacts among still-flying blocks.
- frame_0090.png through frame_0150.png: 0.1-second samples for impact/tumbling;
  bodies have differing contact times, so a filename is not a universal phase.
- frame_0210.png, frame_0300.png, frame_0390.png: late motion/natural rest.
- frame_0450.png, frame_0479.png, frame_0490.png: shrink and cleanup.
- frame_0511.png, frame_0540.png, frame_0600.png: simultaneous six-burst arc.
- frame_0631.png, frame_0660.png, frame_0720.png: repeated overload during motion.
- frame_0900.png, frame_0930.png, frame_1020.png, frame_1190.png,
  frame_1385.png: later burst, rest/cleanup under bounded debris.

results.json records requested and actual observed physics ticks and wall time
for each captured frame; actual screenshots can occur a few ticks after request.
The frames are a timestamped sequence, NOT a 60fps movie. Review block depth,
independent spins, ground contact faces, scale/weight, lifetime and readable
silhouettes around the unchanged player. Independently rerun the same source in
the actual engine and observe it, including simultaneous B ruptures and reset.
There are NO frame-specific visual findings from this worker. This unmet review
blocks full node-4 contract validation, as the earlier separate node-2 review
remains blocked. Root fun/audio/exact-release interactive gates remain unfulfilled.
