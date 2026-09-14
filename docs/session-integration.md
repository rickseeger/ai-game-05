# Default Linux session integration (node 12)

Prerequisite read from the harness database read-only: node 11 completed,
independently accepted, 2026-09-14T03:10:17.443093+00:00. Node 12's full contract,
accepted docs/design.md and evidence/node11-s152/review.md were read first.
No mission/node state is mutated by this worker.

## One production implementation

project.godot now selects opposition.tscn, not controls.tscn. The existing
opposition_session extends controls_session and retains node 11's rules and
priority ordering unchanged: three distinct genuinely destroyed pylons, 1.5m
extraction, 150 active seconds, death/timeout before victory after combat.

The existing HUD and terminal labels now show the objective, controls, destroyed
count, locked/open extraction, ceiling-rounded mm:ss, health, dash and sentries.
HUD reads the actual session/player state each physics tick and synchronously
on progress, pause, terminal and reset boundaries; no parallel UI rules model.
The inherited terminal panel shows PAUSED/Esc or VICTORY/DEFEAT/R, loss reason,
controls and the release/re-press rule. Both panels use the existing dark blue,
white/cyan/amber direction. Amber LOCKED / green OPEN extraction labels and ring
are presentation only, never a replacement collider or alternate win condition.

The inherited start/run-seed/player-replacement boundary is still the only retry.
A rebuild_run extension hook places production cleanup BEFORE player_replaced
and state_changed observers. Rebuild clears combat, opposition, sound and debris,
recreates intact pylons, progress and lock, restores the clock compensation and
loss reason, then seeds two normal warning spawns. It reuses service nodes and
sound bus instead of duplicating callbacks/pools. Pointer knowledge and position
now reset along with held input; pause/resume still preserves ordinary pointer
behavior. Opposition entity sequence resets to 100 for reproducible seeded retry.
Debris.clear now clears its visible instance count immediately, not next draw.
Monotonic combat/debris diagnostic IDs are deliberately retained, not gameplay
state. Sound settings and bounded variant-selection history deliberately persist;
all old voices are stopped and per-body throttle state cleared by existing clear.

Demonstrated source defects addressed: old start emitted PLAYING before production
rebuild (stale observer/HUD window), pointer aim survived reset, seeded enemy IDs
kept increasing, and cleared debris could remain in the render batch until its
next _process. Focused assertions now protect each boundary. No control/weapon,
sentry AI, combat damage, pylon physics, destruction tuning, sound synthesis or
mix parameters changed. Arena marker geometry is merely grouped for tinting;
world/camera geometry and collision values are untouched.

## Reproduction

Linux x86_64 prerequisites/setup are in README. From repository root:

    ./scripts/setup.sh
    .tools/Godot_v4.5.1-stable_linux.x86_64 --headless --path game --editor --import --quit
    uv venv .tools/validation-venv
    uv pip install --python .tools/validation-venv/bin/python numpy==2.5.3 scipy==1.18.1 pillow==12.3.0
    .tools/validation-venv/bin/python scripts/verify_integration_node12.py independent-n12

Use a fresh prefix. GODOT_BIN may point to the identical pinned engine; every
integration launch records its checksum and all game source hashes. The verifier
runs two separate DEFAULT-entry processes (no scene override / no --script), a
plain no-test-flag default smoke process, session rules and accepted subsystem
regressions. Xvfb + actual X11/OpenGL rendering, not headless image substitution.
Targeted tests / ordinary desktop launch:

    python3 scripts/run_integration.py evidence/local-integration-a
    python3 scripts/run_integration.py evidence/local-integration-b
    .tools/validation-venv/bin/python scripts/check_integration.py evidence/local-integration-a evidence/local-integration-b
    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game

Tests use ordinary InputEvents for pause/resume/R, initial four-hit pylon combat,
and movement/firing after each retry. Six forced terminal cycles cover victory,
death and timeout twice, with real opposition always enabled. Position, elapsed,
health and target damage are explicitly injected for terminal setup: NOT natural
victories or a natural full-session deadline run. Tests dirty state, verify old
objects freed, all reset domains restored immediately, real new input works, and
stable node/bus/connection counts with exactly one reset callback per signal.

Independent Python checks recompute HUD strings from recorded state, pause
invariants, reset state/event counts, default-entry command and game hashes.
Eight corrupted traces must be rejected. PNG decoding verifies sizes/diversity,
localized text/panel/marker hide-restore differences, amber/green marker pixels,
and bit-identical paused restoration. 960x720 layout bounds are checked too.
These are code-level drawing checks, not perception or subjective readability.

## Boundaries

Node 13 owns extended normal-control full-session victory/defeat/replay and
bounded tuning; node 8 owns release packaging. Rick at node 9 judges readability
(particularly dense HUD and terminal overlay), audiovisual satisfaction and fun.
Fixed-FPS integration captures are NOT a real-time performance benchmark.
Dummy audio diagnostics establish routing, not hearing speakers. Regression
MovieWriter PCM establishes actual mixer behavior only. No subjective verdict.
See evidence/node12-s153/review.md and verification.json for executed results.
