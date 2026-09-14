# Node 13 execution report — natural sessions verified, human quality unassessed

Repository: git@github.com:rickseeger/ai-game-05.git
Tested source: 31fe4e6db34dce8c9e94281b0f3bd5ee27b284b8.
Accepted production base: 04832df0af77769a10db15272ed901bac1dfd669.
Author: the gardener <root@g.seeger.net>.
The later delivery commit contains evidence/docs only, not game/driver changes.
Prerequisites.json contains the independently completed node-11/12 records and
full node-13 contract (large artifact-ref arrays replaced by their counts).
No durable mission/node completion was declared or mutated by this worker.

## Executed results

Ran, at the tested and already-pushed source:

    .tools/validation-venv/bin/python scripts/verify_natural_node13.py n13-verified

All 14 child commands returned zero. Exact argument arrays, UTC starts and logs
are in raw-regressions.tar.gz under evidence/n13-verified-verification/.
verification.json collects their outputs and each independent natural analysis.
A separate no-test-flag default launch also ran 120 frames without ERROR; command,
source and pinned engine checksum are in plain-default.json and its engine log.
All runtime scenes used Linux X11/OpenGL Compatibility (Mesa llvmpipe), not
headless rendering or a substituted isolated scene. Import alone was headless.

Natural primary movie and independent recorded-input movie each demonstrated:

- Normal startup, ordinary movement/mouse aim/held firing, four swept 3m dashes,
  one-second Esc pause/resume and two ordinary R retries. 2,657 InputEvents and
  2,779 per-physics-step session samples per run.
- Reached extraction early with all three pylons intact. It remained locked and
  PLAYING. Destroyed northern pylons 1 and 2 while on the pad: still no win.
- Destroyed all three distinct pylons with four real 25-damage bolt hits each;
  removed their intact colliders, emitted real physical bursts, advanced genuine
  objective progress and unlocked extraction. Final pylon was destroyed away
  from the pad; continued PLAYING until returning inside the 1.5m radius.
- Natural victory at 21.783333 active seconds, health 100, 19 shots. This includes
  a deliberate nine-second wait to observe settling while normal threats remain
  enabled; it is not a 21.8-second human difficulty estimate.
- Victory retry really moved/fired and destroyed the southern pylon. Then
  withholding movement/counterfire lost naturally at 16.1 active seconds to
  seven actual 15-damage sentry hits. No health injection, invulnerability,
  disabled threat or forced finish was used.
- Defeat retry was fresh/playable: moved, fired, destroyed the southern pylon
  again. It continued through real threat damage and ended PLAYING with health
  85 at 5.45 active seconds, on a naturally silent mixer boundary for clean exit.
- Synchronous reset observations matched every checked reset domain, including
  no stale audio/debris/render instances, input/aim/cooldowns, bolts, objective,
  clocks/spawns, same node/bus counts, and persistent default sound settings.

The independent replay does NOT run navigation/target selection. It reads the
original serialized InputEvents in a fresh default-engine process and observes
its own outcomes/physics/audio/rendering. All 114 compared combat/progression/
terminal/reset events match (four-decimal float tolerance; diagnostic names and
voice occupancy excluded). Both independent WAV files also have identical SHA256:
d074d586793faaea844f8a4696cbc843dffab2db3438c6f3f37323e23b679813.
This is independent execution and an independent Python checker, not an
independent human/controller acceptance.

A third natural scenario preserves every pylon, counterfires at real sentries
from spawn, and loses at EXACTLY 150 active seconds with health 100 and 30 shots.
It retries through R and demonstrates fresh movement/firing/pylon destruction.
Its 80 distinct PNGs decode, including the natural timeout panel bound to that
observed state. A one-second ordinary pause does not consume deadline time.
This shows that survival without objective destruction/extraction still loses.

## Destruction, rendering and actual mixer signal

Each full-session movie decodes to 2,780 frames, with 64 original PNG readbacks
synchronized to engine process-frame indices. Max mean absolute RGB error between
downsampled original PNGs and their corresponding H.264 frames is 1.267/255.
There are 3,180 orange-pixel matches near projected live fragment centers across
the captures, plus per-burst arena motion pixel differences. These establish
rendered activity/timing, NOT perception, readability or appealing motion.

All 96 first-run pylon fragments are checked individually: upward 4.5..7.5m/s
launch, distinct seeded linear and angular velocities, gravity-driven descent,
actual Ground collision, subsequent upward bounce, lateral contact motion with
spin, and eventual sleep (96/96). Measured early vertical acceleration medians
range -10.415..-10.077m/s², consistent with gravity plus accepted linear damping.
The full primary run contains 100,896 actual body samples; births, contacts,
impacts and retirement have their real event/body IDs. The independent replay
and unfixed run separately pass the same 96-arc checks.

Actual MovieWriter PCM: stereo, 48,000Hz, 46.333333 seconds, sample peak 0.3066263,
zero clipped samples. 301 accepted audio requests match real burst/impact sources
in the same physics tick; peak observed voice use is six, under the unchanged
eight-voice cap. Sparse measured fracture/impact signal onsets occur about
22.1..30.1ms after their event frame. Each pylon fracture, including both retries,
also matches its actual variant/pitch waveform in the captured mix, normalized
correlation 0.941..0.972 and delay 20.1..28.1ms. This is actual sample/timing
verification, not merely an assertion that voice.play() was called.

Primary pylon destruction movie frames: 414 (P1), 499 (P2), 703 (P3); fresh
retry P3 frames: 1539 and 2565. Sparse PNGs bracket launch/flight/contact/settling.
All frames, audio and raw traces are in raw-natural-movie.tar.gz; the fresh
independent counterpart is raw-natural-replay.tar.gz. Direct previews:

    evidence/node13-s154/natural-session.mp4
    evidence/node13-s154/actual-game-mixer.wav

Nine corrupted evidence controls are rejected per movie: locked win, missing
real hit, missing R input, dirty reset, unexplained health change, no early entry,
silent PCM, PCM shifted 250ms and clipped PCM. Existing rule/reset checkers also
retain their own negative controls below. No human looked/listened through these
numeric checks; no subjective satisfaction or speaker output claim is made.

## Actual runtime performance, separate from capture FPS

A separate UNFIXED, no-movie/no-PNG process runs the same complete natural loop.
The launch command has --max-fps 60, not --fixed-fps. It wins at the same
21.783333 active seconds, loses at 16.1 and retries naturally again.
Observed monotonic frame intervals (excluding initial warm-up samples):

    p50 25.551ms; p95 30.372ms; p99 32.281ms; worst 69.060ms.
    Mean observed render cadence 38.993 FPS; process wall time 48.043s.

These are actual runtime measurements on this host's software renderer WITH
observer/JSON telemetry overhead; not a laptop/hardware guarantee or a mission
performance-gate decision. Raw per-render frame intervals, engine process/physics
monitors and launch wall time are archived. The 60fps MovieWriter files took
about 115 wall seconds each to capture 46.33s: their encoded FPS is explicitly
NOT claimed as real-time performance. No production tuning was made to hit a
number, and no game/capture performance regression was concealed.

## Reused independent rule/reset regressions

- Two fresh accepted session-rule runs: 55 engine assertions each; genuine bolt
  linkage, distinct progress, exact deadline boundaries, same-tick loss-before-win
  in both bolt insertion orders, pause/idempotency, six trace mutations rejected.
- Accepted default/reset integration run: 127 assertions, six explicitly forced
  terminal fixtures, complete reset/object lifetime/connection domains, fresh
  ordinary input pylon combat, 16 decoded captures and eight mutations rejected.
  Existing HUD/terminal/locked/open marker hide-restore pixel checks pass.

Those deliberately forced fixtures are NOT used as natural-play substitutes.
The new default loader is opt-in; every other production file is checked against
04832df byte-for-byte. No weapon, health, AI, deadline, cover, fragment physics,
sound mixing or rendering parameter was retuned, so no unrelated subsystem was
modified under cover of this task.

## Failed strategies, development history and limits

See docs/natural-session-validation.md for the actual route and design choices:
corridor/dash versus cover collision, suppression versus objective shots, leaving
southern objective cover intact until later, and returning after remote unlock.
The stationary exposed strategy after destroying southern cover really loses;
the objective-neglect strategy really times out. Their full evidence is retained.
The first intended winning route succeeded; no hidden failed victory route or
balance adjustment is being invented to make the history sound more eventful.

Development runs n13-dev1/dev2/dev-movie/dev-timeout and the earlier committed
primary run n13-final-movie are preserved in development-history.tar.gz. Early
runs quit while impact voices were playing, producing Godot shutdown warnings
for AudioStreamPlaybackWAV and resources still in use. A verbose run identifies
the specific WAV playback resources. The driver now releases ordinary input,
continues normal live play, and exits on a naturally silent mixer boundary.
It does not clear/stop voices or mute/freeze production. Final natural logs have
no such shutdown leaks. This is evidence-harness cleanup, not game sound tuning.
The preliminary movie/timeout overlapped each other; their timing is explicitly
not used for the final serial real-time performance report.

Perfect world-coordinate aim and immediate threat selection are strong bot
advantages. Full health and wide deadline slack do not demonstrate human
challenge, enjoyment or balance. No speculative tuning followed those numbers.
Rick's node-9 verdict remains unassessed for fun, readability (especially HUD and
terminal overlays), keyboard feel, visual motion and sound weight/satisfaction.
No reliable vision tool was assumed, no subjective gate waived, no human playtest
solicited and no release packaged by this child.

## Archived verification / controller reproduction

All raw archive members retain their evidence/n13-verified-* repository-relative
paths. At repository root, extract the desired .tar.gz files, then rerun:

    .tools/validation-venv/bin/python scripts/check_natural.py evidence/n13-verified-movie --self-test
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/n13-verified-replay --self-test
    .tools/validation-venv/bin/python scripts/compare_natural_replay.py evidence/n13-verified-movie evidence/n13-verified-replay
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/n13-verified-timeout
    .tools/validation-venv/bin/python scripts/check_natural.py evidence/n13-verified-realtime
    .tools/validation-venv/bin/python scripts/check_session.py evidence/n13-verified-rules-1 evidence/n13-verified-rules-2
    .tools/validation-venv/bin/python scripts/check_integration.py evidence/n13-verified-integration

For a genuinely new engine reproduction, use the full verifier with a NEW prefix
as documented above. Manifest hashes cover every archived member; archive bytes
are read back and verified during packaging. Only disposable shader caches and
the redundant original AVI are excluded (original AVI hashes retained). This
archival packaging is solely validation evidence, not a game release artifact.
