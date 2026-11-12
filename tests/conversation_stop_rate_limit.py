"""Actual client close, server dispatcher/close/capture helpers; synchronous mocked transport."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--negative-controls',action='store_true');a.add_argument('--baseline',action='store_true');args=a.parse_args()
P='src/ServerScriptService/Bootstrap.server.luau'
s=subprocess.check_output(['git','show','c1a0673f188c831d2c7110794e0ebf243a11bd1c:'+P],text=True,cwd=R) if args.baseline else (R/P).read_text()
c=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
def assemble(s):
 close=s[s.index('local function closeConversation(p)'):s.index('local function microSpeaker(')]
 capture=s[s.index('local function canCapture('):s.index('local function attackOrigin(')]
 dispatcher=s[s.index('action.OnServerEvent:Connect(function'):s.index('\nlocal function joined(p)')]
 client=c[c.index('closeConversation=function()'):c.index('local function refreshConversation()')]
 return r'''local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=100;local os={clock=function()return now end};local sessions={};local dispatch
local writes=0;local function bot(owner)return {talkingTo=owner,socialUntil=120,alive=true,root={Parent=true,Position=setmetatable({},{__sub=function()return {Magnitude=1}end})}}end
local p={};local stranger={};local position={};local function parts()return {},{Position=position},{PlatformStand=false}end
local VoiceEligibility={Allowed=function()return true end};local action={OnServerEvent={Connect=function(_,f)dispatch=f end}}
local talkCalls,beginCalls,vendorCalls=0,0,0
local function talk()talkCalls+=1 end;local function vendorPurchase()vendorCalls+=1 end
local VoiceCombat={Begin=function()beginCalls+=1;return false end};function p:SetAttribute()writes+=1 end
local function make()return {micReady=true,voice={},protectedUntil=0,dodgingUntil=0,nextAction=0}end
'''+close+capture+'''\nlocal closeCalls=0;local actualClose=closeConversation;closeConversation=function(p)closeCalls+=1;return actualClose(p)end\n'''+dispatcher+r'''
local s=make();sessions[p]=s;s.nextTalk=102;s.voice.nextCast=105;s.conversationBot=bot(p)
local reserved=s.conversationBot
for i=1,30 do dispatch(p,'Unknown')end
check(s.requestCount==30 and not canCapture(p,s,now),'Saturation setup failed')
local sends=0;local conversationPanel={Visible=true};local conversationNPC={};local conversationRevision=0
-- Actual client helper and synchronous transport; no native network scheduling claim.
local serverClose=closeConversation
local action={FireServer=function(_,verb,arg)sends+=1;dispatch(p,verb,arg)end}
local closeConversation
'''+client+r'''
closeConversation()
check(not conversationPanel.Visible and sends==1,'Client close did not hide/send once')
check(s.conversationBot==nil and reserved.talkingTo==nil and reserved.socialUntil==0,'Saturated close retained conversation')
check(canCapture(p,s,now),'Closed UI still blocks capture')
check(s.requestCount==30 and s.requestWindow==100 and s.nextTalk==102 and s.voice.nextCast==105,'Close reset quota or talk/attack cooldown')
s.micReady=false;check(not canCapture(p,s,now),'Close bypassed microphone readiness');s.micReady=true
s.protectedUntil=now+1;check(not canCapture(p,s,now),'Close bypassed protection');s.protectedUntil=0
local count=s.requestCount;local attr=writes;local closes=closeCalls
for i=1,1000 do dispatch(p,'EndConversation')end
check(s.requestCount==count and writes==attr and closeCalls==closes,'Repeated close amplifies state/output')
closeConversation();check(sends==1,'Hidden client close resent')
s.conversationBot=bot(p);local own=s.conversationBot
for _,arg in ipairs({false,true,1,'npc',{}})do dispatch(p,'EndConversation',arg)end
check(s.conversationBot==own and own.talkingTo==p,'Malformed close bypassed quota')
dispatch(stranger,'EndConversation');dispatch(p,{},nil);check(s.conversationBot==own,'Invalid sender/verb closed owner')
local foreign=bot(stranger);s.conversationBot=foreign;dispatch(p,'EndConversation')
check(s.conversationBot==nil and foreign.talkingTo==stranger and foreign.socialUntil==120,'Close stole foreign reservation')
dispatch(p,'Talk','npc');dispatch(p,'BeginCast',1);dispatch(p,'VendorPurchase',{})
check(talkCalls==0 and beginCalls==0 and vendorCalls==0,'Start or purchase bypassed saturated quota')
now=101.01;dispatch(p,'Talk','npc');check(talkCalls==1,'Window did not recover')
dispatch(p,'Talk','npc');dispatch(p,'VendorPurchase',{});check(talkCalls==1 and vendorCalls==0,'Action cooldown bypassed')
now=102.1;s.conversationBot=bot(p);local malformedOwner=s.conversationBot;dispatch(p,'EndConversation',false)
check(s.conversationBot==malformedOwner,'Unsaturated malformed close cleared reservation')
-- Nil close retains existing current-conversation semantics; no protocol ID added.
s.conversationBot=bot(p);dispatch(p,'EndConversation');check(s.conversationBot==nil,'Current close stopped working')
s.sustained={protocol={nextStart=110}};s.conversationBot=bot(p);dispatch(p,'EndConversation')
check(s.conversationBot==nil and s.sustained.protocol.nextStart==110,'Close changed sustained cooldown')
print('PASS',n,'conversation stop assertions; actual helpers/dispatcher, mocked transport and Talk/Begin/vendor admission boundaries')
'''
def run(source,error=None):
 text=assemble(source)
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.conversation_stop_',dir=R/'tests',delete=False)as f:f.write(text);p=Path(f.name)
 try:r=subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=15)
 finally:p.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode!=0 and error in out,out;print('PASS expected failure:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(s,'Saturated close retained conversation' if args.baseline else None)
if args.negative_controls:
 for old,new,error in [
 ('if verb=="EndConversation" and arg==nil then','if false then','Saturated close retained conversation'),
 ('if verb=="EndConversation" and arg==nil then','if verb=="EndConversation" then','Malformed close bypassed quota'),
 ('if s.conversationBot then closeConversation(p) end','closeConversation(p)','Repeated close amplifies state/output'),
 ('if bot and bot.talkingTo==p then','if bot then','Close stole foreign reservation'),
 ('s.requestCount>30','s.requestCount>3000','Start or purchase bypassed saturated quota')]:
  assert s.count(old)==1,old;run(s.replace(old,new),error)
