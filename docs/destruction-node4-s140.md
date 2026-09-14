# G12 node 4, step 140: independent Linux destruction verification

Assigned execution finished: technical checks pass. This is not a durable node
completion or root acceptance decision. Subjective visual quality belongs to the
node 9 human playtest under the current user instruction; it is not a worker
capability blocker. No vision configuration was sought and no audio was added.

## Unchanged completion contract

Prerequisites: accepted engine choice and runnable arena. Outcome: destroyed targets visibly break into many small blocks with varied upward launch velocities and random angular velocities; fragments rise, spin, descend under gravity, collide with the ground, bounce, tumble or roll, and settle. Preserve readable impact weight through appropriate mass, friction, restitution, and timing. Bound active debris and cleanup without making the payoff vanish prematurely. Evidence: source, seeded automated tests for breakup counts, varied linear/angular velocities, gravity, collision/rebound, settling, and cleanup; timestamped runtime telemetry plus frame sequences or recordings covering the complete destruction arc. Validation: independently rerun destruction in the actual engine and inspect launch, flight, impact, and settling, including repeated simultaneous breaks and measured performance. Cosmetic particles or preanimated trajectories do not satisfy rigid-body behavior.

## Prerequisites, source, and scope

Fresh clone/fetch of git@github.com:rickseeger/ai-game-05.git yielded main
29d4c115fa798666952436b5aa27c9bfee26eba3. All actual-engine evidence below uses
that revision. The delivery changes only evidence, analysis, and this report;
no game code, original tests, benchmark, threshold, camera, or audio changed.
The requested author identity was configured before committing. No harness or
mission-tree state was read or modified. Node 1/3 acceptance and node 10
remediation are prerequisites supplied by the task packet, not newly invented
controller decisions. A fresh arena launch independently passes 337 assertions,
its image/framing checker, and five checker mutations.

Read the prior node-4 rerun, original destruction validation/design, node-10
performance remediation, game source, engine tests, runners, and analysis code.
Older reports retain their historical failures/status; this report is the current
execution result and does not reinstate their obsolete worker-vision blocker.
No demonstrated production defect justified a targeted game repair. The only new
checker, check_phases.py, makes the already-measured frame/physics timestamp and
motion/rest correlation explicit, without changing workload or acceptance gate.

Production source is game/destruction.gd, game/debris_block.gd and
 game/destructible_target.gd. Every fragment is an independent RigidBody3D with a
BoxShape3D, simulated by GodotPhysics3D. MultiMesh rendering copies real engine
body transforms, not preanimated paths. The body observer records solver contacts
but never sets forces/poses/sleep. The unchanged service uses 0.34m boxes, 0.3kg
mass, friction 0.65, restitution 0.42, linear/angular damping 0.12/0.18, CCD and
world-only collision. Debris does not collide with other debris or obstruct actors.
These are existing deliberate design choices, not reduced verification physics.

## Fresh actual execution and technical coverage

Runs began 2026-09-14 00:32:02 UTC; final physics comparison began 00:36:46 UTC.
All engine launches were serial, in independent fresh processes/directories.
Godot 4.5.1 official f62fdbde1, Linux x86_64 kernel 7.0.0-31-generic, four exposed
logical CPUs / AMD EPYC 9354P, X11/Xvfb, Compatibility software OpenGL, llvmpipe
LLVM 21.1.8, 1280x720, Dummy audio. Exact command lines, binary hash, source hashes,
environment, wall timestamps and exit codes are retained. No headless physics,
MovieWriter, laptop/GPU performance, or audible observation is claimed. This is a
shared host; external scheduling was not controlled.

Six positive destruction launches pass all 34 unchanged engine assertions each:
capture seed 1201, independent seed-1201 rerun, seed 2207, and three lightweight
performance runs. Each full positive trace contains 220,256 timestamped samples.
Independent Python checks establish the following:

- Pylons yield 32 nonoverlapping boxes in a 4x4x2 grid; sentinels yield 16. Target
  mesh/collider removal precedes breakup in the same tick and repeated lethal
  damage does not duplicate breakup. All three linear/angular axes have 32
  distinct seeded values. Launch Y is 4.5..7.5m/s, X/Z -3.5..3.5m/s, angular
  velocity -12..12rad/s on each axis, with broad observed variation.
- All 32 original fragments in every full positive run rise, spin, descend,
  contact the actual ground, rebound, tumble and naturally sleep. Seed 1201
  apex range is 1.229867..3.159523m, first contact ticks 57..92, first sleep
  139..296. Seed 2207 gives 1.246006..3.230938m, contacts 56..93, sleep 140..298.
  Maximum gravity+damping integration residual is 0.00007112m/s², below the
  unchanged 0.003 tolerance. Late speed is below 0.015m/s and resting centers
  are 0.10..0.30m above ground. Ground-adjacent quaternion changes demonstrate
  tumbling rather than treating cubes as smooth rolling spheres.
- All original fragments remain full-size through seven seconds. Only meshes
  shrink in the final second; collision boxes are never scaled. TTL retirement
  is at least 8s and less than 8.02s. Explicit clear, three restart cycles,
  pause-frozen lifetime, and complete stress cleanup all pass.
- Six simultaneous bursts reach exactly 192 physical bodies. Further groups at
  ticks 630 and 900 exercise active and sleeping cap eviction without exceeding
  192. The mixed-height fixture proves younger sleepers are evicted before older
  still-active falling bodies. The cap preserves full newest bursts; under
  sustained overload it may retire older active fragments at age two seconds.
  Eight seconds is NOT an unconditional lifetime under arbitrary overload.
- Stress groups born at 510/630/900 have 192/96/96 bodies; all rise, fall, contact,
  spin and tumble. Sampled rebound counts are 188/96/95 and sleep-before-eviction
  counts 96/95/96. Do not claim every cap-retired body finishes a settled arc.
- Capture and independent rerun match all 156,704 normalized samples before tick
  1390, including every stress burst. Hash:
  ea0f0c88c5b0ea62ff3833464b6ee5d16ca42ebd80e5202c59ccb950bf55692a.
  This also matches historical node-10 physics. Later asynchronous pause/cap
  fixtures pass assertions but are excluded from this exact-hash comparison.
  This proves same-VM repeatability, not cross-platform determinism.
- Eight checker mutations are rejected. Fresh actual no-gravity and no-ground
  launches each exit 1 and fail both engine checks and independent physics checks
  (no descent / no ground collision). Both intentional failures are preserved.

Provenance analysis verifies current game hashes equal launch hashes, original
engine tests/runners/body observer/adapter/demo are byte-identical to node 10,
and the ring batching function is unchanged. The previously committed debris
surface shader is the only destruction-service difference from node 10; physical
parameters/lifetime/cap behavior remain unchanged.

## Unchanged reference performance gate

Original --performance workload, 60Hz physics, --disable-vsync --max-fps 60.
All frame intervals with exactly 192 bodies at ticks 510..1109 are retained;
no removed spikes. p95 = sorted[ceil(0.95*n)-1], target <=33.3ms.
The hard check_frame_target.py gate passes all three fresh capture-free runs.

Run      n     median ms  p95 ms  max ms  physics-monitor p95 ms
perf1    376   26.4035    31.504  38.431  5.100
perf2    381   26.216     29.654  33.581  6.276
perf3    377   26.193     31.622  36.746  5.467

This is not a claim of 60 rendered FPS or guaranteed laptop speed. The physics
monitor is sampled instrumentation, not exclusive rigid-body profiling.
Instrumented capture p95 is 34.974ms (numeric target miss, 14 capture-overlap
frames); full-CSV rerun is 33.257ms, full-CSV seed2207 is 33.307ms (numeric miss).
All raw distributions remain. These heavier runs are not substituted for the
unchanged lightweight acceptance workload, nor are their misses hidden.

## Rendered phases and node 9 handoff

32 actual PNGs, 30 distinct hashes, cover the complete original arc and repeated
stress groups. n4s140-frames.json joins each requested/observed physics tick and
UTC timestamp to actual pixel measurements and body/contact/sleep counts.
check_phases.py independently asserts timestamp ordering, body-sample/capture
lag under one second at the same observed tick, actual changed launch/contact/
shrink/stress pixels, pixel-identical natural rest, and empty cleanup frames.
Capture is asynchronous: observed tick, not filename, is the correlation key;
this is a timestamped sequence, not a fabricated constant-frame-rate recording.

Files below are under evidence/destruction/n4s140-capture/ after extraction:
- frame_0010 (observed tick 13): 32 bodies, no contact, 3,120 changed pixels.
- frame_0030 (31): flight, no contact, 6,396 changed pixels.
- frame_0060 (61): 4 solver-contact bodies, 12,115 changed pixels.
- frame_0090..0150: dense contact/rebound/tumble interval; frame_0150 (151)
  has 20 contacting bodies, 2 sleepers, 6,307 changed pixels.
- frame_0210 (210): 17 sleepers, 6,239 changed pixels.
- frame_0300 (301) and frame_0390 (390): all 32 asleep; identical pixel hashes.
- frame_0450: shrink, 5,467 changed pixels. frame_0479 has tiny meshes near TTL;
  frame_0490 has zero physical bodies (only one pixel changes from 0479).
- frame_0511/0540/0600: six simultaneous bursts, exactly 192 bodies.
- frame_0631/0660/0720 and frame_0900/0930/1020: repeated overload at the cap.
- frame_1190: 96 sleeping bodies. frame_1385: no remaining stress bodies.

Pixel differences include shadows/UI and do not prove independent visibility of
every block. Physical contact/spin/rebound are measured in engine telemetry, not
inferred from image interpretation. Rendering/body pose agreement is also tested
at rest. No subjective visual assessment was performed or claimed.

Node 9 must judge convincing weight/ground interaction, small-block silhouette,
depth/spin readability, satisfying payoff duration under cap pressure, crowded
player/enemy/projectile readability, and real laptop smoothness in the integrated
exact Linux release. This is the current human handoff, not a worker blocker or
root satisfaction declaration. No audio acceptance or implementation is included.

## Reproduction and durable artifacts

From the repository root, with a NEW prefix for every rerun:

    export GODOT_BIN=/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64
    python3 evidence/destruction-node4-rerun/rerun.py controller-n4-fresh-140
    python3 evidence/destruction-node4-rerun/analyze.py controller-n4-fresh-140
    python3 evidence/destruction-node4-rerun/check_phases.py controller-n4-fresh-140

Use scripts/setup.sh if the pinned binary is absent. Python 3.14.4, xvfb-run and
ffmpeg are needed. Runners refuse existing output directories and explicitly
expect exit 1 for runtime negatives. Exact per-run commands are recorded in
n4s140-commands.json and per-run launch.json, not merely these summary commands.

To inspect this delivery without launching new engine processes:

    tar -xzf evidence/destruction-node4-rerun/n4s140-raw-runs.tar.gz
    python3 evidence/destruction-node4-rerun/analyze.py n4s140
    python3 evidence/destruction-node4-rerun/check_phases.py n4s140
    python3 scripts/check_frame_target.py evidence/destruction/n4s140-perf1 evidence/destruction/n4s140-perf2 evidence/destruction/n4s140-perf3 --output /tmp/n4s140-controller-performance.json

The archive preserves repository-relative paths for all fresh raw runs and
console logs, including negatives and PNGs. n4s140-artifact-manifest.json lists
every member with size and SHA256; the archive was read back and every member
verified before loose generated copies were removed. n4s140-SHA256SUMS covers
all delivered analysis files, archive, new checker and this report. Engine import
caches are incidental ignored runtime files, not authored work products.
