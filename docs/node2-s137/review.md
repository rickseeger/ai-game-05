# G12 node 2, step 137: fresh Linux renderer and camera verification

Execution result for independent controller review, not durable node acceptance.
Read the full completion contract (task-contract.json), accepted docs/design.md,
evidence/arena/prerequisite.json and prerequisite-verification.json, current main,
renderer source/tests, and existing arena and step-135 evidence. The recorded
node-1 prerequisite is independently contract-validated. No mission state changed.

Tested source: 89f1f7be6c5b8321c2f6d0e326c21fad75e9ad1e, fresh clone of
 git@github.com:rickseeger/ai-game-05.git.
All game/ and scripts/ files are unchanged from previously independently validated
8f311f7643d493e7fa5be11d88feb97c93261ff4. That prior result was NOT reused as a fresh
pass: nine new actual-renderer launches and fresh image analysis were executed.
No reproducible technical renderer defect was found, so no production/test code
was redesigned or altered. This commit adds only execution/evidence documents.

## Fresh observed results

- Actual Godot 4.5.1 stable f62fdbde1, X11/Xvfb, Compatibility OpenGL 4.5,
  Mesa 26.0.8-1ubuntu0.3 llvmpipe LLVM 21.1.8; explicit Dummy audio. No headless
  renderer, MovieWriter, synthetic images, image-perception service or audio claim.
  Engine emits the preserved unsupported V-Sync-setting warning, not script errors.
- 337 assertions pass at EACH of 1280x720, 960x720 and 1680x720. World dimensions,
  collision/rays, perspective, full frustum, camera stability, ground aiming and
  actual live Window.size refit are exercised. Independent PNG decoder checks
  projected amber pixels and seven distinct scene/resize captures per suite.
- Reference sizes have minimum frame margins 0.085761 / 0.081639, minimum projected
  cube width 6.084229 / 5.441956 pixels. Fixed camera changes distance on resize,
  not when the actor or airborne fixture moves; corners and height are sampled.
- Actual 12-degree-FOV negative exits 1 and fails 162 assertions. Five arena-checker
  report mutations and four pixel-checker report mutations are rejected.
- Ordinary real-time tour completes 720 frames, 16.516667 engine seconds, locked
  camera, full ground traversal and peak fixture height 8m. Six distinct captures
  and per-frame trace retained. Post-warmup median 22.222ms, p95 25.110ms: seven
  nonphysical presentation cubes ONLY, not a 192-body or laptop benchmark.
- Fresh analytic visibility runs: 40 sampled poses at each reference size, with
  actual color, clean, depth-tested IDs and individual-cube diagnostic renders.
  Existing engineering guardrails pass; minimum actor-region retention 65.90% /
  63.40%, contact-region retention 83.67% / 73.15%, label-region retention 100%.
- Fresh production-service dense runs: 192 actual RigidBody3D fragments, two active
  sentries, six sampled ticks (1,12,30,60,90,120), both reference sizes. Poses and
  velocities stay identical through paused diagnostic passes; camera stays fixed.
  All existing dense pixel guardrails pass. At least 136 / 133 cubes have three
  depth-visible ID pixels. Minimum shadow-darkened non-debris pixels 2976 / 2367.
- Real renderer perspective oracle: identical near/far one-meter boxes yield
  1402/547 pixels at 720p and 956/426 at 4:3. Together with Perspective Camera3D,
  BoxMesh/3D world geometry, spatial queries, height separation, depth occlusion
  and actual shadow differences, this confirms true 3D rendering, not a 2D imitation.

arena-checks.json, pixel-checks.json and summary.json hold exact fresh measurements.
No historical before/after comparison was rerun: test_visibility.run was reused
with before=[] for current analytic/dense bounds and mutation checks only. No
claim of a new camera improvement or baseline rejection is made in this session.

## Scope and human handoff

These are technical framing/depth/contact/occlusion measurements, NOT proof of
subjective legibility, satisfying destruction, visual comfort or fun. Ground rays
and contact-ring/shadow pixels support ground-contact cues; they cannot judge
whether those cues feel convincing in motion. No input/combat/destruction/audio
contract or release-wide gate is accepted by this node-2 run.

Carry node9-handoff.json and its exact production crowded-burst frames to NODE 9
for human playtest under the current user instruction. No image-perception repair
was attempted or needed; inability to see captures is not a technical blocker or
reason to keep redesigning this renderer. This handoff documents remaining
judgments; it does not silently waive them or claim any node durably complete.

Particularly: dense tick-12 actor-region retention is 27.23% / 37.05%, so most of
the sampled cyan region is briefly hidden. Minimum dense label-region retention
is 87.27% / 78.83%. The tight analytic fixture still exposes only three of seven
pieces above the three-ID-pixel threshold. Region retention is NOT a whole-body
visibility percentage, OCR, human recognition, or the ability to track hidden
pieces. Human review must decide whether these transient occlusions are acceptable.

## Durable artifacts and exact reproduction

The lossless archive evidence/node2-s137/runtime-evidence.tar.xz contains 923 files,
including 886 actual renderer PNGs, all raw launch.json/engine.log records, fixture
and production-pose traces, and runner logs. artifact-manifest.json enumerates every
member with size and SHA256. Every member was read back and hash-verified before
removing loose duplicates. The archive SHA256 is in evidence/node2-s137/SHA256SUMS.

From repository root, inspect original evidence:

    sha256sum -c evidence/node2-s137/SHA256SUMS
    tar -xJf evidence/node2-s137/runtime-evidence.tar.xz

Ordinary views: evidence/arena/n2-s137-{720p,4x3,wide}/*.png
Animated tour: evidence/arena/n2-s137-tour/tour_*.png
Crowded production views: evidence/arena/n2-s137-dense-{720p,4x3}/dense_*_color.png
Analytic production views: evidence/arena/n2-s137-analytic-{720p,4x3}/*_color.png
Other PNG suffixes are measurement diagnostics, not production appearance.

commands.json preserves runner/checker argv, cwd, return codes and logs; each
archived launch.json preserves the actual Godot/Xvfb argv and environment. Source
hashes, exact source SHA, engine SHA/version and host are in provenance.json.
The evidence-only commit SHA is reported separately in the worker delivery so
there is no self-referential commit hash inside committed files.

Install pinned engine with scripts/setup.sh or reuse the verified executable:

    export GODOT_BIN=/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64

Pixel interpreter used: /usr/local/lib/hermes-agent/venv/bin/python, Pillow 12.3.0,
NumPy 2.4.3. Alternatively install those exact packages into a uv venv. Linux needs
Xvfb/xauth/Mesa and ffmpeg. Run the complete fresh independent verification into
UNUSED output names (it reuses existing production tests without changing them):

    /usr/local/lib/hermes-agent/venv/bin/python docs/node2-s137/rerun.py --prefix controller137 --report-dir /tmp/controller137-report

That executes both reference sizes, wide size, negative camera, 720-frame tour,
both analytic and both dense runs, PNG analysis and all regression guardrails.
Read /tmp/controller137-report/arena-checks.json and pixel-checks.json afterwards.
Historical camera before/after comparisons are intentionally out of scope.

Visible Linux desktop launches for human review (no Xvfb on the real desktop):

    "$GODOT_BIN" --path game res://arena_preview.tscn --rendering-method gl_compatibility
    "$GODOT_BIN" --path game res://destruction_demo.tscn --rendering-method gl_compatibility
    "$GODOT_BIN" --path game res://opposition.tscn --rendering-method gl_compatibility

Resize the preview; watch rear corners/high flight and near-ground overlaps.
The destruction demo has B rupture / N reset fixture keys. These are concern
fixtures, not the completed root game; node 9 still needs the exact-release human
playtest and the subjective/audio judgments called out in the handoff.
