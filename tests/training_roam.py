"""Actual training movement/lifecycle functions with fake humanoid and clock; no native pathfinding claim."""
from pathlib import Path
import argparse,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
def read(path):return subprocess.check_output(['git','show','44ee830:'+path],cwd=root,text=True,encoding='utf-8') if args.baseline else (root/path).read_text(encoding='utf-8')
world=read('src/ServerScriptService/World.luau');server=read('src/ServerScriptService/Bootstrap.server.luau')
stop=world[world.index('local function stopWalking('):world.index('function World.Talk(')]
update=world[world.index('function World.UpdateBot('):world.index('return World',world.index('function World.UpdateBot('))]
roam=''
if 'function World.StepTrainingRoam(' in world:
 a=world.index('function World.StepTrainingRoam(');b=world.find('\nfunction ',a+1);roam=world[a:b if b!=-1 else world.index('return World',a)]
life=server[server.index('local function restoreBot('):server.index('local function destructionHint(')]
auto_reset=server[server.index('local function stepTraining('):server.index('local function stepSprint(')]
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z)elseif k=='Unit' then return t/t.Magnitude else return V[k]end end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end};Vector3.zero=Vector3.new(0,0,0)
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)if type(a)=='number' then a,b=b,a end;return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return Vector3.new(a.X/b,a.Y/b,a.Z/b)end
local CFrame={new=function(p)return {Position=p}end}
local Config={BotMaxHealth=80,BotRespawnSeconds=10}
local World={};local randomCalls=0
local rng={NextNumber=function(_,a,b)randomCalls+=1;return a+(b-a)*.5 end,NextInteger=function(_,a,b)return a end}
local function releaseSeat(bot)bot.released=(bot.released or 0)+1 end
local sessions={};local Instance={new=function()error('Unexpected warning disc in quiet-reset fixture')end}
local pending={};local task={delay=function(seconds,fn)table.insert(pending,{seconds=seconds,fn=fn})end}
local function make(training)
 local bot={name="Trainer",training=training and {level=1},alive=true,health=80,maxHealth=80,start=Vector3.new(0,4,0),credit={owner=12},label={},speech={Visible=true},socialUntil=0,reactionUntil=0,gestureUntil=0,id=1}
 bot.root={Parent={},Position=bot.start,Anchored=false,AssemblyLinearVelocity=Vector3.zero,owners={}}
 function bot.root:SetNetworkOwner(owner)table.insert(self.owners,{owner})end
 bot.model={Parent={},attributes={},pivots={}}
 function bot.model:SetAttribute(k,v)self.attributes[k]=v end
 function bot.model:PivotTo(cf)table.insert(self.pivots,cf);bot.root.Position=cf.Position end
 bot.humanoid={Parent={},Health=80,moves={}}
 function bot.humanoid:MoveTo(pos)table.insert(self.moves,pos)end
 return bot
end
local function same(a,b)return (a-b).Magnitude<.000001 end
'''
a=world.index('    if training then\n',world.index('model:SetAttribute("AnimationSeed",index)'))
spawn=world[a:world.index('    if RunService:IsRunning()',a)]
spawn_code='local function spawnTrainer()local bot=make(true);local root,humanoid,model=bot.root,bot.humanoid,bot.model;local training=bot.training;local index=17;local nameLabel={Parent={}};'+spawn+'return bot end\n'
tests=r'''
check(type(World.StepTrainingRoam)=='function','Training roam missing')
local spawned=spawnTrainer();check(not spawned.root.Anchored,'New trainer remains anchored');check(spawned.humanoid.WalkSpeed==7,'New trainer remains zero speed')
local b=make(true)
World.StepTrainingRoam(b,0)
check(#b.humanoid.moves>=1,'Trainer did not start moving')
check(b.humanoid.WalkSpeed==7,'Trainer speed changed')
local target=b.humanoid.moves[#b.humanoid.moves]
check(Vector3.new(target.X-b.start.X,0,target.Z-b.start.Z).Magnitude<=18.00001,'Roam target outside bounded radius')
check(target.Y==b.start.Y,'Roam target vertical drift')
local count=#b.humanoid.moves;local tick=b.trainingStepAt;World.StepTrainingRoam(b,.01);check(#b.humanoid.moves==count and b.trainingStepAt==tick,'Roam tick throttle missing')
World.StepTrainingRoam(b,6);check(#b.humanoid.moves>count,'Stuck trainer never retargeted')
check(b.health==80 and b.credit.owner==12 and #b.model.pivots==0,'Roam changed rewards or teleported healthy trainer')
local credit=b.credit;b.health=40;b.root.Position=b.start+Vector3.new(23,0,0)
World.StepTrainingRoam(b,7)
check(same(b.root.Position,b.start),'Escaped trainer did not recover home')
check(b.health==40 and b.credit==credit and b.credit.owner==12,'Recovery healed or cleared credit')
for _,field in ipairs({'strike','socialUntil','reactionUntil','Anchored','SeatPart','Sit','PlatformStand'})do
 b=make(true);World.StepTrainingRoam(b,0)
 if field=='strike' then b.strike={at=2} elseif field=='Anchored' then b.root.Anchored=true elseif field=='SeatPart' then b.humanoid.SeatPart={} elseif field=='Sit' then b.humanoid.Sit=true elseif field=='PlatformStand' then b.humanoid.PlatformStand=true else b[field]=2 end
 World.StepTrainingRoam(b,.01);local n=#b.humanoid.moves
 World.StepTrainingRoam(b,.6);check(#b.humanoid.moves==n,'Paused trainer keeps issuing moves')
 check(same(b.humanoid.moves[n],b.root.Position),'Pause did not stop movement')
 b.strike=nil;b.socialUntil=0;b.reactionUntil=0;b.root.Anchored=false;b.humanoid.SeatPart=nil;b.humanoid.Sit=false;b.humanoid.PlatformStand=false;World.StepTrainingRoam(b,3);check(#b.humanoid.moves>n,'Trainer did not resume')
end
for _,mode in ipairs({'resident','dead','model','root','humanoid'})do
 b=make(mode~='resident');if mode=='dead' then b.alive=false elseif mode=='model' then b.model.Parent=nil elseif mode=='root' then b.root.Parent=nil elseif mode=='humanoid' then b.humanoid.Parent=nil end
 World.StepTrainingRoam(b,100);check(#b.humanoid.moves==0 and #b.model.pivots==0,'Ineligible bot moved')
end
b=make(true);World.StepTrainingRoam(b,0);b.health=40;b.root.Position=b.start+Vector3.new(5,0,0);local loc=b.root.Position;local n=#b.humanoid.moves
World.UpdateBot(b);check(same(b.root.Position,loc) and #b.model.pivots==0 and #b.humanoid.moves==n,'Damage update interrupted roam or teleported')
knockOutBot(b);World.UpdateBot(b)
check(not b.alive and b.root.Anchored and b.label.Text=='RECOVERING','KO state incorrect')
check(b.trainingDestination==nil and b.trainingStepAt==nil and b.trainingMoveUntil==nil and b.trainingNextMove==nil,'KO retained roam state')
check(b.root.Position.Y==b.start.Y-100,'KO did not hide trainer')
local old=pending[#pending];restoreBot(b)
check(b.alive and b.health==80 and not b.root.Anchored and same(b.root.Position,b.start),'Restore did not return mobile trainer home')
check(next(b.credit)==nil and #b.root.owners==1,'Restore ownership or credit wrong')
local version=b.recoveryVersion;old.fn();check(b.recoveryVersion==version,'Stale respawn callback restored twice')
World.StepTrainingRoam(b,.01);check(not same(b.humanoid.moves[#b.humanoid.moves],b.start),'Restore retained stale roam throttle')
knockOutBot(b);local first=pending[#pending];restoreBot(b);knockOutBot(b);local second=pending[#pending]
first.fn();check(not b.alive,'Old life callback revived newer KO');second.fn();check(b.alive,'Current delayed respawn failed')
knockOutBot(b);b.model.Parent=nil;pending[#pending].fn();check(not b.alive,'Removed bot respawned')
b=make(false);b.health=80;World.UpdateBot(b);check(not b.root.Anchored and same(b.root.Position,b.start),'Normal resident restoration changed')

check(TrainingRules.RoamRadius==18 and TrainingRules.RoamSpeed==7 and TrainingRules.RoamLeash==22 and TrainingRules.Radius==32,'Training bounds changed')
b=make(true)
for step=1,300 do
 local now=step*10;World.StepTrainingRoam(b,now)
 local dest=b.trainingDestination;check(dest~=nil,'Waypoint missing after pause')
 check(Vector3.new(dest.X-b.start.X,0,dest.Z-b.start.Z).Magnitude<=18.000001,'Waypoint sweep escaped radius')
 b.root.Position=dest;World.StepTrainingRoam(b,now+.25)
 check(b.trainingDestination==nil,'Arrival did not stop waypoint')
 local n=#b.humanoid.moves;World.StepTrainingRoam(b,now+1);check(#b.humanoid.moves==n,'Arrival pause missing')
end
b=make(true);World.StepTrainingRoam(b,0);World.StepTrainingRoam(b,4.99);check(b.trainingDestination~=nil,'Movement deadline too short')
World.StepTrainingRoam(b,5.25);check(b.trainingDestination==nil,'Blocked trainer never stops at deadline')
local n=#b.humanoid.moves;World.StepTrainingRoam(b,6);check(#b.humanoid.moves==n,'Blocked trainer skipped rest');World.StepTrainingRoam(b,6.5);check(b.trainingDestination~=nil,'Blocked trainer never resumes')
b=make(true);b.root.Position=b.start+Vector3.new(22,50,0);World.StepTrainingRoam(b,0);check(#b.model.pivots==0,'Leash incorrectly uses vertical displacement or inclusive bound')
b.root.Position=b.start+Vector3.new(22.001,0,0);b.airSince=1;b.root.AssemblyLinearVelocity=Vector3.new(5,5,5);b.root.AssemblyAngularVelocity=Vector3.new(3,3,3);World.StepTrainingRoam(b,.01)
check(#b.model.pivots==1 and same(b.lastGrounded,b.start) and b.airSince==nil,'Leash recovery state incomplete')
check(same(b.root.AssemblyLinearVelocity,Vector3.zero) and same(b.root.AssemblyAngularVelocity,Vector3.zero),'Leash recovery retained impulse')
local n=#b.humanoid.moves;World.StepTrainingRoam(b,1);check(#b.humanoid.moves==n,'Leash recovery skipped pause')

__GATES__
local quiet=make(true);quiet.health=37;quiet.lastTrainingHit=100;quiet.root.Position=quiet.start+Vector3.new(10,0,0)
local oldCredit=quiet.credit;World.Bots={quiet};World.StepTrainingRoam(quiet,100)
stepTraining(125);check(quiet.health==37 and quiet.credit==oldCredit and #quiet.model.pivots==0,'Quiet reset fired at exact boundary')
stepTraining(125.001);check(quiet.health==80 and quiet.alive and not quiet.root.Anchored and same(quiet.root.Position,quiet.start),'Quiet timeout did not restore mobile trainer home')
check(next(quiet.credit)==nil and quiet.credit~=oldCredit and quiet.trainingTarget==nil and quiet.strike==nil,'Quiet reset retained combat credit or target')
check(quiet.trainingDestination==nil and quiet.trainingStepAt==nil and quiet.humanoid.WalkSpeed==7 and #quiet.root.owners==1,'Quiet reset retained movement state')
local version=quiet.recoveryVersion;stepTraining(126);check(quiet.recoveryVersion==version,'Quiet timeout repeatedly reset healthy trainer')
local neverHit=make(true);neverHit.health=30;World.Bots={neverHit};stepTraining(1000);check(neverHit.health==30,'Missing last hit synthesized quiet timeout')
for _,gate in ipairs(gates)do
 check(gate(bot.start+Vector3.new(0,32,0),bot),'Home gate rejected vertical boundary')
 check(not gate(bot.start+Vector3.new(0,32.001,0),bot),'Home gate ignored vertical boundary')
 check(not gate(bot.start+Vector3.new(24,24,0),bot),'Home gate flattened three-dimensional distance')
end
print('PASS '..checks..' actual training roam/lifecycle assertions; fake movement only')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
rules=read('src/ReplicatedStorage/Shared/TrainingRules.luau')
gate_exprs=re.findall(r'\((?:ctx\.position|r\.Position)-bot\.start\)\.Magnitude<=TrainingRules\.Radius',server)
assert len(gate_exprs)==3,'Expected all three home-bound gates'
gates='local gates={'+','.join('function(playerPos,bot)local ctx={position=playerPos};local r={Position=playerPos};return '+expr+' end' for expr in gate_exprs)+'}\n'+r'''
local bot=make(true);bot.root.Position=bot.start+Vector3.new(18,0,0)
for _,gate in ipairs(gates)do
 for _,case in ipairs({{32,true},{32.001,false},{-32,true},{-32.001,false},{49,false},{-30,true}})do
  check(gate(bot.start+Vector3.new(case[1],0,0),bot)==case[2],'Training gate follows roaming target instead of fixed home')
 end
end
'''
code=setup+'local TrainingRules=(function()\n'+rules+'\nend)()\n'+stop+roam+update+life+auto_reset+spawn_code+tests.replace('__GATES__',gates)
if args.baseline:
 run(code,'Training roam missing')
 run(setup+stop+update+life+"local b=make(true);World.UpdateBot(b);check(not b.root.Anchored,'Baseline training restore remains anchored')",'Baseline training restore remains anchored')
 run(setup+spawn_code+"local b=spawnTrainer();check(b.humanoid.WalkSpeed>0,'Baseline training spawn has zero speed')",'Baseline training spawn has zero speed')
else:
 run(code)
 if args.negative_controls:
  cases=[(code.replace('RoamRadius=18','RoamRadius=30'),'Roam target outside bounded radius'),(code.replace('if now<(bot.trainingStepAt or 0) then return end','if false then return end'),'Roam tick throttle missing'),(code.replace('or now>=(bot.trainingMoveUntil or 0)',''),'Stuck trainer never retargeted'),(code.replace('>TrainingRules.ResetAfter','>=TrainingRules.ResetAfter'),'Quiet reset fired at exact boundary'),(code.replace('and bot.health<bot.maxHealth then restoreBot(bot) end','and bot.health<bot.maxHealth then end'),'Quiet timeout did not restore mobile trainer home'),(code.replace('if bot.strike or','if false or'),'Pause did not stop movement'),(code.replace('or bot.humanoid.PlatformStand',''),'Pause did not stop movement'),(code.replace('bot.root.Anchored=false;bot.model:PivotTo','bot.root.Anchored=bot.training~=nil;bot.model:PivotTo'),'Restore did not return mobile trainer home'),(code.replace('and bot.recoveryVersion==version',''),'Old life callback revived newer KO'),(code.replace('bot.trainingDestination=nil;bot.trainingNextMove=nil;bot.trainingStepAt=nil;bot.trainingMoveUntil=nil',''),'KO retained roam state'),(code.replace('(ctx.position-bot.start).Magnitude<=TrainingRules.Radius','(ctx.position-bot.root.Position).Magnitude<=TrainingRules.Radius'),'Training gate follows roaming target instead of fixed home')]
  for mutated,error in cases:
   if error is None:continue
   assert mutated!=code,'Mutation mismatch: '+error
   run(mutated,error)

