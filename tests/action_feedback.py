"""Actual State receiver and server action helpers; simulated UI/time, no network/store."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
client = (root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server = (root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
receiver = client[client.index('local lastMilestone'):client.index('connectClient(UIS.InputBegan')]
speaker = server[server.index('local function microSpeaker('):server.index('local function vendorPurchase(')]
start = server.index(' elseif verb=="ClaimQuest" then') + len(' elseif verb=="ClaimQuest" then')
claim = server[start:server.index(' elseif verb=="SetSettings"', start)]
setup = '''
local now=100;local os={clock=function()return now end}
local notices={};local urgentNotices={};local receiver;local data;local p={};local earned=0;local stops=0
local function notify(message,urgent)table.insert(notices,message);table.insert(urgentNotices,urgent==true)end
local function cueContext()end;local gameplayAudio={ObserveLevel=function()end}
local remotes={State={OnClientEvent={}}}
local function connectClient(_,fn)receiver=fn end
local Config={MaxLevel=100,MicroSpeakerPrice=250,Quests={{id='garden',goal=3}},GetQuest=function(id)
 if id=='garden' then return {id='garden',name='Garden',goal=3,coins=40,xp=100} end
end}
local questsToggle={};local stats={};local xpText={};local xf={};local zone={};local testButton={};local tracked={}
local gold='gold';local white='white';local trackedQuestText
local Color3={fromRGB=function()return 'red' end}
local UDim2={fromScale=function(x,y)return {x,y}end}
local gui={AbsoluteSize={X=390}};local modal={Visible=false}
local function refreshQuestObjects()end;local function refreshHealth()end
local function progressLabel()return 'progress' end;local function showConversation()end;local function render()end
local s={data={coins=10,achievements={},quests={garden={progress=3,claimed=false}}}}
local function packet(message,milestone)
 return {level=10,coins=s.data.coins,xp=0,xpNext=100,quests=s.data.quests,questTime=0,message=message,milestone=milestone}
end
local function state(_,message,conversation,urgent)local value=packet(message,'LEVEL 10 milestone');value.messageUrgent=urgent;receiver(value)end
local Commerce={Multiplier=function()return 1 end}
local function coins(_,amount)s.data.coins+=amount end
local function xp(_,amount)earned+=amount end
local function stopQuest()stops+=1;s.activeQuest=nil end
'''
checks = '''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
receiver(packet('Level 10','LEVEL 10 milestone'))
check(#notices==1 and notices[1]=='LEVEL 10 milestone','New milestone was not shown once')
now=100.1;microSpeaker(p,s,false)
check(s.data.coins==10 and not s.data.amplifierOwned,'Rejected upgrade mutated ownership/coins')
CHECK_REJECTION
check(urgentNotices[#urgentNotices]==true,'Upgrade rejection lost urgency')
now=100.2;claim(p,s,'garden')
check(s.data.quests.garden.claimed and s.data.coins==50 and earned==100,'Valid claim missing reward')
CHECK_REWARD
local count=#notices;claim(p,s,'garden')
check(s.data.coins==50 and earned==100 and #notices==count,'Repeated claim duplicated reward/notice')
for _=1,5 do receiver(packet(nil,'LEVEL 10 milestone')) end
check(#notices==count,'Repeated milestone snapshots replayed a notification')
now=100.3;state(p,'Quest complete! Claim your reward in Quests.')
CHECK_COMPLETE
now=107;state(p,'Speak with the market vendor nearby before buying.')
check(notices[#notices]=='Speak with the market vendor nearby before buying.','Ordinary later failure lost')
receiver(packet(nil,'LEVEL 20 milestone'));check(notices[#notices]=='LEVEL 20 milestone','Later milestone lost')
count=#notices;receiver(packet(nil,nil));check(#notices==count,'Silent state produced a notice')
local critical=packet('Saving is unavailable.','LEVEL 30 milestone');critical.messageUrgent=true;receiver(critical)
check(notices[count+1]=='LEVEL 30 milestone','Critical packet lost milestone')
check(#notices==count+2 and notices[#notices]=='Saving is unavailable.' and urgentNotices[#urgentNotices],'Same-packet milestone hid critical warning')
print('PASS '..checks..' actual action feedback checks; synthetic client UI/time and server helpers')
'''
reproduce = '--reproduce' in sys.argv
checks = checks.replace('CHECK_REJECTION', "check(#notices==1,'Expected baseline suppression missing')" if reproduce else "check(notices[#notices]=='Micro-speaker costs 250 coins. You need 240 more.','Milestone hid upgrade rejection')")
checks = checks.replace('CHECK_REWARD', "check(#notices==1,'Expected baseline reward suppression missing')" if reproduce else "check(notices[#notices]=='Quest reward · +100 XP · +40 coins','Milestone hid reward confirmation')")
checks = checks.replace('CHECK_COMPLETE', "check(#notices==1,'Expected baseline completion suppression missing')" if reproduce else "check(notices[#notices]=='Quest complete! Claim your reward in Quests.','Milestone hid task completion')")
payload = setup+receiver+speaker+'\nlocal function claim(p,s,arg)\n'+claim+'\nend\n'+checks

def run(source, failure=None):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', dir=root/'tests', delete=False) as f:
        path=Path(f.name);f.write(source)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
        if failure:
            assert result.returncode!=0 and failure in result.stderr, result.stdout+result.stderr
            print('PASS negative control: '+failure)
        else:
            print(result.stdout,end='');assert result.returncode==0,result.stderr
    finally:
        path.unlink()

run(payload)
if reproduce:
    print('REPRODUCED: authoritative upgrade rejection, reward confirmation and completion disappear inside the milestone window; debit/reward guards remain correct.')
if '--negative-controls' in sys.argv:
    run(payload.replace('if data.message and (not newMilestone or data.messageUrgent) then','if data.message and os.clock()>=106 then'), 'Milestone hid upgrade rejection')
    run(payload.replace('data.milestone~=lastMilestone','(data.milestone~=lastMilestone or not data.message)'), 'Repeated milestone snapshots replayed a notification')
    run(payload.replace('not v.claimed and v.progress>=q.goal','v.progress>=q.goal'), 'Repeated claim duplicated reward/notice')
    run(payload.replace('(not newMilestone or data.messageUrgent)', '(not newMilestone)'), 'Same-packet milestone hid critical warning')
