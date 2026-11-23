"""Presentation module with UI doubles. No microphone/device or Studio evidence."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
module=(R/'src/StarterPlayer/StarterPlayerScripts/VoiceReactor.luau').read_text()
setup='''
local objects={}
Color3={fromRGB=function(r,g,b)return {r,g,b}end}
UDim={new=function(s,o)return {Scale=s,Offset=o}end}
UDim2={new=function(a,b,c,d)return {X={Scale=a,Offset=b},Y={Scale=c,Offset=d}}end}
UDim2.fromOffset=function(x,y)return UDim2.new(0,x,0,y)end
UDim2.fromScale=function(x,y)return UDim2.new(x,0,y,0)end
Vector2={new=function(x,y)return {X=x,Y=y}end}
Enum={Font={GothamMedium='GothamMedium'},TextXAlignment={Left='Left'}}
Instance={new=function(class)local o={ClassName=class};table.insert(objects,o);return o end}
local Reactor=(function()
'''
checks=r'''
end)()
local n=0;local function check(v,msg)assert(v,msg);n+=1 end
for _,entry in ipairs({{-.5,0},{2,1},{0,0},{.42,.42},{math.huge,1},{-math.huge,0},{0/0,0},{'bad',0}})do check(Reactor.Power(entry[1])==entry[2],'Unbounded power')end
check(Reactor.Power(nil)==0,'Missing power')
local r=Reactor.new({})
check(#r.bars==28 and #r.history==28,'Incorrect sample bank')
check(not r.root.Active,'Decorative view intercepts input')
r:Step(.8,.04,false,true)
check(r.history[28]==.8 and r.history[27]==0,'History not actual samples')
check(r.bars[28].Size.Y.Offset==18 and r.bars[27].Size.Y.Offset==2,'Amplitude geometry incorrect')
r:Step(.2,.04,true,true)
for _,b in ipairs(r.bars)do check(b.Size.Y.Offset==6,'Reduced effects animates history')end
for i=1,28 do r:Step(0,.04,false,false)end
for _,b in ipairs(r.bars)do check(b.Size.Y.Offset==2 and b.BackgroundColor3==Reactor.Theme.Quiet,'Silence fabricated activity')end
r:Step(0/0,0/0,false,true);check(r.fill.Size.X.Scale==0,'Invalid input leaked into geometry')
for _,v in ipairs({{320,true},{390,true},{844,true},{819,false},{820,false},{1280,false}})do
 local w,h=Reactor.Layout(v[1],v[2]);check(w<=v[1]-28 and h<=96,'Unsafe viewport size')
 local bottom=12;local top=bottom+h
 if v[2] or v[1]<820 then check(top<=99,'Meter overlaps reserved actions')end
 if not v[2] and v[1]>=820 then check((v[1]-w)/2>=256 and (v[1]+w)/2<=v[1]-274,'Desktop side HUD overlap')end
end
-- Native baseline footprints from stock Studio emulation. These coordinates
-- are specific to the profiles; physical touch and other stick modes are separate.
for _,v in ipairs({{388,762,103,293},{359,690,103,264}})do
 local w,h=Reactor.Layout(v[1],true,v[2])
 local left=(v[1]-w)/2
 local right=left+w
 check(left-v[3]>=8 and v[4]-right>=8,'Known stock-control clearance not preserved')
 check(h==84,'This fix should not push the meter upward toward actions')
 check(Reactor.Status('live',false,true,v[1],v[2],true)=='BEAMS OFF\nVoice chat unchanged','Compact state suggests mic mute')
 check(Reactor.Status('live',true,true,v[1],v[2],true)=='MIC UNAVAILABLE\nOpen voice settings','Unavailable status precedence changed')
 check(Reactor.Status('live status unchanged',false,false,v[1],v[2],true)=='live status unchanged','Live status must stay truthful')
end
for _,v in ipairs({{749,388,true},{844,390,true},{388,762,false},{1280,900,false},{320,568,true},{343,942,true},{452,800,true}})do
 local oldW,oldH=Reactor.Layout(v[1],v[3])
 local w,h=Reactor.Layout(v[1],v[3],v[2])
 check(oldW==w and oldH==h,'Out-of-scope screen allocation changed')
 check(Reactor.Status('live',false,true,v[1],v[2],v[3])=='BEAMS OFF · TALK FREELY\nVoice chat is unchanged','Out-of-scope copy changed')
end
for width=344,451 do
 local w=Reactor.Layout(width,true,700)
 check((w-20)/28-3>0,'Portrait waveform has negative-width bars')
end
check(r.text.TextSize>=12,'Unreadable status')
local function cue(voiceCooldown,quiet,voiceActive,attack,onset,armed,state)
 __STATUS_CODE__
end
local text,color=cue(4.9,true,false,false,0,true)
check(text=='Cooldown 4.9s · go quiet' and color=='muted','Cooldown hides the reset instruction or looks charged')
text,color=cue(0,true,false,false,0,true)
check(text=='Go quiet' and color=='muted','Reset state encourages speech or looks ready')
text,color=cue(0,false,false,false,0,true)
check(text=='Aim and speak' and color=='gold','Ready cue does not give the next action')
text=cue(0,false,false,false,.1,true)
check(text=='Voice detected • keep speaking','Onset cue changed')
text,color=cue(0,false,true,true,0,true)
check(text=='Attacking • 3.0s left' and color~='muted','Active status lost')
text=cue(4.9,true,false,false,0,false)
check(text=='Beams OFF • E to turn on','Cooldown hides explicit OFF')
local function short(state,cooldown,quiet,active,attack,onset,armed)
 state.touch=true;state.height=state.height or 241
 local _,_,button=cue(cooldown or 0,quiet or false,active or false,attack or false,onset or 0,armed~=false,state)
 return button
end
check(short({},4.9,true,false,false,0,true)=='BEAMS: ON\nCooldown 4.9s · go quiet','Short cooldown hides the quiet cue')
check(short({},4.9,false)=='BEAMS: ON\nCooldown 4.9s','Quiet cooldown still asks for silence')
local _,_,_,_,_,thresholdReady=cue(0,false,false,false,0,true)
local _,_,_,_,_,thresholdCooling=cue(4.9,false,false,false,0,true)
local _,_,_,_,_,thresholdOff=cue(0,false,false,false,0,false)
local _,_,_,_,_,thresholdUnavailable=cue(0,false,false,false,0,true,{serverReady=false})
check(thresholdReady and not thresholdCooling and not thresholdOff and not thresholdUnavailable,'Start threshold must reflect beam availability')
check(short({},0,true)=='BEAMS: ON\nGo quiet','Short reset hides the quiet cue')
check(short({},0,false)=='BEAMS: ON\nAim and speak','Short ready cue lost')
check(short({trainingFar=true},0,false)=='BEAMS: ON\nMove closer','Short beam cue contradicted the training guide')
check(short({trainingFar=true},2,false)=='BEAMS: ON\nCooldown 2.0s','Training distance hid the beam cooldown')
check(short({height=314},0,false)=='BEAMS: ON\nAim and speak','Short cue disappears one pixel early')
check(short({height=315},0,false)=='BEAMS: ON\nTap to turn off','Short cue leaks into full meter layout')
check(short({},0,false,false,false,.1)=='BEAMS: ON\nKeep speaking','Short onset cue lost')
check(short({},0,false,true,true)=='BEAMS: ON\nFiring · 3.0s','Short firing cue lost')
check(short({},0,false,false,true)=='BEAMS: ON\nStarting attack…','Short pending acknowledgement claims firing')
check(short({},0,false,true,true,0,false)=='BEAMS: OFF\nTap to turn on','Stale firing masks OFF')
check(short({},4.9,true,false,false,0,false)=='BEAMS: OFF\nTap to turn on','Stale cooldown masks OFF')
check(short({voiceStatus='denied'},0,false,false,false,0,false)=='BEAMS: OFF\nCheck voice settings','Denied short cue suggests arming')
check(short({voiceStatus='unavailable'},0,false,false,false,0,false)=='BEAMS: OFF\nVoice check delayed','Delayed short cue missing')
check(short({voiceStatus='checking'},0,false,false,false,0,false)=='BEAMS: OFF\nChecking voice','Checking short cue missing')
check(short({voiceStatus='checking',voiceEligible=true})=='BEAMS: ON\nAim and speak','Eligible player was treated as still checking')
check(short({localReady=false},0,false,false,false,0,false)=='BEAMS: OFF\nConnecting mic','Local mic unavailable reported ready')
check(short({localReady=false,inactiveInput=true},0,false,false,false,0,false)=='BEAMS: OFF\nMic inactive','Inactive input was labeled as connecting')
check(short({localReady=false,invalidSignal=true},0,false,false,false,0,false)=='BEAMS: OFF\nNo mic signal','Invalid signal was labeled as connecting')
check(short({localReady=false,localEligible=true},0,false,false,false,0,false)=='BEAMS: OFF\nWaiting for mic input','Missing input was labeled as connecting')
check(short({localReady=false,localEligible=true,detachedInput=true,invalidSignal=true},0,false,false,false,0,false)=='BEAMS: OFF\nWaiting for mic input','Detached input retained an invalid-signal label')
check(short({localReady=false,mutedInput=true,inactiveInput=true},0,false,false,false,0,false)=='BEAMS: OFF\nUnmute in Roblox','Inactive input masked mute guidance')
local _,_,wideInactive=cue(0,false,false,false,0,false,{localReady=false,inactiveInput=true})
check(wideInactive=='BEAMS: OFF\nMic inactive','Wide button hid the concrete input problem')
local _,_,wideMissing=cue(0,false,false,false,0,false,{localReady=false,localEligible=true})
local _,_,talkMissing=cue(0,false,false,false,0,false,{localReady=false,localEligible=true,nearNpc=true})
check(wideMissing==talkMissing and wideMissing=='BEAMS: OFF\nWaiting for mic input','Nearby TALK changed the microphone readiness cue')
check(short({localReady=false,mutedInput=true},0,false,false,false,0,false)=='BEAMS: OFF\nUnmute in Roblox','Muted short cue omitted the recovery action')
check(short({localReady=false,mutedInput=true,detachedInput=true},0,false,false,false,0,false)=='BEAMS: OFF\nConnecting mic','Detached input retained stale mute guidance')
check(short({voiceStatus='denied',localReady=false,mutedInput=true},0,false,false,false,0,false)=='BEAMS: OFF\nCheck voice settings','Mute cue masked denied access')
local _,_,_,_,mutedMeter=cue(0,false,false,false,0,false,{mutedInput=true,localReady=false})
check(mutedMeter=='MIC MUTED\nUnmute in Roblox','Visible meter omitted mute guidance')
check(short({serverReady=false},0,false)=='BEAMS: ON\nConnecting mic','Server mic unavailable reported ready')
check(short({tools=true},0,false)=='BEAMS: ON\nClose Test Tools','Blocked test tools reported ready')
check(short({protection=1.6},0,false)=='BEAMS: ON\nProtected 1.6s','Protection reported ready')
check(short({unconfirmed=true},0,true)=='BEAMS: ON\nGo quiet, then retry','Short rejected attempt hides recovery')
local _,_,desktop,meter=cue(0,true,false,false,0,true,{width=820,nearNpc=true})
check(not meter and desktop=='BEAMS: ON\nGo quiet','Desktop TALK hides the quiet cue')
_,_,desktop,meter=cue(4.9,true,false,false,0,true,{nearNpc=true})
check(not meter and desktop=='BEAMS: ON\nCooldown 4.9s · go quiet','Desktop TALK hides cooldown guidance')
_,_,desktop,meter=cue(0,false,false,false,0,false,{nearNpc=true})
check(not meter and desktop=='BEAMS: OFF\n[E] to turn on','Desktop compact OFF shows the wrong input')
local _,_,gamepad,gamepadMeter=cue(0,false,false,false,0,false,{nearNpc=true,gamepad=true})
check(not gamepadMeter and gamepad=='BEAMS: OFF [RB/R1]\nPress to turn on','Controller compact OFF shows the wrong input')
local _,_,wideGamepad,wideGamepadMeter,wideGamepadText=cue(0,false,false,false,0,false,{gamepad=true})
check(wideGamepadMeter and wideGamepad=='BEAMS: OFF\n[RB/R1] to turn on' and wideGamepadText:find('Voice chat is unchanged',1,true),
 'Controller full meter shows the wrong input')
_,_,desktop,meter=cue(0,true,false,false,0,true,{nearNpc=false})
check(meter and desktop=='BEAMS: ON\n[E] to turn off','Desktop meter or normal hint did not return')
_,_,desktop,meter=cue(0,true,false,false,0,true,{width=819,nearNpc=true})
check(meter and desktop=='BEAMS: ON\n[E] to turn off','Desktop TALK hid the separate narrow meter')
_,_,desktop,meter=cue(0,true,false,false,0,true,{width=567,height=314})
check(not meter and desktop=='BEAMS: ON\nGo quiet','Short desktop lost the quiet cue')
local _,_,wideFiring=cue(0,false,true,true,0,true)
check(wideFiring=='BEAMS: ON\nAttacking • 3.0s left','Wide beam button hides firing phase')
local _,_,wideCooldown=cue(4.9,true,false,false,0,true)
check(wideCooldown=='BEAMS: ON\nCooldown 4.9s · go quiet','Wide beam button hides cooldown phase')
print('PASS '..n..' VoiceReactor contracts with UI doubles; no Studio or live mic')
'''
s=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=s.index('  captureHint=not alive')
end=s.index('\n end\n meterText.Text=',start)
status_code=r'''
 state=state or {}
 local viewport={X=state.width or 1280,Y=state.height or 381}
 local talkTarget=state.nearNpc and {} or nil
 local alive,windowFocused,protectionRemaining,knocked,rolling,touch=true,true,state.protection or 0,false,false,state.touch==true
 local mic={ready=state.localReady~=false,eligible=state.localEligible==true,signalUnavailable=state.invalidSignal==true,
  input=(state.mutedInput or state.inactiveInput or state.invalidSignal) and
   {Muted=state.mutedInput,Active=not state.inactiveInput,Parent=not state.detachedInput} or nil}
 local devPanel={Visible=state.tools==true}
 local UIS={GetFocusedTextBox=function()end}
 local humanoid={PlatformStand=false}
 local data={micReady=state.serverReady~=false,voiceStatus=state.voiceStatus,voiceEligible=state.voiceEligible==true or state.voiceStatus==nil}
''' + s[s.index('local function voiceEligibilityHint('):s.index('-- Process every server transition')] + '''
 local eligibilityHint,inputMuted=voiceEligibilityHint(true)
 local p={GetAttribute=function() return 3 end}
 local serverNow=0
 local sustainedControl={armed=armed,attack=attack,gate={needsQuiet=quiet,onset=onset},unconfirmedUntil=state.unconfirmed and os.clock()+10 or nil}
 local muted,gold='muted','gold'
 local meterFill={}
 local function blocked() return false end
 local function beamBlocked() return not mic.ready or data.voiceEligible~=true or blocked() end
 local captureHint
 local castButton={}
 local meterText,power,academy={},0,{VoiceReactor=Reactor,voiceThreshold={},gamepad=state.gamepad,trainingNeedsCloser=function()return state.trainingFar end}
''' + s[s.index(' local showVoiceMeter='):s.index(' meter.Visible=gameplayVisible and showVoiceMeter')] + s[start:end] + s[s.index('\n meterText.Text=',end):s.index(' local shortLandscape=',end)] + s[s.index(' if sustainedControl then\n  -- Keep the next voice action'):s.index(' -- Keep attack duration/cooldown distinct')] + '''
 return captureHint,meterFill.BackgroundColor3,castButton.Text,showVoiceMeter,meterText.Text,academy.voiceThreshold.Visible
'''
toggle_label=s[s.index('local function screamToggleLabel('):s.index('local function releaseCapture(')]
payload=setup+module+checks.replace('local function cue(',toggle_label+'local function cue(').replace('__STATUS_CODE__',status_code)

def run(source, expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.reactor-',dir=R/'tests',delete=False,encoding='utf-8') as f:
  f.write(source);p=Path(f.name)
 try:
  result=subprocess.run(['luau',str(p)],cwd=R,capture_output=True,text=True)
 finally:p.unlink()
 if expected:
  assert result.returncode and expected in result.stderr,result.stdout+result.stderr
  print('PASS control: '+expected)
 else:
  assert result.returncode==0,result.stderr
  print(result.stdout,end='')

run(payload)
if '--negative-controls' in sys.argv:
 for old,new,expected in [
  ('academy.gamepad and "Press to turn on" or ', '', 'Controller compact OFF shows the wrong input'),
  ('status=captureHint','status=nil','Short cooldown hides the quiet cue'),
  ('or academy.trainingNeedsCloser() and "Move closer"','', 'Short beam cue contradicted the training guide'),
  ('viewport.Y>=315','viewport.Y>=314','Short cue disappears one pixel early'),
  ('viewport.Y>=315','viewport.Y>=316','Short cue leaks into full meter layout'),
  ('if not mic.ready or serverReady~=true then','if serverReady~=true then','Local mic unavailable reported ready'),
  ('if input.Active==false then return "Mic inactive" end','', 'Inactive input was labeled as connecting'),
  ('if mic.signalUnavailable then return "No mic signal" end','', 'Invalid signal was labeled as connecting'),
  ('elseif mic.eligible then return "Waiting for mic input" end','end','Missing input was labeled as connecting'),
  ('or not mic.ready or data.micReady~=true or sustainedControl.armed','or sustainedControl.armed','Wide button hid the concrete input problem'),
  ('and not (not touch and viewport.X>=820 and talkTarget~=nil)','', 'Desktop TALK hides the quiet cue'),
  ('if eligibilityHint then', 'if false then','Denied short cue suggests arming'),
  ('if inputMuted then','if false then','Inactive input masked mute guidance'),
  (' or sustainedControl.armed and (voiceActive or voiceCooldown>0)','', 'Wide beam button hides firing phase'),
 ]:
  assert payload.count(old)==1,old
  run(payload.replace(old,new),expected)
targets=s[s.index('local function playerTargetInfo'):s.index('local sprintButton=')]
assert ' HP' not in targets and 'humanoid.MaxHealth' not in targets
assert 'hf.Size=UDim2.fromScale(current/maximum,1)' in s, 'Player health was removed'
assert 'academy.reactor:Step(power,dt,data.settings.reducedShake' in s
