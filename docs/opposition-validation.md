> Historical step-127 report. Fresh current-source verification and the updated
> worker-scope/human-playtest handoff are in [node6-s139/report.md](../evidence/node6-s139/report.md).
> The old vision blocker below is not the status of the step-139 execution.

# Node 6 opposition execution: technical evidence, visual gate BLOCKED

Recovered the uncommitted node_6_step_126 implementation into a fresh clone of
52d48fa7c8b7589e5e43d18ca72a33c1f7abdcf4. Inspected design/acceptance/interfaces,
source and previous results first. No mission state was changed. The recovery
hashes and prior partial runs are in evidence/opposition/prior-worker-review.json.
This report is NOT durable node completion or root satisfaction.

## Implementation and integration

- game/combat.gd: swept bolts, cover occlusion, 24m/s friendly / 8m/s hostile,
  25/15 damage, once-only hit, ignores decorative debris, bounded 4s TTL.
- game/sentry.gd: actual pursuit/obstacle avoidance to 6m; visible locked red line
  for 0.6s, attacks every 1.8s while in range. Two player hits destroy a sentry.
- game/opposition.gd: two initial warnings; another every 15s, cap six. One-second
  visible spawn warning, >=8m spacing rechecked at spawn, cancellation/re-warning
  if player approaches. No contact damage or test-only natural scenario buffs.
- game/player.gd: 100 health, directional hit marker, damage/health/death signals.
- game/opposition_session.gd and opposition.tscn: actual controls and pylons,
  death -> LOST/pause, R restart cleans bolts/sentries/pylons/debris.
- Existing destruction service is unchanged. Sentry mesh/collider removal before
  one 16-body burst, two-hit death guard, four-hit 32-body pylon breakup, and cover
  removal exposing player are exercised. This proves the integration is usable;
  it does not accept node 4 visual weight/performance or node 2 visual readability.

The default project scene deliberately remains the accepted controls slice.
Launch opposition explicitly; full objectives/exit/countdown/audio and release
integration belong to later work, not a disguised claim of a finished game.

## Actual fresh execution

All runs use Godot 4.5.1 / Xvfb / llvmpipe OpenGL at 1280x720, Dummy audio.
- rerun-focused: 38 assertions pass. Chase, obstruction, exact 36-tick telegraph,
  108-tick cycle, damage, cover, target destruction, cancellation, cap, pause,
  lethal idempotency, and actual R restart. Isolated fixtures are labeled in tests.
- rerun-inactive: separate engine process, no input, seven actual 15-damage hits,
  zero health/LOST by tick 543 (9.05s); 273 decoded video frames including loss.
- rerun-active: separate engine process, same seed/rules, waits for real damage,
  then actual InputEvents for aim/fire/dash; survives 1800 ticks (30s) at 70 health,
  destroys three sentries through swept player bolts and real fragment bursts;
  901 decoded video frames. No healing, direct test damage or threat debuffs.
- controls/opposition-regression: 99 input assertions pass; independent existing
  controls checker and all six trace negative controls pass.
- Independent scripts/check_opposition.py checks natural telemetry rather than
  trusting success flags: clocks, pursuit, spawn/attack timing, health, collision
  provenance, input cadence, destruction and dead threat removal. Decodes both
  videos and verifies frame counts/tick coverage and source hashes. Seven altered
  telemetry negative controls rejected in memory; not retained as genuine runs.
- Actual-engine negative-short-aim temporarily changes AIM_TIME 0.6 -> 0.2,
  rejects three checks including telegraph and interrupt counterplay. Source
  restored in finally; final source hashes match positive runs. Reproduce serially.

Natural recordings use fixed 30 rendered FPS / 60Hz simulation. Their timing is
simulation time, NOT measured reference-machine frame-time or real-time comfort.
Focused and controls suites use ordinary real-time launches. No audio claim.

## Reproduction (fresh output directory names required)

    bash scripts/setup.sh
    export GODOT_BIN="$PWD/.tools/Godot_v4.5.1-stable_linux.x86_64"
    "$GODOT_BIN" --path game res://opposition.tscn
    python3 scripts/run_opposition.py new-focused --scenario focused
    python3 scripts/run_opposition.py new-inactive --scenario inactive --capture
    python3 scripts/run_opposition.py new-active --scenario active --capture
    python3 scripts/check_opposition.py evidence/opposition/new-focused evidence/opposition/new-inactive evidence/opposition/new-active --self-test evidence/opposition/new-active evidence/opposition/new-inactive
    python3 scripts/run_controls.py new-opposition-regression
    python3 scripts/check_controls.py evidence/controls/new-opposition-regression --self-test

The actual negative-control runner uses a fixed fresh negative-short-aim directory;
run scripts/test_opposition_negative.py in a disposable checkout without that
existing evidence directory, serially with no other gameplay test running.

## Remaining precise blocker and handoff

No exposed image/browser perception tool. Fresh configured auxiliary capability
probe returned false: OpenRouter payment/credit error and Nous authentication
unavailable. No frame was visually perceived in either worker. Red marker/beam
visibility flags, PNGs, MP4 decoding and telemetry are NOT readability assessment.
See evidence/opposition/visual-capability.txt, tool-capability.json and
visual-review-handoff.json for exact recordings, retained stills and indexed
moments. A functioning visual reviewer or human must inspect those recordings,
return frame/time-specific cue/counterplay observations, and request any justified
readability fixes before this node can satisfy the full contract.

Node 2/node 4 visual gates remain open; node 4 previously reported p95 35.114ms
against 33.3ms and was not remeasured/remediated. No subjective playability,
convincing weight, audio, balance, victory or release acceptance is claimed.
