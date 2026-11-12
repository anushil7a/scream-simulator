"""Actual dev/reward/Profile fake-store lifecycle, not live saves or multiplayer transport."""
import test_session_rewards as base
import sys,re
CHECKS=r'''
local function acquire(p)
 local data,writable=Profiles.Load(p.UserId);check(writable,'Fake acquisition failed')
 sessions[p]={rewardIdentity={},data=data,canSave=true,voice=Combat.New(),credit={},protectedUntil=0,dodgingUntil=0};return sessions[p]
end
check(Access.PrelaunchAllTesters==true,'Prelaunch flag not enabled')
game.GameId=10769005350
local a=acquire(ordinary);local b=acquire(third)
local beforeA=Profiles.Sanitize(a.data);local beforeB=Profiles.Sanitize(b.data)
for _,command in ipairs({'bad',{},false})do dev(ordinary,command)end
check(a.testBaseline==nil,'Unknown command entered test mode')
busy=true;dev(ordinary,'MaxLevel');busy=false;check(a.testBaseline==nil,'Busy purchase entered test mode')
Access.PrelaunchAllTesters=false;dev(ordinary,'MaxLevel');check(a.testBaseline==nil,'Disabled prelaunch allowed tester command')
Access.PrelaunchAllTesters='true';dev(ordinary,'MaxLevel');check(a.testBaseline==nil,'Malformed flag authorized')
Access.PrelaunchAllTesters=true
for _,creator in ipairs({{Enum.CreatorType.Group,11499795799},{Enum.CreatorType.User,123},{Enum.CreatorType.User,'11499795799'}})do
 game.CreatorType=creator[1];game.CreatorId=creator[2];dev(ordinary,'MaxLevel');check(a.testBaseline==nil,'Foreign creator authorized tester')
end
game.CreatorType=Enum.CreatorType.User;game.CreatorId=11499795799
for _,universe in ipairs({123,0,-1,10769005350.5,'10769005350',0/0,math.huge,false})do
 game.GameId=universe;dev(ordinary,'MaxLevel');check(a.testBaseline==nil,'Wrong or malformed universe authorized tester')
end
game.GameId=nil;dev(ordinary,'MaxLevel');check(a.testBaseline==nil,'Missing universe authorized tester')
check(Access.IsAuthorized(owner,game.CreatorType,game.CreatorId,false,nil),'Owner historical access removed')
check(Access.IsAuthorized(ordinary,Enum.CreatorType.Group,0,true,nil),'Studio historical access removed')
game.GameId=10769005350
check(not Access.IsAuthorized(nil,game.CreatorType,game.CreatorId,false),'Nil player allowed')
dev(ordinary,'ResetBots');dev(ordinary,'StudioMovement');check(a.testBaseline==nil,'Restricted command entered test mode')
dev(ordinary,'AddLevels');dev(third,'AddLevels')
check(a.testBaseline.level==1 and b.testBaseline.level==1 and a.data.level==11 and b.data.level==11,'Both testers not isolated')
local function total(d)local n=d.xp;for i=1,d.level-1 do n+=Config.XPToNext(i)end;return n end
local function fight(attacker,victim,now)
 local vs=sessions[victim];local maximum=Config.HealthForLevel(vs.data.level)
 recordCredit(vs.credit,attacker,maximum,maximum,now)
 awardCombatKO(vs.credit,attacker,vs.data.level,maximum,100,now,victim)
end
local oldXP=total(a.data);local oldCoins=a.data.coins
fight(ordinary,third,100)
check(total(a.data)-oldXP==100 and a.data.coins-oldCoins==20,'Test PvP payout wrong')
check(next(rewardHistory.pairs)==nil and next(testRewardHistory.pairs)~=nil,'Test battle contaminated ordinary repeat history')
local awarded=total(a.data);fight(ordinary,third,101);check(total(a.data)==awarded,'Test repeat cooldown bypassed')
check(a.testBaseline.level==beforeA.level and a.testBaseline.xp==beforeA.xp and a.testBaseline.coins==beforeA.coins,'Attacker baseline mutated')
check(b.testBaseline.level==beforeB.level and b.testBaseline.xp==beforeB.xp and b.testBaseline.coins==beforeB.coins,'Victim baseline mutated')
autosave(ordinary,a);autosave(third,b)
check(durable['Player_'..ordinary.UserId].level==beforeA.level and durable['Player_'..ordinary.UserId].coins==beforeA.coins,'Autosave wrote test attacker')
check(durable['Player_'..third.UserId].level==beforeB.level and durable['Player_'..third.UserId].xp==beforeB.xp,'Autosave wrote test victim')
check(Profiles.Save(ordinary.UserId,a.testBaseline,true) and Profiles.Save(third.UserId,b.testBaseline,true),'Fake release failed')
a=acquire(ordinary);b=acquire(third)
check(a.data.level==beforeA.level and a.data.xp==beforeA.xp and a.data.coins==beforeA.coins and not a.testBaseline,'Attacker rejoin changed saved baseline')
check(b.data.level==beforeB.level and b.data.xp==beforeB.xp and b.data.coins==beforeB.coins and not b.testBaseline,'Victim rejoin changed saved baseline')
a.canSave=false;b.canSave=false;oldXP=total(a.data);oldCoins=a.data.coins
fight(ordinary,third,102)
check(total(a.data)-oldXP==100 and a.data.coins-oldCoins==20,'Test history suppressed ordinary Keep Playing rewards')
check(next(rewardHistory.pairs)~=nil,'Ordinary repeat history missing')
dev(third,'MaxLevel');oldXP=total(a.data);oldCoins=a.data.coins;fight(ordinary,third,200)
check(total(a.data)==oldXP and a.data.coins==oldCoins,'Mixed test victim paid ordinary attacker')
check(next(b.credit)==nil,'Rejected mixed credit not consumed')
print('PASS '..n..' actual prelaunch two-player reward/save/auth assertions; fake storage and sessions only')
'''
def build(mutation=None):
 code=base.build(mutation=mutation)
 assert code.endswith(base.FIXED)
 code=code[:-len(base.FIXED)]+CHECKS
 source=base.read('src/ServerScriptService/Bootstrap.server.luau')
 if mutation:source=mutation(source)
 declarations='\n'.join(re.findall(r'^local (?:testRewardHistory|rewardHistory)=.*$',source,re.M))
 code=code.replace('local rewardHistory={pairs={}};local testRewardHistory={pairs={}}',declarations)
 # Retained old-policy fixture explicitly disables prelaunch; this suite tests current flag.
 code=code.replace('Access.PrelaunchAllTesters=false -- retained owner-only policy','')
 return code
if __name__=='__main__':
 r=base.run(build());print(r.stdout,end='');assert r.returncode==0,r.stderr
 if '--negative-controls' in sys.argv:
  mutations=[('local testRewardHistory={pairs={}}','local testRewardHistory=rewardHistory','Test battle contaminated ordinary repeat history'),('rs.testBaseline and testRewardHistory or rewardHistory','rewardHistory','Test battle contaminated ordinary repeat history'),('s.testBaseline=Profiles.Sanitize(s.data);s.data=Profiles.Sanitize(s.data)','s.testBaseline=s.data','Both testers not isolated'),('s.testBaseline or s.data','s.data','Autosave wrote test attacker')]
  for old,new,error in mutations:
   def mutate(s):
    assert old in s;return s.replace(old,new)
   r=base.run(build(mutate));assert r.returncode and error in r.stderr,r.stdout+r.stderr
  print('PASS '+str(len(mutations))+' negative controls')
