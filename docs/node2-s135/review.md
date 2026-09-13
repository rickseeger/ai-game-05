# Node 2 step 135: a measured camera correction, not visual self-acceptance

Execution finished for independent controller validation. No node/tree state was
changed. No input, combat, destruction, sound, enjoyment or root acceptance is
claimed. Design and feasibility prerequisite was read from the accepted record
in evidence/arena/prerequisite.json, alongside docs/design.md, existing source,
docs/arena-validation.md, docs/node2-s132/review.md, the latest step-133 work and
node-10 performance-remediation documentation. No vision provider was probed,
repaired or used; final subjective visual judgment remains with the human playtest.

## Source and narrow intervention

Fresh baseline: aef37d7 (full SHA in provenance.json).
Camera and new pixel tests: 4bab1cf5822fa4bf67b0e4df7ed3dcf43a1979d1.
Final diagnostic barrier fix: 989d70a6554b676557fd2ea39ab9bdff14088694.
Both commits authored by the gardener <root@g.seeger.net>. The evidence commit
adds only durable records and packaging. Every launcher records its source hash.

The ONLY production change is camera direction Z/Y ratio 0.9 -> 1.2, retaining
zero yaw, the stable arena-locked perspective view, 52-degree FOV, envelope,
lighting, shadows, depth tests and live aspect-ratio refit. It is slightly
shallower, increasing the screen separation of elevation from ground. This is
not a following camera, an x-ray layer, debris transparency, a reduction in the
number of fragments, a fake 2D solution, or a change to the replay trajectories.

The already-corrected step-133 extraction label stays beside its original ring.
Its analytic replay color pixels remain unoccluded, so it was not moved again.
Every other pre-existing game file is byte-identical to baseline. In particular,
Arena.ring is also identical to node 10 f6631e4: the forty markers remain one
MultiMesh batch. Pylons, colliders, world, player, opponents, RNG, physics, burst
counts, lifetimes, limits, fragment shader and destruction batch are unchanged.

A steeper change in the same direction (Z/Y=1.5) was measured and rejected: while
it improved cyan retention further, the analytic exit-region minimum fell to
70.47%. Both candidate suites and captures are preserved. The retained 1.2 is a
bounded compromise, NOT a claim that a camera can reveal fully occluded faces.

## What the new evidence actually measures

scripts/run_visibility.py launches the actual preview via X11/Xvfb OpenGL.
visibility_tests.gd replays the original eight crowded cases from step 133 at
five sample times each: -0.2,-0.1,0,+0.1,+0.2 seconds about the original center.
These are analytic presentation poses, not physical destruction or recorded
continuous motion. Every before/after position and rotation is checked equal.

At each pose the real renderer saves:

- *_color.png: unchanged production appearance.
- *_clean.png: counterfactual with decorative debris hidden, only for measurement.
- *_ids.png: depth-tested material IDs on all seven cubes, not production color.
- *_solo0..6.png: each cube individually rendered with the other cubes hidden;
  world and actor depth occlusion remain. No projection rectangle is counted as
  a visible surface. These ID frames are diagnostic actual renders, not art.

Python decodes actual PNGs, counts each cube ID and compares all/solo surface
pixels. A zero solo area means the world/actor itself hides that piece; the
reported mean assigns it zero, rather than pretending to resolve it. Cube ID
counts measure rendered depth visibility, not whether the eye can track a cube.
Touching-ID RGB edge contrasts are also reported; they do not uniformly improve.

Cyan/mint color-class pixels in fixed local image neighborhoods are compared
pixel-for-pixel against the clean render. These are region-retention proxies,
NOT segmentation of the entire actor body, OCR, percentages of complete physical
surface area, or proof that a word is readable. The cyan actor neighborhood can
include parts of its ground ring; the separate contact region samples that ring.
Shadows can also affect color thresholds. All reference/retained pixel counts,
regions and formulas are public in check_visibility.py and pixel-checks-v2.json.

For actual destruction, dense_visibility_tests.gd launches opposition.tscn,
waits for the normal two sentries to spawn, then destroys the three actual pylons
and injects three additional production-service bursts near actor/exit/center.
Exactly 192 normal RigidBody3D cubes remain through six sampled physics ticks
1,12,30,60,90,120. Opposition stays active during the live intervals; no threat
settings or code are changed. This is a deliberate renderer stress placement,
not a claim that normal gameplay produces six simultaneous pylon ruptures.

Only diagnostic snapshots pause the whole simulation. The same production
MultiMesh renders all cubes, first normally, then hidden, then with material IDs,
then with sun shadows disabled to measure actual shadow-darkened pixels. Poses
and velocities are asserted unchanged across diagnostic passes. Before/after
captures at each size have exactly equal 192-body physics snapshots and the same
two sentries. These snapshot timings are NOT a real-time performance benchmark.

Two additional actual images render identical one-meter boxes at near/far ground
positions. Their measured pixel areas, not just projected coordinates, differ:
1280x720: 1402 vs 547 pixels; 960x720: 956 vs 426 pixels. Actual material-ID depth
occlusion, perspective Camera3D/BoxMesh geometry, ray tests and shadow differences
together establish genuine 3D rendering, not a 2D imitation.

## Results and residual tradeoffs

See metric-summary.txt and pixel-checks-v2.json for exact numbers. Analytic minimum
cyan-region retention improves 55.62% -> 65.90% at 720p and 55.85% -> 63.40% at 4:3.
Mean cube visible/solo fraction improves 68.17% -> 70.62% and 68.40% -> 71.11%.
Minimum footprint-region retention improves 72.65% -> 83.67% and 72.63% -> 73.15%.
The label region retains 100% of sampled mint reference pixels at both sizes.

Tradeoff: analytic exit-ring-region retention decreases 86.46% -> 83.53% and
87.57% -> 78.00%. The label remains unobscured in those same samples; the actual
floor ring is still partly crowded. Seam contrast rises at 720p but declines
slightly at 4:3. This is not an across-the-board aesthetic improvement.

In the production dense sequence, at least 133 of 192 fragments have three or
more depth-visible pixels in every sampled final frame; at the peak spread all
192 do. At the crowded 12-tick state, cyan-region retention improves from 20.71%
to 27.23% at 720p, and 24.46% to 37.05% at 4:3. Exit-region retention at that state
improves from 48.90% to 57.19% and 47.06% to 60.80%. Cyan reference pixels do not
vanish, but most are briefly hidden in that deliberately dense near-player burst.
At tick 30 the final cyan-region retention is 94.34% / 84.75%; it largely recovers.
Actual destruction also crosses the label later: minimum mint-region retention
is 87.27% / 78.82%. Thus the analytic label success is not extrapolated to every
possible physical burst. Exact dense values live in the final pixel report.

The tight seven-cube fixture still has only three pieces with at least three
visible ID pixels in its worst near-ground state. Hidden middles cannot be
counted or tracked from opaque images. Region identification, hovering clearance,
per-piece tracking and the acceptability of short occlusions need human motion
judgment. Do not turn these engineering bounds into subjective visual approval,
or use them to waive the unchanged node contract.

## Focused runtime and preservation verification

Fresh launch results on Godot 4.5.1 f62fdbde1, Linux, X11/Xvfb, Mesa 26.0.8
llvmpipe LLVM 21.1.8, Compatibility OpenGL; no headless renderer or MovieWriter.
Dummy audio was explicit. Per-launch argv/environment and unedited engine logs
are archived. Binary SHA256, host, source hashes and preservation are in provenance.

- 1280x720, 960x720 and 1680x720 suites: 337 assertions each, no failures.
  Real Window.size changes refit the actual camera and capture the resized view.
  Minimum cube projection 6.084px / 5.442px at the two reference sizes; these are
  sampling/framing evidence only. Full 26x26x8 envelope stays in frame.
- The 12-degree FOV negative fails 162 assertions and exits 1. All five original
  checker mutations are rejected. These tests and existing checker are unchanged.
- New pixel guardrails pass both final analytic and dense viewports, reject both
  old-camera analytic baselines, and reject missing-frame/lost-cyan/lost-label/
  lost-debris report mutations. Thresholds are explicit engineering regression
  bounds chosen for these samples, not an independent perceptual acceptance bar.
- Ordinary tour: 720 real-time frames, 15.93524 engine seconds; post-warmup median
  21.667ms and p95 25.0ms. Only seven analytic cubes, not destruction performance.
- Original ring test: 349 assertions; all original/batched rendered ring image
  pairs identical. No batch or marker change.
- Original capture-free 192-body benchmark, two serial launches: p95 29.595ms and
  28.091ms, below the unchanged 33.3ms target at 1280x720. Original workload,
  ticks 510..1109, cap, lifetime, resolution and 34 assertions unchanged. No
  capture overlap; no claim of laptop speed or improved performance over baseline.
- Original controls regression: 99 assertions and independent checker pass.
  That is a technical camera-integration regression, not input/combat acceptance.

Arena/tour/ring/controls/performance launches used 4bab1cf. Final pixel launches
used 989d70a. Production code is identical between these revisions; only the
new diagnostic capture barrier changed. Each launch records exact source hashes.
The older check_crowding.py was a historical step-133 unchanged-camera proof;
its byte-identical-camera premise deliberately no longer applies. Use the new
pixel checks, current arena suite and preserved-source proof for this revision.

## Honest diagnostic failures

The first driver used unsupported Array(Vector3/Vector2i) constructors and failed
parsing. It was fixed before successful measurements; the failed log is preserved.
A later repeated dense launch exposed a stale first color frame despite identical
recorded physics poses: one render boundary was insufficient for pending MultiMesh
updates. Neither the old pass nor its claim of first-frame accuracy is reused.
The final driver flushes two complete render cycles before reading. Two separate
post-fix dense launches produce byte-identical production PNGs at all six times.
All final before/after pixel runs were repeated with that driver. Use v2 evidence,
not the older development pixel-checks.json or pre-v2 dense reports.

## Evidence and independent reproduction

The lossless runtime archive is evidence/node2-s135/runtime-evidence.tar.xz.
artifact-manifest.json gives every member path, size and SHA256; the archive was
read back member-by-member. It contains every raw run, including failed/trial
runs and session logs. Only *_color.png and ordinary scene captures represent
production appearance; never show diagnostic IDs/hidden/shadowless passes as art.

Extract from repository root:

    tar -xJf evidence/node2-s135/runtime-evidence.tar.xz

Principal final sequences are:

    evidence/arena/n2-s135-verified-v2-720p/*_color.png
    evidence/arena/n2-s135-verified-v2-4x3/*_color.png
    evidence/arena/n2-s135-verified-v2-dense-720p/dense_*_color.png
    evidence/arena/n2-s135-verified-v2-dense-4x3/dense_*_color.png
    evidence/arena/n2-s135-final-{720p,4x3,wide}/*.png
    evidence/arena/n2-s135-final-tour/tour_*.png

Before counterparts use n2-s135-before-v2-{720p,4x3,dense-720p,dense-4x3}.
All sequences include launch.json, physics/fixture records and diagnostics.

Install pinned Godot with scripts/setup.sh, or export GODOT_BIN to a verified
Godot_v4.5.1-stable_linux.x86_64 executable. This worker used the existing engine
at /opt/g-harness/workspace/G12/node_1_step_112/tools/. Xvfb/xauth/Mesa/FFmpeg are
the existing Linux prerequisites. Pixel analysis needs Pillow 12.3.0 and NumPy
2.4.3; this worker used /usr/local/lib/hermes-agent/venv/bin/python. Alternatively:

    uv venv /tmp/g12-pixels
    uv pip install --python /tmp/g12-pixels/bin/python Pillow==12.3.0 numpy==2.4.3

Fresh independent commands (new output names are mandatory):

    python3 scripts/run_arena.py controller135-720p
    python3 scripts/run_arena.py controller135-4x3 --size 960x720
    python3 scripts/run_arena.py controller135-wide --size 1680x720
    python3 scripts/run_arena.py controller135-tour --tour-frames 720
    python3 scripts/run_arena.py controller135-negative --negative-camera
    python3 scripts/run_visibility.py controller135-pixels
    python3 scripts/run_visibility.py controller135-pixels43 --size 960x720
    python3 scripts/run_dense_visibility.py controller135-dense
    python3 scripts/run_dense_visibility.py controller135-dense43 --size 960x720
    python3 scripts/run_ring_batch.py controller135-rings
    python3 scripts/run_destruction.py controller135-performance --performance

The negative command must exit 1. Check fresh pixels with check_visibility.py and
check_dense_visibility.py, each accepting a directory and --output JSON path.
Full paired guardrail command, after extracting archived before evidence:

    /tmp/g12-pixels/bin/python scripts/test_visibility.py --analytic evidence/arena/controller135-pixels evidence/arena/controller135-pixels43 --dense evidence/arena/controller135-dense evidence/arena/controller135-dense43 --before evidence/arena/n2-s135-before-v2-720p evidence/arena/n2-s135-before-v2-4x3 --output /tmp/controller135-pixels.json

Run scripts/check_arena.py on all fresh arena directories with --negative-dir,
--tour-dir and --self-test, and scripts/check_frame_target.py on the performance
directory with --output. Existing launcher output directories are never reused.

Visible desktop preview (explicit scene; the default main scene is controls):

    "$GODOT_BIN" --path game res://arena_preview.tscn --rendering-method gl_compatibility

Resize it and watch near-ground cyan overlap, high rear-corner flight and the exit.
Production destruction presentation can be exercised with destruction_demo.tscn
and its existing B rupture / N reset fixture keys; active opposition uses
opposition.tscn. Neither fixture is the completed root game. Controller should
independently launch the final revision and retain the residual occlusion notes
for the eventual exact-release human playtest.
