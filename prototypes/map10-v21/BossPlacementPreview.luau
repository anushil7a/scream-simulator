-- Isolated MAP-10 v2.1 placement review. Real presentation and patrol; no combat/progression.
local Run=game:GetService("RunService")
local Server=game:GetService("ServerScriptService")
local Shared=game:GetService("ReplicatedStorage"):WaitForChild("Shared")
local Homes=require(Shared.CompactLayout).BossHomes

return function(world)
 if not Run:IsStudio() or game.GameId~=0 or game.PlaceId~=0 then return end
 local Service=require(Server.BossService)
 local params=RaycastParams.new()
 params.FilterType=Enum.RaycastFilterType.Include
 params.FilterDescendantsInstances={world}
 local seen,probes={},0
 for id,home in pairs(Homes) do
  local ground=Vector3.new(home.x,home.y,home.z)
  for band=0,5 do
   local radius=band==0 and 0 or (home.radius+home.patrolRadius)*band/5
   for tick=0,(band==0 and 0 or 23) do
    local a=tick*math.pi/12
    local p=ground+Vector3.new(math.cos(a)*radius,0,math.sin(a)*radius)
    local floor=workspace:Raycast(p+Vector3.new(0,3,0),Vector3.new(0,-6,0),params)
    assert(floor and floor.Instance:GetAttribute("ZoneId")==home.district
      and math.abs(floor.Position.Y-p.Y)<=.12 and floor.Normal.Y>.98,
      id.." lacks level floor at "..tostring(p))
    local obstruction=workspace:Raycast(p+Vector3.new(0,.16,0),Vector3.new(0,17.84,0),params)
    assert(not obstruction,id.." has an overhead obstruction at "..tostring(p))
    probes+=2
   end
  end
  seen[id]=true
 end
 local folder=Instance.new("Folder");folder.Name="ScreamSimulatorWorld"
 local no=function() end
 local service=Service.new(folder,{context=no,player=no,reward=no,damage=no})
 local count=0
 for _,boss in ipairs(service.bosses) do
  local home=Homes[boss.spec.id]
  assert(seen[boss.spec.id] and boss.center==Vector3.new(home.x,home.y,home.z)
   and boss.spec.radius==home.radius and boss.spec.moveLeash==home.patrolRadius,"misplaced boss: "..boss.spec.id)
  count+=1;seen[boss.spec.id]=nil
  boss.model:SetAttribute("MapDistrict",home.district)
  boss.idleText=boss.spec.name.." · Lv "..boss.spec.level.."+\nPlacement preview · patrol only"
  boss.label.Text=boss.idleText
 end
 assert(next(seen)==nil and count==5,"MAP-10 boss preview roster mismatch")
 folder.Parent=workspace
 workspace:SetAttribute("ReviewBossCount",count)
 workspace:SetAttribute("ReviewBossPlacementProbes",probes)
 print("[BossPlacementReview] verified",count,"homes with",probes,"floor and headroom probes")
 local loop;loop=Run.Heartbeat:Connect(function()
  if folder.Parent~=workspace or world.Parent~=workspace then
   loop:Disconnect()
   folder:Destroy()
  else service:Step(os.clock()) end
 end)
end
