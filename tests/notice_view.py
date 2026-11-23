"""Real NoticeView/Layout/Queue and Client notice block; synthetic text metrics and GUI."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
paths=['NoticeLayout','NoticeView'];sources={n:(R/f'src/StarterPlayer/StarterPlayerScripts/{n}.luau').read_text(encoding='utf-8-sig') for n in paths}
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();city=(R/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text();mini=city[city.index('function CityMap.MiniLayout('):city.index('function CityMap.MiniUpdate(')]
integration=client[client.index(' -- Pause queue time while covered,'):client.index(' beamScreenFeedback:Step(',client.index(' -- Pause queue time while covered,'))]
assert 'local arenaActive=academy.refreshZone()' in client[client.index('connectClient(Run.RenderStepped,function(dt)'):client.index(integration)]
builder=(R/'tests/build_sustained_review.py').read_text(encoding='utf-8')
travel_callback=builder[builder.index(' local function travelNotice()'):builder.index(' connectClient(p:GetAttributeChangedSignal("TravelStatus")')]
texts=[]
for f in (R/'src').rglob('*.luau'):
 for t in re.findall(r'"([^"\n]+)"',f.read_text(encoding='utf-8-sig')):
  if len(t) in (93,85,142,114) and ('sav' in t.lower() or 'progress' in t.lower()) and t not in texts:texts.append(t)
profile=(R/'src/ServerScriptService/Profiles.luau').read_text()
recovery=re.search(r'local RECOVERY_NOTICE="([^"]+)"',profile).group(1)
for suffix in (' Another session owns this profile; progress here is temporary. Rejoin shortly.',' Saving is unavailable; progress here is temporary.'):
 assert suffix.strip() in profile
 texts.append(recovery+suffix)
assert [len(t)for t in texts]==[93,85,142,114]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=0;local os={clock=function()return now end};local measured=0
local V={};V.__index=V;function V.__sub(a,b)return setmetatable({X=a.X-b.X,Y=a.Y-b.Y},V)end
local Vector2={new=function(x,y)return setmetatable({X=x,Y=y},V)end};Vector2.zero=Vector2.new(0,0)
local UDim={new=function(s,o)return {Scale=s or 0,Offset=o or 0}end}
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local UDim2={new=function(xs,x,ys,y)return {X={Scale=xs,Offset=x},Y={Scale=ys,Offset=y}}end}
function UDim2.fromOffset(x,y)return UDim2.new(0,x,0,y)end
local Enum={ScrollingDirection={Y=1},TextYAlignment={Top=1},ApplyStrokeMode={Border=1,Contextual=2}}
local function signal()local s={};function s:Connect(fn)local c={fn=fn,on=true};function c:Disconnect()self.on=false end;table.insert(self,c);return c end;function s:Fire()for _,c in ipairs(self)do if c.on then c.fn()end end end;return s end
local instances=0;local Instance={new=function(kind)instances+=1;local x={ClassName=kind,Visible=true,CanvasPosition=Vector2.zero,AbsolutePosition=Vector2.zero,AbsoluteSize=Vector2.zero,MouseEnter=signal(),MouseLeave=signal(),InputBegan=signal(),changed=signal()};function x:GetPropertyChangedSignal()return self.changed end;function x:Destroy()self.dead=true;self.Parent=nil end;return x end}
local TextService={GetTextSize=function(_,text,size,font,bounds)measured+=1;return {Y=math.ceil(#text*size*.55/bounds.X)*18}end}
local game={GetService=function()return TextService end};local script={Parent={NoticeLayout='layout'}}
local function loadLayout()
'''
checks=r'''
local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local function make()
 local text=Instance.new('TextLabel');text.Text='';text.Font='Gotham';local v=View.new({},text);return v
end
do
 local styled=make()
 check(styled.corner.ClassName=='UICorner' and styled.corner.Name=='NoticeCorner' and styled.corner.Parent==styled.root and styled.corner.CornerRadius.Scale==0 and styled.corner.CornerRadius.Offset==6,'NoticeCorner missing 6px radius')
 check(styled.stroke.ClassName=='UIStroke' and styled.stroke.Name=='NoticeStroke' and styled.stroke.Parent==styled.root and styled.stroke.ApplyStrokeMode==Enum.ApplyStrokeMode.Border and styled.stroke.Thickness==1,'NoticeStroke not border-scoped')
 check(styled.stroke.Transparency==.55 and styled.stroke.Color.R==235 and styled.stroke.Color.G==190 and styled.stroke.Color.B==105,'NoticeStroke transparency or gold color wrong')
 check(styled.hint.BorderSizePixel==0 and styled.hint.BackgroundColor3.R==48 and styled.hint.BackgroundColor3.G==42 and styled.hint.BackgroundColor3.B==28 and styled.hint.BackgroundTransparency==.15,'Scroll hint background treatment missing')
 check(styled.hint.TextColor3 and styled.hint.TextColor3.R==255 and styled.hint.TextColor3.G==214 and styled.hint.TextColor3.B==128,'Scroll hint lost accent color')
 check(styled.hintCorner.ClassName=='UICorner' and styled.hintCorner.Name=='NoticeScrollHintCorner' and styled.hintCorner.Parent==styled.hint and styled.hintCorner.CornerRadius.Offset==4,'Scroll hint corner missing')
 check(styled.hintStroke.ClassName=='UIStroke' and styled.hintStroke.Name=='NoticeScrollHintStroke' and styled.hintStroke.Parent==styled.hint and styled.hintStroke.ApplyStrokeMode==Enum.ApplyStrokeMode.Border and styled.hintStroke.Thickness==1 and styled.hintStroke.Transparency==.65,'Scroll hint stroke wrong')
 styled:Destroy()
end
local CityMap={aspectRatio=1.2}
MINI
local samples=SAMPLES
do
 local pos,size=Vector2.new(14,64),Vector2.new(242,94)
 local status={x=14,y=64,width=242,height=94}
 local w,h=666,316
 local map=CityMap.MiniLayout(Vector2.new(w,h),true,true)
 local beside=Layout.Get(w,h,true,map,true,false,pos,size)
 check(beside.available and beside.x>=264 and not Layout.Overlaps(beside,status),'Landscape notice covers health and progress')
 local portrait=Layout.Get(390,844,true,{available=true,width=112},false,false,pos,size)
 check(portrait.available and portrait.y>=166 and not Layout.Overlaps(portrait,status),'Narrow tall notice cannot move below the status card')
 local questPortrait=Layout.Get(390,844,true,{available=true,width=112},false,false,pos,size,210)
 check(questPortrait.available and questPortrait.y>=218,'Notice below the status card hides the timed quest tracker')
 local small=Layout.Get(390,316,true,{available=true,width=112},false,false,pos,size)
 check(not small.available,'Short narrow notice should use the existing menu fallback')
end
for _,size in ipairs({{320,315},{640,360},{390,844},{1280,720}})do
 for _,dev in ipairs({false,true})do
  local w,h=size[1],size[2];local map=CityMap.MiniLayout(Vector2.new(w,h),true,dev);local l=Layout.Get(w,h,true,map,dev)
  check(l.available and l.height>=44 and l.width>=120,'Supported notice unavailable')
  local blockers={{x=14,y=14,width=w<380 and 176 or 229,height=44},{x=w-map.width-14,y=14,width=map.width,height=map.height},{x=w-274,y=h-195,width=108,height=44},{x=w-158,y=h-195,width=144,height=44},{x=w-178,y=h-143,width=164,height=44}}
  if dev then table.insert(blockers,{x=w-(w<432 and 100 or 126),y=14+map.height+8,width=w<432 and 86 or 112,height=44})end
  for _,b in ipairs(blockers)do check(not Layout.Overlaps(l,b),'Notice overlaps actionable target')end
  local withTalk=Layout.Get(w,h,true,map,dev,true)
  if withTalk.available then
   local talk={x=withTalk.moveTalk and withTalk.talkX or w/2-60,y=withTalk.moveTalk and withTalk.talkY or h-249,width=120,height=44}
   for _,b in ipairs(blockers)do check(not Layout.Overlaps(talk,b),'Moved TALK overlaps actionable target')end
   check(not Layout.Overlaps(talk,withTalk),'TALK overlaps notice')
   check(not withTalk.moveTalk or talk.y==14,'TALK moved into native thumbstick zone')
  else check(w==320 and h==315,'Unexpected nearby-NPC fallback')end
  for _,message in ipairs(samples)do
   local v=make();local entry={};now=1;v:Update(message,l,true,now,14,entry)
   check(v.text.Text==message and v.text.Size.Y.Offset+8==v.textHeight,'Full warning truncated')
   check(not v:CanAdvance(),'New message immediately charged dwell')
   check(v.scroll.Size.Y.Offset>=44,'Actual scrolling target below44px')
   check(v.hint.Active==false and v.hint.Selectable==false and v.hint.Interactable==false,'Cue intercepts scroll input')
   now=2;v:Update(message,l,true,now,14,entry)
   if v.overflow then
    check(not v:CanAdvance() and v.hint.Text=='Scroll for full notice','Unseen overflow expires')
    v.scroll.CanvasPosition=Vector2.new(0,v.contentHeight-v.visibleHeight);v.scroll.changed:Fire();v:Update(message,l,true,now,14,entry)
    check(not v:CanAdvance(),'Scrolling charges dwell')
    now=4;v:Update(message,l,true,now,14,entry);check(v:CanAdvance(),'Bottom exposure never enables dwell')
    check(v.text.Position.Y.Offset+v.text.Size.Y.Offset-v.scroll.CanvasPosition.Y<=v.visibleHeight,'Last text line remains under cue')
   else check(v:CanAdvance(),'Fitting notice never enables dwell')end
   local before=measured;for i=1,120 do v:Update(message,l,true,now,14,entry)end;check(measured==before,'Measured text every frame')
   v.scroll.MouseEnter:Fire();v:Update(message,l,true,now,14,entry);check(not v:CanAdvance(),'Hovered notice expires');v.scroll.MouseLeave:Fire();v:Update(message,l,true,now,14,entry)
   v:Update(message,l,false,now,14,entry);check(not v:CanAdvance() and not v.root.Visible,'Covered notice expires')
   v:Update(message,l,true,now,14,{});check(not v:CanAdvance() and v.scroll.CanvasPosition.Y==0,'Same-text replacement keeps stale exposure')
   local links=v.connections;v:Destroy();v:Destroy();check(v.root.dead and not v:CanAdvance(),'Destroyed view remains active');for _,c in ipairs(links)do check(not c.on,'View signal leaked')end
  end
 end
end
for _,size in ipairs({{320,280},{280,315},{640,168}})do
 local l=Layout.Get(size[1],size[2],true,{available=false},false);check(not l.available,'Tiny viewport claimed safe access')
 local v=make();v:Update(samples[1],l,true,1,14,{});check(not v:CanAdvance() and not v.root.Visible and v.text.Text==samples[1],'Tiny fallback lost notice or charged time');v:Destroy()
end
local compact=Layout.Get(320,315,true,{available=true,width=90},false)
local v=make();v:Update('Short',compact,true,1,14,{});check(v.panelHeight==44,'Short notice wastes max-height lane')
local identity={};v:Update('Larger native text bounds',compact,true,1,14,identity);local initial=v.textHeight
v.text.TextBounds=Vector2.new(180,300);v:Update('Larger native text bounds',compact,true,2,14,identity)
check(v.textHeight==308 and v.overflow and not v:CanAdvance(),'Larger actual TextBounds clipped or charged time');v:Destroy()
-- Enlarged rendered cue is content, not a fixed overlay. Actual engine metrics are mocked.
local v=make();local id={};local message=string.rep('Critical warning ',30)
v:Update(message,compact,true,1,14,id)
check(v.hint.Parent==v.scroll and v.hint.TextWrapped,'Cue remains outside scroll content')
check(v.hint.Size.Y.Offset>=18,'Cue measurement omitted')
v.scroll.CanvasPosition=Vector2.new(0,v.contentHeight-v.visibleHeight);v:Update(message,compact,true,2,14,id)
check(v:CanAdvance(),'Initial bottom never exposed')
v.hint.TextBounds=Vector2.new(100,80)
v:Update(message,compact,true,3,14,id)
check(v.measuredHintHeight==80 and v.hint.Size.Y.Offset==80,'Enlarged cue clipped')
check(v.text.Position.Y.Offset>=v.hint.Position.Y.Offset+v.hint.Size.Y.Offset,'Cue overlaps body')
v.text.TextBounds=Vector2.new(100,900);v:Update(message,compact,true,3.1,14,id)
check(v.text.Size.Y.Offset==900 and v.scroll.Size.Y.Offset>=44,'Enlarged body or scroll target clipped')
check(not v:CanAdvance() and not v.atBottom,'Remeasure kept stale bottom exposure')
v.scroll.CanvasPosition=Vector2.new(0,v.contentHeight-v.visibleHeight);v:Update(message,compact,true,4,14,id)
check(v:CanAdvance() and v.text.Position.Y.Offset+v.text.Size.Y.Offset-v.scroll.CanvasPosition.Y<=v.visibleHeight,'Enlarged last line inaccessible')
local calls=measured;v:Update(message,compact,true,5,14,id);check(measured==calls,'Enlarged metrics repeatedly measured')
local wider={x=14,y=66,width=300,height=80,available=true};v:Update(message,wider,true,6,14,id)
check(not v:CanAdvance() and v.hint.Size.X.Offset==284,'Resize did not remeasure cue')
v.hint.TextBounds=nil;v.text.TextBounds=nil;v:Update('Short',compact,true,7,14,{})
check(v.headerHeight==0 and not v.hint.Visible and v.text.Position.Y.Offset==4 and v.scroll.CanvasPosition.Y==0,'Replacement retained header offsets')
v:Destroy()
-- Execute the actual per-frame Client queue/layout block with real helper/queue.
local NoticeLayout=Layout;local noticeView=make();local notifications=Queue.new();local viewport=Vector2.new(320,315);local touch=true;local data={devAccess=true}
local modal={Visible=false};local title={Visible=true};local talkTarget
local academy
local selected='Shop';local function closeMenu()modal.Visible=false;academy.menuNoticeRequested=nil end;local function render()end
local devPanel={Visible=false};local closeConversation;local shopRefreshes=0
local action={FireServer=function(_,verb)if verb=='ShopRefresh' then shopRefreshes+=1 end end}
local GuiService={MenuIsOpen=false}
academy={surface=function()end,compactObjective={},damageReadout={},gearUpgrade=function()return nil end,presentTalk=function()end} -- The extracted tab handler shares the Client UI namespace.
local renderedTab,renderedMenuKey
HALL_NOTICE_POLICY
local travelStatus
local p={GetAttribute=function(_,key)assert(key=="TravelStatus");return travelStatus end}
local function notify(text,urgent,key)notifications:Push(text,urgent,key)end
TRAVEL_NOTICE
TOGGLE
local top={};local dark,gold={},{};local function button(_,_,text,_,_,fn)return {Visible=true,callback=fn,Text=text}end
local storeSignal={}
local function frame(_,name)check(name=='StoreSignal','Unexpected store launcher decoration');return storeSignal end
MENU_BUTTON
QUEST_BUTTON
PASS_BUTTON
check(storeSignal.Interactable==false and storeSignal.Active==false and storeSignal.Selectable==false,'Store signal intercepted activation')
local Config={Quests={{id='a',goal=3},{id='b',goal=2}}};data.quests={}
local gold,white={},{}
QUEST_LABEL
local function receiveQuests(quests)
 data.quests=quests
RECEIVER_COUNT
end
local gameplayVisible=true;local windowFocused=true;local gui={AbsolutePosition=Vector2.zero};local dt=.05;local arenaActive=false
local function rect(x,y,w,h)return {Visible=true,AbsolutePosition=Vector2.new(x,y),AbsoluteSize=Vector2.new(w,h),Position={}}end
academy.guidePanel=rect(16,270,290,62);local meter=rect(490,612,300,96)
local talkButton=rect(100,66,120,44);local hud=rect(14,118,240,88);local tracked=rect(16,214,290,50);local zone=rect(40,12,240,28);local saveNotice=rect(35,40,250,28)
local function frame()
 local notice=notifications:Step(0,false)
 local shortLandscape=viewport.Y<300 and viewport.X>viewport.Y
 INTEGRATION
end
notifications:Push(samples[1],true,'save');local saved=notifications.active.remaining
for i=1,400 do now=i*.05;frame()end
check(notifications.active and notifications.active.remaining==saved,'Unseen Client overflow expired')
notifications:Push('More important temporary warning',true,'save');frame();check(noticeView.message=='More important temporary warning' and noticeView.scroll.CanvasPosition.Y==0,'Save replacement did not reset view')
notifications:Remove('save');frame();check(not noticeView.root.Visible and noticeView.message=='','Recovered save left stale scroll state')
notifications:Push('Short',false);now=50;frame();local old=notifications.active.remaining
windowFocused=false;for i=1,300 do now+=.05;frame()end;check(notifications.active.remaining==old,'Unfocused Client charged queue')
windowFocused=true;gameplayVisible=false;for i=1,300 do now+=.05;frame()end;check(notifications.active.remaining==old,'Covered Client charged queue')
gameplayVisible=true;for i=1,300 do now+=.05;frame()end;check(not notifications.active,'Readable Client notice never expires')
notifications:Push(string.rep('Long ordinary notice ',30),false);frame();local ordinary=notifications.active
notifications:Push(samples[1],true,'save');frame();check(notifications.active~=ordinary and noticeView.message==samples[1],'Urgent save did not preempt unread ordinary notice')
notifications:Remove('save');frame();check(notifications.active==ordinary and noticeView.message==ordinary.text and not noticeView:CanAdvance(),'Preempted message resumed with stale exposure')
notifications=Queue.new()
notifications:Push('Purchase unavailable. Nothing was charged.',true);modal.Visible=true;gameplayVisible=false;frame()
check(noticeView.root.Visible and noticeView.layout.y+noticeView.layout.height<=56 and not shop.Visible and not questsToggle.Visible,'Shop error hidden or covers modal navigation')
modal.Visible=false;gameplayVisible=true;frame();check(shop.Visible and not questsToggle.Visible,'Modal exit failed to restore grouped navigation')
notifications=Queue.new();selected="Style";frame()
check(shop.Text=="MENU [B]" and shop.Visible and not questsToggle.Visible,'Ordinary HUD retained separate menu buttons')
renderedTab,renderedMenuKey="Style","previous position"
shop.callback();check(modal.Visible and selected=="Style",'Menu toggle did not reopen the last tab')
check(renderedTab=="Style" and renderedMenuKey=="previous position",'Ordinary menu reopen discarded scroll')
shop.callback();check(not modal.Visible,'Menu toggle did not close its group')
selected="Quests";academy.starterGearReady=true
shop.callback();check(modal.Visible and selected=="Style",'Gear-ready Menu reopened Quests instead of Gear')
shop.callback();check(not modal.Visible,'Gear-ready Menu did not close its group')
renderedTab,renderedMenuKey="Style","below the gear upgrade"
shop.callback();check(modal.Visible and selected=="Style" and renderedTab==nil,
 'Gear-ready Menu preserved scroll below the upgrade')
closeMenu();academy.starterGearReady=false
selected="Settings";shop.callback()
check(modal.Visible and selected=="Settings",'Ordinary Menu stopped reopening the last tab')
closeMenu();selected="Style"

local beforePassRefresh=shopRefreshes
renderedTab,renderedMenuKey="Style","previous position"
academy.passesToggle.callback()
check(modal.Visible and selected=='Shop' and shopRefreshes==beforePassRefresh+1 and renderedTab==nil,'Passes did not open and refresh the Shop immediately')
academy.passesToggle.callback();check(modal.Visible and shopRefreshes==beforePassRefresh+1,'Covered Passes toggle reactivated')
shop.callback()
renderedTab,renderedMenuKey="Quests","below ready reward"
selected="Quests";data.quests={a={progress=3}};frame()
questsToggle.callback()
check(modal.Visible and renderedTab==nil and renderedMenuKey==nil,'Ready reward shortcut preserved stale scroll')
shop.callback();data.quests={}
notifications=Queue.new();notifications:Push(samples[3],true,'save');talkTarget={};modal.Visible=false;gameplayVisible=true;frame()
check(not noticeView.root.Visible and questsToggle.Text=='NOTICE' and questsToggle.Visible,'Unavailable notice has no reachable disclosure')
windowFocused=false;frame();check(questsToggle.Text=='QUESTS','Unfocused fallback launcher not restored');windowFocused=true;frame()
questsToggle.callback();frame();check(modal.Visible and noticeView.root.Visible and noticeView.text.Text==samples[3],'Actual NOTICE launcher does not expose full retained warning')
check(noticeView.scroll.Size.Y.Offset>=44,'Modal scroll target below44px')
noticeView.scroll.CanvasPosition=Vector2.new(0,noticeView.contentHeight-noticeView.visibleHeight);frame();check(noticeView.text.Position.Y.Offset+noticeView.text.Size.Y.Offset-noticeView.scroll.CanvasPosition.Y<=noticeView.visibleHeight,'Modal last line remains beneath cue')
modal.Visible=false;viewport=Vector2.new(640,360);frame();check(questsToggle.Text=='QUESTS' and noticeView.root.Visible,'Fitting resize retained fallback disclosure')
notifications:Remove('save');frame();check(questsToggle.Text=='QUESTS' and not questsToggle.Visible,'Recovered notice retained disclosure launcher')
viewport=Vector2.new(455,218);talkTarget=nil
notifications=Queue.new()
notifications:Push('Speech can fire.',false,'voice')
local sparAward='Rookie defeated · +48 XP · +5 coins'
notifications:Push(sparAward,false,'trainingReceipt');frame()
check(questsToggle.Visible and questsToggle.Text=='WIN' and not noticeView.root.Visible,'Hidden training reward did not offer its win shortcut')
questsToggle.callback();frame()
check(modal.Visible and noticeView.root.Visible and noticeView.text.Text==sparAward,'Win shortcut did not show the actual reward first')
closeMenu();notifications=Queue.new()
-- The narrow Hall header shares a strip with notices. Defer only ambient traffic.
academy.hideMap=true;local viewportBefore=viewport
for _,size in ipairs({Vector2.new(455,218),Vector2.new(567,241)})do
 viewport=size;notifications=Queue.new();modal.Visible=false;gameplayVisible=true
 notifications:Push("Fresh Hall welcome",false,"welcome")
 travelStatus="Arrival rehearsal. Safe arrival.";travelNotice()
 local welcome=notifications.active
 shop.callback();gameplayVisible=false
 for i=1,100 do frame() end
 check(modal.Visible and title.Visible and not noticeView.root.Visible and welcome.remaining==4,
  "Routine Hall welcome displaced the menu title or consumed dwell")
 notifications:Push("Shop update",false,"shopResult")
 frame();check(noticeView.root.Visible,"Queued action feedback was trapped behind a hidden welcome")
 -- Urgent warnings still take over immediately, and removing them re-evaluates ambient visibility.
 notifications:Push("Saving unavailable",true,"save")
 frame();check(noticeView.root.Visible and noticeView.message=="Saving unavailable","Hall title suppressed urgent saves")
 notifications:Remove("save");notifications:Remove("welcome");notifications:Remove("shopResult");modal.Visible=false;gameplayVisible=true
 -- The viewport is short enough that the preserved arrival uses the existing shortcut.
 frame()
 check(questsToggle.Visible and questsToggle.Text=="NOTICE","Deferred Hall guidance lost its HUD shortcut")
 questsToggle.callback();gameplayVisible=false;frame()
 check(noticeView.root.Visible and noticeView.message=="Arrival rehearsal. Safe arrival.","NOTICE failed to expose deferred Hall guidance")
 shop.callback()
 check(not academy.menuNoticeRequested,"Closing menu retained explicit notice disclosure")
 gameplayVisible=true;shop.callback();gameplayVisible=false
 travelStatus="Portal reached. This local rehearsal stays in the same place.";travelNotice()
 frame();check(noticeView.root.Visible and noticeView.message==travelStatus,
  "Explicit portal result was deferred like passive arrival")
 travelStatus=nil;travelNotice();frame()
 check(noticeView.message=="","Clearing travel status left an obsolete notice")
 shop.callback()
end
viewport=Vector2.new(567,299);notifications=Queue.new();modal.Visible=false;gameplayVisible=true;touch=false
travelStatus="Arrival rehearsal. Safe arrival.";travelNotice()
frame();check(noticeView.root.Visible,"Safe Hall arrival was hidden")
local arrival=notifications.active;local dwell=arrival.remaining
arenaActive=true
for i=1,20 do frame() end
check(not noticeView.root.Visible and arrival.remaining==dwell,"Passive Hall arrival obscured live combat or consumed unread dwell")
check(questsToggle.Visible and questsToggle.Text=="NOTICE","Hall combat lost its deferred notice shortcut")
questsToggle.callback();gameplayVisible=false;frame()
check(modal.Visible and noticeView.root.Visible and noticeView.message==travelStatus,"Explicit Hall combat notice reveal failed")
shop.callback();gameplayVisible=true;frame()
check(not noticeView.root.Visible,"Closing the notice reopened it over Hall combat")
arenaActive=false;frame();check(noticeView.root.Visible,"Leaving Hall combat did not restore arrival guidance")
arenaActive=true;notifications:Push("Saving unavailable",true,"save");frame()
check(noticeView.root.Visible and noticeView.message=="Saving unavailable","Hall combat suppressed an urgent save notice")
notifications:Remove("save");travelStatus="Portal reached. This local rehearsal stays in the same place.";travelNotice();frame()
check(noticeView.root.Visible and noticeView.message==travelStatus,"Hall combat suppressed portal confirmation")
arenaActive=false;touch=true
academy.hideMap=false;viewport=viewportBefore;modal.Visible=false;gameplayVisible=true
-- The baseline safe HUD measured 567 × 242 even though the camera was taller.
viewport=Vector2.new(567,242);talkTarget={};notifications=Queue.new()
local function checkShortTalk()
 frame()
 local position=talkButton.Position
 local x=position.X.Scale*viewport.X+position.X.Offset
 local y=position.Y.Scale*viewport.Y+position.Y.Offset
 local target={x=x,y=y,width=120,height=44}
 check(talkButton.Visible and y>=0 and y+44<=viewport.Y,'Short phone TALK extends outside the safe HUD')
 local blockers={{x=14,y=12,width=229,height=44},{x=441,y=14,width=112,height=44},
  {x=293,y=viewport.Y-195,width=260,height=96},{x=14,y=64,width=242,height=94}}
 for _,b in ipairs(blockers)do check(not Layout.Overlaps(target,b),'Short phone TALK overlaps an existing HUD control')end
 return x,y
end
-- This section runs across render frames without any layout-pass-only locals.
academy.stackedTouchActions=true
for _,sample in ipairs({{150,44,0},{204,44,0},{205,84,50},{238,84,50}}) do
 local height,width,y=table.unpack(sample)
 viewport=Vector2.new(491,height);frame()
 check(talkButton.Size.X.Offset==width and talkButton.Size.Y.Offset==44 and talkButton.Position.Y.Offset==y,
  'Compact touch TALK did not keep its allocated width across frames')
end
academy.stackedTouchActions=false
viewport=Vector2.new(567,242)
local firstX,firstY=checkShortTalk()
notifications:Push(samples[1],true,'save')
local noticeX,noticeY=checkShortTalk()
check(firstX==noticeX and firstY==noticeY and not noticeView.root.Visible,'Hidden notice moved or covered short phone TALK')
viewport=Vector2.new(567,241);checkShortTalk()
-- Reachable residents must stay clear of health and PvP state without a notice.
for _,sample in ipairs({{567,315,false,120},{480,315,false,117},{480,292,true,95},{480,241,true,95}}) do
 local w,h,tester,expectedWidth=table.unpack(sample)
 data.devAccess=tester;viewport=Vector2.new(w,h);notifications=Queue.new()
 hud=rect(14,64,242,94);zone=rect(14,49,190,14)
 local function assertTalkLane()
  frame()
  local p,s=talkButton.Position,talkButton.Size
  local target={x=p.X.Scale*w+p.X.Offset,y=p.Y.Scale*h+p.Y.Offset,width=s.X.Offset,height=s.Y.Offset}
  check(not Layout.Overlaps(target,{x=14,y=64,width=242,height=94}), 'Touch TALK covered health and progress without a notice')
  check(target.x==251 and target.y==math.min(14,h-239) and target.width==expectedWidth and target.height==44,
   'Touch TALK lost its fallback side lane or target size')
  check(not Layout.Overlaps(target,{x=14,y=49,width=190,height=14}) and target.y+target.height<=h-195,
   'Touch TALK covered PvP status or the Beams control')
 end
 assertTalkLane()
 notifications:Push(samples[1],true,'save');assertTalkLane()
end
data.devAccess=true;hud=rect(14,118,240,88);zone=rect(40,12,240,28)
notifications=Queue.new();viewport=Vector2.new(390,844);frame()
local portrait=talkButton.Position
check(portrait.X.Scale*390+portrait.X.Offset==135 and portrait.Y.Scale*844+portrait.Y.Offset==595,'Portrait TALK moved out of its existing lane')
notifications=Queue.new()
touch=false
viewport=Vector2.new(491,150)
for _,tester in ipairs({true,false})do
 data.devAccess=tester
 frame()
 local position=talkButton.Position
 local size=talkButton.Size
 local target={x=position.X.Scale*491+position.X.Offset,y=position.Y.Scale*150+position.Y.Offset,width=size.X.Offset,height=size.Y.Offset}
 check(not Layout.Overlaps(target,{x=94,y=2,width=64,height=46}),'491 × 150 desktop TALK overlaps Passes')
 check(target.x==251 and target.y==12 and target.width==84 and target.height==34,'Short desktop TALK lost its compact target')
 for _,blocker in ipairs({{x=164,y=2,width=78,height=36},{x=217,y=48,width=260,height=44},{x=365,y=14,width=112,height=44}})do
  check(not Layout.Overlaps(target,blocker),'Short desktop TALK overlaps adjacent controls')
 end
end
data.devAccess=true
for _,width in ipairs({480,491,567}) do
 for _,height in ipairs({168,180,219,220}) do
  local map={available=true,width=90,height=44}
  local layout=Layout.Get(width,height,false,map,true,true)
  local beside=height<220
  local test=beside and {x=width-156,y=14,width=44,height=44}
   or {x=width-126,y=66,width=112,height=44}
  local talk={x=layout.baseTalkX or width/2-60,y=layout.baseTalkY or height-108,width=layout.baseTalkWidth or 120,height=34}
  check(not Layout.Overlaps(talk,test),'Desktop TALK overlaps Test next to MAP')
  check(not Layout.Overlaps(talk,{x=width-104,y=14,width=90,height=44}),'Desktop TALK overlaps MAP')
  check(not Layout.Overlaps(talk,{x=164,y=2,width=78,height=36}),'Desktop TALK overlaps navigation after MAP appears')
  if beside then
   check(talk.y==12 and talk.width>=64,'Short desktop TALK fell onto the status card when MAP appeared')
  end
 end
end
for _,desktop in ipairs({{416,416,14,308},{567,416,165,308},{567,241,251,12},{683,416,281,308},{684,416,282,308},{1280,720,580,612}})do
 local w,h,x,y=table.unpack(desktop)
 hud=rect(14,w<820 and 64 or h-108,242,94)
 tracked=rect(16,w<820 and 160 or 64,290,50)
 academy.guidePanel.Visible=false
 viewport=Vector2.new(w,h);notifications=Queue.new();frame()
 local pos=talkButton.Position
 check(pos.X.Scale*w+pos.X.Offset==x and pos.Y.Scale*h+pos.Y.Offset==y,'Desktop TALK left its clear lane')
 local target={x=x,y=y,width=120,height=34}
 check(not Layout.Overlaps(target,{x=w-274,y=h-102,width=260,height=88}),'Desktop TALK covers combat')
 notifications:Push(samples[1],true,'save');frame()
 check(noticeView.root.Visible,'Desktop TALK hides the save warning')
 check(not Layout.Overlaps(target,noticeView.layout),'Desktop save warning covers TALK')
end
touch=true;notifications=Queue.new()
local compact=Layout.Modal(567,241,true)
check(compact.available and compact.x==20 and compact.x+compact.width<=499 and compact.y+compact.height<=52,
 'Short modal notice overlaps Close or the tab row')
viewport=Vector2.new(567,241);modal.Visible=true;notifications:Push(samples[1],true,'save');frame()
check(not title.Visible and not shop.Visible and noticeView.root.Visible,
 'Short modal hides the warning or leaves header and launch buttons over it')
notifications:Remove('save');frame()
check(title.Visible and not shop.Visible,'Short modal title did not return when the notice cleared')
local v=make();local id={};v:Update('Short',Layout.Modal(1024,720),true,1,16,id);local before=measured
v:Update('Short',Layout.Modal(1280,720),true,2,16,id);check(v.root.Position.X.Offset==320 and measured==before,'Same-size reposition used stale drawn bounds');v:Destroy()
modal.Visible=false;talkTarget=nil;viewport=Vector2.new(640,360);notifications=Queue.new()
receiveQuests({a={progress=3,claimed=false},b={progress=2,claimed=false}});frame();check(questsToggle.Text=='QUESTS 2' and questsToggle.Visible,'Frame erased actual receiver reward count')
notifications:Push('Ordinary notice',false);frame();check(questsToggle.Text=='QUESTS 2','Ordinary notice erased reward count')
viewport=Vector2.new(320,315);talkTarget={};frame();check(questsToggle.Text=='NOTICE','Reward count prevented fallback disclosure')
receiveQuests({a={progress=3,claimed=true},b={progress=2,claimed=false}});frame();check(questsToggle.Text=='NOTICE','Receiver displaced active disclosure')
notifications:Remove(nil);notifications=Queue.new();frame();check(questsToggle.Text=='QUESTS 1','Recovery restored stale reward count')
notifications:Push(samples[1],true,'save');frame();viewport=Vector2.new(640,360);frame();check(questsToggle.Text=='QUESTS 1','Resize restored stale reward count')
receiveQuests({a={progress=3,claimed=true},b={progress=2,claimed=true}});frame();check(questsToggle.Text=='QUESTS' and not questsToggle.Visible,'Claimed reward count persisted')
notifications=Queue.new();academy.shortObjective=true;viewport=Vector2.new(509,162);talkTarget=nil
receiveQuests({a={progress=3,claimed=false}});frame()
check(questsToggle.Text=='REWARD' and questsToggle.Visible,'Compact reward shortcut does not fit its role')
notifications:Push(samples[1],true,'save');frame()
check(questsToggle.Text=='NOTICE' and questsToggle.Visible,'Compact reward displaced the urgent notice')
notifications=Queue.new();academy.shortObjective=false;viewport=Vector2.new(640,360)
receiveQuests({a={progress=3,claimed=true}});frame()
-- Native fractional-height reproduction modeled at the actual allocation boundary.
local oldMeasure=TextService.GetTextSize
TextService.GetTextSize=function(_,text)measured+=1;return {Y=text=='Scroll for full notice' and 16.2000008 or 81.5999985}end
local f=make();local id={};local lane={available=true,x=14,y=66,width=194,height=46}
f:Update('Fractional recovery warning',lane,true,1,14,id)
check(math.floor(f.text.Size.Y.Offset)>=81.5999985,'Fractional body allocation truncates text')
check(math.floor(f.hint.Size.Y.Offset)>=16.2000008,'Fractional header allocation truncates text')
check(f.contentHeight==115 and f.scroll.CanvasSize.Y.Offset==115,'Fractional canvas not derived from rounded text')
f.scroll.CanvasPosition=Vector2.new(0,f.contentHeight-f.visibleHeight)
f:Update('Fractional recovery warning',lane,true,2,14,id)
check(f.text.Position.Y.Offset+82-f.scroll.CanvasPosition.Y<=46,'Fractional last line inaccessible at bottom')
f.text.TextBounds=Vector2.new(178,82.2);f.hint.TextBounds=Vector2.new(178,17.2)
f:Update('Fractional recovery warning',lane,true,3,14,id)
check(f.text.Size.Y.Offset==83 and f.hint.Size.Y.Offset==18,'Subpixel rendered growth ignored')
check(not f:CanAdvance(),'Fractional growth retained old exposure')
local count=measured;f:Update('Fractional recovery warning',lane,true,4,14,id)
check(measured==count,'Rounded measurement causes repeated invalidation')
f:Destroy();TextService.GetTextSize=oldMeasure
print('PASS',n,'notice module/Client assertions; mock text metrics/GUI, no native access claim')
'''.replace('MINI',mini).replace('SAMPLES','{'+','.join(json.dumps(t) for t in texts)+'}').replace('INTEGRATION',integration).replace('HALL_NOTICE_POLICY',client[client.index('do\n local function ambient(entry)'):client.index('\nend',client.index(' function academy.deferArrivalNotice('))+len('\nend')]).replace('TRAVEL_NOTICE',travel_callback).replace('TOGGLE',client[client.index('local function toggleTab('):client.index('local shop=button(')]).replace('MENU_BUTTON',next(x for x in client.splitlines() if x.startswith('local shop=button('))).replace('QUEST_LABEL',client[client.index('local function questLauncherText()'):client.index('local hud=frame(gui,"CompactHUD"')]).replace('RECEIVER_COUNT',client[client.index(' local unclaimed=0'):client.index(' refreshQuestObjects();stats.Text=')]).replace('PASS_BUTTON',client[client.index('academy.passesToggle=button('):client.index('local function questLauncherText()')]).replace('QUEST_BUTTON',client[client.index('local questsToggle=button('):client.index('questsToggle.Visible=false')])
def run(layout,view,body=checks,error=None):
 code=setup+layout+'\nend\nlocal Layout=loadLayout();local function require(k)if k=="layout"then return Layout end;return _G.require(k)end\nlocal function loadView()\n'+view+'\nend\nlocal View=loadView()\n'+body
 # Preserve ordinary file require while mocking just the module dependency.
 code=code.replace('local function require(k)','local realRequire=require;local function require(k)').replace('_G.require(k)','realRequire(k)')
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.notice_',dir=R/'tests',encoding='utf-8',delete=False)as f:f.write(code);q=Path(f.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=20)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(sources['NoticeLayout'],sources['NoticeView'])
if a.negative_controls:
 run(sources['NoticeLayout'].replace('if status and result.available and Layout.Overlaps(result,status) then','if false then',1),
     sources['NoticeView'],error='Landscape notice covers health and progress')
 run(sources['NoticeLayout'].replace('objectiveBottom or 0','0',1),
     sources['NoticeView'],error='Notice below the status card hides the timed quest tracker')
 for old,new,error in [('corner.CornerRadius=UDim.new(0,6)','corner.CornerRadius=UDim.new(0,0)','NoticeCorner missing 6px radius'),('stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border','stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Contextual','NoticeStroke not border-scoped'),('stroke.Transparency=.55','stroke.Transparency=0','NoticeStroke transparency or gold color wrong'),('hint.TextColor3=Color3.fromRGB(255,214,128)','hint.TextColor3=text.TextColor3','Scroll hint lost accent color'),('math.ceil(math.max(measured,self.renderedHeight or 0))','math.max(measured,self.renderedHeight or 0)','Fractional body allocation truncates text'),('math.ceil(math.max(hintHeight,self.renderedHintHeight or 0))','math.max(hintHeight,self.renderedHintHeight or 0)','Fractional header allocation truncates text'),('rendered.Y>self.measuredHeight','rendered.Y>self.measuredHeight+1','Subpixel rendered growth ignored'),('hintBounds.Y>self.measuredHintHeight','hintBounds.Y>self.measuredHintHeight+1','Subpixel rendered growth ignored'),('hint.Parent=scroll','hint.Parent=root','Cue remains outside scroll content'),('self.measuredHintHeight=math.ceil(math.max(hintHeight,self.renderedHintHeight or 0))','self.measuredHintHeight=16','Cue measurement omitted'),('self.renderedHintHeight=hintBounds.Y;self.key=nil','self.renderedHintHeight=nil','Enlarged cue clipped'),('self.visibleHeight=self.panelHeight;','self.visibleHeight=self.panelHeight-16;','Actual scrolling target below44px'),('self.textHeight+self.headerHeight','self.textHeight','Last text line remains under cue'),('hint.Interactable=false','hint.Interactable=true','Cue intercepts scroll input'),('self.atBottom and not self.hover','true and not self.hover','Unseen overflow expires'),('and not self.hover','and true','Hovered notice expires'),('entry~=self.entry','false','Same-text replacement keeps stale exposure'),('and now>=self.pauseUntil','and true','Scrolling charges dwell'),('not fresh and self.atBottom','self.atBottom','New message immediately charged dwell'),('self.visible==true and','true and','Covered notice expires'),('self.root.Position=UDim2.fromOffset(layout.x,layout.y)\n local rendered','local rendered','Same-size reposition used stale drawn bounds')]:
  assert old in sources['NoticeView'];run(sources['NoticeLayout'],sources['NoticeView'].replace(old,new),error=error)
 bad=checks.replace('notifications:Step(dt,noticeView:CanAdvance())','notifications:Step(dt,true)');run(sources['NoticeLayout'],sources['NoticeView'],bad,'Unseen Client overflow expired')
if a.negative_controls:
 for old,new,error in [('h>=44','h>=1','Tiny viewport claimed safe access'),('width-map.width-22','width-14','Notice overlaps actionable target'),('result.talkY=14','result.talkY=height-143','TALK moved into native thumbstick zone')]:
  assert old in sources['NoticeLayout'];run(sources['NoticeLayout'].replace(old,new),sources['NoticeView'],error=error)
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('or questLauncherText()', 'or "QUESTS"'),'Frame erased actual receiver reward count')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace(' and questShortcut~="QUESTS"',''),'Modal exit failed to restore grouped navigation')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('hiddenWin and "WIN" or',''),
     'Hidden training reward did not offer its win shortcut')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('),toggle,gold);shop.TextColor3', '),function()toggleTab("Shop")end,gold);shop.TextColor3'),'Menu toggle did not reopen the last tab')
 for old,new,error in [
     ('elseif academy.starterGearReady then toggleTab("Style",true)', 'elseif academy.starterGearReady then toggleTab(selected)', 'Gear-ready Menu reopened Quests instead of Gear'),
     ('elseif academy.starterGearReady then toggleTab("Style",true)', 'elseif academy.starterGearReady then toggleTab("Style")', 'Gear-ready Menu preserved scroll below the upgrade'),
 ]:
  assert old in checks;run(sources['NoticeLayout'],sources['NoticeView'],checks.replace(old,new),error)
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('toggleTab("Quests",true)','toggleTab("Quests")'),'Ready reward shortcut preserved stale scroll')
 run(sources['NoticeLayout'].replace('local statusOverlap=status and Layout.Overlaps(status,talk)','local statusOverlap=false'),
     sources['NoticeView'],error='Touch TALK covered health and progress without a notice')
 run(sources['NoticeLayout'].replace('sideWidth>=84','sideWidth>=120'),sources['NoticeView'],
     error='Touch TALK covered health and progress without a notice')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('elseif noticeLayout.baseTalkX then','elseif noticeView.visible and noticeLayout.baseTalkX then'),'Short phone TALK extends outside the safe HUD')
 run(sources['NoticeLayout'].replace('talk.x=x;talk.y=','talk.x=navRight-24;talk.y='),sources['NoticeView'],error='Short phone TALK overlaps an existing HUD control')
 for old,new,error in [
     ('noticeVisible and not noticeDeferred','noticeVisible and true','Routine Hall welcome displaced'),
     ('(modal.Visible or arenaActive)','modal.Visible','Passive Hall arrival obscured live combat'),
     ('(not noticeLayout.available or noticeDeferred)','not noticeLayout.available','Hall combat lost its deferred notice shortcut'),
     ('if not ambient(entry) then return false end','if false then return false end','Queued action feedback was trapped'),
     ('academy.menuNoticeRequested=academy.noticeShortcut','academy.menuNoticeRequested=false','NOTICE failed to expose deferred Hall guidance'),
     ('entry.key=="travelArrival"','(entry.key=="travelArrival" or entry.key=="travel")','Explicit portal result was deferred'),
     ('notifications:Remove(key=="travel" and "travelArrival" or "travel")','','Explicit portal result was deferred'),
 ]:
  assert old in checks
  run(sources['NoticeLayout'],sources['NoticeView'],checks.replace(old,new),error)
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('(gameplayVisible or modal.Visible)','gameplayVisible'),'Shop error hidden or covers modal navigation')
 run(sources['NoticeLayout'].replace('if height>=150 and height<318','if height>=156 and height<318'),sources['NoticeView'],error='491 × 150 desktop TALK overlaps Passes')
 run(sources['NoticeLayout'].replace('width-map.width-74','width-map.width-22'),sources['NoticeView'],error='Desktop TALK overlaps Test next to MAP')
 run(sources['NoticeLayout'].replace('topWidth>=(toolsBesideMap and 64 or 72)','topWidth>=72'),sources['NoticeView'],error='Short desktop TALK fell onto the status card when MAP appeared')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('academy.stackedTouchActions and (viewport.Y<205 and 44 or 84) or noticeLayout.baseTalkWidth or 120','splitTalkLane and 44 or stackedActions and 84 or noticeLayout.baseTalkWidth or 120'),'Compact touch TALK did not keep its allocated width across frames')
 run(sources['NoticeLayout'].replace('if not touch and talkVisible then','if false then'),sources['NoticeView'],error='Short desktop TALK lost its compact target')
print('Actual warning lengths:',[len(t)for t in texts])

assert client.index('local nextNotice=notifications:Step(dt,noticeView:CanAdvance())')<client.index('elapsed+=dt;if elapsed<.15'), 'Notice dwell behind throttled gate'
assert 'local notice=notifications:Step(0,false)' in client and 'noticeView:Destroy()' in client
print('PASS source contracts: neutral peek, render cadence, teardown')
