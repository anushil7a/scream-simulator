-- Run with the actual Rules/Service modules in a disposable Studio SERVER session.
-- Only the bench's repair delay is shortened; the occupied-volume retry remains five seconds.
return function(Rules,Service)
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0)
 local Collection=game:GetService("CollectionService")
 local world=Instance.new("Model");world.Name="DestructionAudit";world.Parent=workspace
 local function target(name,kind,x)
  local model=Instance.new("Model");model.Name=name;model.Parent=world;model:SetAttribute("DestructibleType",kind)
  local body=Instance.new("Part");body.Name="Body";body.Size=Vector3.new(4,2,2);body.CFrame=CFrame.new(x,1000,0);body.Anchored=true;body.Parent=model
  Collection:AddTag(model,"CityDestructible");return model,body
 end
 local bench,body=target("Bench","Bench",0)
 local seat=Instance.new("Seat");seat.Anchored=true;seat.CFrame=body.CFrame;seat.Disabled=true;seat.Parent=bench
 local prompt=Instance.new("ProximityPrompt");prompt.Parent=body
 local tree,treeBody=target("Tree","SmallTree",20)
 local blocker=Instance.new("Model");blocker.Name="Resident";blocker.Parent=world;Collection:AddTag(blocker,"CityResident")
 local torso=Instance.new("Part");torso.Size=Vector3.new(2,2,1);torso.CFrame=body.CFrame;torso.Anchored=true;torso.CanQuery=false;torso.CanCollide=true;torso.Parent=blocker
 local savedDelay=Rules.Types.Bench.repair;Rules.Types.Bench.repair=.15
 Service.Start(world)
 local ok,err=pcall(function()
  assert(bench:GetAttribute("ObjectId")~=tree:GetAttribute("ObjectId"),"Unique IDs")
  local denied=Service.Damage(treeBody,25,48);assert(denied.reason=="level" and tree:GetAttribute("ObjectHealth")==110,"Level gate")
  local first=Service.Damage(body,1,48);assert(first.health==2 and not first.destroyed,"Partial damage")
  Service.Register(bench);assert(bench:GetAttribute("ObjectHealth")==2,"Registration preserves damage")
  local second=Service.Damage(body,1,2);assert(second.destroyed and not body.CanCollide and body.Transparency==1 and not prompt.Enabled,"Destroyed state")
  task.wait(.3)
  assert(bench:GetAttribute("Destroyed"),"Repair must wait for non-queryable resident")
  torso.Position+=Vector3.new(50,0,0)
  task.wait(5.1)
  assert(not bench:GetAttribute("Destroyed") and body.CanCollide and body.Transparency==0,"Repair after vacancy")
  assert(seat.Disabled and prompt.Enabled and bench:GetAttribute("ObjectHealth")==50,"Original seat/prompt/health restored")
  Service.Damage(body,1,48);Service.Damage(body,1,2);Collection:RemoveTag(bench,"CityDestructible")
  task.wait(.3);assert(bench:GetAttribute("Destroyed"),"Removed object cancels stale repair")
 end)
 Rules.Types.Bench.repair=savedDelay;world:Destroy()
 assert(ok,err)
 return {passed=true,checks=9,shortenedRepairDelay=.15,occupancyRetrySeconds=5}
end
