# G12 node 2 / step 148: fresh focused renderer verification

Assigned execution finished; this is not durable node completion or perceptual acceptance.
Tested source: 08be9c20e8f48fac462738b9df855f464677c50b.
Prior independent validation supplied by controller: ed443098523eb09094b9024f42d45a3e4117897e.
Repository: git@github.com:rickseeger/ai-game-05.git.

Read the accepted design and feasibility evidence, prerequisite acceptance snapshot,
current Arena/Camera/preview and focused tests, established launch/check scripts,
and prior node-2 reviews/handoffs before execution. Node-1 independent acceptance
is retained in evidence/arena/prerequisite.json and prerequisite-verification.json.
No mission state, production source, assets, existing tests or thresholds changed.
Integrated controls, destruction, audio and threats are preserved byte-for-byte.
The renderer/camera source and established focused scripts also have no changes
since the supplied prior independent revision (see provenance.json).

## Fresh actual execution

Reused scripts/run_arena.py and scripts/check_arena.py, with new n2-s148 directories.
Godot 4.5.1.stable.official.f62fdbde1, Linux X11/Xvfb, actual OpenGL 4.5
Compatibility, Mesa 26.0.8-1ubuntu0.3 llvmpipe LLVM 21.1.8. Explicit Dummy audio;
not --headless, MovieWriter, synthesized screenshots or visual perception.

- 1280x720 and 960x720: 337 focused assertions each, zero failures, exit 0.
  Actual Window.size changes refit the camera in both directions; moving the
  stand-in and airborne fixtures does not pan the locked camera. Nine ground
  locations, heights through 8m, boundary framing, perspective scaling, world
  ray/sphere collision queries, clear spawns and ground-aim round trips pass.
- Actual framebuffer pixels at projected airborne coordinates pass the independent
  FFmpeg PNG decoder/color checker. Corner, overview, airborne and live-resized
  frames are retained at both sizes. Projected minimum cube widths 6.084229px /
  5.441956px; minimum frame margins 0.085760951 / 0.081639051.
- Deliberately narrowed 12-degree FOV exits 1 with 162 failed assertions, including
  144 framing failures. Checker also rejects all five original report mutations.
  These expected failures are not production defects or positive evidence.
- Ordinary real-time tour: 720 frames, 16.594645 engine seconds, six distinct
  saved PNGs, stable camera and airborne fixture peak approximately 8m. Post-warmup
  median 22.508ms, p95 25.739556ms. Seven nonphysical presentation cubes only;
  not dense destruction performance, display latency or Rick-laptop capability.

Perspective Camera3D projects real BoxMesh/MultiMesh 3D geometry; world collision
queries locate the y=0 ground and cover. DirectionalLight3D shadows, shaded faces,
floor grid and actor-contact pad/ring provide technical depth/contact mechanisms.
Live 3D projection and framebuffer sampling establish genuine renderer output,
not a 2D imitation. Their convincing appearance and perceptual legibility remain
UNASSESSED. No input/combat/destruction/audio acceptance is inferred from this scene.

No reproducible technical renderer/camera failures found, so no speculative fix or
redesign was made. Driver warning about unsupported V-Sync changes is retained.
A new orchestration wrapper initially had an escaped-newline SyntaxError, repaired
before any engine launch; its actual failed log is preserved in the archive.
No failed run was relabeled a pass. No dense-scene experiments were repeated.

## Durable evidence and reproduction

Start at repository root. Full argv/cwd/exit statuses: commands.json; underlying
Godot argv/environment: each archived launch.json. Engine hash, host and source
hashes: provenance.json. Focused aggregate: arena-checks.json.

    bash scripts/setup.sh
    export GODOT_BIN="$PWD/.tools/Godot_v4.5.1-stable_linux.x86_64"
    python3 docs/node2-s148/rerun.py --prefix controller148 --report-dir /tmp/controller148-report

Requires Linux Xvfb/xauth/Mesa, Python 3 and FFmpeg. No Pillow/NumPy or vision
configuration required for this focused run. Use unused prefix and report paths.
The actual worker used the pinned engine already installed at:
/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64
Executed wrapper command:

    python3 docs/node2-s148/rerun.py --prefix n2-s148 --report-dir docs/node2-s148

Four engine launches (two sizes, negative camera, ordinary tour) and one checker
are orchestrated; the negative launch is required to return 1, all others 0.
Controller can launch each command separately using commands.json.

    sha256sum -c evidence/node2-s148/SHA256SUMS
    tar -xzf evidence/node2-s148/runtime-evidence.tar.gz
    python3 scripts/check_arena.py evidence/arena/n2-s148-720p evidence/arena/n2-s148-4x3 --negative-dir evidence/arena/n2-s148-negative --tour-dir evidence/arena/n2-s148-tour --self-test

The archive retains 45 raw files including 27 actual PNGs (negative captures
included), all engine reports/logs, launch metadata, tour trace, checker log and
wrapper-failure log. artifact-manifest.json indexes every member with size/SHA256
and filesystem save timestamp. Packaging verified each member, extracted into a
fresh temporary directory, reran the full checker, and obtained identical results.
Only then were uncompressed duplicates removed. See verification.json.

Key frames after extraction: evidence/arena/n2-s148-{720p,4x3}/overview.png,
airborne.png, northwest.png, northeast.png and resized.png. Tour frames/trace:
evidence/arena/n2-s148-tour/. All captures are actual renderer output.

Visible Linux desktop camera launch (not the default controls scene):

    "$GODOT_BIN" --path game res://arena_preview.tscn --rendering-method gl_compatibility

Resize and observe corners, high debris and ground contact. It is an animated
camera fixture, not playable combat. Existing destruction_demo.tscn and
opposition.tscn remain available, unchanged; this worker did not validate them.

## Carry forward to node 9, not another numerical-readability loop

node9-handoff.json supplies exact existing recorded paths, verified hashes,
source identities, extraction command and specific review questions. Historical
node2-s138 production dense frame sequences preserve brief actor/exit occlusion;
only *_color.png represents production appearance. Their member hashes were
checked again, not rerendered or claimed current captures. Existing node5-s147
runtime.mp4 provides actual motion including crowded and overload destruction;
its game source matches this source, and its stream metadata/hash and event-based
review times are recorded. It is offline MovieWriter, not real-time performance.

Historical cyan-region retention at dense tick 12 was 27.23% / 37.05%, recovering
at tick 30 to 94.34% / 84.75%. These are sparse local color measurements, not
whole-body visibility, continuous occlusion duration or subjective tolerability.
The tight seven-cube overlap case and outside-envelope escaped below-floor
fragments remain explicit handoff concerns. Do not require every fragment visible
or expand the camera without a demonstrated in-envelope framing defect.

Rick must judge actor/threat tracking, extraction recognition, airborne motion,
contact/weight, resize comfort and satisfaction on the exact final Linux release.
No reliable vision tool was available; no visual/auditory satisfaction is claimed.
The current task explicitly assigns subjective judgment to node 9; historical
intermediate-vision blockers are not instructions to begin another rerun loop.
Final gate is not waived, and the controller alone decides durable completion.
