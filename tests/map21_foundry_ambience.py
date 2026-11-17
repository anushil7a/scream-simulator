"""Actual standalone client script under mocked Roblox services; no listening claim."""
from pathlib import Path
import os,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'prototypes/map10-v21/FoundryAmbience.client.luau').read_text()
pre=r'''
local checks=0
local function check(v,m)assert(v,m);checks+=1 end
local function event()
 local e={callbacks={}}
 function e:Connect(f)local c={active=true};function c:Disconnect()self.active=false end;table.insert(self.callbacks,{f=f,c=c});return c end
 function e:Fire(...)for _,x in ipairs(self.callbacks)do if x.c.active then x.f(...) end end end
 return e
end
local function scenario(studio,place,loaded)
 local made={};local loads=0
 local run={Heartbeat=event(),IsStudio=function()return studio end}
 local anchorMT={__sub=function(a,b)return {Magnitude=math.abs(a.x-b.x)}end}
 local function vector(x)return setmetatable({x=x},anchorMT)end
 local world={tag="Map10V21FoundryReview",CurrentCamera={CFrame={Position=vector(0)}}}
 function world:GetAttribute()return self.tag end
 local anchors={}
 for _,kind in ipairs({"Dock","Lighthouse"})do
  local a={Position=vector(0),alive=true};function a:GetAttribute()return kind end
  function a:IsA(t)return t=="BasePart" end;function a:IsDescendantOf()return self.alive end
  table.insert(anchors,a)
 end
 local player={Character={FindFirstChildOfClass=function()return {Health=100} end},FindFirstChildOfClass=function()return {}end}
 local services={RunService=run,Players={LocalPlayer=player},CollectionService={GetTagged=function()return anchors end},ContentProvider={PreloadAsync=function(_,paths,cb)loads+=1;cb(paths[1],loaded and 1 or 0)end}}
 local game={GameId=0,PlaceId=place,GetService=function(_,n)return services[n]end}
 local workspace=world;local script={Destroying=event()};local task={wait=function()end}
 local Enum={AssetFetchStatus={Success=1},RollOffMode={InverseTapered=1}}
 local UDim2={fromOffset=function()end,new=function()end};local Color3={fromRGB=function()end}
 local Instance={new=function(kind)
  local o={ClassName=kind,Activated=event(),plays=0,stops=0}
  function o:Play()self.plays+=1 end;function o:Stop()self.stops+=1 end;function o:Destroy()self.destroyed=true end
  table.insert(made,o);return o
 end}
 local function execute()
'''
post=r'''
 end
 execute()
 return {made=made,run=run,world=world,script=script,loads=loads,player=player,anchors=anchors}
end
local live=scenario(false,0,true);check(#live.made==0 and live.loads==0,"non Studio enabled")
local published=scenario(true,123,true);check(#published.made==0,"published place enabled")
local failed=scenario(true,0,false);check(#failed.made==0 and failed.loads==2,"failed assets must stay silent")
local s=scenario(true,0,true)
local function tick(n)for _=1,n do s.run.Heartbeat:Fire(.25)end end
tick(12)
local sounds={};local button
for _,o in ipairs(s.made)do if o.ClassName=="Sound"then table.insert(sounds,o)elseif o.ClassName=="TextButton"then button=o end end
check(#sounds==2 and s.loads==2,"bounded sources and loads")
for _,sound in ipairs(sounds)do check(sound.plays==1 and sound.Volume==.025 and not sound.Looped,"quiet one shot")end
button.Activated:Fire();tick(80)
for _,sound in ipairs(sounds)do check(sound.plays==1 and sound.stops>0,"mute must stop and suppress")end
button.Activated:Fire();s.world.CurrentCamera.CFrame.Position=setmetatable({x=1000},getmetatable(s.world.CurrentCamera.CFrame.Position));tick(80)
for _,sound in ipairs(sounds)do check(sound.plays==1,"distance gating")end
s.script.Destroying:Fire();tick(10)
for _,sound in ipairs(sounds)do check(sound.destroyed and sound.plays==1,"terminal cleanup")end
local before=#s.made;tick(20);check(#s.made==before,"post destruction allocation")
local streamed=scenario(true,0,true)
local later=streamed.anchors[2];streamed.anchors[2]=nil
streamed.run.Heartbeat:Fire(.25)
local function activeSounds(t)local n=0;for _,v in ipairs(t.made)do if v.ClassName=="Sound" and not v.destroyed then n+=1 end end;return n end
check(activeSounds(streamed)==1,"initial partial stream")
streamed.anchors[2]=later;streamed.run.Heartbeat:Fire(1)
check(activeSounds(streamed)==2,"late second anchor discovered")
local replacement=table.clone(later);later.alive=false;streamed.anchors[2]=replacement;replacement.alive=true
streamed.run.Heartbeat:Fire(1)
check(activeSounds(streamed)==2,"replacement keeps bounded voices")
for _,v in ipairs(streamed.made)do if v.ClassName=="Sound" and v.Parent==later then check(v.destroyed and v.stops>0,"old streamed source released")end end
streamed.anchors[2]=nil;streamed.run.Heartbeat:Fire(1)
check(activeSounds(streamed)==1,"tag removal releases sound")
streamed.script.Destroying:Fire();check(activeSounds(streamed)==0,"streamed lifecycle cleanup")
print("Foundry ambience: "..checks.." mocked checks passed")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:
 f.write(pre+source+post);name=f.name
try:subprocess.run([os.environ.get('LUAU') or shutil.which('luau') or '/tmp/map21-bin/luau',name],check=True)
finally:Path(name).unlink()
