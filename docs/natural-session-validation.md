# Node 13: natural production sessions, not subjective acceptance

Prerequisites were read from the harness database read-only: nodes 11 and 12
independently completed at 2026-09-14T03:10:17.443093+00:00 and
2026-09-14T03:39:01.357291+00:00. The full persisted node-13 contract, README,
node-11/12 reviews and reproduction instructions were read before execution.
No mission-tree state is written by this worker.

## Reproduce

Linux x86_64, Godot 4.5.1, Xvfb/X11, OpenGL Compatibility. Prerequisites in README.
Tested source: 31fe4e6db34dce8c9e94281b0f3bd5ee27b284b8 (the subsequent evidence
commit changes no gameplay/driver source). Python validation uses numpy 2.5.3,
scipy 1.18.1, Pillow 12.3.0; the executed interpreter is CPython 3.12.14.

    ./scripts/setup.sh
    .tools/Godot_v4.5.1-stable_linux.x86_64 --headless --path game --editor --import --quit
    uv venv .tools/validation-venv
    uv pip install --python .tools/validation-venv/bin/python numpy==2.5.3 scipy==1.18.1 pillow==12.3.0
    .tools/validation-venv/bin/python scripts/verify_natural_node13.py independent-n13

Use a fresh prefix. This actually runs the default production entry (no scene
substitution / --script). Each run has private user settings, preserving normal
0.85 Master/SFX defaults without modifying another session's saved preferences.
The verifier runs serially: a full natural MovieWriter session, independent
recorded-input replay movie, natural timeout plus PNG sequence, an UNFIXED
no-capture real-time run, then the accepted rule and default/reset regressions.
It fails on any command failure and preserves commands and stdout/stderr.

Targeted primary / independent replay:

    python3 scripts/run_natural.py evidence/local-natural --movie
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/local-natural --self-test
    python3 scripts/run_natural.py evidence/local-replay --movie --replay evidence/local-natural
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/local-replay --self-test
    .tools/validation-venv/bin/python scripts/compare_natural_replay.py evidence/local-natural evidence/local-replay

Additional natural scenarios:

    python3 scripts/run_natural.py evidence/local-timeout --mode timeout --fixed --frames
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/local-timeout
    python3 scripts/run_natural.py evidence/local-realtime
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/local-realtime

No-test desktop launch remains the ordinary default game, not a benchmark:

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game

## Trust boundary and assertions

The ONLY production change relative to accepted 04832df is a four-line opt-in
--natural-test loader. Without that flag it does nothing. Normal scene, initial
start/run seed, health, position, rules, weapon values, threats/spawn policy,
physics, rendering style and sound are unmodified. The independent checker
compares every top-level production file with the accepted revision, subtracting
only the exact loader, and checks the captured source hashes. The driver also
passes a defensive no-production-assignment / no-forced-API source audit. These
checks complement, not replace, controller inspection of the small hook/driver.

The driver observes the world (including read-only raycasts for clear shots),
then sends actual InputEventKey / MouseMotion / MouseButton to
Input.parse_input_event. It never calls start, finish, pause, apply_damage,
spawn_bolt, fixed_step, burst, or writes position/health/time/progress. No actor is
frozen, healed, teleported or made invulnerable. Dash is the real swept move.
Perfect world-coordinate aiming is an automation advantage, not a human model.

The separate replay process does not run the route/target-selection policy.
It consumes only serialized ordinary InputEvents plus scheduled read-only
observation times, at the original physics ticks. It gets its own default scene,
normal startup, physics, real threats, mixer, captures, event trace and checker.
The comparator matches progression, combat, terminal/reset and final state across
fresh processes, excluding diagnostic names/voice occupancy and rounding floats
to four decimal places. This is independent execution/checking, NOT an independent
human reviewer or durable node acceptance.

External Python checks trace four real 25-damage swept player bolts per pylon,
normal fired signals/origins, exact destruction tick, collider removal, 32-body
burst, distinct progress events and unlock. Locked extraction is actually
visited before any pylon destruction, with the production rules still PLAYING.
Three pylons do not win remotely; natural victory has positive health, time under
150, unlock and ground-plane distance <=1.5m. Death has seven real 15-damage
threat hits. Timeout reaches exactly 150 active seconds with positive health.
Tick-to-tick health, time and movement continuity is checked independently.

Every terminal is followed by ordinary R. At the synchronous replacement signal,
checks cover complete state reset: player/spawn/health/shots/aim/held input and
cooldowns; intact pylons/progress/extraction; active/opposition clocks, pending
warnings/next spawn/enemy ID; no old bolts, debris or visible instances, active
voices or body throttle history; same nodes/buses and persistent audio settings.
Actual movement and fresh four-hit southern-pylon destruction prove replay is
playable, not merely a clean-looking HUD. The accepted node-12 dirty-boundary
fixtures additionally cover exhaustive old-object/callback/connection domains.
Those fixtures are explicitly NOT substituted for natural outcomes.

The one-second Esc pause freezes clock, health, position, enemies, bolts and
debris. Original rule fixtures separately cover exact deadline edges, duplicate
signals, outside/inside boundary, loss-before-win and terminal idempotency.

## Rendering, sound and solver evidence

Each MovieWriter AVI is made by the real default game and its actual mixer at
60Hz/60fps, then decoded to 32-bit PCM WAV and an H.264/AAC preview. The original
AVI SHA256 is retained; the redundant intermediate AVI is discarded. No audio
is generated to replace a missing capture. PNG readbacks and trace/frame/usec
clocks are from the same live process. Every movie frame is decoded. Original
PNG readbacks are compared numerically against the corresponding decoded movie
frame, not merely against a file-count assertion. Arena pixel deltas and orange
pixels near projected live rigid bodies verify drawn activity; they do NOT
establish readability or appealing motion.

All 96 first-run pylon fragments have distinct seeded launch linear/spin
velocities, positive launch Y, measured gravity descent, actual Ground contact,
subsequent positive-Y bounce, low-height contact with lateral motion and spin,
and eventual low speed/sleep. The actual GodotPhysics state is sampled; no
parallel solver, steered fragment or prerecorded trajectory is used. Birth,
impact and retirement telemetry stays associated with burst/body IDs.

Every accepted audio request must match the physical burst/impact source in the
same engine tick and obey eight-voice bounds. Actual PCM is tested for silence
before any source, nonzero output, clipping and sparse break/impact onset delays.
For each destroyed pylon (including retries), its recorded source asset variant
and pitch are correlated against the actual mix: this identifies that fracture
waveform and timing even when preceding impacts overlap. Asset correlation is
analysis of captured PCM, not synthesized replacement evidence. Shifted/silent/
clipped captures and six corrupted rule/input/reset traces must be rejected.

## Challenge, failed route and tuning boundary

The winning route uses the narrow x=2.5 corridor around central cover, dash to
cross distance, and immediate counterfire at exposed sentries before objective
fire. It visits locked extraction, destroys the two northern pylons from that
vantage, leaves the pad to destroy the southern pylon, waits for debris phases
while countering the next normal spawn, then returns to unlocked extraction.
Destroying objective cover and choosing between sentry suppression and objective
fire are actual choices in these runs; debris remains physical but does not
block the accepted player/bolt collision layers.

The failed strategy is recorded, not hidden: after a victory retry, the driver
moves, counterfires at one sentry and destroys southern cover, then withholds
counterfire/movement. A remaining real sentry pursues/attacks and kills the player.
The timeout route makes a different bad objective choice: it keeps all pylons
intact and counterfires at threats from spawn until the real deadline ends the
session. Surviving combat is insufficient to complete the objective. These are
intentional natural losing strategies; the first intended winning route did not
need a secret failed-run deletion, balance buff or redesign.

No production tuning was made. The perfect-aim driver can clear quickly without
health loss, so these results do not prove challenge for a practiced human, let
alone fun. There is substantial deadline slack on this route. Reducing that
slack from this bot result alone would be speculative; human challenge/style
judgments remain at node 9. Development history is retained: early captures quit
while impact voices were active and Godot logged shutdown AudioStreamPlaybackWAV
leaks. Only the observer's final quit boundary changed: release ordinary input,
continue live play, and exit on a naturally silent mixer boundary. It does NOT
stop voices, disable threats or change the sound service to hide that diagnostic.

## Limits

Fixed-FPS/capture frame rate is not runtime performance. The separate UNFIXED
no-movie/no-PNG process reports actual monotonic frame intervals and wall time,
including observer overhead on this host's llvmpipe renderer. That is not a
hardware/laptop performance guarantee or a new release performance gate.
MovieWriter/signal checks are not proof of speakers or listening. No reliable
image-perception tool was used. Fun, visual readability (especially dense HUD and
terminal overlays), sound weight and audible satisfaction remain unassessed for
Rick at node 9. No playtest was solicited and no release was packaged here.
See evidence/node13-s154/review.md for executed results and archive instructions.
