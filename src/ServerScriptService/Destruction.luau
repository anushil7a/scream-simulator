local Players=game:GetService('Players')
local Collection=game:GetService('CollectionService')
local Rules=require(game.ReplicatedStorage.Shared.DestructionRules)
local Service={objects={}}
function Service.Register(model)
 if Service.objects[model] then return end
 local kind=model:GetAttribute('DestructibleType');local spec=Rules.Types[kind]
 if not spec then return end
 local parts={}
 for _,part in ipairs(model:GetDescendants()) do
  if part:IsA('BasePart') then parts[part]={color=part.Color,transparency=part.Transparency,collide=part.CanCollide,query=part.CanQuery,touch=part.CanTouch} end
 end
 local cf,size=model:GetBoundingBox()
 Service.objects[model]={parts=parts,kind=kind,health=spec.health,box=cf,size=size,version=0,prompts={}}
 for _,item in ipairs(model:GetDescendants()) do if item:IsA("ProximityPrompt") then Service.objects[model].prompts[item]=item.Enabled end end
 model:SetAttribute('ObjectHealth',spec.health);model:SetAttribute('ObjectMaxHealth',spec.health);model:SetAttribute('RequiredLevel',spec.level);model:SetAttribute('Destroyed',false)
end
local function occupied(object)
 local characters={};for _,p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(characters,p.Character) end end
 if #characters==0 then return false end
 local params=OverlapParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances=characters;params.MaxParts=1
 return #workspace:GetPartBoundsInBox(object.box,object.size+Vector3.new(2,3,2),params)>0
end
local function restore(model,object,version)
 if not model.Parent or object.version~=version then return end
 if occupied(object) then model:SetAttribute('RepairAt',workspace:GetServerTimeNow()+5);task.delay(5,function() restore(model,object,version) end);return end
 local spec=Rules.Types[object.kind];object.health=spec.health
 for part,original in pairs(object.parts) do if part.Parent then part.Transparency=original.transparency;part.CanCollide=original.collide;part.CanQuery=original.query;part.CanTouch=original.touch;part.Color=original.color;if part:IsA("Seat") then part.Disabled=false end end end
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
 object.health=health;model:SetAttribute('ObjectHealth',health)
 local ratio=health/Rules.Types[object.kind].health;model:SetAttribute('DamageStage',destroyed and 3 or ratio<.35 and 2 or ratio<.7 and 1 or 0)
 for part,original in pairs(object.parts) do if part.Parent then
  if destroyed then part.Transparency=1;part.CanCollide=false;part.CanQuery=false;part.CanTouch=false;if part:IsA("Seat") then if part.Occupant then part.Occupant.Sit=false end;part.Disabled=true end
  else part.Color=original.color:Lerp(Color3.fromRGB(90,76,67),(1-ratio)*.45) end
 end end
 if destroyed then
  for prompt in pairs(object.prompts) do if prompt.Parent then prompt.Enabled=false end end
  object.version+=1;local version=object.version;local duration=Rules.Types[object.kind].repair
  model:SetAttribute('Destroyed',true);model:SetAttribute('RepairAt',workspace:GetServerTimeNow()+duration)
  task.delay(duration,function() restore(model,object,version) end)
 end
 return {model=model,destroyed=destroyed,health=health,kind=object.kind,position=object.box.Position}
end
function Service.Start(world)
 Service.objects={}
 for _,model in ipairs(Collection:GetTagged('CityDestructible')) do if model:IsDescendantOf(world) then Service.Register(model) end end
 if Service.added then Service.added:Disconnect() end
 Service.added=Collection:GetInstanceAddedSignal('CityDestructible'):Connect(function(model) if model:IsDescendantOf(world) then Service.Register(model) end end)
end
return Service
