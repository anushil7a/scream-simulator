"""Generate original, quiet gameplay cues using only the Python standard library.

Run from any directory: python tools/make_gameplay_audio.py
Verify committed assets without writing: python tools/make_gameplay_audio.py --check
No recordings, external libraries, downloads, uploads, or runtime asset IDs are used.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import random
import struct
import wave

RATE = 44100
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "audio" / "gameplay"
VERSION = 1


def smooth(value: float) -> float:
    """Raised-cosine ramp with zero slope at both ends."""
    x = min(1.0, max(0.0, value))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def envelope(t: float, duration: float, attack: float, release: float) -> float:
    if not 0.0 < t < duration:
        return 0.0
    return smooth(t / attack) * smooth((duration - t) / release)


def filtered_noise(count: int, seed: int, low: float, high: float) -> list[float]:
    """Two-pole low-pass, then one-pole high-pass, with deterministic noise."""
    rng = random.Random(seed)
    lp_alpha = 1.0 - math.exp(-math.tau * high / RATE)
    hp_alpha = 1.0 - math.exp(-math.tau * low / RATE)
    state1 = state2 = low_state = 0.0
    result = []
    for _ in range(count):
        state1 += lp_alpha * (rng.uniform(-1.0, 1.0) - state1)
        state2 += lp_alpha * (state1 - state2)
        low_state += hp_alpha * (state2 - low_state)
        result.append(state2 - low_state)
    return result


def hit_confirm() -> list[float]:
    count = round(0.09 * RATE)
    noise = filtered_noise(count, 1001, 950.0, 3400.0)
    result = []
    for i in range(count):
        t = i / RATE
        # Rounded, short body and a restrained bright tick. No impulse samples.
        body = math.sin(math.tau * (780.0 * t - 1250.0 * t * t))
        tick = math.sin(math.tau * (1860.0 * t - 1900.0 * t * t))
        transient = 0.36 * noise[i] * math.exp(-t / 0.014)
        tone = 0.49 * body * math.exp(-t / 0.019)
        tone += 0.12 * tick * math.exp(-t / 0.011)
        result.append((tone + transient) * envelope(t, 0.09, 0.0035, 0.022))
    return result


def dodge_whoosh() -> list[float]:
    count = round(0.25 * RATE)
    rng = random.Random(1002)
    state1 = state2 = low_state = 0.0
    hp_alpha = 1.0 - math.exp(-math.tau * 420.0 / RATE)
    result = []
    for i in range(count):
        x = i / (count - 1)
        # Broad, breath-free air sweep; no formants or pitched vocal layer.
        cutoff = 1100.0 + 2300.0 * math.sin(math.pi * x) ** 1.4
        alpha = 1.0 - math.exp(-math.tau * cutoff / RATE)
        state1 += alpha * (rng.uniform(-1.0, 1.0) - state1)
        state2 += alpha * (state1 - state2)
        low_state += hp_alpha * (state2 - low_state)
        result.append((state2 - low_state) * math.sin(math.pi * x) ** 2.2)
    return result


def prop_break() -> list[float]:
    count = round(0.4 * RATE)
    noise = filtered_noise(count, 1003, 230.0, 3300.0)
    result = []
    debris = ((0.047, 0.075, 0.28), (0.105, 0.090, 0.22),
              (0.184, 0.100, 0.16), (0.268, 0.095, 0.10))
    for i in range(count):
        t = i / RATE
        crack = noise[i] * 1.45 * math.exp(-t / 0.038)
        body = 0.17 * math.sin(math.tau * 455.0 * t) * math.exp(-t / 0.027)
        body += 0.07 * math.sin(math.tau * 815.0 * t) * math.exp(-t / 0.019)
        value = (crack + body) * envelope(t, 0.4, 0.0045, 0.05)
        for start, duration, gain in debris:
            age = t - start
            if 0.0 < age < duration:
                value += gain * noise[i] * math.exp(-age / 0.030) * envelope(
                    age, duration, 0.006, 0.030)
        result.append(value)
    return result


def level_up() -> list[float]:
    count = round(0.65 * RATE)
    # A simple original three-tone rising cue, not a sampled tune or quotation.
    notes = ((0.0, 587.33, 0.28), (0.155, 739.99, 0.30),
             (0.310, 880.0, 0.34))
    result = []
    for i in range(count):
        t = i / RATE
        value = 0.0
        for start, frequency, duration in notes:
            age = t - start
            if 0.0 < age < duration:
                tone = math.sin(math.tau * frequency * age)
                tone += 0.13 * math.sin(math.tau * frequency * 2.0 * age)
                tone += 0.035 * math.sin(math.tau * frequency * 3.0 * age)
                value += tone * envelope(age, duration, 0.012, 0.15)
        result.append(value)
    return result


SPECS = (
    ("hit-confirm", hit_confirm, 0.09, -14.0,
     "Tight rounded tick for a confirmed hit; rate-limit sustained-hit playback."),
    ("dodge-whoosh", dodge_whoosh, 0.25, -16.0,
     "Soft filtered-air sweep for a confirmed roll/dodge."),
    ("prop-break", prop_break, 0.40, -13.5,
     "Muted material crack with restrained debris for an actual prop break."),
    ("level-up", level_up, 0.65, -15.5,
     "Gentle rising three-tone reward for an actual level increase."),
)


def master(raw: list[float], peak_dbfs: float) -> list[int]:
    """Remove sub-bass/DC, gently round edges, then scale without clipping."""
    alpha = 1.0 - math.exp(-math.tau * 130.0 / RATE)
    low_state = 0.0
    filtered = []
    weights = []
    for i, value in enumerate(raw):
        low_state += alpha * (value - low_state)
        filtered.append(value - low_state)
        weights.append(smooth(i / (RATE * 0.002)) *
                       smooth((len(raw) - 1 - i) / (RATE * 0.008)))
    # Weighted DC correction preserves exact silence at the file boundaries.
    dc = sum(v * w for v, w in zip(filtered, weights)) / sum(weights)
    samples = [(v - dc) * w for v, w in zip(filtered, weights)]
    gain = 10.0 ** (peak_dbfs / 20.0) / max(abs(v) for v in samples)
    pcm = [round(v * gain * 32767.0) for v in samples]
    if any(abs(v) >= 32767 for v in pcm):
        raise ValueError("Unexpected clipping; refusing to write a clipped asset")
    return pcm


def wav_bytes(pcm: list[int]) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(struct.pack(f"<{len(pcm)}h", *pcm))
    return out.getvalue()


def dbfs(amplitude: float) -> float | None:
    return round(20.0 * math.log10(amplitude), 5) if amplitude else None


def measure(name: str, pcm: list[int], data: bytes) -> dict:
    values = [v / 32768.0 for v in pcm]
    peak = max(abs(v) for v in values)
    rms = math.sqrt(sum(v * v for v in values) / len(values))
    return {
        "file": name,
        "frames": len(pcm),
        "seconds": round(len(pcm) / RATE, 6),
        "bytes": len(data),
        "peak_dbfs": dbfs(peak),
        "rms_dbfs": dbfs(rms),
        "crest_factor_db": round(20.0 * math.log10(peak / rms), 5),
        "mean_dc_full_scale": round(sum(values) / len(values), 10),
        "max_adjacent_delta_full_scale": round(max(
            abs(a - b) for a, b in zip(values, values[1:])), 8),
        "clipped_samples": sum(abs(v) >= 32767 for v in pcm),
        "first_sample": pcm[0],
        "last_sample": pcm[-1],
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def validate(pcm: list[int], data: bytes, duration: float) -> None:
    """Validate exported PCM, not only the floating-point synthesis buffers."""
    with wave.open(io.BytesIO(data), "rb") as wav:
        assert wav.getparams()[:4] == (1, 2, RATE, round(duration * RATE))
        decoded = list(struct.unpack(f"<{wav.getnframes()}h", wav.readframes(wav.getnframes())))
    assert decoded == pcm, "WAV payload mismatch"
    assert pcm[0] == pcm[-1] == 0, "Nonzero file boundary"
    assert 0 < max(abs(v) for v in pcm) < 0.225 * 32768, "Peak outside quiet budget"
    assert abs(sum(pcm) / len(pcm) / 32768.0) < 0.00002, "Unexpected DC"
    assert math.sqrt(sum((v / 32768.0) ** 2 for v in pcm) / len(pcm)) < 0.13
    assert all(abs(v) < 32767 for v in pcm), "PCM clipping"


def build() -> tuple[dict[str, bytes], dict]:
    files = {}
    assets = []
    cues = []
    preview = [0] * round(0.35 * RATE)
    for name, synth, duration, peak, purpose in SPECS:
        pcm = master(synth(), peak)
        filename = f"{name}.wav"
        data = wav_bytes(pcm)
        validate(pcm, data, duration)
        files[filename] = data
        record = measure(filename, pcm, data)
        record.update({"purpose": purpose, "design_peak_dbfs": peak,
                       "roblox_asset_id": None})
        assets.append(record)
        start = len(preview)
        preview.extend(pcm)
        cues.append({"cue": name, "start_frame": start,
                     "start_seconds": round(start / RATE, 6),
                     "end_seconds": round(len(preview) / RATE, 6)})
        preview.extend([0] * round(0.60 * RATE))
    # Keep only 350 ms of the final inter-cue silence.
    preview = preview[:len(preview) - round(0.25 * RATE)]
    preview_data = wav_bytes(preview)
    validate(preview, preview_data, len(preview) / RATE)
    files["gameplay-preview.wav"] = preview_data
    manifest = {
        "schema_version": VERSION,
        "sample_rate_hz": RATE,
        "channels": 1,
        "pcm_bits": 16,
        "origin": "Original deterministic oscillator and seeded-noise synthesis; no recordings or external samples.",
        "generator": "tools/make_gameplay_audio.py",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "external_dependencies": [],
        "status": "Local originals for review; no Roblox upload or publication performed.",
        "measurement_note": "Peak/RMS/DC are decoded 16-bit PCM measurements, not LUFS, SPL, or a listening result.",
        "assets": assets,
        "preview": {**measure("gameplay-preview.wav", preview, preview_data), "cues": cues},
    }
    files["audio-manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    lines = [
        "# Original gameplay audio", "",
        "Four locally synthesized, voice-first one-shot cues. No external recordings, samples,",
        "libraries, downloaded code, or franchise audio are used. The generator uses only the",
        "Python standard library and fixed seeds. These files do not replace the owner's",
        "equipped-scream audio. All WAVs are mono 44,100 Hz, 16-bit PCM.", "",
        "## Assets", "",
        "| File | Duration | Peak | RMS | Intended event |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in assets:
        lines.append(f"| {record['file']} | {record['seconds']:.2f} s | "
                     f"{record['peak_dbfs']:.2f} dBFS | {record['rms_dbfs']:.2f} dBFS | "
                     f"{record['purpose']} |")
    lines += ["", "## Audition", "",
              "Play `gameplay-preview.wav` at a low, comfortable device volume. The preview",
              "uses the exact asset PCM without extra gain. Labels are listed below rather",
              "than spoken into the file; no voice samples are present.", "",
              "| Cue | Start | End |", "| --- | --- | --- |"]
    for cue in cues:
        lines.append(f"| {cue['cue']} | {cue['start_seconds']:.2f} s | {cue['end_seconds']:.2f} s |")
    lines += [
        "", "## Regenerate and verify", "",
        "From the repository root, run `python tools/make_gameplay_audio.py` to rebuild this",
        "folder. Run `python tools/make_gameplay_audio.py --check` to regenerate in memory",
        "and compare every WAV, this README, and the JSON manifest byte-for-byte without",
        "writing. The manifest contains file SHA-256 hashes, the generator hash, PCM",
        "levels, boundary/DC checks, durations, and the preview cue frames.", "",
        "The generator validates actual exported PCM headers/payloads, duration, non-silence,",
        "zero-valued start/end samples, modest peak/RMS bounds, DC, and absence of clipping.",
        "Determinism was checked with the installed Python runtime; math-library changes",
        "on other systems may affect rounding near a quantization boundary.", "",
        "## Integration and remaining checks", "",
        "These are local candidate assets, not uploaded Roblox IDs. No asset access, runtime",
        "playback, publication, or human-listening approval is implied. Upload the four",
        "individual cues only after the owner approves upload and intended experience",
        "access, then configure the returned IDs. Do not upload the combined preview.", "",
        "Use quiet runtime gain, bounded simultaneous sources, event throttling, voice",
        "ducking, calibration silence, and a user off control. Do not retrigger the hit",
        "cue every damage tick or the level cue for each intermediate level in one reward.",
        "Check actual repeated-hit/dodge/destruction/reward flows, cleanup and mute, then",
        "listen with headphones and speakers alongside player voice and equipped-scream",
        "audio. Loudness, intelligibility and microphone-feedback comfort still require",
        "human/device testing. Numerical dBFS is not a hearing-safety guarantee or LUFS.", "",
        "Asset provenance is the original generator here. No legal conclusion about",
        "copyright ownership or a third-party library license is asserted.", "",
    ]
    files["README.md"] = "\n".join(lines).encode("utf-8")
    return files, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing files without writing")
    args = parser.parse_args()
    files, manifest = build()
    if args.check:
        mismatches = [name for name, data in files.items()
                      if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if mismatches:
            raise SystemExit("Missing or changed generated files: " + ", ".join(mismatches))
        print(f"PASS: {len(files)} generated files match; WAV PCM, bounds, hashes and cue timing verified.")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (OUT / name).write_bytes(data)
        print(f"Wrote {len(files)} generated files to {OUT}")
    print(json.dumps({"assets": manifest["assets"], "preview": manifest["preview"]}, indent=2))


if __name__ == "__main__":
    main()
