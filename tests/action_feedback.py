"""Actual State receiver and server action helpers; simulated UI/time, no network/store."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
client = (root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server = (root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
receiver = client[client.index('local lastMilestone'):client.index('connectClient(UIS.InputBegan')]
speaker = server[server.index('local function gearAction('):server.index('local function vendorPurchase(')]
start = server.index(' elseif verb=="ClaimQuest" then') + len(' elseif verb=="ClaimQuest" then')
claim = server[start:server.index(' elseif verb=="SetSettings"', start)]
setup = '''
local now=100;local os={clock=function()return now end}
local academy={refreshGuide=function()end,refreshZone=function()end,refreshTestLauncher=function()end}
local notifications={Remove=function()end}
local notices={};local urgentNotices={};local receiver;local data;local p={SetAttribute=function()end};local earned=0;local stops=0
local function notify(message,urgent)table.insert(notices,message);table.insert(urgentNotices,urgent==true)end
-- Account eligibility lifecycle is exercised by voice_eligibility.py; this fixture isolates notifications.
local function observeVoiceEligibility()end
local function cueContext()end;local gameplayAudio={ObserveLevel=function()end}
local remotes={State={OnClientEvent={}}}
local function connectClient(_,fn)receiver=fn end
local Config={Gear=require("../src/ReplicatedStorage/Shared/GearCatalog"),MaxLevel=100,MicroSpeakerPrice=200,Quests={{id='garden',goal=3}},GetQuest=function(id)
 if id=='garden' then return {id='garden',name='Garden',goal=3,coins=40,xp=100,event='Garden'} end
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
local function coins(_,amount)s.data.coins+=amount;return amount end
local function xp(_,amount)earned+=amount;return amount end
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
checks = checks.replace('CHECK_REJECTION', "check(#notices==1,'Expected baseline suppression missing')" if reproduce else "check(notices[#notices]=='Need '..(Config.Gear.Get('MicroSpeaker').price-10)..' more coins.','Milestone hid upgrade rejection')")
checks = checks.replace('CHECK_REWARD', "check(#notices==1,'Expected baseline reward suppression missing')" if reproduce else "check(notices[#notices]=='Quest reward · +100 XP · +40 coins','Milestone hid reward confirmation')")
checks = checks.replace('CHECK_COMPLETE', "check(#notices==1,'Expected baseline completion suppression missing')" if reproduce else "check(notices[#notices]=='Quest complete! Claim your reward in Quests.','Milestone hid task completion')")
# Client label and server reward helper have separate namespaces in production.
payload = setup+'\ndo local coins={}\n'+receiver+'\nend\n'+speaker+'\nlocal function claim(p,s,arg)\n'+claim+'\nend\n'+checks

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

# Use the actual queue with the State receiver and its frame-bound idle handoff.
gear_setup = setup.replace(
    'local function notify(message,urgent)table.insert(notices,message);table.insert(urgentNotices,urgent==true)end',
    """local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local notifications
local function notify(message,urgent,key)notifications:Push(message,urgent,key)end""",
)
render_hint = client.split('connectClient(Run.RenderStepped,function(dt)\n -- The optional gear hint', 1)[1]
render_hint = ' -- The optional gear hint' + render_hint.split(' local notice=notifications:Step(0,false)', 1)[0]
gear_checks = r"""
local function update(coins, options, message)
 local d=packet(message)
 d.coins=coins
 for k,v in pairs(options or {}) do d[k]=v end
 receiver(d)
end
local function frame()
 frameHint()
 return notifications:Step(.1,true)
end
local function waitFor(text)
 for _=1,150 do if frame()==text then return true end end
 return false
end
local n=0;local function check(value,message) assert(value,message);n+=1 end
local hint='Academy Megaphone ready to buy · MENU → GEAR'
Config.CompactCity=true
reset();update(130)
check(frame()=='','Existing wallet was mistaken for freshly earned coins')
reset();update(80);update(99)
check(frame()=='','Hint appeared below the catalog price')
update(100,{savingAvailable=false},'Level 2')
check(frame()=='Level 2','Gear hint displaced the level notice')
update(100,nil,'Quest reward')
local seen={}
for _=1,145 do
 local value=frame()
 if value~='' and value~=seen[#seen] then table.insert(seen,value) end
 if value==hint then break end
end
check(#seen==3 and seen[1]=='Level 2' and seen[2]=='Quest reward' and seen[3]==hint,
 'Gear hint missing after the real notices drained')
update(100,{megaphoneOwned=true})
check(frame()=='','Buying the item left stale affordability text')
update(20);update(130)
check(frame()=='','Repeated crossing replayed an already shown hint')
reset();update(80);update(130,nil,'Reward');update(90)
check(not waitFor(hint) and frame()=='','Falling below price left a queued hint')
reset();update(80);update(130,nil,'Reward');update(130,{megaphoneOwned=true})
check(not waitFor(hint) and frame()=='','Ownership did not cancel a pending hint')
reset();update(80);update(130,{testSession=true})
check(frame()=='','Temporary test coins advertised the gear')
update(130)
check(frame()=='','Leaving test mode was mistaken for an earning event')
Config.ResonanceLayout=true
reset();update(80);update(130)
check(frame()=='','City guidance leaked into Resonance Hall')
print('PASS '..n..' actual gear affordability/queue checks; simulated State and render timing')
"""
gear_payload = gear_setup + '\nlocal frameHint\nlocal function reset()\n local coins={}\n notifications=Queue.new()\n' + receiver + '\n frameHint=function()\n' + render_hint + '\n end\nend\n' + gear_checks
run(gear_payload)
if '--negative-controls' in sys.argv:
    for before, after, expected in (
        ('starterGear.lastCoins and starterGear.lastCoins<item.price', 'true', 'Existing wallet was mistaken'),
        ('and not notifications.active then', 'then', 'Gear hint missing after the real notices drained'),
        ('   starterGear.pending=nil\n   notifications:Remove("starterGear")', '   notifications:Remove("starterGear")', 'Falling below price left a queued hint'),
        ('   notifications:Remove("starterGear")', '', 'Buying the item left stale affordability text'),
        ('not starterGear.shown and starterGear.lastCoins', 'starterGear.lastCoins', 'Repeated crossing replayed'),
    ):
        assert before in gear_payload
        run(gear_payload.replace(before, after, 1), expected)
if reproduce:
    print('REPRODUCED: authoritative upgrade rejection, reward confirmation and completion disappear inside the milestone window; debit/reward guards remain correct.')
if '--negative-controls' in sys.argv:
    run(payload.replace('if data.message and (not newMilestone or data.messageUrgent) then','if data.message and os.clock()>=106 then'), 'Milestone hid upgrade rejection')
    run(payload.replace('data.milestone~=lastMilestone','(data.milestone~=lastMilestone or not data.message)'), 'Repeated milestone snapshots replayed a notification')
    run(payload.replace('not v.claimed and v.progress>=q.goal','v.progress>=q.goal'), 'Repeated claim duplicated reward/notice')
    run(payload.replace('(not newMilestone or data.messageUrgent)', '(not newMilestone)'), 'Same-packet milestone hid critical warning')
