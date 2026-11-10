"""Actual gameplay audio adapter with mocked Roblox instances, not real playback."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/GameplayAudio.luau').read_text()
setup='''local RealMix=require("../src/StarterPlayer/StarterPlayerScripts/CueAudioMix")
local original=require("../src/ReplicatedStorage/Shared/GameplayAudioConfig")
local settings=table.clone(original)
settings.Asset=function(kind)return settings.Cues[kind] and "rbxassetid://123" end
local nodes={}
local Instance={new=function(class)
 local node={class=class,plays=0,stops=0,destroys=0}
 function node:Play()
  self.plays+=1;self.playing=true;self.volumeAtPlay=self.Volume;self.totalAtPlay=0
  for _,other in ipairs(nodes)do if other.playing then self.totalAtPlay+=other.Volume end end
 end
 function node:Stop()self.stops+=1;self.playing=false end
 function node:Destroy()self.destroys+=1;self.Parent=nil end
 table.insert(nodes,node);return node
end}
local soundService={};local workspace={}
local jobs={};local waits=0;local attempts=0;local failAll=false;local duringLoad
local task={spawn=function(fn)table.insert(jobs,fn)end,wait=function()waits+=1 end}
local content={PreloadAsync=function(_,assets,callback)
 attempts+=1
 if duringLoad then local fn=duringLoad;duringLoad=nil;fn() end
 callback(assets[1],failAll and "Failure" or "Success")
end}
local function loadJobs()
 local pending=jobs;jobs={}
 for _,fn in ipairs(pending)do fn()end
end
local game={GetService=function(_,name)
 if name=="SoundService" then return soundService end
 if name=="ContentProvider" then return content end
 return {Shared={GameplayAudioConfig="settings"}}
end}
local script={Parent={WaitForChild=function()return "mix" end}}
local require=function(name)return name=="settings" and settings or RealMix end
local Enum={RollOffMode={InverseTapered="tapered"},AssetFetchStatus={Success="Success"}}
local Vector3={one={}}
local Audio=(function()
'''
checks='''
end)()
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local mixer=Audio.new()
check(#nodes==2 and nodes[1].class=="SoundGroup" and nodes[2].Parent==nodes[1],"Cue group/EQ missing")
check(nodes[1].Volume==settings.GroupVolume and nodes[2].MidGain<0,"Voice-friendly mix missing")
check(not mixer:Play("Hit",0) and #nodes==2,"Cold cue allocated before preload")
loadJobs();check(attempts==4,"Configured cues not preloaded once")
check(mixer:Play("Hit",0),"Nonspatial hit did not play")
local hit=nodes[3]
check(hit.Parent==soundService and hit.SoundGroup==nodes[1],"Hit used a world emitter")
check(hit.volumeAtPlay>0 and hit.volumeAtPlay<=settings.TotalVolume,"Short cue started silently pending a render frame")
mixer:Step(.1,.1)
check(hit.plays==1 and hit.volumeAtPlay>0,"Long frame restarted or erased cue onset")
check(hit.SoundId=="rbxassetid://123" and hit.plays==1 and not hit.Looped and hit.PlaybackSpeed==1 and hit.PlayOnRemove==false,"Cue playback defaults")
check(mixer:Play("Dodge",.1,42),"Dodge did not play")
local anchor,sound=nodes[4],nodes[5]
check(anchor.Position==42 and anchor.CanQuery==false and anchor.CanTouch==false and anchor.CanCollide==false and anchor.CastShadow==false,"Emitter altered geometry")
check(sound.Parent==anchor and sound.SoundGroup==nodes[1] and sound.RollOffMaxDistance==settings.Range,"Spatial cue unbounded/ungrouped")
check(sound.volumeAtPlay>0 and sound.totalAtPlay<=settings.TotalVolume+.000001,"New playback escaped gain budget before older cues were reduced")
mixer:Step(.12,.02);check(hit.plays==1 and sound.plays==1,"Gain updates restarted recordings")
mixer:SetContext(false,true)
check(hit.stops==1 and hit.destroys==1 and sound.stops==1 and anchor.destroys==1,"Suppression leaked cue nodes")
mixer:SetContext(false,false);mixer:Play("LevelUp",1);local reward=nodes[6]
mixer:SetEnabled(false)
check(reward.stops==1 and reward.destroys==1,"Mute retained reward")
mixer:Destroy();mixer:Destroy()
check(nodes[1].destroys==1,"Group cleanup was missing or repeated")
check(not mixer:Play("Hit",10),"Queued call revived adapter")
failAll=true;local failed=Audio.new();local before=attempts;local previousWaits=waits
loadJobs();check(attempts-before==12 and waits-previousWaits==8,"Failed preload retries were not bounded")
check(not failed:Play("Hit",10) and #failed.entries==0,"Failed asset allocated a sound")
failed:Destroy();failAll=false
local cancelled=Audio.new();before=attempts;cancelled:Destroy();loadJobs()
check(attempts==before,"Queued preload ran after teardown")
local interrupted=Audio.new();duringLoad=function()interrupted:Destroy()end;before=attempts;loadJobs()
check(attempts==before+1 and not interrupted:Play("Hit",10),"Late successful preload revived destroyed audio")
local muted=Audio.new();muted:SetEnabled(false);before=#nodes;loadJobs()
check(#nodes==before and not muted:Play("Hit",20),"Late preload played despite mute")
muted:SetEnabled(true);check(muted:Play("Hit",21),"Muted preload could not serve a fresh request")
muted:Destroy()
local suppressed=Audio.new();suppressed:SetContext(false,true);before=#nodes;loadJobs()
check(#nodes==before and not suppressed:Play("Hit",30),"Late preload played during calibration")
suppressed:SetContext(false,false);check(suppressed:Play("Hit",31),"Calibrated preload could not serve a fresh request")
suppressed:Destroy()
print("PASS "..checks.." actual gameplay audio adapter checks with mocked instances")
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.gameplay_audio_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
assert 'if hitFeedback:Accept(id,aura,os.clock()) then playGameplayCue("Hit") end' in client
assert 'gameplayAudio:ObserveLevel(nextData.level,nextData.testSession,os.clock())' in client
assert 'playGameplayCue("Dodge",pos)' in client and 'playGameplayCue("Break",pos)' in client
assert 'gameplayAudio:Clear()' in client and 'gameplayAudio:Destroy()' in client
assert 'gameplayAudioSettings.Range' in client
assert client.index('gameplayAudio:Step(os.clock(),dt)')<client.index('elapsed+=dt;if elapsed<.15')
print('PASS 6 client hookup source-contract checks; not native event execution')
