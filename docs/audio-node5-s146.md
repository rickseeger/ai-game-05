# Node 5 / step 146: verified existing integrated audio

Execution result, not durable node acceptance. No mission-tree state was changed.
Read docs/design.md, docs/audio-contract.json, prior node-5 delivery and accepted
destruction source/evidence. Reused the existing working implementation rather
than making an unmotivated sound/physics change. No game source, assets, test
thresholds or unrelated work changed. Fresh cloned source revision:
79f709f89dcfc8607dd49674d8ba47bfb5c22a1b (main at dispatch).

## Integration and provenance

The committed sound.gd binds actual destruction signals in destruction_demo.tscn
and opposition.tscn. Collider removal, burst and break request share a physics
tick. Real solver contacts drive debris impacts, not a timer or scripted landing.
The implementation retains layered attack/low thump/grit, four break and six
impact assets, randomized nonrepeating samples and energy-dependent gain/pitch.
Eight preallocated spatial voices; impacts cannot steal breaks. Excess breaks
may steal older voices; there is no growing playback queue. Impact threshold
1m/s, global three-tick throttle and eight-tick per-body cooldown, -2dB limiter,
26m inverse-distance reference for the elevated camera. Persistent Master/SFX
sliders, M mute and minus/equal volume controls work during pause too.

Generated MIT assets use only seeded noise and mathematical oscillators, not
third-party or AI recordings. LICENSE, game/audio/provenance.json and
scripts/generate_sound_assets.py contain licensing, seeds and hashes. This run
regenerated all ten WAVs byte-for-byte. Packaging checks each live/offline source
hash against both the worktree and git HEAD before retaining the evidence.

The default scene remains the controls-only slice. Destruction and actual combat
scenes are integrated; this worker does not claim a finished node-7 game loop.

## Fresh actual execution

Pinned Godot 4.5.1 Linux binary SHA256:
db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199
Reused a local copy of the pinned engine. Python 3.14.4 orchestration;
numpy 2.5.3 / scipy 1.18.1 in a uv-created Python 3.12.14 environment.
X11/Xvfb, Compatibility llvmpipe, 1280x720. Import alone used headless mode.
All rendering and physics runs used the real Linux engine, not a substitute.

Primary common-clock MovieWriter capture: 26.25s / 1,575 frames / stereo 48kHz.
738 focused assertions pass offline and in a separate normal real-time
PulseAudio game. Forty-five target breaks, 222 real thresholded contacts, all
267 playback requests matched to same-tick sources. Four/six sample variants,
eight peak slots, six steals in overload, 192 peak physical bodies, final slots
drain to zero. Controls, GUI fire suppression, saved settings, mute, zero levels,
pause/resume and repeated destruction exercised by the existing test suite.

PCM peak 0.7943325 (-1.99995dBFS), four-times oversampled peak 0.8034191;
zero full-scale clipping. AAC decoded peak 0.7931038 with zero clipping.
Five isolated break onsets: 28.9583, 29.1667, 21.1875, 20.9167, 20.7917ms after
rendered damage markers. First isolated emitted-contact onset: 27.0417ms.
The contact observer can lag the solver by another 16.667ms physics step.
Later overlapping impacts are joined through actual event/contact telemetry;
no claim they are individually separable by ear or waveform. Mute/zero-master
windows are exactly silent after the existing 80ms settling allowance. Low-SFX
peak ratio 0.20344; attack 35..200Hz energy fraction 0.982627. These numbers are
signal checks, not proof of subjective weight, comfortable loudness or clarity.
Eight existing deliberately broken routing/signal cases are rejected.

Spatial capture passes: far/near RMS 0.665974 versus inverse-distance prediction
0.674567; mirrored left/right pan verified. All three spatial checker mutations
are rejected. Nine rendered damage markers match event frame indices exactly;
222 downsampled arena pixels change through physical flight. No vision claim.

Actual combat routing: 47 assertions, three breaks, nine contacts, same-tick
routing and five peak slots, with four negative mutations rejected. Normal
30-second input-driven combat: 12 assertions, three sentries destroyed, health
70. Controls regression: 99 assertions and six checker mutations. Accepted
physics: 34 assertions plus eight checker mutations, 220,256 samples. All
156,704 normalized samples before tick 1390 equal accepted node-4 step-140,
including repeated stress bursts, rebound, spin and tumble.

Three lightweight stress performance runs pass p95 <=33.3ms: 30.127, 30.048,
30.651ms. Separately the full-CSV physics regression p95 is 33.405ms, so that
instrumented run MISSES 33.3ms. Neither result certifies laptop performance.

## Listening and capture limits: explicit, not waived

What this worker actually heard: NOTHING. There is no auditory-perception tool
or physical soundcard. aplay -l reports no soundcards; actual aplay -D hw:0 of
the captured WAV fails. A private PulseAudio null sink accepts paplay and the
normal game; monitor sample peaks are 0.794342 and 0.809845 without clipping.
The daemon was stopped and its lifecycle recorded; no default daemon changed.

Successful playback to a null sink, nonzero PCM and API calls are NOT listening,
and NOT proof of forceful or satisfying audible output. Full-recording virtual
loopback fidelity FAILS (correlation 0.103022); supplemental external video has
only 51 frames and drops. Do not use that transport clock as sync evidence.
Primary MovieWriter video/PCM supplies verified common-clock synchronization,
but is offline execution, not speaker latency or real-time A/V certification.

Final human Linux playtest should listen to real destruction/ground contacts on
speakers/headphones: attack/weight/grit, distance and impact-strength variation,
crowded mix clarity, chatter, pumping, sensible levels, mute and pause/restart.
Judge visual debris weight/readability there too. The worker execution is
finished; these unverified subjective outcomes remain for independent acceptance.
This is not a request to block development over unavailable vision, nor a claim
that the complete audible-quality contract has been subjectively satisfied.
No Argument-list-too-long transport failure occurred in this dispatch.

## Exact retrieval and reproduction

New committed package: evidence/audio-node5-s146/. Per-member file inventory,
bytes and hashes are in manifest.json; summary.json includes measured results and
exact executed command arrays. No fabricated samples or edited traces.

    sha256sum -c evidence/audio-node5-s146/SHA256SUMS
    tar -xzf evidence/audio-node5-s146/runtime-evidence.tar.gz
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/n5s146 --transport evidence/audio/n5s146-transport --self-test
    .tools/audio-venv/bin/python scripts/check_audio_spatial.py evidence/audio/n5s146-spatial --self-test
    python3 scripts/check_combat_audio.py evidence/opposition/n5s146 --self-test

Primary lossless audio and synchronized preview after extraction:
    evidence/audio/n5s146/runtime.wav
    evidence/audio/n5s146/runtime.mp4
    evidence/audio/n5s146/results.json
    evidence/audio/n5s146/frames.csv
Spatial pair capture: evidence/audio/n5s146-spatial/runtime.mp4.

Fresh reproduction from repository root (choose unused run names):

    bash scripts/setup.sh
    uv venv .tools/audio-venv
    uv pip install --python .tools/audio-venv/bin/python numpy==2.5.3 scipy==1.18.1
    python3 scripts/rerun_audio_node5.py fresh
    python3 scripts/run_audio.py fresh-spatial --spatial
    .tools/audio-venv/bin/python scripts/check_audio_spatial.py evidence/audio/fresh-spatial --self-test
    python3 scripts/run_audio_transport.py fresh-transport --wav evidence/audio/fresh/runtime.wav
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/fresh --transport evidence/audio/fresh-transport --self-test

Requires xvfb/xauth, OpenGL/Mesa, ffmpeg, ALSA/PulseAudio utilities and python3
3.14+ for the existing regression frame checker. Engine setup downloads the
pinned upstream binary with checksum validation. Actual commands/UTC times and
engine source/environment hashes are retained in each launch.json and report.

Physics comparison executed after extracting the single accepted baseline
physics.csv.gz member from evidence/destruction-node4-rerun/n4s140-raw-runs.tar.gz
(member evidence/destruction/n4s140-capture/physics.csv.gz) into
.tools/n5s146-physics-baseline/:

    python3 scripts/compare_destruction_physics.py .tools/n5s146-physics-baseline evidence/destruction/n5s146 --output evidence/n5s146-report/physics-comparison.json

Package command actually exercised (new output required):

    python3 scripts/package_audio_submission.py n5s146 audio-node5-s146 --review docs/audio-node5-s146.md

It verifies every archived member before removing only redundant loose run
copies. Engine/import caches/venv and intermediate AVI are incidental; original
AVI checksums survive in launch metadata. No older evidence is deleted.

On a graphical Linux desktop with real output, start at a comfortable volume:

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://destruction_demo.tscn --rendering-method gl_compatibility
    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://opposition.tscn --rendering-method gl_compatibility

B ruptures / N resets the fixture; normal LMB combat in opposition. M mutes;
minus/equal adjusts SFX and Master/SFX sliders work paused. Play the delivered
MP4/WAV locally as a listening reference, not a replacement for interactive play.
