"""Actual landmark loader with deferred mock preloads; no Roblox asset evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
setup='''
local function event()
 local e={links={}};function e:Connect(fn)local c={fn=fn,connected=true};function c:Disconnect()self.connected=false end;table.insert(self.links,c);return c end
 function e:Fire(...)for _,c in self.links do if c.connected then c.fn(...) end end end;return e
end
local added,removed=event(),event();local script={Destroying=event()}
local queue={};local task={spawn=function(fn)table.insert(queue,fn)end}
local Enum={AssetFetchStatus={Success='ok'}}
local collection={GetInstanceAddedSignal=function()return added end,GetInstanceRemovedSignal=function()return removed end,GetTagged=function()return {}end}
local loads=0;local preloadHook
local content={PreloadAsync=function(_,meshes,callback)loads+=1;if preloadHook then preloadHook(callback) else callback('mesh','ok') end end}
local game={GetService=function(_,name)return name=='CollectionService' and collection or content end}
local workspace={}
local function model()
 local mesh={MeshId='mesh',TextureID='',IsA=function(_,kind)return kind=='BasePart' or kind=='MeshPart' end}
 local fallback={IsA=function(_,kind)return kind=='BasePart' end}
 local m={views={DetailedVisual={GetDescendants=function()return {mesh}end},FallbackVisual={GetDescendants=function()return {fallback}end}}}
 function m:FindFirstChild(name)return self.views[name]end
 function m:IsDescendantOf()return true end
 function m:SetAttribute(_,value)self.status=value end
 return m,mesh,fallback
end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local first,mesh,fallback=model();added:Fire(first)
check(#queue==1 and mesh.LocalTransparencyModifier==1 and fallback.LocalTransparencyModifier==0,'Pending asset hid fallback')
queue[1]();check(first.status=='Detailed' and fallback.LocalTransparencyModifier==1 and mesh.LocalTransparencyModifier==0,'Successful mock load did not swap visuals')
local failed,failedMesh,failedFallback=model();preloadHook=function(callback)callback('mesh','failed')end
added:Fire(failed);queue[#queue]()
check(failed.status=='Fallback' and failedFallback.LocalTransparencyModifier==0 and failedMesh.LocalTransparencyModifier==1,'Failed asset hid fallback')
local crashed,crashedMesh,crashedFallback=model();preloadHook=function()error('mock asset failure')end
added:Fire(crashed);queue[#queue]()
check(crashed.status=='Fallback' and crashedFallback.LocalTransparencyModifier==0,'Load exception hid fallback')
local streamed,streamMesh,streamFallback=model()
preloadHook=function(callback)coroutine.yield();callback('mesh','ok')end
added:Fire(streamed);local old=coroutine.create(queue[#queue]);assert(coroutine.resume(old))
removed:Fire(streamed);added:Fire(streamed)
assert(coroutine.resume(old))
check(streamFallback.LocalTransparencyModifier==0 and streamMesh.LocalTransparencyModifier==1,'Old in-flight result changed re-entered model')
preloadHook=nil;queue[#queue]()
check(streamed.status=='Detailed' and streamFallback.LocalTransparencyModifier==1,'Fresh streaming load failed')
local second,lateMesh,lateFallback=model();added:Fire(second)
local deferred=queue[#queue];local queued=#queue;local loadsBefore=loads
script.Destroying:Fire()
check(first.status=='Fallback' and fallback.LocalTransparencyModifier==0 and mesh.LocalTransparencyModifier==1,'Teardown did not restore authored fallback')
deferred()
check(loads==loadsBefore,'Queued load started after teardown')
check(second.status=='Fallback' and lateFallback.LocalTransparencyModifier==0 and lateMesh.LocalTransparencyModifier==1,'Late preload changed visuals after teardown')
check(not added.links[1].connected and not removed.links[1].connected,'Teardown retained collection listeners')
added:Fire(model());apply(model())
check(#queue==queued,'Late registration restarted asset load')
print('PASS '..checks..' actual landmark lifecycle checks with mocked asset loading')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+(root/'src/StarterPlayer/StarterPlayerScripts/LandmarkVisuals.client.luau').read_text()+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
