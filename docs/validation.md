# Execution evidence and independent validation path

## Reproduce the probe

From the repository root on Linux x86_64:

    sudo apt-get update
    sudo apt-get install -y curl unzip xvfb xauth libgl1 libgl1-mesa-dri ffmpeg python3
    ./scripts/setup.sh
    ./scripts/run_probe.sh run-local
    python3 scripts/check_probe.py evidence/run-local
    python3 scripts/test_checker.py

Prerequisite packages were already installed here; apt commands are setup guidance,
not commands falsely claimed to have run. setup.sh WAS executed and its archive
checksum validated against the release asset digest retrieved from GitHub's API.
The attempted release SHA256-SUMS.txt URL returned 404; the API was the successful
alternative. Xvfb does not support -version; dpkg-query provided its version.
No pip, venv, export templates or editor import is needed for this probe.
Pin: Godot 4.5.1.stable.official.f62fdbde1; archive provenance is in
evidence/godot-download.json; system dependency versions in dependencies.txt.

Actual first two launch commands from the worker directory:

    GODOT_BIN="$PWD/tools/Godot_v4.5.1-stable_linux.x86_64" repo/scripts/run_probe.sh run1
    GODOT_BIN="$PWD/tools/Godot_v4.5.1-stable_linux.x86_64" repo/scripts/run_probe.sh run2

Each script starts its own Xvfb server, runs real OpenGL rendering (NOT Godot
--headless), GodotPhysics3D and MovieWriter's actual offline audio mixer. Seed
1201; physics and movie rate 60 Hz; seven simulated seconds. It extracts four
960x540 PNGs, lossless 16-bit stereo audio.wav, and compresses the full video to
probe.mp4. Only temporary oversized movie.avi is deleted. Commands/output for
FFmpeg extraction and encoding are in each extract.log. No frames, trajectories,
samples or logs are manufactured for successful evidence. WAV is the authoritative
signal; MP4 AAC is a convenient lossy viewing/listening copy.

The source is intentionally limited to a technology probe: fragment burst at
0.5 seconds, floor collisions, throttled impact sounds and auto-exit. Not gameplay,
not the complete destruction service; 192-body caps and lifetime not implemented.

## Observed results and inspection

Both runs exit successfully with PROBE_DONE ticks=420 bodies=32. Renderer is Mesa
26.0.8 llvmpipe (LLVM 21.1.8) through OpenGL 4.5 Compatibility; CPU software rendering
in Xvfb, not a physical GPU/display. Each trace has 12,512 body samples; all 32
rise, fall, change quaternion, collide, rebound and settle above the floor.
Body 0 peaks at y=3.072845 m and finishes at y=0.169104 m. There are 250 ground
contact events and 51 throttled impact sound triggers. Cubes visibly rotating is
supported by quaternion change and genuine rendered frame files; no claim that a
human or vision model reviewed those frames in this terminal session.

Four selected frame files are distinct, each 960x540 with thousands of distinct
colors. PNG decoding, nonuniformity and dynamics checks are automated inspection,
NOT visual-quality judgment. View launch.png, airborne.png, collision.png and
settled.png plus probe.mp4 to judge scale, spin and tumbling. Screenshot names
refer to sampled times, not a promise that every cube collides in that frame.

PCM: 48,000 Hz, stereo, seven seconds, signed-16 peak 1,564 and RMS approximately
173.36. Destruction-window RMS approximately 418.91; largest impact-window RMS
approximately 462.53. This is non-silent engine-mixed spatial audio, quiet relative
to full scale; final gain/impact punch requires a real listening/tuning pass.
Physics CSV, event CSV and audio WAV are byte-identical between the two runs;
this is observed same-environment repeatability, not a cross-platform determinism
promise. evidence/comparison.json and run*/checks.json retain exact values.

check_probe.py verifies trajectories, collisions/bounce, rotation and ground
motion; image decode and change; destruction/impact audio windows; no clipping;
and successful engine completion without script errors. test_checker.py passes
the real baseline then rejects silent audio and static physics (temporary negative
controls). evidence/checker-tests.json records the failed assertions as expected.
Checks do not measure fun, precise no-slip rolling, hardware audibility or balance.

Run 1 MovieWriter reports seven seconds of simulated footage recorded in eight
wall-clock seconds, with rendering and encoding costs in engine.log. This is NOT
a 192-body performance test and not proof of real-time laptop performance.

## Real-time runtime and actual blockers

Also executed ordinary non-MovieWriter runtime:

    mkdir -p repo/evidence/realtime
    PROBE_OUT="$PWD/repo/evidence/realtime" GODOT_SILENCE_ROOT_WARNING=1 \
      LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a \
      tools/Godot_v4.5.1-stable_linux.x86_64 --path repo/probe \
      --rendering-method gl_compatibility > repo/evidence/realtime/engine.log 2>&1

It renders and finishes 420 physics ticks. Default hardware audio initialization
fails: ALSA cannot find card 0, Unknown PCM default, then all audio drivers fail
and Godot falls back to Dummy. /dev/snd contains only seq and timer, not a PCM
playback device. DISPLAY was unset. The log preserves the real errors and warning.
An Xvfb VSync warning occurs on all runs; it does not stop rendering.

There is no human-visible desktop, speaker route, screenshot-view tool or audio
perception tool in this worker's terminal-only capabilities. MovieWriter bypasses
physical playback and captures the real mixer output despite Dummy driver; it is
neither a hardware loopback recording nor proof anyone heard it. The node-1
contract explicitly allows captured signal, so this does not block the assigned
technology proof. It DOES block claims of interactive visible/audible play here.
No satisfaction/fun claim is made and the root validation condition is not waived.

## Exact-release validation gate for later G session

1. Package a standalone Linux export using matching official export templates.
   Produce release manifest containing source commit, executable/PCK SHA256, build
   commands, engine version and licenses. This packaging is future feature work.
2. Independent validator downloads that release, verifies checksums and runs it
   outside the repository on a real Linux graphical session. Record distro,
   graphics driver, display resolution and audio sink. Do not use a different
   editor scene or instrumented easier build as a substitute for the release.
3. Give the G validation session an actual GUI observation/control path and audio
   observation: connected Linux desktop/remote desktop with tested audio forwarding,
   screenshot/video input available to the agent, input injection, and recorded
   mixer output available to an audio-capable observer. Prove readiness with a
   displayed frame, injected movement and a test sound heard at the client. A
   silent VNC/Xvfb screen alone is insufficient. Current tools do NOT provide this.
4. G must send real movement/aim/fire/dash input into that exact executable,
   repeatedly observe screenshots/video/audio, and play at least three runs:
   natural win, deliberate death/timeout, restart/retry. Record exact inputs/events,
   outcomes, health/clock/objectives and executable hash. Probe has no such controls;
   this is a gate for the game, not a claim of present play.
5. Record the actual display and actual sink monitor (e.g. Linux ffmpeg x11grab
   and PulseAudio monitor, or equivalent verified PipeWire/desktop recorder).
   Select a real sink explicitly; verify recorded signal AND have Rick or another
   observer hear the physical speakers/headphones. Inspect a destruction event
   frame-by-frame with its audio: launch/spin, descent/contact, bounce/tumble and
   timed impact transient; also inspect 192-body stress and cleanup evidence.
6. G reports tension, understandable choices, avoidable attacks, incentive to break
   objectives and observed enjoyment honestly, separately from automated passes.
   Rick's play/listening feedback supplements G's own interactive validation; it
   must not be represented as G having played. If the available model cannot
   perceive audio or the GUI is inaccessible, report that capability blocker and
   request the required validation environment rather than inferring satisfaction
   from PCM amplitude, logs or a human's unrelated run.
7. Save validation notes, recording, screenshots, signal and outcome tests alongside
   the exact release identity. Any repair invalidates that build's final signoff:
   rebuild, rehash and replay the repaired artifact. No root completion from probe.

Immediate practical human check, if desired: on Rick's Linux desktop run the
pinned engine with --path probe, or play evidence/run1/probe.mp4 and audio.wav.
The former exercises real runtime/speakers; the latter only reviews stored evidence.
Neither is the finished game or the required future G game-play gate.
