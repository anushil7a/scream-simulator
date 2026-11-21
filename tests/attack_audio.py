"""Actual Roblox audio adapter with mocked instances; no asset loading/listening."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'src/StarterPlayer/StarterPlayerScripts/AttackAudio.luau').read_text()
setup = '''
local RealMix=require("../src/StarterPlayer/StarterPlayerScripts/BeamAudioMix")
local settings=require("../src/ReplicatedStorage/Shared/AttackAudioConfig")
local nodes={}
local Instance={new=function(class)
 local node={class=class,plays=0,stops=0,IsLoaded=class=="Sound"}
 function node:Play()self.plays+=1 end
 function node:Stop()self.stops+=1 end
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
mixer:Destroy();check(nodes[1].destroyed,"Teardown leaked SoundGroup")
check(not mixer:Pulse(2,1,10,true),"Destroyed adapter recreated audio")
print("PASS "..checks.." actual attack audio adapter checks with mocked instances")
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.attack_audio_', dir=root/'tests', delete=False) as f:
    path = Path(f.name)
    f.write(setup+source+checks)
try:
    subprocess.run(['luau', str(path)], cwd=root, check=True)
finally:
    path.unlink()
