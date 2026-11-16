"""Execute actual BossService with deterministic mocked Instances/players, not native physics."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
cat=(root/'src/ReplicatedStorage/Shared/BossCatalog.luau').read_text()
layout=(root/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
motion=(root/'src/ReplicatedStorage/Shared/BossMotion.luau').read_text()
patterns=(root/'src/ReplicatedStorage/Shared/BossPatterns.luau').read_text()
rules=(root/'src/ReplicatedStorage/Shared/BossRules.luau').read_text()
service=(root/'src/ServerScriptService/BossService.luau').read_text().split('local Service={}',1)[1]
setup=r'''
workspace={GetServerTimeNow=function()return 10000 end}
local V={};V.__index=function(t,k) if k=="Magnitude" then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z) elseif k=="Unit" then return t/t.Magnitude else return V[k] end end
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return Vector3.new(a.X/b,a.Y/b,a.Z/b)end
Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
Color3={fromRGB=function(...)return {...}end};UDim2={fromOffset=function(...)return {...}end,fromScale=function(...)return {...}end}
local CF={};CF.__mul=function(a,b)return a end
CFrame={new=function(pos)return setmetatable({Position=pos},CF)end,Angles=function(...)return setmetatable({},CF)end}
Enum={Material={Neon=1},PartType={Cylinder=1}}
local labelWrites=0
Instance={new=function(class)
 local attrs={}
 local values={SetAttribute=function(_,k,v)attrs[k]=v end,GetAttribute=function(_,k)return attrs[k]end,ClassName=class,Destroy=function(self)self.destroyed=true end}
 return setmetatable({}, {__index=values,__newindex=function(_,key,value)
  if class=="TextLabel" and key=="Text" then labelWrites+=1 end
  if key=="CFrame" and value.Position then values.Position=value.Position end
  values[key]=value
 end})
end}
'''
tests=r'''
local checks=0
local function check(v,message)assert(v,message);checks+=1 end
local users={};local contexts={};local rewards={};local damage={}
Catalog.Entries[1].y=32 -- exercise elevated terrain without changing production catalog
local service=Service.new({}, {
 player=function(id)return users[id]end,
 context=function(p)return contexts[p.UserId]end,
 reward=function(p,spec,share)table.insert(rewards,{id=p.UserId,coins=math.floor(spec.coins*share),xp=math.floor(spec.xp*share)})end,
 damage=function(p,amount)table.insert(damage,{p=p,amount=amount})end,
})
check(#service.bosses==#Catalog.Entries,"all catalog bosses constructed")
check(service.bosses[1].center.Y==32 and service.bosses[1].root.Position.Y==39,"elevated boss ground/anchor")
check(service.bosses[1].root.Transparency==1,"obsolete box body visible")
local beforeIdle=labelWrites
for tick=1,100 do service:Step(tick*.11) end
check(labelWrites-beforeIdle<=#Catalog.Entries,"idle labels rewritten each tick")
print("Idle boss label writes over 100 ticks: "..(labelWrites-beforeIdle).." (previous source: 500)")
local targetLists={};for _,b in ipairs(service.bosses) do targetLists[b]=b.targets;check(type(b.targets)=="table","missing reusable targets") end
service:Step(12)
for b,list in pairs(targetLists) do check(b.targets==list,"idle target list churn") end
service.nextStep=0

local byId={};for _,b in ipairs(service.bosses) do byId[b.spec.id]=b end
local expected={metronome=10,golem=30,ignis=50,leviathan=70,conductor=95}
local count=0;for id,level in pairs(expected) do count+=1;check(byId[id] and byId[id].spec.level==level,"exact requested boss level: "..id) end
check(#service.bosses==count,"exact roster")
local function player(id,b,level)
 local p={UserId=id};users[id]=p;contexts[id]={identity={},position=b.center+Vector3.new(0,3,10),level=level or b.spec.level};return p
end
for _,b in ipairs(service.bosses) do
 service.nextStep=0
 local p=player(1,b,b.spec.level-1)
 check(not service:CanHit(b,p,1),"level gate")
 contexts[1].level=b.spec.level
 check(service:CanHit(b,p,1),"eligible hit")
 contexts[1].position=b.center+Vector3.new(23,3,0)
 check(not service:CanHit(b,p,1),"outside radius")
 contexts[1].position=b.center+Vector3.new(0,13,0)
 check(not service:CanHit(b,p,1),"roof sniping")
 contexts[1].position=b.center+Vector3.new(0,3,10)
 local hp=b.health
 check(service:Hit(b,p,0/0,1)==0 and b.health==hp,"NaN")
 check(service:Hit(b,p,math.huge,1)==0,"infinity")
 check(service:Hit(b,p,-1,1)==0,"negative")
 local q=player(2,b)
 local before=#rewards
 service:Hit(b,p,hp*.6,2);service:Hit(b,q,hp,3)
 check(b.health==0 and b.readyAt==3+Catalog.Respawn,"KO cooldown")
 check(#b.targets==0,"KO retained participant references")
 check(#rewards==before+2,"assist and finisher rewarded")
 check(rewards[#rewards].coins+rewards[#rewards-1].coins<=b.spec.coins,"bounded coin pot")
 check(rewards[#rewards].xp+rewards[#rewards-1].xp<=b.spec.xp,"bounded XP pot")
 check(service:Hit(b,p,100,4)==0 and #rewards==before+2,"no duplicate KO")
 local respawn=4+Catalog.Respawn
 service:Step(respawn);check(b.health==hp,"respawn")
 service:Hit(b,p,hp,respawn+1);check(#rewards==before+2,"per-player cooldown")
 service:Step(respawn+Catalog.Respawn+2);check(b.health==hp,"second respawn")
end
-- Exercise each exact catalog cadence/footprint and fixed aim independently.
for _,b in ipairs(service.bosses) do
 local now=1000;Rules.Reset(b,b.spec,now);service.nextStep=0;b.turn=0
 local p=player(20,b);service:Hit(b,p,1,now+2)
 for i=1,2 do
  now=1002+(i-1)*b.spec.interval
  service:Step(now)
  check(b.strike and #b.strike.shapes>0,"catalog footprint "..b.spec.id)
  check(math.abs(b.strike.at-now-b.spec.windup)<.001,"catalog tell "..b.spec.id)
  check(math.abs(b.nextAttack-now-b.spec.interval)<.001,"catalog cadence "..b.spec.id)
  check(#b.strike.shapes<=16,"bounded markers "..b.spec.id)
  service:Step(now+b.spec.windup+.11)
 end
end
-- New instance isolates times/cooldowns for deterministic telegraph tests.
local b=byId.metronome;Rules.Reset(b,b.spec,400);service.nextStep=0
local p=player(3,b);local bystander=player(4,b)
local before=#damage
service:Step(401);check(not b.strike,"no proximity aggression")
service:Hit(b,p,10,402);service:Step(402)
check(b.strike and b.strike.at==403.5,"full fixed 1.5 second tell")
local fixed=b.strike.shapes[1]
contexts[3].position=b.center+Vector3.new(10,3,0)
service:Step(403.6);check(#damage==before,"move off fixed point avoids strike")
service:Step(407);check(b.strike~=nil,"second strike")
contexts[3].position=b.center+Vector3.new(b.strike.shapes[1].x,3,b.strike.shapes[1].z)
service:Step(409);check(#damage==before+1 and damage[#damage].p==p,"only participant hit")
service:Step(412);check(b.strike~=nil,"next strike")
contexts[3].position=b.center+Vector3.new(23,3,0)
service:Step(414);check(#damage==before+1,"escape ring avoids damage")
check(b.credit[3]==nil,"escape removes credit")
service:Step(425);check(b.health==b.spec.health and b.strike==nil,"idle reset cleans warning and credit")
contexts[3].position=b.center+Vector3.new(17,3,0)
service:Hit(b,p,10,427);service:Step(427)
check(#b.strike.shapes==1,"edge pattern fixed")
local old=contexts[3].identity;contexts[3].identity={}
service:Step(428);check(#damage==before+1 and b.credit[3]==nil,"session identity prevents stale hit")
local e={identity=old,damage=b.spec.health,at=1}
check(not Rules.Eligible(e,old,b.spec,22),"expired contribution cannot collect")
check(not Rules.Eligible(e,{},b.spec,2),"reconnect cannot collect")
check(not Rules.Eligible({identity=old,damage=1,at=1},old,b.spec,2),"AFK threshold")
-- Every shape's true corners/circumference stay inside the public boundary.
for _,spec in ipairs(Catalog.Entries) do
 check(spec.scale==1.4 and spec.aimHeight==7 and spec.engageHeight==12,"shared scale/range definition")
 for turn=1,4 do
  local pattern=Patterns.Build(spec.id,turn,18,0)
  for _,shape in ipairs(pattern.shapes) do
   if shape.kind=="disk" then
    check(math.sqrt(shape.x^2+shape.z^2)+shape.radius<=18,"disk containment")
   else
    for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
     local x=sx*shape.width/2;local z=sz*shape.length/2
     local wx=shape.x+math.cos(shape.angle)*x+math.sin(shape.angle)*z
     local wz=shape.z-math.sin(shape.angle)*x+math.cos(shape.angle)*z
     check(math.sqrt(wx^2+wz^2)<=18,"bar containment")
    end end
   end
   check(Patterns.Contains(shape,shape.x,shape.z),"shape center hit")
   check(not Patterns.Contains(shape,100,100),"outside shape miss")
  end
 end
 local boss=byId[spec.id];Rules.Reset(boss,spec,2000)
 local attacker=player(90,boss)
 for _,off in ipairs({Vector3.new(22.001,3,0),Vector3.new(0,12.001,0),Vector3.new(0,-12.001,0),Vector3.new(0/0,3,0),Vector3.new(math.huge,3,0)}) do
  contexts[90].position=boss.center+off
  check(not service:CanHit(boss,attacker,2002),"authoritative admission outside/invalid")
  check(service:Hit(boss,attacker,100,2002)==0 and boss.health==spec.health,"direct damage cannot bypass admission")
 end
 contexts[90].position=boss.center+Vector3.new(22,12,0)
 check(service:CanHit(boss,attacker,2002),"inclusive exact limits")
 service:Hit(boss,attacker,1,2002);service.nextStep=0;service:Step(2002)
 local warning=boss.warning
 contexts[90].position=boss.center+Vector3.new(23,3,0)
 service:Step(2002.2)
 check(not boss.strike and not boss.warning and warning.destroyed,"empty encounter cancels before impact")
 -- A fresh cast locks its participant set; late opt-ins get the next full tell.
 Rules.Reset(boss,spec,2100);service.nextStep=0
 contexts[90].position=boss.center+Vector3.new(0,3,10)
 service:Hit(boss,attacker,1,2102);service:Step(2102)
 local shape=boss.strike.shapes[1]
 contexts[90].position=boss.center+Vector3.new(shape.x,3,shape.z)
 local late=player(91,boss);contexts[91].position=contexts[90].position
 local bystander=player(92,boss);contexts[92].position=contexts[90].position
 service:Hit(boss,late,1,2102.2)
 local n=#damage;local oldWarning=boss.warning
 service:Step(2102+spec.windup+.1)
 check(#damage==n+1 and damage[#damage].p==attacker,"one impact, no late or passive victim")
 check(oldWarning.destroyed and not boss.warning,"impact marker cleanup")
 service:Step(2102+spec.windup+.3)
 check(#damage==n+1,"impact cannot repeat")
 Rules.Reset(boss,spec,2200);service.nextStep=0
 service:Hit(boss,attacker,1,2202);service:Step(2202)
 oldWarning=boss.warning
 service:Hit(boss,attacker,spec.health,2202.1)
 check(oldWarning.destroyed and not boss.strike and not boss.warning,"KO cancels pending hazard")
end
-- Pure authoritative patrol: deterministic, bounded, speed-capped even after stalls.
for _,spec in ipairs(Catalog.Entries) do
 local a,c=Motion.New(),Motion.New()
 for i=1,500 do
  local x,z=a.x,a.z
  Motion.Step(a,spec,.1);Motion.Step(c,spec,.1)
  check(a.x==c.x and a.z==c.z and a.yaw==c.yaw,"deterministic patrol")
  check(a.x*a.x+a.z*a.z<=spec.moveLeash^2+.0001,"patrol never leaves inner leash")
  check(math.sqrt((a.x-x)^2+(a.z-z)^2)<=spec.moveSpeed*.1+.0001,"patrol speed bound")
 end
 local x,z=a.x,a.z;Motion.Step(a,spec,100)
 check(math.sqrt((a.x-x)^2+(a.z-z)^2)<=spec.moveSpeed*.25+.0001,"stall cannot teleport")
 for turn=1,2 do
  local pattern=Patterns.Build(spec.id,turn,22,0)
  for _,shape in ipairs(pattern.shapes) do
   if shape.kind=="disk" then
    check(math.sqrt(shape.x^2+shape.z^2)+shape.radius+spec.moveLeash<=spec.radius,"translated disk bound")
   else
    for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
     local x,z=sx*shape.width/2,sz*shape.length/2
     local wx=shape.x+math.cos(shape.angle)*x+math.sin(shape.angle)*z
     local wz=shape.z-math.sin(shape.angle)*x+math.cos(shape.angle)*z
     check(math.sqrt(wx^2+wz^2)+spec.moveLeash<=spec.radius,"translated true corner bound")
    end end
   end
  end
 end
 local boss=byId[spec.id];Rules.Reset(boss,spec,3000);boss.recoverUntil=0;service.nextStep=0
 local attacker=player(100,boss);service:Hit(boss,attacker,1,3002);service:Step(3002)
 check(boss.model:GetAttribute("BossState")=="Windup","replicated windup state")
 local x,z,yaw=boss.motion.x,boss.motion.z,boss.motion.yaw
 local shape=boss.strike.shapes[1];local sx,sz=shape.x,shape.z
 service:Step(3002.2)
 check(boss.motion.x==x and boss.motion.z==z and boss.motion.yaw==yaw,"pose frozen during warning")
 check(shape.x==sx and shape.z==sz,"ground warning never follows core/player")
 service:Step(3002+spec.windup+.1)
 check(boss.model:GetAttribute("BossState")=="Recovery","replicated recovery state")
 service:Step(3002+spec.windup+.3)
 check(boss.motion.x==x and boss.motion.z==z,"recovery settles boss")
 service:Step(3002+spec.windup+.8)
 check(boss.model:GetAttribute("BossState")=="Moving","patrol resumes after recovery")
 local center=boss.center
 check(center.X==spec.x and center.Z==spec.z,"range home never follows moving root")
 contexts[100].position=center+Vector3.new(22.01,3,0)
 check(service:Hit(boss,attacker,10,3006)==0,"moving toward player never extends admission")
 contexts[100].position=center+Vector3.new(0,3,0)
 service:Hit(boss,attacker,spec.health,3007)
 check(boss.model:GetAttribute("BossState")=="Defeated","KO state immediate")
 x,z=boss.motion.x,boss.motion.z;service:Step(3008)
 check(boss.motion.x==x and boss.motion.z==z,"no dead patrol")
 service:Step(3007+Catalog.Respawn)
 check(boss.motion.x==0 and boss.motion.z==0 and boss.model:GetAttribute("BossState")=="Idle","respawn clean home pose")
end
-- Captain reskin retains slot and progression while changing the mechanical theme.
local captain=byId.leviathan.spec
check(captain.name=="Seagull Siren Captain" and captain.level==70,"captain public name and exact level")
check(captain.health==1280 and captain.damage==36 and captain.coins==95 and captain.xp==340,"captain unchanged balance")
check(captain.x==420 and captain.y==0 and captain.z==420 and captain.radius==22,"captain existing pier arena")
for _,angle in ipairs({0,math.pi/4,math.pi/2,math.pi}) do
 local dx,dz=math.sin(angle),math.cos(angle)
 local cutlass=Patterns.Build("leviathan",1,dx*10,dz*10)
 local sirens=Patterns.Build("leviathan",2,dx*10,dz*10)
 check(#cutlass.shapes==1 and #sirens.shapes==2,"captain distinct bounded pattern counts")
 check(Patterns.Hits(cutlass,dx*8,dz*8),"cutlass forward broadside danger")
 check(not Patterns.Hits(cutlass,0,0),"cutlass retreat safe")
 check(not Patterns.Hits(cutlass,-dx*8,-dz*8),"cutlass behind safe")
 check(not Patterns.Hits(sirens,dx*10,dz*10),"dual siren middle gap safe")
 check(Patterns.Hits(sirens,math.cos(angle)*6,-math.sin(angle)*6),"dual siren shoulder lane danger")
 check(not Patterns.Hits(sirens,dx*16,dz*16),"dual siren outer escape safe")
end
print("Boss service: "..checks.." assertions passed (mocked)")
'''
code=setup+'\nlocal Layout=(function()\n'+layout+'\nend)()\nlocal script={Parent={CompactLayout="CompactLayout"}}\nlocal function require(name) assert(name=="CompactLayout");return Layout end\nlocal Catalog=(function()\n'+cat+'\nend)()\nlocal Rules=(function()\n'+rules+'\nend)()\nlocal Motion=(function()\n'+motion+'\nend)()\nlocal Patterns=(function()\n'+patterns+'\nend)()\nlocal Service=(function()\nlocal Service={}'+service+'\nend)()\n'+tests
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:f.write(code);name=f.name
try:subprocess.run(['luau',name],check=True,cwd=root)
finally:Path(name).unlink()
# Execute actual bootstrap adapter callbacks with service construction intercepted.
server=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
block=server[server.index('-- Bosses are separate'):server.index('local function stepTraining(')]
pre=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local callbacks
local script={Parent={BossService={}}};local workspace={ScreamSimulatorWorld={}}
local require=function()return {new=function(_,cb)callbacks=cb;return {}end}end
local Config={CompactCity=true,HealQuietSeconds=12,InArena=function(p)return p.arena end}
local sessions={};local fixture=false
local Players={GetPlayerByUserId=function(_,id)return id end}
local function canDamageBots(s)return s~=nil and (s.testBaseline==nil or fixture)end
local function parts(p)return {},p.root,p.h end
local rewards={coins=0,xp=0};local function coins(_,n)rewards.coins+=n end;local function xp(_,n)rewards.xp+=n end
local function state()end
local ejected=0;local function eject()ejected+=1 end
local bosses
'''
post=r'''
local p={root={Position={}},h={Health=100}}
sessions[p]={data={level=95},rewardIdentity={},micReady=false,protectedUntil=0,dodgingUntil=0}
check(callbacks.context(p,1)~=nil,"mic toggling must not undo participation")
sessions[p].testBaseline={};check(callbacks.context(p,1)==nil,"live test-mode isolation")
fixture=true;check(callbacks.context(p,1)~=nil,"guarded local fixture usable")
fixture=false;sessions[p].testBaseline=nil;sessions[p].protectedUntil=10
check(callbacks.context(p,1)==nil,"protected state admission")
callbacks.damage(p,20,1);check(p.h.Health==100,"protected players unharmed")
sessions[p].protectedUntil=0;sessions[p].dodgingUntil=10
callbacks.damage(p,20,1);check(p.h.Health==100,"dodge avoids hazard")
sessions[p].dodgingUntil=0;callbacks.damage(p,20,1)
check(p.h.Health==80 and sessions[p].nextHeal==13,"normal damage and healing delay")
callbacks.damage(p,90,1);check(ejected==1,"lethal damage uses existing safe ejection")
callbacks.reward(p,{name="Boss",coins=35,xp=100},.31)
check(rewards.coins==10 and rewards.xp==31,"fractional share rounded down")
p.root.Position.arena=true;check(callbacks.context(p,1)==nil,"arena isolation")
print("Boss bootstrap callbacks: "..checks.." assertions passed (mocked)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:f.write(pre+block+post);name=f.name
try:subprocess.run(['luau',name],check=True,cwd=root)
finally:Path(name).unlink()
assert 'add("boss:"..boss.spec.id,{boss=boss})' in server
assert 'dealt+=bosses:Hit(target.boss,p,hit.damage,now)' in server
assert 'bosses:Hit(boss,p,sound.damage,now)' in server
assert 'if bosses then bosses:Step(now) end' in server
print('Boss sustained/legacy/heartbeat wiring source contracts passed')
