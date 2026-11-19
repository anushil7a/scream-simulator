"""Actual isolated damage resolver/application, not native Roblox or real persistence."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
server=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
path=root/'src/ServerScriptService/CombatRules.luau'
rules=path.read_text().split('\n',1)[1]
block=server[server.index('local function resolveTestBeam('):server.index('local function sustainedContext(')]
for denied in ('awardCombatKO','recordCredit','questProgress','BossService','World.Bots','Commerce','coin','xp','reward','Destruction','Soccer','BeachVolley','FireAllClients'):
    assert denied not in block,denied
assert 'applyTestBeam(p,s,now,hits,details)' in server
assert 'pcall(Profiles.Save,p.UserId,s.testBaseline or s.data' in server
setup=r'''
local count=0;local function check(v,msg)assert(v,msg);count+=1 end
local V;local mt={}
V=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__sub=function(a,b)return V(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__mul=function(a,n)return V(a.X*n,a.Y*n,a.Z*n)end
mt.__index=function(a,k)
 if k=="Dot" then return function(x,y)return x.X*y.X+x.Y*y.Y+x.Z*y.Z end end
 if k=="Magnitude" then return (a.X*a.X+a.Y*a.Y+a.Z*a.Z)^.5 end
end
local Config={HealQuietSeconds=12,InArena=function(p)
 return p.X>=0 and p.X<=100 and p.Y>=0 and p.Y<=12 and p.Z>=0
end}
local sessions,players={},{}
local Players={GetPlayers=function()return players end}
local function player(id,x,y,z)
 local p={UserId=id,allowed=true,root={Position=V(x,y,z)},health={Health=100}}
 p.Character={key=id}
 local s={testBaseline={},protectedUntil=0,dodgingUntil=0,credit={},data={level=1,coins=15}}
 sessions[p]=s;table.insert(players,p)
 return p,s
end
local function parts(p)
 if p.health.Health>0 then return p.Character,p.root,p.health end
end
local function toolAuthorized(p)return p.allowed==true end
local cover,sight=nil,true
local function beamObstruction(_,_,_,_,seen)
 check(seen==players,"preview obstructed differently from real aiming")
 return cover and {Distance=cover}
end
local function audible(_,_,_,_)return sight end
local dealt,ejections,recordAt=0,0,nil
local function recordDamage(p,s,now,n)
 check(p.UserId==10 and s==sessions[p],"damage readout leaked across accounts")
 dealt+=n;recordAt=now
end
local function eject(p,h)
 check(p==players[2] and h==p.health,"ejected non-target/no normal ejection")
 ejections+=1;h.Health=100
end
local Rules=(function()
'''
checks=r'''
local p,s=player(10,10,3,10)
local paired,pairedSession=player(11,20,3,10)
local ordinary,ordinarySession=player(12,24,3,10);ordinarySession.testBaseline=nil
local other,otherSession=player(13,18,3,10);other.allowed=false
local direction=V(1,0,0);local stats={range=30,width=4}
local ctx={character=p.Character,root=p.root,origin=p.root.Position}
local function sample(now)
 local ids,data=resolveTestBeam(p,s,ctx,direction,stats,now or 5)
 return ids or {},data or {}
end
local ids,data=sample()
check(#ids==1 and ids[1]=="player:11" and data.length==30,"Only the legitimate paired test opponent should resolve")
check(data[ids[1]].player==paired,"Wrong target bound")
local before=pairedSession.credit
applyTestBeam(p,s,5,{{id=ids[1],damage=17}},data)
check(paired.health.Health==83 and pairedSession.nextHeal==17 and s.nextHeal==17,"actual isolated target HP not applied")
check(ordinary.health.Health==100 and other.health.Health==100,"Isolation bypass")
check(dealt==17 and recordAt==5 and pairedSession.credit==before and next(before)==nil,"private damage changed combat credit")
check(s.data.coins==15 and pairedSession.data.coins==15,"damage rewarded saved/session coins")
paired.health.Health=2
applyTestBeam(p,s,6,{{id=ids[1],damage=100}},data)
check(ejections==1 and dealt==19 and paired.health.Health==100,"KO did not eject once or overkill included")
applyTestBeam(p,s,6,{{id="object:x",damage=100},{id="player:12",damage=100}},data)
check(dealt==19 and ejections==1 and ordinary.health.Health==100,"Non-resolved target should never apply damage")
paired.health.Health=100
for _,case in ipairs({"coverLength","coverSight","targetRange","aligned","targetArena","originArena","targetDodge","targetProtected","originProtected","targetFlight","originFlight","noBaseline","revoked","dead"}) do
 cover=nil;sight=true;s.protectedUntil=0;pairedSession.protectedUntil=0;pairedSession.dodgingUntil=0
 s.flight=nil;pairedSession.flight=nil;paired.allowed=true;paired.health.Health=100;s.testBaseline={}
 p.root.Position=V(10,3,10);ctx.origin=p.root.Position;paired.root.Position=V(20,3,10)
 if case=="coverLength" then cover=6 elseif case=="coverSight" then sight=false
 elseif case=="targetRange" then paired.root.Position=V(50,3,10) elseif case=="aligned" then paired.root.Position=V(20,3,18)
 elseif case=="targetArena" then paired.root.Position=V(20,13,10) elseif case=="originArena" then p.root.Position=V(10,13,10)
 elseif case=="targetDodge" then pairedSession.dodgingUntil=8 elseif case=="targetProtected" then pairedSession.protectedUntil=8
 elseif case=="originProtected" then s.protectedUntil=8 elseif case=="targetFlight" then pairedSession.flight={}
 elseif case=="originFlight" then s.flight={} elseif case=="noBaseline" then s.testBaseline=nil
 elseif case=="revoked" then paired.allowed=false else paired.health.Health=0 end
 check(#sample()==0,"Illegal test damage target allowed: "..case)
end
print("PASS "..count.." real test beam targeting, HP and isolation assertions; synthetic only")
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    name=Path(f.name);f.write(setup+rules+'\nend)()\n'+block+checks)
try:
    subprocess.run(['luau',str(name)],cwd=root,check=True)
finally:
    name.unlink()
