# G12 node 2 step 138: focused fresh renderer verification

Assigned execution result, not durable node completion or contract acceptance.
Tested source revision: 954782e0fb5b6b535ce99168795872ae56ad4c16
Repository: git@github.com:rickseeger/ai-game-05.git

Read the durable node-2 contract and accepted node-1 design/prerequisite evidence,
latest step-137 review, handoff and task contract, and current renderer/tests.
The previously referenced /tmp/g12-node2-validation-lHPoSz directory IS available;
its dense-check.json is readable. No historical result was substituted for a
fresh run. No mission state, production source, existing tests or contract changed.
No reproducible renderer/camera defect was established; no speculative fixes.

## Actual execution

Reused the existing step-137 runner with a fresh step-138 output prefix. Godot
4.5.1 f62fdbde1 on actual Linux X11/Xvfb, OpenGL 4.5 Compatibility, Mesa 26.0.8,
llvmpipe LLVM 21.1.8. Dummy audio explicitly selected. Not headless rendering,
MovieWriter, invented images or vision-based review. The driver warns that V-Sync
settings are unsupported; retained logs have no script errors in successful runs.

Nine fresh renderer launches: three arena sizes, negative camera, real-time tour,
and analytic/dense fixtures at each reference size. Expected process statuses:
all 0 except deliberately narrow-FOV camera 1. Arena checker 0; runner 0;
final focused concerns.py analysis 0. Exact argv/cwd/status in commands.json;
underlying Godot argv, environment, source hashes and exit codes in launch.json.

337 focused assertions pass at EACH 1280x720, 960x720 and 1680x720. Resizing the
live Window refits the camera while actor/airborne movement leaves it locked.
Reference frame margins: 0.085760951 / 0.081639051; minimum projected cube widths:
6.084229 / 5.441956 pixels. Negative FOV fails 162 assertions. Five arena report
mutations and four pixel-report mutations are rejected, not mistaken for passes.

Real-time tour: 720 frames, 16.519138 engine seconds, six distinct saved images,
peak fixture height 8m. Post-warmup median 22.727273ms, p95 25.212048ms. This is
seven nonphysical presentation cubes, NOT dense performance or laptop capability.

Analytic: 40 sampled poses per reference size; color/clean/ID/isolated renderer
passes. Minimum actor retention 0.659004 / 0.633987, contact 0.836735 / 0.731507.
Dense: 192 production RigidBody3D fragments, two sentries, six snapshots at ticks
1,12,30,60,90,120 per size; poses/velocities frozen identically during diagnostics.
Existing pixel guardrails pass. Minimum fragments with >=3 ID pixels: 136 / 133.
Minimum shadow-darkened non-debris pixels: 2976 / 2367. Identical near/far boxes
produce 1402/547 and 956/426 magenta pixels. Perspective Camera3D, BoxMesh geometry,
world rays/collision, depth-tested occlusion, projected height separation and
shadow differences establish genuine 3D rendering, not a 2D imitation.

## Focused investigation, not a visibility-of-every-piece requirement

concerns.py adds independent mathematical projection, checked against two engine
projected landmarks to <0.001 pixel, plus per-snapshot world/depth/height and
pixel-difference measurements. Every sampled fragment center WITHIN the configured
26x26x8m visual envelope is on-screen. Dense tick 30 has all 192 centers above 1m;
tick 60 maximum height is 2.974934m. Nonzero production-frame pixel differences
confirm changing rendered frames. Ground rays, contact rings and shadow pixels
are technical depth/contact evidence, not a judgment of convincing weight.

Actor occlusion reproduces: at tick 12 retention is 125/459 (27.23%) cyan-region
pixels at 720p, 153/413 (37.05%) at 4:3. Tick 30 recovers to 94.34% / 84.75%,
with later samples near/full retention. These are sparse local color-class
samples, not whole-body percentages, OCR, continuous occlusion duration or proof
that a human can track the actor. Existing guardrails pass; subjective tolerability
remains for node 9. Do not infer no occlusion between captured ticks.

The three-of-seven fixture is tour_0360_12. At 720p combined ID counts are
[196,35,0,0,0,0,73], isolated [201,115,29,0,0,0,73]. At 4:3 they are
[132,27,1,0,0,1,57], isolated [137,81,18,0,0,2,58]. Minimum center margins are
105.766918 / 148.128297 pixels. Thus some loss is inter-fragment overlap and some
is occlusion by the rest of the scene even with other fragments hidden. It is
not evidence of camera framing failure or a requirement to expose all seven.

The initial new analysis attempted an overbroad all-centers-in-frame assertion
(exit 1), then an all-isolated-cubes-visible assertion (exit 1). Investigating the
actual data, rather than changing the game to satisfy those assumptions, found:
IDs 111 and 128 travel beyond the floor (z=14.904 / 15.204m) and below ground
(y=-2.890 / -4.033m) by dense tick 120. Both are offscreen at 720p; only ID 128
at 4:3. The floor is 24x24m and walls 0.75m high. The camera promises the bounded
arena/airborne envelope, not escaped falling fragments. Final analysis records
all these exceptions and enforces the existing in-envelope framing constraint.
No global all-fragments-visible requirement was invented. Boundary behavior is
carried to the human/destruction handoff, not silently declared correct physics.

## Rerun and evidence

From repository root on Linux with Xvfb/xauth/Mesa and ffmpeg available:

    ./scripts/setup.sh
    export GODOT_BIN="$PWD/.tools/Godot_v4.5.1-stable_linux.x86_64"
    /usr/local/lib/hermes-agent/venv/bin/python docs/node2-s137/rerun.py --prefix controller138 --report-dir /tmp/controller138-report
    /usr/local/lib/hermes-agent/venv/bin/python docs/node2-s138/concerns.py --prefix controller138 --output /tmp/controller138-report/concerns.json

The executed run used GODOT_BIN at
/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64.
Use UNUSED output names. Interpreter requires Pillow 12.3.0 and NumPy 2.4.3;
a uv venv with those packages is an alternative to the recorded interpreter.
Source/binary hashes and host details: provenance.json. Captures have actual UTC
filesystem save timestamps in concerns.json; tour.json has frame/elapsed time,
dense.json has physics ticks (tick/60), analytic records have fixture step offsets.
Diagnostic capture pauses must not be confused with live simulation time.

    sha256sum -c evidence/node2-s138/SHA256SUMS
    tar -xJf evidence/node2-s138/runtime-evidence.tar.xz

The archive contains raw runs and runner logs, verified member-by-member against
artifact-manifest.json. All 886 actual PNGs retained losslessly, including negative
and diagnostic images. Production crowded sequences are listed in node9-handoff.json.
Existing game source and tests are unchanged; only new docs/evidence are committed.
Evidence commit SHA is in the worker delivery, not self-referenced in this report.

Visible desktop camera launch (not offscreen server validation):

    "$GODOT_BIN" --path game res://arena_preview.tscn --rendering-method gl_compatibility

Resize and observe corners, ground contact and high debris. The destruction fixture
can be launched with res://destruction_demo.tscn (B rupture/N reset). Neither is
presented as a finished game. Subjective readability, satisfaction, comfort and
exact-release human acceptance stay at node 9. No vision configuration is required;
no subjective visual inspection, input/combat/destruction/audio/root acceptance,
or durable node completion is claimed.
