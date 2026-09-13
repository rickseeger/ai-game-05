#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .tools
url=https://github.com/godotengine/godot-builds/releases/download/4.5.1-stable/Godot_v4.5.1-stable_linux.x86_64.zip
curl -fL "$url" -o .tools/godot.zip
printf '%s  %s\n' '02ec53d1cc7dbb9cc6355393c61b9ab43d1244751a124f10248a4802830788cd' '.tools/godot.zip' | sha256sum -c -
(cd .tools && unzip -o godot.zip)
.tools/Godot_v4.5.1-stable_linux.x86_64 --version
