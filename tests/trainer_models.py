"""Actual makeBot/helpers differential against d05f431. Mock Instances, RNG and symbolic CFrames;
not native physics, rendering, animation or Roblox RNG-value evidence. Requires local baseline Git object.
"""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
PATH='src/ServerScriptService/World.luau'
BASE='d05f431'
current=(R/PATH).read_text(encoding='utf8')
try:baseline=subprocess.check_output(['git','show',BASE+':'+PATH],cwd=R,text=True,encoding='utf8',stderr=subprocess.PIPE)
except subprocess.CalledProcessError as exc:raise SystemExit('Trainer differential requires local Git object d05f431; no network fetch attempted.') from exc
def extracted(s):
 return (s[s.index('local C = {'):s.index('local function vehicle(')]+
 s[s.index('local names = {'):s.index('local function faceToward(')]+
 s[s.index('local function makeBot('):s.index('local function atmosphere()')])
SETUP=r'''
local count=0;local function check(v,m)assert(v,m);count+=1 end
local function fixture(sourceFactory,index,role,tier,compact,jobMode)
 local nodes={};local rngLog={};local Enum=setmetatable({},{__index=function(t,k)local v=setmetatable({},{__index=function(_,n)return k..'.'..n end});rawset(t,k,v);return v end})
 local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
 local Vector2={new=function(x,y)return {X=x,Y=y}end}
 local CF={};CF.__mul=function(a,b)return setmetatable({op='multiply',a=a,b=b},CF)end
 local CFrame={new=function(...)return setmetatable({op='new',values={...}},CF)end,Angles=function(...)return setmetatable({op='angles',values={...}},CF)end}
 local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end,new=function(r,g,b)return {R=r*255,G=g*255,B=b*255}end}
 local function tuple(...)return {...}end
 local UDim={new=tuple};local UDim2={fromOffset=tuple,fromScale=tuple,new=tuple};local NumberRange={new=tuple};local NumberSequence={new=tuple};local ColorSequence={new=tuple}
 local methods={}
 function methods:SetAttribute(k,v)self.attributes[k]=v end
 function methods:SetStateEnabled(k,v)self.states[k]=v end
 function methods:FindFirstChild(name)for _,n in ipairs(nodes)do if n.Parent==self and n.Name==name then return n end end end
 function methods:SetNetworkOwner(v)self.networkOwnerWasSet=true end
 local Instance={new=function(kind)local o=setmetatable({ClassName=kind,Name=kind,attributes={},states={},Transparency=0,Anchored=false},{__index=methods});table.insert(nodes,o);return o end}
 local Random={new=function(seed)local state=seed;return {NextInteger=function(_,a,b)state=(state*48271)%2147483647;table.insert(rngLog,{'int',a,b,state});return a+state%(b-a+1)end,NextNumber=function(_,a,b)state=(state*48271)%2147483647;table.insert(rngLog,{'number',a,b,state});return (a or 0)+(state/2147483647)*((b or 1)-(a or 0))end}end}
 local Config={CompactCity=compact,BotMaxHealth=80};local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
 local World={Bots={}};local RunService={IsRunning=function()return false end}
 local Collection={AddTag=function(_,model,tag)model.tag=tag end}
 local task={spawn=function()error('Unexpected constructor worker')end,delay=function()error('Unexpected delay')end}
 local function typeof(v)return getmetatable(v)==CF and 'CFrame' or type(v)end
 local make=sourceFactory(Instance,Enum,Vector3,Vector2,CFrame,Color3,UDim,UDim2,NumberRange,NumberSequence,ColorSequence,Random,Config,TrainingRules,World,RunService,Collection,task,typeof)
 local parent=Instance.new('Folder');parent.Name='Residents'
 local training=tier and TrainingRules.Tiers[tier]
 local job=jobMode and {name='Authored '..role,stations={{position=Vector3.new(1,3,2)}},quests={'garden'}} or nil
 make(parent,index,-245,-100,role,job,training)
 return {nodes=nodes,bot=World.Bots[1],rng=rngLog}
end
local function path(o)if not o then return 'nil'end;return (o.Parent and path(o.Parent)..'/' or '')..o.Name..':'..o.ClassName end
local function serial(v,seen)
 if type(v)~='table'then return tostring(v)end
 if v.ClassName then return '@'..path(v)end
 local keys={};for k in pairs(v)do table.insert(keys,k)end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 local out={};for _,k in ipairs(keys)do table.insert(out,tostring(k)..'='..serial(v[k]))end;return '{'..table.concat(out,';')..'}'
end
local function added(o)return o.Name:sub(1,7)=='Academy' or (o.Parent and o.Parent.Name:sub(1,7)=='Academy')end
local function compare(a,b,trainer)
 check(serial(a.rng)==serial(b.rng),'RNG draw sequence changed')
 check(serial(a.bot)==serial(b.bot),'Bot gameplay/state fields changed')
 local originals={};local extra={}
 for _,n in ipairs(b.nodes)do if added(n)then table.insert(extra,n)else table.insert(originals,n)end end
 if not trainer then check(#extra==0,'Trainer kit leaked into resident')end
 check(#originals==#a.nodes,'Original hierarchy count changed')
 for i,old in ipairs(a.nodes)do
  local new=originals[i];check(path(old)==path(new),'Original hierarchy changed')
  local keys={};for k in pairs(old)do keys[k]=true end;for k in pairs(new)do keys[k]=true end
  for k in pairs(keys)do
   local recolor=trainer and k=='Color' and (old.Name=='Torso' or old.Name=='Left Leg' or old.Name=='Right Leg' or old.Name=='LeftSleeve' or old.Name=='RightSleeve')
   local hidden=trainer and k=='Transparency' and (old.Name=='Jacket' or old.Name=='FighterArmband')
   if recolor then
    if old.Name=='LeftSleeve' or old.Name=='RightSleeve' then check(old.CanCollide==false and old.CanQuery==false and old.CanTouch==false,'Recolored sleeve is not safe costume')end
    check(serial(new[k])==serial({R=31,G=48,B=67}),'Unexpected body palette')
   elseif hidden then check(new[k]==1 and old.CanCollide==false and old.CanQuery==false and old.CanTouch==false,'Hidden part is not safe costume')
   else check(serial(old[k])==serial(new[k]),'Original property changed '..old.Name..'.'..k)end
  end
 end
 if not trainer then check(#extra==0,'Trainer kit leaked into resident');return end
 check(#extra==16,'Expected eight cosmetics and eight welds')
 local expected={AcademyChestLeft='Torso',AcademyChestRight='Torso',AcademyCenter='Torso',AcademyBack='Torso',AcademyBelt='Torso',AcademyWristLeft='Left Arm',AcademyWristRight='Right Arm',AcademyCollar='Torso'}
 local seen={}
 for _,n in ipairs(extra)do
  if n.ClassName=='Part'then
   check(expected[n.Name] and not seen[n.Name],'Unexpected/duplicate cosmetic');seen[n.Name]=true
   check(n.CanCollide==false and n.CanQuery==false and n.CanTouch==false and n.Massless==true and n.Anchored==false,'Cosmetic gameplay flags changed')
   check(n.Material=='Material.SmoothPlastic','Cosmetic material changed')
   local accents={rookie={R=111,G=196,B=180},brawler={R=219,G=120,B=94},elite={R=240,G=192,B=89}}
   local accented=n.Name=='AcademyCenter' or n.Name=='AcademyBelt' or n.Name=='AcademyWristLeft' or n.Name=='AcademyWristRight'
   local expectedColor=accented and accents[b.bot.training.id] or {R=238,G=230,B=207}
   check(serial(n.Color)==serial(expectedColor),'Tier palette incorrect')
   check(n.CollisionGroup=='Residents' and next(n.attributes)==nil,'Cosmetic authority changed')
   check(n.Size.X>0 and n.Size.X<=2.04 and n.Size.Y>0 and n.Size.Y<=1.3 and n.Size.Z>0 and n.Size.Z<=1.06,'Cosmetic unbounded dimensions')
   local welds=0;for _,w in ipairs(extra)do if w.Parent==n then check(w.ClassName=='WeldConstraint' and w.Part1==n and w.Part0.Name==expected[n.Name] and w.Part0.Parent==n.Parent,'Cosmetic attachment changed');welds+=1 end end
   check(welds==1,'Missing cosmetic weld')
  else check(n.ClassName=='WeldConstraint','Unexpected cosmetic object')end
 end
end
'''
ARGS='Instance,Enum,Vector3,Vector2,CFrame,Color3,UDim,UDim2,NumberRange,NumberSequence,ColorSequence,Random,Config,TrainingRules,World,RunService,Collection,task,typeof'
def build(source):
 return SETUP+'\nlocal old=function('+ARGS+')\n'+extracted(baseline)+'\nreturn makeBot end\nlocal new=function('+ARGS+')\n'+extracted(source)+r'''
return makeBot end
local roles={'Local','Tourist','Fighter','Commuter','Vendor','CafeWorker','Sanitation','BeachWorker','Gardener','Artist','Busker','Soccer'}
for _,compact in ipairs({false,true})do
 for index=1,20 do
  for _,role in ipairs(roles)do for _,job in ipairs({false,true})do compare(fixture(old,index,role,nil,compact,job),fixture(new,index,role,nil,compact,job),false)end end
  for tier=1,3 do compare(fixture(old,index,'Fighter',tier,compact,false),fixture(new,index,'Fighter',tier,compact,false),true)end
 end
end
print('PASS '..count..' actual constructor differential/safety assertions; synthetic engine/RNG')
'''
def run(source):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(build(source));p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],text=True,capture_output=True,timeout=30)
 finally:p.unlink()
if __name__=='__main__':
 stripped=current[:current.index('-- Original academy sparring kit:')]+current[current.index('local function faceToward('):]
 stripped=stripped.replace('    if training then trainerOutfit(model,torso,la,ra,ll,rl,training) end\n','')
 assert stripped==baseline,'Source outside bounded cosmetic insertion changed'
 print('PASS source contract: all other World behavior exactly baseline')
 out=run(current);print(out.stdout,end='');assert out.returncode==0,out.stderr
 if '--negative-controls' in sys.argv:
  call='if training then trainerOutfit(model,torso,la,ra,ll,rl,training) end'
  chest=next(line for line in current.splitlines() if 'accessory(model,torso,"AcademyChestLeft"' in line)
  cases=[
   ('p.CanQuery = false','p.CanQuery = true','Original property changed'),
   ('Vector3.new(2, 2, 1), cf, shirt, true','Vector3.new(3, 2, 1), cf, shirt, true','Original property changed'),
   (call,'trainerOutfit(model,torso,la,ra,ll,rl,training or TrainingRules.Tiers[1])','Trainer kit leaked into resident'),
   (chest,chest.replace('accessory(', 'local unsafe=accessory(',1)+';unsafe.CanQuery=true','Cosmetic gameplay flags changed'),
   (chest,chest.replace('Enum.Material.SmoothPlastic','Enum.Material.Fabric'),'Cosmetic material changed'),
   ('Color3.fromRGB(111,196,180)','Color3.fromRGB(240,192,89)','Tier palette incorrect'),
   ('local outfit = avatarRng:NextInteger(1, 5)','local outfit = avatarRng:NextInteger(1, 4)','RNG draw sequence changed'),
  ]
  for old,new,message in cases:
   assert old in current,old;out=run(current.replace(old,new));assert out.returncode and message in out.stderr,(message,out.stdout,out.stderr)
  print('PASS 7 trainer negative controls')
