"""Build-only standalone actual ShopUI comparison with deterministic local pricing."""
from pathlib import Path
import hashlib,json,subprocess

R=Path(__file__).resolve().parents[1];OUT=R/'build/boost-status-review';OUT.mkdir(parents=True,exist_ok=True)
BASE='5622daa54424e639e7d3f671b2e453ff377b2cb6';P='src/StarterPlayer/StarterPlayerScripts/ShopUI.luau'
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(p):return sha(p.read_bytes())
raw={'BeforeShop':subprocess.check_output(['git','show',BASE+':'+P],cwd=R),'AfterShop':(R/P).read_bytes()}
provider='local Marketplace={GetProductInfoAsync=function() script:SetAttribute("FixturePriceLookupCalls",(script:GetAttribute("FixturePriceLookupCalls") or 0)+1);error("Fixture forbids marketplace requests") end}'
for name,b in raw.items():
 s=b.decode('utf8').replace('\r\n','\n');line='local Marketplace=game:GetService("MarketplaceService")';assert s.count(line)==1
 (OUT/(name+'.luau')).write_text(s.replace(line,provider,1),encoding='utf8')
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf8')
helpers=client[client.index('local function frame(parent,'):client.index('-- Presentation only: no subscriptions')]
card=client[client.index('local function card(height)'):client.index('local function info(',client.index('local function card(height)'))]
palette=next(line for line in client.splitlines() if line.startswith('local dark=Color3.fromRGB'))
prefix=r'''
local Run=game:GetService("RunService")
assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0,"LOCAL BOOST REVIEW ONLY")
local player=game.Players.LocalPlayer;local playerGui=player:WaitForChild("PlayerGui",12)
assert(playerGui and playerGui.Parent==player,"PlayerGui unavailable after12seconds")
local Http=game:GetService("HttpService")
local Before=require(game.ReplicatedStorage.BeforeShop);local After=require(game.ReplicatedStorage.AfterShop)
local Catalog=require(game.ReplicatedStorage.Shared.ShopCatalog);local Config=require(game.ReplicatedStorage.Shared.Config)
local clientDestroyed=false;local screen,control,content,hidden,watchdog
for _,item in ipairs(Catalog.Items)do assert(item.id==0,"Fixture requires unchanged unconfigured catalog")end
assert(Config.MovementPassId==0,"Fixture requires unchanged MovementPassId")
local function cleanup()
 if clientDestroyed then return end;clientDestroyed=true
 Before.Clear();After.Clear()
 if screen then screen:Destroy()end;if control then control:Destroy()end
 if watchdog and watchdog~=coroutine.running()then pcall(task.cancel,watchdog)end;watchdog=nil
end
script.Destroying:Connect(cleanup)
'''
body=r'''
local calls={};local action={FireServer=function(_,verb,key)table.insert(calls,{verb=verb,key=key})end}
local ok,err=xpcall(function()
 watchdog=task.delay(300,function()workspace:SetAttribute("BoostReviewState","timed-out");watchdog=nil;cleanup()end)
 screen=Instance.new("ScreenGui");screen.Name="BoostStatusLocalReview";screen.ResetOnSpawn=false;screen.ScreenInsets=Enum.ScreenInsets.None;screen.DisplayOrder=100;screen.Parent=playerGui
 local allocation=frame(screen,"LogicalAllocation",UDim2.fromOffset(390,844),UDim2.fromOffset(16,16));allocation.BackgroundTransparency=1
 local reviewPanel=frame(allocation,"BoostReviewPanel",UDim2.fromOffset(366,620),UDim2.fromOffset(12,20),dark)
 local title=label(reviewPanel,"BOOST STATUS / LOCAL PREVIEW",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),16,gold)
 content=Instance.new("ScrollingFrame");content.Name="Content";content.Position=UDim2.fromOffset(20,54);content.Size=UDim2.new(1,-40,1,-70);content.BackgroundTransparency=1;content.BorderSizePixel=0;content.ScrollBarThickness=4;content.AutomaticCanvasSize=Enum.AutomaticSize.Y;content.CanvasSize=UDim2.new();content.Parent=reviewPanel
 local list=Instance.new("UIListLayout");list.Padding=UDim.new(0,10);list.SortOrder=Enum.SortOrder.LayoutOrder;list.Parent=content
 hidden=Instance.new("Folder");hidden.Name="HiddenNonBoostCards";hidden.Parent=screen
 local function clear()
  Before.Clear();After.Clear()
  for _,child in ipairs(content:GetChildren())do if child:IsA("GuiObject")then child:Destroy()end end
  for _,child in ipairs(hidden:GetChildren())do child:Destroy()end
 end
 local function bounds(o)return {x=o.AbsolutePosition.X,y=o.AbsolutePosition.Y,w=o.AbsoluteSize.X,h=o.AbsoluteSize.Y}end
 local function settle()for _=1,3 do Run.RenderStepped:Wait();assert(not clientDestroyed and playerGui.Parent==player,"Review stopped")end end
 local function select(options)
  assert(Run:IsStudio() and game.GameId==0 and game.PlaceId==0 and not clientDestroyed,"LOCAL BOOST REVIEW ONLY")
  assert(type(options)=="table","Options table required")
  if options.cleanup then cleanup();workspace:SetAttribute("BoostReviewState","cleaned");return {cleaned=true,actions=#calls}end
  assert(options.mode=="Before" or options.mode=="After","Mode Before/After required")
  local width=options.width;assert(width==320 or width==390 or width==1280,"Width320/390/1280 required")
  local case=options.case or 'mixed';assert(case=='mixed' or case=='inactive' or case=='active' or case=='unavailable' or case=='saved' or case=='expires','Unknown state case')
  assert(options.focus==nil or options.focus=='Coins' or options.focus=='XP','Unknown focus')
  clear();allocation.Size=UDim2.fromOffset(width,width==320 and 568 or width==390 and 844 or 720)
  local panelWidth=math.min(720,width-24);reviewPanel.Size=UDim2.fromOffset(panelWidth,math.min(620,allocation.Size.Y.Offset-76));reviewPanel.Position=UDim2.fromOffset((width-panelWidth)/2,20)
  title.Text=options.mode:upper().." / BOOST STATUS"
  local now=os.time();local ready=case~='unavailable'
  local data={savingAvailable=ready,spectrumPass=false,movementPass=false,shop={ready=ready,inventory={xp=case=='saved' and 2 or 0,coins=case=='saved' and 1 or 0},ends={xp=case=='inactive' and 0 or now+(case=='expires' and 2 or 1254),coins=case=='active' and now+601 or 0},serverNow=now}}
  local module=options.mode=='Before' and Before or After
  module.Render(data,{card=card,frame=frame,label=label,button=button,info=function()end,narrow=panelWidth<620},action)
  for _,c in ipairs(content:GetChildren())do if c:IsA('GuiObject') and c.Name~='BoostXP' and c.Name~='BoostCoins'then c.Visible=false;c.Parent=hidden end end
  content.CanvasPosition=Vector2.zero;settle();module.Tick();settle()
  local transition
  if case=='expires'then
   local c=content:FindFirstChild('BoostXP');local text=c:FindFirstChild('BoostStatusText',true)
   if not text then for _,o in ipairs(c:GetDescendants())do if o:IsA('TextLabel') and o.Text:find('ACTIVE',1,true)then text=o;break end end end
   assert(text,'Expiry status label missing');local band=c:FindFirstChild('BoostStatus')
   local function statusStyle()
    return {text=text.Text,color=tostring(text.TextColor3),band=band and tostring(band.BackgroundColor3),textFits=text.TextFits}
   end
   transition={before=statusStyle()};task.wait(2.1);assert(not clientDestroyed,'Review stopped during expiry');module.Tick();settle();transition.after=statusStyle()
  end
  if options.focus then
   local c=assert(content:FindFirstChild('Boost'..options.focus),'Boost card missing')
   local y=content.CanvasPosition.Y+c.AbsolutePosition.Y-content.AbsolutePosition.Y-6
   content.CanvasPosition=Vector2.new(0,math.clamp(y,0,math.max(0,content.AbsoluteCanvasSize.Y-content.AbsoluteSize.Y)));settle()
  end
  local rows={}
  for _,c in ipairs(content:GetChildren())do if c:IsA('GuiObject')then
   local row={name=c.Name,bounds=bounds(c),labels={},buttons={},statusBands={}}
   for _,o in ipairs(c:GetDescendants())do
    if o:IsA('TextLabel')then table.insert(row.labels,{name=o.Name,text=o.Text,textFits=o.TextFits,textBounds=tostring(o.TextBounds),textSize=o.TextSize,color=tostring(o.TextColor3),bounds=bounds(o)})end
    if o:IsA('TextButton')then table.insert(row.buttons,{name=o.Name,text=o.Text,textFits=o.TextFits,bounds=bounds(o),autoButtonColor=o.AutoButtonColor})end
    if o:IsA('Frame') and o.Name=='BoostStatus'then table.insert(row.statusBands,{bounds=bounds(o),color=tostring(o.BackgroundColor3),active=o.Active,selectable=o.Selectable,interactable=o.Interactable})end
   end
   table.insert(rows,row)
  end end
  local camera=workspace.CurrentCamera
  local lookups=(game.ReplicatedStorage.BeforeShop:GetAttribute('FixturePriceLookupCalls') or 0)+(game.ReplicatedStorage.AfterShop:GetAttribute('FixturePriceLookupCalls') or 0)
  assert(lookups==0,'Unconfigured catalog unexpectedly requested prices')
  local result={mode=options.mode,case=case,logicalAllocation=tostring(allocation.AbsoluteSize),physicalViewport=camera and tostring(camera.ViewportSize),panelBounds=bounds(reviewPanel),contentBounds=bounds(content),canvasPosition=tostring(content.CanvasPosition),canvasSize=tostring(content.AbsoluteCanvasSize),cards=rows,transition=transition,actionCount=#calls,actions=calls,priceLookupCalls=lookups,sourceIdentity="__IDENTITY__",scope="Actual ShopUI Render/Tick and Client factories, unchanged zero product/pass IDs, forbidden-price provider/fake actions, full Render with non-boost cards hidden. Logical allocations are not actual device validation; no prices, purchases, receipt delivery or saved state."}
  workspace:SetAttribute("BoostReviewResult",Http:JSONEncode(result));return result
 end
 control=Instance.new('BindableFunction');control.Name='BoostStatusReviewControl'
 local busy=false
 control.OnInvoke=function(options)
  if busy then return {failed=true,error='Control busy'}end;busy=true
  local result=table.pack(xpcall(function()return select(options)end,debug.traceback));busy=false
  if not result[1]then workspace:SetAttribute('BoostReviewState','failed');workspace:SetAttribute('BoostReviewError',tostring(result[2]));cleanup();return {failed=true,error=tostring(result[2])}end
  return table.unpack(result,2,result.n)
 end
 local ready=select({mode='After',width=390,case='mixed'})
 assert(not clientDestroyed and playerGui.Parent==player,'Stopped before publication')
 control.Parent=playerGui;workspace:SetAttribute('BoostReviewState','ready');print('BOOST_REVIEW_READY '..Http:JSONEncode(ready))
end,debug.traceback)
if not ok then workspace:SetAttribute('BoostReviewState','failed');workspace:SetAttribute('BoostReviewError',tostring(err));cleanup();warn(tostring(err))end
'''
identity=sha(raw['AfterShop']);body=body.replace('__IDENTITY__',identity)
fixture=prefix+'\n'+palette+'\n'+helpers+'\n'+card+'\n'+body
(OUT/'Review.client.luau').write_text(fixture,encoding='utf8')
total=sum((OUT/n).stat().st_size for n in ('BeforeShop.luau','AfterShop.luau','Review.client.luau'));assert total<200000
project={'name':'BoostStatusReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(R/'src/ReplicatedStorage/Shared')},'BeforeShop':{'$path':str(OUT/'BeforeShop.luau')},'AfterShop':{'$path':str(OUT/'AfterShop.luau')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','BoostStatusReview':{'$path':str(OUT/'Review.client.luau')}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[100,1,100]}}}}}
(OUT/'Review.project.json').write_text(json.dumps(project,indent=2),encoding='utf8')
for name in ('BeforeShop.luau','AfterShop.luau','Review.client.luau'):subprocess.run(['luau-compile',str(OUT/name)],cwd=R,check=True,stdout=subprocess.DEVNULL)
subprocess.run(['rojo','build',str(OUT/'Review.project.json'),'-o',str(OUT/'Review.rbxl')],cwd=R,check=True)
assert (R/P).read_bytes()==raw['AfterShop'],'ShopUI changed during build'
report={'baseline':BASE,'rawShopHashes':{name:sha(b) for name,b in raw.items()},'clientFactoriesSha256':filehash(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'),'factoryExcerptSha256':sha((helpers+card).encode()),'providerSubstitution':provider,'threeSourceBytes':total,'builderSha256':filehash(Path(__file__)),'artifacts':{n:filehash(OUT/n) for n in ('BeforeShop.luau','AfterShop.luau','Review.client.luau','Review.project.json','Review.rbxl')},'sharedSourceHashes':{str(p.relative_to(R)).replace('\\','/'):filehash(p) for p in (R/'src/ReplicatedStorage/Shared').glob('*.luau')},'scope':'Build/compile only. Full actual ShopUI modules differ only by forbidden-request Marketplace provider substitution. Original product/pass IDs remain zero and price provider must receive zero calls; action logger has no network/prompt method. Actual Client helpers/card widths; non-boost cards hidden after full Render; ColorMixer never called. No normal Client, server Bootstrap, profiles or purchase/receipt execution.','control':'LocalPlayer.PlayerGui.BoostStatusReviewControl:Invoke({mode="Before"/"After",width=320/390/1280,case="mixed"/"inactive"/"active"/"unavailable"/"saved"/"expires",focus="XP"/"Coins" optional}); {cleanup=true}','limits':['Native text/layout pending.','Logical sizes are not physical-device evidence.','Original zero IDs produce COMING SOON; no price service request is allowed.','Actual purchase/saved buttons send only to the fixture action logger; no real purchase/receipt or persistence claim.','Expires case uses actual2.1second wait and Tick with no clock substitution; no long-running countdown/performance claim.']}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'artifact':str(OUT/'Review.rbxl'),'artifactSha256':report['artifacts']['Review.rbxl'],'scriptSha256':report['artifacts']['Review.client.luau'],'threeSourceBytes':total,'afterShopSha256':identity,'nativeExecuted':False}))
