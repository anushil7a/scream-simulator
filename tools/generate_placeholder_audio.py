"""Generate original, temporary cartoon scream effects as 16-bit mono WAV files.

These are synthetic placeholders, not copies of meme recordings. Import them in
Roblox Studio and set the approved asset IDs in Config.luau before publishing.
"""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

RATE = 22_050
OUTPUT = Path(__file__).resolve().parents[1] / "audio"
RNG = random.Random(8044)


def envelope(t: float, duration: float, attack: float = 0.035) -> float:
    return min(1.0, t / attack) * min(1.0, (duration - t) / 0.10)


def voiced(t: float, start: float, end: float, duration: float, wobble: float = 0.0) -> float:
    pitch = start + (end - start) * (t / duration) + wobble * math.sin(2 * math.pi * 13 * t)
    phase = 2 * math.pi * (start * t + 0.5 * (end - start) * t * t / duration)
    value = 0.0
    for harmonic in range(1, 9):
        weight = 1.0 / harmonic**1.05
        if 650 < harmonic * pitch < 1800:
            weight *= 1.8
        value += weight * math.sin(harmonic * phase)
    return value / 3.0


def segment(duration: float, start: float, end: float, *, wobble: float = 0.0, grit: float = 0.0) -> list[float]:
    samples = []
    for index in range(round(duration * RATE)):
        t = index / RATE
        carrier = voiced(t, start, end, duration, wobble)
        rough = RNG.uniform(-1, 1) * grit
        samples.append(envelope(t, duration) * (carrier + rough))
    return samples


def silence(duration: float) -> list[float]:
    return [0.0] * round(duration * RATE)


def bass_hit(duration: float, start: float = 130.0) -> list[float]:
    samples = []
    for index in range(round(duration * RATE)):
        t = index / RATE
        phase = 2 * math.pi * (start * t - 0.5 * (start - 55) * t * t / duration)
        samples.append(0.6 * math.exp(-18 * t) * math.sin(phase))
    return samples


def mix(*tracks: list[float]) -> list[float]:
    length = max(map(len, tracks))
    return [sum(track[i] if i < len(track) else 0 for track in tracks) for i in range(length)]


def write(name: str, samples: list[float]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    peak = max(1.0, max(abs(value) for value in samples) / 0.82)
    payload = b"".join(struct.pack("<h", round(max(-1, min(1, value / peak)) * 32767)) for value in samples)
    with wave.open(str(OUTPUT / f"{name}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(payload)


def main() -> None:
    tiny = segment(0.48, 460, 700, wobble=12, grit=0.05)
    pop = mix(segment(0.32, 340, 870, wobble=20, grit=0.08), bass_hit(0.27))
    chicken = segment(0.31, 700, 930, wobble=45, grit=0.09) + silence(0.08) + segment(0.60, 560, 1080, wobble=65, grit=0.14)
    laugh = (
        segment(0.17, 390, 520, wobble=18, grit=0.04)
        + silence(0.06)
        + segment(0.18, 410, 550, wobble=18, grit=0.04)
        + silence(0.06)
        + segment(0.70, 520, 250, wobble=36, grit=0.16)
    )
    long_shout = segment(1.05, 280, 660, wobble=42, grit=0.18)
    low_layer = segment(1.05, 145, 310, wobble=10, grit=0.08)
    mega = mix(long_shout, low_layer, bass_hit(0.55, 170))
    for name, samples in {
        "TinyAah": tiny,
        "IyoPop": pop,
        "PanicChicken": chicken,
        "Laughquake": laugh,
        "MegaChaos": mega,
    }.items():
        write(name, samples)
        print(OUTPUT / f"{name}.wav")


if __name__ == "__main__":
    main()
