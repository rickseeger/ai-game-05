# Node 2 step 133 — targeted readability corrections and exact crowded replays

Execution completed for independent controller review; no durable node acceptance
or mission-state change is made here. The task packet explicitly states that
design/engine feasibility is independently accepted. Read docs/design.md,
docs/arena-validation.md, docs/node2-s132/review.md, all twenty saved image
analyses there, and docs/destruction-performance-remediation.md.

## Result and limits first

This is a real Godot perspective 3D scene, not a 2D imitation. Four viewport
suites, live resize, exact crowded-state replays and ring/performance regressions
pass. The extraction word no longer disappears behind the amber fixture, and
P3 text is out of its old overlap band. The cyan actor remains identifiable
through the low-flight overlaps. A dark ground pad / brighter perimeter and
stronger body-face contrast clarify its footprint; dark, lit debris face borders
retain more internal edges without changing any geometry or motion.

Do not convert this into a blanket visual pass. The tightly overlapping seven
cubes still read most reliably as an activity cluster, not seven separately
trackable objects. Exact per-piece height is ambiguous at low flight and in the
extraction projection. Body-to-ground contact remains compressed at this scale;
the pawn is deliberately a hover body, and a footprint is not a physical foot.
The independent controller must decide whether cluster-level action readability
meets this node's unchanged contract. These residuals are real visual findings,
not a capability blocker, not hidden by passing containment tests, and not a
claim that input/combat/destruction/audio or the mission is accepted.

## Revisions and narrow scope

Fresh clone baseline: 3e2072699e640b98cb9b788b199eb659f5eec914.
Production changes: 74c66eba2c950581f903bb0cc948e4df9086c5ef.
Replay typing/checker fix: e5198ee (full SHA in provenance.json).
Preservation checker: fa3b585a4d644283506682e7f8fce4ab95ffc3ed.
The later evidence commit changes no production code. Author for every commit:
the gardener <root@g.seeger.net>. Exact source SHA256s are in provenance.json
and each crowded replay launch.json; before captures use baseline production
plus the new replay driver, not altered scene geometry.

- Arena labels are larger upright depth-tested Label3D billboards. Extraction
  label sits beside its unchanged ring/cross; pylon labels sit beside their sites.
  They are world annotations, not x-ray graphics or screen-space substitutions.
- Arena.actor_contact adds one shallow floor-level dark cylinder and uses the
  existing forty-instance MultiMesh ring. Preview and actual Player share it.
  Player body color changes; collider, dimensions, input, movement and firing do not.
- debris_surface.gdshader adds derivative-smoothed dark borders on the same 0.34m
  BoxMesh faces. It remains lit, opaque and depth/shadow tested, with no displacement
  or extra rendering pass. Preview uses tint; the actual destruction MultiMesh
  uses its existing per-instance colors. No RNG calls, bodies, poses, counts,
  lifetimes, gravity, restitution, damping, CCD, cap policies or workload changed.
- Camera source and Arena.ring function are byte-identical to baseline. Two
  yaw trials were rejected, not shipped: direction (0.65,1,0.65) reduced minimum
  cube projection to 3.625px and failed seven size assertions plus resize-refit;
  (0.25,1,0.9) passed size but made 16:9/4:3 share a fit and did not solve
  individual occlusion. Keeping the original view preserves its better density,
  stable orientation and live aspect refit. Correction is presentation, not a
  claim that arbitrary camera motion fixes geometrically crowded projections.

## Temporal evidence and actual perception

Each before/after run renders eight 25-frame windows through the actual X11
OpenGL renderer. It saves five frames per window, at offsets -0.2,-0.1,0,+0.1,+0.2s.
The six tour centers are taken from the original step-132 tour.json at frame
1/120/240/360/480/600, not from this run's wall-clock frame numbers. This avoids
mistaking software-renderer timing differences for a presentation improvement.
The two additional windows keep the original extraction (0,0,0; height 8) and
P3-overview (0,0,10; height 4) states, varying height continuously around center.
Initial negative times clamp to zero: the first window intentionally includes
repeated early states. No cubes are moved apart or removed. The checker verifies
before/after JSON records exactly equal, including all seven position/rotation
triples and projections; original center positions/heights agree within 1e-5.

These are deterministic presentation-clock windows, not recorded rigid-body
motion. Each step is rendered normally; 0.1s describes the sampled fixture clock,
not a measurement of screen delivery time. The separate ordinary 720-frame tour
runs without MovieWriter or forced timestep. Neither sparse contact sheets nor
this parent session amount to watching continuous desktop video.

Forty successful pixel-grounded analyses are preserved, with original question,
actual image path, SHA256 and unedited tool response. They cover fresh before
720p windows, development trials, all final windows at 720p and 4:3, both live
resize frames, and 16:10/ultrawide overviews. Full 4:3 before frames/sheets are
also saved; they were not separately sent for auxiliary perception. Native
250x280 fixed crops plus a reduced full center frame are assembled from actual
viewport PNGs; no scene pixels are synthesized. Some crops intentionally omit
other landmarks: a cropped mint ring is not renderer clipping. Complete frames
remain available alongside every sheet.

The working vision route is installed Hermes tools.vision_tools.vision_analyze_tool
using a child process with set_runtime_main("openai", "gpt-6-astra"), matching
this worker. No credentials/config/profile were edited. Default CLI auxiliary
capability checks still print aggregator/auth diagnostics; all forty actual
OpenAI image analyses succeeded and their image hashes were read back and checked.
The parent worker receives those pixel-grounded observations as text, not native
image attachments or a human's direct desktop experience.

## Explicit assessment of the previously problematic cases

1. tour_0001, near-ground cyan overlap: before has amber flecks on both sides,
   then a band across the upper body. Final 720p and 4:3 preserve body and the
   ground ellipse in every sample. Upper-body occlusion increases at +0.1s and
   clears substantially at +0.2s. Dark cube edges survive locally. Activity and
   actor identification pass at group level; independent cube identities and
   exact low-flight clearance remain unresolved. This is not persistent actor loss.
2. tour_0360, near-ground southeast: both versions show a changing diagonal
   band, side slivers at center, then a band again. Final body and floor ring
   remain recognizable through the whole window at both sizes; the border does
   not hide the actor. Individual amber correspondence and body/ring contact
   edge remain ambiguous. The correction is not claimed to separate every cube.
3. extraction/airborne/resized: before, the cluster persistently crosses the
   text and no sampled clean word recovers. Final native crops at both sizes
   explicitly read EXTRACT in every sample; both actual resize frames also
   read the word. Plus and most of ring survive. Amber still locally crosses
   the lower-left ring: sustained partial overlap, not loss of marker identity.
   Cluster height and middle piece boundaries remain weak. This is the clearest
   corrected defect, and the floor ring was not moved to evade it.
4. P3 overview: before, the label intersects the cube band. Final P3 label and
   pylon remain readable and separate from the band at both sizes. Cyan body
   stays visible, but the thin upper extension remains close to/intersects the
   lowest amber projections. Displaced shadows support an airborne reading;
   the packed middle still cannot be reliably counted or tracked piece-by-piece.
5. tour_0120, left edge/high flight: before and after retain the whole cluster.
   Final endpoints/facets have visible edges, but the middle remains a ribbon.
   Gap from rim widens over the window; detached floor shadow supports elevation.
   A shadow/red-block overlap near -0.1s is transient. Cyan footprint/body stay
   locatable; exact contact contour is small. No viewport-edge truncation.
6. tour_0240, rear/right flight: cluster descends toward the rim with a visible
   gap remaining even at the final sample, separate from cyan. End facets and
   dark seams are visible; individual correspondence remains weaker than group
   tracking. Cyan body/base stay recognizable against the rear rim. Extraction
   is partly outside this diagnostic crop, not outside the actual viewport.
7. tour_0480, central obstacle: rising band increasingly overlays the upper gray
   cover in both versions. Final warm/cool contrast and dark seams keep the
   cluster visible; it never merges with cyan. Detached shadow supports height.
   Local contour ownership remains crowded, and the contact ellipse is clearer
   as a floor location than a precise body contact. Extraction text is readable
   when inside the native crop; full-frame marker remains intact.
8. tour_0600, foreground high flight: the cluster shifts left/down toward the
   rail but stays separate from cyan, with a detached dark floor silhouette.
   Edged ends and some faces resolve; packed central pieces still do not all
   separate. Actor/body/ring remain locatable. No sampled wholesale identity loss.

Depth and grounded world geometry remain positive: actual perspective Camera3D,
BoxMesh/Node3D volumes, directional light with shadows, top/side face contrast,
converging rails/grid, grounded base edges and detached airborne shadows. Sparse,
low-poly presentation remains diagram-like. Tests of real depth scaling and
world-plane ray intersections corroborate the architecture, not visual beauty.
Larger aspect-ratio overviews show readable extraction/pylon labels; the small
amber/cyan-upper-extension junction remains crowded, as in 720p.

## Fresh focused results and preservation checks

- 1280x720, 960x720, 1280x800, 1680x720: 337 assertions each, zero failures.
  Every process changes its real Window.size to the other reference aspect,
  checks the size_changed-driven refit and captures resized.png. No mocked resize.
  Minimum 0.34m projected widths: 6.0471, 5.6354, 6.7191, 6.0471 pixels respectively.
  These metrics establish sampling/containment only, not readability.
- 12-degree FOV negative exits 1, 162 failures including all 144 framing checks;
  independent checker rejects it. All five checker mutations are rejected.
- Final replay at both sizes: 225 checks each and 40 PNGs each. Both before/after
  pairs have exactly identical fixture/camera records. All 160 paired PNGs decode
  successfully; forty vision response/image hashes verified.
- Ordinary tour: 720 frames, 15.88268s engine time, 21.6667ms median and 23.895ms
  p95 after warmup. Seven-cube fixture only, not the destruction performance gate.
- Original ring regression: 349 checks, four before/batched image pairs have
  zero changed channel bytes. Arena.ring's function is byte-identical to node 10.
- Same original 192-active-body destruction benchmark, sequential and unrecorded:
  p95 28.496ms and 29.179ms, both below unchanged 33.3ms; 34 checks each, original
  ticks 510..1109 stress filter and no capture overlap. No workload reduction.
- Controls technical regression: 99 checks and original independent checker pass.
  This does not constitute input/combat acceptance in this focused assignment.
- check_crowding.py verifies unchanged camera, ring function, fixture poses,
  destruction constants and every function from _process onward, rigid-body
  script, destruction test workload, and player fixed-step/input logic.

## Honest failures, not overwritten evidence

The first replay driver and first final assertion driver had inferred-type parse
errors; corrected annotations are committed and fresh v2 directories pass.
The yaw trials and their failing suite output are retained. Final suites all
passed in-engine but the old Python checker disagreed on a few dark-border pixels:
byte 102 is exposed by Godot Image.get_pixel as float32 0.40000000596, which
passes >0.4; the Python scaled-byte test wrongly excluded 102. threshold-diagnosis.json
lists every affected pixel. The checker now reconstructs float32 channels and
uses the exact original comparisons, retaining exact pixel-count equality, the
>=3 requirement and all original test/mutation counts. The same saved frames
then pass without edits; prior step-132 images also pass the repaired checker.
The original validation-commands.json retains the failed checker and driver
exits; subsequent arena-checks.json and v2 launch.jsons are the successful reruns.

## Evidence packaging and independent reproduction

To keep the file handoff bounded, fresh raw runs, failed attempts, logs, contact
sheets, all vision analyses and technical result JSONs are stored losslessly in:

    evidence/node2-s133/runtime-evidence.tar.gz

docs/node2-s133/artifact-manifest.json lists every archive member and its size
and SHA256. Extract from repo root before running evidence checkers or opening
member paths below:

    tar -xzf evidence/node2-s133/runtime-evidence.tar.gz
    python3 scripts/check_crowding.py
    python3 scripts/check_arena.py evidence/arena/n2-s133-720p evidence/arena/n2-s133-4x3 evidence/arena/n2-s133-16x10 evidence/arena/n2-s133-ultrawide --negative-dir evidence/arena/n2-s133-negative --tour-dir evidence/arena/n2-s133-tour --self-test
    python3 scripts/check_frame_target.py evidence/destruction/n2-s133-performance-1 evidence/destruction/n2-s133-performance-2 --output /tmp/node2-performance-check.json

Principal raw sequences:
    evidence/arena/n2-s133-before-720p-v2/{sequence.json,launch.json,*.png}
    evidence/arena/n2-s133-before-4x3/{sequence.json,launch.json,*.png}
    evidence/arena/n2-s133-after-720p-v2/{sequence.json,launch.json,*.png}
    evidence/arena/n2-s133-after-4x3-v2/{sequence.json,launch.json,*.png}
Matching sheets are docs/node2-s133/<same-run>/{case.png,sheets.json}.
Actual image responses: docs/node2-s133/<run>-<case>-vision.json.
Primary checks: docs/node2-s133/{arena-checks,crowding-checks,performance-gate}.json.
Every runner saves expanded argv/environment and unedited engine output.

Independent fresh commands (choose unused output names; existing paths refused):

    export GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64
    python3 scripts/run_arena.py controller-133-720p
    python3 scripts/run_arena.py controller-133-4x3 --size 960x720
    python3 scripts/run_arena.py controller-133-wide --size 1680x720
    python3 scripts/run_crowding.py controller-133-crowded --verify-presentation
    python3 scripts/run_crowding.py controller-133-crowded-4x3 --size 960x720 --verify-presentation
    python3 scripts/run_arena.py controller-133-tour --tour-frames 720
    python3 scripts/run_arena.py controller-133-negative --negative-camera

Last command must exit 1. Original scripts/setup.sh obtains the pinned engine;
actual tested binary/version/hash/host are in provenance.json. For a visible
Linux desktop, explicitly launch the preview (default main is now controls):

    "$GODOT_BIN" --path game res://arena_preview.tscn --rendering-method gl_compatibility

Resize while watching low-flight overlap, rear-corner flight and the exit. For
fresh sheets, run scripts/crowding_sheets.py <new-crowding-run> with Python/Pillow;
review actual PNG paths with docs/node2-s133/review_frames.py in installed Hermes.
This worker used /usr/local/lib/hermes-agent/venv/bin/python for those helpers;
the exact engine was /opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64.

Controller follow-up: launch independently and explicitly judge the residual
crowding/hover-ground clarity. If the bar requires individually trackable cubes
through their projected overlap, this patch does not meet that stronger visual
bar; do not mark the node accepted merely because technical checks pass. Do not
reduce physics/destruction workload or count the analytic fixture as destruction
validation. No input, combat, sound, enjoyment, release or root acceptance here.
