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
local GuiService={MenuIsOpen=false};local originalTouchControls=true;local miniMapAvailable=true;local windowFocused=true;local toast={Visible=false};local data={devAccess=false}
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
 close=source[source.index('local micSetupOpen=true'):source.index('button(micPanel,"Calibrate"')]
 panel_actions='\n'.join(line(source, 'button(micPanel,"'+name+'"') for name in ('Calibrate','Retry'))+'\n'
 opening=source[source.index('openMicSetup=function()'):source.index('local talkTarget',source.index('openMicSetup=function()'))]
 settings=source[source.index('  local setupCard=card(58)'):source.index('\n  info("Changed microphone',source.index('  local setupCard=card(58)'))]
 toggle=source[source.index('local function toggleVoice()'):source.index('local function screamToggleLabel(')]
 observe=source[source.index('local function observeVoiceEligibility('):source.index('local function toggleVoice()')]
 step=source[source.index(' if sustainedControl then\n  if data.voiceStatus'):source.index(' if captureSource and beamBlocked()')]
 vis=source[source.index(' -- Readiness recovery may finish setup;'):source.index(' local calibrationActive=',source.index(' -- Readiness recovery may finish setup;'))]
 cancel= (R/'src/StarterPlayer/StarterPlayerScripts/Microphone.luau').read_text();cancel=cancel[cancel.index('function Microphone:CancelCalibration()'):cancel.index('function Microphone:FindInput()')].replace('function Microphone:','function mic:')
 setup=r"""
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local now=100;local os={clock=function()return now end};local workspace={GetServerTimeNow=function()return now end}
local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false};local micPanel={Visible=false}
local originalTouchControls=true;local GuiService={MenuIsOpen=false};local textFocus;local UIS={GetFocusedTextBox=function()return textFocus end}
local attrs={};local humanoid={Health=100,PlatformStand=false};local p={Character={FindFirstChildOfClass=function()return humanoid end},GetAttribute=function(_,k)return attrs[k]end}
local data={voiceEligible=false,voiceStatus='denied',micReady=false,devAccess=false};local windowFocused=true;local voiceAccessInterrupted=false
local lockController={Clear=function()end}
local mic={ready=false,power=0,phase=nil,model={calibrated=false},calibrations=0}
function mic:Calibrate()self.ready=false;self.phase='quiet';self.phaseStarted=now;self.calibrations+=1 end
local buttons={};local function button(_,name,_,_,_,callback)local b={callback=callback};buttons[name]=b;return b end
local UDim2={new=function()return {}end,fromOffset=function()return {}end};local function card()return {}end
local miniMapAvailable=true;local toast={Visible=false};local miniMapButton={};local controls={};local hud={}
local function closeMenu()modal.Visible=false end;local function closeConversation()conversationPanel.Visible=false end
local sprint=false;local function setSprint(v)sprint=v end
local sent={};local function send(v,arg)table.insert(sent,v);if v=='SustainedBegin'then attrs.SustainedActive=true;attrs.SustainedSequence=arg.sequence elseif v=='SustainedStop'then attrs.SustainedActive=false end end
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls');local Gate=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local sustainedControl=Controls.new(Gate.new(),send,function()return 1 end)
local function cancelCapture()sustainedControl:Cancel()end
local function notify()end;local function voiceEligibilityHint()return 'Unavailable' end
local openMicSetup,closeMicSetup;local clientDestroyed=false
"""
 frame='local function frame()\n local dt=.05;now+=dt;local alive=humanoid.Health>0;local voiceCooldown,voiceActive\n'+vis+step+line(source,'local gameplayVisible=')+'\n'+line(source,'local showTouchControls=')+'\n'+line(source,'if GuiService.TouchControlsEnabled~=showTouchControls')+'\n'+line(source,'local miniVisible=')+'\n'+line(source,'miniMapButton.Visible=')+'\nreturn gameplayVisible,showTouchControls,miniVisible end\n'
 return setup+cancel+blocked+close+panel_actions+opening+settings+observe+toggle+frame+r"""
local function advance(n)for _=1,n do frame()end end
local g,t,m=frame();check(micPanel.Visible and not g and not t,'Initial setup missing')
buttons.Close.callback();g,t,m=frame();check(not micPanel.Visible and g and t and m and not blocked() and beamBlocked(),'Dismissed nonvoice navigation remains blocked')
data.voiceEligible=true;check(beamBlocked(),'Unready mic allowed beam');data.voiceEligible=false
advance(120);check(not micPanel.Visible and #sent==0,'Closed setup reappeared or ineligible attack sent')
buttons.OpenMicSetup.callback();frame();check(micPanel.Visible and blocked() and beamBlocked(),'Explicit setup did not open/block gameplay')
mic.phase='quiet';mic.quiet={1};mic.spoken={2};buttons.Close.callback();frame();check(mic.phase==nil and #mic.quiet==0 and #mic.spoken==0 and not mic.ready,'Close retained unfinished calibration')
mic.ready=true;mic.model.calibrated=true;data.micReady=true;data.voiceEligible=true;data.voiceStatus='eligible';frame()
check(not micPanel.Visible,'Successful readiness transition did not close setup')
buttons.OpenMicSetup.callback();advance(20);check(micPanel.Visible and mic.ready and mic.model.calibrated,'Explicit ready setup immediately autoclosed or erased calibration')
buttons.Close.callback();frame();check(mic.ready and mic.model.calibrated and not micPanel.Visible,'Close erased completed calibration')
mic.ready=false;data.micReady=false;observeVoiceEligibility({voiceEligible=false,voiceStatus='denied'});data.voiceEligible=false;data.voiceStatus='denied';advance(120)
g,t,m=frame();check(g and t and m and not micPanel.Visible and not blocked() and beamBlocked(),'Readiness loss trapped ordinary navigation')
local before=#sent;mic.power=1;toggleVoice();advance(40);check(not sustainedControl.armed and #sent==before,'Ineligible power/toggle began attack')
mic.ready=true;data.micReady=true;data.voiceEligible=true;data.voiceStatus='eligible';frame();check(not sustainedControl.armed,'Recovery silently rearmed')
mic.power=0;toggleVoice();advance(12);mic.power=.8;advance(12);check(sustainedControl.attack~=nil,'Manual rearm did not start synthetic attack')
toggleVoice();g,t,m=frame();check(not sustainedControl.armed and not sustainedControl.attack and g and t and m,'OFF hid navigation or retained attack')
for _,access in ipairs({false,true})do
 data.devAccess=access;toast.Visible=true;g,t,m=frame();check(m,'Toast or test access hid minimap')
end
for _,status in ipairs({'checking','denied','unavailable'})do
 data.voiceStatus=status;data.voiceEligible=false;observeVoiceEligibility(data);g,t,m=frame();check(g and t and m and not micPanel.Visible and beamBlocked(),'Voice status hid navigation: '..status)
end
for _,panel in ipairs({modal,devPanel,conversationPanel})do
 panel.Visible=true;g,t,m=frame();check(not g and not t and not m and blocked(),'Open panel leaked gameplay navigation');panel.Visible=false
end
GuiService.MenuIsOpen=true;g,t,m=frame();check(not g and not t and not m and blocked(),'Roblox menu leaked gameplay');GuiService.MenuIsOpen=false
originalTouchControls=false;g,t,m=frame();check(not t,'Overrode user touch-control setting');originalTouchControls=true
windowFocused=false;g,t,m=frame();check(not m,'Unfocused minimap stayed visible');windowFocused=true
textFocus={};check(blocked(),'Typing did not block gameplay');textFocus=nil
humanoid.PlatformStand=true;check(blocked(),'Ragdoll allowed action');humanoid.PlatformStand=false
modal.Visible=true;conversationPanel.Visible=true;devPanel.Visible=true;sprint=true
buttons.Recalibrate.callback();frame();check(micPanel.Visible and not modal.Visible and not conversationPanel.Visible and not devPanel.Visible and mic.phase=='quiet' and not sprint and not sustainedControl.armed and mic.calibrations==1,'Recalibrate did not open setup safely')
buttons.Close.callback();advance(120);check(mic.phase==nil and not micPanel.Visible,'Canceled recalibration reopened')
-- Use the actual Calibrate method for the destructive retained-callback case.
local Power={new=function()return {calibrated=false}end}
function mic:FindInput()return {Muted=false,Active=true}end
function mic:Cancel()end
mic.eligible=true;mic.checkPending=false
ACTUAL_CALIBRATE
local accessChecks=0;function mic:Check()accessChecks+=1 end
mic.ready=true;mic.model={calibrated=true};mic.phase=nil
buttons.Close.callback();local retainedCalibrate=buttons.Calibrate.callback;local retainedRetry=buttons.Retry.callback
retainedCalibrate();check(mic.ready and mic.model.calibrated and mic.phase==nil,'Hidden Calibrate erased completed readiness')
retainedRetry();check(accessChecks==0,'Hidden Retry started access check')
buttons.OpenMicSetup.callback();clientDestroyed=true
retainedCalibrate();check(mic.ready and mic.model.calibrated and mic.phase==nil,'Destroyed Calibrate erased readiness')
retainedRetry();check(accessChecks==0,'Destroyed Retry started access check')
clientDestroyed=false;retainedCalibrate();check(not mic.ready and not mic.model.calibrated and mic.phase=='quiet','Visible Calibrate no longer works')
retainedRetry();check(accessChecks==1,'Visible Retry no longer works')
print('PASS',checks,'actual mic setup callbacks/frame/controls assertions; synthetic power and GUI only')
""".replace('ACTUAL_CALIBRATE', 'function mic:Calibrate()'+(R/'src/StarterPlayer/StarterPlayerScripts/Microphone.luau').read_text().split('function Microphone:Calibrate()',1)[1].split('function Microphone:Cancel()',1)[0])
if args.baseline:baseline()
else:
 source=(R/PATH).read_text();run(current(source))
 if args.negative_controls:
  mutants=[
   ('if clientDestroyed or not micPanel.Visible then return end;mic:Calibrate()', 'if clientDestroyed then return end;mic:Calibrate()', 'Hidden Calibrate erased completed readiness'),
   ('if clientDestroyed or not micPanel.Visible then return end;mic:Calibrate()', 'if not micPanel.Visible then return end;mic:Calibrate()', 'Destroyed Calibrate erased readiness'),
   ('if clientDestroyed or not micPanel.Visible then return end;mic:Check()', 'if clientDestroyed then return end;mic:Check()', 'Hidden Retry started access check'),
   ('if clientDestroyed or not micPanel.Visible then return end;mic:Check()', 'if not micPanel.Visible then return end;mic:Check()', 'Destroyed Retry started access check'),
   ('micPanel.Visible=micSetupOpen and','micPanel.Visible=not mic.ready and','Dismissed nonvoice navigation remains blocked'),
   ('if mic.ready and not previousMicReady then','if mic.ready then','Explicit ready setup immediately autoclosed'),
   ('local gameplayVisible=not GuiService.MenuIsOpen','local gameplayVisible=mic.ready and not GuiService.MenuIsOpen','Dismissed nonvoice navigation remains blocked'),
   ('local miniVisible=miniMapAvailable and gameplayVisible and windowFocused','local miniVisible=miniMapAvailable and gameplayVisible and windowFocused and not toast.Visible','Toast or test access hid minimap'),
   ('if mic.phase then mic:CancelCalibration();','if false then mic:CancelCalibration();','Close retained unfinished calibration'),
   ('return not mic.ready or data.voiceEligible~=true or blocked()','return data.voiceEligible~=true or blocked()','Unready mic allowed beam'),
  ]
  for old,new,expected in mutants:
   assert source.count(old)==1,old;run(current(source.replace(old,new)),expected)
