"""Actual server capture eligibility with mocked character/conversation state."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start=source.index('local function canCapture(')
end=source.index('local function attackOrigin(',start)
setup='''
local VoiceEligibility=require('../src/ServerScriptService/VoiceEligibility')
local eligibility=VoiceEligibility.New(false);local token=VoiceEligibility.Poll(eligibility,0);VoiceEligibility.Complete(eligibility,token,1,true,true)
local mt={__sub=function(a,b)return {Magnitude=math.abs(a.x-b.x)}end}
local function position(x)return setmetatable({x=x},mt)end
local root={Position=position(0)}
local humanoid={PlatformStand=false}
local parts=function()return {},root,humanoid end
'''
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local p={};local s={voiceEligibility=eligibility,micReady=true,protectedUntil=0,dodgingUntil=0,knockedUntil=0}
check(canCapture(p,s,10),'Valid ordinary attack blocked')
s.micReady=false;check(not canCapture(p,s,10),'Unavailable mic accepted');s.micReady=true
for _,key in ipairs({'protectedUntil','dodgingUntil','knockedUntil'})do
 s[key]=11;check(not canCapture(p,s,10),'Blocked movement/protection accepted: '..key);s[key]=0
end
local bot={alive=true,root={Parent=true,Position=position(10)},talkingTo=p,socialUntil=20}
s.conversationBot=bot
check(not canCapture(p,s,10),'Active nearby dialogue accepted attack')
bot.socialUntil=10;check(canCapture(p,s,10),'Expired dialogue locked attack');bot.socialUntil=20
bot.talkingTo={};check(canCapture(p,s,10),'Another player conversation locked attack');bot.talkingTo=p
bot.root.Position=position(15);check(canCapture(p,s,10),'Stale distant dialogue locked attack');bot.root.Position=position(14)
check(not canCapture(p,s,10),'Boundary dialogue accepted attack')
bot.alive=false;check(canCapture(p,s,10),'Dead resident locked attack');bot.alive=true
bot.root.Parent=nil;check(canCapture(p,s,10),'Removed resident locked attack');bot.root.Parent=true
s.conversationBot=nil;check(canCapture(p,s,10),'Closing conversation did not unblock')
humanoid.PlatformStand=true;check(not canCapture(p,s,10),'Ragdoll accepted attack without knockdown timer')
humanoid.PlatformStand=false;check(canCapture(p,s,10),'Recovered character remained blocked')
humanoid=nil;check(not canCapture(p,s,10),'Missing humanoid accepted attack')
root=nil;check(not canCapture(p,s,10),'Missing character accepted attack')
print('PASS '..checks..' actual server combat availability checks with mocked character/dialogue')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.availability_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
