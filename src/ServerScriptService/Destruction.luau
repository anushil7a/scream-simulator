local Players=game:GetService('Players')
local Collection=game:GetService('CollectionService')
local Rules=require(game.ReplicatedStorage.Shared.DestructionRules)
local Service={objects={},ids={}}
function Service.Register(model)
 if Service.objects[model] then return end
 local kind=model:GetAttribute('DestructibleType');local spec=Rules.Types[kind]
 if not spec then return end
 local parts={}
 for _,part in ipairs(model:GetDescendants()) do
  if part:IsA('BasePart') then parts[part]={color=part.Color,transparency=part.Transparency,collide=part.CanCollide,query=part.CanQuery,touch=part.CanTouch,seatDisabled=part:IsA("Seat") and part.Disabled or false} end
 end
 if next(parts)==nil then return end
 local cf,size=model:GetBoundingBox()
 local id=string.format("%s:%.3f:%.3f:%.3f",kind,cf.Position.X,cf.Position.Y,cf.Position.Z)
 if Service.ids[id] and Service.ids[id]~=model then warn("Duplicate destructible position",id);return end
 Service.ids[id]=model;model:SetAttribute("ObjectId",id)
 Service.objects[model]={parts=parts,kind=kind,health=spec.health,box=cf,size=size,version=0,prompts={}}
 for _,item in ipairs(model:GetDescendants()) do if item:IsA("ProximityPrompt") then Service.objects[model].prompts[item]=item.Enabled end end
 model:SetAttribute('ObjectName',spec.name);model:SetAttribute('ObjectHealth',spec.health);model:SetAttribute('ObjectMaxHealth',spec.health);model:SetAttribute('RequiredLevel',spec.level);model:SetAttribute('Destroyed',false)
end
local function occupied(object)
 local characters={};for _,p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(characters,p.Character) end end
 local world=Service.world
 if world then for _,model in ipairs(game:GetService("CollectionService"):GetTagged("CityResident")) do if model:IsDescendantOf(world) then table.insert(characters,model) end end end
 if #characters==0 then return false end
 local params=OverlapParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances=characters;params.MaxParts=1;params.RespectCanCollide=true
 return #workspace:GetPartBoundsInBox(object.box,object.size+Vector3.new(2,3,2),params)>0
end
local function restore(model,object,version)
 if not model.Parent or Service.objects[model]~=object or object.version~=version then return end
 if occupied(object) then model:SetAttribute('RepairAt',workspace:GetServerTimeNow()+5);task.delay(5,function() restore(model,object,version) end);return end
 local spec=Rules.Types[object.kind];object.health=spec.health
 for part,original in pairs(object.parts) do if part.Parent then part.Transparency=original.transparency;part.CanCollide=original.collide;part.CanQuery=original.query;part.CanTouch=original.touch;part.Color=original.color;if part:IsA("Seat") then part.Disabled=original.seatDisabled end end end
 for prompt,enabled in pairs(object.prompts) do if prompt.Parent then prompt.Enabled=enabled end end
 model:SetAttribute('ObjectHealth',spec.health);model:SetAttribute('Destroyed',false);model:SetAttribute('RepairAt',0);model:SetAttribute('DamageStage',0)
end
function Service.Damage(instance,level,damage)
 local model=instance
 while model and not Service.objects[model] do model=model.Parent end
 local object=model and Service.objects[model]
 if not object then return nil end
 local health,destroyed,reason=Rules.Hit(object.kind,level,object.health,damage)
 if reason then return {model=model,reason=reason,required=Rules.Types[object.kind].level} end
 object.health=health;object.lastDamaged=os.clock();model:SetAttribute('ObjectHealth',health)
 local ratio=health/Rules.Types[object.kind].health;model:SetAttribute('DamageStage',destroyed and 3 or ratio<.35 and 2 or ratio<.7 and 1 or 0)
 for part,original in pairs(object.parts) do if part.Parent then
  if destroyed then part.Transparency=1;part.CanCollide=false;part.CanQuery=false;part.CanTouch=false;if part:IsA("Seat") then if part.Occupant then part.Occupant.Sit=false end;part.Disabled=true end
  else part.Color=original.color:Lerp(Color3.fromRGB(90,76,67),(1-ratio)*.45) end
 end end
 if destroyed then
  for prompt in pairs(object.prompts) do if prompt.Parent then prompt.Enabled=false end end
  model:SetAttribute('Destroyed',true)
 end
 -- Every accepted hit restarts repair, including damage that leaves the object standing.
 -- The version guard prevents an older deadline restoring through a newer hit.
 object.version+=1;local version=object.version;local duration=Rules.Types[object.kind].repair
 model:SetAttribute('RepairAt',workspace:GetServerTimeNow()+duration)
 task.delay(duration,function() restore(model,object,version) end)
 return {model=model,destroyed=destroyed,health=health,kind=object.kind,position=object.box.Position}
end
-- Local maintenance complements the automatic repair timer. A worker must
-- physically reach the object and finish its work after a quiet interval.
function Service.MaintenanceTarget(origin,radius)
 local candidates={}
 for model,object in pairs(Service.objects) do
  if model.Parent and (object.kind=="Bench" or object.kind=="Bin")
   and object.health<Rules.Types[object.kind].health and os.clock()-(object.lastDamaged or os.clock())>=45
   and (object.box.Position-origin).Magnitude<=radius then
   table.insert(candidates,{model=model,object=object,distance=(object.box.Position-origin).Magnitude})
  end
 end
 table.sort(candidates,function(a,b) return a.distance<b.distance end)
 for _,candidate in ipairs(candidates) do
  local object=candidate.object
  if not occupied(object) then
   local approach
   for _,offset in ipairs({Vector3.new(object.size.X/2+2.4,0,0),Vector3.new(-object.size.X/2-2.4,0,0),Vector3.new(0,0,object.size.Z/2+2.4),Vector3.new(0,0,-object.size.Z/2-2.4)}) do
    local p=object.box:PointToWorldSpace(offset);p=Vector3.new(p.X,origin.Y,p.Z)
    if not approach or (p-origin).Magnitude<(approach-origin).Magnitude then approach=p end
   end
   return {position=approach,lookAt=object.box.Position,action="Repairing "..Rules.Types[object.kind].name:lower(),maintenanceModel=candidate.model,maintenanceVersion=object.version}
  end
 end
end
function Service.FinishMaintenance(station,workerPosition)
 local model=station.maintenanceModel;local object=Service.objects[model]
 if not object or not model.Parent or object.version~=station.maintenanceVersion
  or (object.kind~="Bench" and object.kind~="Bin") or object.health>=Rules.Types[object.kind].health
  or os.clock()-(object.lastDamaged or os.clock())<45 or (workerPosition-station.position).Magnitude>2
  or (workerPosition-object.box.Position).Magnitude>12 or occupied(object) then return false end
 -- Invalidate the old timer only after all safety checks pass.
 object.version+=1;restore(model,object,object.version)
 return true
end
function Service.Start(world)
 Service.objects={};Service.ids={};Service.world=world
 for _,model in ipairs(Collection:GetTagged('CityDestructible')) do if model:IsDescendantOf(world) then Service.Register(model) end end
 if Service.added then Service.added:Disconnect() end
 Service.added=Collection:GetInstanceAddedSignal('CityDestructible'):Connect(function(model) if model:IsDescendantOf(world) then task.defer(function() if model:IsDescendantOf(world) then Service.Register(model) end end) end end)
 if Service.removed then Service.removed:Disconnect() end
 Service.removed=Collection:GetInstanceRemovedSignal("CityDestructible"):Connect(function(model) local id=model:GetAttribute("ObjectId");if id and Service.ids[id]==model then Service.ids[id]=nil end;Service.objects[model]=nil end)
end
return Service
