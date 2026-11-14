"""Reproducible original synthesis; stdlib only, no sampled franchise audio.

Writes a seamless two-second mono loop and a four-second attack audition.
The audition is louder than the deliberately quiet in-game mix for review.
"""
from pathlib import Path
import hashlib
import json
import math
import random
import struct
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audio'
RATE = 44100
DURATION = 2


def write(name, samples):
    path = OUT / name
    pcm = b''.join(struct.pack('<h', round(max(-1, min(1, s))*32767)) for s in samples)
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm)
    rms = math.sqrt(sum(s*s for s in samples)/len(samples))
    return {'file': name, 'seconds': len(samples)/RATE,
            'peakDbFS': 20*math.log10(max(abs(s) for s in samples)),
            'rmsDbFS': 20*math.log10(rms),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(92026)
    # Classic anime beam character: rushing noise, snarling FM energy, fluttering
    # electric whine and a compressed low body. Timbre stays forceful; playback
    # volume, rather than removing the character, keeps it beneath player voice.
    # All tonal cycles repeat across two seconds. Warm filters for two periods
    # of the same deterministic noise before capturing the third loop.
    count = RATE*DURATION
    noise = [rng.uniform(-1, 1) for _ in range(count)]
    loop = []
    low = high = grit = 0
    for i in range(count*3):
        j = i % count
        t = j/RATE
        cutoff = 2900+900*math.sin(math.tau*t)
        low += (noise[j]-low)*(1-math.exp(-math.tau*cutoff/RATE))
        high += (noise[j]-high)*(1-math.exp(-math.tau*240/RATE))
        rush = (low-high)*(.7+.3*math.sin(math.tau*13*t)**2)
        grit += (noise[j]-grit)*(1-math.exp(-math.tau*1500/RATE))
        crackle = (noise[j]-grit)*max(0, math.sin(math.tau*23*t))**6
        snarl = math.sin(math.tau*280*t+4.8*math.sin(math.tau*93.5*t)+.6*math.sin(math.tau*4*t))
        whine = math.sin(math.tau*1020*t+7*math.sin(math.tau*3*t)+1.8*math.sin(math.tau*61*t))
        body = math.sin(math.tau*70*t+1.2*math.sin(math.tau*35*t))
        beam = .8*rush+.22*snarl+.13*whine+.09*body+.09*crackle
        sample = math.tanh(beam*2.0)*(.84+.16*math.sin(math.tau*9*t)**2)
        if i>=count*2:
            loop.append(sample)
    # Remove DC; limit the original master peak to -9 dBFS.
    mean = sum(loop)/len(loop)
    loop = [s-mean for s in loop]
    scale = 10**(-9/20)/max(abs(s) for s in loop)
    loop = [s*scale for s in loop]
    attack = []
    position = 0
    for i in range(round(RATE*4.16)):
        t = i/RATE
        release = max(0, min(1, (t-4)/.16))
        pitch = (.68+.32*min(t/.22, 1))*(1-.24*release)
        envelope = min(t/.12, 1)*(1-release)
        index = int(position) % len(loop)
        fraction = position-int(position)
        sample = loop[index]*(1-fraction)+loop[(index+1) % len(loop)]*fraction
        attack.append(sample*envelope*.7)
        position += pitch
    records = [write('energy-beam-loop.wav', loop), write('energy-beam-preview.wav', attack)]
    assert max(abs(s) for s in loop) < .36
    # A broadband waveform need not have identical adjacent samples. Its loop
    # seam must be no sharper than ordinary neighboring-sample transitions.
    assert abs(loop[0]-loop[-1]) <= max(abs(a-b) for a, b in zip(loop, loop[1:])), 'Loop boundary discontinuity'
    assert attack[0] == 0 and abs(attack[-1]) < .001, 'Audition fade boundary'
    (OUT/'audio-audit.json').write_text(json.dumps({'sampleRate': RATE, 'channels': 1,
        'origin': 'Original deterministic oscillator synthesis; no recordings or external samples',
        'loopBoundaryDelta': abs(loop[0]-loop[-1]), 'assets': records}, indent=2)+'\n')
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
