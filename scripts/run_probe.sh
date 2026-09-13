#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root="$PWD"
godot="${GODOT_BIN:-$root/.tools/Godot_v4.5.1-stable_linux.x86_64}"
run="${1:-run-local}"
mkdir -p "evidence/$run"
export PROBE_OUT="$root/evidence/$run"
export LIBGL_ALWAYS_SOFTWARE=1
export GODOT_SILENCE_ROOT_WARNING=1
# Movie mode drives the real audio mixer offline; Dummy is NOT speaker playback.
xvfb-run -a -s '-screen 0 960x540x24' "$godot" --path "$root/probe" --rendering-method gl_compatibility --audio-driver Dummy --write-movie "$PROBE_OUT/movie.avi" --fixed-fps 60 > "$PROBE_OUT/engine.log" 2>&1
ffmpeg -y -i "$PROBE_OUT/movie.avi" -vn -c:a pcm_s16le "$PROBE_OUT/audio.wav" > "$PROBE_OUT/extract.log" 2>&1
for spec in '0.9 launch' '1.5 airborne' '2.6 collision' '6.5 settled'; do
    read -r time label <<< "$spec"
    ffmpeg -y -ss "$time" -i "$PROBE_OUT/movie.avi" -frames:v 1 -update 1 "$PROBE_OUT/$label.png" >> "$PROBE_OUT/extract.log" 2>&1
done
# Retain compact, inspectable video instead of bulky temporary MJPEG/PCM AVI.
ffmpeg -y -i "$PROBE_OUT/movie.avi" -c:v libx264 -crf 23 -pix_fmt yuv420p -c:a aac "$PROBE_OUT/probe.mp4" >> "$PROBE_OUT/extract.log" 2>&1
python3 scripts/check_probe.py "$PROBE_OUT" > "$PROBE_OUT/checks.json"
rm "$PROBE_OUT/movie.avi"
