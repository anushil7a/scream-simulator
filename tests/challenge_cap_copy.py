"""Actual challenge-card loop and authoritative completion helpers; fake UI/session.
No native text-fit, persistence or multiplayer claim. Controls are opt-in.
"""
from pathlib import Path
import argparse, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
CLIENT='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
SERVER='src/ServerScriptService/Bootstrap.server.luau'
def build(client,server):
    a=client.index('  for _,spec in ipairs(Config.Progression.Challenges) do')
    card=client[a:client.index('\n  info("Training:',a)]
    a=server.index('local function xp(')
    xp=server[a:server.index('\nlocal function ',a+1)]
    a=server.index('local function combatChallenge(')
    challenge=server[a:server.index('\nlocal function ',a+1)]
    return '''local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local Config={MaxLevel=Progression.MaxLevel,Progression=Progression,XPToNext=Progression.XPToNext,Sounds={}}
local p={};local sessions={};local data;local messages={};local notices={};local multiplier=1
local Commerce={Multiplier=function()return multiplier end}
local VoiceCombat={Stats=function()return {health=100,maxDps=1}end}
local function syncHealth()end
local function state(_,message)table.insert(notices,message)end
local function info(text)table.insert(messages,text)end
local function render(value)data=value;messages={}
'''+card+'\nreturn table.concat(messages," | ") end\n'+xp+'\n'+challenge+CHECKS
CHECKS='''
local checks=0;local function check(ok,message)assert(ok,message);checks+=1 end
local function reset(level,experience)
 local d={level=level,xp=experience,combatChallenges={fighters=2},coins=17}
 sessions[p]={data=d};notices={};return d
end
local d=reset(100,0)
local text=render(d)
check(text:find('MAX LEVEL · no XP awarded',1,true)~=nil,'Capped card promises unavailable XP')
check(not text:find('+200 XP',1,true),'Capped nominal reward still shown')
check(text:find('2/3',1,true) and text:find('renews automatically',1,true),'Counter or renewal missing')
check(d.combatChallenges.fighters==2 and d.xp==0,'Renderer mutated progression')
local nominal,credited=combatChallenge(p,'fighters',false)
check(nominal==200 and credited==0 and d.xp==0 and d.level==100,'Capped payout changed')
check(d.combatChallenges.fighters==0 and d.coins==17,'Capped challenge did not renew independently')
check(notices[#notices]:find('+0 XP',1,true)~=nil,'Capped completion feedback incorrect')
check(render(d):find('0/3',1,true)~=nil,'Renewed counter stale')
for _,level in ipairs({1,60,99})do
 d=reset(level,0);local reward=Progression.ChallengeXP(level);text=render(d)
 check(text:find('+'..reward..' XP on completion',1,true)~=nil,'Below-cap reward copy changed')
 check(not text:find('MAX LEVEL',1,true),'Below-cap mislabeled capped')
 nominal,credited=combatChallenge(p,'fighters',false)
 check(nominal==reward and credited==reward and d.xp==reward and d.level==level,'Below-cap payout changed')
 check(d.combatChallenges.fighters==0,'Below-cap renewal changed')
end
d=reset(99,Config.XPToNext(99)-7);multiplier=2
nominal,credited=combatChallenge(p,'fighters',false)
check(nominal==200 and credited==7 and d.level==100 and d.xp==0,'Near-cap boosted payout changed')
check(render(d):find('MAX LEVEL · no XP awarded',1,true)~=nil,'Post-level-up card not cap-aware')
check(d.combatChallenges.fighters==0,'Near-cap renewal changed')
print('PASS '..checks..' actual challenge card/completion checks')
'''
def run(client,server):
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',prefix='tmp_challenge_',dir=ROOT/'tests',delete=False) as f:
        path=Path(f.name);f.write(build(client,server))
    try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True)
    finally:path.unlink()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
    client=(ROOT/CLIENT).read_text(encoding='utf-8');server=(ROOT/SERVER).read_text(encoding='utf-8')
    if args.baseline:
        client=subprocess.check_output(['git','show','b402c3f:'+CLIENT],cwd=ROOT,text=True,encoding='utf-8')
        result=run(client,server)
        assert result.returncode and 'Capped card promises unavailable XP' in result.stderr,result.stdout+result.stderr
        print('PASS pinned b402c3f actual renderer reproduces capped XP promise');return
    result=run(client,server);assert result.returncode==0,result.stdout+result.stderr;print(result.stdout.strip())
    if args.negative_controls:
        cases=[('cap guard',client.replace('data.level>=Config.MaxLevel and "MAX LEVEL · no XP awarded"','false and "MAX LEVEL · no XP awarded"',1),server,'Capped card promises'),('early cap',client.replace('data.level>=Config.MaxLevel and "MAX LEVEL · no XP awarded"','data.level>=99 and "MAX LEVEL · no XP awarded"',1),server,'Below-cap reward copy'),('renewal',client,server.replace('local reward,name=Config.Progression.Advance(s.data.combatChallenges,id,s.data.level)','local reward,name=200,"Challenge"',1),'Capped challenge did not renew'),('payout',client,server.replace('local credited=math.max(0,math.floor(amount))','local credited=0',1),'Below-cap payout changed')]
        for name,c,s,diagnostic in cases:
            assert c!=client or s!=server,name
            result=run(c,s);assert result.returncode and diagnostic in result.stderr,name+result.stdout+result.stderr
        print('PASS 4 targeted negative controls')
if __name__=='__main__':main()
