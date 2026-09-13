# Node 2: Breakwater arena and camera

## Scope and prerequisite

Work starts at remote main 6cc761438b8ddfd369d79f084dd8b56b454e8e75.
Read docs/design.md, docs/acceptance.md and docs/validation.md before implementation.
The read-only persisted node-1 record said completed, "contract validated against
referenced artifacts"; evidence/arena/prerequisite.json preserves that record and
prerequisite-verification.json preserves the prior verification evidence. This
worker neither rewrote a mission nor accepted its own node into durable state.

Godot 4.5.1 stable / GDScript / Compatibility OpenGL / GodotPhysics3D remains pinned.
game/ is the new scene. probe/, its scripts and original evidence are unchanged.
Only arena/world and camera production modules plus explicit presentation/test
fixtures are implemented. No player input/movement, combat, destruction service,
audio or session rules. Seven animated cubes are MeshInstance3D position fixtures,
NOT independently simulated fragments; their motion proves camera presentation
only. No test fixture can count as the later destruction or gameplay validation.

## Interface and layout

Arena is game/arena.gd (Node3D). add_child invokes build(1201); calling build(seed)
again safely frees/replaces world geometry and returns a Dictionary containing:

- player_spawn: Transform3D at (0,0,10).
- pylon_spawns: Array[Transform3D], (-8,0,-7), (8,0,-6), (0,0,6).
- enemy_spawn_points: Array[Vector3], four (+/-10,0,+/-10) corners and (+/-10,0,0).
- exit_transform: Transform3D at (0,0,-10), marked with a 1.5m ring and cross.

These same values are exposed as properties. Coordinates are Arena-local meters;
use arena.to_global / arena.global_transform when integrating actors. Seed is
accepted for the stable interface but intentionally does not randomize this fixed
layout. Spawn return arrays are copies. Floor top is y=0, exactly 24 x 24m. Wall
inner faces are +/-12m, thickness 0.5m, height 0.75m. Three fixed cover boxes top
out at 1.2m at (-4,0,2), (4,0,0), (0,0,-4). All eight StaticBody3D objects use
world collision layer 1 and mask 0. Actors/projectiles later select world in their
own masks. Floor/grid, warm pylon site rings, and mint extraction marker establish
scale and grounded positions. The preview adds amber pylon blocks and blue/red
actor stand-ins. None owns gameplay collision/health; the later Pylon module must
provide intact cover collision and remove its own collider, not Arena's floor.

ArenaCamera is game/arena_camera.gd, a true perspective Camera3D. configure(arena)
sets current, 52-degree vertical FOV, 0.1/160m near/far and an elevated oblique view.
It deliberately does not follow a player. In a small bounded arena a fixed view
keeps targets, threats and rising fragments in one stable reference frame rather
than introducing edge pan, lag or airborne tracking. refit() analytically fits a
26 x 26 x 8m visual envelope with 12% total framing slack and responds to the
actual viewport size_changed signal. It accounts for perspective depth and aspect
ratio, rather than merely fitting a 2D rectangle. At 1280x720 the camera is roughly
(0,26.41,21.97), looking toward (0,2,0); a 4:3 window pulls it back automatically.

camera.ground_aim(screen_position) intersects a world-space y=0 Arena plane and
returns a world Vector3, or null on a miss/outside +/-12m. It deliberately ignores
cover and decorative debris; no mouse input is read here. Actual pointer mapping,
movement and screen-relative controls remain node 3. Integration assumes an
upright, unscaled Arena. Later fragment trajectories leaving the fitted envelope,
actual actor occlusion, dense destruction and final HUD overlap require integration
validation; this slice does not promise arbitrary heights/off-arena trajectories.

Perspective foreshortening, differently lit box faces, directional shadows, 2m
grid and a ground-level contact ring give depth/contact cues. Ambient/sun strengths
were reduced after actual pixel inspection found clipped amber highlights in a
development run. This is measured color separation, not a human art-quality review.

## Reproduce on Linux

From the repository root, install the same prerequisites and pinned engine:

    sudo apt-get update
    sudo apt-get install -y curl unzip xvfb xauth libgl1 libgl1-mesa-dri ffmpeg python3
    ./scripts/setup.sh

No editor import, pip dependency, export template or third-party asset is required.
This worker reused the already verified node-1 binary, rather than claiming a new
install. Every launch.json records the actual absolute binary and argv. Independent
validators can use the default .tools binary or set GODOT_BIN to their verified
4.5.1 executable. The runner refuses an existing output directory. Choose fresh
names on every rerun:

    python3 scripts/run_arena.py controller-720p
    python3 scripts/run_arena.py controller-4x3 --size 960x720
    python3 scripts/run_arena.py controller-tour --tour-frames 720
    python3 scripts/run_arena.py controller-negative --negative-camera

The negative command MUST exit 1, with frustum failures; do not treat it as a
positive scene result. Then verify real reports and decode the actual images:

    python3 scripts/check_arena.py evidence/arena/controller-720p evidence/arena/controller-4x3 --negative-dir evidence/arena/controller-negative --tour-dir evidence/arena/controller-tour --self-test

To recheck committed evidence without rerendering:

    python3 scripts/check_arena.py evidence/arena/verified-720p evidence/arena/verified-4x3 --negative-dir evidence/arena/verified-negative --tour-dir evidence/arena/realtime-tour --self-test
    sha256sum -c evidence/arena/SHA256SUMS

Ordinary visible Linux desktop launch (close window to end):

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game --rendering-method gl_compatibility

The scripted stand-in loops through the center and four arena corners, with a
0.3..8m analytic airborne-height sample. There are no gameplay controls. Resize
the window and observe the fixed camera refit. Examine overview.png, the four
corner PNGs, airborne.png and resized.png, plus realtime-tour/tour_*.png. Independent
controller should launch its own process, inspect those actual frames/desktop,
and explicitly judge ground contact, depth and silhouette readability before
accepting the node. This document does not substitute worker assertions for that
independent judgment.

## Actual results

Accepted execution evidence is evidence/arena/verified-720p, verified-4x3,
verified-negative and realtime-tour. Full programmatic recheck: checks.json.

Both positive suites: 337 assertions, zero failures, exit 0. Each exercises nine
ground locations (center, corners, edge centers) at heights 0,2,4,8m, all visual
boundary corners, stable camera transform, ground-ray round trips, collision ray
and sphere sweeps, clear spawns, rebuild idempotence, perspective depth scaling,
actual amber pixels at projected airborne cube coordinates, and live Window.size
changes. Each records seven genuine viewport PNGs after frame_post_draw. The
checker independently decodes them with FFmpeg, validates dimensions/nontrivial
colors, rechecks cube pixels and rejects identical fixture frames. It does not
infer visual polish from image entropy.

1280x720: minimum sampled screen-edge margin 0.08324; minimum projected 0.34m
cube width 6.047px. 960x720: margin 0.08036; cube width 5.635px. Live resizing in
each suite moves the camera between the two fitted positions and retains the
full envelope. The deliberate 12-degree FOV mutation fails 162 assertions,
including all 144 framing checks. Five checker-only mutations (missing/duplicate/
failed assertion, clipped margin, headless display) are also rejected.

The normal non-MovieWriter tour renders 720 frames, exits 0 and writes six PNGs
plus tour.json's per-frame positions, height and fixed-camera trace. Actual wall
time is 19.025s; engine elapsed is 17.464s. Warmup-excluded engine frame interval
median 23.611ms and p95 26.404ms, peak fixture height 8m. This is a small preview
on Mesa llvmpipe software rendering, NOT a 192-body destruction stress result or
a performance promise for Rick's laptop. Delta timings are engine measurements,
not a display-presentation latency measurement.

The tests use Xvfb with actual OpenGL (NOT --headless), explicit Dummy audio,
Mesa 26.0.8 / llvmpipe LLVM 21.1.8 on Linux x86_64. An unsupported VSync warning
is retained in logs. No audio implementation is present. This worker has no
visible desktop, screenshot perception tool or heard audio path. PNG decoding,
3D projection/color inspection and physics queries are automated evidence only;
no claim of visual playtesting, heard sound, destruction quality, enjoyment,
interactive input validation or root completion is made.

## Failed attempts and preservation

No capture directory was reused. development-history.tar.gz retains the original
development logs/reports/PNGs byte-for-byte; development-history.json explains each
attempt and records archive verification. Initial test type annotations were
fixed after a parse failure; the old runner timeout left two owned child processes
that were explicitly terminated. The runner now kills its own process group on
timeout and records exit 124. Subsequent fixes addressed excessive light, mismatched
logical/physical screenshot coordinates under viewport scaling, and an ineffective
low-level display resize call. No failed run has been relabeled a success.
Original node-1 evidence remains byte-identical to the baseline commit.

The unchanged evidence/SHA256SUMS describes the node-1 baseline, not this newer
README/acceptance checklist. Use evidence/arena/SHA256SUMS for this slice; its
provenance.json also checks unchanged probe, scripts and evidence against Git.
