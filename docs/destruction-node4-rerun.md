# G12 node 4 — fresh actual-engine validation, step 136

Execution finished; technical checks pass. This report does not durably complete
any mission node or approve subjective destruction quality. The task packet
accepts node 1 and node 10, and establishes a runnable node 2 arena while keeping
its perceptual readability question open. No harness state was read or changed.

## Source and scope

Fresh clone of git@github.com:rickseeger/ai-game-05.git at
8f311f7643d493e7fa5be11d88feb97c93261ff4. No game source, existing tests, benchmark,
thresholds, camera or audio were changed: no objective failure needing a fix was
reproduced. This delivery adds evidence and reproduction/analysis helpers only.
Author: the gardener <root@g.seeger.net>.

Read docs/design.md, docs/destruction-validation.md and
 docs/destruction-performance-remediation.md and the existing engine tests and
runners before execution. The old reports remain historical: their original
performance failure was remediated by node 10, and lack of worker image perception
is not a blocker in this assignment. The current report supersedes those old
execution-status statements, not the human quality gate.

Production remains game/destruction.gd, game/debris_block.gd and
 game/destructible_target.gd; the fixture is game/destruction_demo.tscn.
GodotPhysics3D owns independent RigidBody3D/BoxShape3D trajectories. The MultiMesh
copies actual body transforms for rendering only. No custom trajectory, forced
sleep, particle substitute or weakened collision/physics workload was introduced.
Pylons have 32 boxes, sentinels 16; side 0.34m, mass 0.3kg, friction 0.65,
restitution 0.42, linear/angular damping 0.12/0.18, CCD, world-only collision mask.

The provenance checker verifies node 10 ring batching is byte-identical at the
function level. Original destruction tests/runners, frame gate, body observer,
rupture adapter and demo are byte-identical to f6631e4. The existing destruction
service difference from node 10 is only the already-committed surface material;
physics/lifetime/cap code is unchanged. Every current game file matches its fresh
launch SHA256. The new same-seed trace hash also matches node 10 historical data.

## Actual execution

Runs started 2026-09-13 23:51:35 UTC; final comparison started 23:56:18 UTC.
All engine processes ran sequentially, never concurrently with another engine
started by this worker. Shared-host scheduling is not controlled.
Godot 4.5.1 official f62fdbde1, Linux x86_64 kernel 7.0.0-31-generic,
four logical CPUs, exposed AMD EPYC 9354P, X11/Xvfb, Compatibility OpenGL 4.5,
Mesa 26.0.8 llvmpipe LLVM21.1.8, 1280x720, Dummy audio. No headless physics,
MovieWriter timing, GPU/laptop performance or audible review is claimed.

- Arena: 337 assertions plus independent pixel/framing checks and five checker
  mutations pass. Minimum frame margin 0.08576095, minimum projected cube size
  6.08423 pixels. Six projected-cube pixel regions and resized output validated.
- Six positive destruction launches: 34 assertions each, no engine failures.
  Capture seed 1201, independent process rerun seed 1201, varied seed 2207,
  and three capture-free performance launches. Each full positive trace has
  220,256 timestamped samples; all 32 initial bodies pass complete lifetime arcs.
- Initial positions form a nonoverlapping 4x4x2 grid. All axes have 32 distinct
  seeded linear and angular velocities spanning the original ranges. Upward
  launch Y is 4.5..7.5m/s, X/Z -3.5..3.5m/s, spin -12..12rad/s per axis.
- Seed 1201 measured apex range 1.229867..3.159523m, first ground contacts ticks
  57..92, first natural sleep ticks 139..296. Seed 2207: apex
  1.246006..3.230938m, contacts 56..93, natural sleep 140..298.
  Maximum gravity+damping integration residual is 0.00007112m/s² across these
  positive arcs, below unchanged 0.003 tolerance. All 32 rise, spin, descend,
  contact, rebound, tumble and settle on the ground; late speed <0.015m/s.
- All first-burst bodies remain full size seven seconds; only drawing shrinks
  during second eight. Collision boxes are never resized; TTL retires at >=8s
  and <8.02s. Explicit clear, three restarts and paused lifetime all pass.
- Six simultaneous bursts reach exactly 192 physical bodies. Repeated groups at
  ticks 630 and 900 keep the cap at 192 and exercise active and sleeping eviction.
  The separate mixed-height fixture proves younger sleepers are retired before
  older active bodies. Sustained overload may retire older active fragments at
  age two seconds: this is the original accepted cap policy, not an unconditional
  eight-second lifetime at arbitrary burst rates. Full newest bursts survive.
- Full-lifetime first burst: all 32 rebound and settle. Stress groups born at
  ticks 510/630/900: 192/96/96 bodies all rise, descend, contact, spin and tumble;
  sampled rebounds 188/96/95, natural sleep before eviction 96/95/96. Do not
  claim every cap-retired stress fragment completes a full settled arc.
- Capture/rerun normalized physics is identical for 156,704 samples through
  tick 1389, including every stress burst. SHA256:
  ea0f0c88c5b0ea62ff3833464b6ee5d16ca42ebd80e5202c59ccb950bf55692a.
  This matches historical node 10 data; it is not cross-platform determinism.
- Eight destruction checker mutations are rejected. Actual no-gravity and
  no-ground engine runs each exit 1 and independently fail trace validation
  (no descent / no ground collision). Original failures and all logs are kept.

## Unchanged reference performance gate

Filter: frames with exactly 192 bodies, physics ticks 510..1109 inclusive.
No removed outliers. Original lightweight --performance workload, 60Hz physics,
1280x720, --disable-vsync --max-fps 60. p95 is sorted[ceil(0.95*n)-1].
Target remains p95 <=33.3ms; scripts/check_frame_target.py passes all three runs.

Run       samples  median ms  p95 ms   max ms  physics monitor p95 ms
perf1     379      26.278     30.520   39.598  4.723
perf2     388      25.7525    29.430   32.548  4.730
perf3     400      25.0745    29.495   34.191  6.635

These are reference VM measurements, not a claim of 60 rendered FPS. The Godot
physics monitor is sampled instrumentation, not precise body profiling.
Instrumented capture/full-CSV run p95 is 33.863ms (FAIL relative to the numeric
target, with 14 capture-overlap frames); the full-CSV rerun/2207 p95 values are
33.089/32.654ms. All distributions and outliers are retained. Instrumented runs
are not substituted for the unchanged capture-free acceptance workload.

## Rendering evidence and node 9 handoff

32 actual engine PNG frames, 29 distinct hashes, cover launch through natural
rest, shrink and cleanup plus repeated simultaneous bursts. JSON has requested
and observed ticks and UTC wall time; timestamps are not an invented fixed-rate
movie. Physics/contact/sleep counts are correlated at the observed tick.
Pixel decoding, frame differences and sleeping render/body pose agreement pass.
These checks establish actual nontrivial changing renderer output and physical
behavior, NOT subjective realism or independent visibility of every fragment.

After extracting raw-runs.tar.gz, inspect evidence/destruction/n4s136-capture/:
- frame_0010/0030: early launch/flight (observed ticks 14/31).
- frame_0060: first contacts while other blocks remain airborne.
- frame_0090 through frame_0150: dense contact/rebound/tumble sequence.
- frame_0210: 18 sleepers; frame_0300 and frame_0390: all 32 asleep.
  The latter two have identical pixels, as expected for a resting scene.
- frame_0450/0479/0490: shrink and physics cleanup. Nearly vanished final-second
  meshes can be subpixel before physical retirement; no early collider cleanup.
- frame_0511/0540/0600, frame_0631/0660/0720 and frame_0900/0930/1020:
  simultaneous and repeated stress arcs. frame_1190: 96 sleeping bodies;
  frame_1385: complete stress TTL cleanup.

Subjective destruction weight, convincing ground interaction, readable small
block silhouettes/depth/spin, satisfying payoff duration under cap pressure,
and crowded-scene player/enemy/projectile readability remain UNASSESSED.
Carry these explicitly to node 9 human playtest on the integrated exact Linux
release, including repeated simultaneous breaks. No screenshot was visually
perceived here; no vision infrastructure was probed and no vision blocker is
reported. No audio implementation, audio acceptance or root fun claim is made.

For an optional focused interactive fixture on a graphical Linux desktop:
    "$GODOT_BIN" --path game res://destruction_demo.tscn --rendering-method gl_compatibility
B breaks three targets; N resets; Esc pauses. This fixture is not the full game
loop and does not replace node 9 exact-release playtesting.

## Reproduce and inspect

From the repository root (Python 3.14.4, ffmpeg and xvfb-run were used):
    export GODOT_BIN=/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64
    python3 evidence/destruction-node4-rerun/rerun.py controller-fresh-01
    python3 evidence/destruction-node4-rerun/analyze.py controller-fresh-01

Use a new prefix every time; the helper refuses existing log/output directories.
The helper invokes existing runners/checkers without modifications, explicitly
expects exit 1 for both negatives, runs performance serially and enforces the
unchanged hard gate. Exact individual commands, engine argv, environment, wall
start times, exit codes, source commit and SHA256 are in n4s136-commands.json and
raw per-run launch.json. analyze.py also verifies preserved source and render
batching and checks the historical physics hash; it creates no synthetic poses.

To inspect archived original evidence from the repository root:
    tar -xzf evidence/destruction-node4-rerun/raw-runs.tar.gz
    python3 scripts/check_destruction.py evidence/destruction/n4s136-capture evidence/destruction/n4s136-rerun evidence/destruction/n4s136-seed2207 --self-test --negative evidence/destruction/n4s136-no-gravity --negative evidence/destruction/n4s136-no-ground
    python3 scripts/check_frame_target.py evidence/destruction/n4s136-perf1 evidence/destruction/n4s136-perf2 evidence/destruction/n4s136-perf3 --output /tmp/g12-node4-performance-review.json

Archive members preserve repository-relative paths. artifact-manifest.json lists
every raw member size/SHA256, verified by reading the archive before removing the
loose generated copies. SHA256SUMS covers delivered evidence and this report.
Engine import caches are incidental ignored files, not evidence artifacts.
