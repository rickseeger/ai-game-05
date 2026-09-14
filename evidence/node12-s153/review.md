# Node 12 delivery: default Linux session and reliable shared retry

Tested and pushed source: 08dfe3261aa662d302331f5b8e6264836a0169c2.
Accepted base: ea9bab25d6de2caac5939d91c123f2a818c1e78f (node 11).
Authors: the gardener <root@g.seeger.net>.
See docs/session-integration.md for implementation and exact reproduction.
Prerequisites.json records node 11 independently accepted and node 12's contract;
worker did not declare or change durable mission-node completion.

## Actual results

Ran .tools/validation-venv/bin/python scripts/verify_integration_node12.py
n12-s153-final at the tested source. All eight top-level commands returned zero,
including the nested fifteen-command accepted-subsystem verifier. A plain
no-test-flag default entry also ran 120 frames without engine errors. Rendering
was Linux X11, Godot 4.5.1 Compatibility OpenGL, Mesa llvmpipe; Dummy audio is
explicit. No scene override is passed to default-entry integration launches.

Both fresh default processes passed 127 assertions each. Each performed six
forced win/death/timeout retry cycles, with live production opposition, a real
normal-input four-hit pylon destruction, pause/resume, and fresh movement/fire
following each retry. They check immediate state restoration, old objects freed,
no stale firing/dash/audio, three intact pylons and locked extraction, two seeded
warning spawns, stable node/bus/connection counts and one notification per reset.
Python independently recomputes HUD bindings, clock, input, objective and reset
event invariants and rejects eight mutated traces per run.

Each captured 16 fresh Linux PNGs, including default play, pause, 960x720 layout,
explicit victory/death/timeout fixtures, unlocked extraction and live retry.
Code-level hide/restore tests: 12494 changed HUD text pixels, 138370 panel pixels,
1090 locked marker pixels (658 amber) and 948 open marker pixels (643 green).
Each paused restoration is pixel-identical. Images decode to the requested
1280x720 / 960x720 dimensions; text/panel deltas lie within recorded UI bounds.
This proves rendering/state binding, not human readability.

After source push, cloned git@github.com:rickseeger/ai-game-05.git again into a
separate clean checkout, imported assets, and launched the actual default entry
through run_integration.py. That remote-source run also passed 127 assertions,
six forced resets, 16 captures and the independent checker. Clean status was
empty; its source revision matches the above. clean-remote-verification.tar.gz
contains commands, source metadata, engine logs, snapshots and PNGs. This is an
independent clean-checkout execution, NOT an independent human acceptance.

Accepted regressions rerun without weakening their tests:
- Session rules: two runs, 55 assertions each, same-tick loss-before-win and real
  combat/destruction/audio routing preserved, six trace mutations rejected.
- Opposition: focused 47, inactive 5, active 12 assertions. Inactive player died
  naturally at tick 543 / 9.05 seconds from seven hits; active survived 30 seconds
  with 70 health and destroyed three SENTRIES, not the three objective pylons.
- Controls: unchanged 99 assertions and six negative trace controls passed.
- Destruction: 34 assertions; 220256 samples; 32 independently checked arcs;
  eight mutated traces rejected. This no-capture fixture measured p95 32.274ms
  on llvmpipe versus 33.3ms target; not a whole-game/laptop performance verdict.
- Sound: unchanged 738 assertions, 267 same-tick source/voice matches, eight-voice
  cap; actual engine mixer 26.25s stereo 48000Hz PCM, sample peak 0.7943325,
  4x true peak 0.8034191, zero clipped samples, mute/zero-master silence. Decoded
  video 1575 frames; eight signal/routing corruptions rejected. Not speaker proof.
- Arena: 337 assertions. Ring batching: 349 assertions. No rendering/collision
  tuning or sound synthesis/mix edits were needed.
All exact commands, stdout/stderr, source hashes and raw traces are archived.

## Development history, not concealed failures

The first development driver passed 123 checks, before adding extra marker pixel
pairs and the real HUD backing panel. The next passed all engine checks, but the
new independent checker rejected a phase-labeling mistake: the final intentional
pause belonged to the last reset phase and looked like an extra reset state event.
Driver now labels final replay separately; no runtime behavior weakened.

The first complete verifier at 24990b64cdae74f8a759f2ded507a79e3d4f4e67 failed three
accepted controls-only fresh-fire checks because global pointer clearing changed
that isolated slice's contract. Fixed by scoping pointer clearing to production's
rebuild_run hook, leaving accepted controls behavior/tests unchanged. Reran the
ENTIRE verification at 08dfe3261aa662d302331f5b8e6264836a0169c2, all passing. Initial
runs and failed controls evidence remain in development-history.tar.gz.

## Scope and reproduction

Forced terminal fixtures inject damage, position and clock solely to exercise
reset boundaries. They are NOT natural complete-session victories. Do not infer
fun, balance, readability, visual quality or audible satisfaction from passes.
Rick's node-9 concern: assess dense HUD text, extraction text and terminal overlay
on his actual display, and sound/keyboard feel. Node 13 owns natural full-session
victory/defeat/replay and bounded tuning. Node 8 owns packaging. No human playtest
was solicited and no subjective gate was waived.

From a clean Linux clone at the tested source (or evidence-only delivery commit):

    ./scripts/setup.sh
    .tools/Godot_v4.5.1-stable_linux.x86_64 --headless --path game --editor --import --quit
    uv venv .tools/validation-venv
    uv pip install --python .tools/validation-venv/bin/python numpy==2.5.3 scipy==1.18.1 pillow==12.3.0
    .tools/validation-venv/bin/python scripts/verify_integration_node12.py independent-n12

For archived validation, extract raw-runs.tar.gz at the repository root; its
members retain evidence/n12-s153-final-... paths. Then:

    .tools/validation-venv/bin/python scripts/check_integration.py evidence/n12-s153-final-integration-1 evidence/n12-s153-final-integration-2

For actual desktop play (no test driver):

    .tools/Godot_v4.5.1-stable_linux.x86_64 --path game

Artifact manifest covers all archived files. Excluded only disposable shader
cache files and the redundant MovieWriter AVI: original decoded PCM and MP4,
engine traces, encoding logs and video metadata remain for regression checking.
