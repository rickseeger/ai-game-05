# G12 node 6 — step 139 opposition verification

Worker execution finished. No mission node was durably completed or modified.
Base: ed443098523eb09094b9024f42d45a3e4117897e. This fresh-clone delivery
supersedes the old node-6 report's worker-vision blocker, not the unchanged
completion contract or the final human playtest.

## Scope and prerequisites

Read docs/design.md, accepted controls source/report, current opposition and
combat, destruction.gd/destructible_target.gd, previous node-6 evidence, and
node-4 fresh rerun report. Did not assume any node's durable completion.
The existing opposition already implements the designed behavior; no production
repair was justified. All production game files remain byte-identical to base.
Source is committed in game/sentry.gd, opposition.gd, combat.gd,
opposition_session.gd, player.gd and the existing destruction service.
Only verification was extended: wall timestamps on events/state trace,
a frozen on/off/restored actual-beam renderer fixture, an independent RGB
checker, a fresh-name option for the existing actual-engine negative runner,
and an exercised serial reproduction script. No redesigned enemies, audio,
packaging, release integration, or full-loop tuning.

The focused engine suite verifies that the destruction interface actually works:
three player bolts leave a pylon at 25 health, the fourth removes solid cover and
creates 32 real fragments, then a hostile bolt reaches the now-exposed player.
Two swept player bolts kill a sentry, its collider and intact mesh are absent
before the single 16-body burst, further damage cannot duplicate destruction,
and destruction interrupts a cued attack. This is fresh runtime integration
evidence, not an inference from node-4 status.

## Executed results

Final serial run: 2026-09-14 00:22:50 through 00:25:38 UTC approximately; exact
per-command starts/exit codes are in verification.json and archived commands.json.
Pinned Godot 4.5.1 official f62fdbde1, verified release ZIP checksum,
X11/Xvfb, Compatibility OpenGL, llvmpipe LLVM21.1.8, 1280x720, 60Hz physics,
Dummy audio. No headless substitute or subjective visual/audio claim.

- Focused: 42 checks pass, zero failures. Pursuit to 6m, obstacle avoidance,
  36-tick cue, 108-tick attack cycle, 15 damage, solid-cover collision,
  pylon and sentry destruction, interruption, locked-direction dodge, spawn
  warning/spacing/cancellation/cap, pause, lethal idempotency and R restart.
- Inactive: independent engine process, ordinary seed 1201, absolutely no
  player input or fixture damage. Seven actual hostile hits reduce health to
  zero, sole Session enters LOST and pauses, result at tick 543 / 9.05s.
  The real died event is engine tick 543 (observer event tick 542); the next
  observer sample records terminal state. 273 decoded frames include loss.
- Active: another process, same seed and unchanged rules. Waits for actual
  damage before InputEvent aim/fire and one dash; no healing, direct damage,
  time skips, enemy debuffs, fixture repositioning or AI freezing. Survives
  1800 ticks / 30s with 70 health, destroys three sentries through two
  25-damage swept hits each and actual destruction bursts. Destroyed actors
  disappear and never attack again. 901 decoded frames include the outcome.
  This is counterplay survival, NOT victory or a completed objective loop.
- Independent telemetry checker passes both scenarios, source SHA256 checks,
  clocks, approach distances, attack timing, collision/damage provenance,
  input cadence, same-tick bursts, removed threats, video counts and decoding.
  Seven telemetry mutations rejected. Normal controls regression: 99 checks
  plus six independent trace mutations pass.
- Cue rendering: real production beam at its normal aim state, isolated
  fixture only. Pause physics without a pause overlay, capture on/off/restored
  after render flush, restore visibility before resuming. In projected ROI
  [456,575,646,587], 298 pixels change and 286 are newly red across 143 columns;
  restored image is byte-identical in decoded RGB. Three negative image
  controls (absent, swapped, not restored) rejected. Natural scenarios NEVER
  freeze or toggle beams. This proves renderer contribution, not subjective
  readability at every position or through debris.
- Actual-engine negative: AIM_TIME temporarily 0.6 -> 0.2; engine exits 1 with
  three expected failures (timing, interrupted attack, preserved health).
  Runner restores source in finally and post-restore positive source hashes
  match. Negative wrapper exits 0 only because rejection was observed.

The reproduction helper itself was exercised end to end, all commands successful
(including the wrapper that requires the negative engine to fail). An initial
new-fixture parse error was repaired with an explicit String type. The failed
launch/log remain archived as development evidence, not a positive run. Earlier
step-139 positive runs also remain archived; final results above use final-*.

## Evidence and reproduction

verification.json contains final independent results and exact command history.
raw-runs.tar.gz preserves every step-139 generated engine log, launch metadata,
timestamped trace/results, cue PNGs and MP4s, retained natural PNGs, ffprobe
metadata, negative results and checker output at repository-relative paths.
artifact-manifest.json hashes every archive member; package.py reads them back
and checks hashes before declaring archive success. provenance.json verifies
unchanged production source and records engine hashes. human-handoff.json indexes
actual event ticks/wall times to the nearest captured video frame.

From repository root, install prerequisites per docs/validation.md then:

    bash scripts/setup.sh
    python3 scripts/rerun_opposition_node6.py controller-n6-fresh

Use a new prefix every time. Run serially: the actual-engine negative temporarily
changes sentry.gd. The helper invokes the original runners, preserves logs,
checks cues, regressions, negative rejection, and restored source.

To inspect this committed delivery:

    tar -xzf evidence/node6-s139/raw-runs.tar.gz
    python3 scripts/check_opposition.py evidence/opposition/n6s139-final-focused evidence/opposition/n6s139-final-inactive evidence/opposition/n6s139-final-active --self-test evidence/opposition/n6s139-final-active evidence/opposition/n6s139-final-inactive
    python3 scripts/check_opposition_cue.py evidence/opposition/n6s139-final-focused
    python3 scripts/check_controls.py evidence/controls/n6s139-final-controls --self-test

Recordings after extraction:
    evidence/opposition/n6s139-final-inactive/runtime.mp4
    evidence/opposition/n6s139-final-active/runtime.mp4

For actual graphical Linux play:
    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://opposition.tscn --rendering-method gl_compatibility

The default main scene still deliberately opens the accepted controls slice;
launch opposition.tscn explicitly. Integrating it into the final session and
release is later-node work. Death is a real production opposition-session rule,
not the controls fixture's manually supplied terminal condition.

## Contract limits and human handoff

No remaining reproduced technical gap in assigned opposition behavior or
verification. Worker completion does not accept subjective readability/fun.
Warnings, red line versus red bolt discrimination, hit-direction legibility,
threat/counterplay readability under debris, difficulty and response feel remain
UNASSESSED for final node-9 human playtest on the integrated Linux release.
No vision tool was sought or used; its absence is not a blocker under this packet.
The completion contract is unchanged. Pixel counts/decoded video are not a
fabricated visual judgment. Fixed-30-render-FPS recordings use 60Hz physics;
video seconds are simulation time, not real wall-time performance. No sound,
victory, countdown, release packaging, or whole-game satisfaction claim.
