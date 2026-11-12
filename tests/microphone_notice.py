"""Actual microphone setup/settings text and render mechanics with synthetic text metrics.
No policy enforcement, microphone capture or native text-fit claim.
"""
from pathlib import Path
import argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
name='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
src=subprocess.check_output(['git','show','899b0b8:'+name],cwd=ROOT,text=True,encoding='utf-8') if args.baseline else (ROOT/name).read_text(encoding='utf-8')
setup_line=next(line for line in src.splitlines() if line.startswith('label(micPanel,sustainedControl and'))
info_start=src.index('local function info(')
info=src[info_start:src.index('\nscript.Destroying:Connect(',info_start)]
a=src.index('  title.Text="SETTINGS & CONTROLS"');b=src.index('\n end\n -- Restore only after AutomaticCanvasSize',a);settings=src[a:b]
a=src.index(' local key=menuKey()',src.index('render=function()'));b=src.index(' if selected=="Shop" then',a);prefix=src[a:b]
a=src.index(' -- Restore only after AutomaticCanvasSize');b=src.index('\nfor i,name in ipairs',a);tail=src[a:b]
a=b+1;b=src.index('\nlocal conversationNPC',a);tabs_source=src[a:b]
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local UDim2={new=function(xs,xo,ys,yo)return {X={Scale=xs or 0,Offset=xo or 0},Y={Scale=ys or 0,Offset=yo or 0}}end,fromOffset=function(x,y)return {X={Offset=x},Y={Offset=y}}end}
local Vector2={new=function(x,y)return {X=x,Y=y}end,zero={X=0,Y=0}}
local Color3={fromRGB=function(...)return {...}end};local Enum={Font={GothamMedium=1}}
local gui={AbsoluteSize={X=390}};local micPanel={};local muted={};local gold={};local panel={}
local content={children={},CanvasPosition={X=0,Y=0},AbsoluteCanvasSize={Y=1500},AbsoluteWindowSize={Y=400}}
function content:GetChildren()return self.children end
local cards,labels,buttons={}, {}, {};local destructions=0
local function card(height)
 local c={height=height,labels={}};function c:IsA(kind)return kind=='GuiObject'end;function c:Destroy()self.destroyed=true;destructions+=1 end
 table.insert(cards,c);table.insert(content.children,c);return c
end
local function label(parent,text,size,pos,font,color)
 local t={Text=text,Size=size,Position=pos};table.insert(labels,t);if parent.labels then table.insert(parent.labels,t)end;return t
end
local function button(parent,name,text,size,pos,callback)local b={Text=text,call=callback};buttons[name]=b;return b end
local measured={}
local TextService={GetTextSize=function(_,text,size,font,dimensions)
 local height=math.ceil(#text*7.5/math.max(1,dimensions.X))*18;measured[text]=height;return {Y=height}
end}
local sustainedControl;local sustainedRules={MaxDuration=4,Cooldown=5};local UIS={TouchEnabled=false}
local Config={DodgeCooldown=3,SprintDuration=5,SprintRecovery=4,SprintRegenDelay=2}
local mic={Calibrate=function(self)self.count=(self.count or 0)+1 end};local modal={Visible=true}
local cancellations,sprints=0,0;local function cancelCapture()cancellations+=1 end;local function setSprint()sprints+=1 end
local action={FireServer=function()error('Rendering safety notice must not send a server action')end}
local data={settings={volume=.5,reducedShake=false}}
local attackAudio={level='NORMAL',SetLevel=function(self,v)self.level=v end}
local gameplayAudio={enabled=true,SetEnabled=function(self,v)self.enabled=v end};local gameplayAudioSettings={Ready=function()return true end}
local title,subtitle={},{};local tabs={};local ShopUI={Clear=function()end};local mapDot
local selected='Settings';local renderedMenuKey,renderedTab;local renderRevision=0;local narrow;local render
local function menuKey()return selected..':'..gui.AbsoluteSize.X..':'..tostring(sustainedControl)..':'..tostring(UIS.TouchEnabled)end
local pending={};local task={spawn=function(fn)table.insert(pending,fn)end};local Run={Heartbeat={Wait=function()end}}
local function flush()for _,fn in ipairs(pending)do fn()end;pending={}end
local function setupNotice()
 labels={}
'''
after_setup=r'''
 return labels[1]
end
'''
close_helper=src[src.index('local function closeMenu()'):src.index('button(modal,"Close","X"')] if 'local function closeMenu()' in src else ''
open_helper=src[src.index('openMicSetup=function()'):src.index('local talkTarget')] if 'openMicSetup=function()' in src else ''
before_render='\n'+close_helper+'\nlocal openMicSetup;local micSetupOpen=false\n'+open_helper+'\nrender=function()\n'
after_prefix='\n if selected=="Settings" then\n'
after_settings='\n end\n'
checks=r'''
for _,automatic in ipairs({false,true})do
 sustainedControl=automatic and {SetArmed=function(self,v)self.armed=v end} or nil
 local notice=setupNotice()
 check(string.find(notice.Text,'Avoid profanity.',1,true)~=nil,'Setup profanity warning missing')
 check(string.find(notice.Text,'Roblox records and moderates voice.',1,true)~=nil,'Setup recording/moderation warning missing')
 check(notice.Size.Y.Offset==50 and notice.Position.Y.Offset==146,'Setup warning moved existing controls')
 if automatic then check(string.find(notice.Text,'OFF does not mute voice.',1,true)~=nil,'Setup confuses attack off and voice mute')
 else check(string.find(notice.Text,'Roblox voice access required.',1,true)~=nil,'Legacy access notice missing')end
 for _,width in ipairs({320,390,844,1280})do
  for _,touch in ipairs({false,true})do
   gui.AbsoluteSize.X=width;UIS.TouchEnabled=touch;selected='Settings';renderedMenuKey=nil;cards={};content.children={};labels={};buttons={};modal.Visible=true
   render();flush()
   local safety,found
   for i,c in ipairs(cards)do if c.labels[1] and string.find(c.labels[1].Text,'VOICE SAFETY',1,true) then check(not safety,'Duplicate safety card');safety=c;found=i end end
   check(safety~=nil,'VoiceSafety card missing');check(found==2,'Voice safety not directly after attack help')
   local text=safety.labels[1].Text
   for _,phrase in ipairs({'VOICE SAFETY','Avoid profanity.','rating and settings','harassment, threats and hate speech','may restrict voice or your account','Roblox records voice for moderation','volume, not words','Stopping attacks does not mute voice','Report Abuse'})do check(string.find(text,phrase,1,true)~=nil,'Safety notice missing required distinction: '..phrase)end
   check(not string.find(text,'automatically banned',1,true) and not string.find(text,'we record',1,true),'Safety notice invents enforcement or recording')
   check(safety.height>=measured[text]+24,'Safety card fails measured height growth')
   check(safety.labels[1].Size.Y.Scale==1 and safety.labels[1].Size.Y.Offset==-20,'Safety label no longer fills dynamic card')
   for _,id in ipairs({'Recalibrate','Volume','AttackAudio','GameplayAudio','ReducedFX'})do check(buttons[id]~=nil,'Existing settings control removed')end
   local old=#cards;render();flush();check(#cards==old,'Unchanged menu duplicated safety notice')
   content.CanvasPosition={X=0,Y=220};renderedMenuKey=nil;render();flush();check(content.CanvasPosition.Y==220,'Same-tab rebuild lost scroll')
   selected='Map';render();flush();selected='Settings';render();flush();check(content.CanvasPosition.Y==0,'New tab retained stale scroll')
   local before=mic.count or 0;buttons.Recalibrate.call();check(mic.count==before+1 and not modal.Visible,'Recalibration callback changed')
   if automatic then check(sustainedControl.armed==false,'Recalibration failed to disarm')end
  end
 end
end
-- With the menu visible, the preserved tab callback selects Settings. Hidden callbacks are tested in shop_modal_lifecycle.py.
buttons={}
__TABS__
modal.Visible=true;selected='Map';buttons.Settings.call();flush();check(selected=='Settings','Settings tab cannot open notice')
check(destructions>0,'Rerender did not dispose old cards')
print('PASS '..checks..' actual microphone notice/settings/render assertions; mocked text metrics only')
'''
def assemble(setup_text=setup_line,settings_text=settings,info_text=info):return setup+setup_text+after_setup+info_text+before_render+prefix+after_prefix+settings_text+after_settings+tail+checks.replace('__TABS__',tabs_source)
code=assemble()
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
if args.baseline:run(code,'Setup profanity warning missing')
else:
 run(code)
 if args.negative_controls:
  cases=[(assemble(settings_text=settings.replace('VOICE SAFETY','OTHER NOTICE')),'VoiceSafety card missing'),(assemble(settings_text=settings.replace('Stopping attacks does not mute voice','Stopping attacks mutes voice')),'Safety notice missing required distinction: Stopping attacks does not mute voice'),(assemble(info_text=info.replace('math.max(height or 70,fit)','height or 70')),'Safety card fails measured height growth'),(assemble(setup_text=setup_line.replace('OFF does not mute voice.','OFF mutes voice.')),'Setup confuses attack off and voice mute')]
  for changed,message in cases:
   assert changed!=code,'Mutation missing: '+message
   run(changed,message)

if not args.baseline:
 content_line=next(line for line in src.splitlines() if line.startswith('local content=Instance.new("ScrollingFrame")'))
 assert 'content.AutomaticCanvasSize=Enum.AutomaticSize.Y' in content_line and 'content.CanvasSize=UDim2.new()' in content_line,'Settings no longer auto-scrolls'
 label_source=src[src.index('local function label('):src.index('local function button(')]
 assert 'l.TextWrapped=true' in label_source,'Setup label no longer wraps'
 assert 'No recordings are saved by this game' not in setup_line and 'This game saves no recordings' not in setup_line,'Unqualified recording guarantee returned'
 print('PASS 3 source contracts: wrapping, scrolling and no game-wide recording guarantee')
