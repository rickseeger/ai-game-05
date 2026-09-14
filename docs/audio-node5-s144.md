# Node 5 / step 144: destruction audio submission

Assigned execution finished; independent validation and human quality judgment
remain separate. No mission-tree state was changed. Stored completion contract:
docs/audio-contract.json. Read validated design, accepted node-4 implementation,
current audio source/tests and step-143 evidence before changing anything.

Source revision: 89babcea01c20c7892d3382c0f4369f03ee82cf0.
Baseline main: 36eb08e (exact parent SHA in summary.json). Captures were taken
before the source commit; launch.json records that baseline plus exact tested
source hashes. Packaging verifies those hashes equal the committed sources.

## Targeted repair, not a replacement physics system

The existing generated low crack/thump/grit, collision-energy gain/pitch,
four break/six impact variants, 1m/s threshold, 3-tick global / 8-tick body
throttles, eight-slot priority pool, -2dB limiter, persistent Master/SFX sliders,
M mute and minus/equal controls are preserved. Asset regeneration reproduced all
ten WAVs byte-for-byte. MIT licensing and oscillator/seed provenance are in
LICENSE, game/audio/provenance.json and scripts/generate_sound_assets.py.
No external sample or purchased asset was used.

Found and reproduced a real spatial defect: sound.gd used a 50m unity radius
with max_db=0. The elevated camera is only 27.046m and 40.094m from the paired
near/far arena test positions. Both attacks captured exactly the same peak
0.444712 and effectively identical RMS, despite their different distances.
Existing panning worked, but arena distance attenuation did not.

Changed ONLY the production audio inverse-distance unit_size to 26m and made
its attenuation model explicit. New game/tests/audio_spatial_tests.gd loads the
actual destruction scene, inflicts lethal damage at four actual arena locations,
spawns 32 physical blocks each, and keeps sample/seed/pitch equal for comparison.
No alternate mixer/physics, fabricated PCM or test-only gain modification.
The early 450ms analysis windows precede all contact sounds. Real later contacts
are required too. New scripts/check_audio_spatial.py rejects the old behavior,
missing attenuation, missing pan and reversed pan.

Fresh paired capture: far/near RMS 0.665974 versus inverse-distance prediction
0.674567 (small difference includes the existing distance-dependent filter).
Left/right loud-side RMS is about 1.173 times the other channel; mirrored RMS
matches. Near peak 0.354585 and far peak 0.233091. These establish spatial signal
behavior, NOT perceived loudness, realism or satisfaction. The 26m tuning keeps
near attacks near unity while opening space for nearer effects in the mix.

## Fresh running-game evidence

Linux X11/Xvfb, Godot 4.5.1 f62fdbde1, Compatibility llvmpipe, 1280x720.
Pinned binary hash, environment, commands, UTC times and source hashes retained.
Headless mode was used ONLY for asset import, never runtime rendering/physics.

Actual-engine MovieWriter primary: 26.25s, 1,575 frames, stereo 48kHz PCM from
its common video/mixer clock. 738 original audio assertions pass: 45 real target
breaks, 222 thresholded solver-contact impacts, all 267 requests joined to their
same-tick physics source. Four/six variants, six steals, peak eight slots under
192-body repeated destruction and twelve-break overload; final slots drain to
zero. Break attacks cannot be stolen by impacts. Controls, pause/resume, saved
settings, zero levels, GUI fire suppression and mute are exercised.

PCM sample peak 0.794333 (-1.99995dBFS), 4x oversampled peak 0.803419; no clipped
samples. AAC decoded peak 0.793104, no clipping. Five isolated break onsets are
20.792..29.167ms after the damage markers. First isolated emitted-contact onset
is 27.042ms after its event. The body observer can report one 16.667ms physics
step after contact; do not claim sample-exact collision latency. Overlapping
later contacts are joined by telemetry, not claimed separable in the waveform.
Mute/zero-master windows are exactly silent after the unchanged 80ms settling
margin. Low-SFX/max-single peak ratio 0.20344; attack 35..200Hz energy fraction
0.98263. Eight existing signal/routing negative mutations are rejected.
Nine rendered damage markers match event frame indices exactly; 222 downsampled
arena pixels change through physical flight. No image-perception claim.

Production combat also passes: 47 focused assertions, three pylon/sentry breaks,
nine impacts, same-tick audio, five peak slots, four negative checker mutations.
The normal 30-second LMB/movement/dash combat run passes its 12 assertions with
three sentries destroyed and 70 health remaining. Dummy playback there proves
routing only. The default controls-only scene is still NOT a finished game loop;
this work integrates the destruction and opposition slices, preserving node-7
scope instead of silently changing the project main scene.

Accepted destruction unchanged: 34 original assertions and eight checker
mutations; 220,256 actual physics samples. All 156,704 normalized samples before
tick 1390 match node-4 step-140 exactly, including repeated 192-body stress.
Three original lightweight performance runs pass p95 <=33.3ms at 29.933, 30.083,
30.140ms. The heavier full-CSV regression has p95 34.538ms and MISSES that numeric
target; it is not substituted for the specified lightweight performance workload.
No laptop performance certification. Original controls pass 99 assertions and
six negative mutations. No physics, camera, asset or existing test thresholds
were changed to obtain these passes.

## Playback / listening / visual limitations

ALSA hw:0 playback of the delivered WAV was attempted and FAILED: no sound card.
A private PulseAudio null sink accepted paplay of the actual capture and a fresh
normal real-time game with the PulseAudio driver; its 738 assertions pass too.
Monitor peaks are 0.794342 (WAV playback) and 0.814575 (live), neither clips.
The private daemon was verified stopped. No default/system daemon was modified.

What this worker heard: NOTHING. No auditory-perception capability or physical
speaker/headphone path is available. Nonzero virtual transport is NOT listening
and is NOT proof of forceful, clear, satisfying audible output. Final exact-release
human Linux playtest must listen for attack/weight/grit, near/far audibility,
impact-strength variation, dense-mix clarity, chatter and limiter pumping, and
exercise comfortable volume, mute, pause and restart. Also judge debris visual
weight/readability there. This is an explicit unverified quality handoff, not a
fabricated subjective acceptance or a request to block for unavailable vision.

Virtual transport fidelity diagnostic FAILS: fixed-offset correlation 0.103022;
its clock is not reliable for synchronization. Supplemental external live video
contains only 53 frames with drops. Neither is treated as synchronization proof.
The primary common-clock MovieWriter video/PCM supplies measured synchronization;
it is offline execution, not a real-time end-to-end speaker-latency benchmark.

## Retrieve and reproduce

Committed evidence archive, summary and per-member SHA256 manifest:
evidence/audio-node5-s144/. All generated run files except intermediate AVI are
in runtime-evidence.tar.gz. AVI hash/encoding commands are in launch.json.

    tar -xzf evidence/audio-node5-s144/runtime-evidence.tar.gz
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/n5s144-final --transport evidence/audio/n5s144-transport --self-test
    .tools/audio-venv/bin/python scripts/check_audio_spatial.py evidence/audio/n5s144-spatial-final --before evidence/audio/n5s144-spatial-before --self-test

Listen on real Linux hardware to extracted evidence/audio/n5s144-final/runtime.mp4
or runtime.wav; paired distance/pan capture is n5s144-spatial-final/runtime.mp4.
Results.json and frames.csv alongside primary capture contain event/physics times.

Fresh rerun (new names required; repository root):

    bash scripts/setup.sh
    uv venv .tools/audio-venv
    uv pip install --python .tools/audio-venv/bin/python numpy==2.5.3 scipy==1.18.1
    python3 scripts/rerun_audio_node5.py fresh-audio
    python3 scripts/run_audio.py fresh-spatial --spatial
    .tools/audio-venv/bin/python scripts/check_audio_spatial.py evidence/audio/fresh-spatial --self-test
    python3 scripts/run_audio_transport.py fresh-transport --wav evidence/audio/fresh-audio/runtime.wav
    .tools/audio-venv/bin/python scripts/check_audio.py evidence/audio/fresh-audio --transport evidence/audio/fresh-transport --self-test

Requires python3 3.14+ for the existing regression frame checker, xvfb-run,
ffmpeg, PulseAudio/ALSA tools and pinned Godot. Venv is only for numpy/scipy.
Interactive destruction_demo.tscn: B breaks / N resets. opposition.tscn: normal
LMB combat. M mutes, minus/equal adjusts SFX; sliders are usable while paused.
Start actual speakers/headphones at a comfortable system volume.
