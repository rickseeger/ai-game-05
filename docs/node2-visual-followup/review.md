# Node 2 visual follow-up: BLOCKED

## Revision and scope

Repository: git@github.com:rickseeger/ai-game-05.git
Target revision: d649df50a96cccb200226bb7886f65abd0e42082.
Fresh clone HEAD exactly matched that revision. This is the target for review,
NOT a revision for which visual acceptance has been established.
Read docs/design.md, docs/arena-validation.md, docs/acceptance.md,
docs/validation.md, and prerequisite-verification/provenance evidence.
The packet states prior independent prerequisite acceptance and automated scene
validation. This worker did not reopen or change those decisions.

## Capability discovery (actual results)

The session tool catalog contains terminal/process and text web tools, but no
image-loading, screenshot perception, browser observation or reviewer tool.
A tool search for image visual inspection/reviewer returned no matches and
reported only the deferred terminal source. No codex or claude executable was
found by command -v. Hermes itself is installed.

Checked the authoritative Hermes documentation:
https://hermes-agent.nousresearch.com/docs/user-guide/features/vision
web_extract failed because the configured Brave backend is search-only; curl
successfully retrieved the actual documentation instead. It describes native
image attachments and the auxiliary vision_analyze path. A text terminal file
read or base64 output is not an image attachment to this worker.

hermes tools list shows vision enabled in CLI configuration. That flag alone is
NOT proof a working image reviewer is available. Inspected the installed
vision_tools.py requirement check, then exercised check_vision_requirements()
using the installed Hermes Python environment and ordinary default-profile
configuration. Reproducible command from repository root:

    /usr/local/lib/hermes-agent/venv/bin/python docs/node2-visual-followup/capability_probe.py

Actual output is retained verbatim in capability-output.txt: requirement check
false; auxiliary vision provider auto, model unset; CLI default main model
DeepSeek V4 Pro, provider deepseek. Resolver logs report OpenRouter unhealthy
with a payment/credit-error label and Nous authentication unavailable. These
are resolver diagnostics, not an independently diagnosed account balance or a
successful image inference request. The probe does not send a frame for review.
This worker session itself identifies as GPT-6 Astra/OpenAI; that is distinct
from the CLI default and does not give this session an exposed image tool.
No alternate provider credentials were provisioned, no configuration was
modified, and no external human reviewer was contacted or available in-session.

Conclusion: no usable image observation path was established with the exposed
tools or configured auxiliary reviewer. Do not mistake an installed/enabled
vision module or a vision-capable model name for receipt of image pixels.

## Observed visual findings

NONE. No frame was visually inspected. Depth cues, visible ground contact,
action silhouette and airborne debris readability remain UNASSESSED here.
There is no pass/fail judgment for any individual frame and no identified
concrete scene/camera defect. No source change is justified by this session.

The previously reported 337 assertions per size, PNG decoding, projected pixel
checks and 720-frame tour are automated evidence supplied by the packet and
repository, not new observations and not a substitute for the missing judgment.
Per the explicit stop condition, no scene was rerendered, no test suite repeated,
and no additional proxy evidence generated. The hash handoff below only names
existing captures precisely; it does not test visual quality.

## Exact captures awaiting human/image-capable review

Preserved in place (read only):
/opt/g-harness/workspace/G12/controller_node2_validation/evidence/arena

captures-requiring-review.json names each existing controller PNG with SHA256.
In each of controller-720p and controller-4x3, inspect:

- overview.png: overall depth, box-face shading, perspective/grid and contact.
- northwest.png, northeast.png, southwest.png, southeast.png: corner actor
  silhouette versus walls/cover, ground ring/shadow visibility and clipping.
- airborne.png: separation of raised cubes from ground and other silhouettes,
  readable height/depth and sufficient frame margin.
- resized.png: retained arena/debris framing and readability after actual resize.

Also inspect controller-tour/tour_0001.png, tour_0120.png, tour_0240.png,
tour_0360.png, tour_0480.png and tour_0600.png alongside its tour.json trace.
These are review QUESTIONS, not findings inferred from filenames.
The repository also retains verified-720p, verified-4x3 and realtime-tour PNGs
at the target revision for remote access; do not relabel those as the controller
captures. Do not use verified-negative frames as positive acceptance evidence.

## Required follow-up

Provide this worker/controller a working image input tool or authenticated
image-capable reviewer, or have a human review the named controller captures.
For full independent scene/camera validation, launch the target revision and
exercise the live resize/animated tour, rather than only trusting stored files.
Documented commands (NOT executed in this follow-up), from repository root:

    GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64 python3 scripts/run_arena.py visual-review-720p
    GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64 python3 scripts/run_arena.py visual-review-4x3 --size 960x720
    GODOT_BIN=/path/to/Godot_v4.5.1-stable_linux.x86_64 python3 scripts/run_arena.py visual-review-tour --tour-frames 720
    /path/to/Godot_v4.5.1-stable_linux.x86_64 --path game --rendering-method gl_compatibility

Use fresh output names. Prior engine provenance identifies a local binary at
/opt/g-harness/workspace/G12/node_1_step_112/tools/Godot_v4.5.1-stable_linux.x86_64;
its availability/version was not rechecked because renderer execution was gated
on establishing image-review capability first.

Record frame-specific actual observations, reviewer identity/capability, exact
revision and commands. Fix only concrete scene/camera defects then rerun affected
validation. Static captures alone do not prove live camera behavior or engine
geometry; combine actual observations with independently accepted runtime/source
evidence. The preview cubes are analytic presentation fixtures, not destruction.
Input, combat, destruction, audio, fun and root acceptance are outside this task.

No mission state was mutated and no node was declared durably complete.
This commit is a durable blocker/handoff report only, not visual approval.
