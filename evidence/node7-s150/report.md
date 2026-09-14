# Node 7 / step 150: integration readiness audit — needs re-decomposition

Worker result, not durable node/tree completion. No harness state was changed.

## Decision

The current repository does not yet contain the complete short game that this
focused packet asks to exercise and tune. This is missing session implementation,
not a failed strategy, image-perception limitation, missing audio import, or a
request to reopen the accepted renderer/controls/destruction/audio/threats.

Inspected README, design, acceptance and validation instructions, current session,
arena, player/input, target, combat, opposition, sound, and the existing natural
and focused opposition tests before running anything. The packet supplies the
accepted prerequisites; this worker did not change their acceptance state.

Tested source: e815172c725883a02664771723ed00de85e35953 (repository HEAD at clone).
All tracked game files, including accepted systems and existing tests, remain
byte-identical to that revision. File hashes are in provenance.json. The new
audit script and these evidence products are the only additions.

## Concrete missing integration

1. Default entry is still controls-only. game/project.godot names
   res://controls.tscn, which instantiates controls_session.gd; it does not create
   Combat, Opposition, Destruction, or Sound. Launching the default is not launching
   a finished game. Explicit opposition.tscn is the most integrated existing slice.
2. No production caller can win. controls_session.gd:114-125 implements a guarded
   finish(result) boundary, but references to State.WON only validate or display
   that boundary. opposition_session.gd:54 calls finish(LOST) on real player death.
   There is no objective resolver or finish(WON) gameplay call. Natural victory
   cannot be captured honestly by choosing a better input route.
3. No pylon objective counter or exit unlock. opposition_session.gd:41-52 creates
   three real damageable pylons but does not subscribe to their destroyed signals.
   destructible_target.gd already emits a once-only destruction event after removal
   of intact cover and a real fragment burst. Consume this interface; do not replace
   it. arena.gd:9,47-52 only locates/draws the extraction marker; no session checks
   its 1.5m radius or gates extraction on the three targets.
4. No 150-second deadline. controls_session.gd:138-141 increments elapsed without
   enforcing a timeout. No countdown is displayed. The design's loss-before-win
   same-tick policy has not been integrated. Session processing currently has
   priority -10; Combat has +10. A naive victory check in the inherited early
   callback would run before same-tick bolt damage. Resolve after gameplay, with
   explicit precedence tests, rather than adding an early distance-to-exit win.
5. Presentation still explicitly says objectives pending.
   opposition_session.gd:69-74 shows controls, health, dash, sentry count and attack
   facts, but no pylon progress, locked/open extraction state, countdown, final
   completion time or remaining-health result. Generic pause/retry text exists.
6. Restart machinery exists, but full-run reset cannot yet be tested: there is no
   objective/exit/deadline state to reset. start() reconstructs player and combat
   targets and clears threats, bolts, sound and debris. Extend that boundary, not
   a second restart implementation. Existing focused tests include forced damage
   and isolated fixtures; they are not substitutes for natural victory/restart.
7. Existing natural active driver fights sentries from near the initial location
   for 30 seconds, not a pylon-and-extraction route. End-to-end input-driven
   progression/restart tests and synchronized full-run mixer capture need their
   own bounded verification pass once a complete Session exists.

Source-survey.json records exact line references across production scripts. The
search is supporting evidence for source inspection, not a claim that arbitrary
program semantics can be established from a keyword count.

## Fresh actual Linux diagnostic

Executed the accepted opposition slice, not an isolated scene, with unchanged
normal seed/rules. The existing inactive driver starts seed 1201 once, then sends
no player input, performs no healing/damage/position mutation, and observes natural
sentry bolts. This is a deliberately inactive defeat diagnostic, NOT a claim that
the worker played a complete session or verified a winning strategy.

- Godot 4.5.1.stable.official.f62fdbde1, rendered X11/Xvfb Compatibility path.
- Imported WAV assets first using headless editor import, preserving the fresh-clone
  prerequisite established by node 6. Headless was not used for gameplay rendering.
- Natural loss at tick 543 / 9.05 simulation seconds: seven 15-damage collisions,
  zero health, one death, LOST. Five existing engine assertions passed.
- Existing independent check_opposition.py passed: actual collision provenance,
  damage accounting, normal clock, spacing, warning/attack timing, stationary
  inactivity, once-only death, source hashes and video coverage.
- MP4 fully decoded: 273 frames at 1280x720. Retained five original PNGs.
  Pixel decoding found 1,575–2,037 unique RGB colors per still and 100,575 changed
  pixels from first to last. This establishes nonuniform rendering and temporal
  change only; it does not establish text readability or aesthetic quality.
- Capture is fixed 30 rendered FPS / 60Hz simulation, not laptop performance.
  This diagnostic MP4 is video-only, with Dummy audio driver; there is no claim of
  synchronized mixer capture, listening, destruction evidence, or full-game victory.

Raw launch metadata, engine/encoder logs, telemetry, stills and MP4 are in
raw-inactive.tar.gz; artifact-manifest.json indexes and hashes every member and
was verified by reading the archive back. The independent checker output is
retained separately. No failed run was substituted with fabricated output.

## Reproduce from repository root

    bash scripts/setup.sh
    export GODOT_BIN="$PWD/.tools/Godot_v4.5.1-stable_linux.x86_64"
    export GODOT_SILENCE_ROOT_WARNING=1
    python3 scripts/audit_session_node7.py my-fresh-node7-audit

Use a fresh output prefix. The audit performs import, rendered inactive capture,
independent checking, pixel checks and archive verification. This execution reused
an already installed official binary from the preceding node-6 workspace rather
than redownloading it; exact path, commands, hash and version are preserved in
commands.json/provenance.json. No files in that other workspace were modified.

To inspect the committed recording without a rerun:

    tar -xzf evidence/node7-s150/raw-inactive.tar.gz
    python3 scripts/check_opposition.py evidence/opposition/node7-s150-inactive

## Proposed focused follow-up, for controller judgment only

A. Implement the missing full Session + presentation and focused state tests.
   Build on opposition_session.gd, preserving the accepted systems. Connect once-
   only pylon events, gate the existing extraction pad, add the designed 150-second
   deadline and loss-precedence resolver, controls/objective HUD, final result and
   restart reset. Make the complete session the default only once it exists. Test
   all rule boundaries, paused clock, once-only objective accounting, terminal
   idempotency, loss-before-win ordering and repeated cleanup. Clearly label any
   isolated rule fixtures; never present them as natural play evidence. Keep the
   specified values initially. Commit implementation/tests and executable test logs.

B. After A is independently accepted, exercise and tune the complete session.
   Use ordinary WASD/mouse/LMB/dash/Esc/R InputEvents, production collisions and
   unchanged rules. Record natural victory, deliberate defeat, and a fresh retry
   after each. Assert pylon hit/progress provenance, locked-exit rejection,
   post-three-pylon extraction, removal of real cover, pause behavior, and full
   reset of health/timers/targets/exit/bolts/threats/debris/voices/input. Capture
   fresh frames/video plus actual synchronized game-mixer audio with a common
   clock and source/event hashes. If the first route fails, retain the failure and
   make only bounded evidence-driven adjustments. Commit the route/test harness,
   captures and measured observations. No forced outcomes, health mutations,
   threat disabling, or isolated fixtures in the natural recordings.

proposed-decomposition.json provides these scopes and dependency explicitly. This
worker has not created child nodes or selected work for the harness.

No gameplay tuning was made: the first demonstrated gap is absence of session
rules, not evidence that accepted mechanics need rebalancing. No release packaged
and no final playtest solicited. Subjective tension, fun, readability and audiovisual
satisfaction remain unassessed for Rick at node 9. Natural victory, complete restart,
progression tests and synchronized full-run audio remain undelivered; therefore the
assigned full integration execution is NOT reported completed.
