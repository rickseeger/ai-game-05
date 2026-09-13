# G12 node 10 — destruction reference-frame remediation

Execution result: original llvmpipe failure reproduced, narrowly corrected, and
independently rerun from a detached corrected checkout. This is worker evidence,
not a durable node/tree completion decision. Node 4 visual acceptance is unchanged.

## Revisions and scope

Original node 4 implementation: 52d48fa7c8b7589e5e43d18ca72a33c1f7abdcf4.
Its saved performance-1201 source SHA256 map matches that commit in every entry.
Fresh remediation baseline: e954f4861733832c6f405950f6add657e4e69dd1 (repository HEAD
on arrival). Corrected source/tests: f6631e436e3caedc33f705bec65a5a646db609da.
The later evidence commit adds reports, recordings and analysis/recording helpers;
it does not alter the corrected game source or original benchmark.

The only production change is Arena.ring in game/arena.gd: forty independent
MeshInstance3D submissions become forty identical BoxMesh instances in one
MultiMesh. Every marker, dimension, transform, material, visibility inheritance,
shadow setting and triangle remains. This applies to the arena/player/reticle
rings already present in the destruction workload; it does not remove decoration,
change scene settings, lower resolution, disable shadows, or change simulation.
The actual bottleneck was scene rendering, not a need to cut physics fidelity.

The original run_destruction.py, check_destruction.py, destruction_tests.gd,
destruction implementation, target, demo, project settings and camera are byte
identical across node 4, baseline and corrected revisions. Hashes are in
evidence/destruction-remediation/environment.json. No harness or mission state
was edited. Author identity is the gardener <root@g.seeger.net>.

## Reproduced environment and unchanged measurement

Same Linux host g, x86_64 VM, four logical CPUs, exposed AMD EPYC 9354P; kernel
7.0.0-31-generic. Same Godot 4.5.1 f62fdbde1 binary originally used by node 4:
/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64.
Same OpenGL 4.5 Compatibility, Mesa 26.0.8-1ubuntu0.3 llvmpipe LLVM21.1.8,
LIBGL_ALWAYS_SOFTWARE=1, X11/Xvfb 1280x1024 display, 1280x720 game, Dummy audio,
--disable-vsync --max-fps 60. GodotPhysics3D remains 60Hz and gravity 9.8m/s².
No CPU affinity, renderer quality, physics rate, capacity, lifetime or workload
setting was changed. apitrace was installed only for diagnostic profiling;
the package log is preserved. Actual packages, binary hash, CPU and OS details,
and per-run argv/environment/source hashes are preserved, not inferred from a
user profile. Runs were sequential, with no other worker-started engine running.
This is a shared VM; unrelated host scheduling and shader-cache effects are not
controlled. No GPU/laptop or perceptual smoothness result is claimed.

The original lightweight --performance benchmark runs the same full physics and
34 assertions, while omitting screenshots and expensive per-body CSV output.
Frame CSV still records every presentation interval and the sampled Godot physics
monitor. Its unchanged stress filter is ticks 510..1109 inclusive, active=192;
all selected intervals remain, including burst spikes. Median is the ordinary
sample median; p95 is sorted[ceil(0.95*n)-1]. Target remains p95 <=33.3ms, not max
<=33.3ms and not an assertion of 60fps. Full telemetry and recordings are separate
runs and are not substituted for this timing gate.

## Fresh frame distributions (milliseconds)

Run                         n     median      p95       max
baseline-1                  335   29.721      34.069    37.715 FAIL
baseline-2                  335   29.436      37.114    44.481 FAIL
batched-trial-1              385   25.848      30.221    37.490 PASS (development)
corrected-1                 416   24.032      27.532    30.713 PASS
corrected-2                 408   24.2675     28.717    33.571 PASS
corrected-3                 413   24.085      28.229    31.035 PASS
baseline-return             368   26.892      31.416    33.821 PASS
paired-baseline-1            315   31.527      36.625    43.931 FAIL
paired-corrected-1           397   24.800      29.115    32.257 PASS
paired-baseline-2            316   31.667      36.625    40.703 FAIL
paired-corrected-2           395   25.050      29.958    35.451 PASS

Names carry the n10- prefix in raw evidence. The three corrected runs and two
paired corrected runs used a separate detached checkout of f6631e4 and independent
fresh processes. All five pass the original target and all 34 behavioral checks.
The passing baseline-return is deliberately retained: baseline performance is
variable, not guaranteed to fail every run. Subsequent serial baseline/corrected
pairs reproduced the miss and improvement without changing hardware or settings.
Original node 4 historical p95 was 35.114ms; it is not relabeled as a fresh result.
measurements.json contains every fresh run, including slower instrumented,
capture, negative and screen-recorded diagnostics, with full physics-monitor
distributions. Raw frames.csv files retain the complete distributions.

The original checker reports meets_p95_target but does not fail its process for
a miss. New scripts/check_frame_target.py calls that unchanged checker and adds
a hard assertion on its original target/window, only for capture-free performance
mode. It passed all five corrected verification runs and explicitly rejected the
two measured paired baseline failures at 36.625ms in the baseline checkout (not
because of a source-hash mismatch). Neither old checker nor threshold was edited.

## Profiling, diagnosis and regression protection

perf record -F 99 -g around a separate baseline launch found execution dominated
by llvmpipe worker/JIT and Mesa rasterization work, not game physics. perf samples,
reports and exact apitrace commands are archived. apitrace traces show two passes
of hundreds of tiny marker draws. At a common dense-scene topology the baseline
submitted 559 indexed draws / 18,554 triangles; corrected submitted 169 indexed
draws / the same 18,554 triangles. Other common topologies likewise keep identical
triangle totals with 390 fewer draws. The five visible forty-marker rings become
five submissions instead of 200 in each of two passes. No destruction block or
rendered marker was eliminated. Real uninstrumented frame-time reruns above
establish the improvement; profiler throughput is not acceptance evidence.

The baseline glretrace GPU-query output is retained as diagnostic data only.
Its software-driver query spans overlap/defer work and must NOT be summed into
exclusive per-material costs. No claim of precise per-shader milliseconds rests
on that output. The call topology, sampled profile, narrow batching intervention
and serial A/B measurements support the rendering-submission diagnosis.

New rendered ring_batch_tests.gd reconstructs the pre-change implementation as
an oracle. Independent rerun passes 349 checks: all forty markers, identical box
faces and local/world transforms under a translated/rotated/nonuniformly scaled
parent, original material/shadow mode, inherited visibility, and four radii used
by the game. All four actual before/after image pairs are byte-identical (zero
changed channel bytes), stricter than the test tolerance. These are technical
image comparisons, not a visual-quality assessment.

Regression reruns against the corrected checkout:
- Destruction: 34 checks per positive run; full capture, independent same-seed
  rerun, and seed 2207 all pass the unchanged independent trace checker.
- Original 32 first-burst blocks all rise, spin, fall, collide, bounce, tumble,
  sleep and clean up, preserving seven full-size seconds and the eight-second TTL.
- Eight independent checker mutations rejected. Fresh actual no-gravity and
  no-ground launches exit 1 and are rejected by both engine and trace checker.
- Arena: 337 checks, rendered captures and independent checker pass.
- Controls: 99 checks plus independent trace/image checker pass.
- Opposition focused/active/inactive: 38/7/5 engine checks, independent checker
  and its seven mutations pass. This is not visual, audio or fun acceptance.

## Physics preserved, including repeated simultaneous breaks

Both fresh before/after full traces contain 220,256 samples. Through tick 1389,
all 156,704 samples are byte-identical after removing wall timestamps. Hash:
ea0f0c88c5b0ea62ff3833464b6ee5d16ca42ebd80e5202c59ccb950bf55692a.
This includes all three stress burst groups, not merely the first single burst.
The later asynchronous pause/mixed-height cap fixture is independently asserted
but excluded from the exact cross-run hash. Physics-comparison.json and
scripts/compare_destruction_physics.py document the streaming comparison.

Burst tick       bodies  rise/fall/contact/spin/tumble  rebound detected  sleep
510              192     192 each                       188               96
630               96      96 each                        96               95
900               96      96 each                        95               96

These observed counts are exactly the same before/after. Not every stress body
is promised to sleep before cap retirement, and the sampled rebound detector does
not register every block. First-burst full-lifetime behavioral assertions remain
all-32, unchanged. The existing overload policy retires sleeping bodies first,
then oldest active; it can retire older active fragments at age two seconds under
cap pressure. This is not a newly shortened lifetime. Every one of the 192 active
blocks remains an independent RigidBody3D/BoxShape3D with the original mass, CCD,
friction, bounce, gravity, damping, randomized upward velocity and angular spin.
No animation, forced sleep, pose steering or physical workload reduction was used.

## Reproduction from repository root

    export GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64
    git worktree add --detach /tmp/g12-before e954f4861733832c6f405950f6add657e4e69dd1
    git worktree add --detach /tmp/g12-after f6631e436e3caedc33f705bec65a5a646db609da

Run from /tmp/g12-before, then /tmp/g12-after, serially, using fresh output names:

    python3 scripts/run_destruction.py fresh-performance --performance
    python3 scripts/check_destruction.py evidence/destruction/fresh-performance
    python3 scripts/run_destruction.py fresh-capture

From /tmp/g12-after also run:

    python3 scripts/check_frame_target.py evidence/destruction/fresh-performance --output fresh-performance-gate.json
    python3 scripts/run_ring_batch.py fresh-rings
    python3 scripts/run_destruction.py fresh-rerun --no-captures
    python3 scripts/run_destruction.py fresh-2207 --seed 2207 --no-captures
    python3 scripts/run_destruction.py fresh-no-gravity --negative-gravity --no-captures
    python3 scripts/run_destruction.py fresh-no-ground --negative-ground --no-captures
    python3 scripts/check_destruction.py evidence/destruction/fresh-capture evidence/destruction/fresh-rerun evidence/destruction/fresh-2207 evidence/destruction/fresh-performance --self-test --negative evidence/destruction/fresh-no-gravity --negative evidence/destruction/fresh-no-ground --output fresh-checks.json
    python3 scripts/run_arena.py fresh-arena
    python3 scripts/check_arena.py evidence/arena/fresh-arena
    python3 scripts/run_controls.py fresh-controls
    python3 scripts/check_controls.py evidence/controls/fresh-controls

The two negative engine commands must exit 1. Do not chain them with && expecting
success. To use the new hard gate on an old baseline checkout, copy only the new
Python check_frame_target.py helper into its scripts directory; it imports that
checkout’s unchanged checker and validates its actual source hashes.

From the evidence commit checkout, compare fresh full traces:

    python3 scripts/compare_destruction_physics.py /tmp/g12-before/evidence/destruction/fresh-capture /tmp/g12-after/evidence/destruction/fresh-capture --output comparison.json

Profile separately, never concurrently with acceptance timing:

    perf record -F 99 -g -o baseline-perf.data -- python3 scripts/run_destruction.py fresh-profile --performance
    perf report -i baseline-perf.data --stdio --no-children --sort comm,dso

Exact apitrace wrapper argv/environment is archived. apitrace prepends its trace
command before the Godot executable inside the original xvfb-run argv. The first
manual attempt inserted it after the executable, timed out at 160 seconds and
left its child alive; that specific Godot and Xvfb were terminated before any
further run. Its original command/log and the successful corrected invocation
are preserved. No output was invented or timeout relabeled as a successful trace.

## Evidence layout, recordings and outstanding perception gate

All evidence below is under evidence/destruction-remediation/:
- environment.json, measurements.json: provenance, full run inventory/statistics.
- baseline-checks.json, corrected-checks.json, performance-gate JSONs,
  baseline-rejection.json, ring-regression.json and scene regression JSONs.
- physics-comparison.json and draw-submission-comparison.json.
- raw-runs.tar.gz: fresh raw engine logs, launches, frame distributions, physics
  CSVs and screenshots. Archive paths preserve repo/, validation/ and
  baseline-verify/ prefixes from the actual working directory.
- baseline-profile.tar.gz, corrected-profile.tar.gz: actual full OpenGL traces,
  perf data, shader/call dumps and diagnostic reports.
- session-logs.tar.gz: runner/checker console outputs and command manifests.
- artifact-manifest.json: each archive member path/size/SHA256; SHA256SUMS covers
  the delivered top-level evidence. Extract archives to inspect raw evidence;
  do not validate old baseline hashes against current corrected game source.

runtime-before.mp4 and runtime-after.mp4 are fresh ordinary X11 screen recordings
of complete benchmark runs, 30fps 1280x1024 desktop captures containing the unchanged
1280x720 game window. Both were independently probed as 30.533333-second recordings.
They include launch, flight, contact/rest, cleanup and repeated simultaneous
breaks. Recording uses external FFmpeg x11grab, not MovieWriter or generated
physics animation. It adds overhead and is explicitly NOT a timing acceptance
run. Raw recording metadata and corresponding frame/event timelines are archived.
Reproduce with scripts/record_destruction.py <performance-launch.json> <fresh-dir>.

No recording or screenshot was visually perceived in this session. Technical PNG
comparisons, dynamics traces and successful timing do not establish convincing
weight, pleasing destruction, satisfying sound, smoothness or fun. An independent
image/video-capable validator must still observe the actual destruction and
apply the original node 4 contract (and unresolved node 2 / node 6 visual gates).
This remediation supplies performance and behavioral evidence only; it does not
approve or change those contracts or claim gameplay/root release acceptance.
