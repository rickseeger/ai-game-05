# G12: Breakwater — design and Linux technology probe

This repository is a node-1 work product, NOT the game or a completed mission.
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
