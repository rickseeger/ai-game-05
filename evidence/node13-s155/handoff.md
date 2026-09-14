Node 13 resume validation handoff

Repository: git@github.com:rickseeger/ai-game-05.git
Tested game/driver source: eb46c211639144fd94b46f7d3637672e5c40f6f8.
Remote HEAD matched that exact SHA before and after execution. This delivery adds
checks/evidence and the existing imported driver UID, not gameplay tuning.
Prerequisites: committed node13-s154/prerequisites.json records independently
accepted rules node 11 and default/reset node 12. No harness state was modified.
This reports worker execution only, not durable node acceptance.

What was outstanding on entry

The lead logs were not sufficient alone: source/capture provenance, full driver
mutation audit, numeric capture verification and independent fresh execution
needed rechecking. The controller suite had stopped during its first timeout
capture. That incomplete run has no successful launch/end evidence and is NOT
counted. Successful subsequent timeout/realtime runs were reusable, not reasons
to repeat the whole expensive suite. Existing checks already covered most of the
contract. This resume additionally asserts held-input firing lineage, swept-hit
geometry, actual continued play after remote unlock, and identifies specific
Ground-impact asset waveforms in real PCM instead of relying only on amplitudes.

Work actually executed

1. Inspected prior worker/controller reports and complete input-only driver before
   expensive execution; cloned the designated remote into this worker directory.
   Source-audit.json records hashes and inspected trust boundaries. Every captured
   source hash matches; production comparison to accepted 04832df permits only
   the already accepted opt-in loader. No isolated scenes/forced APIs/state edits
   substitute for any natural outcome. InputEventKey, MouseMotion and MouseButton
   enter the ordinary production collector through Input.parse_input_event.
2. Reran independent checks on copied controller movie, input replay, unfixed
   realtime, and successful timeout data. All passed; originals left untouched.
3. Ran ONE fresh Linux X11/OpenGL default-engine recorded-input replay movie,
   not the bot navigation policy, in .tools/s155-fresh-replay. All natural checks,
   audio and pixel decoding, solver checks and negative controls passed. Compared
   114 combat/progression/terminal/reset events with the controller original;
   matched within the documented four-decimal tolerance. Fresh process provenance
   is in fresh-launch.json; exact successful commands in commands.json.
4. Added scripts/check_natural_resume.py and ran it against both fresh and original
   controller movies. Both pass. Rechecked unchanged accepted rule/reset fixture
   archives (not natural substitutes): two 55-assertion rule runs and the
   127-assertion/six-reset integration run; decoded pixels and negative tests pass.
5. Archived full raw input/event/collision/physics/render-frame logs, PNGs,
   captures and provenance, including interrupted timeout and controller logs.
   All 380 new archive members were read back/hash-verified, as were all 456
   previous-worker archive members and its SHA256SUMS. This is evidence archival,
   NOT release packaging. Previous development/failed-run evidence is unchanged.

Natural outcomes and complete playable retry

Fresh replay: 2,657 ordinary InputEvents, 2,779 physics-step snapshots; movement,
aim/fire, four real swept dashes, one-second Esc pause and two ordinary R retries.
All three pylons each receive four actual 25-damage swept player-bolt hits before
collider removal/destruction/burst and distinct objective progression. Supplemental
checks tie all 31 fired signals to held ordinary mouse input and all 39 collision
hits to the corresponding real bolt swept segment, not just a reported counter.

The player actually visits locked extraction with three intact pylons and cannot
win. The last pylon dies away from extraction at tick 703; 663 ensuing observed
samples remain unlocked, outside extraction and PLAYING (11.05 active seconds),
then actual entry wins. Victory: 21.783333 active seconds, health 100, 19 shots.
Victory retry moves/fires/destroys a fresh southern pylon, then a real remaining
sentry kills the exposed stationary player: seven 15-damage hits, death at 16.1s.
Death retry again moves/fires/destroys the fresh southern pylon and remains
playable. No teleports, health injections, disabled opposition or forced finish.
Successful reused timeout run preserves objectives and survives until exactly
150 active seconds (health 100, 30 shots), then ordinary R yields fresh combat.
Its 80 distinct rendered PNGs decode, including the observed timeout state.

Natural reset snapshots cover health/spawn/clocks, intact objectives/extraction
lock, aim/input/cooldowns/shots, opposition/spawns, clearing bolts/debris/render
instances/voices/body-throttle history, stable nodes/buses and sound settings.
The accepted dirty-boundary fixtures separately cover lifetime/callback domains.
Diagnostic lifetime IDs intentionally need not rewind. Pause freezes actual
clock/player/threat/projectile/debris state, not just HUD text.

Destruction, rendering and actual mixer audio

Fresh recording decodes all 2,780 frames (46.333333s encoded at 60fps) and 64 PNG
readbacks match their exact movie frame, maximum RGB mean error 1.26685/255.
3,180 orange-pixel matches near projected live fragment centers plus per-burst
arena pixel differences establish drawn activity, NOT subjective readability.

96 first-session pylon fragments have distinct seeded launch linear/spin vectors,
upward 4.5..7.5m/s launch, measured gravity descent (median early vertical
acceleration -10.415..-10.077m/s2 including damping), actual Ground contact,
subsequent bounce, lateral ground contact with spin/rolling, and eventual sleep
(96/96). 100,896 body samples retain real body/burst IDs. Original renderer copies
real solver transforms to the batch; no simulated replacement trajectory.

Actual MovieWriter game-mixer PCM: 48kHz stereo, peak 0.3066263, no clipped samples.
301 audio requests match their actual physical source in the same physics tick.
Five pylon fracture assets match variant/pitch in the PCM (correlation .941..972,
alignment 20.08..28.10ms). Six sparse actual ground-impact sounds independently
match variant/pitch (correlation .920..942) and the same launched body has observed
Ground contacts within three physics ticks. Their waveform alignment is
26.125..44.063ms, not a claim that correlation peaks are exact perceptual onsets.
Separate sparse amplitude onsets, including break and impact, are 22.06..30.06ms.
The original checker rejects nine corrupted evidence cases; the supplement rejects
five more (missing fire press, remote unlock win, off-ray hit, silent/delayed PCM).

The first supplemental checker failed, not the game: an 80ms impact template
included subsequent impacts and selected later periodic-tail correlation aliases.
The diagnostic sweep also exposed near-zero-energy FFT roundoff for tiny windows.
Retained supplement-initial.py, failure log and diagnostic JSONs document this.
The final check uses the first 40ms attack, the independently established 0..50ms
mixer delay search, and excludes effectively zero-energy windows. Same .8 match
threshold, plus normalized score <=1.000001. No captured samples or gameplay
parameters changed; both actual movies and supplemental negative controls reran.

Direct fresh captures (also within the complete fresh archive):
    evidence/node13-s155/fresh-natural-session.mp4
    evidence/node13-s155/fresh-actual-game-mixer.wav
PCM SHA256: d074d586793faaea844f8a4696cbc843dffab2db3438c6f3f37323e23b679813
Fresh PCM/video are byte-identical to earlier deterministic fixed-seed replay;
the new process has independent UTC/wall-clock/engine traces, not copied playback.

Performance: actual unfixed runtime, NOT offline capture FPS

Revalidated controller-realtime-retry uses --max-fps 60, never --fixed-fps or
MovieWriter/PNGs. Observed mean render cadence 38.5987 FPS; frame p50 25.7635ms,
p95 30.61655ms, p99 32.89875ms, worst 69.076ms; wall duration 47.97419s. This is
llvmpipe on this host with observer overhead, not a laptop performance guarantee.
The fresh 60fps offline movie took 116.31729 wall seconds for 46.33333 seconds of
encoded content; its capture FPS does NOT establish real-time performance.
No performance issue was hidden or production parameter changed.

Challenge, choices and limitations

The route dashes down the x=2.5 corridor, suppresses nearby sentries before pylon
fire, visits locked extraction, destroys the northern objectives, leaves to
remove southern cover, waits for debris settling under active threats, then
returns to extraction. Suppression versus objective shots, when to remove cover,
and leaving/returning after unlock are genuine choices represented by inputs.
The exposed stop-counterfiring strategy loses to live threats; the objective-
neglect strategy loses to the deadline. Both failing routes remain in evidence.
The first intended winning route succeeded; no invented failed route or tuning
story. Perfect aim/read-only threat knowledge, substantial deadline slack and no
winning-route damage limit all difficulty conclusions. Production tuning: NONE.

Coverage outstanding within this execution contract: none identified after these
checks. This is independent process execution and Python validation, not an
independent human review. Fixed default seed only, not exhaustive route/seed
coverage. Numeric pixels/audio do not prove fun, readability, keyboard feel,
speaker output, sound weight or audible satisfaction. Those subjective verdicts
remain Rick at node 9. No playtest solicited; no release built or packaged.

Reproduce without spending time on completed runs

At repo root, use README/setup for Godot 4.5.1 and Xvfb; Python dependencies are
pinned in environment.json. Import game once. Extract whichever new raw archive
you need with tar -xzf evidence/node13-s155/NAME.tar.gz; members restore .tools/NAME.
Then run the matching commands in commands.json. The original normal driver and
checkers are committed under game/tests/natural_play.gd and scripts/{run_natural,
check_natural,compare_natural_replay}.py. Independent new supplemental checker is
scripts/check_natural_resume.py. Archive-manifest.json enumerates every raw file
and its digest; reuse-provenance.json preserves pre-recheck origin hashes.

To independently run another actual engine process, choose a NEW directory:
    python3 scripts/run_natural.py .tools/new-n13-replay --movie --replay .tools/controller-n13-movie
    .tools/validation-venv/bin/python scripts/check_natural.py .tools/new-n13-replay --self-test
    .tools/validation-venv/bin/python scripts/check_natural_resume.py .tools/new-n13-replay --output .tools/new-n13-supplement.json
    .tools/validation-venv/bin/python scripts/compare_natural_replay.py .tools/controller-n13-movie .tools/new-n13-replay
Full optional all-scenario engine suite remains scripts/verify_natural_node13.py.
No need to rerun it merely to validate the reused successful timeout/performance
captures. To reproduce fixture rechecks, extract the existing node13-s154
raw-regressions.tar.gz under .tools/regression-reuse, then use commands.json.
