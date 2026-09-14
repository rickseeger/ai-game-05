#!/usr/bin/env python3
"""Original deterministic PCM synthesis; no samples, models or external assets.
Copyright 2026 the gardener. MIT, same license as repository.
"""
import math, random, wave, struct, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game/audio"
OUT.mkdir(exist_ok=True)
manifest = {}
for kind, count, duration in [("break", 4, .62), ("impact", 6, .19)]:
    for variant in range(count):
        rng = random.Random(120141 + variant + (100 if kind == "impact" else 0))
        data = []; low = 0.0; phase = 0.0
        for i in range(round(48000 * duration)):
            t = i / 48000
            noise = rng.uniform(-1, 1)
            low += .13 * (noise - low)
            attack = min(1, t / .0015)
            if kind == "break":
                # Sharp broadband fracture, descending sub/body thump, metal/grit tail.
                f = 49 + variant * 3 + 95 * math.exp(-t * 24)
                phase += 2 * math.pi * f / 48000
                value = (.85 * math.sin(phase) * math.exp(-t * 12)
                    + .85 * noise * math.exp(-t * 105)
                    + .42 * low * math.exp(-t * 9)
                    + .12 * math.sin(2 * math.pi * (780 + 83*variant)*t) * math.exp(-t*29))
            else:
                f = 155 + variant * 33
                value = (.68 * math.sin(2*math.pi*f*t) * math.exp(-t*36)
                    + .7 * noise * math.exp(-t*130)
                    + .19 * math.sin(2*math.pi*(1103+127*variant)*t)*math.exp(-t*42))
            data.append(value * attack * min(1, (duration-t)/.015))
        scale = .92 / max(map(abs, data))
        pcm = struct.pack("<%dh" % len(data), *(round(v * scale * 32767) for v in data))
        path = OUT / ("%s_%d.wav" % (kind, variant))
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(pcm)
        manifest[path.name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "duration_s": duration, "peak": .92, "seed": 120141 + variant + (100 if kind == "impact" else 0)}
(OUT / "provenance.json").write_text(json.dumps({"license": "MIT (../../LICENSE)", "author": "the gardener <root@g.seeger.net>", "source": "scripts/generate_sound_assets.py", "inputs": "Only deterministic PRNG noise and mathematical oscillators; no external samples or AI-generated recordings", "assets": manifest}, indent=2)+"\n")
