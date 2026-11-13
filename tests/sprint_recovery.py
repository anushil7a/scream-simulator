"""Actual sprint client helper/dispatcher recovery; synthetic clock and transport only."""
from pathlib import Path
import argparse, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
b=(ROOT/'src/ServerScriptService/Bootstrap.server.luau').read_text(encoding='utf-8')
c=subprocess.check_output(['git','show','44f1f60:src/StarterPlayer/StarterPlayerScripts/Client.client.luau'],cwd=ROOT,text=True,encoding='utf-8') if args.baseline else (ROOT/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
dispatch=b[b.index('action.OnServerEvent:Connect(function'):b.index('\nlocal function joined(p)')]
helper=c[c.index('local sprinting=false'):c.index('\nlocal function targetCovered(')]
step=b[b.index('local function stepSprint('):b.index('\ntask.spawn(function()',b.index('local function stepSprint('))]
setup=r'''
local now=0;local os={clock=function()return now end}
local workspace={GetServerTimeNow=function()return now end}
local h={Health=100};local attrs={};local p={Character={FindFirstChildOfClass=function()return h end},GetAttribute=function(_,key)return attrs[key]end}
local s={nextAction=999,sprintRequested=false,micReady=true,sprintRunning=false,sprintCharge=10,sprintLockedUntil=0,dodgingUntil=0}
local sessions={[p]=s};local dispatch;local sends={}
local action={OnServerEvent={Connect=function(_,fn)dispatch=fn end},FireServer=function(_,verb,arg)table.insert(sends,{now,arg});dispatch(p,verb,arg)end}
local windowFocused=true;local mic={ready=true};local GuiService={};local focused=nil
local UIS={GetFocusedTextBox=function()return focused end};local micPanel={Visible=false};local modal={};local devPanel={};local conversationPanel={}
local Config={SprintDuration=10,SprintRegenDelay=.75,SprintRecovery=3}
local n=0;local function check(v,m)assert(v,m);n+=1 end
'''
checks=r'''
for i=1,30 do dispatch(p,'Unknown')end
setSprint(true);check(sprinting and not s.sprintRequested,'Saturated initial request not rejected')
for i=1,120 do now=i/60;setSprint(true)end
if BASELINE then
 check(sprinting and not s.sprintRequested and #sends==1,'Historical missing retry no longer reproduced')
 print('REPRO: held sprint remains local true/server false after quota expiry; release/repress required')
 return
end
check(s.sprintRequested,'Held sprint did not recover after quota expiry')
check(#sends<=5 and #sends>=3,'Held retry rate not bounded to half-second cadence')
for i=2,#sends do check(sends[i][1]-sends[i-1][1]>=.5-1e-7,'Retry faster than half second')end
local count=#sends;setSprint(false);check(#sends==count+1 and not s.sprintRequested and not sprinting,'Release not immediate')
for i=1,120 do now+=1/60;setSprint(false)end
check(#sends==count+1,'Repeated OFF sends extra packets')
now+=2;count=#sends;setSprint(true);check(#sends==count+1,'Fresh ON delayed')
now+=.01;setSprint(false);check(#sends==count+2 and not s.sprintRequested,'Fast OFF delayed')
now+=.01;setSprint(true);check(#sends==count+3 and s.sprintRequested,'Fresh transition throttled')
setSprint(false)
for _,kind in ipairs({'focus','menu','typing','modal','dev','conversation','missing','dead','platform','sit','seat','knock'})do
 now+=2;setSprint(true);check(sprinting,'Precondition failed '..kind)
 local character=p.Character
 if kind=='focus'then windowFocused=false elseif kind=='setup'then micPanel.Visible=true elseif kind=='menu'then GuiService.MenuIsOpen=true elseif kind=='typing'then focused={} elseif kind=='modal'then modal.Visible=true elseif kind=='dev'then devPanel.Visible=true elseif kind=='conversation'then conversationPanel.Visible=true elseif kind=='missing'then p.Character=nil elseif kind=='dead'then h.Health=0 elseif kind=='platform'then h.PlatformStand=true elseif kind=='sit'then h.Sit=true elseif kind=='seat'then h.SeatPart={} elseif kind=='knock'then attrs.KnockdownEnds=now+1 end
 now+=.01;count=#sends;setSprint(true);check(not sprinting and not s.sprintRequested and #sends==count+1 and sends[#sends][2]==false,'Interrupted intent retained '..kind)
 windowFocused=true;mic.ready=true;micPanel.Visible=false;GuiService.MenuIsOpen=false;focused=nil;modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false;p.Character=character;h.Health=100;h.PlatformStand=false;h.Sit=false;h.SeatPart=nil;attrs.KnockdownEnds=nil
 now+=2;if sprinting then setSprint(true)end;check(#sends==count+1,'Interruption automatically resumed '..kind)
end
mic.ready=false;s.micReady=false;now+=2;setSprint(true);check(sprinting and s.sprintRequested,'Unready microphone blocked dismissed-setup sprint');setSprint(false);mic.ready=true;s.micReady=true
local root={AssemblyLinearVelocity={X=4,Z=0}};s.sprintCharge=8;s.sprintRunning=true;s.sprintRegenAt=0;s.sprintLockedUntil=0
local before=s.sprintCharge
for i=1,10 do dispatch(p,'Sprint',true)end
check(s.sprintCharge==before,'Repeated true reset charge')
now+=.1;stepSprint(s,root,h,now,.1);check(math.abs(s.sprintCharge-7.9)<1e-7,'Repeated true changed interval charge')
print('PASS',n,'actual sprint helper/dispatcher assertions; synthetic time and transport')
'''
def run(fragment,error=None):
 body=setup+dispatch+'\n'+fragment+'\n'+step+'\n'+checks.replace('BASELINE',str(args.baseline).lower())
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False) as f:f.write(body);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],capture_output=True,text=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0
run(helper)
if args.negative_controls and not args.baseline:
 mutations=[
  ('if sprinting==requested and (not requested or now<nextSprintSend)', 'if sprinting==requested', 'Held sprint did not recover'),
  ('nextSprintSend=now+.5','nextSprintSend=now','Held retry rate not bounded'),
  ('if sprinting==requested and (not requested or now<nextSprintSend)', 'if now<nextSprintSend or (sprinting==requested and not requested)', 'Release not immediate'),
  ('if sprinting==requested and (not requested or now<nextSprintSend)', 'if (requested and now<nextSprintSend) or (sprinting==requested and not requested)', 'Fresh transition throttled'),
  ('then requested=false end','then requested=true end','Interrupted intent retained focus'),
 ]
 for old,new,error in mutations:
  assert helper.count(old)==1,old
  run(helper.replace(old,new),error)
