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
Color3={fromRGB=function(...)return {...}end};UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end,fromScale=function(...)return {...}end}
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
 damage=function(p,amount,now,b,strike)table.insert(damage,{p=p,amount=amount,push=strike.push,kind=strike.kind,serial=strike.serial})end,
})
check(#service.bosses==#Catalog.Entries,"all catalog bosses constructed")
for _,b in pairs(service.bosses) do
 check(b.model:GetAttribute("BossHealth")==b.spec.health and b.model:GetAttribute("BossMaxHealth")==b.spec.health,"initial authoritative HP")
end
check(service.bosses[1].center.Y==32 and service.bosses[1].root.Position.Y==32+Catalog.Entries[1].aimHeight,"elevated boss ground/anchor")
check(service.bosses[1].root.Transparency==1,"obsolete box body visible")
local function nameplates()
 for _,b in ipairs(service.bosses) do
  check(b.label.Name=="NameAndLevel" and b.label.Text==b.spec.name.." · Lv "..b.spec.level and not b.label.TextWrapped,
    "nameplate contains descriptive or transient boss copy")
  check(b.label.Parent.Size[1]==296 and b.label.Parent.Size[2]==32 and b.label.Size[2]==-16
    and b.label.Position[1]==8,"nameplate lost the measured glyph/padding budget")
 end
end
nameplates()
local beforeIdle=labelWrites
for tick=1,100 do service:Step(tick*.11) end
check(labelWrites==beforeIdle,"identity labels rewritten in idle")
nameplates()
print("Static nameplate label writes over 100 ticks: "..(labelWrites-beforeIdle))
local targetLists={};for _,b in ipairs(service.bosses) do targetLists[b]=b.targets;check(type(b.targets)=="table","missing reusable targets") end
service:Step(12)
for b,list in pairs(targetLists) do check(b.targets==list,"idle target list churn") end
service.nextStep=0

local byId={};for _,b in ipairs(service.bosses) do byId[b.spec.id]=b end
local expected={metronome=10,golem=30,ignis=50,leviathan=70,conductor=95}
local count=0;for id,level in pairs(expected) do count+=1;check(byId[id] and byId[id].spec.level==level,"exact requested boss level: "..id) end
check(#service.bosses==count,"exact roster")
local function player(id,b,level)
 local p={UserId=id};users[id]=p;contexts[id]={identity={},position=b.center+Vector3.new(0,3,8),level=level or b.spec.level};return p
end
for _,b in ipairs(service.bosses) do
 service.nextStep=0
 local p=player(1,b,b.spec.level-1)
 check(not service:CanHit(b,p,1),"level gate")
 contexts[1].level=b.spec.level
 check(service:CanHit(b,p,1),"eligible hit")
 contexts[1].position=b.center+Vector3.new(b.spec.radius+1,3,0)
 check(not service:CanHit(b,p,1),"outside radius")
 contexts[1].position=b.center+Vector3.new(0,13,0)
 check(not service:CanHit(b,p,1),"roof sniping")
 contexts[1].position=b.center+Vector3.new(0,3,8)
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
-- In a melee cadence slot, a close participant wins over the distant
-- rotation target; if both are distant, the boss casts a ranged tell.
do
 local b=byId.metronome
 for _,close in ipairs({true,false}) do
  local now=close and 920 or 940
  Rules.Reset(b,b.spec,now);b.turn=1;service.nextStep=0
  local nearest=player(13,b);local distant=player(14,b)
  contexts[13].position=b.center+Vector3.new(0,3,close and 7 or 26)
  contexts[14].position=b.center+Vector3.new(25,3,0)
  service:Hit(b,nearest,1,now+2);service:Hit(b,distant,1,now+2);service:Step(now+2)
  check(b.strike and b.strike.kind==(close and "Melee" or "Ranged"),"melee selects a reachable contributor or falls back to ranged")
  local before=#damage
  service:Step(now+2+b.spec.windup+.2)
  if close then check(#damage==before+1 and damage[#damage].p==nearest and damage[#damage].push==4 and damage[#damage].amount==b.spec.meleeDamage,"only eligible melee victim gets the tuned strike and one shove") end
 end
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
  local style=i==1 and "Ranged" or "Melee"
  check(b.strike.kind==style and (b.strike.push~=nil)==(i==2),"one melee and one ranged mode per boss")
  check(b.model:GetAttribute("BossAttackKind")==style and b.model:GetAttribute("BossAttackStyle")==b.strike.style,"server animation cue semantics")
  check(b.model:GetAttribute("BossAttackStartAt")==b.model:GetAttribute("BossStateAt"),"shared server start clock")
  local before=#damage
  local impactShape=b.strike.shapes[1]
  local retreat=contexts[20].position
  contexts[20].position=b.center+Vector3.new(impactShape.x,3,impactShape.z)
  service:Step(now+b.spec.windup+.11)
  contexts[20].position=retreat
  check(#damage==before+1 and damage[#damage].p==p,"exactly one accepted impact in this actual service cast")
  check(damage[#damage].amount==(i==1 and b.spec.damage or b.spec.meleeDamage),"expected ranged/melee damage reached Bootstrap callback")
 end
end
-- New instance isolates times/cooldowns for deterministic telegraph tests.
local b=byId.metronome;Rules.Reset(b,b.spec,400);service.nextStep=0;b.turn=0
local p=player(3,b);local bystander=player(4,b)
local before=#damage
service:Step(401);check(not b.strike,"no proximity aggression")
service:Hit(b,p,10,402);service:Step(402)
check(b.strike and b.strike.at==403.5,"full fixed 1.5 second tell")
local fixed=b.strike.shapes[1]
contexts[3].position=b.center+Vector3.new(fixed.x+10*math.cos(fixed.angle),3,fixed.z-10*math.sin(fixed.angle))
service:Step(403.6);check(#damage==before,"move off fixed point avoids strike")
service:Step(407);check(b.strike~=nil,"second strike")
contexts[3].position=b.center+Vector3.new(b.strike.shapes[1].x,3,b.strike.shapes[1].z)
service:Step(409);check(#damage==before+1 and damage[#damage].p==p,"only participant hit")
service:Step(412);check(b.strike~=nil,"next strike")
contexts[3].position=b.center+Vector3.new(b.spec.radius+1,3,0)
service:Step(414);check(#damage==before+1,"escape ring avoids damage")
check(b.credit[3]==nil,"escape removes credit")
service:Step(425);check(b.health==b.spec.health and b.strike==nil,"idle reset cleans warning and credit")
check(b.model:GetAttribute("BossHealth")==b.spec.health,"idle refill replicated to bar")
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
 check(spec.scale==2.8 and spec.aimHeight==14 and spec.engageHeight==12,"shared scale/range definition")
 local ranged=Patterns.Build(spec.id,1,0,30,spec.radius,spec.moveLeash)
 local reach=spec.id=="conductor" and 20 or 30
 check(Patterns.Hits(ranged,0,reach),"distinct ranged attack reaches farther than previous pattern")
 local melee=Patterns.Build(spec.id,2,0,8,spec.radius,spec.moveLeash)
 check(melee.push>0 and melee.push<=6.5 and not Patterns.Hits(melee,0,reach),"melee remains close and separately bounded")
 for turn=1,4 do
  local pattern=Patterns.Build(spec.id,turn,18,0,spec.radius,spec.moveLeash)
  for _,shape in ipairs(pattern.shapes) do
   if shape.kind=="disk" then
    check(math.sqrt(shape.x^2+shape.z^2)+shape.radius<=spec.radius,"disk containment")
   else
    for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
     local x=sx*shape.width/2;local z=sz*shape.length/2
     local wx=shape.x+math.cos(shape.angle)*x+math.sin(shape.angle)*z
     local wz=shape.z-math.sin(shape.angle)*x+math.cos(shape.angle)*z
     check(math.sqrt(wx^2+wz^2)<=spec.radius,"bar containment")
    end end
   end
   check(Patterns.Contains(shape,shape.x,shape.z),"shape center hit")
   check(not Patterns.Contains(shape,100,100),"outside shape miss")
  end
 end
 local boss=byId[spec.id];Rules.Reset(boss,spec,2000)
 local attacker=player(90,boss)
 for _,off in ipairs({Vector3.new(spec.radius+.001,3,0),Vector3.new(0,12.001,0),Vector3.new(0,-12.001,0),Vector3.new(0/0,3,0),Vector3.new(math.huge,3,0)}) do
  contexts[90].position=boss.center+off
  check(not service:CanHit(boss,attacker,2002),"authoritative admission outside/invalid")
  check(service:Hit(boss,attacker,100,2002)==0 and boss.health==spec.health,"direct damage cannot bypass admission")
 end
 contexts[90].position=boss.center+Vector3.new(spec.radius,12,0)
 check(service:CanHit(boss,attacker,2002),"inclusive exact limits")
 service:Hit(boss,attacker,1,2002);service.nextStep=0;service:Step(2002)
 local warning=boss.warning
 contexts[90].position=boss.center+Vector3.new(spec.radius+1,3,0)
 service:Step(2002.2)
 check(not boss.strike and not boss.warning and warning.destroyed,"empty encounter cancels before impact")
 -- A fresh cast locks its participant set; late opt-ins get the next full tell.
 Rules.Reset(boss,spec,2100);service.nextStep=0
 contexts[90].position=boss.center+Vector3.new(0,3,8)
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
 local melee=damage[#damage].kind=="Melee"
 check((damage[#damage].push~=nil)==melee,"only resolved melee may push")
 check(damage[#damage].amount==(melee and spec.meleeDamage or spec.damage),"one cast deals correct kind's authored damage")
 check(damage[#damage].serial==boss.model:GetAttribute("BossAttackImpactSerial"),"confirmed serial corresponds to actual hit")
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
  local pattern=Patterns.Build(spec.id,turn,22,0,spec.radius,spec.moveLeash)
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
 contexts[100].position=center+Vector3.new(spec.radius+.01,3,0)
 check(service:Hit(boss,attacker,10,3006)==0,"moving toward player never extends admission")
 contexts[100].position=center+Vector3.new(0,3,0)
 service:Hit(boss,attacker,spec.health,3007)
 check(boss.model:GetAttribute("BossState")=="Defeated","KO state immediate")
 x,z=boss.motion.x,boss.motion.z;service:Step(3008)
 check(boss.motion.x==x and boss.motion.z==z,"no dead patrol")
 service:Step(3007+Catalog.Respawn)
 check(boss.motion.x==0 and boss.motion.z==0 and boss.model:GetAttribute("BossState")=="Idle","respawn clean home pose")
end
-- Ignis patrol offset from the native repro; the first/alternate ranged
-- casts still hit a stationary contributor and offer reachable escape gaps.
do
 local spec=byId.ignis.spec
 for _,turn in ipairs({1,3,5}) do
  for _,offset in ipairs({2.6,-2.6}) do
   local x,z=-offset,23
   local pattern=Patterns.Build("ignis",turn,x,z,spec.radius,spec.moveLeash)
   local center=pattern.shapes[2]
   check(#pattern.shapes==3 and center.x==0 and center.z==0,"Ignis lanes originate at the frozen patrol position")
   check(Patterns.Contains(center,x,z),"Ignis center lane aims at a stationary participant off the world axis")
   local stepX,stepZ=math.cos(center.angle)*4,-math.sin(center.angle)*4
   check(not Patterns.Hits(pattern,x+stepX,z+stepZ) and not Patterns.Hits(pattern,x-stepX,z-stepZ),"Ignis parallel lanes leave safe gaps on both sides")
  end
 end
end
-- Captain reskin retains slot and progression while changing the mechanical theme.
local captain=byId.leviathan.spec
check(captain.name=="Seagull Siren Captain" and captain.level==70,"captain public name and exact level")
check(captain.coins==95 and captain.xp==340,"captain unchanged reward pool")
check(captain.x==420 and captain.y==0 and captain.z==420 and captain.radius==38,"captain existing pier arena")
for _,angle in ipairs({0,math.pi/4,math.pi/2,math.pi}) do
 local dx,dz=math.sin(angle),math.cos(angle)
 local cutlass=Patterns.Build("leviathan",2,dx*10,dz*10,captain.radius,captain.moveLeash)
 local sirens=Patterns.Build("leviathan",1,dx*10,dz*10,captain.radius,captain.moveLeash)
 check(#cutlass.shapes==1 and #sirens.shapes==2,"captain distinct bounded pattern counts")
 check(Patterns.Hits(cutlass,dx*8,dz*8),"cutlass forward broadside danger")
 check(not Patterns.Hits(cutlass,0,0),"cutlass retreat safe")
 check(not Patterns.Hits(cutlass,-dx*8,-dz*8),"cutlass behind safe")
 check(Patterns.Hits(sirens,dx*10,dz*10),"stationary target is in a committed shoulder lane")
 local sx,sz=sirens.aimX,sirens.aimZ
 check(not Patterns.Hits(sirens,sx*10,sz*10),"dual siren middle gap safe")
 check(Patterns.Hits(sirens,sz*6,-sx*6),"dual siren shoulder lane danger")
 check(Patterns.Hits(sirens,sx*30+sz*6,sz*30-sx*6),"dual siren longer reach")
 check(not Patterns.Hits(sirens,sx*34+sz*6,sz*34-sx*6),"dual siren outer escape safe")
end
nameplates()
for i,boss in ipairs(service.bosses) do
 local now=50000+i*(Catalog.Respawn+5)
 local finisher=player(601,boss)
 check(service:Hit(boss,finisher,13,now)==13 and boss.model:GetAttribute("BossHealth")==boss.spec.health-13,"hit replicated")
 check(service:Hit(boss,finisher,boss.spec.health+77,now+.1)==boss.spec.health-13,"lethal hit clamps overkill")
 check(boss.model:GetAttribute("BossHealth")==0 and boss.model:GetAttribute("BossMaxHealth")==boss.spec.health,"defeat replicated")
 service:Step(now+1+Catalog.Respawn)
 check(boss.model:GetAttribute("BossHealth")==boss.spec.health,"respawn refill replicated")
end
check(labelWrites==beforeIdle,"strike/defeat rewrote the identity label")
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
local V=Vector3.new
Vector3.zero=V(0,0,0)
RaycastParams={new=function()return {}end};Enum.Material.Air=2;Enum.RaycastFilterType={Exclude=1}
local script={Parent={BossService="BossService",BossKnockback="BossKnockback"}};local workspace={ScreamSimulatorWorld={}}
local shoves,query,cover=0,nil,false
local require=function(name)
 if name=="BossKnockback" then return {Target=function(_,_,_,_,params,_,inWorld)
  assert(params.RespectCanCollide and #params.FilterDescendantsInstances==1)
  assert(inWorld(V(3,3,3)) and not inWorld(V(50,3,0)),"world guard")
  shoves+=1;return query
 end} end
 assert(name=="BossService");return {new=function(_,cb)callbacks=cb;return {}end}
end
local function audible(c,origin,target,model)assert(c and origin and target and model);return not cover end
local Config={CompactCity=true,HealQuietSeconds=12,MapMin=V(-30,-10,-30),MapMax=V(30,30,30),InArena=function(p)return p.arena end}
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
local p={root={Position=V(0,3,0),CFrame=CFrame.new(V(0,3,0))},h={Health=100}}
local boss={root={Position=V(0,14,0)},model={}}
local ranged,melee={}, {push=4}
sessions[p]={data={level=95},rewardIdentity={},micReady=false,protectedUntil=0,dodgingUntil=0}
check(callbacks.context(p,1)~=nil,"mic toggling must not undo participation")
sessions[p].testBaseline={};check(callbacks.context(p,1)==nil,"live test-mode isolation")
fixture=true;check(callbacks.context(p,1)~=nil,"guarded local fixture usable")
fixture=false;sessions[p].testBaseline=nil;sessions[p].protectedUntil=10
check(callbacks.context(p,1)==nil,"protected state admission")
callbacks.damage(p,20,1,boss,melee);check(p.h.Health==100,"protected players unharmed")
sessions[p].protectedUntil=0;sessions[p].dodgingUntil=10
callbacks.damage(p,20,1,boss,melee);check(p.h.Health==100,"dodge avoids hazard")
sessions[p].dodgingUntil=0;cover=true
callbacks.damage(p,20,1,boss,melee);check(p.h.Health==100 and shoves==0,"cover blocks melee damage and shove")
cover=false;callbacks.damage(p,20,1,boss,ranged)
check(p.h.Health==80 and sessions[p].nextHeal==13,"normal damage and healing delay")
check(shoves==0,"ranged hit never shoves")
p.h.FloorMaterial=Enum.Material.Air
callbacks.damage(p,20,1,boss,melee);check(p.h.Health==60 and shoves==0,"airborne player not shoved")
p.h.FloorMaterial=nil;query=V(4,3,0)
callbacks.damage(p,20,1,boss,melee)
check(p.h.Health==40 and shoves==1 and p.root.CFrame.Position==query and p.root.AssemblyLinearVelocity==Vector3.zero,"valid grounded melee shifts once")
callbacks.damage(p,90,1,boss,melee);check(ejected==1 and shoves==1,"lethal damage only uses existing safe ejection")
callbacks.reward(p,{name="Boss",coins=35,xp=100},.31)
check(rewards.coins==10 and rewards.xp==31,"fractional share rounded down")
p.root.Position.arena=true;check(callbacks.context(p,1)==nil,"arena isolation")
print("Boss bootstrap callbacks: "..checks.." assertions passed (mocked)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:f.write(setup+pre+block+post);name=f.name
try:subprocess.run(['luau',name],check=True,cwd=root)
finally:Path(name).unlink()
assert 'add("boss:"..boss.spec.id,{boss=boss})' in server
assert 'dealt+=bosses:Hit(target.boss,p,hit.damage,now)' in server
assert 'bosses:Hit(boss,p,sound.damage,now)' in server
assert 'if bosses then bosses:Step(now) end' in server
print('Boss sustained/legacy/heartbeat wiring source contracts passed')

dodge=(root/'src/ServerScriptService/DodgeMotion.luau').read_text()
shove=(root/'src/ServerScriptService/BossKnockback.luau').read_text()
motion_setup=r'''
local script={Parent={DodgeMotion="DodgeMotion"}}
local function require(name)assert(name=="DodgeMotion");return DodgeMotion end
'''
motion_tests=r'''
local checks=0
local function check(v,msg) assert(v,msg);checks+=1 end
local V=Vector3.new
local boss={center=V(0,0,0),spec={radius=38,engageHeight=12}}
local bossAttack={x=0,z=0,aimX=1,aimZ=0,push=6.5}
local opts={wall=math.huge,edge=math.huge,slope=0,base=0,groundNormal=1}
local sweep,scan=0,0
local world={}
local params={}
function world:Blockcast(frame,size,delta,passed)
 check(passed==params and size.X==2 and delta.Magnitude<=.83,"reuse bounded avatar sweep with the caller's collision exclusions")
 sweep+=1
 if frame.Position.X+delta.X+size.X/2>=opts.wall then return {Distance=0} end
end
function world:Raycast(origin,delta,passed)
 check(passed==params and delta.Y==-8,"reuse floor check with caller's collision exclusions")
 scan+=1
 if origin.X<opts.edge then return {Position=V(origin.X,opts.base+origin.X*opts.slope,origin.Z),Normal=V(0,opts.groundNormal,0)} end
end
local veto=math.huge
local function target(x,y)
 return Knockback.Target(world,CFrame.new(V(x,y,0)),boss,bossAttack,params,{MaxSlopeAngle=40},function(next)return next.X<veto end)
end
check(target(8,3).X==14.5 and sweep==13,"exact legal 6.5-stud displacement")
check(target(0,3).X==6.5,"center shove uses committed facing")
opts.wall=11;check(target(8,3).X==9.5,"sweep stops before wall with full avatar width")
opts.wall=math.huge;opts.edge=10;check(target(8,3).X==9.5,"never crosses missing support")
opts.edge=math.huge;opts.groundNormal=.2;check(target(8,3)==nil,"steep surface rejected")
opts.groundNormal=1;opts.slope=2;check(target(8,3)==nil,"vertical discontinuity rejected")
opts.slope=.5;check(target(8,11).X==10 and target(8,11).Y==12,"valid grades stop at vertical arena boundary")
opts.slope=0;check(target(35,3).X==36.5 and target(36.5,3)==nil,"arena edge retains avatar margin")
veto=9;check(target(8,3).X==8.5,"world and separate gameplay zones stop shove")
veto=8;check(target(8,3)==nil,"no forced change when no safe substep exists")
print("Boss knockback + real DodgeMotion: "..checks.." assertions passed (mocked ground/collision)")
'''
code=setup+'\nlocal DodgeMotion=(function()\n'+dodge+'\nend)()\n'+motion_setup+'\nlocal Knockback=(function()\n'+shove+'\nend)()\n'+motion_tests
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False) as f:f.write(code);name=f.name
try:subprocess.run(['luau',name],check=True,cwd=root)
finally:Path(name).unlink()
