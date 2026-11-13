"""Whole Client startup with synchronous module doubles; no native scheduling/input claim."""
from pathlib import Path
import subprocess,tempfile,argparse,re
R=Path(__file__).resolve().parents[1]
P='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
BASE='76ded0b'
EXPECTED_COMMON = [
 'wait:PlayerScripts/CityMap','require:CityMap','wait:ReplicatedStorage/Shared','wait:Shared/Config','require:Config',
 'wait:Shared/FirstBeamGuide','require:FirstBeamGuide','wait:Shared/InteractionRules','require:InteractionRules',
 'wait:PlayerScripts/Microphone','require:Microphone','wait:PlayerScripts/AttackAudio','require:AttackAudio','require:AttackAudioConfig',
 'wait:PlayerScripts/GameplayAudio','require:GameplayAudio','require:GameplayAudioConfig','wait:PlayerScripts/ShopUI','require:ShopUI',
 'wait:PlayerScripts/ScreamEffects','require:ScreamEffects','wait:ReplicatedStorage/ScreamRemotes','wait:ScreamRemotes/Action','wait:Player/PlayerGui',
 'wait:PlayerScripts/BeamScreenFeedback','require:BeamScreenFeedback','wait:PlayerScripts/NotificationQueue','require:NotificationQueue',
 'wait:PlayerScripts/NoticeLayout','require:NoticeLayout','wait:PlayerScripts/NoticeView','require:NoticeView']
EXPECTED_AUTO = ['wait:Shared/SustainedAttack','require:SustainedAttack','wait:Shared/VoiceActivation','require:VoiceActivation','wait:PlayerScripts/SustainedControls','require:SustainedControls']
EXPECTED_TAIL = ['wait:PlayerScripts/HitFeedback','require:HitFeedback','wait:PlayerScripts/BeamVisuals','require:BeamVisuals']
SETUP=r'''
local RealControls=require("../src/StarterPlayer/StarterPlayerScripts/SustainedControls")
local variant=VARIANT
local warnings=0;local function warn(message)assert(message=="ScreamSimulator Client cleanup failed");warnings+=1 end
local singletonClears={};local cleanupOrder={};local renders=0;local jobs={};local terminalShopClears=0
local automatic=AUTO
local expectFixed=FIXED
local pauseAt=PAUSE
local boundaries,signals,objects,owned,commands={},{},{},{},{}
local function boundary(name)
 table.insert(boundaries,name)
 if #boundaries==pauseAt then coroutine.yield(name) end
end
local function signal(name)
 local s={name=name,connections={}}
 function s:Connect(fn)local c={Connected=true,fn=fn};function c:Disconnect()self.Connected=false end;table.insert(self.connections,c);return c end
 function s:Wait()coroutine.yield()end
 function s:Fire(...) local copy=table.clone(self.connections);for _,c in ipairs(copy)do if c.Connected then c.fn(...)end end end
 function s:Count()local n=0;for _,c in ipairs(self.connections)do if c.Connected then n+=1 end end;return n end
 table.insert(signals,s);return s
end
local methods={}
local mt={__index=function(t,k)
 if methods[k] then return methods[k] end
 if k=="Parent" or k=="dead" then return nil end
 if k=='Destroying' or k=='AncestryChanged' or k=='Activated' or k=='InputBegan' or k=='InputEnded' or k=='OnClientEvent' or k=='CharacterAdded' or k=='CharacterRemoving' or k=='PlayerRemoving' or k=='Heartbeat' or k=='RenderStepped' or k=='JumpRequest' or k=='WindowFocusReleased' or k=='WindowFocused' or k=='MenuOpened' then local s=signal(t.Name..'.'..k);rawset(t,k,s);return s end
 for _,o in ipairs(objects)do if rawget(o,"Parent")==t and rawget(o,"Name")==k then return o end end
 return nil
end}
local function object(name,parent)
 local o=setmetatable({Name=name,Parent=parent,Visible=true,ZIndex=1,attrs={},AbsoluteSize={X=640,Y=360},AbsolutePosition={X=0,Y=0}},mt);table.insert(objects,o);return o
end
function methods:IsDescendantOf(root)local n=self;while n do if n==root then return true end;n=n.Parent end;return false end
function methods:GetChildren()local a={};for _,o in ipairs(objects)do if o.Parent==self then table.insert(a,o)end end;return a end
function methods:GetDescendants()local a={};for _,o in ipairs(objects)do if o~=self and o:IsDescendantOf(self)then table.insert(a,o)end end;return a end
function methods:Destroy()if self.dead then return end;self.dead=true;self.Destroying:Fire();for _,o in ipairs(self:GetChildren())do o:Destroy()end;for _,v in pairs(self)do if type(v)=='table' and v.connections then for _,c in ipairs(v.connections)do c:Disconnect()end end end;self.Parent=nil end
function methods:JSONEncode()return 'fixture' end
function methods:GetTextSize()return {Y=30}end
function methods:IsStudio()return true end
function methods:IsA(c)return c==self.ClassName or c=='GuiObject' end
function methods:WaitForChild(n)boundary('wait:'..self.Name..'/'..n);assert(self[n],'Missing mock child '..n);return self[n] end
function methods:FindFirstChild(n)return self[n] end
function methods:GetAttribute(n)return self.attrs[n]end
function methods:GetPropertyChangedSignal(n)local k='property:'..n;if not rawget(self,k)then rawset(self,k,signal(self.Name..'.'..k))end;return self[k]end
methods.GetAttributeChangedSignal=methods.GetPropertyChangedSignal
function methods:FireServer(verb,...)table.insert(commands,verb)end
local game=object('game');local workspace=object('Workspace',game)
workspace.CurrentCamera=object('Camera',workspace);workspace.CurrentCamera.ViewportSize={X=640,Y=360}
function workspace:GetServerTimeNow()return 100 end
local services={};function game:GetService(n)assert(services[n],'Missing service '..n);return services[n] end
for _,n in ipairs({'Players','ReplicatedStorage','UserInputService','RunService','TweenService','Debris','TextService','GuiService','HttpService','CollectionService'})do services[n]=object(n,game)end
local player=object('Player',services.Players);services.Players.LocalPlayer=player
player.CameraMode='original';player.CameraMinZoomDistance=.5;player.CameraMaxZoomDistance=12
player.PlayerGui=object('PlayerGui',player);player.Character=nil
services.GuiService.TouchControlsEnabled=true;services.GuiService.ReducedMotionEnabled=false
local scriptParent=object('PlayerScripts',player);local script=object('Client',scriptParent)
local shared=object('Shared',services.ReplicatedStorage);services.ReplicatedStorage.Shared=shared
local remotes=object('ScreamRemotes',services.ReplicatedStorage);services.ReplicatedStorage.ScreamRemotes=remotes;remotes.attrs.AutomaticVoice=automatic
for _,n in ipairs({'Action','State','Effect'})do remotes[n]=object(n,remotes)end
local function enum(t)return setmetatable(t or {},{__index=function(self,k)local v=enum({Name=k});rawset(self,k,v);return v end})end
local Enum=enum()
local Vector2={new=function(x,y)return {X=x,Y=y}end};Vector2.zero=Vector2.new(0,0)
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local UDim={new=function(s,o)return {Scale=s or 0,Offset=o or 0}end}
local UDim2={new=function(a,b,c,d)return {X=UDim.new(a,b),Y=UDim.new(c,d)}end}
UDim2.fromOffset=function(x,y)return UDim2.new(0,x,0,y)end;UDim2.fromScale=function(x,y)return UDim2.new(x,0,y,0)end
local Color3={new=function(...)return {}end,fromRGB=function(...)return {}end}
local ColorSequence={new=function(...)return {}end};local NumberSequence={new=function(...)return {}end}
local Instance={new=function(class)local o=object(class);o.ClassName=class;if class=='ScreenGui' and variant=='late-gui' then script.Destroying:Fire()end;return o end}
local task={spawn=function(fn)table.insert(jobs,fn)end,defer=function()error('Unexpected startup task.defer')end}
local modules={}
local function resource(name)
 local o={name=name,destroyed=0,ready=false,power=0,gate={OnPower=.5},sequence=0}
 function o:Destroy()self.destroyed+=1;table.insert(cleanupOrder,name);if variant=="cleanup-error" and name=="Microphone" then error("fixture cleanup error")end end
 function o:Clear()end
 function o:Cancel()end
 function o:Pulse()end
 if name~='NotificationQueue' and name~='HitFeedback' and name~='VoiceActivation' then table.insert(owned,o)end;if variant=="late-"..name then script.Destroying:Fire()end;return o
end
for _,n in ipairs({'CityMap','Config','FirstBeamGuide','InteractionRules','Microphone','AttackAudio','AttackAudioConfig','GameplayAudio','GameplayAudioConfig','ShopUI','ScreamEffects','BeamScreenFeedback','NotificationQueue','NoticeLayout','NoticeView','SustainedAttack','VoiceActivation','SustainedControls','HitFeedback','BeamVisuals','SustainedBeams','LockOn','TrainingRules'})do
 local node=object(n,shared);shared[n]=node;scriptParent[n]=node
 modules[n]={new=function(...)return resource(n)end,Clear=function()singletonClears[n]=(singletonClears[n] or 0)+1;table.insert(cleanupOrder,n)end}
end
modules.Config={MaxLevel=100,MicroSpeakerPrice=1500,MovementPassId=0,XPToNext=function()return 100 end,Auras={Gold={}}}
modules.TrainingRules={Tiers={{id='rookie',x=0,z=0}},Radius=32}
modules.CityMap.create=function()return {}end
modules.Config.GetSound=function()return {effect='fixture',level=1}end
modules.AttackAudioConfig.Range=100
modules.ShopUI.Render=function()renders+=1 end;modules.ShopUI.ColorMixer=function()renders+=1 end
modules.ScreamEffects.Render=function()renders+=1 end
modules.BeamVisuals.Create=function()renders+=1;return {}end
modules.SustainedBeams.new=function(create)
 local o=resource('SustainedBeams');o.Update=function()create()end;return o
end
modules.SustainedControls.new=function(gate,send,getAim,changed)
 local o=RealControls.new(gate,send,getAim,changed);o.name='SustainedControls';o.destroyCount=0
 local destroy=o.Destroy
 o.Destroy=function(self)self.destroyCount+=1;destroy(self)end
 table.insert(owned,o)
 if variant=='active-stop' or variant=='late-SustainedControls' then o.attack={sequence=7};o.sequence=7 end
 if variant=='late-SustainedControls' then script.Destroying:Fire()end
 return o
end
local function require(node)boundary('require:'..node.Name);assert(modules[node.Name]);return modules[node.Name]end
local function assertRetired()
 for _,o in ipairs(owned)do assert((o.destroyCount or o.destroyed)==1,'Owned resource not retired exactly once: '..o.name..' '..tostring(o.destroyCount or o.destroyed))end
 for _,o in ipairs(objects)do if o.ClassName=='ScreenGui' then assert(o.dead and not o.Parent,'GUI not retired')end end
 for _,sig in ipairs(signals)do if not string.find(sig.name,'Client.',1,true)then assert(sig:Count()==0,'Connection survived: '..sig.name)end end
 for _,n in ipairs({'ShopUI','ScreamEffects','BeamVisuals'})do local expected=((variant=='used-shop' or variant=='used-style' or variant=='used-shop-switch') and n=='ShopUI') or (variant=='used-effects' and n=='ScreamEffects') or (variant=='used-beams' and n=='BeamVisuals');assert((singletonClears[n] or 0)==(expected and (n=='ShopUI' and terminalShopClears+1 or 1) or 0),'Singleton cleanup ownership wrong: '..n)end
 if variant=='replacement' then assert(player.CameraMode=='replacement' and player.CameraMinZoomDistance==9 and player.CameraMaxZoomDistance==25,'Replacement camera overwritten')else assert(player.CameraMode=='original' and player.CameraMinZoomDistance==.5 and player.CameraMaxZoomDistance==12,'Camera not restored')end
 assert(services.GuiService.TouchControlsEnabled==(variant~='replacement' and variant~='touch-replacement'),'Touch control replacement/restoration incorrect')
end
local co=coroutine.create(function()
'''
TAIL=r'''
end)
local ok,err=coroutine.resume(co);assert(ok,err)
if pauseAt>0 then
 assert(coroutine.status(co)=='suspended','Boundary not reached')
 local mode=INVALIDATE
 if mode=='destroy' then script.Destroying:Fire()
 elseif mode=='unparent' then script.Parent=nil
 elseif mode=='ancestor' then scriptParent.Parent=nil
 elseif mode=='reparent' then local replacement=object('Replacement',player);scriptParent.Parent=replacement end
 local beforeObjects,beforeResources,beforeCommands=#objects,#owned,#commands
 ok,err=coroutine.resume(co);if expectFixed or mode=="reparent" then assert(ok,err)elseif not ok then print("BASELINE_ERROR "..tostring(err))end
 if expectFixed and mode~='reparent' then
  assert(#objects==beforeObjects and #owned==beforeResources,'Post-terminal construction')
  assert(#commands==beforeCommands,'Post-terminal command')
  assertRetired()
 end
 print('OBS '..tostring(automatic)..' '..pauseAt..' '..mode..' '..(#objects-beforeObjects)..' '..(#owned-beforeResources)..' '..(#commands-beforeCommands)..' '..tostring(player.CameraMode=='original'))
end
assert(coroutine.status(co)=='dead','Unexpected second suspension')
for i,n in ipairs(boundaries)do print('BOUNDARY '..i..' '..n)end
local frames=services.RunService.RenderStepped:Count()
local sync=0;for _,verb in ipairs(commands)do if verb=='Sync'then sync+=1 end end
if (pauseAt==0 and not string.find(variant,'late-',1,true)) or INVALIDATE=='reparent' then
 assert(frames==1 and sync==1,'Normal startup did not reach EOF exactly once')
 if variant=='used-shop' or variant=='used-style' or variant=='used-shop-switch' then
  local modal;for _,o in ipairs(objects)do if o.Name=='Menu' then modal=o end end
  assert(modal);modal.Visible=true
  modal[variant=='used-style' and 'Style' or 'Shop'].Activated:Fire()
  assert(renders==1,'Actual registered tab did not use Shop module')
  if variant=='used-shop-switch' then modal.Style.Activated:Fire();assert(renders==2 and singletonClears.ShopUI==1,'Ordinary render Clear changed')end
  terminalShopClears=singletonClears.ShopUI or 0
 end
 if variant=='used-effects' or variant=='used-beams' then
  local pos=setmetatable({},{__sub=function()return {Magnitude=0}end})
  player.Character=object('Character',player);player.Character.HumanoidRootPart=object('HumanoidRootPart',player.Character);player.Character.HumanoidRootPart.Position=pos
  services.Players.GetPlayerByUserId=function()return player end
  remotes.Effect.OnClientEvent:Fire(variant=='used-effects' and 'Beam' or 'SustainedBeam',pos,1,'Gold',{},10,4,'style',1)
  assert(renders==1,'Actual registered effect did not use module')
 end
 if variant=='replacement' then player.CameraMode='replacement';player.CameraMinZoomDistance=9;player.CameraMaxZoomDistance=25;services.GuiService.TouchControlsEnabled=false end
 script.Destroying:Fire();if expectFixed then assertRetired();script.Destroying:Fire();assertRetired()end
 for _,fn in ipairs(jobs)do local thread=coroutine.create(fn);assert(coroutine.resume(thread));if coroutine.status(thread)=='suspended'then assert(coroutine.resume(thread))end end
elseif expectFixed then assert(frames==0 and sync==0,'Terminal startup reached Sync/frame');assertRetired()end
if expectFixed then
 if variant=='used-beams' then local manager,pool;for i,name in ipairs(cleanupOrder)do if name=='SustainedBeams'then manager=i elseif name=='BeamVisuals'then pool=i end end;assert(manager and pool and manager<pool,'Pool cleared before owned manager')end
 if variant=='cleanup-error' then assert(warnings==1,'Cleanup failure diagnostic missing')else assert(warnings==0,'Unexpected cleanup error')end
 if variant=='active-stop' or variant=='late-SustainedControls' then local stops=0;for _,verb in ipairs(commands)do if verb=='SustainedStop'then stops+=1 else assert(verb=='Sync','Unexpected attack command')end end;assert(stops==1,'Actual Controls Stop not exactly once')end
end
print('END frames='..frames..' sync='..sync..' objects='..#objects..' resources='..#owned)
'''
def run(source,automatic=True,pause=0,mode='destroy',fixed=False,variant='normal'):
 # Execute only the exact production touch-write statement inside Client lexical scope.
 # This does not run or simulate the rest of RenderStepped.
 if variant in ('touch-owned','touch-replacement'):
  line=next(line for line in source.splitlines() if 'lastTouchControls=showTouchControls;' in line)
  source+='\nlocal showTouchControls=false\n'+line+'\n'
  if variant=='touch-replacement':source+='showTouchControls=true\n'+line+'\nGuiService.TouchControlsEnabled=false\n'
 text=SETUP.replace('VARIANT',repr(variant)).replace('FIXED',str(fixed).lower()).replace('AUTO',str(automatic).lower()).replace('PAUSE',str(pause))+source+TAIL.replace('INVALIDATE',repr(mode))
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(text);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=15)
 finally:path.unlink()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--baseline',action='store_true');a.add_argument('--negative-controls',action='store_true');args=a.parse_args()
 source=subprocess.check_output(['git','show',BASE+':'+P],cwd=R).decode() if args.baseline else (R/P).read_text()
 total=0
 for auto in [False,True]:
  r=run(source,auto,fixed=not args.baseline);assert r.returncode==0,r.stdout+r.stderr
  boundaries=re.findall(r'^BOUNDARY (\d+) (.+)$',r.stdout,re.M)
  expected=([name for name in EXPECTED_COMMON if args.baseline or name not in ('wait:Shared/FirstBeamGuide','require:FirstBeamGuide')])+([] if args.baseline else ['wait:PlayerScripts/LockOn','require:LockOn','wait:Shared/TrainingRules','require:TrainingRules'])+(EXPECTED_AUTO if auto else [])+EXPECTED_TAIL+(['wait:PlayerScripts/SustainedBeams','require:SustainedBeams'] if auto else [])
  assert [name for _,name in boundaries]==expected,'Startup dependency boundary coverage changed'
  print(('automatic' if auto else 'legacy')+' boundaries='+str(len(boundaries)))
  for i,name in boundaries:
   for mode in ['destroy','unparent','ancestor','reparent']:
    result=run(source,auto,int(i),mode,fixed=not args.baseline)
    assert result.returncode==0,f'{auto} {name} {mode}\n'+result.stdout+result.stderr
    if args.baseline and mode!='reparent':
     match=re.search(r'OBS \S+ \d+ \S+ (\d+) (\d+) (\d+) (\S+)',result.stdout)
     assert match and (int(match[1])+int(match[2])+int(match[3])>0 or match[4]=='false' or 'BASELINE_ERROR' in result.stdout),'Baseline did not reproduce continuation'
    total+=1
 print(f'PASS {total} whole-script boundary scenarios; '+('historical continuation reproduced' if args.baseline else 'terminal cleanup and in-DataModel reparent controls'))

 if not args.baseline:
  for variant in ['touch-owned','touch-replacement','used-shop','used-style','used-shop-switch','used-effects','used-beams','active-stop','cleanup-error','replacement','late-gui','late-Microphone','late-AttackAudio','late-GameplayAudio','late-BeamScreenFeedback','late-NoticeView','late-SustainedControls','late-SustainedBeams','late-LockOn']:
   r=run(source,True,fixed=True,variant=variant);assert r.returncode==0,variant+'\n'+r.stdout+r.stderr
  print('PASS 19 actual ownership/late-constructor/Controls cancellation scenarios')
  if args.negative_controls:
   mutations=[('table.insert(clientConnections,script.Destroying:Connect(retireClient))','',1,'destroy','normal'),('if not clientDestroyed and not script:IsDescendantOf(game) then retireClient() end','',1,'ancestor','normal'),('if clientDestroyed then attemptClientCleanup(cleanup) else table.insert(clientCleanups,cleanup) end','if not clientDestroyed then table.insert(clientCleanups,cleanup) end',0,'destroy','late-Microphone'),('if shopUsed then ShopUI.Clear() end','ShopUI.Clear()',0,'destroy','normal'),('if screamEffectsUsed then ScreamEffects.Clear() end','ScreamEffects.Clear()',0,'destroy','normal'),('if beamVisualsUsed then BeamVisuals.Clear() end','BeamVisuals.Clear()',0,'destroy','normal')]
   mutations += [('screamEffectsUsed=true;ScreamEffects.Render(', 'ScreamEffects.Render(',0,'destroy','used-effects'),('if verb=="SustainedStop" or not clientDestroyed then','if not clientDestroyed then',0,'destroy','active-stop'),('local ok=pcall(callback)','callback();local ok=true',0,'destroy','cleanup-error')]
   mutations += [('ownClient(function() modal.Visible=false;renderedMenuKey=nil;renderRevision+=1 end)','ownClient(function() closeMenu() end)',0,'destroy','used-shop-switch')]
   restore='if lastTouchControls~=nil and GuiService.TouchControlsEnabled==lastTouchControls then GuiService.TouchControlsEnabled=originalTouchControls end'
   mutations += [(restore,'',0,'destroy','touch-owned'),(restore,'GuiService.TouchControlsEnabled=originalTouchControls',0,'destroy','touch-replacement')]
   for old,new,pause,mode,variant in mutations:
    assert source.count(old)==1,old
    r=run(source.replace(old,new),True,pause,mode,True,variant)
    assert r.returncode and any(x in r.stderr for x in ['Post-terminal','Owned resource not retired','Singleton cleanup ownership wrong','Actual Controls Stop not exactly once','fixture cleanup error','Touch control replacement/restoration incorrect']),r.stdout+r.stderr
   print('PASS 12 ownership/startup negative controls')
