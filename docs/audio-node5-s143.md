# Node 5 / step 143 — fresh destruction-audio execution

Technical execution delivered, not durable mission acceptance. The unchanged
contract is docs/audio-contract.json. Current main on clone was 402793a; the
integrated audio implementation and original generated MIT assets were already
present. Read docs/design.md, destruction/body observers, target and combat
integration and node-4 step-140 evidence before testing. No production game code,
physics, rendering, asset tuning or original acceptance thresholds changed here.
Asset regeneration reproduced all ten WAVs byte-for-byte.

## Delivered and exercised

- Existing game/sound.gd: layered fracture attack/low body/grit; four break and
  six contact variants; minimum speed 1m/s, three-tick global throttle, eight-tick
  body cooldown, eight preallocated voices, fracture priority, -2dB limiter.
  Master/SFX sliders, M mute, minus/equal adjustment, pause and persisted settings.
  Source and synthesis provenance remain game/audio/provenance.json and
  scripts/generate_sound_assets.py (MIT; mathematical oscillators and seeded noise).
- New production-combat audio assertions in game/tests/opposition_tests.gd join
  real swept-bolt kills of pylons AND sentries to their once-only same-tick audio.
  This adds five checks without weakening any of the original 42. Its independent
  checker rejects wrong tick, duplicate break, missing contact and nine voices.
  Actual focused run: 47 assertions, three breaks, nine impacts, peak five slots.
  Additional natural 30-second mouse/LMB/dash combat run: 12 assertions pass,
  three sentries destroyed and 70 health remaining; its audio route assertions
  also pass. No direct damage/healing fixture or alternate physics in that run.
  Dummy driver there establishes routing only, not audible combat playback.
- New serial regression runner and private PulseAudio transport wrapper make fresh
  evidence reproducible. The playback verifier now drains real monitor output
  before SIGINT instead of cutting off buffered PCM. No padding/fabrication.

## Fresh measured evidence

Primary MovieWriter capture is actual X11 Linux Godot 4.5.1 Compatibility/llvmpipe,
1280x720, 60 rendered frames/s, 60Hz GodotPhysics and 48kHz stereo mixer on a common
clock. It is offline execution, NOT performance or physical speaker evidence.
26.25s / 1,575 decoded frames; 738 passing assertions; 45 actual damage-triggered
breaks, 222 thresholded solver-contact impacts, all 267 voice requests routed in
the source tick. Six-at-once repeats and twelve-break overload exercise 192 real
bodies and eight slots; six steals, final voice drain zero. Four/six sample variants.

PCM peak 0.7943363 (-1.9999dBFS), oversampled peak 0.814714, zero full-scale clipping.
AAC decoded peak 0.791734, zero clipping. Five isolated fracture onsets occur
20.792–29.146ms after rendered damage markers. First isolated emitted contact
impact onset: 26.896ms after its source event. The contact observer can lag the
underlying solver contact by one 16.667ms step; this is not sample-exact contact
latency. Overlapping later impacts are verified by telemetry, not separable-ear
claims. Mute/zero-master windows are exactly silent after an 80ms settling margin.
Low-SFX/max-single peak ratio 0.2029; default attack 35–200Hz energy fraction
0.9824. These measurements establish signal characteristics, not perceived weight.
Nine damage marker frames match telemetry exactly, with 222 downsampled arena
pixels changing during physical flight. No subjective visual claim. Eight audio
checker mutations are rejected, including clipping, silence and 250ms delay.

Fresh destruction regression: 34 original assertions, eight checker mutations,
220,256 physics samples. All 156,704 normalized samples before tick 1390 exactly
match accepted node-4 step-140 physics, including repeated stress bursts. Three
serial original lightweight 192-body performance runs pass the unchanged 33.3ms
p95 gate at 29.423, 29.589, 30.516ms. Full-CSV capture-free testing is separate from
that lightweight gate. Shared server timings do not certify Rick’s laptop.
Fresh controls: 99 assertions and six checker mutations. Production sources are
hash-checked against launch metadata and the cloned main. No harness changes.

## Playback is not listening — outstanding subjective clauses

Attempted ALSA hw:0 playback FAILED: no physical sound card. A private temporary
PulseAudio null sink accepted paplay of the delivered WAV and a new real-time
Linux game process. Both produced measured nonzero monitor audio without
full-scale clipping. The live engine independently passed all 738 assertions.
Both private daemon runs were read back as stopped; no default daemon modified.

Nothing was actually heard by this worker: no auditory perception or physical
speaker/headphone path. Forceful attack, convincing weight, clear crowded mix,
comfortable loudness and satisfying audible output remain UNVERIFIED. A WAV,
audio API success, nonzero loopback or numerical analysis cannot satisfy those
subjective clauses. Node 9 must listen to the exact Linux release on real hardware,
judge impact chatter, variation, attack/body/grit balance and limiter pumping,
and exercise volume/mute/pause/restart. Also judge visuals/readability there.

Transport limitations are retained, not promoted to acceptance: first monitor
was only 25.9125s for 26.25s source, causing the transport checker to fail. The
bounded drain repair yields 27.9032s actual monitor output, but full-recording
fixed-offset correlation is still only 0.072064 (fidelity diagnostic FAIL).
External live FFmpeg video encoded only 52 frames with drops. Neither virtual
clock nor supplemental external video validates sync; the common-clock primary
MovieWriter recording does. Initial runner also failed before engine launch for
missing GODOT_BIN, then used the pinned repository-local fallback in a fresh run.
Superseded evidence and diagnostic summaries remain in the archive.

## Reproduce and retrieve

Repository root; scripts/setup.sh provides the pinned engine if needed. Requires
python3 3.14+, xvfb-run, ffmpeg, PulseAudio/ALSA utilities; create an isolated
numpy==2.5.3/scipy==1.18.1 environment at .tools/audio-venv (uv venv / uv pip).
Set GODOT_BIN if it is not .tools/Godot_v4.5.1-stable_linux.x86_64. Use NEW prefixes:

    python3 scripts/rerun_audio_node5.py controller-audio-fresh
    python3 scripts/run_audio_transport.py controller-transport-fresh --wav evidence/audio/controller-audio-fresh/runtime.wav
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/controller-audio-fresh --transport evidence/audio/controller-transport-fresh --self-test

Inspect committed evidence without re-recording:

    tar -xzf evidence/audio-node5-s143/runtime-evidence.tar.gz
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/n5s143-final --transport evidence/audio/n5s143-transport-final --self-test
    python3 scripts/check_combat_audio.py evidence/opposition/n5s143-final --self-test

Primary listenable preview and lossless mixed audio after extraction:
evidence/audio/n5s143-final/runtime.mp4 and runtime.wav. Physics/audio timestamps
are in results.json and frames.csv alongside them. Interactive Linux scenes:

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://destruction_demo.tscn
    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game res://opposition.tscn

Fixture B ruptures / N resets; opposition uses ordinary LMB combat. The default
controls-only scene is not misrepresented as the node-7 finished gameplay loop.
Compact summary, source/provenance hashes, exact commands, archived-member hashes
and reproduction pointers are under evidence/audio-node5-s143/. Incidental import
caches, venv, sockets and large intermediate AVI are not deliverables; primary
AVI hash and encoding commands are retained in launch.json.
