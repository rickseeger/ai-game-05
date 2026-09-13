# Acceptance checklist

These are worker evidence results, not durable node or root completion decisions.
PASS means observed by the specified measurement; PENDING means not done.

## Node 1: bounded design and technology proof

- PASS: read persisted node 1 and root contracts unchanged, repo_url and budget
  from read-only SQLite; locate actual harness interface. evidence/context.json.
- PASS: clone configured ai-game-05 repository, verify initially empty and configure
  requested git author. Repository work is independent of mission-tree state.
- PASS: choose real 3D rendering, rigid-body physics and audio stack; Linux runtime
  and pinned reproducible download. README.md, dependencies.txt, setup.log.
- PASS: compact game design names agency, moving/shooting opposition, explicit
  victory/defeat and destruction required for victory. docs/design.md (design only).
- PASS: destruction counts, random upward/spin velocities, gravity/collision,
  bounce/friction/tumble, lifetime/caps and sound synchronization specified.
- PASS: module interfaces, implementation order and budget stop/reserve policy.
- PASS: two separate engine/movie launches, 420 frames each; full 3D scene with
  camera, light, perspective grid, solid ground and 32 independent rigid cubes.
  run1/ and run2/ each retain four PNGs and a complete MP4, engine log and traces.
- PASS: both evidence checks rerun and inspected programmatically; all 32 bodies
  rose, fell, rotated, contacted ground, bounced and settled. Ground tumbling
  observed. Physics and event traces and captured PCM match across these runs.
- PASS: actual Godot mixed stereo PCM at 48 kHz, nonzero destruction and impact
  windows; no full-scale clipping. Signal capture, NOT audible playback.
- PASS: checks reject substituted silence and static physics in temporary negative
  controls. No substituted evidence is retained as an actual run.
- PASS: ordinary real-time launch reaches tick 420. Hardware audio attempt fails
  on ALSA, falls back to Dummy; failure preserved, not hidden. realtime/engine.log.
- PASS: document independent exact-release visual/audible interactive gate and
  environmental blockers, without inferring fun or satisfaction from logs.

## Later feature/release gates: ALL PENDING

- Player movement/aim/fire/dash/pause works on actual input; movement cannot leave
  arena or cross intact cover. Resume does not jump simulation or timers.
- Enemy visibly approaches/telegraphs/fires; shots collide correctly with cover;
  surviving inactivity is not a win; death is achievable. Spawn cap/spacing holds.
- Every damage event applied once; destroyed target collider removed once;
  destroyed pylons permanently advance counter; three pylons plus exit wins;
  time/health loss and simultaneous terminal-event precedence tested.
- Fragment cap 192, TTL/fade, sleep and restart cleanup; no residual bodies or
  audio voices after repeated restarts; stressed contact/memory cost measured.
- Impact energy gate and per-body cooldown reduce chatter; destruction and impacts
  synchronized, clear and satisfying when actually heard; spatial cues/gain and
  mute settings correct. Probe sound alone does not meet this subjective gate.
- 192-body stress at 1280x720 meets declared frame-time target on documented
  Linux hardware; reference laptop run, not MovieWriter throughput extrapolation.
- HUD teaches controls, threat, health, objectives and explicit win/loss/retry;
  readable silhouettes and sound survive dense debris. At least three play runs,
  including natural victory, deliberate defeat and a fresh restart.
- Source, tests, release export, licenses, engine version and exact artifact SHA256
  recorded; run on clean Linux outside the source checkout. No editor dependency.
- G interactively plays EXACT release and directly inspects visual/audio evidence;
  addresses any real tension/fun failures. Rick's feedback is useful but must not
  be relabeled as G's own play. Enable missing GUI/audio capabilities first.
- Root subjective validation and human approval remain unfulfilled, unchanged.
