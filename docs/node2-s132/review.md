# Node 2 independent renderer/camera follow-up — step 132

Execution finished; controller acceptance remains separate. No mission-tree state was changed.

## Exact revision, prerequisite and preservation

Fresh clone: git@github.com:rickseeger/ai-game-05.git at
d82ead7427f9ee89b24a322f5b30781ce90ed0fc.
The task packet states independent acceptance of node 1 and completion of nodes 3
and 10. Read docs/design.md, docs/arena-validation.md, the entire
node2-visual-followup directory, and docs/destruction-performance-remediation.md.
evidence/arena/prerequisite.json also preserves node 1 completed with independent
contract-validation memo. This session did not re-adjudicate that prerequisite.

No game or existing test/runner source was changed. In particular game/arena.gd
is byte-identical to node 10 optimization commit
f6631e436e3caedc33f705bec65a5a646db609da. The forty-marker MultiMesh remains intact.
provenance.json records source SHA256s, binary hash, author and preservation checks.
No camera/layout rebuild, physics change, resolution reduction or shadow removal.

## Actual independent Linux executions

Run from this fresh repository, sequentially, with new output directories:

    export GODOT_BIN=/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64
    "$GODOT_BIN" --version
    python3 scripts/run_arena.py n2-s132-720p
    python3 scripts/run_arena.py n2-s132-4x3 --size 960x720
    python3 scripts/run_arena.py n2-s132-tour --tour-frames 720
    python3 scripts/run_arena.py n2-s132-negative --negative-camera
    python3 scripts/check_arena.py evidence/arena/n2-s132-720p evidence/arena/n2-s132-4x3 --negative-dir evidence/arena/n2-s132-negative --tour-dir evidence/arena/n2-s132-tour --self-test > evidence/arena/n2-s132-checks.json

Negative launch intentionally exits 1; other launches and checker exit 0. Choose
unused names for controller reruns; the runner refuses an existing output path.
Each launch.json contains the exact expanded engine argv, environment, OS and
wall time. Godot 4.5.1.stable.official.f62fdbde1, real X11/Xvfb OpenGL 4.5
Compatibility, Mesa 26.0.8-1ubuntu0.3 llvmpipe LLVM 21.1.8. No --headless or
MovieWriter. Dummy audio was explicit. Unsupported VSync warning is preserved.

1280x720: 337 assertions, zero failures; margin 0.0832377672195435;
minimum sampled 0.34m cube projection 6.047119140625 pixels.
960x720: 337 assertions, zero failures; margin 0.0803557634353638;
minimum cube projection 5.63543701171875 pixels.

Camera starts at (0,26.4101524353027,21.9691371917725) at 1280x720,
and (0,28.6639976501465,23.9975967407227) at 960x720. Both suites change the
actual live Window.size to the other size and observe the size_changed-driven
refit and retained envelope, not a mocked projection. Seven fresh frames per
positive suite include the resulting resized viewport.

Tests independently exercise center/corners/edge centers, four sampled heights,
fixed camera transforms, perspective foreshortening, ground-ray round trips,
world collision queries, spawn clearance, real viewport captures and resize.
The 12-degree FOV mutation produces 162 failures including all 144 framing
checks; the checker rejects it. Five checker mutations are also rejected.

Ordinary realtime tour: 720 recorded engine frames, six renderer PNGs, fixed
camera while the fixture traverses the arena, peak height 8m. Engine elapsed
15.7047619047619s; launch wall time 17.202987453001697s. Warmup-excluded median
21.36483333333345ms and p95 24.736ms. This is a seven-cube presentation fixture,
not node 10 stress acceptance, laptop performance or perceived smoothness.

Desktop reproduction with the same real scene:

    /path/to/Godot_v4.5.1-stable_linux.x86_64 --path game res://arena_preview.tscn --rendering-method gl_compatibility

The explicit scene argument matters: the current default game scene is no
longer the original arena preview. Resize between 1280x720 and 960x720 while
watching the tour. This session exercised these changes via the real runtime
test rather than a human dragging the window.

## Repaired perception path actually exercised

The exposed session catalog has no native image tool. That did NOT end this
attempt. Read current authoritative Hermes vision documentation (local fetched
copy ../vision-docs.html relative to repository; web_extract failed because its
configured backend is search-only, curl succeeded).

The old capability probe still returns false under default CLI DeepSeek/auto
configuration, with aggregator/auth resolver diagnostics. A standalone child
Python process does not inherit the main Hermes runtime context. In that child,
set_runtime_main(openai, gpt-6-astra), matching this worker session, resolves a
working OpenAI gpt-6-astra image-capable auxiliary client. This is process-local
context, NOT an edit to Hermes config, credentials, profiles or harness settings.

Executed installed tools.vision_tools.vision_analyze_tool with each actual PNG
path, which encodes and sends real image pixels to the auxiliary reviewer.
Twenty successful image analyses are preserved as *-vision.json: all seven PNGs
at each positive viewport and all six realtime-tour PNGs. No negative-control
frame is passed off as a positive frame. Each record preserves the precise
question, source path, SHA256 and full unedited returned analysis. Hashes were
read back and checked against actual captured files. capability.json and console
logs establish the route; successful analyses, not a capability flag or PNG
entropy, establish that the perception path works.

Reviewer: OpenAI gpt-6-astra through the installed Hermes auxiliary vision
implementation. The parent worker received these pixel-grounded analyses as
text, not native image attachments. It did not personally watch a desktop or
continuous video. This distinction is intentional, not a claim of human viewing.

Reproduce review from repository root with installed Hermes environment:

    /usr/local/lib/hermes-agent/venv/bin/python docs/node2-s132/review_frames.py evidence/arena/n2-s132-720p/overview.png

Pass the other PNG paths as additional arguments. The script limits concurrency
to four. The actual full argument set was: the six remaining 720p images,
overview/northwest/northeast/southwest/southeast/airborne/resized at 4:3, and
tour_0001/0120/0240/0360/0480/0600. The first overview was reviewed separately.
An initial script quoting SyntaxError was fixed before any image request; its
original console output is retained. No unsuccessful analysis was relabeled.

## Candid visual assessment (pixel observations, not telemetry conclusions)

Depth: positive. The fresh overview and corner reviews describe converging
floor/rail lines, visible wall thickness and top/side faces, contrasting lit
faces on amber pylons and gray cover, and offset dark shadows. The appearance
is sparse and diagram-like, but volumetric. Independently read production source
uses Node3D, BoxMesh/MeshInstance3D, real perspective Camera3D and DirectionalLight3D
with shadows; the runtime perspective-depth test passes. Together these establish
real 3D rendering rather than a 2D imitation. Still-image appearance alone would
not establish engine architecture.

Ground contact: positive for the floor, cover and pylons. Reviews observe base
edges meeting the floor, adjacent shadows and ground-level rings. Cyan pawn and
red stand-in contacts are less finely resolved, especially at rear corners;
the cyan ring can blend with its body. This is not evidence of floating world
geometry. The preview pawn is intentionally a hover stand-in; rings alone are
not proof of physical contact. Ray queries are separate technical evidence.

Arena legibility: positive for major geometry and locations. The whole perimeter,
three pylons, three cover blocks, cyan actor, two red actors and mint exit marker
remain distinguishable at both sizes and after refit. No reviewed image shows
viewport-edge truncation. Labels are tiny; the extraction text is particularly
weak where amber fixture geometry projects over it. The substantial empty upper
margin reserves vertical room but reduces the pixels available to small objects.

Action and airborne readability: qualified, not an unconditional visual pass.
Cyan/red colors locate the stand-ins clearly; they are simple block silhouettes,
not detailed characters, and cannot validate actual combat readability. Airborne
amber activity is visible as a bright moving-position cluster across the captured
tour states, including outside the floor footprint but inside the viewport. The
rear-corner images show separation above the rear rail; southwest and tour_0600
reviews identify detached floor shadows supporting elevation.

However, all sizes reveal a tightly packed diagonal amber cluster: individual
cube boundaries often overlap, reading as a jagged strip. At airborne.png and
resized.png it crowds the mint extraction marker/label; at overview.png it crowds
the P3 region. Near-ground tour_0001 and tour_0360 overlap the cyan silhouette;
precise height is weak in individual stills. Do NOT turn the greater-than-four-
pixel assertion or the on-screen height caption into proof of visual clarity.
Exact cube counts, per-cube orientation and exact heights are not visually
resolved consistently. A continuous-motion visual assessment was not performed.

These limitations are genuine fresh observations, not the prior perception
blocker. The code deliberately packs seven analytic presentation cubes into a
1.3m horizontal band with no Z separation; projected overlaps are therefore not
by themselves evidence of camera malfunction or physical debris intersections.
No actual camera clipping, bad refit, 2D substitution or arena defect was
reproduced that justified modifying production code. Changing the fixture to
hide its crowded cases would not improve the production camera and was avoided.

Controller handoff: technical 3D/framing/contact evidence is positive and the
perception blocker is resolved. The basic airborne effect stays visible, but
its individual pieces and local marker text are not cleanly separated. Preserve
this qualification when applying the unchanged readability contract; this
report is NOT a blanket claim that all visual acceptance criteria passed. If
that crowding fails the controller's node-2 quality bar, scope a targeted
camera/presentation correction and rerun these same crowded cases, retaining
node 10 batching. Do not waive the gate or treat test passage as visual approval.

## Scope boundaries

The seven preview cubes are analytic nonphysical MeshInstance3D fixtures. This
session does not validate input, combat, destruction dynamics/dense bursts,
audio, enjoyment, release quality or root completion. All game source remains
unchanged. This work finishes the assigned independent launch/test/inspection
execution and supplies candid evidence for separate controller validation;
only the controller can durably accept or return the node.
