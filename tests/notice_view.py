"""Real NoticeView/Layout/Queue and Client notice block; synthetic text metrics and GUI."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
paths=['NoticeLayout','NoticeView'];sources={n:(R/f'src/StarterPlayer/StarterPlayerScripts/{n}.luau').read_text(encoding='utf-8-sig') for n in paths}
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();city=(R/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text();mini=city[city.index('function CityMap.MiniLayout('):city.index('function CityMap.MiniUpdate(')]
integration=client[client.index(' -- Pause queue time while covered,'):client.index(' beamScreenFeedback:Step(',client.index(' -- Pause queue time while covered,'))]
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
local UDim2={new=function(xs,x,ys,y)return {X={Scale=xs,Offset=x},Y={Scale=ys,Offset=y}}end}
function UDim2.fromOffset(x,y)return UDim2.new(0,x,0,y)end
local Enum={ScrollingDirection={Y=1},TextYAlignment={Top=1}}
local function signal()local s={};function s:Connect(fn)local c={fn=fn,on=true};function c:Disconnect()self.on=false end;table.insert(self,c);return c end;function s:Fire()for _,c in ipairs(self)do if c.on then c.fn()end end end;return s end
local instances=0;local Instance={new=function(kind)instances+=1;local x={Visible=true,CanvasPosition=Vector2.zero,AbsolutePosition=Vector2.zero,AbsoluteSize=Vector2.zero,MouseEnter=signal(),MouseLeave=signal(),InputBegan=signal(),changed=signal()};function x:GetPropertyChangedSignal()return self.changed end;function x:Destroy()self.dead=true;self.Parent=nil end;return x end}
local TextService={GetTextSize=function(_,text,size,font,bounds)measured+=1;return {Y=math.ceil(#text*size*.55/bounds.X)*18}end}
local game={GetService=function()return TextService end};local script={Parent={NoticeLayout='layout'}}
local function loadLayout()
'''
checks=r'''
local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local function make()
 local text=Instance.new('TextLabel');text.Text='';text.Font='Gotham';local v=View.new({},text);return v
end
local CityMap={aspectRatio=1.2}
MINI
local samples=SAMPLES
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
    check(v.textHeight-v.scroll.CanvasPosition.Y<=v.visibleHeight-16,'Last text line remains under cue')
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
-- Execute the actual per-frame Client queue/layout block with real helper/queue.
local NoticeLayout=Layout;local noticeView=make();local notifications=Queue.new();local viewport=Vector2.new(320,315);local touch=true;local data={devAccess=true}
local modal={Visible=false};local shop={Visible=true};local talkTarget
local selected='Shop';local function closeMenu()modal.Visible=false end;local function render()end
local devPanel={Visible=false};local closeConversation;local action={FireServer=function()end}
TOGGLE
local top={};local function button(_,_,_,_,_,fn)return {Visible=true,callback=fn}end
QUEST_BUTTON
local Config={Quests={{id='a',goal=3},{id='b',goal=2}}};data.quests={}
local gold,white={},{}
QUEST_LABEL
local function receiveQuests(quests)
 data.quests=quests
RECEIVER_COUNT
end
local gameplayVisible=true;local windowFocused=true;local GuiService={MenuIsOpen=false};local gui={AbsolutePosition=Vector2.zero};local dt=.05
local function rect(x,y,w,h)return {Visible=true,AbsolutePosition=Vector2.new(x,y),AbsoluteSize=Vector2.new(w,h),Position={}}end
local talkButton=rect(100,66,120,44);local hud=rect(14,118,240,88);local tracked=rect(16,214,290,50);local zone=rect(40,12,240,28);local saveNotice=rect(35,40,250,28)
local function frame()
 local notice=notifications:Step(0,false)
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
modal.Visible=false;gameplayVisible=true;frame();check(shop.Visible and questsToggle.Visible,'Modal notice lost navigation launchers')
notifications=Queue.new();notifications:Push(samples[3],true,'save');talkTarget={};modal.Visible=false;gameplayVisible=true;frame()
check(not noticeView.root.Visible and questsToggle.Text=='NOTICE' and questsToggle.Visible,'Unavailable notice has no reachable disclosure')
windowFocused=false;frame();check(questsToggle.Text=='QUESTS','Unfocused fallback launcher not restored');windowFocused=true;frame()
questsToggle.callback();frame();check(modal.Visible and noticeView.root.Visible and noticeView.text.Text==samples[3],'Actual NOTICE launcher does not expose full retained warning')
check(noticeView.scroll.Size.Y.Offset>=44,'Modal scroll target below44px')
noticeView.scroll.CanvasPosition=Vector2.new(0,noticeView.contentHeight-noticeView.visibleHeight);frame();check(noticeView.textHeight-noticeView.scroll.CanvasPosition.Y<=noticeView.visibleHeight-16,'Modal last line remains beneath cue')
modal.Visible=false;viewport=Vector2.new(640,360);frame();check(questsToggle.Text=='QUESTS' and noticeView.root.Visible,'Fitting resize retained fallback disclosure')
notifications:Remove('save');frame();check(questsToggle.Text=='QUESTS' and questsToggle.Visible,'Recovered notice retained disclosure launcher')
local v=make();local id={};v:Update('Short',Layout.Modal(1024,720),true,1,16,id);local before=measured
v:Update('Short',Layout.Modal(1280,720),true,2,16,id);check(v.root.Position.X.Offset==320 and measured==before,'Same-size reposition used stale drawn bounds');v:Destroy()
modal.Visible=false;talkTarget=nil;viewport=Vector2.new(640,360);notifications=Queue.new()
receiveQuests({a={progress=3,claimed=false},b={progress=2,claimed=false}});frame();check(questsToggle.Text=='QUESTS 2','Frame erased actual receiver reward count')
notifications:Push('Ordinary notice',false);frame();check(questsToggle.Text=='QUESTS 2','Ordinary notice erased reward count')
viewport=Vector2.new(320,315);talkTarget={};frame();check(questsToggle.Text=='NOTICE','Reward count prevented fallback disclosure')
receiveQuests({a={progress=3,claimed=true},b={progress=2,claimed=false}});frame();check(questsToggle.Text=='NOTICE','Receiver displaced active disclosure')
notifications:Remove(nil);notifications=Queue.new();frame();check(questsToggle.Text=='QUESTS 1','Recovery restored stale reward count')
notifications:Push(samples[1],true,'save');frame();viewport=Vector2.new(640,360);frame();check(questsToggle.Text=='QUESTS 1','Resize restored stale reward count')
receiveQuests({a={progress=3,claimed=true},b={progress=2,claimed=true}});frame();check(questsToggle.Text=='QUESTS','Claimed reward count persisted')
print('PASS',n,'notice module/Client assertions; mock text metrics/GUI, no native access claim')
'''.replace('MINI',mini).replace('SAMPLES','{'+','.join(json.dumps(t) for t in texts)+'}').replace('INTEGRATION',integration).replace('TOGGLE',client[client.index('local function toggleTab('):client.index('local function toggle()')]).replace('QUEST_LABEL',client[client.index('local function questLauncherText()'):client.index('local hud=frame(gui,"CompactHUD"')]).replace('RECEIVER_COUNT',client[client.index(' local unclaimed=0'):client.index(' refreshQuestObjects();stats.Text=')]).replace('QUEST_BUTTON',next(x for x in client.splitlines() if x.startswith('local questsToggle=button(')))
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
 for old,new,error in [('self.visibleHeight=self.panelHeight;','self.visibleHeight=self.panelHeight-16;','Actual scrolling target below44px'),('self.textHeight+(self.overflow and 16 or 0)','self.textHeight','Last text line remains under cue'),('hint.Interactable=false','hint.Interactable=true','Cue intercepts scroll input'),('self.atBottom and not self.hover','true and not self.hover','Unseen overflow expires'),('and not self.hover','and true','Hovered notice expires'),('entry~=self.entry','false','Same-text replacement keeps stale exposure'),('and now>=self.pauseUntil','and true','Scrolling charges dwell'),('not fresh and self.atBottom','self.atBottom','New message immediately charged dwell'),('self.visible==true and','true and','Covered notice expires'),('self.root.Position=UDim2.fromOffset(layout.x,layout.y)\n local rendered','local rendered','Same-size reposition used stale drawn bounds')]:
  assert old in sources['NoticeView'];run(sources['NoticeLayout'],sources['NoticeView'].replace(old,new),error=error)
 bad=checks.replace('notifications:Step(dt,noticeView:CanAdvance())','notifications:Step(dt,true)');run(sources['NoticeLayout'],sources['NoticeView'],bad,'Unseen Client overflow expired')
if a.negative_controls:
 for old,new,error in [('h>=44','h>=1','Tiny viewport claimed safe access'),('width-map.width-22','width-14','Notice overlaps actionable target'),('result.talkY=14','result.talkY=height-143','TALK moved into native thumbstick zone')]:
  assert old in sources['NoticeLayout'];run(sources['NoticeLayout'].replace(old,new),sources['NoticeView'],error=error)
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('or questLauncherText()', 'or "QUESTS"'),'Frame erased actual receiver reward count')
 run(sources['NoticeLayout'],sources['NoticeView'],checks.replace('(gameplayVisible or modal.Visible)','gameplayVisible'),'Shop error hidden or covers modal navigation')
print('Actual warning lengths:',[len(t)for t in texts])

assert client.index('local nextNotice=notifications:Step(dt,noticeView:CanAdvance())')<client.index('elapsed+=dt;if elapsed<.15'), 'Notice dwell behind throttled gate'
assert 'local notice=notifications:Step(0,false)' in client and 'noticeView:Destroy()' in client
print('PASS source contracts: neutral peek, render cadence, teardown')
