"""Build-only exact Client HUD comparison in a disposable local place. Never starts Studio."""
from pathlib import Path
import hashlib,json,re,subprocess,sys

R=Path(__file__).resolve().parents[1];OUT=R/'build/hud-readability-review';OUT.mkdir(parents=True,exist_ok=True)
BASE='025389f916c481f031a088dd4c2d021061a487b3';P='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return sha(p.read_bytes())
def once(s,a,b):
 assert s.count(a)==1,(a[:90],s.count(a))
 return s.replace(a,b,1)

raw={'Before':subprocess.check_output(['git','show',BASE+':'+P],cwd=R),'After':(R/P).read_bytes()}
subprocess.run([sys.executable,str(R/'tests/build_ui_preview.py'),'1280','640'],cwd=R,check=True)
preview=(R/'build/StudioUIPreview.luau').read_text(encoding='utf8');preview=preview[:preview.rindex('local report={}')]
marker='-- This owner covers only this Client\'s resources; terminal cleanup is reentrant.'
modules=preview[preview.index('assert(game:GetService'):preview.index(marker)]
current_body=preview[preview.index(marker):]
original_remotes='local remotes=RS:WaitForChild("ScreamRemotes");if not clientCheckpoint() then return end'
mock_remotes=current_body[current_body.index('local receiver\n'):current_body.index('\nlocal action=remotes:WaitForChild("Action")')]
original_gui='local gui=Instance.new("ScreenGui");ownClient(function() gui:Destroy() end);if not clientCheckpoint() then return end\ngui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=playerGui'
mock_gui=current_body[current_body.index('local screen=Instance.new("ScreenGui")'):current_body.index('\nlocal dark=Color3.fromRGB')]
mock_mic=re.search(r'mic=\{Destroy=function\(\).*?\}\n',current_body).group(0).rstrip('\n')
def client_body(b):
 s=b.decode('utf8').replace('\r\n','\n')
 start=s.index('local function loadClientDependency(');end=s.index('\nend\n',start)+5
 s=s[:start]+s[end-1:]
 s=re.sub(r'loadClientDependency\((?:script.Parent|RS.Shared|shared),"([A-Za-z0-9_]+)"(?:,true)?\)',lambda m:'modules.'+m[1],s)
 s=once(s,'local shared=RS:WaitForChild("Shared");if not clientCheckpoint() then return end','if not clientCheckpoint() then return end')
 s=once(s,'mic=mic.new()',mock_mic);s=once(s,original_remotes,mock_remotes);s=once(s,original_gui,mock_gui)
 s=s.replace('workspace.CurrentCamera.ViewportSize','Vector2.new(1280,640)').replace('UIS.TouchEnabled','fixtureTouch')
 assert 'loadClientDependency' not in s and not re.search(r'\brequire\s*\(',s)
 return s+'\n'
assert client_body(raw['After'])==current_body,'Custom binding differs from recognized preview transformation'

tail=r'''
return (function()
 local fixtureModel
 local function clearHealth()if fixtureModel then fixtureModel:Destroy();fixtureModel=nil end;fixtureHealthCharacter=nil end
 ownClient(clearHealth)
 local function rect(o)return {x=o.AbsolutePosition.X,y=o.AbsolutePosition.Y,w=o.AbsoluteSize.X,h=o.AbsoluteSize.Y}end
 local function settle()for _=1,4 do Run.RenderStepped:Wait();assert(clientCheckpoint() and playerGui.Parent==p,'Review retired during settle')end end
 local function capture(o)
  local r={name=o.Name,visible=o.Visible,bounds=rect(o)}
  if o:IsA('TextLabel') or o:IsA('TextButton')then r.text=o.Text;r.textFits=o.TextFits;r.textBounds={o.TextBounds.X,o.TextBounds.Y};r.textSize=o.TextSize;r.color=tostring(o.TextColor3)end
  return r
 end
 local function select(options)
  assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0 and clientCheckpoint(),'LOCAL HUD REVIEW ONLY')
  local width=options.width;assert(width==320 or width==390 or width==1280,'Width320/390/1280 required')
  assert(type(options.touch)=='boolean','Fixture touch flag required')
  local case=options.case;assert(case=='full' or case=='low' or case=='dead' or case=='respawn-gap' or case=='large' or case=='unsaved' or case=='recovered' or case=='delayed','Unknown HUD state')
  clearHealth();gui.Size=UDim2.fromOffset(width,width==320 and 568 or width==390 and 844 or 640);fixtureTouch=options.touch
  gui.Position=UDim2.fromOffset(12,12);modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false
  sample.level=case=='large' and 100 or 1;sample.coins=case=='large' and 2147483647 or 350
  sample.xp=case=='large' and 1800 or 81;sample.xpNext=case=='large' and 1800 or 103
  sample.maxHealth=case=='large' and 450 or 100;sample.health=sample.maxHealth
  sample.activeQuest='garden';sample.questTime=90;sample.devAccess=false;sample.inWarZone=false;sample.testSession=false
  sample.savingAvailable=case~='unsaved';sample.savingDelayed=case=='delayed';sample.recoveryWarning=case=='recovered'
  sample.settings={volume=0,reducedShake=true};mic.power=0;mic.ready=true;mic.eligible=true;mic.status='Fixture mic available; no audio capture'
  fixtureModel=Instance.new('Model');fixtureModel.Name='OwnedHUDHealthSource';fixtureModel.Parent=screen
  local h=Instance.new('Humanoid');h.MaxHealth=sample.maxHealth;h.Health=case=='low' and 23 or (case=='dead' or case=='respawn-gap')and 0 or sample.maxHealth;h.Parent=fixtureModel
  fixtureHealthCharacter=fixtureModel
  receiver(sample);refreshHealth();sustainedControl:SetArmed(false)
  if case=='respawn-gap'then fixtureHealthCharacter=nil;refreshHealth()end
  settle()
  local texts={};local parts={}
  for _,o in ipairs(hud:GetDescendants())do
   if o:IsA('TextLabel') or o:IsA('TextButton')then table.insert(texts,capture(o))end
   if o:IsA('GuiObject')then table.insert(parts,capture(o))end
  end
  local camera=workspace.CurrentCamera
  return {mode='__MODE__',case=case,logicalAllocation={gui.AbsoluteSize.X,gui.AbsoluteSize.Y},translation={gui.AbsolutePosition.X,gui.AbsolutePosition.Y},physicalViewport=camera and {camera.ViewportSize.X,camera.ViewportSize.Y},fixtureTouch=fixtureTouch,gameId=game.GameId,placeId=game.PlaceId,hud=capture(hud),texts=texts,parts=parts,healthText=health.Text,healthFill={hf.Size.X.Scale,hf.Size.Y.Scale},xpText=xpText.Text,xpFill=xf.Size.X.Scale,quest=capture(tracked),minimap=capture(miniMapButton),controls=capture(controls),saveNotice=capture(saveNotice),healthSource={health=h.Health,maximum=h.MaxHealth,gap=fixtureHealthCharacter==nil},identity='__IDENTITY__',scope='Actual full Client/helpers/controllers/layout and dependency bundle. Preview microphone/remotes/touch and owned native Humanoid source are fixture inputs. Logical GUI allocation is not a physical phone; no server, saved data, real voice, damage or input acceptance.'}
 end
 screen.Name='HUDReadabilityLocalReview';screen.DisplayOrder=100
 return {select=select,cleanup=retireClient}
end)()
'''

guard='assert(game:GetService("RunService"):IsStudio() and game.GameId==0 and game.PlaceId==0,"LOCAL HUD REVIEW ONLY")\n'
for mode,b in raw.items():
 body=client_body(b)
 body=once(body,'local view=Vector2.new(1280,640)','local view=workspace.CurrentCamera.ViewportSize')
 body=once(body,'local playerGui=p:WaitForChild("PlayerGui");if not clientCheckpoint() then return end','local playerGui=p:WaitForChild("PlayerGui",12);assert(playerGui and playerGui:IsA("PlayerGui"),"PlayerGui unavailable after12seconds");if not clientCheckpoint() then return end')
 body=once(body,'local function refreshHealth()\n local character=p.Character','local function refreshHealth()\n local character=fixtureHealthCharacter')
 body=once(body,'local function ownClient(cleanup)','onCleanupReady(retireClient)\nlocal function ownClient(cleanup)')
 assert 'modules.Profiles=' not in modules and 'Bootstrap' not in modules
 script=guard+'return function(onCleanupReady)\nlocal fixtureTouch=true\nlocal fixtureHealthCharacter\n'+modules+body+tail.replace('__MODE__',mode).replace('__IDENTITY__',sha(b))+'\nend\n'
 (OUT/(mode+'Client.luau')).write_text(script,encoding='utf8',newline='\n')
 (OUT/(mode+'Client.raw.luau')).write_bytes(b)

driver=r'''
local Run=game:GetService('RunService')
assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0,'LOCAL HUD REVIEW ONLY')
local p=game.Players.LocalPlayer;local pg=p:WaitForChild('PlayerGui',12);assert(pg,'PlayerGui unavailable after12seconds')
local factories={Before=require(game.ReplicatedStorage.BeforeClient),After=require(game.ReplicatedStorage.AfterClient)}
local active,mode,control,watchdog,busy,closed
local function cleanup()
 if closed then return end;closed=true
 if active then pcall(active.cleanup);active=nil end
 if control then control:Destroy();control=nil end
 if watchdog and watchdog~=coroutine.running()then pcall(task.cancel,watchdog)end;watchdog=nil
end
script.Destroying:Connect(cleanup)
local function select(options)
 assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0 and not closed,'LOCAL HUD REVIEW ONLY')
 assert(type(options)=='table','Options table required')
 if options.cleanup then workspace:SetAttribute('HUDReadabilityReviewState','cleaned');cleanup();return {cleaned=true,gameId=game.GameId,placeId=game.PlaceId}end
 assert(not busy,'Review control already busy');busy=true
 local ok,result=xpcall(function()
  assert(options.mode=='Before' or options.mode=='After','Before/After required')
  if options.mode~=mode then
   if active then active.cleanup();active=nil end
   mode=options.mode
   local nextActive=factories[mode](function(fn)active={cleanup=fn}end)
   assert(nextActive and nextActive.select and nextActive.cleanup,'Client factory failed')
   active=nextActive
  end
  return active.select(options)
 end,debug.traceback)
 busy=false
 if not ok then workspace:SetAttribute('HUDReadabilityReviewState','failed');workspace:SetAttribute('HUDReadabilityReviewError',tostring(result));cleanup();error(result)end
 return result
end
local ok,err=xpcall(function()
 workspace:SetAttribute('HUDReadabilityReviewState','initializing')
 watchdog=task.delay(300,function()watchdog=nil;workspace:SetAttribute('HUDReadabilityReviewState','timed-out');cleanup()end)
 local initial=select({mode='After',width=390,touch=true,case='full'})
 assert(not closed and pg.Parent==p,'Review stopped before publication')
 control=Instance.new('BindableFunction');control.Name='HUDReadabilityReviewControl';control.OnInvoke=select;control.Parent=pg
 workspace:SetAttribute('HUDReadabilityReviewState','ready');print('HUD_READABILITY_REVIEW_READY '..game:GetService('HttpService'):JSONEncode(initial))
end,debug.traceback)
if not ok then workspace:SetAttribute('HUDReadabilityReviewState','failed');workspace:SetAttribute('HUDReadabilityReviewError',tostring(err));cleanup();warn(err)end
'''
(OUT/'Review.client.luau').write_text(driver,encoding='utf8',newline='\n')
project={'name':'HUDReadabilityReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(R/'src/ReplicatedStorage/Shared')},'BeforeClient':{'$path':str(OUT/'BeforeClient.luau')},'AfterClient':{'$path':str(OUT/'AfterClient.luau')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','HUDReadabilityReview':{'$path':str(OUT/'Review.client.luau')}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[100,1,100],'Color':[.15,.22,.25]}},'Spawn':{'$className':'SpawnLocation','$properties':{'Anchored':True,'Neutral':True,'Duration':0}}}}}
(OUT/'Review.project.json').write_text(json.dumps(project,indent=2),encoding='utf8',newline='\n')
for n in ('BeforeClient.luau','AfterClient.luau','Review.client.luau'):subprocess.run(['luau-compile',str(OUT/n)],cwd=R,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['rojo','build',str(OUT/'Review.project.json'),'-o',str(OUT/'Review.rbxl')],cwd=R,check=True)
assert (R/P).read_bytes()==raw['After'],'Client changed during build'
names=list(dict.fromkeys(re.findall(r'modules\.([A-Za-z0-9_]+)=\(function\(',modules)))
paths={p.stem:p for d in ('src/ReplicatedStorage/Shared','src/StarterPlayer/StarterPlayerScripts','src/ServerScriptService') for p in (R/d).glob('*.luau')}
artifact_names=('BeforeClient.luau','AfterClient.luau','BeforeClient.raw.luau','AfterClient.raw.luau','Review.client.luau','Review.project.json','Review.rbxl')
report={'baseline':BASE,'gitHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'rawClientHashes':{n:sha(b) for n,b in raw.items()},'normalizedClientHashes':{n:sha(b.decode('utf8').replace('\r\n','\n').encode()) for n,b in raw.items()},'moduleSourceHashes':{str(paths[n].relative_to(R)).replace('\\','/'):filehash(paths[n]) for n in names},'sourceBytes':{n:(OUT/n).stat().st_size for n in ('BeforeClient.luau','AfterClient.luau','Review.client.luau')},'builderSha256':filehash(Path(__file__)),'artifacts':{n:filehash(OUT/n) for n in artifact_names},'nativeExecuted':False,'scope':'Build/compile only. Exact full Before025389f/current Client and current dependency bundle using recognized build_ui_preview substitutions, strict Studio0/0 guard, one owned mode at a time and actual callbacks/RenderStepped. No Bootstrap/server script, real microphone/remotes or profiles.','fixtureEdits':['Fake mic/remotes/sample and touch flag from existing UI preview.','ScreenGui replaced with transparent allocated Frame; physical camera viewport retained for lock marker.','Only refreshHealth character binding points at an owned native Humanoid model; gap case explicitly clears it after observing zero. No actual avatar health or respawn mutation.','DisplayOrder100, root translation12,12; 320x568/390x844/1280x640 are logical allocations only.','One factory active at a time; Client cleanup on mode switch, control error, Destroying, explicit cleanup or300secondwatchdog.','Native health/XP/server callbacks use fixture data; no real transport acceptance.'],'control':'LocalPlayer.PlayerGui.HUDReadabilityReviewControl:Invoke({mode="Before"/"After",width=320/390/1280,touch=boolean,case="full"/"low"/"dead"/"respawn-gap"/"large"/"unsaved"/"recovered"/"delayed"}); {cleanup=true}','limits':['Native rendered appearance and TextFits pending root Play.','Logical allocation and fixtureTouch are not actual device/input validation.','Machine snapshots and synthetic Health do not establish damage/replication/voice/saving/gameplay behavior.','Large case intentionally uses level100/450HP/2147483647coins to expose typography limits.','Full Client modules are inlined using existing harness resolver; this does not test normal ModuleScript startup.']}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
print(json.dumps({'artifact':str(OUT/'Review.rbxl'),'artifactSha256':report['artifacts']['Review.rbxl'],'afterClientSha256':report['rawClientHashes']['After'],'sourceBytes':report['sourceBytes'],'modules':len(names),'nativeExecuted':False}))
