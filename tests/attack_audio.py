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
 local node={class=class,plays=0,stops=0}
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
check(not mixer:Pulse(1,0,10,true) and #nodes==2,"Unconfigured ID created a sound")
settings.LoopAssetId="rbxassetid://123" -- mock only; never uploaded or loaded
check(mixer:Pulse(1,0,10,true),"Configured sound not allocated")
local anchor,sound=nodes[3],nodes[4]
check(anchor.CanQuery==false and anchor.CanTouch==false and anchor.CanCollide==false,"Audio changed combat geometry")
check(sound.Volume==0 and sound.Looped and sound.PlayOnRemove==false and sound.plays==1,"Unsafe playback defaults")
check(sound.SoundGroup==nodes[1] and sound.RollOffMaxDistance==settings.Range,"Unbounded or ungrouped sound")
mixer:Pulse(1,.1,20,true);mixer:Step(.1,.1,false)
check(sound.plays==1 and anchor.Position==20 and sound.Volume>0,"Updates restarted sound")
mixer:SetEnabled(false)
check(anchor.destroyed and sound.stops==1 and mixer.count==0,"Mute left sound playing")
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
