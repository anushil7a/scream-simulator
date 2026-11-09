-- Appended only to PerformanceReview, an unpublished temporary-profile place.
-- Server Command Bar: game.ServerStorage.RunServerSample:Invoke(30, "idle")
do
 local sampleRunning=false
 local function worldCounts()
  local descendants=workspace:GetDescendants();local parts=0
  for _,item in ipairs(descendants) do if item:IsA("BasePart") then parts+=1 end end
  local counts={workspaceInstances=#descendants,baseParts=parts,players=#Players:GetPlayers(),
   residents=0,workingResidents=0,recoveringResidents=0,activeScreams=0,
   destructibles=0,damagedObjects=0,destroyedObjects=0,blockedRepairs=0}
  local collection=game:GetService("CollectionService")
  for _,model in collection:GetTagged("CityResident") do
   if model:IsDescendantOf(workspace) then
    counts.residents+=1
    if model:GetAttribute("ResidentActive")==false then counts.recoveringResidents+=1
    elseif model:GetAttribute("Working")==true then counts.workingResidents+=1 end
   end
  end
  for _,model in collection:GetTagged("CityDestructible") do
   if model:IsDescendantOf(workspace) then
    counts.destructibles+=1
    local health,maximum=model:GetAttribute("ObjectHealth"),model:GetAttribute("ObjectMaxHealth")
    if type(health)=="number" and type(maximum)=="number" and health<maximum then counts.damagedObjects+=1 end
    if model:GetAttribute("Destroyed")==true then counts.destroyedObjects+=1 end
    if model:GetAttribute("RepairBlocked")==true then counts.blockedRepairs+=1 end
   end
  end
  for _,session in sessions do
   if session.sustained and session.sustained.protocol.active then counts.activeScreams+=1 end
  end
  return counts
 end
 local runner=Instance.new("BindableFunction");runner.Name="RunServerSample"
 runner.OnInvoke=function(seconds,scenario)
  if sampleRunning then return {error="A sample is already running"} end
  if type(seconds)~="number" or seconds~=seconds or seconds==math.huge or seconds==-math.huge then seconds=30 end
  seconds=math.clamp(seconds,10,120)
  scenario=type(scenario)=="string" and string.sub(scenario,1,80) or "unspecified"
  sampleRunning=true
  local ok,result=pcall(function()
   local before=worldCounts();local values={};local start=os.clock()
   while os.clock()-start<seconds and #values<20000 do
    table.insert(values,RunService.Heartbeat:Wait())
   end
   local elapsed=os.clock()-start
   return {scenario=scenario,durationSeconds=elapsed,requestedSeconds=seconds,
    sampleCapReached=#values>=20000,heartbeat=summarizeHeartbeat(values),before=before,after=worldCounts(),
    scope="Local Studio SERVER heartbeat intervals only; not client FPS, CPU time, live network or voice verification"}
  end)
  sampleRunning=false
  if not ok then warn("SERVER_SAMPLE_ERROR",result);return {error=tostring(result)} end
  print("SERVER_SAMPLE",game:GetService("HttpService"):JSONEncode(result))
  return result
 end
 runner.Parent=game:GetService("ServerStorage")
 print("SERVER_SAMPLE_READY · RunServerSample:Invoke(30, scenario) · disposable local server only")
end
