"""Actual Roblox audio adapter with mocked instances; no asset loading/listening."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'src/StarterPlayer/StarterPlayerScripts/AttackAudio.luau').read_text()
setup = '''
local RealMix=(function()
__MIX__
end)()
local settings=require("../src/ReplicatedStorage/Shared/AttackAudioConfig")
local nodes={}
local Instance={new=function(class)
 local node={class=class,plays=0,stops=0,IsLoaded=class=="Sound",IsPlaying=false}
 function node:Play()self.plays+=1;self.IsPlaying=true end
 function node:Stop()self.stops+=1;self.IsPlaying=false end
 function node:Destroy()self.destroyed=true;self.Parent=nil end
 table.insert(nodes,node);return node
end}
local soundService={};local workspace={}
local game={GetService=function(_,name)
 if name=="SoundService" then return soundService end
 return {Shared={AttackAudioConfig="settings"}}
end}
local script={Parent={WaitForChild=function()return "mix" end}}
local require=function(name)return name=="settings" and settings or RealMix end
local Enum={RollOffMode={InverseTapered="tapered"}}
local Vector3={one={}}
local Audio=(function()
'''
checks = '''
end)()
local checks=0;local function check(ok,message)assert(ok,message);checks+=1 end
local mixer=Audio.new()
check(#nodes==2 and nodes[1].class=="SoundGroup" and nodes[2].Parent==nodes[1],"Effects escaped their group")
check(nodes[1].Volume==settings.GroupVolume and nodes[2].MidGain<0 and nodes[2].HighGain<0,"Voice-space mix missing")
check(not mixer:Pulse(1,0,10,true,1) and #nodes==2,"Starter played an unassigned sound")
check(mixer:Pulse(1,0,10,true,10),"Configured tier not allocated")
local anchor,sound=nodes[3],nodes[4]
check(anchor.CanQuery==false and anchor.CanTouch==false and anchor.CanCollide==false,"Audio changed combat geometry")
check(sound.Volume==0 and not sound.Looped and sound.PlaybackSpeed==1 and sound.PlayOnRemove==false and sound.plays==0,"Sound started before its first mix update")
check(sound.SoundId=="rbxassetid://112589551277234","Wrong level-10 recording")
check(sound.SoundGroup==nodes[1] and sound.RollOffMaxDistance==settings.Range,"Unbounded or ungrouped sound")
mixer:Pulse(1,.1,20,true,100);mixer:Step(.1,.1,false)
check(sound.plays==1 and anchor.Position==20 and sound.Volume>0,"Updates restarted sound")
check(sound.SoundId=="rbxassetid://112589551277234","In-flight style change replaced the recording")
mixer:SetEnabled(false)
check(anchor.destroyed and sound.stops==1 and mixer.count==0,"Mute left sound playing")
mixer:SetEnabled(true);check(mixer:Pulse(2,1,10,false,100),"Level-100 sound did not start")
check(nodes[6].SoundId=="rbxassetid://79853512837585","Remote attacker tier used listener's style")
local pending=nodes[6];pending.IsLoaded=false
mixer:Step(1.05,.05,false)
check(pending.plays==0,"Unloaded sound was queued for playback")
mixer:Stop(2,1.06);pending.IsLoaded=true
mixer:Step(1.08,.03,false)
check(pending.plays==0,"A late load started after the beam stopped")
mixer:Step(1.23,.15,false)
check(mixer.count==0 and nodes[5].destroyed,"Cancelled pending sound leaked")
check(mixer:Pulse(3,2,10,false,100),"Next beam was rejected")
local delayed=nodes[8];delayed.IsLoaded=false
mixer:Step(2.05,.05,false);delayed.IsLoaded=true
mixer:Step(2.10,.05,false,true)
check(delayed.plays==0,"A sound started during calibration")
mixer:Step(2.11,.01,false)
local gain=delayed.Volume
check(delayed.plays==1 and gain>0,"Live beam failed to start when loaded")
mixer:Step(2.12,.01,false)
check(delayed.plays==1,"Live beam restarted on a later mix step")
mixer:Stop(3,2.12);mixer:Step(2.20,.08,false)
check(delayed.plays==1 and delayed.Volume>0 and delayed.Volume<gain,"A playing beam lost its normal fade")
mixer:Clear()
local start=#nodes
check(mixer:Pulse(4,3,10,false,10) and mixer:Pulse(5,3,10,false,20),"Concurrent beams rejected")
local audible,loading=nodes[start+2],nodes[start+4]
loading.IsLoaded=false
mixer:Step(3.13,.13,false)
check(audible.plays==1 and math.abs(audible.Volume-settings.TotalVolume)<1e-6 and loading.Volume==0,"Unloaded beam took a share of the mix")
loading.IsLoaded=true
mixer:Step(3.14,.01,false)
check(loading.plays==1 and math.abs(audible.Volume-settings.TotalVolume/2)<1e-6 and math.abs(audible.Volume+loading.Volume-settings.TotalVolume)<1e-6,"Newly loaded beam did not share the bounded mix")
check(mixer:Pulse(6,3.14,10,false,30),"Third beam rejected")
local canceled=nodes[start+6]
mixer:Stop(6,3.15)
mixer:Step(3.16,.02,false)
check(canceled.plays==0 and canceled.Volume==0 and math.abs(audible.Volume+loading.Volume-settings.TotalVolume)<1e-6,"Stopped unplayed beam took a share of the mix")
mixer:Step(3.17,.01,true)
check(audible.Volume+loading.Volume<=settings.LowVolume*mixer.duck+1e-6,"Loaded beams exceeded the voice-active ceiling")
audible.IsPlaying=false -- natural completion does not stop the beam pulse stream
check(mixer:Pulse(4,3.18,14,false,10) and mixer:Pulse(5,3.18,20,false,20),"Live casts lost their entries")
mixer:Step(3.18,.01,true)
check(audible.Volume==0 and math.abs(loading.Volume-settings.LowVolume*mixer.duck)<1e-6,"Completed beam still took a share of the mix")
mixer:Step(3.19,.01,false)
check(audible.plays==1 and not audible.IsPlaying and loading.plays==1,"Natural completion or mix recovery restarted a recording")
check(math.abs(loading.Volume-settings.TotalVolume*mixer.duck)<1e-6,"Remaining beam did not regain its normal budget")
mixer:Step(3.20,.01,false,true)
check(loading.Volume==0 and loading.IsPlaying,"Calibration did not mute current playback")
mixer:Clear()
local edgeStart=#nodes
check(not mixer:Pulse(11,4,71,false,10,71) and #nodes==edgeStart,"Distant first pulse allocated audio")
check(mixer:Pulse(11,4,69,false,10,69) and mixer:Pulse(12,4,6,false,20,6),"Nearby casts not admitted")
mixer:Step(4.13,.13,false)
local edge=mixer.entries[11].sound
local close=mixer.entries[12].sound.sound
check(edge.sound.plays==1 and close.plays==1,"Initial clips did not start")
check(mixer:Pulse(11,4.14,71,false,10,71),"Range exit lost the live clip")
mixer:Step(4.14,.01,false)
check(edge.anchor.Position==71 and edge.sound.Volume==0 and edge.sound.IsPlaying,"Distant clip was not silently advanced at its new position")
check(math.abs(close.Volume-settings.TotalVolume*mixer.duck)<1e-6,"Distant clip took a share of nearby gain")
check(mixer:Pulse(11,4.15,69,false,10,69),"Reentry rejected continuing clip")
mixer:Step(4.15,.01,false)
check(edge==mixer.entries[11].sound and edge.sound.plays==1 and edge.sound.Volume>0,"Range reentry restarted the recording")
mixer:Stop(11,4.16)
check(not mixer:Pulse(11,4.17,69,false,10,69),"Range reentry revived stopped audio")
mixer:Step(4.33,.16,false)
check(not mixer.entries[11] and edge.anchor.destroyed,"Stopped range-tracked audio did not release its handle")
mixer:Clear()
for id=21,24 do check(mixer:Pulse(id,5,20,false,10,20),"Base slot not admitted") end
check(not mixer:Pulse(25,5,10,false,20,10) and mixer.count==4,"All-nearby cap changed")
for id=21,24 do check(mixer:Pulse(id,5.05,id+60,false,10,id+60),"Distant existing handle lost") end
local evicted=mixer.entries[24].sound.anchor
check(not mixer:Pulse(25,5.06,20,false,1,20) and not evicted.destroyed and mixer.count==4,"Unassigned starter evicted a live handle")
check(mixer:Pulse(25,5.07,20,false,20,20) and mixer.count==4 and evicted.destroyed and not mixer.entries[24],"Nearby clip did not reclaim the farthest slot")
mixer:Step(5.13,.13,false)
check(mixer.entries[25].sound.sound.plays==1,"Reclaimed slot did not play")
mixer:Step(5.74,.25,false)
check(mixer.count==0,"Distant entries escaped normal timeout cleanup")
mixer:Destroy();check(nodes[1].destroyed,"Teardown leaked SoundGroup")
check(not mixer:Pulse(2,1,10,true),"Destroyed adapter recreated audio")
print("PASS "..checks.." actual attack audio adapter checks with mocked instances")
'''
mix = (root/'src/StarterPlayer/StarterPlayerScripts/BeamAudioMix.luau').read_text()
def run(mixer_source):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.attack_audio_', dir=root/'tests', delete=False) as f:
        path = Path(f.name)
        f.write(setup.replace('__MIX__', mixer_source) + source + checks)
    try:
        return subprocess.run(['luau', str(path)], cwd=root, capture_output=True, text=True)
    finally:
        path.unlink()

result = run(mix)
assert result.returncode == 0, result.stderr
print(result.stdout.strip())
if '--negative-controls' in sys.argv:
    for old, new, diagnostic in (
        ('  if distance and distance>self.settings.Range then return false end', '', 'Distant first pulse allocated audio'),
        ('(not entry.distance or entry.distance<=self.settings.Range) and ', '', 'Distant clip was not silently advanced'),
        (' or not self.canCreate(tier)', '', 'Unassigned starter evicted a live handle'),
    ):
        assert mix.count(old) == 1, old
        result = run(mix.replace(old, new))
        assert result.returncode and diagnostic in result.stderr, result.stderr
    print('PASS 3 audio range negative controls')
