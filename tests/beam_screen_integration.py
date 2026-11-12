"""Actual Client registrations/helpers plus real feedback modules; synthetic GUI/transport only."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
c=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
fx=(R/'src/StarterPlayer/StarterPlayerScripts/BeamScreenFeedback.luau').read_text()
def build(c):
 comfort=c[c.index('\n',c.index('beamScreenFeedback=beamScreenFeedback.new('))+1:c.index('local function frame(parent,',c.index('local platformReducedMotion'))]
 helpers=c[c.index('local function blocked()'):c.index('local function beginCapture(')]
 effect=c[c.index('connectClient(remotes.Effect.OnClientEvent,function('):c.index('\nlocal elapsed=0',c.index('connectClient(remotes.Effect.OnClientEvent,function('))]
 a=c.index(' -- A current local acknowledgement,',c.index('connectClient(Run.RenderStepped'))
 # Isolate the actual acknowledged-attack hook and feedback/audio cadence.
 # Resident/notice presentation between them is covered by its own integration suite.
 hook_end=c.index('\n end',a)+5
 cadence_end=c.index(' aimInfo.Text=',a)
 tail_start=min(c.index(' beamScreenFeedback:Step(',hook_end),c.index(' cueContext();',hook_end))
 cadence=c[a:hook_end]+'\n'+c[tail_start:cadence_end]
 assert cadence.count('beamScreenFeedback:Step(')==1
 gui=c[c.index('local beamFeedbackGui='):c.index('local beamScreenFeedback=loadClientDependency(')]
 control=c[c.index('  sustainedControl:Step(dt,'):c.index('\n end',c.index('  sustainedControl:Step(dt,'))]
 return SETUP+'\nlocal BeamFX=(function()\n'+fx+'\nend)()\n'+gui+'local beamScreenFeedback=BeamFX.new(beamFeedbackGui)\n'+comfort+helpers+effect+'\nlocal elapsed=0;local function tick(dt)now+=dt;local alive=h.Health>0;local voiceCooldown=0;local voiceActive=attrs.SustainedActive\nif sustainedControl then\n'+control+'\nend\n'+cadence+'\nend\n'+CHECKS.replace('HOOK_ONLY',cadence[:cadence.index('\n end')+5])
SETUP=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local now=10;local os={clock=function()return now end};local workspace={GetServerTimeNow=function()return now end}
local function vec(x,y,z)return setmetatable({X=x,Y=y,Z=z},{__sub=function(a,b)return {Magnitude=math.sqrt((a.X-b.X)^2+(a.Y-b.Y)^2+(a.Z-b.Z)^2)}end})end
local Vector3={new=vec};local Vector2={new=function(x,y)return {X=x,Y=y}end}
local UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end,fromScale=function(...)return {...}end}
local Color3={fromRGB=function(r,g,b)return {R=r/255,G=g/255,B=b/255,kind='Color3'}end}
local function typeof(v)return type(v)=='table' and v.kind or type(v)end
local Instance={new=function()return {Destroy=function(self)self.dead=true end}end}
local Enum={ScreenInsets={None='None'},ZIndexBehavior={Sibling='Sibling'}}
local gold=Color3.fromRGB(255,220,90);local attrs={SustainedActive=true,SustainedSequence=1}
local h={Health=100,PlatformStand=false};local root={Position=vec(0,0,0)}
local character={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return h end}
local p={PlayerGui={},UserId=7,Character=character,CharacterRemoving={},GetAttribute=function(_,k)return attrs[k]end}
local cleanups={};local function ownClient(fn)table.insert(cleanups,fn)end;local function clientCheckpoint()return true end
local callbacks={};local function connectClient(signal,fn)callbacks[signal]=fn end
local script={Destroying={Connect=function(self,fn)callbacks[self]=fn end}}
local comfortSignal={};local comfort=false;local comfortError=false;local signalError=false
local GuiService=setmetatable({MenuOpened={},MenuIsOpen=false,GetPropertyChangedSignal=function()if signalError then error('unsupported signal')end;return comfortSignal end},{__index=function(_,k)if k=='ReducedMotionEnabled'then if comfortError then error('unsupported property')end;return comfort end end})
local typing;local UIS={WindowFocusReleased={},GetFocusedTextBox=function()return typing end}
local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false};local micPanel={Visible=false}
local clientDestroyed=false;local windowFocused=true;local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local gate={Cancel=function(self)self.next=nil end,Step=function(self)local n=self.next;self.next=nil;return n end}
local sent={};local sustainedControl=Controls.new(gate,function(verb,arg)table.insert(sent,{verb,arg})end,function()return {}end);sustainedControl:SetArmed(true);local mic={ready=true,power=0,phase=nil}
local data={micReady=true,voiceEligible=true,settings={reducedShake=false}}
local hitFeedback=require('../src/StarterPlayer/StarterPlayerScripts/HitFeedback').new()
local remotes={Effect={OnClientEvent={}}};local Players={GetPlayerByUserId=function(_,id)return (id==7 or id==8) and {} or nil end}
local Config={Auras={Gold=gold},GetSound=function()return nil end}
local worldUpdates,worldRemoves,audioStops,cues=0,0,0,0
local sustainedBeams={Update=function()worldUpdates+=1 end,Remove=function()worldRemoves+=1 end}
local attackAudioSettings={Range=100};local attackAudio={Stop=function()audioStops+=1 end,Remove=function()end,Pulse=function()end,Step=function()end}
local gameplayAudio={Step=function()end};local function cueContext()end;local function playGameplayCue()cues+=1 end
'''
CHECKS=r'''
local send=callbacks[remotes.Effect.OnClientEvent]
local function beam(id)send('SustainedBeam',vec(0,0,0),id,'Gold',vec(0,0,-1),20,4)end
local function start()
 attrs.SustainedActive=false;sustainedControl:Cancel();gate.next='start';tick(.001)
 check(sustainedControl.attack and not sustainedControl.attack.acknowledged,'Local intent failed')
 return sustainedControl.attack.sequence
end
local function ack(seq)attrs.SustainedActive=true;attrs.SustainedSequence=seq;tick(.001)end
check(beamFeedbackGui.ScreenInsets==Enum.ScreenInsets.None and beamFeedbackGui.DisplayOrder==-1 and beamFeedbackGui.Parent==p.PlayerGui,'Feedback viewport/HUD layer mismatch')
check(screenFeedbackAllowed(),'Initial feedback unavailable')
beam(8);check(beamScreenFeedback.sequence==0 and worldUpdates==1,'Remote owner launched local feedback')
local seq=start();beam(7);check(beamScreenFeedback.sequence==0,'Unacknowledged visual packet launched feedback')
ack(seq);check(sustainedControl.attack.acknowledged and beamScreenFeedback.sequence==seq and beamScreenFeedback.launchEnds==now+.45,'Event-before-attributes lost launch')
local ending=beamScreenFeedback.launchEnds;tick(.01);beam(7);check(beamScreenFeedback.launchEnds==ending,'Repeated pulse/frame extended launch')
send('SustainedBeamEnd',nil,8);check(beamScreenFeedback.launchEnds==ending and audioStops==1,'Remote end cleared local feedback')
send('SustainedBeamEnd',nil,7);attrs.SustainedActive=false;tick(.001);check(beamScreenFeedback.launchEnds==0 and audioStops==2 and not sustainedControl.attack,'Local end did not clear feedback')
seq=start();send('SustainedBeamEnd',nil,7);ack(seq);check(beamScreenFeedback.sequence==seq and beamScreenFeedback.launchEnds==0,'End-before-ack replayed launch')
seq=start();attrs.SustainedActive=true;attrs.SustainedSequence=seq
sustainedControl:Step(.001,now,mic.power,true,true,true,seq);check(sustainedControl.attack.acknowledged,'Real Controls did not acknowledge before render')
send('SustainedBeamEnd',nil,7);tick(.001);check(beamScreenFeedback.launchEnds==0,'End-after-ack-before-frame replayed launch')
seq=start();ack(seq);check(beamScreenFeedback.launchEnds==now+.45,'Fresh sequence after early end suppressed')
seq=start();ack(seq);check(beamScreenFeedback.sequence==seq,'Attributes-before-event lost launch');ending=beamScreenFeedback.launchEnds;beam(7);check(beamScreenFeedback.launchEnds==ending,'Later visual packet replayed launch')
seq=start();local prior=beamScreenFeedback.sequence;attrs.SustainedActive=true;attrs.SustainedSequence=seq+100;tick(.001);check(beamScreenFeedback.sequence==prior and not sustainedControl.attack.acknowledged,'Mismatched local/server sequence launched')
attrs.SustainedSequence='bad';tick(.001);check(beamScreenFeedback.sequence==prior,'Malformed server sequence launched');ack(seq);check(beamScreenFeedback.sequence==seq,'Matching acknowledgement without visual packet failed')
-- Independently exercise frame-hook fences, even if Controls removed a stale attack first.
local hookSequence=seq+1;sustainedControl.attack={sequence=hookSequence,acknowledged=false};attrs.SustainedSequence=hookSequence;attrs.SustainedActive=true
HOOK_ONLY
check(beamScreenFeedback.sequence==seq,'Frame hook admitted unacknowledged intent')
sustainedControl.attack.acknowledged=true;attrs.SustainedSequence=hookSequence+1
HOOK_ONLY
check(beamScreenFeedback.sequence==seq,'Frame hook admitted mismatched sequence')
attrs.SustainedSequence=hookSequence;attrs.SustainedActive=false
HOOK_ONLY
check(beamScreenFeedback.sequence==seq,'Frame hook admitted inactive server state')
sustainedControl:Cancel()
now+=.4;send('SustainedHit',nil,1,10);check(beamScreenFeedback.hitEnds==now+.25 and cues==1,'Accepted hit missing feedback')
local hitEnd=beamScreenFeedback.hitEnds;now+=.5;send('SustainedHit',nil,1,10);check(beamScreenFeedback.hitEnds==hitEnd and cues==1,'Duplicate hit replayed feedback')
send('SustainedHit',nil,0,20);check(cues==1,'Stale hit replayed feedback')
send('SustainedHit',nil,1,11);check(cues==2 and beamScreenFeedback.hitEnds==now+.25,'Increasing confirmed total rejected')
local blockers={
 function(v)clientDestroyed=v end,function(v)windowFocused=not v end,function(v)sustainedControl.armed=not v end,
 function(v)mic.ready=not v end,function(v)data.voiceEligible=not v end,function(v)data.settings.reducedShake=v end,
 function(v)platformReducedMotion=v end,function(v)modal.Visible=v end,function(v)devPanel.Visible=v end,
 function(v)conversationPanel.Visible=v end,function(v)micPanel.Visible=v end,function(v)GuiService.MenuIsOpen=v end,
 function(v)typing=v and {} or nil end,function(v)h.PlatformStand=v end,function(v)h.Health=v and 0 or 100 end,
 function(v)attrs.KnockdownEnds=v and now+1 or 0 end}
for i,f in ipairs(blockers)do
 f(true);check(not screenFeedbackAllowed(),'Eligibility bypass '..i)
 tick(.001);check(not beamScreenFeedback.root.Visible,'Blocked effect remained visible '..i)
 f(false);check(screenFeedbackAllowed(),'Eligibility recovery failed '..i)
end
local saved=sustainedControl;sustainedControl=nil;check(not screenFeedbackAllowed(),'Legacy mode allowed effect');sustainedControl=saved
comfort=true;callbacks[comfortSignal]();check(platformReducedMotion and not screenFeedbackAllowed(),'Comfort signal ignored')
comfort=false;callbacks[comfortSignal]();check(not platformReducedMotion,'Comfort preference not restored')
comfortError=true;refreshScreenComfort();check(platformReducedMotion and not screenFeedbackAllowed(),'Comfort read failure enabled effects');comfortError=false;refreshScreenComfort()
seq=start();elapsed=0;ack(seq);check(beamScreenFeedback.root.Visible,'Screen feedback throttled behind HUD gate')
for _,signal in ipairs({UIS.WindowFocusReleased,GuiService.MenuOpened})do
 callbacks[signal]();check(not beamScreenFeedback.root.Visible and beamScreenFeedback.launchEnds==0,'Immediate focus/menu cleanup missing');seq=start();ack(seq)
end
callbacks[p.CharacterRemoving]();check(not beamScreenFeedback.root.Visible and beamScreenFeedback.launchEnds==0,'Character removal retained effect')
seq=start();ack(seq);for i=#cleanups,1,-1 do cleanups[i]()end;check(beamScreenFeedback.destroyed and beamScreenFeedback.root==nil and beamFeedbackGui.dead,'Destroy retained effect')
print('PASS',checks,'actual Client feedback integration assertions; real Controls ack, mocked GUI/world/audio and synthetic events')
'''

def run(source,error=None):
 body=build(source)
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as f:f.write(body);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=20)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0,out
run(c)
if args.negative_controls:
 cases=[
 ('if ended then beamScreenFeedback:Begin(ended.sequence,os.clock(),nil,false) end','if ended then end','End-before-ack replayed'),
 ('screenAttack and screenAttack.acknowledged and','screenAttack and','Frame hook admitted unacknowledged'),
 ('and p:GetAttribute("SustainedSequence")==screenAttack.sequence then','then','Frame hook admitted mismatched'),
 ('and p:GetAttribute("SustainedActive")==true and','and','Frame hook admitted inactive'),
 ('if id==p.UserId then\n   -- End has no sequence payload.','if true then\n   -- End has no sequence payload.','Remote end cleared'),
 ('if hitFeedback:Accept(id,aura,os.clock()) then','if true then','Duplicate hit replayed'),
 ('not platformReducedMotion and not beamBlocked()','not platformReducedMotion','Eligibility bypass 4'),
 ('not clientDestroyed and windowFocused and sustainedControl~=nil','windowFocused and sustainedControl~=nil','Eligibility bypass 1'),
 ('windowFocused and sustainedControl~=nil','sustainedControl~=nil','Eligibility bypass 2'),
 ('and sustainedControl.armed','and true','Eligibility bypass 3'),
 ('not data.settings.reducedShake and not platformReducedMotion','not platformReducedMotion','Eligibility bypass 6'),
 ('and not platformReducedMotion and not beamBlocked()','and not beamBlocked()','Eligibility bypass 7'),
 ('connectClient(UIS.WindowFocusReleased,function() beamScreenFeedback:Clear() end)','connectClient(UIS.WindowFocusReleased,function() end)','Immediate focus/menu cleanup'),
 ('connectClient(GuiService.MenuOpened,function() beamScreenFeedback:Clear() end)','connectClient(GuiService.MenuOpened,function() end)','Immediate focus/menu cleanup'),
 ('platformReducedMotion=not ok or value==true','platformReducedMotion=ok and value==true','Comfort read failure'),
 ('connectClient(p.CharacterRemoving,function() beamScreenFeedback:Clear() end)','connectClient(p.CharacterRemoving,function() end)','Character removal retained'),
 ('ownClient(function() beamScreenFeedback:Destroy() end)','ownClient(function() end)','Destroy retained'),
 ]
 for old,new,error in cases:
  assert c.count(old)==1,old;run(c.replace(old,new),error)
 line=next(s for s in c.splitlines()if s.strip().startswith('beamScreenFeedback:Step('));gate=' elapsed+=dt;if elapsed<.15 then return end;elapsed=0'
 assert gate in c;run(c.replace(line+'\n','').replace(gate,gate+'\n'+line),'Screen feedback throttled')
