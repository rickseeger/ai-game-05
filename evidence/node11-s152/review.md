# Node 11: production session rules, not a complete game acceptance

Tested source: 5b05232d9e9de5a95732afd4c2fccb0a33d8cd59
Accepted opposition base: ae06960675a8d0a304c337aa8212c4098f4abb92
Repository: git@github.com:rickseeger/ai-game-05.git
Commit author: the gardener <root@g.seeger.net>.
Persisted G12/node-11 contract was read from the harness SQLite database read-only;
its text matches the packet. README, design, accepted implementation and fixtures
were inspected first. No repository AGENTS.md was present. No node state changed.

## Implementation and processing-order inspection

The production scene remains game/opposition.tscn and extends controls_session.gd.
No alternate rules implementation or demonstration scene was substituted.

- rebuild_combat connects each real target.destroyed to on_target_destroyed.
  DestructibleTarget still guards is_destroyed, removes intact mesh/collider,
  creates its physical burst, and then emits destroyed once. No target changes.
- The consumer checks PLAYING, pylon kind, registered genuinely destroyed target,
  and an ID set. Duplicate deliveries do not count twice or emit extra progress.
  remaining_pylons() and objectives_changed expose the 3 -> 2 -> 1 -> 0 sequence.
- in_extraction uses the existing Arena exit_transform converted to world space
  and an inclusive 1.5m ground-plane radius, matching the existing ring. Unlock
  alone does not win remotely. Locked entry never wins. If already inside when
  the last pylon breaks, eligibility is assessed there after the damage pass.
- Ordinary movement, sentries and spawn manager run at physics priority 0;
  Combat runs at 10; opposition_session overrides the inherited -10 with 20.
  Its _physics_process advances active time, then calls resolve_tick. It does
  NOT call the inherited clock callback, so there is no double increment.
- Removed the immediate died -> finish connection. All bolts in the damage pass
  now finish, including a final pylon break after a lethal bolt. No early tree
  pause aborts the pass. Combat algorithm unchanged; its comment was updated.
- Resolution checks death, then elapsed >= 150, then unlocked extraction. Both
  loss conditions precede victory. Death supplies the reason if both losses
  coincide. Existing finish guard makes terminal state immutable and pauses the
  tree; later resolve/finish/pause/progress calls cannot change the outcome.
- Compensated clock addition reaches exactly 150 at the 9000th 60Hz step without
  an early-loss epsilon. Pause freezes clock and threats through the inherited
  pausable tree plus state guard. Rebuild clears progress and clock compensation.
- Existing opposition lethal fixture now waits for end-of-tick resolution before
  asserting LOST. No weakened health assertion or replacement damage path.

Source.diff shows the complete game-side change. Renderer, camera, player,
input, target, arena, sentry, spawn manager, destruction physics and sound source
are unchanged from the accepted base. Default launch remains controls.tscn.
Only the opposition banner was corrected to say status UI pending; node 12 owns
objective HUD, extraction presentation, default launch and thorough retry polish.

## Actual execution and independent evidence checks

Executed .tools/validation-venv/bin/python scripts/verify_session_node11.py n11-s152
at 5b05232d9e9de5a95732afd4c2fccb0a33d8cd59. All 15 child commands exited 0; exact argument arrays, UTC times,
engine stdout/stderr and source hashes are in the runtime archive. Two separately
launched rendered Linux processes each passed 55 new focused assertions. The
independent Python checker recomputes progression, same-tick order, deadline,
combat-hit/death/burst/audio linkage and source hashes from their event traces;
it rejects six corrupted-evidence controls per run. This is an independent
checker and fresh-process rerun, not a claim of an independent human reviewer.

New coverage: duplicates and target once-only guard; unknown/alive/non-pylon
signals; locked/two-pylon extraction; any-order third unlock; outside 1.501m and
inclusive 1.5m entry; victory; deferred death; exactly 8999/9000 ticks; immediately
before, at and across deadline; timeout-before-win; pause/resume with real engine
ticks; won/lost terminal idempotency; real four-bolt pylon damage, collider removal,
32-body bursts and same-tick break sound; both bolt insertion orders for final
pylon + lethal damage + extraction in one tick; damage before deadline resolution.

Existing regressions also passed:
- Opposition focused: 47 assertions; inactive: 5; active counterplay: 12.
  Natural inactive player died from seven 15-damage hits at observed test tick 543
  (9.05 seconds). Active driver survived 30 seconds with 70 health and destroyed
  three sentries, NOT three pylons. Seven trace mutations rejected.
- Combat audio routing: three breaks, nine impacts, same-tick source matching,
  five peak active slots; four corruptions rejected. Cue on/off/restored pixel
  check: 298 changed pixels, 286 red, restored identical; three mutations rejected.
- Controls: 99 assertions, six mutated traces rejected.
- Destruction physics: 34 assertions; 220256 samples; 32 independent arcs checked
  for launch/gravity/contact/settling, with cap/lifetime/cleanup rules; eight
  corruptions rejected. No destruction tuning or solver change was made.
- Audio: 738 assertions; 267 same-tick source/voice matches, eight-slot bound;
  offline engine mixer captured 26.25s stereo PCM at 48000Hz. Sample peak
  0.7943325, 4x true peak 0.8034191, zero clipped samples, mute/zero-master silence.
  Video decoded to 1575 frames; eight signal/routing corruptions rejected.
- Each session fixture saved a real 1280x720 rendered frame with 6454 RGB colors;
  code-level diversity only, not a visual judgment.

Performance caveat, explicitly NOT a pass: the unchanged destruction fixture
reported llvmpipe p95 frame interval 34.009ms versus its 33.3ms target (median
29.754ms). Functional/physics checks pass independently of that reported metric.
This child neither establishes the performance gate nor retunes accepted systems.
MovieWriter/fixed FPS results are not real-time performance measurements.

## Scope and human concerns

Session-rule runs are deliberately isolated fixtures: frozen opposition,
position/clock injection, direct damage for boundary setup, and production bolt
API calls. They exercise the real session and physics, but are NOT a natural
full-session victory, natural timeout, polished restart or proof of playability.
The existing inactive/active opposition drivers are natural threat/counterplay
regressions only. Audio movie is the accepted destruction fixture, not a full-run
soundtrack. Dummy output and captured PCM are not proof that speakers were heard.

No subjective fun, sound satisfaction, readability or full-session balance claim.
Rick still needs to judge those after nodes 12/13. Existing extraction appearance
has no new locked/open presentation; status UI and default game entry await node
12. Natural full-session victory/defeat/replay and bounded tuning await node 13.
Controller should independently rerun these commands and inspect event wiring
before accepting this worker result; worker did not declare a durable completion.

## Reproduction

From repository root on Linux x86_64 (see README for apt prerequisites):

    git checkout 5b05232d9e9de5a95732afd4c2fccb0a33d8cd59
    ./scripts/setup.sh
    .tools/Godot_v4.5.1-stable_linux.x86_64 --headless --path game --editor --import --quit
    uv venv .tools/validation-venv
    uv pip install --python .tools/validation-venv/bin/python numpy==2.5.3 scipy==1.18.1 pillow==12.3.0
    .tools/validation-venv/bin/python scripts/verify_session_node11.py independent-n11

Use a fresh prefix. Asset import alone is headless; all runtime tests use X11
through Xvfb/software OpenGL and the actual Godot 4.5.1 engine. Development fixture
and import logs are preserved separately. Targeted rules-only rerun:

    python3 scripts/run_session.py evidence/independent-rules-a
    python3 scripts/run_session.py evidence/independent-rules-b
    .tools/validation-venv/bin/python scripts/check_session.py evidence/independent-rules-a evidence/independent-rules-b

Interactive opposition entry (default deliberately unchanged):

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://opposition.tscn --rendering-method gl_compatibility

The evidence-only delivery commit may be used instead of 5b05232d9e9de5a95732afd4c2fccb0a33d8cd59: no game or
verification-script source changes follow that source revision. To inspect the
preserved original runs from the delivery commit, extract raw-runs.tar.gz at the
repository root (its members retain evidence/... paths), then run the independent
checkers with the original n11-s152 paths in archived commands.json. Manifest
hashes cover every archived file. Source hashes are rechecked by the checkers.
