#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$(uname -m)" != x86_64 ]; then
    printf "%s\n" "This release supports Linux x86_64 only." >&2; exit 1
fi
ENGINE="$ROOT/runtime/Godot_v4.5.1-stable_linux.x86_64"
if [ ! -x "$ENGINE" ]; then
    printf "%s\n" "Bundled runtime missing. Use the extracted release; see docs/linux-release.txt." >&2; exit 1
fi
# Import from included originals on every launch; no inherited editor cache needed.
# The extracted directory must be writable. Import uses Dummy; gameplay does not.
"$ENGINE" --headless --path "$ROOT/game" --editor --import --quit
if [ "${1:-}" = --import-only ]; then exit 0; fi
exec "$ENGINE" --path "$ROOT/game" --rendering-method gl_compatibility --display-driver x11 "$@"
