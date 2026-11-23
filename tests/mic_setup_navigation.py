"""Actual client setup/navigation fragments with mocked UI/time; no native/device claim."""
from pathlib import Path
import argparse,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
PATH='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.mic_navigation_',dir=R/'tests',encoding='utf-8',delete=False)as f:f.write(code);q=Path(f.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=20)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:print(out,end='');assert r.returncode==0,out
def line(source,prefix):
 found=[s.strip() for s in source.splitlines() if s.strip().startswith(prefix)];assert len(found)==1,(prefix,len(found));return found[0]
def baseline():
 s=subprocess.check_output(['git','show','b60dada:'+PATH],cwd=R,text=True,encoding='utf-8')
 code="""local mic={ready=true};local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false};local micPanel={Visible=false}
local GuiService={MenuIsOpen=false};local originalTouchControls=true;local academy={testLauncherBlocked=false};local miniMapAvailable=true;local windowFocused=true;local toast={Visible=false};local data={devAccess=false}
local function frame()
"""+line(s,'micPanel.Visible=')+'\n'+line(s,'local gameplayVisible=')+'\n'+line(s,'local showTouchControls=')+'\n'+line(s,'local miniVisible=')+"""
return gameplayVisible,showTouchControls,miniVisible end
local gameplay,touch,mini=frame();assert(not micPanel.Visible and gameplay and touch and mini)
mic.ready=false;gameplay,touch,mini=frame();assert(micPanel.Visible and not gameplay and not touch and not mini)
micPanel.Visible=false;frame();assert(micPanel.Visible)
print('REPRO readiness loss reopens setup every frame and hides navigation/touch/minimap')
mic.ready=true;toast.Visible=true;gameplay,touch,mini=frame();assert(gameplay and not mini)
print('REPRO notification hides otherwise available minimap; no native rendering claim')
"""
 run(code)

def current(source):
 blocked=source[source.index('local function blocked()'):source.index('local function beginCapture(')]
 touch_update = next(row.strip() for row in source.splitlines() if 'lastTouchControls=showTouchControls;' in row)
 frame='\n'.join((line(source,'local gameplayVisible='),line(source,'local showTouchControls='),touch_update,line(source,'local miniVisible=')))+'\n'+line(source[source.index('local miniVisible='):],'if miniMapButton then miniMapButton.Visible=')
 return r"""
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local workspace={GetServerTimeNow=function()return 100 end};local attrs={};local humanoid={Health=100,PlatformStand=false}
local p={Character={FindFirstChildOfClass=function()return humanoid end},GetAttribute=function(_,k)return attrs[k]end}
local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false}
local mic={ready=false};local data={voiceEligible=false,devAccess=false};local GuiService={MenuIsOpen=false};local focus
local UIS={TouchEnabled=true,GetFocusedTextBox=function()return focus end};GuiService.TouchControlsEnabled=true;local originalTouchControls=true;local lastTouchControls
local academy={testLauncherBlocked=false};local miniMapAvailable=true;local windowFocused=true;local toast={Visible=false};local miniMapButton={}
"""+blocked+'\nlocal function frame()\n'+frame+'\nreturn gameplayVisible,showTouchControls,miniVisible end\n'+r"""
for _,ready in ipairs({false,true})do for _,eligible in ipairs({false,true})do
 mic.ready=ready;data.voiceEligible=eligible
 for _,access in ipairs({false,true})do for _,notice in ipairs({false,true})do
  data.devAccess=access;toast.Visible=notice
  local g,t,m=frame();check(g and t and m and not blocked(),'Microphone/access/notice trapped navigation')
  check(beamBlocked()==(not ready or not eligible),'Beam prerequisite changed')
 end end
end end
mic.ready=false;data.voiceEligible=true;check(beamBlocked(),'Unready mic allowed beam')
mic.ready=true;data.voiceEligible=false;check(beamBlocked(),'Ineligible mic allowed beam')
mic.ready=true;data.voiceEligible=true
for _,panel in ipairs({modal,conversationPanel})do
 panel.Visible=true;local g,t,m=frame();check(not g and not t and not m and blocked() and beamBlocked(),'Open panel leaked gameplay');panel.Visible=false
end
devPanel.Visible=true;local g,t,m=frame();check(g and t and m and blocked() and beamBlocked(),'Open devPanel hid HUD/minimap or leaked attack');devPanel.Visible=false
GuiService.MenuIsOpen=true;local g,t,m=frame();check(not g and not t and not m and blocked(),'Roblox menu leaked gameplay');GuiService.MenuIsOpen=false
originalTouchControls=false;g,t,m=frame();check(not t,'Overrode user touch setting');originalTouchControls=true
modal.Visible=true;frame();check(not GuiService.TouchControlsEnabled,'Touch menu did not hide stock controls')
modal.Visible=false;frame();check(GuiService.TouchControlsEnabled,'Touch menu did not restore stock controls')
UIS.TouchEnabled=false
for _,panel in ipairs({modal,conversationPanel})do
 panel.Visible=true;frame();check(GuiService.TouchControlsEnabled,'Panel changed stock controls without a touchscreen')
 panel.Visible=false;frame();check(GuiService.TouchControlsEnabled,'Panel close changed stock controls without a touchscreen')
end
GuiService.TouchControlsEnabled=false;frame()
check(not GuiService.TouchControlsEnabled,'HUD overwrote another owner without a touchscreen')
UIS.TouchEnabled=true;frame()

windowFocused=false;g,t,m=frame();check(not m,'Unfocused minimap stayed visible');windowFocused=true
focus={};check(blocked(),'Typing did not block actions');focus=nil
humanoid.PlatformStand=true;check(blocked(),'Ragdoll allowed actions');humanoid.PlatformStand=false
humanoid.Health=0;check(blocked(),'Dead character allowed actions');humanoid.Health=100
for _,key in ipairs({'ProtectionEnds','DodgeEnds','KnockdownEnds'})do attrs[key]=101;check(beamBlocked(),'Protection state allowed beam');attrs[key]=nil end
print('PASS',checks,'actual navigation/beam prerequisite fragments; synthetic GUI only')
"""
if args.baseline:baseline()
else:
 source=(R/PATH).read_text();assert 'micPanel' not in source and 'openMicSetup' not in source and 'mic:Calibrate()' not in source,'Retired setup wall returned'
 run(current(source))
 if args.negative_controls:
  mutants=[('local gameplayVisible=not GuiService.MenuIsOpen','local gameplayVisible=mic.ready and not GuiService.MenuIsOpen','Microphone/access/notice trapped navigation'),('local miniVisible=miniMapAvailable and gameplayVisible and windowFocused','local miniVisible=miniMapAvailable and gameplayVisible and windowFocused and not toast.Visible','Microphone/access/notice trapped navigation'),('return not mic.ready or data.voiceEligible~=true or blocked()','return data.voiceEligible~=true or blocked()','Beam prerequisite changed'),('return not mic.ready or data.voiceEligible~=true or blocked()','return not mic.ready or blocked()','Beam prerequisite changed')]
  mutants.append(('if UIS.TouchEnabled and GuiService.TouchControlsEnabled~=showTouchControls then',
                   'if GuiService.TouchControlsEnabled~=showTouchControls then',
                   'Panel changed stock controls without a touchscreen'))
  for old,new,message in mutants:
   assert source.count(old)==1,old;run(current(source.replace(old,new)),message)
