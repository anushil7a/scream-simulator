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
local builtPads={}
local function part(_,name,size,position,color,material) local p={Name=name,Size=size,Position=position,Color=color,Material=material};if name:sub(1,12)=="TrainingPad_" then builtPads[name]=p end;return p end
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
 local pad=builtPads['TrainingPad_'..tier.id];local spec
 for _,v in ipairs(Layout.PartSpecs)do if v.id=='TrainingPad'..i then spec=v end end
 check(pad and spec and pad.Color==spec.color,'Authoritative pad masks compact tier color')
 check(pad.Size.X==64 and pad.Size.Y==.2 and pad.Size.Z==64 and pad.Position.X==home.x and pad.Position.Y==.1 and pad.Position.Z==home.z and pad.Material==Enum.Material.SmoothPlastic,'Pad geometry or material changed')
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
fountain=read('src/ServerScriptService/Fountain.luau');art=read('src/ServerScriptService/StreetArt.luau')
soccerdecl=soccer[soccer.index('local compact='):soccer.index('local function sphere(')]
volleydecl=volley[volley.index('local compact='):volley.index('local gameState')]
socceroutside=re.search(r'if (nextPosition.X<minimum.X[^\n]+) then',soccer)[1]
volleyoutside=re.search(r'if (position.X<minimum.X[^\n]+) then fault',volley)[1]
sports='\ndo\n'+soccerdecl+"\ncheck(origin==Layout.Soccer.origin and center==Layout.Soccer.center and minimum==Layout.Soccer.min and maximum==Layout.Soccer.max,'Soccer mapping wrong')\ncheck(origin.Y==1.2,'Soccer floor height wrong')\nlocal function outside(nextPosition)return "+socceroutside+" end\n"
sports+="for _,v in ipairs({Vector3.new(minimum.X-.01,1,center.Z),Vector3.new(maximum.X+.01,1,center.Z),Vector3.new(center.X,1,minimum.Z-.01),Vector3.new(center.X,1,maximum.Z+.01)})do check(outside(v),'Soccer outside accepted')end\ncheck(not outside(minimum) and not outside(maximum),'Soccer boundary rejected')\nend\ndo\n"+volleydecl
sports+="\ncheck(serve==Layout.Volley.serve and minimum==Layout.Volley.min and maximum==Layout.Volley.max and netZ==Layout.Volley.netZ,'Volley mapping wrong')\ncheck(floorBallY==1.1 and minimumCrossingHeight==9.2,'Volley floor/net height wrong')\nlocal function outside(position)return "+volleyoutside+" end\nfor _,v in ipairs({Vector3.new(minimum.X-.01,1,netZ),Vector3.new(maximum.X+.01,1,netZ),Vector3.new(serve.X,1,minimum.Z-.01),Vector3.new(serve.X,1,maximum.Z+.01)})do check(outside(v),'Volley outside accepted')end\ncheck(not outside(minimum) and not outside(maximum),'Volley boundary rejected')\nend\n"
# Exercise the actual net-height predicate and landing branch, not just declared values.
net_predicate=re.search(r'elseif (old.Y[^\n]+) then',volley)[1]
a=volley.index('  if state.phase=="Playing" then');landing=volley[a:volley.index('  state.position=position',a)]
height_tests="\ndo\n"+volleydecl+"\nlocal function netHit(y)local old={Y=y};local position={Y=y};local alpha=.5;return "+net_predicate+" end\ncheck(netHit(9.199) and not netHit(9.2),'Actual volley crossing height wrong')\nlocal function land(y)\n local position=V(serve.X,y,serve.Z);local state={phase='Playing'};local reason\n local function fault(_,why)reason=why end\n"+landing+"\n return position,reason\nend\nlocal landed,why=land(1.1);check(landed.Y==1.1 and why=='Ball landed','Actual volley landing threshold wrong')\nlocal airborne,reason=land(1.101);check(airborne.Y==1.101 and reason==nil,'Volley landed above threshold')\nend\n"
equipment=read('src/ServerScriptService/Equipment.luau')
module_checks=r'''
do
 local V3={}
 local Vector3
 V3.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
 V3.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
 V3.__unm=function(a)return Vector3.new(-a.X,-a.Y,-a.Z)end
 V3.__mul=function(a,b)
  if type(a)=='number' then return Vector3.new(a*b.X,a*b.Y,a*b.Z)
  elseif type(b)=='number' then return Vector3.new(a.X*b,a.Y*b,a.Z*b)
  else return Vector3.new(a.X*b.X,a.Y*b.Y,a.Z*b.Z) end
 end
 Vector3={new=function(x,y,z)return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},V3)end}
 Vector3.zero=Vector3.new(0,0,0)
 Vector3.yAxis=Vector3.new(0,1,0)
 local Vector2={new=function(x,y)return {X=x,Y=y}end}
 local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end,new=function(r,g,b)return {R=(r or 0)*255,G=(g or 0)*255,B=(b or 0)*255}end}
 local ColorSequence={new=function(a,b)return {colors=b and {a,b} or {a}}end}
 local NumberSequenceKeypoint={new=function(t,v)return {Time=t,Value=v}end}
 local NumberSequence={new=function(v)
  if type(v)=='number' then return {Keypoints={{Time=0,Value=v},{Time=1,Value=v}},scalar=v}
  else return {Keypoints=v} end
 end}
 local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
 local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end,fromScale=function(x,y)return {X=x,Y=y}end}
 local CF={};CF.__index=CF;local CFrame={}
 CF.__mul=function(a,b)return CFrame.new((a.X or 0)+(b.X or 0),(a.Y or 0)+(b.Y or 0),(a.Z or 0)+(b.Z or 0))end
 function CF:ToObjectSpace()return CFrame.new(0,0,0)end
 function CFrame.new(x,y,z)
  if type(x)=='table' then return setmetatable({X=x.X or 0,Y=x.Y or 0,Z=x.Z or 0},CF) end
  return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},CF)
 end
 function CFrame.Angles()return CFrame.new(0,0,0)end
 function CFrame.fromMatrix(pos)return CFrame.new(pos)end
 local Enum={
  Material={SmoothPlastic='SmoothPlastic',Neon='Neon',Limestone='Limestone',CeramicTiles='CeramicTiles',Glass='Glass'},
  PartType={Ball='Ball',Cylinder='Cylinder'},
  Font={GothamMedium='GothamMedium',GothamBold='GothamBold'},
  ApplyStrokeMode={Border='Border',Contextual='Contextual'},
  KeyCode={F='F'},
  ModelStreamingMode={Atomic='Atomic'},
  NormalId={Front='Front'},
  SurfaceGuiSizingMode={FixedSize='FixedSize'},
 }
 local function signal()return {Connect=function()return {Disconnect=function()end}end}end
 local created={}
 local function makeInst(class)
  local raw={ClassName=class,attributes={},children={}}
  if class=='ProximityPrompt' then raw.Triggered=signal() end
  local proxy={}
  local mt={
   __index=function(_,k)
    if k=='FindFirstChild' then
     return function(_,name)
      for _,c in ipairs(raw.children)do if c.Name==name then return c end end
      return nil
     end
    elseif k=='GetChildren' then
     return function()return raw.children end
    elseif k=='GetDescendants' then
     return function()
      local out={}
      local function walk(list)for _,c in ipairs(list)do table.insert(out,c);walk(c._children) end end
      walk(raw.children)
      return out
     end
    elseif k=='IsA' then
     return function(_,kind)return raw.ClassName==kind or (kind=='BasePart' and raw.ClassName=='Part')end
    elseif k=='Clone' then
     return function()
      local copy=makeInst(raw.ClassName)
      for prop,val in pairs(raw)do
       if prop~='children' and prop~='Parent' and prop~='attributes' and prop~='ClassName' and prop~='Triggered' then copy[prop]=val end
      end
      for _,child in ipairs(raw.children)do child:Clone().Parent=copy end
      return copy
     end
    elseif k=='ScaleTo' or k=='PivotTo' then
     return function()end
    elseif k=='GetBoundingBox' then
     return function()return CFrame.new(0,0,0),Vector3.new(1,2,1)end
    elseif k=='GetPivot' then
     return function()return CFrame.new(0,0,0)end
    elseif k=='Destroy' then
     return function(self)
      raw.destroyed=true
      if raw.Parent then
       local list=raw.Parent._children
       for i=#list,1,-1 do if list[i]==self then table.remove(list,i) end end
       raw.Parent=nil
      end
     end
    elseif k=='SetAttribute' then
     return function(_,attr,val)raw.attributes[attr]=val end
    elseif k=='_children' then
     return raw.children
    end
    return raw[k]
   end,
   __newindex=function(self,k,v)
    if k=='Parent' then
     if raw.Parent then
      local old=raw.Parent._children
      for i=#old,1,-1 do if old[i]==self then table.remove(old,i) end end
     end
     raw.Parent=v
     if v and v._children then table.insert(v._children,self) end
    else
     raw[k]=v
    end
   end
  }
  local inst=setmetatable(proxy,mt)
  table.insert(created,inst)
  return inst
 end
 local Instance={new=function(class)return makeInst(class)end}
 local Equipment=(function()
'''+equipment+r'''
 end)()
 local function approx(a,b)return math.abs(a-b)<1e-6 end
 local function checkVec(v,x,y,z,msg)check(v and approx(v.X,x) and approx(v.Y,y) and approx(v.Z,z),msg)end
 local function checkColor(c,r,g,b,msg)check(c and c.R==r and c.G==g and c.B==b,msg)end
 local function testRig(handName,handSize,handCF)
  local character=Instance.new('Model')
  local hand=Instance.new('Part');hand.Name=handName;hand.Size=handSize;hand.CFrame=handCF;hand.Parent=character
  local player={Character=character}
  Equipment.Sync(player,true)
  local model=character:FindFirstChild('MicroSpeakerAccessory')
  check(model and model.ClassName=='Model' and model.Parent==character,'Equipment model missing for '..handName)
  check(#model._children==14,'Expected 14 equipment parts for '..handName)
  local byName={};local grilleSlots={}
  for _,p in ipairs(model._children)do
   check(p.ClassName=='Part','Equipment child not a Part')
   check(p.CanCollide==false and p.CanTouch==false and p.CanQuery==false and p.Massless==true,'Equipment part flags unsafe')
   local weld=p._children[1]
   check(#p._children==1 and weld and weld.ClassName=='WeldConstraint' and weld.Part0==hand and weld.Part1==p and weld.Parent==p,'Equipment weld missing hand')
   if p.Name=='GrilleSlot' then table.insert(grilleSlots,p)
   else check(byName[p.Name]==nil,'Duplicate equipment part '..p.Name);byName[p.Name]=p end
  end
  local gripY=-handSize.Y/2+.15
  local function checkPart(name,sx,sy,sz,ox,oy,oz,r,g,b,mat,shape)
   local p=byName[name]
   check(p~=nil,'Missing equipment part '..name)
   checkVec(p.Size,sx,sy,sz,name..' size wrong')
   checkVec(p.CFrame,handCF.X+ox,handCF.Y+gripY+oy,handCF.Z-.25+oz,name..' CFrame wrong')
   checkColor(p.Color,r,g,b,name..' color wrong')
   check(p.Material==mat,name..' material wrong')
   check(p.Shape==shape,name..' shape wrong')
  end
  checkPart('Grip',.25,.6,.25,0,0,0,46,57,64,Enum.Material.SmoothPlastic,nil)
  checkPart('Enclosure',.72,.78,.5,0,.42,-.28,38,56,62,Enum.Material.SmoothPlastic,nil)
  checkPart('GoldTrim',.64,.7,.06,0,.42,-.56,232,186,92,Enum.Material.SmoothPlastic,nil)
  checkPart('SpeakerGrille',.54,.58,.06,0,.42,-.6,36,42,47,Enum.Material.SmoothPlastic,nil)
  checkPart('StatusLight',.08,.08,.04,.23,.7,-.65,119,233,182,Enum.Material.Neon,Enum.PartType.Ball)
  checkPart('PommelCap',.29,.08,.29,0,-.32,0,232,186,92,Enum.Material.SmoothPlastic,nil)
  checkPart('GuardCollar',.34,.08,.32,0,.22,-.08,238,230,207,Enum.Material.SmoothPlastic,nil)
  checkPart('AcousticCone',.18,.18,.05,0,.42,-.64,232,186,92,Enum.Material.SmoothPlastic,Enum.PartType.Ball)
  checkPart('TelemetrySpine',.22,.56,.06,0,.42,-.02,238,230,207,Enum.Material.SmoothPlastic,nil)
  check(#grilleSlots==5,'Expected 5 GrilleSlot parts')
  for i=-2,2 do
   local found=false
   for _,slot in ipairs(grilleSlots)do
    if approx(slot.CFrame.Y,handCF.Y+gripY+.42+i*.1) then
     found=true
     checkVec(slot.Size,.43,.025,.02,'GrilleSlot size wrong')
     checkVec(slot.CFrame,handCF.X,handCF.Y+gripY+.42+i*.1,handCF.Z-.25-.64,'GrilleSlot CFrame wrong')
     checkColor(slot.Color,98,117,120,'GrilleSlot color wrong')
     check(slot.Material==Enum.Material.SmoothPlastic,'GrilleSlot material wrong')
    end
   end
   check(found,'Missing GrilleSlot index '..i)
  end
  Equipment.Sync(player,true)
  check(character:FindFirstChild('MicroSpeakerAccessory')==model and #character._children==2 and #model._children==14 and not model.destroyed,'Equipment.Sync re-sync not idempotent')
  Equipment.Sync(player,false)
  check(model.destroyed==true and character:FindFirstChild('MicroSpeakerAccessory')==nil,'Equipment.Sync unequip did not destroy')
  Equipment.Sync(player,false)
  check(character:FindFirstChild('MicroSpeakerAccessory')==nil,'Equipment.Sync double unequip failed')
 end
 testRig('RightHand',Vector3.new(1,1,1),CFrame.new(10,5,2))
 testRig('Right Arm',Vector3.new(1,2,1),CFrame.new(-4,6,3))
 local tags={}
 local workspace={ScreamSimulatorWorld=Instance.new('Folder')}
 local game={GetService=function(_,name)
  if name=='RunService' then return {Heartbeat=signal()}
  elseif name=='Players' then return {PlayerRemoving=signal()}
  elseif name=='ReplicatedStorage' then return {Shared={Config='Config'}}
  elseif name=='CollectionService' then return {AddTag=function(_,inst,tag)tags[inst]=tags[inst] or {};tags[inst][tag]=true end}
  else error('Unexpected service '..tostring(name)) end
 end}
 local script={Parent={CombatRules='CombatRules'}}
 local require=function(target)
  if target=='CombatRules' then return {}
  elseif target=='Config' then return Config
  else error('Unexpected require '..tostring(target)) end
 end
 local Volley=(function()
'''+volley+r'''
 end)()
 created={}
 local parent=Instance.new('Folder')
 local volleyModel=Volley.Start(parent)
 local readout=volleyModel:FindFirstChild('CourtReadout')
 check(readout~=nil,'CourtReadout missing')
 local gui=readout._children[1]
 check(gui and gui.ClassName=='BillboardGui','CourtReadout BillboardGui missing')
 local text=gui._children[1]
 check(text and text.ClassName=='TextLabel','CourtReadout TextLabel missing')
 local stroke
 for _,n in ipairs(created)do if n.ClassName=='UIStroke' and n.Name=='ReadoutStroke' then stroke=n end end
 check(stroke~=nil,'CourtReadout ReadoutStroke missing')
 check(stroke.ApplyStrokeMode==Enum.ApplyStrokeMode.Border,'CourtReadout ReadoutStroke ApplyStrokeMode wrong')
 checkColor(stroke.Color,235,190,105,'CourtReadout ReadoutStroke color wrong')
 check(stroke.Thickness==1,'CourtReadout ReadoutStroke thickness wrong')
 check(approx(stroke.Transparency,.4),'CourtReadout ReadoutStroke transparency wrong')
 check(stroke.Parent==text,'CourtReadout ReadoutStroke parent wrong')
 local Soccer=(function()
'''+soccer+r'''
 end)()
 created={}
 local soccerPlayer={UserId=101,DisplayName='Tester'}
 Soccer.Start(soccerPlayer,function()end)
 local soccerModel=workspace.ScreamSimulatorWorld:FindFirstChild('SoccerAttempt_101')
 check(soccerModel~=nil,'SoccerAttempt model missing')
 local function checkCaption(partName)
  local p=soccerModel:FindFirstChild(partName)
  check(p~=nil,'Soccer part missing '..partName)
  local cgui=p:FindFirstChild('ChallengeCaption')
  check(cgui and cgui.ClassName=='BillboardGui','Soccer ChallengeCaption missing on '..partName)
  local clabel=cgui._children[1]
  check(clabel and clabel.ClassName=='TextLabel','Soccer caption TextLabel missing on '..partName)
  checkColor(clabel.BackgroundColor3,25,48,51,'Soccer caption bg color wrong on '..partName)
  check(approx(clabel.BackgroundTransparency,.12),'Soccer caption bg transparency wrong on '..partName)
  checkColor(clabel.TextColor3,255,239,205,'Soccer caption text color wrong on '..partName)
  check(clabel.TextWrapped==true,'Soccer caption TextWrapped wrong on '..partName)
  local cstroke=clabel:FindFirstChild('CaptionStroke')
  check(cstroke and cstroke.ClassName=='UIStroke','SoccerChallenge CaptionStroke missing')
  check(cstroke.ApplyStrokeMode==Enum.ApplyStrokeMode.Border,'SoccerChallenge CaptionStroke ApplyStrokeMode wrong')
  checkColor(cstroke.Color,235,190,105,'SoccerChallenge CaptionStroke color wrong')
  check(cstroke.Thickness==1,'SoccerChallenge CaptionStroke thickness wrong')
  check(approx(cstroke.Transparency,.4),'SoccerChallenge CaptionStroke transparency wrong')
  check(cstroke.Parent==clabel,'SoccerChallenge CaptionStroke parent wrong')
 end
 checkCaption('ChallengeBall')
 for i=1,3 do checkCaption('LostTrainingBall'..i) end
 Soccer.Cancel(soccerPlayer)
 check(soccerModel.destroyed==true and workspace.ScreamSimulatorWorld:FindFirstChild('SoccerAttempt_101')==nil,'Soccer.Cancel did not destroy model')
 local Fountain=(function()
'''+fountain+r'''
 end)()
 created={}
 local template=Instance.new('Model')
 local meshPart=Instance.new('Part');meshPart.Name='Mesh';meshPart.Parent=template
 local fountainParent=Instance.new('Folder')
 local fountainModel=Fountain.create(template,fountainParent,Vector3.new(0,0,0))
 check(fountainModel and fountainModel.Name=='MosaicFountain' and tags[fountainModel] and tags[fountainModel].OptionalLandmarkVisual,'Fountain model or tag missing')
 local fallbackVisual=fountainModel:FindFirstChild('FallbackVisual')
 check(fallbackVisual~=nil,'Fountain FallbackVisual missing')
 local fallbackParts=0
 for _,c in ipairs(fallbackVisual._children)do if c.ClassName=='Part' then fallbackParts+=1 end end
 check(fallbackParts==28,'Fountain FallbackVisual part count wrong')
 local colliderNames={'FountainCollision','ColumnCollision','BowlCollision'}
 local colliderCount=0
 for _,cname in ipairs(colliderNames)do
  local col=fountainModel:FindFirstChild(cname)
  if col and col.ClassName=='Part' and col.Shape==Enum.PartType.Cylinder and col.CanCollide==true then colliderCount+=1 end
 end
 check(colliderCount==3,'Fountain solid collision cylinder count wrong')
 local fountainCollider=fountainModel:FindFirstChild('FountainCollision')
 for i=0,3 do
  local stream=fountainCollider:FindFirstChild('WaterStream'..i)
  check(stream and stream.ClassName=='Beam','Fountain WaterStream missing '..i)
  check(#stream.Color.colors==2,'Fountain WaterStream color wrong')
  checkColor(stream.Color.colors[1],220,248,252,'Fountain WaterStream color1 wrong')
  checkColor(stream.Color.colors[2],132,216,228,'Fountain WaterStream color2 wrong')
  local kps=stream.Transparency.Keypoints
  check(#kps==3,'Fountain WaterStream transparency keypoints wrong')
  check(approx(kps[1].Time,0) and approx(kps[1].Value,.15),'Fountain WaterStream keypoint 1 wrong')
  check(approx(kps[2].Time,.7) and approx(kps[2].Value,.28),'Fountain WaterStream keypoint 2 wrong')
  check(approx(kps[3].Time,1) and approx(kps[3].Value,.55),'Fountain WaterStream keypoint 3 wrong')
  local core=fountainCollider:FindFirstChild('WaterCore'..i)
  check(core and core.ClassName=='Beam','Fountain WaterCore missing')
  check(approx(core.Width0,.06) and approx(core.Width1,.1),'Fountain WaterCore width wrong')
  check(#core.Color.colors==1,'Fountain WaterCore color count wrong')
  checkColor(core.Color.colors[1],245,253,255,'Fountain WaterCore color wrong')
  check(approx(core.Transparency.scalar,.2),'Fountain WaterCore transparency wrong')
 end
 local Art=(function()
'''+art+r'''
 end)()
 local function checkArt(coastal,expectedTitle)
  created={}
  local artParent=Instance.new('Folder')
  local wall=Art.create(artParent,CFrame.new(0,3,0),12,coastal)
  check(wall and wall.Name=='CourtyardMural','StreetArt CourtyardMural missing')
  check(wall.CanCollide==false and wall.CanTouch==false and wall.CanQuery==false and wall.CastShadow==false,'StreetArt CourtyardMural physics flags unsafe')
  local canvas=wall:FindFirstChild('OriginalStreetArt')
  check(canvas and canvas.ClassName=='SurfaceGui','StreetArt OriginalStreetArt SurfaceGui missing')
  local paper=canvas:FindFirstChild('Paper')
  check(paper~=nil,'StreetArt Paper missing')
  local border=paper:FindFirstChild('MuralBorder')
  check(border and border.ClassName=='UIStroke','StreetArt MuralBorder missing')
  check(border.ApplyStrokeMode==Enum.ApplyStrokeMode.Border,'StreetArt MuralBorder ApplyStrokeMode wrong')
  checkColor(border.Color,39,71,78,'StreetArt MuralBorder color wrong')
  check(border.Thickness==3,'StreetArt MuralBorder thickness wrong')
  check(approx(border.Transparency,.25),'StreetArt MuralBorder transparency wrong')
  local title=canvas:FindFirstChild('MuralTitle')
  check(title and title.ClassName=='TextLabel' and title.Text==expectedTitle,'StreetArt MuralTitle text wrong')
  local accent=canvas:FindFirstChild('MuralAccent')
  check(accent and accent.ClassName=='Frame','StreetArt MuralAccent missing')
  check(accent.Position.X==335 and accent.Position.Y==92 and accent.Size.X==132 and accent.Size.Y==4,'StreetArt MuralAccent geometry wrong')
  checkColor(accent.BackgroundColor3,242,166,75,'StreetArt MuralAccent color wrong')
  local accentCorner=accent._children[1]
  check(accentCorner and accentCorner.ClassName=='UICorner' and approx(accentCorner.CornerRadius.Scale,.5),'StreetArt MuralAccent corner missing')
 end
 checkArt(true,'SOL I MAR')
 checkArt(false,'VIU EL BARRI')
end
print('PASS '..checks..' actual compact integration assertions; mocks/snippets, not native physics')
'''
trainer_loop=spawn[spawn.index('    for index,originalTier'):spawn.index('    if layout.traffic') ]
legacy='\nConfig.CompactCity=false;builtPads={}\n'+trainer_loop+'''
for _,tier in ipairs(TrainingRules.Tiers)do local pad=builtPads['TrainingPad_'..tier.id]
 check(pad.Color==C.green and pad.Position.X==tier.x and pad.Position.Y==1.1 and pad.Position.Z==tier.z,'Original-map pad appearance or position changed')
 check(pad.Size.X==64 and pad.Size.Y==.2 and pad.Size.Z==64,'Original-map pad geometry changed')
end
Config.CompactCity=true;World.Bots={}
'''
code=setup+pre+layout+bridge+config+citybridge+city+worldsetup+spawn+worldchecks+legacy+reset+rescuechecks+height_tests+sports+module_checks
def run(body,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(body);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(code)
if args.negative_controls:
 for old,new,error in [('then padColor=spec.color;break end','then padColor=C.green;break end','Authoritative pad masks compact tier color'),('tier=table.clone(originalTier)','tier=originalTier','Trainer relocation did not clone tier'),('if layout.traffic~=false then','if true then','Legacy traffic created'),('resetMovement(p,s,h,r);running=false','running=false','Compact rescue retained own seat'),('if Config.ObjectDestruction==true then Destruction.Start','if true then Destruction.Start','Disabled destruction started'),('if Config.ObjectDestruction==true and obstruction then','if obstruction then','Disabled sustained destruction emitted target'),('Config.ObjectDestruction==true and Destruction.Damage','true and Destruction.Damage','Disabled legacy destruction damaged'),('nextPosition.X<minimum.X','nextPosition.X< -9999','Soccer outside accepted'),('position.X<minimum.X','position.X< -9999','Volley outside accepted'),('alpha<minimumCrossingHeight','alpha<10.2','Actual volley crossing height wrong'),('position.Y<=floorBallY','position.Y<=2.1','Volley landed above threshold'),('add("PommelCap",','add("PommelX",','Missing equipment part PommelCap'),('add("GuardCollar",','add("GuardX",','Missing equipment part GuardCollar'),('add("AcousticCone",','add("AcousticX",','Missing equipment part AcousticCone'),('add("TelemetrySpine",','add("TelemetryX",','Missing equipment part TelemetrySpine'),('add("AcousticCone",Vector3.new(.18,.18,.05),CFrame.new(0,.42,-.64),Color3.fromRGB(232,186,92),Enum.PartType.Ball)','add("AcousticCone",Vector3.new(.18,.18,.05),CFrame.new(0,.42,-.64),Color3.fromRGB(232,186,92))','AcousticCone shape wrong'),('local existing=character:FindFirstChild("MicroSpeakerAccessory")\n if not equipped then if existing then existing:Destroy() end;return end\n if existing then return end','local existing=character:FindFirstChild("MicroSpeakerAccessory")\n if not equipped then if existing then existing:Destroy() end;return end\n if false then return end','Equipment.Sync re-sync not idempotent'),('local existing=character:FindFirstChild("MicroSpeakerAccessory")\n if not equipped then if existing then existing:Destroy() end;return end','local existing=character:FindFirstChild("MicroSpeakerAccessory")\n if not equipped then return end','Equipment.Sync unequip did not destroy'),('part.CanQuery=false','part.CanQuery=true','Equipment part flags unsafe'),('weld.Part0=torso','weld.Part0=nil','Equipment weld missing hand'),('stroke.Name="ReadoutStroke"','stroke.Name="WrongStroke"','CourtReadout ReadoutStroke missing'),('stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border','stroke.ApplyStrokeMode=nil','CourtReadout ReadoutStroke ApplyStrokeMode wrong'),('stroke.Color=Color3.fromRGB(235,190,105)','stroke.Color=Color3.fromRGB(0,0,0)','CourtReadout ReadoutStroke color wrong'),('stroke.Thickness=1;stroke.Transparency=.4','stroke.Thickness=2;stroke.Transparency=.4','CourtReadout ReadoutStroke thickness wrong'),('stroke.Thickness=1;stroke.Transparency=.4','stroke.Thickness=1;stroke.Transparency=0','CourtReadout ReadoutStroke transparency wrong'),('stroke.Parent=text','stroke.Parent=gui','CourtReadout ReadoutStroke parent wrong'),('stroke.Name="CaptionStroke"','stroke.Name="WrongCaptionStroke"','SoccerChallenge CaptionStroke missing'),('stroke.Color=Color3.fromRGB(235,190,105);stroke.Thickness=1;stroke.Transparency=.4;stroke.Parent=label','stroke.Color=Color3.fromRGB(0,0,0);stroke.Thickness=1;stroke.Transparency=.4;stroke.Parent=label','SoccerChallenge CaptionStroke color wrong'),('stroke.Thickness=1;stroke.Transparency=.4;stroke.Parent=label','stroke.Thickness=2;stroke.Transparency=.4;stroke.Parent=label','SoccerChallenge CaptionStroke thickness wrong'),('stroke.Thickness=1;stroke.Transparency=.4;stroke.Parent=label','stroke.Thickness=1;stroke.Transparency=0;stroke.Parent=label','SoccerChallenge CaptionStroke transparency wrong'),('core.Name="WaterCore"..i','core.Name="WrongCore"..i','Fountain WaterCore missing'),('core.Width0=.06;core.Width1=.1','core.Width0=.2;core.Width1=.1','Fountain WaterCore width wrong'),('core.Color=ColorSequence.new(Color3.fromRGB(245,253,255))','core.Color=ColorSequence.new(Color3.fromRGB(0,0,0))','Fountain WaterCore color wrong'),('core.Transparency=NumberSequence.new(.2)','core.Transparency=NumberSequence.new(.9)','Fountain WaterCore transparency wrong'),('stream.Color=ColorSequence.new(Color3.fromRGB(220,248,252),Color3.fromRGB(132,216,228))','stream.Color=ColorSequence.new(Color3.fromRGB(156,225,234))','Fountain WaterStream color wrong'),('NumberSequenceKeypoint.new(0,.15),NumberSequenceKeypoint.new(.7,.28),NumberSequenceKeypoint.new(1,.55)','NumberSequenceKeypoint.new(0,.15),NumberSequenceKeypoint.new(1,.55)','Fountain WaterStream transparency keypoints wrong'),('NumberSequenceKeypoint.new(.7,.28)','NumberSequenceKeypoint.new(.7,.9)','Fountain WaterStream keypoint 2 wrong'),('border.Name="MuralBorder"','border.Name="WrongBorder"','StreetArt MuralBorder missing'),('border.Thickness=3;border.Transparency=.25','border.Thickness=1;border.Transparency=.25','StreetArt MuralBorder thickness wrong'),('border.Thickness=3;border.Transparency=.25','border.Thickness=3;border.Transparency=0','StreetArt MuralBorder transparency wrong'),('shape("MuralAccent",335,92,132,4,colors.sun,true)','shape("WrongAccent",335,92,132,4,colors.sun,true)','StreetArt MuralAccent missing'),('shape("MuralAccent",335,92,132,4,colors.sun,true)','shape("MuralAccent",335,92,100,4,colors.sun,true)','StreetArt MuralAccent geometry wrong'),('shape("MuralAccent",335,92,132,4,colors.sun,true)','shape("MuralAccent",335,92,132,4,colors.sun,false)','StreetArt MuralAccent corner missing')]:
  changed=code.replace(old,new);assert changed!=code,old;run(changed,error)
client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
assert 'Next destruction tier:' not in client and 'All destruction tiers unlocked' not in client,'UI advertises disabled destruction tiers'
print('PASS no disabled destruction tier advertisement source contract')
