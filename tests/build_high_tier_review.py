"""Build-only matched high-tier clarity comparison. No Studio/app/Play operations."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from review_baseline import contact_renderer

R=Path(__file__).resolve().parents[1];OUT=R/'build/high-tier-review';OUT.mkdir(parents=True,exist_ok=True)
BASE='b76c94fafd65be4cec85f1c5f2caa4355262e43b'
VP='src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
def sha(data):return hashlib.sha256(data).hexdigest()
def filehash(path):return sha(path.read_bytes())
sources={str(p.relative_to(R)).replace('\\','/'):filehash(p) for p in (R/'src').rglob('*.luau')}
before=contact_renderer()
(OUT/'BeforeVisuals.luau').write_bytes(before)
subprocess.run([sys.executable,str(R/'tests/build_ui_preview.py'),'1280','640'],cwd=R,check=True)
preview=(R/'build/StudioUIPreview.luau').read_text(encoding='utf8');prefix=preview[:preview.rindex('local report={}')]
assert prefix.count('local view=Vector2.new(1280,640)')==1
prefix=prefix.replace('local view=Vector2.new(1280,640)','local view=workspace.CurrentCamera.ViewportSize',1)
waiting='local playerGui=p:WaitForChild("PlayerGui");if not clientCheckpoint() then return end'
assert prefix.count(waiting)==1
prefix=prefix.replace(waiting,'local playerGui=p:WaitForChild("PlayerGui",12);assert(playerGui and playerGui:IsA("PlayerGui"),"Fixture PlayerGui unavailable after12seconds");if not clientCheckpoint() then return end',1)
assert 'local viewport=gui.AbsoluteSize' in prefix and 'modules.Profiles=' not in prefix and 'Bootstrap' not in prefix
prefix='assert(game:GetService("RunService"):IsStudio() and game.GameId==0 and game.PlaceId==0,"LOCAL HIGH-TIER REVIEW ONLY")\n'+prefix
(OUT/'Prefix.luau').write_text(prefix,encoding='utf8')
tail=r'''
;(function()
local Http=game:GetService("HttpService");local Collection=game:GetService("CollectionService")
local identity="__PREFIX_SHA__"
local world,control,root,character,camera,prior,rig,renderer,watchdog
local Before=require(game.ReplicatedStorage.BeforeVisuals);local After=modules.BeamVisuals
local function cleanup()
 Before.Clear();After.Clear();rig=nil
 if world then world:Destroy();world=nil end
 if control then control:Destroy();control=nil end
 if prior then
  if root.Parent==character then root.Anchored=prior.anchored;root.CFrame=prior.frame end
  if workspace.CurrentCamera==camera then camera.CFrame=prior.cameraFrame;camera.CameraSubject=prior.subject;camera.CameraType=prior.cameraType end
 end
 if watchdog and watchdog~=coroutine.running()then pcall(task.cancel,watchdog)end;watchdog=nil
end
ownClient(cleanup)
workspace:SetAttribute("HighTierReviewState","initializing")
local ok,err=xpcall(function()
 watchdog=task.delay(300,function()watchdog=nil;workspace:SetAttribute("HighTierReviewState","timed-out");retireClient()end)
 local deadline=os.clock()+12;local stable=0;local lastCamera,lastSize
 repeat
  assert(clientCheckpoint(),"Client stopped during readiness")
  character=p.Character;root=character and character:FindFirstChild("HumanoidRootPart")
  local h=character and character:FindFirstChildOfClass("Humanoid")
  camera=workspace.CurrentCamera;local size=camera and camera.ViewportSize
  if root and h and h.Health>0 and camera and size.X>=124 and size.Y>=44 and playerGui.Parent==p then
   stable=camera==lastCamera and size==lastSize and stable+1 or 1
  else stable=0 end
  lastCamera,lastSize=camera,size
  if stable>=3 then break end
  Run.RenderStepped:Wait()
 until os.clock()>=deadline
 assert(stable>=3 and clientCheckpoint() and p.Character==character and root.Parent==character and playerGui.Parent==p,"Avatar/camera/PlayerGui unavailable after12seconds")
 prior={frame=root.CFrame,anchored=root.Anchored,cameraFrame=camera.CFrame,cameraType=camera.CameraType,subject=camera.CameraSubject}
 root.Anchored=true
 world=Instance.new("Model");world.Name="HighTierReviewScene";world.Parent=workspace
 require(game.ReplicatedStorage.CompactCity).Build(world)
 local home=Vector3.new(-245,3,-15)
 root.CFrame=CFrame.new(home+Vector3.new(6,0,8))
 local dummy=Instance.new("Model");dummy.Name="HighTierReviewTarget";dummy.Parent=world
 local function part(name,size,pos,color)
  local f=Instance.new("Part");f.Name=name;f.Size=size;f.Position=pos;f.Color=color;f.Material=Enum.Material.SmoothPlastic;f.Anchored=true;f.CanCollide=false;f.CanQuery=false;f.CanTouch=false;f.CastShadow=false;f.Parent=dummy;return f
 end
 local torso=part("HumanoidRootPart",Vector3.new(2,2,1),home,Color3.fromRGB(36,55,66))
 part("Head",Vector3.new(1.5,1.5,1.5),home+Vector3.new(0,1.75,0),Color3.fromRGB(222,196,157))
 for _,side in ipairs({-1,1})do
  part("Arm"..side,Vector3.new(.7,2,.9),home+Vector3.new(side*1.4,0,0),Color3.fromRGB(43,66,79))
  part("Leg"..side,Vector3.new(.85,2,.85),home+Vector3.new(side*.55,-2,0),Color3.fromRGB(233,225,204))
 end
 local h=Instance.new("Humanoid");h.RequiresNeck=false;h.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None;h.Parent=dummy
 dummy.PrimaryPart=torso;dummy:SetAttribute("TrainingTier","rookie");dummy:SetAttribute("ResidentActive",true)
 Collection:AddTag(dummy,"CityResident");ownClient(function()Collection:RemoveTag(dummy,"CityResident")end)
 local backdrop=part("FixtureContrastBackdrop",Vector3.new(44,20,.6),home+Vector3.new(0,6,-13),Color3.fromRGB(239,224,190))
 local function rect(o)return {x=o.AbsolutePosition.X,y=o.AbsolutePosition.Y,w=o.AbsoluteSize.X,h=o.AbsoluteSize.Y}end
 local function settle()for _=1,3 do Run.RenderStepped:Wait();assert(clientCheckpoint() and p.Character==character and root.Parent==character,"Review/character replaced")end end
 local function tuple(v)return {v.X,v.Y,v.Z}end
 local function select(options)
  assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0 and clientCheckpoint(),"LOCAL HIGH-TIER REVIEW ONLY")
  assert(type(options)=="table","Options table required")
  if options.cleanup then
   workspace:SetAttribute("HighTierReviewState","cleaned");retireClient()
   return {cleaned=true,cameraType=tostring(camera.CameraType),rootAnchored=root.Parent and root.Anchored,gameId=game.GameId,placeId=game.PlaceId}
  end
  local mode,level,reduced,age,view=options.mode,options.level,options.reduced,options.age,options.view
  assert((mode=="Before" or mode=="After") and (level==1 or level==50 or level==70 or level==80 or level==90 or level==100) and type(reduced)=="boolean","Mode/level/reduced invalid")
  assert(age==0 or age==.06 or age==.16 or age==.29,"Age must be0/.06/.16/.29")
  assert(view=="front" or view=="oblique","View must befront/oblique")
  assert(options.backdrop==nil or options.backdrop=="bright" or options.backdrop=="dark","Backdrop invalid")
  assert(p.Character==character and root.Parent==character and playerGui.Parent==p and workspace.CurrentCamera==camera,"Owned avatar/GUI/camera replaced")
  Before.Clear();After.Clear();rig=nil
  sample.level=level;sample.xpNext=Config.XPToNext(level);sample.devAccess=false;sample.micReady=true;sample.voiceEligible=true;sample.settings.reducedShake=reduced;receiver(sample)
  fixtureTouch=false;gui.Size=UDim2.fromOffset(1280,640);gui.Position=UDim2.fromOffset(10,10)
  modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false;windowFocused=true;mic.power=0;mic.ready=true;sustainedControl:SetArmed(true)
  local position=home+(view=="front" and Vector3.new(0,6,26) or Vector3.new(12,6,24));local look=home+Vector3.new(0,1,0)
  camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(position,look)
  backdrop.Color=options.backdrop=="dark" and Color3.fromRGB(42,65,72) or Color3.fromRGB(239,224,190)
  settle();lockController:Clear();academy.lockLostUntil=0;toggleLock();settle()
  assert(lockController.target and lockController.target.model==dummy,"Native lock acquisition failed")
  renderer=mode=="Before" and Before or After;rig=renderer.Create();rig.born=99
  local width=Config.VoiceCombat.Stats(level,1,false).width
  renderer.Update(rig,home+Vector3.new(0,0,16),Vector3.new(0,0,-1),25,width,Config.Auras.Gold,level,reduced)
  assert(renderer.Contact(rig,torso.Position,100,1),"Contact setter rejected fixture target");renderer.Animate(rig,100+age,position,reduced,true,reduced)
  settle()
  local allocated,pooled=renderer.Budget();local words=lockMarker:FindFirstChild("LockText") or lockMarker
  local contacts=rig.contact and rig.contact.parts or {};local contactParts={}
  for _,f in ipairs(contacts)do table.insert(contactParts,{size=tuple(f.Size),position=tuple(f.Position),transparency=f.Transparency,material=f.Material.Name})end
  local row={identity=identity,gameId=game.GameId,placeId=game.PlaceId,mode=mode,level=level,reduced=reduced,frozenAge=age,renderNow=100+age,beamBorn=99,contactBorn=100,view=view,backdrop=options.backdrop or "bright",physicalViewport=tuple(Vector3.new(camera.ViewportSize.X,camera.ViewportSize.Y,0)),logicalAllocation=tostring(gui.AbsoluteSize),camera={position=tuple(position),lookAt=tuple(look)},beam={origin=tuple(home+Vector3.new(0,0,16)),direction={0,0,-1},length=25,width=width,coreAndTierParts=#rig.parts,contactParts=#contacts,contactGeometry=contactParts,allocated=allocated,pooled=pooled,contactActive=rig.contactPosition~=nil},target={position=tuple(torso.Position),health=h.Health,opaque=torso.Transparency==0},lock={retained=lockController.target~=nil,markerVisible=lockMarker.Visible,bounds=rect(lockMarker),text=words.Text,textFits=words.TextFits,textBounds=tostring(words.TextBounds),buttonText=lockButton.Text,buttonTextFits=lockButton.TextFits},scope="Actual native Client HUD/lock and renderer/City constructors with fake mic/remotes, scripted target/level/comfort state, frozen VFX timestamps and fixture contrast wall. No real hit, damage, voice, physical-device or animated/performance proof."}
  assert(allocated<=512,"Shared visual pool exceeded512")
  if age==.29 then assert(#contacts==0 and not rig.contactPosition,"Expired contact retained")end
  workspace:SetAttribute("HighTierReviewResult",Http:JSONEncode(row));return row
 end
 local busy=false
 control=Instance.new("BindableFunction");control.Name="HighTierReviewControl"
 control.OnInvoke=function(options)
  if busy then return {failed=true,error="Control busy"}end;busy=true
  local result=table.pack(xpcall(function()return select(options)end,debug.traceback));busy=false
  if not result[1]then workspace:SetAttribute("HighTierReviewState","failed");workspace:SetAttribute("HighTierReviewError",tostring(result[2]));retireClient();return {failed=true,error=tostring(result[2])}end
  return table.unpack(result,2,result.n)
 end
 local ready=select({mode="After",level=50,reduced=false,age=.06,view="front",backdrop="bright"})
 assert(clientCheckpoint() and playerGui.Parent==p,"Stopped before publication")
 control.Parent=playerGui;workspace:SetAttribute("HighTierReviewState","ready");print("CONTACT_REVIEW_READY "..Http:JSONEncode(ready))
end,debug.traceback)
if not ok then workspace:SetAttribute("HighTierReviewState","failed");workspace:SetAttribute("HighTierReviewError",tostring(err));retireClient();warn(tostring(err))end
end)()
'''
tail=tail.replace('__PREFIX_SHA__',filehash(OUT/'Prefix.luau'))
(OUT/'Tail.luau').write_text(tail,encoding='utf8');(OUT/'Review.client.luau').write_text(prefix+tail,encoding='utf8')
project={'name':'BeamHighTierReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel',
 'ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(R/'src/ReplicatedStorage/Shared')},'BeforeVisuals':{'$path':str(OUT/'BeforeVisuals.luau')},'CompactCity':{'$path':str(R/'src/ServerScriptService/CompactCity.luau')}},
 'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','HighTierReview':{'$path':str(OUT/'Review.client.luau')}}},
 'Workspace':{'$className':'Workspace','Spawn':{'$className':'SpawnLocation','$properties':{'Anchored':True,'Position':[0,0,0],'Neutral':True,'Duration':0}}}}}
(OUT/'Review.project.json').write_text(json.dumps(project,indent=2),encoding='utf8')
subprocess.run(['luau-compile',str(OUT/'Review.client.luau')],cwd=R,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['rojo','build',str(OUT/'Review.project.json'),'-o',str(OUT/'Review.rbxl')],cwd=R,check=True)
assert all(filehash(R/name)==value for name,value in sources.items()),'Production source changed during build'
names=list(dict.fromkeys(re.findall(r'modules\.([A-Za-z0-9_]+)=\(function\(',prefix)))
inputs={n:sources[n] for n in sources if n.startswith('src/ReplicatedStorage/Shared/') or Path(n).stem in names or n.endswith('/CompactCity.luau') or n=='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'}
artifact_names=('BeforeVisuals.luau','Prefix.luau','Tail.luau','Review.client.luau','Review.project.json','Review.rbxl')
report={'version':1,'baseline':BASE,'baselineFixture':'tests/fixtures/nov13-contact-baseline/manifest.json','sourceHashes':inputs,'beforeVisualsSha256':sha(before),'builderSha256':filehash(Path(__file__)),
 'artifacts':{name:filehash(OUT/name) for name in artifact_names},'nativeExecuted':False,
 'scope':'High-tier clarity build/compile only: matched b76 baseline/current renderer, both with identical fixture-injected contact. Actual Client preview prefix with fake microphone/remotes, genuine static City constructor, opaque scripted humanoid and one renderer at a time. No server Bootstrap/Profiles. Only root runs reviewed native fixture.',
 'fixtureEdits':['Matched Before/After logical UI allocation1280x640 and virtual touchfalse fit the current native capture; this is not a device setting. Marker camera viewport restored to real camera.','PlayerGui startup wait bounded12seconds.','Fixture camera/avatar/target and ivory/slate backdrop, fully cleaned.','Sample level/reduced state is fake local UI data; no settings service or real profile.','Explicit frozen renderer timeline: born99/contact100/Animate100+age; no animation loop or real damage event.'],
 'control':'LocalPlayer.PlayerGui.HighTierReviewControl:Invoke({mode="Before"/"After",level=1/50/70/80/90/100,reduced=boolean,age=0/.06/.16/.29,view="front"/"oblique",backdrop="bright"/"dark"}); cleanup via {cleanup=true}',
 'limits':['High-tier clarity native appearance pending.','Frozen ages do not prove motion/comfort/performance.','Fake mic/remotes/state and scripted humanoid do not establish human voice/phone/multiplayer/server hits.','Both endpoints remain9studs past target; identical Contact calls are fixture-injected at target root in both Before and After.','Fixture Spawn is declared at origin(0,0,0), matching the previous observed native export; root verifies actual origin and more than100studs from target before use.']}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'artifact':str(OUT/'Review.rbxl'),'sha256':report['artifacts']['Review.rbxl'],'scriptSha256':report['artifacts']['Review.client.luau'],'prefixSha256':report['artifacts']['Prefix.luau'],'modules':len(names),'nativeExecuted':False}))
