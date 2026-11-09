"""Actual server close helper with mocked sessions; no multiplayer timing evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function closeConversation(p)');b=s.index('local function microSpeaker(',a)
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local a,b={},{};local bot={talkingTo=a,socialUntil=20}
sessions[a]={conversationBot=bot};sessions[b]={conversationBot=bot}
closeConversation(a)
check(bot.talkingTo==nil and bot.socialUntil==0 and sessions[a].conversationBot==nil,'Owner did not release conversation')
bot.talkingTo=b;bot.socialUntil=40;sessions[a].conversationBot=bot
closeConversation(a)
check(bot.talkingTo==b and bot.socialUntil==40 and sessions[b].conversationBot==bot,'Late old owner canceled new player dialogue')
check(sessions[a].conversationBot==nil,'Late owner retained stale reference')
closeConversation(a)
check(bot.talkingTo==b and bot.socialUntil==40,'Repeated close canceled another owner')
bot.talkingTo=nil;bot.socialUntil=60;sessions[a].conversationBot=bot
closeConversation(a)
check(bot.socialUntil==60,'Stale player close canceled ambient social window')
sessions[a]=nil;closeConversation(a)
check(bot.socialUntil==60,'Departed player close changed resident state')
bot.talkingTo=b;closeConversation(b)
check(bot.talkingTo==nil and bot.socialUntil==0 and sessions[b].conversationBot==nil,'Current owner could not close after stale request')
print('PASS '..checks..' actual server conversation ownership checks with mocked sessions')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write('local sessions={}\n'+s[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
