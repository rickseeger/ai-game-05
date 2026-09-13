# G12: Breakwater — design and Linux technology probe

This repository contains a node-1 technology probe, node-2 arena/camera slice,
and node-3 player controls slice,
NOT a playable game or a completed mission.
The repository was empty when cloned from the persisted G12 configuration.

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

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game --rendering-method gl_compatibility

WASD moves, mouse aims, hold LMB emits fire commands, Space dashes, Esc pauses.
R restarts only after terminal state (natural win/loss rules are not implemented).
No projectiles/damage, destruction, sound or opposition are presented as complete.
See docs/controls-validation.md for interfaces, actual input-driven tests/traces,
exact reproduction commands and limitations. Node 2 visual assessment remains
unperformed; automated runtime input checks do not establish playability.

    python3 scripts/run_controls.py local-controls
    python3 scripts/check_controls.py evidence/controls/local-controls --self-test
