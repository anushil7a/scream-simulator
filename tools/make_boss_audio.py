#!/usr/bin/env python3
"""Original deterministic boss cues, stdlib only. Run with --check to audit bytes.
No samples, downloads, voice imitation, copyrighted melodies, or uploads.
"""
import argparse, hashlib, io, json, math, pathlib, random, struct, wave
ROOT=pathlib.Path(__file__).resolve().parents[1]/'assets/audio/bosses'
RATE=24000
SPECS={
 'metronome':('Clockwork Metronome','precise wood/metal ticking',.55,.40),
 'golem':('Stone Golem','rounded bass stone resonance',.72,.82),
 'ignis':('Ignis','organ-pipe warning and fire crackle',.85,.78),
 'leviathan':('Seagull Siren Captain','maritime horn and cutlass slash; not a sea monster',1.0,.62),
 'conductor':('Conductor','harmonic bell and resonant downbeat',.82,1.05),
}
def tone(t,f):return math.sin(math.tau*f*t)
def decay(t,start,length):
 d=t-start
 return math.exp(-d*7/length) if 0<=d<length else 0.0
def synth(key,stage,duration):
 seed=int.from_bytes(hashlib.sha256((key+'/'+stage).encode()).digest()[:8],'little')
 rng=random.Random(seed);samples=[];last=0
 for i in range(round(RATE*duration)):
  t=i/RATE;noise=rng.uniform(-1,1);last=.92*last+.08*noise
  if key=='metronome':
   if stage=='tell':
    value=sum(decay(t,p,.11)*(.6*tone(t-p,1150)+.28*noise+.25*tone(t-p,2800)) for p in (.03,.22,.41))
   else:value=decay(t,.01,.38)*(.7*tone(t,690)+.25*tone(t,2070)+.2*noise)
  elif key=='golem':
   if stage=='tell':value=(.7*tone(t,115)+.25*tone(t,172.5)+.15*last)*(.7+.3*tone(t,4))
   else:value=math.exp(-t*5)*(.8*math.sin(math.tau*(105*t-22*t*t))+.25*tone(t,210)+.35*last)+.13*noise*math.exp(-t*35)
  elif key=='ignis':
   if stage=='tell':value=(.55*tone(t,196)+.28*tone(t,392)+.16*tone(t,588))*(.4+.6*min(1,t/.45))+.06*noise
   else:value=(.4*tone(t,147)+.2*tone(t,294))*math.exp(-t*4)+noise*(.35*math.exp(-t*5)+.12*(max(0,tone(t,19))**14))
  elif key=='leviathan':
   if stage=='tell':value=(.55*tone(t,220)+.27*tone(t,330)+.18*tone(t,440))*(.75+.25*tone(t,3))
   else:
    # Cutlass: short bright sweep plus metal ring, not monster vocalization.
    value=.5*noise*math.exp(-((t-.12)/.07)**2)+(.25*tone(t,1300)+.14*tone(t,1950))*math.exp(-t*9)
  else:
   if stage=='tell':value=sum(a*tone(t,f)*math.exp(-t*d) for a,f,d in [( .6,660,2),(.3,1320,4),(.15,1980,6)])
   else:value=sum(a*tone(t,f)*math.exp(-t*d) for a,f,d in [(.6,330,3),(.25,660,5),(.2,990,6),(.12,1650,8)])+.05*noise*math.exp(-t*30)
  fade=min(1,t/.012,(duration-t)/.09)
  samples.append(value*max(0,fade))
 # Remove DC using a tapered correction, preserving silent endpoints.
 weights=[min(1,i/(RATE*.012),(len(samples)-1-i)/(RATE*.09)) for i in range(len(samples))]
 dc=sum(samples)/sum(weights)
 samples=[v-dc*w for v,w in zip(samples,weights)]
 peak=max(abs(v) for v in samples);samples=[v*.46/peak for v in samples]
 pcm=[max(-32767,min(32767,round(v*32767))) for v in samples];pcm[0]=0;pcm[-1]=0
 stream=io.BytesIO()
 with wave.open(stream,'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(struct.pack('<%dh'%len(pcm),*pcm))
 raw=stream.getvalue()
 audit={'file':f'{key}-{stage}.wav','boss':key,'stage':stage,'durationSeconds':len(pcm)/RATE,'sampleRate':RATE,'channels':1,'bits':16,
        'peak':round(max(abs(v) for v in pcm)/32768,7),'rms':round(math.sqrt(sum((v/32768)**2 for v in pcm)/len(pcm)),7),
        'dc':round(sum(pcm)/len(pcm)/32768,9),'sha256':hashlib.sha256(raw).hexdigest(),'robloxAssetId':''}
 assert audit['peak']<=.5 and abs(audit['dc'])<.00001 and pcm[0]==pcm[-1]==0
 return raw,audit
README='''# Original boss warning and impact cues

Ten original procedural mono 16-bit PCM WAVs, 24 kHz. Generated entirely with
Python standard-library oscillators and seeded noise, without downloaded samples,
recordings, speech, or borrowed melodies. Each warning has a visually paired runtime
cue; sound must never be the only attack warning. Tell/impact distinction comes from
rhythm, spectrum and envelope rather than higher volume. The `leviathan` routing key
is the Seagull Siren Captain: maritime horn/cutlass identity, not a sea monster.

Peak <= 0.46 full scale, tapered starts/ends, near-zero DC. Peak-safe source files do
not establish safe playback loudness or good game mixing. Runtime warning priority,
concurrency caps, spatial attenuation, cleanup and actual-device listening remain
integration responsibilities. No Roblox asset IDs assigned and no uploads performed.
These WAVs are delivery sources, not yet audible custom Roblox assets; keep approved
runtime fallback until the owner authorizes import/upload and the IDs are verified.

Rebuild: python tools/make_boss_audio.py
Verify deterministic bytes and audits: python tools/make_boss_audio.py --check
'''
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 outputs={};entries=[]
 for key,(name,theme,tell,impact) in SPECS.items():
  for stage,duration in [('tell',tell),('impact',impact)]:
   raw,audit=synth(key,stage,duration);audit.update(displayName=name,identity=theme);outputs[audit['file']]=raw;entries.append(audit)
 outputs['manifest.json']=(json.dumps({'generator':'make_boss_audio.py','originalProcedural':True,'uploaded':False,'cues':entries},indent=2)+'\n').encode()
 outputs['README.md']=README.encode()
 if args.check:
  for name,data in outputs.items():assert (ROOT/name).read_bytes()==data,'Non-deterministic or modified asset: '+name
 else:
  ROOT.mkdir(parents=True,exist_ok=True)
  for name,data in outputs.items():(ROOT/name).write_bytes(data)
 print(('CHECK PASS' if args.check else 'BUILT')+': 10 original WAVs; peak <= .46, |DC| < .00001, silent endpoints; no upload')
if __name__=='__main__':main()
