"""Actual audio adapter and event gate with fake services; no native playback claim."""
from pathlib import Path
import ast,tempfile,subprocess
R=Path(__file__).resolve().parents[1]
tree=ast.parse((R/'tests/gameplay_audio.py').read_text())
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup.replace('GameplayAudioConfig','BossAudioConfig').replace('settings.Asset=function(kind)return settings.Cues[kind] and "rbxassetid://123" end','')
source=(R/'src/StarterPlayer/StarterPlayerScripts/BossAudio.luau').read_text()
checks=r'''
end)()
local n=0;local function check(v,m)assert(v,m);n+=1 end
local unique={};for k in pairs(settings.Cues)do unique[settings.Asset(k)]=true end
local count=0;for _ in pairs(unique)do count+=1 end
local a=Audio.new();check(not a:Play('metronome_tell_1',0,42),'Cold playback allocated')
loadJobs();check(attempts==count,'Preload not deduplicated')
for i,key in ipairs({'metronome_tell_1','golem_tell_1','ignis_tell_1','leviathan_tell_1'})do check(a:Play(key,1,42),'Theme not playable after success')end
check(not a:Play('conductor_tell_1',1,42),'Global concurrency cap escaped')
local gain=0;for _,e in ipairs(a.entries)do gain+=e.handle.sound.Volume end
check(gain<=settings.TotalVolume+.000001,'Aggregate budget escaped')
a:SetContext(true,false);a:Step(1,.1);gain=0;for _,e in ipairs(a.entries)do gain+=e.handle.sound.Volume end
check(gain<=settings.TotalVolume*settings.VoiceDuck+.000001,'Voice duck missing')
a:CancelTell('golem');check(#a.entries==3,'Canceled tell retained')
a:SetEnabled(false);check(#a.entries==0 and not a:Play('conductor_tell_1',2,42),'Mute did not stop/reject')
a:SetEnabled(true);a:SetContext(false,true);check(not a:Play('conductor_tell_1',2,42),'Calibration allowed playback')
a:SetContext(false,false);check(a:Play('conductor_impact_2',3,42),'Impact2 unavailable')
local h=a.entries[1].handle;check(not h.sound.Looped and h.sound.PlaybackSpeed==settings.Cues.conductor_impact_2.Speed,'Pattern pitch/one-shot changed')
check(not h.anchor.CanCollide and not h.anchor.CanTouch and not h.anchor.CanQuery,'Audio altered geometry')
a:Step(5,.1);check(#a.entries==0 and h.anchor.destroys==1,'Lifetime leaked')
a:SetContext(false,false)
for _,key in ipairs({'metronome_impact_1','golem_impact_1','ignis_impact_1','leviathan_impact_1'})do check(a:Play(key,6,42),'Impact fill failed')end
check(a:Play('conductor_tell_1',6,42) and #a.entries==4,'Warning did not replace decorative impact')
a:Destroy();a:Destroy();check(not a:Play('metronome_tell_1',8,42),'Destroyed adapter revived')
failAll=true;local failed=Audio.new();local before=attempts;loadJobs();check(attempts-before==count*3,'Failed preload unbounded')
check(not failed:Play('metronome_tell_1',9,42) and #failed.entries==0,'Missing asset made emitter')
failed:Destroy();failAll=false
local gone=Audio.new();before=attempts;gone:Destroy();loadJobs();check(attempts==before,'Queued work after teardown')
local muted=Audio.new();muted:SetEnabled(false);loadJobs();check(not muted:Play('metronome_tell_1',10,42),'Late load unmuted');muted:Destroy()
print('PASS '..n..' actual boss adapter bounded-loading/mix checks')
'''
def run(text):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(text);p=Path(f.name)
 try:subprocess.run(['luau',str(p)],cwd=R,check=True)
 finally:p.unlink()
run(setup+source+checks)
run(r'''
local Events=require('../src/StarterPlayer/StarterPlayerScripts/BossAudioEvents')
local n=0;local function check(v,m)assert(v,m);n+=1 end
local calls={};local cancels=0
local gate=Events.new(function(...)table.insert(calls,{...})end,function()cancels+=1 end)
local model={};local function step(serial,deadline,impact,at,state,now,allowed)gate:Step(model,'golem',serial,deadline,impact,at,state,now,{},allowed~=false)end
step(0,0,0,0,'Idle',0);check(#calls==0,'Initial playback')
step(1,0,0,0,'Idle',1);check(#calls==0,'Split serial burned or played early')
step(1,3,0,0,'Windup',1.05);check(#calls==1 and calls[1][2]=='tell','Split tell not retried')
step(1,3,0,0,'Windup',1.1);check(#calls==1,'Duplicate tell')
step(1,3,1,0,'Recovery',3);check(#calls==1,'Impact before timestamp')
step(1,3,1,3,'Recovery',3.05);check(#calls==2 and calls[2][2]=='impact','Split impact not retried')
step(1,3,1,3,'Recovery',3.1);check(#calls==2,'Duplicate impact')
step(2,6,1,3,'Windup',4,false);step(2,6,1,3,'Windup',4.1,true);check(#calls==2,'Mute/range replay')
step(2,6,2,5,'Recovery',6);check(#calls==2,'Stale impact played')
step(3,9,2,5,'Windup',7);check(#calls==3,'Next tell rejected');local before=cancels
step(3,9,2,5,'Idle',7.1);check(cancels>before,'Canceled attack tell retained')
model={};step(8,12,8,10,'Recovery',10);check(#calls==3,'Replacement replay')
gate:RemoveAbsent({});check(next(gate.seen)==nil,'Unstreamed boss retained');gate:Clear()
local played={};local g=Events.new(function(...)table.insert(played,{...})end,function()end)
local m={}
g:Step(m,'golem',0,0,0,0,'Idle',0,{},true)
g:Step(m,'golem',1,2,0,0,'Windup',1,{},true)
g:Step(m,'golem',1,2,1,2,'Recovery',2,{},true)
g:Step(m,'golem',2,5,1,2,'Windup',3,{},true)
g:Step(m,'golem',2,5,2,2,'Recovery',5,{},true)
check(#played==3,'Previous positive timestamp played/consumed new impact')
g:Step(m,'golem',2,5,2,5,'Recovery',5.05,{},true)
check(#played==4 and played[4][2]=='impact','New timestamp did not rescue pending impact')
g:Step(m,'golem',2,5,2,5,'Recovery',5.1,{},true);check(#played==4,'Retried impact duplicated')
print('PASS '..n..' actual boss event serial/split/stale/cancellation checks')
''')
service=(R/'src/ServerScriptService/BossService.luau').read_text()
assert 'phase(b,"Windup")' in service
listener=(R/'src/StarterPlayer/StarterPlayerScripts/BossAttackAudio.client.luau').read_text()
for key in ['BossAttackSerial','BossAttackAt','BossAttackImpactSerial','BossAttackImpactAt','BossAudioSuppressed','BossAudioEnabled']:assert key in listener
print('PASS exact production Windup phase and audio-only metadata/preferences contract')

client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=client.index('local function cueContext()');b=client.index('local function playGameplayCue(',a)
run(r'''
local attrs={};local writes=0;local p={SetAttribute=function(_,k,v)attrs[k]=v;writes+=1 end}
local oldSuppressed;local gameplayAudio={enabled=true,SetContext=function(_,voice,suppressed)oldSuppressed=suppressed end}
local mic={ready=false,power=0}
''' +client[a:b]+r'''
cueContext();assert(writes==3 and attrs.BossAudioEnabled and attrs.BossAudioVoiceActive and attrs.BossAudioSuppressed==false,'No-mic listener missing quiet cues')
assert(oldSuppressed==true,'Original four-cue not-ready policy changed')
cueContext();assert(writes==3,'Unchanged frame rewrote attributes')
mic.phase='quiet';cueContext();assert(attrs.BossAudioSuppressed and writes==4,'Calibration not silent')
mic.phase=nil;mic.ready=true;cueContext();assert(not attrs.BossAudioVoiceActive and not attrs.BossAudioSuppressed,'Ready quiet mix stale')
gameplayAudio.enabled=false;cueContext();assert(attrs.BossAudioEnabled==false,'Gameplay mute not forwarded')
print('PASS actual boss preference no-mic/calibration/mute/change-only attribute checks')
''')
