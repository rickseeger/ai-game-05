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

## Node 2: arena/camera execution evidence (not controller signoff)

- PASS: prerequisite node 1 recorded as independently contract-validated; baseline
  commit and read-only persisted acceptance snapshot in evidence/arena/.
- PASS: 24 x 24m world floor, exact +/-12m inner boundaries, three solid cover
  objects, three pylon sites, six enemy spawn points, player spawn and exit marker.
  Pylon/actor meshes in the preview are noncolliding stand-ins, not gameplay.
- PASS: actual perspective Camera3D and MeshInstance3D rendering through the pinned
  Compatibility renderer; directional lighting/shadows, ground grid/contact ring.
- PASS: two fresh engine launches, 337 assertions each at 1280x720 and 960x720;
  boundary ray/shape queries, spawn clearance, idempotent rebuild, ground aiming,
  perspective scaling, full-envelope framing and live window resize/refit.
- PASS: actual rendered airborne-cube pixels located at projected 3D coordinates;
  seven PNGs per suite decoded and checked independently of engine assertions.
- PASS: 720-frame ordinary real-time animated fixture tour, six more PNGs and
  per-frame position/camera/interval trace. No MovieWriter timing substitution.
- PASS: narrowed-frustum engine negative control rejected; five checker mutations
  rejected. Earlier failed development attempts retained separately, not hidden.
- PENDING: independent controller rerun and visual readability judgment. This
  terminal worker did not observe a desktop, hear audio, or play a game. These
  checks do not validate input, combat, destruction, fun or root satisfaction.


## Node 3: controls execution evidence (not durable acceptance)

- PASS: fresh arena baseline at both sizes, 337 assertions each plus independent
  PNG checks; unchanged Arena/Camera/preview interfaces and geometry.
- PASS: production physical WASD/LMB/Space/Esc/R; real 5m/s CharacterBody movement,
  normalized diagonals, bounded world collision, swept 3m dash/cooldown, all
  walls/covers, sliding/corners and aiming through actual mouse events/resize.
- PASS: actual fire-command press/hold/release/cadence/targeting (not Combat).
- PASS: actual Esc pause/resume with frozen active cooldowns, no stuck input;
  R after injected terminal state, fresh player/controls, repeated restarts;
  focus clearing via an explicitly labelled notification fixture.
- PASS: two rendered input-driven launches with 99 assertions each; independent
  trace/source/image checking, six rejected trace mutations, real disabled-world
  collision negative rejected. evidence/controls/checks.json.
- PENDING: node 2 independent visual assessment, unchanged. Programmatic arena
  reruns do not satisfy that remaining visual gate.
- PENDING: physical-desktop/visual comfort assessment, full Combat, pylon collider
  integration, natural win/loss, complete restart cleanup and exact-release play.
  No playability claim is inferred from these automated tests.

## Node 4: destruction technical evidence (NOT durable completion)

- PASS: fresh rendered arena prerequisite, 337 checks; unchanged arena/camera/player
  source. Controls regression, 99 checks, independent trace/image checkers pass.
- PASS: actual 32/16 independent RigidBody3D boxes, seeded varied upward/spin launch,
  gravity/contact/rebound/tumbling/natural sleep. Render batching copies real poses.
- PASS: same-tick once-only target mesh/collider removal before burst notification;
  bounded 192 bodies, sleeping-first/oldest eviction, final-second shrink, TTL,
  explicit clear, three session restarts and pause freezing.
- PASS: four positive rendered launches, 34 engine assertions each; three full
  220256-sample traces, independent physics checks, 32 timestamped renderer PNGs,
  eight rejected checker mutations and two rejected actual broken-physics runs.
- FAIL reference performance: capture-free lightweight 192-body p95 35.114ms exceeds
  33.3ms on the documented four-vCPU llvmpipe VM. No laptop/GPU result claimed.
- BLOCKED: visual perception/reviewer unavailable; convincing appearance/weight and
  frame-specific launch/impact/rest observations remain unassessed. Node 2 unchanged.
- PENDING: independent observing validator rerun, Combat/opposition/run integration,
  Sound implementation/audible tuning, root fun and exact-release play validation.

See docs/destruction-validation.md and evidence/destruction/checks.json. Earlier
pending release-wide gates remain pending; this feature evidence is not root signoff.
