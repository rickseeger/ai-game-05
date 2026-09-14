Linux release packaging: see docs/linux-release.txt for the playable artifact layout, launch, controls, dependencies, licensing, reproducible assembly and clean-artifact validation. Release tooling does not change accepted gameplay.

# G12: Breakwater — Linux session integration

Default launch now runs the complete production session: destroy three pylons,
then reach north EXTRACT alive before the 150-second active-play deadline.
WASD move, mouse aim, hold LMB fire, Space dash, Esc pause/resume; R retries
only after victory/defeat. Master/SFX sliders, M mute, -/= SFX volume.

    ./scripts/setup.sh
    .tools/Godot_v4.5.1-stable_linux.x86_64 --headless --path game --editor --import --quit
    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game

The accepted combat, physical destruction, sound and opposition are integrated;
this is NOT release packaging or a completed mission. Node 12 tests reset/HUD
integration with explicitly forced terminal fixtures, not natural full-session
victories. Node 13 adds natural normal-input victory/death/deadline/retry evidence,
including exact-input replay and synchronized game-mixer captures; see
docs/natural-session-validation.md. Independent acceptance is still required;
subjective readability, sound satisfaction and fun remain Rick's node-9 playtest.
See docs/session-integration.md for the earlier reset fixtures and limitations.

The following probe/slice sections are historical validation entry points, NOT
the default game. They remain available for focused subsystem regressions.

- docs/design.md: bounded loop, destruction/audio specification, interfaces and order.
- docs/acceptance.md: probe results versus later release gates.
- docs/validation.md: reproducible commands, observed results and real limitations.
- probe/: executable Godot 4.5.1 3D/physics/audio technology probe.
- scripts/: pinned setup, capture, evidence assertions and negative-control tests.
- evidence/: actual engine logs, traces, PNGs, PCM audio and MP4s from two launches;
  realtime/ documents the normal runtime and failed hardware audio path.

Quick check on Linux x86_64 (Debian/Ubuntu prerequisites):

    sudo apt-get update
    sudo apt-get install -y curl unzip xvfb xauth libgl1 libgl1-mesa-dri ffmpeg python3
    ./scripts/setup.sh
    ./scripts/run_probe.sh run-local
    python3 scripts/check_probe.py evidence/run-local
    python3 scripts/test_checker.py

On a graphical Linux desktop with working speakers:

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path probe

The probe auto-exits after seven simulated seconds. It has no player controls.
MovieWriter captures the engine's mixed audio offline; it does not prove that a
speaker made sound. Read docs/validation.md before interpreting any check as
human visual/audible validation. No claim of fun or satisfaction has been made.

## Arena / camera slice (node 2)

See docs/arena-validation.md for interface, automated results and exact reruns.
The original probe and its evidence are unchanged.

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://arena_preview.tscn --rendering-method gl_compatibility

This launches a looping scripted stand-in tour, not player controls or combat.
On an offscreen Linux server:

    python3 scripts/run_arena.py local-arena
    python3 scripts/check_arena.py evidence/arena/local-arena

Use a new output name each time. Seven PNGs, engine log, launch metadata and
337 focused assertions are produced per suite. No headless rendering substitute.

## Player controls slice (node 3)

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://controls.tscn --rendering-method gl_compatibility

WASD moves, mouse aims, hold LMB emits fire commands, Space dashes, Esc pauses.
In this historical slice only, R tests terminal reset without natural win/loss rules.
No projectiles/damage, destruction, sound or opposition are presented as complete.
See docs/controls-validation.md for interfaces, actual input-driven tests/traces,
exact reproduction commands and limitations. Node 2 visual assessment remains
unperformed; automated runtime input checks do not establish playability.

    python3 scripts/run_controls.py local-controls
    python3 scripts/check_controls.py evidence/controls/local-controls --self-test

## Destruction slice (node 4)

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://destruction_demo.tscn --rendering-method gl_compatibility

Explicit fixture: B ruptures targets; N resets them. Uses unchanged player controls,
real independent rigid-body blocks, a hard 192-body cap and eight-second cleanup.
Not full Combat, opposition, audio or run objectives. See docs/destruction-validation.md
for source interfaces, exact executed tests, captures, performance and limitations.
Visual assessment is BLOCKED; the software-renderer benchmark also misses its p95
target. Neither is relabelled a pass on the strength of automated physics tests.

    python3 scripts/run_destruction.py local-destruction
    python3 scripts/check_destruction.py evidence/destruction/local-destruction --self-test

## Destruction audio integration (node 5)

The destruction fixture and opposition slice now route real breaks/rigid-body
impacts through an eight-voice spatial sound service with generated MIT assets,
limiter, persistent Master/SFX controls and M mute. See docs/audio-validation.md
for real execution, captures, independent checks and explicit listening limits.
The default game now includes this service; this command still runs the audio fixture.

    python3 scripts/run_audio.py local-audio
