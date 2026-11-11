"""Extracted root integration with actual compact modules; synthetic instances/state, no native physics."""
from pathlib import Path
import ast,argparse,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
def read(path):return (ROOT/path).read_text(encoding='utf-8')
server=read('src/ServerScriptService/Bootstrap.server.luau');world=read('src/ServerScriptService/World.luau')
layout=read('src/ReplicatedStorage/Shared/CompactLayout.luau');city=read('src/ServerScriptService/CompactCity.luau');config=read('src/ReplicatedStorage/Shared/Config.luau')
tree=ast.parse(read('tests/compact_world.py'));setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup[:setup.index('local Layout=')]
pre=r'''
Vector3.zero=Vector3.new(0,0,0)
local Healing=require('../src/ReplicatedStorage/Shared/Healing');local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat');local Progression=require('../src/ReplicatedStorage/Shared/Progression');local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local Layout=(function()
'''
bridge=r'''
end)()
local script={Parent={WaitForChild=function(_,name)return name end}}
local require=function(name)if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression elseif name=='CompactLayout' then return Layout else error('Unexpected require '..tostring(name))end end
local Config=(function()
'''
citybridge=r'''
end)()
local game={GetService=function()return {Shared={CompactLayout='CompactLayout'}}end}
local City=(function()
'''
worldsetup=r'''
end)()
check(Config.CompactCity and Config.ObjectDestruction==false and Config.CityLayout==Layout,'Compact config flags wrong')
check(Config.MapMin==Layout.BoundsMin and Config.MapMax==Layout.BoundsMax and Config.ZoneMin==Layout.ZoneMin and Config.ZoneMax==Layout.ZoneMax,'Config bounds not mapped')
check(Config.DeliveryStops==Layout.DeliveryStops,'Config delivery stops not mapped')
check(Config.InArena(Vector3.new(-120,0,-180)) and Config.InArena(Vector3.new(200,0,140)),'Arena exact boundary missing')
for _,pos in ipairs({Vector3.new(-120.01,0,0),Vector3.new(200.01,0,0),Vector3.new(0,0,-180.01),Vector3.new(0,0,140.01),Vector3.new(-270,3,130),Vector3.new(-245,3,-100)})do check(not Config.InArena(pos),'Safe region classified PvP')end
local parent={};local layout=City.Build(parent)
local World={Bots={},Cars={},SafeSpawn=layout.spawn};local C={green={},gold={}}
local function makeBot(_,index,x,z,role,job,training)table.insert(World.Bots,{index=index,x=x,z=z,role=role,job=job,training=training})end
local function part()return {}end
local function billboard()return {Parent={}}end
local function vehicle()error('Legacy traffic created in compact world')end
local function taxi()error('Legacy traffic created in compact world')end
local original={};for i,tier in ipairs(TrainingRules.Tiers)do original[i]=table.clone(tier)end
'''
a=world.index('    local roles=',world.index('function World.Build()'));b=world.index('    if RunService:IsRunning()',a);spawn=world[a:b]
worldchecks=r'''
check(#World.Bots==#layout.seeds+#layout.jobs+3,'Wrong compact resident/trainer count')
for i,seed in ipairs(layout.seeds)do local bot=World.Bots[i];check(bot.x==seed[1] and bot.z==seed[2] and bot.role==seed.role,'Compact seed ignored')end
for i,job in ipairs(layout.jobs)do local bot=World.Bots[#layout.seeds+i];check(bot.job==job and bot.x==job.stations[1].position.X and bot.z==job.stations[1].position.Z,'Compact job ignored')end
for i,tier in ipairs(TrainingRules.Tiers)do
 local bot=World.Bots[#layout.seeds+#layout.jobs+i];local home=Layout.TrainingHomes[i]
 check(bot.training~=tier and bot.x==home.x and bot.z==home.z,'Trainer relocation did not clone tier')
 for k,v in pairs(original[i])do check(tier[k]==v,'Pure training tier mutated')end
 check(bot.training.health==tier.health and bot.training.xp==tier.xp and bot.training.level==tier.level,'Training reward stats changed')
end
World.Bots={}
local protected,messages=0,0
local function protect(p,s)protected+=1;s.protectedUntil=55 end
local function state()messages+=1 end
'''
a=server.index('local function resetMovement(');reset=server[a:server.index('local function eject(',a)]
a=server.index('    if Config.CompactCity and (r.Position.');rescue=server[a:server.index('    elseif not Config.CompactCity',a)]+' end\n'
rescuechecks=r'''
local function rescueAt(position)
 local r={Position=position,Anchored=false,AssemblyLinearVelocity='moving',AssemblyAngularVelocity='turning'};function r:SetNetworkOwnershipAuto()self.auto=true end
 local c={};function c:PivotTo(where)self.where=where end
 local p={Character=c,attributes={}};function p:SetAttribute(k,v)self.attributes[k]=v end
 local own={Name='SeatWeld',Part1={IsDescendantOf=function(_,model)return model==c end}}
 local other={Name='SeatWeld',Part1={IsDescendantOf=function()return false end}}
 local furniture={Name='Joint',Part1=own.Part1}
 for _,w in ipairs({own,other,furniture})do function w:IsA(kind)return kind=='Weld'end;function w:Destroy()self.destroyed=true end end
 local h={Sit=true,PlatformStand=true,AutoRotate=false,SeatPart={GetChildren=function()return {own,other,furniture}end}}
 local s={dodgingUntil=99,knockedUntil=99,premiumRoll=true,sprintRequested=true,sprintCharge=3,nextDodge=88};local running=true
 __RESCUE__
 return {r=r,c=c,p=p,h=h,s=s,running=running,own=own,other=other,furniture=furniture}
end
for _,position in ipairs({Vector3.new(-370.01,0,0),Vector3.new(370.01,0,0),Vector3.new(0,0,-310.01),Vector3.new(0,0,310.01),Vector3.new(0,-15.01,0)})do
 local v=rescueAt(position)
 check(v.c.where==World.SafeSpawn and not v.running,'Compact rescue missing or running retained')
 check(v.own.destroyed and not v.other.destroyed and not v.furniture.destroyed and not v.h.Sit,'Compact rescue retained own seat or destroyed foreign joint')
 check(v.s.dodgingUntil==0 and v.s.knockedUntil==0 and not v.s.premiumRoll and not v.s.sprintRequested,'Compact rescue retained movement state')
 check(v.r.AssemblyLinearVelocity==Vector3.zero and v.r.AssemblyAngularVelocity==Vector3.zero and v.r.auto,'Compact rescue retained velocity/ownership')
 check(v.h.AutoRotate and not v.h.PlatformStand and v.s.protectedUntil==55,'Compact rescue lacks protection/recovery')
 check(v.s.sprintCharge==3 and v.s.nextDodge==88,'Compact rescue reset cooldown budgets')
end
for _,position in ipairs({Vector3.new(-370,0,0),Vector3.new(370,0,0),Vector3.new(0,0,-310),Vector3.new(0,0,310),Vector3.new(0,-15,0)})do check(rescueAt(position).c.where==nil,'Compact rescue inclusive boundary changed')end
local starts,damages=0,0
local object={GetAttribute=function(_,key)return key=='ObjectId' and 'fixture' or nil end}
local Destruction={objects={[object]=true},Start=function()starts+=1 end,Damage=function()damages+=1;return {}end}
local workspace={ScreamSimulatorWorld={}}
__START__
check(starts==0,'Disabled destruction started')
local obstruction={Instance=object,Distance=5};local s={data={level=1}};local sound={damage=10}
local function legacyDamage()
 __DAMAGE__
 return result
end
check(legacyDamage()==nil and damages==0,'Disabled legacy destruction damaged')
local Players={GetPlayers=function()return {}end}
local function beamObstruction()return obstruction end
__RESOLVE__
local ids,details=resolveSustained({character={},origin=Vector3.zero,position=Vector3.zero},Vector3.new(1,0,0),{range=30,width=4,power=1},0)
check(#ids==0 and next(details)==nil,'Disabled sustained destruction emitted target')
'''
start=next(line for line in server.splitlines() if 'then Destruction.Start(' in line)
damage=next(line.strip() for line in server.splitlines() if 'local result=Config.ObjectDestruction' in line)
a=server.index('local function resolveSustained(');resolve=server[a:server.index('local function restoreBot(',a)]
rescuechecks=rescuechecks.replace('__RESCUE__',rescue).replace('__START__',start).replace('__DAMAGE__',damage).replace('__RESOLVE__',resolve)
soccer=read('src/ServerScriptService/SoccerChallenge.luau');volley=read('src/ServerScriptService/BeachVolley.luau')
soccerdecl=soccer[soccer.index('local compact='):soccer.index('local function sphere(')]
volleydecl=volley[volley.index('local compact='):volley.index('local gameState')]
socceroutside=re.search(r'if (nextPosition.X<minimum.X[^\n]+) then',soccer)[1]
volleyoutside=re.search(r'if (position.X<minimum.X[^\n]+) then fault',volley)[1]
sports='\ndo\n'+soccerdecl+"\ncheck(origin==Layout.Soccer.origin and center==Layout.Soccer.center and minimum==Layout.Soccer.min and maximum==Layout.Soccer.max,'Soccer mapping wrong')\ncheck(origin.Y==1.2,'Soccer floor height wrong')\nlocal function outside(nextPosition)return "+socceroutside+" end\n"
sports+="for _,v in ipairs({Vector3.new(minimum.X-.01,1,center.Z),Vector3.new(maximum.X+.01,1,center.Z),Vector3.new(center.X,1,minimum.Z-.01),Vector3.new(center.X,1,maximum.Z+.01)})do check(outside(v),'Soccer outside accepted')end\ncheck(not outside(minimum) and not outside(maximum),'Soccer boundary rejected')\nend\ndo\n"+volleydecl
sports+="\ncheck(serve==Layout.Volley.serve and minimum==Layout.Volley.min and maximum==Layout.Volley.max and netZ==Layout.Volley.netZ,'Volley mapping wrong')\ncheck(floorBallY==1.1 and minimumCrossingHeight==9.2,'Volley floor/net height wrong')\nlocal function outside(position)return "+volleyoutside+" end\nfor _,v in ipairs({Vector3.new(minimum.X-.01,1,netZ),Vector3.new(maximum.X+.01,1,netZ),Vector3.new(serve.X,1,minimum.Z-.01),Vector3.new(serve.X,1,maximum.Z+.01)})do check(outside(v),'Volley outside accepted')end\ncheck(not outside(minimum) and not outside(maximum),'Volley boundary rejected')\nend\nprint('PASS '..checks..' actual compact integration assertions; mocks/snippets, not native physics')\n"
# Exercise the actual net-height predicate and landing branch, not just declared values.
net_predicate=re.search(r'elseif (old.Y[^\n]+) then',volley)[1]
a=volley.index('  if state.phase=="Playing" then');landing=volley[a:volley.index('  state.position=position',a)]
height_tests="\ndo\n"+volleydecl+"\nlocal function netHit(y)local old={Y=y};local position={Y=y};local alpha=.5;return "+net_predicate+" end\ncheck(netHit(9.199) and not netHit(9.2),'Actual volley crossing height wrong')\nlocal function land(y)\n local position=V(serve.X,y,serve.Z);local state={phase='Playing'};local reason\n local function fault(_,why)reason=why end\n"+landing+"\n return position,reason\nend\nlocal landed,why=land(1.1);check(landed.Y==1.1 and why=='Ball landed','Actual volley landing threshold wrong')\nlocal airborne,reason=land(1.101);check(airborne.Y==1.101 and reason==nil,'Volley landed above threshold')\nend\n"
code=setup+pre+layout+bridge+config+citybridge+city+worldsetup+spawn+worldchecks+reset+rescuechecks+height_tests+sports
def run(body,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(body);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(code)
if args.negative_controls:
 for old,new,error in [('tier=table.clone(originalTier)','tier=originalTier','Trainer relocation did not clone tier'),('if layout.traffic~=false then','if true then','Legacy traffic created'),('resetMovement(p,s,h,r);running=false','running=false','Compact rescue retained own seat'),('if Config.ObjectDestruction==true then Destruction.Start','if true then Destruction.Start','Disabled destruction started'),('if Config.ObjectDestruction==true and obstruction then','if obstruction then','Disabled sustained destruction emitted target'),('Config.ObjectDestruction==true and Destruction.Damage','true and Destruction.Damage','Disabled legacy destruction damaged'),('nextPosition.X<minimum.X','nextPosition.X< -9999','Soccer outside accepted'),('position.X<minimum.X','position.X< -9999','Volley outside accepted'),('alpha<minimumCrossingHeight','alpha<10.2','Actual volley crossing height wrong'),('position.Y<=floorBallY','position.Y<=2.1','Volley landed above threshold')]:
  changed=code.replace(old,new);assert changed!=code,old;run(changed,error)
client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
assert 'Next destruction tier:' not in client and 'All destruction tiers unlocked' not in client,'UI advertises disabled destruction tiers'
print('PASS no disabled destruction tier advertisement source contract')
